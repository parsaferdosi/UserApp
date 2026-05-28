import secrets

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from user.models import Account
from utils.code_generator import generate_numeric_code
from utils.Redis import redis_manager
from utils.sms import get_sms_provider


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["email", "username", "phone_number", "password"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True},
            "username": {"required": True},
            "phone_number": {"required": True},
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = Account(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        exclude = ("is_staff", "is_superuser")
        read_only_fields = ("created_at", "last_updated", "is_active", "is_verified")
        extra_kwargs = {"password": {"required": False, "write_only": True}}

    def update(self, instance, validated_data):
        password = validated_data.get("password")
        phone_number = validated_data.get("phone_number", instance.phone_number)
        email = validated_data.get("email", instance.email)
        first_name = validated_data.get("first_name", instance.first_name)
        last_name = validated_data.get("last_name", instance.last_name)
        if password:
            instance.set_password(password)
        instance.phone_number = phone_number
        instance.email = email
        instance.first_name = first_name
        instance.last_name = last_name
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        username_or_email = attrs.get("username_or_email")
        password = attrs.get("password")

        from django.db.models import Q

        user = Account.objects.filter(
            Q(email=username_or_email) | Q(username=username_or_email)
        ).first()

        if not user or not user.check_password(password):
            raise serializers.ValidationError("نام کاربری یا رمز عبور اشتباه است.")

        if not user.is_active:
            raise serializers.ValidationError("این حساب کاربری غیرفعال است.")

        if not user.phone_number:
            raise serializers.ValidationError("شماره تلفنی برای این حساب ثبت نشده است.")

        attrs["user"] = user
        return attrs

    def send_code(self):
        user = self.validated_data["user"]
        # Generate OTP and session token
        otp_code = generate_numeric_code(6)
        session_token = secrets.token_urlsafe(32)

        # Store only immutable data in Redis — attempts are tracked separately
        session_data = {"user_id": user.id, "code": otp_code}
        try:
            redis_manager.set_data("otp", f"2fa:session:{session_token}", session_data, expire=120)
        except Exception as e:
            raise serializers.ValidationError("خطا در ارتباط با حافظه موقت (Redis).") from e

        # Send SMS
        try:
            sms = get_sms_provider()
            sms.send_sms(user.phone_number, f"کد تایید ورود شما: {otp_code}")
        except Exception:
            # Silent fail for SMS in serializer so logic continues, but can be logged
            pass

        # Return formatted response data to the view
        return {"session_token": session_token, "message": "کد تایید با موفقیت پیامک شد."}


class AuthorizationSerializer(serializers.Serializer):
    session_token = serializers.CharField(required=True)
    otp_code = serializers.CharField(max_length=6, min_length=6, required=True)

    MAX_ATTEMPTS = 3

    def validate(self, attrs):
        session_token = attrs.get("session_token")
        otp_code = attrs.get("otp_code")

        session_key = f"2fa:session:{session_token}"
        attempts_key = f"2fa:attempts:{session_token}"

        try:
            session_data = redis_manager.get_data("otp", session_key)
        except Exception as e:
            raise serializers.ValidationError("خطا در ارتباط با حافظه موقت (Redis).") from e

        if not session_data:
            raise serializers.ValidationError("نشست منقضی شده یا نامعتبر است.")

        user_id = session_data.get("user_id")
        saved_code = session_data.get("code")

        # Atomically increment attempts — INCR is single-threaded in Redis, no race condition
        if saved_code != otp_code:
            attempts = redis_manager.incr_data(
                "otp",
                attempts_key,
                expire=120,
            )

            remaining = self.MAX_ATTEMPTS - attempts

            if remaining <= 0:
                redis_manager.delete_data("otp", session_key)
                redis_manager.delete_data("otp", attempts_key)

                raise serializers.ValidationError(
                    "تعداد دفعات تلاش بیش از حد مجاز است. لطفا مجددا لاگین کنید."
                )

            raise serializers.ValidationError(
                {"otp_code": f"کد تایید اشتباه است. {remaining} تلاش باقی مانده است."}
            )
        # Success — clean up both keys
        redis_manager.delete_data("otp", session_key)
        redis_manager.delete_data("otp", attempts_key)

        try:
            user = Account.objects.get(id=user_id)
        except Account.DoesNotExist:
            raise serializers.ValidationError("کاربر یافت نشد.")  # noqa: B904

        if not user.is_active:
            raise serializers.ValidationError("حساب کاربری غیرفعال شده است.")

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "email": user.email,
            "username": user.username,
            "message": "ورود با موفقیت انجام شد.",
        }

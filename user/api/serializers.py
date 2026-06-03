import secrets
from time import time

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
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


class ProfileReterieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ("id",
                  "email",
                  "username",
                  "phone_number",
                  "created_at",
                  "last_updated",
                  "is_active",
                  "is_verified")

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Account
        fields=("email","username","phone_number")
        
class ChangePasswordSerialzier(serializers.Serializer):
    old_password=serializers.CharField(required=True)
    new_password0=serializers.CharField(required=True)
    new_password1=serializers.CharField(required=True)
    
    def validate(self, attrs):
        user=self.instance
        old_password = attrs.get('old_password')
        new_password0 = attrs.get('new_password0')
        new_password1 = attrs.get('new_password1')
        
        if not user.check_password(old_password):
            raise serializers.ValidationError(_("رمز عبور فعلی اشتباه است"))
        if new_password0 != new_password1:
            raise serializers.ValidationError(_("رمز های عبور جدید با هم مطابقت ندارند"))
        try:
            validate_password(new_password0,user)
        except DjangoValidationError as e:
            raise serializers.ValidationError(_({"new_password0": list(e.messages)})) from e

        return attrs
    
    def save(self,**kwargs):
        user=self.instance
        new_password=self.validated_data['new_password0']
        user.set_password(new_password)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)


    def is_email(self, value):
        try:
            validate_email(value)
            return True
        except DjangoValidationError:
            return False

    def get_user(self,username_or_email):
        try:
            user=None
            if username_or_email:
                if self.is_email(username_or_email):
                    user=Account.objects.get(email=username_or_email)
                else:
                    user=Account.objects.get(username=username_or_email)
            return user
        except Account.DoesNotExist:
            return None
    

    def validate(self, attrs):
        username_or_email = attrs.get("username_or_email")
        password = attrs.get("password")

        user = self.get_user(username_or_email)
        if not user or not user.check_password(password):
            raise serializers.ValidationError(_("نام کاربری یا رمز عبور اشتباه است."))

        if not user.is_active:
            raise serializers.ValidationError(_("این حساب کاربری غیرفعال است."))

        if not user.phone_number:
            raise serializers.ValidationError(_("شماره تلفنی برای این حساب ثبت نشده است."))

        return {"user": user}

    def send_code(self):
        user = self.validated_data["user"]
        # Generate OTP and session token
        otp_code = generate_numeric_code(6)
        session_token = secrets.token_urlsafe(32)

        # Store only immutable data in Redis — attempts are tracked separately
        session_data = {"user_id": user.id, "code": otp_code}
        try:
            #Note: OTP expire time has hardcoded to a default of 2 minutes (120 seconds)
            #Becuase I was to lazy to set it dyanamic from main setting in django
            #and also for Capability reason.
            redis_manager.set_data("otp", f"2fa:session:{session_token}", session_data, expire=120)
        except Exception as e:
            raise serializers.ValidationError(_("خطا در ارتباط با حافظه موقت (Redis).")) from e

        # Send SMS
        try:
            sms = get_sms_provider()
            sms.send_sms(user.phone_number, f"کد تایید ورود شما: {otp_code}")
        except Exception as e:
            raise serializers.ValidationError(_("ارسال پیامک با خطا مواجه شد.")) from e
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
            raise serializers.ValidationError(_("خطا در ارتباط با حافظه موقت (Redis).")) from e

        if not session_data:
            raise serializers.ValidationError(_("نشست منقضی شده یا نامعتبر است."))

        user_id = session_data.get("user_id")
        saved_code = session_data.get("code")

        if not secrets.compare_digest(saved_code, otp_code):
            attempts = redis_manager.incr_data(
                "otp",
                attempts_key,
                expire=120,
            )

            remaining = self.MAX_ATTEMPTS - attempts

            if remaining <= 0:
                redis_manager.delete_data("otp", session_key)
                redis_manager.delete_data("otp", attempts_key)

                raise serializers.ValidationError(_(
                    "تعداد دفعات تلاش بیش از حد مجاز است. لطفا مجددا لاگین کنید."
                ))

            raise serializers.ValidationError(_(
                {"otp_code": f"کد تایید اشتباه است. {remaining} تلاش باقی مانده است."}
            ))
        # Success — clean up both keys
        redis_manager.delete_data("otp", session_key)
        redis_manager.delete_data("otp", attempts_key)

        return {"user_id": user_id}

    def generate_token(self):
        user_id=self.validated_data["user_id"]
        try:
            user = Account.objects.get(id=user_id)
        except Account.DoesNotExist:
            raise serializers.ValidationError(_("کاربر یافت نشد."))  # noqa: B904

        if not user.is_active:
            raise serializers.ValidationError(_("حساب کاربری غیرفعال شده است."))

        refresh = RefreshToken.for_user(user)

        exp=refresh["exp"]
        ttl=exp-int(time())
        try:
            redis_manager.set_data(
                "session",
                refresh["jti"],
                str(user.id),
                ttl,
            )
        except Exception as e:
            raise serializers.ValidationError(_("خطا در هنگام ورود به سیستم،لطفا مجددا تلاش کنید")) from e  # noqa: E501

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "message": "ورود با موفقیت انجام شد.",
        }
        
class LogoutSerializer(serializers.Serializer):
    refresh=serializers.CharField(required=True)
    
    def validate(self,attrs):
        self.token=attrs["refresh"]
        return attrs
    def save(self,**kwargs):
        try:
            refresh_token=RefreshToken(self.token)
            jti=refresh_token['jti']
            redis_manager.delete_data("sesstion",jti)
        except TokenError as e:
            raise serializers.ValidationError(_("توکن نا معتبر است یا قبلا منقظی شده است"))from e
        except Exception as e:
            raise serializers.ValidationError(_("خطا در عملیات خروج. لطفا مجددا تلاش کنید.")) from e

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        old_refresh = RefreshToken(attrs["refresh"])

        if not redis_manager.exist_data(
            "session",
            old_refresh["jti"]
        ):
            raise serializers.ValidationError(_("نشست کاربر منقضی شده است"))

        data = super().validate(attrs)

        new_refresh = RefreshToken(data["refresh"])
        user_id=str(new_refresh["user_id"])
        ttl = new_refresh["exp"] - int(time())

        redis_manager.update_data(
            "session",
            old_refresh["jti"],
            user_id,
            new_refresh["jti"],
            ttl
        )

        return data
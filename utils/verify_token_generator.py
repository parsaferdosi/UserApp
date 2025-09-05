import jwt
from datetime import datetime, timedelta , timezone
from django.conf import settings
from django.core.mail import send_mail


class GenerateJWT:
    def generate_verify_jwt(user):

        payload = {
            "user_id":user.id,
            "purpose" : "verify_account",
            "exp":  datetime.now(timezone.utc) + timedelta(minutes=3),
            "iat" : datetime.now(timezone.utc)
        }

        token_encode = jwt.encode(payload , settings.SECRET_KEY , algorithm="HS256")
        verifaction_link = f"http://127.0.0.1:8000/api/user/verify/?token={token_encode}"

        send_mail(
            subject= "تایید ایمیل",
            message= f"برای تایید حساب خود روی لینک زیر کلیک کنید {verifaction_link}",
            from_email= settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email]
        )

        return token_encode
    
    def generate_reset_password_jwt(user):

        payload = {
            "user_id":user.id,
            "purpose" : "reset_password",
            "exp":  datetime.now(timezone.utc) + timedelta(minutes=3),
            "iat" : datetime.now(timezone.utc)
        }

        token_encode = jwt.encode(payload , settings.SECRET_KEY , algorithm="HS256")
        verifaction_link = f"http://127.0.0.1:8000/api/user/reset_password/?token={token_encode}"

        send_mail(
            subject= "تغییر رمز عبور ",
            message= f"برای تغییر رمز عبور خود روی لینک زیر کلیک کنید {verifaction_link}",
            from_email= settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email]
        )

        return token_encode

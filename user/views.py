#ApiView based on DRF and django
from user.serializer import AccountSerializer, ResetPasswordSerializer , SendResetPasswordSerializer
from user.models import Account
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser
from rest_framework.viewsets import GenericViewSet,ModelViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
#swagger manual schema
from drf_yasg.utils import swagger_auto_schema
import jwt
from django.conf import settings
from utils.verify_token_generator import GenerateJWT
from .models import Account
from django.shortcuts import get_object_or_404

class MyAccountViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    """AccountViewSet is a viewset for managing user accounts.
    It provides create, retrieve, update, and destroy operations for user accounts.

    Args:
        CreateModelMixin (POST): create a new user account.
        RetrieveModelMixin (GET): retrieve user account details.
        UpdateModelMixin (PATCH): update user account details.
        DestroyModelMixin (DELETE): delete a user account.
        ViewSet (_type_): Base class for viewsets that provides default implementations for common actions.
    """
    serializer_class = AccountSerializer
    def get_permissions(self):
        """allow non-authenticated user to create(), but everything else must be authenticated"""
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    def get_object(self):
        """get the user account object based on the authenticated user"""
        return self.request.user
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
class AdminAccountViewSet(ModelViewSet):
    """AdminAccountViewSet is a viewset for managing user accounts by admin users.
    It provides create, retrieve, update, and destroy operations for user accounts.

    Args:
        ModelViewSet: A viewset that provides default implementations for create, retrieve, update, partial_update, destroy, and list actions.
    """
    serializer_class = AccountSerializer
    queryset = Account.objects.all()
    permission_classes = [IsAdminUser]

class SendVerifyLinkAPIView(APIView):
    """
    Send Verify link API View
    -------------------------------
    Methode : GET

    Description : 
        Send verify link from email to user.

    Permissions : 
        IsAuthenticated

    Request:
        No body required.
        Authentication token must be sent in the request header.

    """
    permission_classes = [IsAuthenticated]
    def get(self , request):
        user = request.user
        GenerateJWT.generate_verify_jwt(user)
        return Response({"message":"لینک ارسال شد"},status=status.HTTP_200_OK)
    





class VerifyAccountAPIView(APIView):
    """
    Verify Account API View
    -------------------------------

    This endpoint is used to verify a user's account using a JWT verification token.

    Method:
        GET:
            - Requires a valid JWT verification token passed as a query parameter (?token=<token>).
            - Decodes and validates the token (checks expiration, validity, and purpose).
            - If valid, marks the user's account as verified (`is_verified = True`).

    Request Query Parameters:
        token (str) : A valid JWT token with purpose = "verify_account".
    """

    def get(self , request):
        token = request.GET.get("token")
        try :
            payload = jwt.decode(token , settings.SECRET_KEY , algorithms=["HS256"])
            if payload.get("purpose") != "verify_account" :
                return Response({"message":"توکن نامعتبر است "}, status=status.HTTP_400_BAD_REQUEST)
            
            user = Account.objects.get(id = payload.get("user_id"))
            user.is_verified = True
            user.save()
            return Response({"message":"حساب کاربری شما با موفقیت تایید شد"}, status=status.HTTP_200_OK)
        except Account.DoesNotExist:
            return Response({"message":"کاربر یافت نشد"}, status=status.HTTP_404_NOT_FOUND)
        except jwt.ExpiredSignatureError:
            return Response({"error": "لینک منقضی شده"}, status=400)
        except jwt.InvalidTokenError:
            return Response({"error": "توکن نامعتبر است"}, status=400)


class SendRestPasswordAPIView(APIView):
    """
    Send Rest Password API View

    -------------------------------
    Methode :
        (GET) : When the user authenticated and have request
        (POST) : When user forgoted password and want login

    descriptions :
        This view send rest password link for user , then user
        can change his password.

    Permissions :
        (GET) : IsAuthenticated
        (POST) : AllowAny

    """

    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [IsAuthenticated]
        else :
            permission_classes= [AllowAny]
        
        return [permission() for permission in permission_classes]

    def get(self , request):
        user = request.user
        GenerateJWT.generate_reset_password_jwt(user)
        return Response({"message":"لینک با موفقیت ارسال شد لطفا ایمیلتان را چک کنید"})
    
    def post(self , request):
        srz_data = SendResetPasswordSerializer(data = request.data)
        if srz_data.is_valid():
            email = srz_data.validated_data.get("email")
            user = get_object_or_404(Account , email = email)
            GenerateJWT.generate_reset_password_jwt(user)
            return Response({"message":"لینک ارسال شد"},status=status.HTTP_200_OK)
        return Response(srz_data.errors , status=status.HTTP_400_BAD_REQUEST)
      


class ChangeRestPasswordAPIView(APIView):
    """
    Change Password API View
    -------------------------------

    This endpoint allows a user to change their password using a valid reset token.

    Method:
        POST:
            - Requires a valid JWT reset token passed as a query parameter (?token=<token>).
            - Validates the token (checks expiration, validity, and purpose).
            - Accepts `password` and `confirm_password` in the request body.
            - If the token and data are valid, the user's password will be updated.

    Request Query Parameters:
        token (str) : A valid JWT reset token with purpose = "reset_password".

    """

    def post(self , request ):
        
        token = request.GET.get("token")
        try :
            payload = jwt.decode(token ,  settings.SECRET_KEY  ,algorithms=["HS256"] )
            if payload.get("purpose") != "reset_password":
                return Response({"message":"توکن نامعتبر است "}, status=status.HTTP_400_BAD_REQUEST)
            
            user = get_object_or_404(Account , pk = payload["user_id"])
            srz_data =ResetPasswordSerializer(data = request.data)
            if srz_data.is_valid():
                srz_data.save(user=user)
                return Response({"message": "پسورد شما با موفقیت عوض شد"}, status=status.HTTP_200_OK)

            return Response(srz_data.errors, status=status.HTTP_400_BAD_REQUEST)

        except jwt.ExpiredSignatureError:
            return Response({"error": "لینک منقضی شده"}, status=400)
        except jwt.InvalidTokenError:
            return Response({"error": "توکن نامعتبر است"}, status=400)

                



            
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView

from . import serializers


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.RegisterSerializer


class LoginView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.send_code()

        return Response(data, status=status.HTTP_200_OK)


class AuthorizationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.AuthorizationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data=serializer.generate_token()
        return Response(data, status=status.HTTP_200_OK)

class LogoutView(generics.GenericAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=serializers.LogoutSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message":_("خروج با موفقیت انجام شد")},
            status=status.HTTP_200_OK
        )

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method=="GET":
            return serializers.ProfileReterieveSerializer
        else: 
            return serializers.ProfileUpdateSerializer

class ChangePasswordView(generics.UpdateAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=serializers.ChangePasswordSerialzier
    
    def get_object(self):
        return self.request.user

    def put(self,request,*args,**kwargs):
        user=self.get_object()
        serializer = self.get_serializer(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            _({"message":"رمز عبور با موفقیت تغییر پیدا کرد"}),
            status=status.HTTP_200_OK
        )

class DeleteAccountView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class CustomTokenRefreshView(TokenRefreshView):
    serializer_class=serializers.CustomTokenRefreshSerializer
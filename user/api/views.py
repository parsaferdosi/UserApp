from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

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


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ProfileSerializer

    def get_object(self):
        return self.request.user


class DeleteAccountView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

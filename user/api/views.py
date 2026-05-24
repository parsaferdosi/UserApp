from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from . import serializers


class RegisterView(generics.CreateAPIView):
    permission_classes=[AllowAny]
    serializer_class=serializers.RegisterSerializer

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=serializers.ProfileSerializers

class DeleteAccountView(generics.DestroyAPIView):
    permission_classes=[IsAuthenticated]
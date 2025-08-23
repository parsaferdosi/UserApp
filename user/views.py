#ApiView based on DRF and django
from user.serializer import AccountSerializer
from user.models import Account
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser
from rest_framework.viewsets import GenericViewSet,ModelViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework import status

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

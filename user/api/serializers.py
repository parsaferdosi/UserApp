from rest_framework import serializers
from user.models import Account


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model=Account
        fields=["email","username","phone_number","password"]
        extra_kwargs={
            "password":{"write_only":True},
            "email":{"required":True},
            "username":{"required":True},
            "phone_number":{"required":True}
        }
    def create(self,validated_data):
        password=validated_data.pop('password')
        user=Account(**validated_data)
        user.set_password(password)
        user.save()
        return user
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=Account
        exclude=("is_staff","is_superuser")
        read_only_fields = (
            'created_at',
            'last_updated',
            'is_active',
            'is_verified'
)
        extra_kwargs={
            "password":{"required":False,"write_only":True}
        }
    def update(self, instance, validated_data):
        instance.phone_number = validated_data.get("phone_number", instance.phone_number)
        instance.email = validated_data.get("email", instance.email)
        if validated_data.get("password"):
            instance.set_password(validated_data.get("password", instance.password))
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.save()
        return instance
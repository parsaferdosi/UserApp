#thie file is used to define serializers for user models
from rest_framework import serializers
from .models import Account
import re
# Serializer for the Account model
class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model=Account
        exclude = ('groups', 'user_permissions')
        read_only_fields = ('date_joined', 'last_updated','is_active', 'is_staff', 'is_superuser', 'is_verified')
        required_fields = ['email', 'username', 'password']
        extra_kwargs={
            'password': {'write_only': True},
        }
    def __init__(self,*args,**kwargs):
        partial = kwargs.get('partial', False)
        super().__init__(*args, **kwargs)

        if partial:
            for field in self.fields:
                self.fields[field].required = False
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Account(**validated_data)
        user.set_password(password)
        user.save()
        return user
class ResetPasswordSerializer(serializers.Serializer):

    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):

        if data["password"] != data["confirm_password"] :
            raise serializers.ValidationError("The password and confrim password must be match")
        
        if len(data["password"]) < 8 :
            raise serializers.ValidationError("The password must be at least 8 characters.")
        
        if not re.search(r"\d", data["password"]):
            raise serializers.ValidationError("The password must be at least numbers")
        
        if not re.search(r"[A-Z]", data["password"]):
            raise serializers.ValidationError("The password must be at least big letters")
        
        return data
    
    def save(self, user ):
        password = self.validated_data["password"]
        user.set_password(password)
        user.save()
        return user
    

class SendResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()   

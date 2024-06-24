from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import logging

from users.models import CustomUser

logger = logging.getLogger(__name__)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        logger.debug(f"Attempting to authenticate user: {username}")

        user = authenticate(username=username, password=password)

        if user is None:
            logger.error(f"Authentication failed for user: {username}")
            raise serializers.ValidationError("No active account found with the given credentials")

        if not user.is_active:
            logger.error(f"Inactive user: {username}")
            raise serializers.ValidationError("User account is disabled")

        data = super().validate(attrs)
        data['username'] = user.username
        logger.debug(f"Authenticated user: {user.username}")
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        logger.debug(f"User created: {user.username}")
        return user

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

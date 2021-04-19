from django.contrib.auth import authenticate

from rest_framework import serializers

from .models import CustomUser


class LoginSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128, write_only=True)
    username = serializers.CharField(max_length=255, write_only=True)
    token = serializers.JSONField(read_only=True)
    user = serializers.JSONField(read_only=True)

    def validate(self, data):
        """
        Validates user data.
        """
        username = data.get('username', None)
        password = data.get('password', None)
        if username is None:
            raise serializers.ValidationError(
                'An login is required to log in.'
            )
        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )
        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError(
                'A user with this login and password was not found.'
            )
        return {
            "user": {
                "name": user.name,
                "surname": user.surname,
                "user_type": user.user_type,
            },
            "token": user.token
        }


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('name', 'surname', 'user_type')


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,
    )
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'name', 'surname', 'password', 'user_type', 'token',)

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)

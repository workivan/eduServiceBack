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
                {"message": 'Заполните логин'}
            )
        if password is None:
            raise serializers.ValidationError(
                {"message": 'Заполните пароль'}
            )
        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError({"message": 'Нет пользователя с таким логином и паролем'})
        return {
            "user": {
                "name": user.name,
                "surname": user.surname,
                "user_type": user.user_type,
            },
            "token": user.token
        }


class CustomUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['name', 'surname', "username", 'user_type']


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

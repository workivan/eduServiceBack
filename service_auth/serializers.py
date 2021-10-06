from django.contrib.auth import authenticate

from rest_framework import serializers

from .models import CustomUser, Student


class LoginSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128, write_only=True)
    username = serializers.CharField(max_length=255, write_only=True)
    token = serializers.JSONField(read_only=True)
    user = serializers.JSONField(read_only=True)

    def validate(self, data):
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
            raise serializers.ValidationError({"message": "Нет пользователя с таким логином и паролем"})
        return {
            "user": {
                "username": user.username,
                "name": user.name,
                "surname": user.surname,
                "user_type": user.user_type,
            },
            "token": user.token
        }


class CustomUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255, write_only=True)

    class Meta:
        model = CustomUser
        fields = ['name', 'surname', "username", "username", 'user_type', 'password']


class StudentSerializer(serializers.ModelSerializer):
    personal = CustomUserSerializer()
    control = serializers.CharField()

    def validate(self, obj):
        students = Student.objects.filter(personal__username=obj["personal"]["username"])
        if len(students) > 0:
            raise serializers.ValidationError(
                {"message":  'Ученик с таким никнеймом уже существует'}
            )
        return obj

    def create(self, validated_data):
        cuser = CustomUser.objects.create_user(**validated_data["personal"])
        validated_data.pop("personal")
        return Student.objects.create(personal=cuser, **validated_data)

    class Meta:
        model = Student
        fields = '__all__'


class UpdateStudentSerializer(serializers.Serializer):
    surname = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    place = serializers.CharField(required=True)
    job = serializers.CharField(required=True)
    city = serializers.CharField(required=True)

    def create(self, validated_data):
        cuser = CustomUser.objects.filter(username=validated_data["username"])
        cuser.update(surname=validated_data["surname"], name=validated_data["name"])
        validated_data.pop("username")
        validated_data.pop("surname")
        validated_data.pop("name")
        student = Student.objects.filter(personal=cuser.first())
        return student.update(**validated_data)


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

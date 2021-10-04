from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView

from django.forms.models import model_to_dict

from core.models import CourseProgress
from .serializers import LoginSerializer, UpdateStudentSerializer, RegistrationSerializer, CustomUserSerializer, StudentSerializer
from .models import CustomUser, Student


class UserRetrieveAPIView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = CustomUserSerializer

    def get(self, request):
        if request.user.pk is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        user = CustomUser.objects.get(username=request.user.username)
        serializer = CustomUserSerializer(data=model_to_dict(user), many=False)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegistrationAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "token": user.token
            },
            status=status.HTTP_201_CREATED,
        )


class StudentsCreationAPIView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = StudentSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            status=status.HTTP_201_CREATED,
        )


class StudentUpdateAPIView(UpdateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UpdateStudentSerializer

    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            status=status.HTTP_201_CREATED,
        )

class StudentDeleteAPIView(DestroyAPIView):
    permission_classes = [AllowAny]

    def delete(self, request, *args, **kwargs):
        cuser = CustomUser.objects.filter(username=request.query_params["username"])
        student = Student.objects.filter(personal=cuser.first())
        CourseProgress.objects.filter(student=student.first()).delete()
        student.delete()
        cuser.delete()
        return Response(
            status=status.HTTP_200_OK,
        )


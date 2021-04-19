from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView

from django.forms.models import model_to_dict

from .serializers import LoginSerializer, RegistrationSerializer, CustomUserSerializer
from .models import CustomUser


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
    """
    Logs in an existing user.
    """
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
                "user": {
                    "id": user.token,
                },
                "token": user.token
            },
            status=status.HTTP_201_CREATED,
        )

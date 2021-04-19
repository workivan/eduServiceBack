from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Course
from .serializers import CourseListSerializer, CourseSerializer


class CourseListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CourseListSerializer
    queryset = Course.objects.all()

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class CourseAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = CourseSerializer

    def get(self, request):
        course = get_object_or_404(Course, course_id=request.GET["course_id"])
        serializer = self.serializer_class(course)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            status=status.HTTP_201_CREATED,
        )





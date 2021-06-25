from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.generics import ListAPIView, UpdateAPIView, CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Course, Lesson, CourseProgress, Test
from service_auth.models import Student
from service_auth.serializers import StudentSerializer
from .mixin import get_content_from_file
from .serializers import CourseListSerializer, CourseSerializer, LessonSerializer, \
    CourseProgressSerializer, TestSerializer


class CourseProgressAPIView(UpdateAPIView, CreateAPIView, ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CourseProgressSerializer
    queryset = CourseProgress.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        if "progress_student" in self.request.GET:
            student = get_object_or_404(Student, personal__username=self.request.GET["progress_student"])
            return qs.filter(student=student, display=True)
        if "course_id" in self.request.GET:
            course = get_object_or_404(Course, id=self.request.GET["course_id"])
            return qs.filter(course=course)
        return qs

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def put(self, request):
        st = get_object_or_404(Student, personal__username=request.data["username"])
        progress = get_object_or_404(CourseProgress, student=st, course=request.data["course"])
        if "solution" in request.data:
            progress.test_passed = request.data["solution"]
            progress.save()
            return Response(
                status=status.HTTP_200_OK,
            )

    def post(self, request, *args, **kwargs):
        st = get_object_or_404(Student, personal__username=request.data["username"])
        crs = get_object_or_404(Course, id=request.data["course"])
        progress = CourseProgress.objects.get_or_create(student=st, course=crs)
        progress[0].display = self.request.data["display"]
        progress[0].save()
        return Response(
            status=status.HTTP_201_CREATED,
        )


class StudentListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = StudentSerializer
    queryset = Student.objects.all()

    def list(self, request, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class CourseListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CourseListSerializer
    queryset = Course.objects.all()

    def get_queryset(self):
        if self.request.user.user_type == "ST":
            st = Student.objects.get(personal=self.request.user)
            progresses = CourseProgress.objects.filter(student=st, display=True)
            qs = [progress.course for progress in progresses]
            return qs
        return super().get_queryset()

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class CourseAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = CourseSerializer

    def get(self, request):
        course = get_object_or_404(Course, id=request.GET["course_id"])
        serializer = self.serializer_class(course)
        return Response(serializer.data)

    def put(self, request):
        course = get_object_or_404(Course, id=request.data["id"])
        serializer = self.serializer_class(course, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(
            status=status.HTTP_201_CREATED,
        )


class LessonListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(course=self.request.GET["course_id"]).order_by("lesson_number")
        return qs

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class LessonAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LessonSerializer

    def get(self, request):
        course = get_object_or_404(Lesson, lesson_number=request.GET["lesson_id"], course=request.GET["course_id"])
        serializer = self.serializer_class(course)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        lesson = get_object_or_404(Lesson, course=request.data["course"], lesson_number=request.data["lesson"])
        serializer = self.serializer_class(lesson, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        data = request.data.dict()
        media = get_content_from_file(data["file"])
        data.update({"content": media})
        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(
            status=status.HTTP_201_CREATED,
        )


class TestListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = TestSerializer
    queryset = Test.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(course=self.request.GET["course_id"]).order_by("test_number")
        return qs

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class TestAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = TestSerializer

    def get(self, request):
        course = get_object_or_404(Test, test_number=request.GET["test_id"], course=request.GET["course_id"])
        serializer = self.serializer_class(course)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(
            status=status.HTTP_201_CREATED,
        )

    def put(self, request):
        course = get_object_or_404(Test, course=request.data["course"], test_number=request.data["id"])
        serializer = self.serializer_class(course, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

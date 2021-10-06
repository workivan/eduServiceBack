from django.shortcuts import get_object_or_404
from django.db.models import F

from rest_framework import status
from rest_framework.generics import ListAPIView, UpdateAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Course, Lesson, CourseProgress, Test
from service_auth.models import Student
from service_auth.serializers import StudentSerializer
from .mixin import get_content_from_file, get_current_test_number, check_answr_correct, update_result, \
    set_lessons_content
from .serializers import CourseListSerializer, CourseSerializer, LessonSerializer, \
    CourseProgressSerializer, TestSerializer, CheckAnswerSetializer


class CourseProgressAPIView(UpdateAPIView, CreateAPIView, ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CourseProgressSerializer
    queryset = CourseProgress.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        if "student" in self.request.GET and "course_id" in self.request.GET:
            student = get_object_or_404(Student, personal__username=self.request.GET["student"])
            course = get_object_or_404(Course, id=self.request.GET["course_id"])
            return qs.filter(course=course, student=student)
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
            if isinstance(request.data["solution"], bool):
                progress.test_passed = request.data["solution"]
            else:
                progress.test_passed = False
                progress.current_test = 1
                progress.test_result = 0
            progress.save()
            return Response(
                status=status.HTTP_200_OK,
            )

    def post(self, request, *args, **kwargs):
        st = get_object_or_404(Student, personal__username=request.data["username"])
        crs = get_object_or_404(Course, id=request.data["course"])
        progress = CourseProgress.objects.get_or_create(student=st, course=crs)
        if isinstance(self.request.data.get("display"), bool):
            progress[0].display = bool(self.request.data.get("display"))
        if isinstance(self.request.data.get("lesson"), int):
            progress[0].current_lesson = int(self.request.data.get("lesson"))
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


class StudentRetrieveAPIView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = StudentSerializer
    queryset = Student.objects.all()

    def get(self, request, **kwargs):
        st = self.get_queryset().get(personal__username=request.query_params["student"])
        serializer = self.serializer_class(st)
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


class CheckAnswerAPI(UpdateAPIView):
    permission_classes = [AllowAny]
    queryset = CourseProgress.objects.all()
    serializer_class = CheckAnswerSetializer

    def put(self, request, *args, **kwargs):
        data = self.serializer_class(data=request.data)
        if data.is_valid(raise_exception=True):
            progress = get_object_or_404(CourseProgress, student__personal__username=data.validated_data["username"],
                                         course=data.validated_data["course_id"])
            correct = check_answr_correct(data.validated_data["course_id"], data.validated_data["test_id"],
                                          data.validated_data["answer_id"])
            course = get_object_or_404(Course, id=data.validated_data["course_id"])
            update_result(correct, progress, course.tests.count())
            return Response(status=status.HTTP_200_OK)


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

    def delete(self, request):
        course = get_object_or_404(Course, id=request.query_params["course_id"])
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
        data = request.data.dict()
        if "file" in data:
            media = get_content_from_file(data["file"])
            data.update({"content": media})
        lesson = get_object_or_404(Lesson, course=data["course"], lesson_number=data["lesson"])
        if "content" not in data:
            data.update({"content": set_lessons_content(lesson.content)})
        serializer = self.serializer_class(lesson, data=data)
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

    def delete(self, request):
        lesson = get_object_or_404(Lesson, course=request.query_params["course"],
                                   lesson_number=request.query_params["lesson_number"])
        lessons = Lesson.objects.filter(lesson_number__gt=lesson.lesson_number, course__id=lesson.course_id)
        lessons.update(lesson_number=F("lesson_number") - 1)
        lesson.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
        try:
            test_number = int(request.GET["username"])
        except ValueError:
            test_number = get_current_test_number(request.GET["course_id"], request.GET["username"])
            if not isinstance(test_number, int):
                return Response({
                    "test_number": 0
                }, status=status.HTTP_200_OK)
        test = get_object_or_404(Test, test_number=test_number, course=request.GET["course_id"])
        serializer = self.serializer_class(test)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(
            status=status.HTTP_201_CREATED,
        )

    def put(self, request):
        test = get_object_or_404(Test, course=request.data["course"], test_number=request.data["id"])
        serializer = self.serializer_class(test, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        test = get_object_or_404(Test, course=request.query_params["course"],
                                 test_number=request.query_params["test_number"])
        tests = Test.objects.filter(test_number__gt=test.test_number, course__id=test.course_id)
        tests.update(test_number=F("test_number") - 1)
        test.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

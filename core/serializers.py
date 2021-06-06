from rest_framework import serializers

from service_auth.models import Student
from service_auth.serializers import CustomUserSerializer
from .models import Course, Media, Lesson, CourseProgress, Test, Answer


class CourseListSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField(read_only=True)

    def get_lessons(self, instance):
        return instance.lessons.count()

    class Meta:
        model = Course
        fields = ['id', 'name', 'img', 'lessons']


class MediaSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        pass

    class Meta:
        model = Media
        fields = '__all__'


class LessonSerializer(serializers.ModelSerializer):
    medias = MediaSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = ['medias', 'course', 'lesson_number']


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["text", "correct"]


class TestSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Test
        fields = ['course', 'question', 'answers', 'test_number']

    def create(self, validated_data):
        last_id = Test.objects.last().id
        test = Test.objects.create(id=last_id + 1, **validated_data)
        validated_data = validated_data.pop("questions")
        validated_data = validated_data.pop("course")
        for answer in validated_data["answers"]:
            Answer.objects.create(cases_id=test, **validated_data)


class CourseSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return Course.objects.create(**validated_data)

    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'img']


class StudentSerializer(serializers.ModelSerializer):
    personal = CustomUserSerializer(read_only=True)
    last_name = serializers.CharField(allow_null=False)
    city = serializers.CharField(allow_null=False)
    position = serializers.CharField(allow_null=False)
    job = serializers.CharField(allow_null=False)

    class Meta:
        model = Student
        fields = ['personal', 'last_name', 'city', 'job', 'position']


class CourseProgressSerializer(serializers.ModelSerializer):
    course = serializers.SlugRelatedField(slug_field='name', read_only=True)
    student = StudentSerializer(read_only=True)

    class Meta:
        model = CourseProgress
        fields = ['course', 'test_passed', 'current_lesson', 'current_test', 'student']

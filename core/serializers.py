from rest_framework import serializers

from service_auth.models import Student
from service_auth.serializers import CustomUserSerializer
from .models import Course, Media, Lesson, CourseProgress, Test, Answer


class CourseListSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField(read_only=True)
    img = serializers.FileField(required=False, allow_null=True)

    def get_lessons(self, instance):
        return instance.lessons.count()

    class Meta:
        model = Course
        fields = ['id', 'name', 'img', 'lessons']


class MediaSerializer(serializers.ModelSerializer):
    content = serializers.FileField(write_only=True)
    title = serializers.CharField(allow_blank=True)
    body = serializers.CharField(allow_blank=True)

    def to_internal_value(self, data):
        return super().to_internal_value(data)

    class Meta:
        model = Media
        fields = ['title', 'body', 'content']


class LessonSerializer(serializers.ModelSerializer):
    content = MediaSerializer()

    def create(self, validated_data):
        last_id = Lesson.objects.filter(course=validated_data["course"]).last()
        media = validated_data.pop("content")
        lesson = Lesson.objects.create(lesson_number=last_id.lesson_number + 1 if last_id else 1, **validated_data)

        Media.objects.create(lesson=lesson, title=media["title"], body=media["body"])
        return lesson

    class Meta:
        model = Lesson
        fields = ['course', 'lesson_number', 'content']


class AnswerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Answer
        fields = ["text", "correct", "id"]


class TestSerializer(serializers.ModelSerializer):
    answers = serializers.ListSerializer(child=AnswerSerializer())

    class Meta:
        model = Test
        fields = ['course', 'question', 'answers', 'test_number']

    def update(self, instance, validated_data):
        instance.question = validated_data.get('question', instance.question)
        instance.save()

        answers = validated_data.get('answers')
        for i, answer in enumerate(answers):
            ans = Answer.objects.get(number=i + 1, cases=instance)
            ans.text = answer.get('text', ans.text)
            ans.correct = answer.get('correct', ans.correct)
            ans.save()

        return instance

    def create(self, validated_data):
        last_id = Test.objects.filter(course=validated_data["course"]).last()
        answers = validated_data.pop("answers")
        test = Test.objects.create(test_number=last_id.test_number + 1 if last_id else 1, **validated_data)
        for answer in answers:
            Answer.objects.create(cases=test, text=answer["text"], correct=answer["correct"])
        return test


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

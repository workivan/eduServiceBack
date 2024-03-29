from rest_framework import serializers

from service_auth.serializers import StudentSerializer
from .models import Course, Media, Lesson, CourseProgress, Test, Answer


class CourseListSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField(read_only=True)
    tests_count = serializers.SerializerMethodField(read_only=True)
    img = serializers.FileField(required=False)

    def get_lessons_count(self, obj):
        les = obj.lessons.count()
        return les

    def get_tests_count(self, obj):
        tes = obj.tests.count()
        return tes

    class Meta:
        model = Course
        fields = ['id', 'name', 'img', "lessons_count", "tests_count"]


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['title', 'body']


class LessonSerializer(serializers.ModelSerializer):
    content = MediaSerializer()
    name = serializers.CharField(max_length=100, allow_null=False, allow_blank=False)
    course = serializers.UUIDField(write_only=True)

    def create(self, validated_data):
        last_id = Lesson.objects.filter(course__id=validated_data["course"]).last()
        media = validated_data.pop("content")
        validated_data["course"] = Course.objects.get(id=validated_data.get("course"))
        lesson = Lesson.objects.create(lesson_number=last_id.lesson_number + 1 if last_id else 1, **validated_data)

        Media.objects.create(lesson=lesson, title=media["title"], body=media["body"])
        return lesson

    def update(self, instance, validated_data):
        instance.course = Course.objects.get(id=validated_data.get("course"))
        content = validated_data["content"]
        instance.content.title = content.get("title", instance.content.title)
        instance.content.body = content.get("body", instance.content.body)
        instance.name = validated_data["name"]
        instance.content.save()
        instance.save()

        return instance

    class Meta:
        model = Lesson
        fields = ['course', 'lesson_number', 'content', 'name']


class AnswerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    correct = serializers.BooleanField(write_only=True)

    class Meta:
        model = Answer
        fields = ["text", "id", "correct"]


class CheckAnswerSetializer(serializers.Serializer):
    course_id = serializers.UUIDField(required=True)
    username = serializers.CharField(required=True)
    test_id = serializers.IntegerField(required=True)
    answer_id = serializers.IntegerField(required=True)


class TestSerializer(serializers.ModelSerializer):
    answers = serializers.ListSerializer(child=AnswerSerializer())
    test_number = serializers.IntegerField(read_only=True)

    class Meta:
        model = Test
        fields = ['question', 'answers', 'test_number', 'course']

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
        for i, answer in enumerate(answers):
            Answer.objects.create(number=i + 1, cases=test, text=answer["text"], correct=bool(answer["correct"]))
        return test


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField(read_only=True)
    lessons_names = serializers.SerializerMethodField(read_only=True)
    tests_count = serializers.SerializerMethodField(read_only=True)
    img = serializers.FileField(required=False)

    def get_lessons_count(self, obj):
        les = obj.lessons.count()
        return les

    def get_lessons_names(self, obj):
        lessons = obj.lessons.order_by("lesson_number")
        names = [value.get("name") for value in lessons.values("name")]
        return names

    def get_tests_count(self, obj):
        tes = obj.tests.count()
        return tes

    def create(self, validated_data):
        return Course.objects.create(**validated_data)

    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'img', "lessons_count", "tests_count", "lessons_names"]


class CourseProgressSerializer(serializers.ModelSerializer):
    course = serializers.SlugRelatedField(slug_field='name', read_only=True)
    student = StudentSerializer(read_only=True)

    class Meta:
        model = CourseProgress
        fields = ['course', 'test_passed', 'current_lesson', 'current_test', 'student', 'display', "test_result"]

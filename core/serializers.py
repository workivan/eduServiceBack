from django.http import HttpRequest
from .models import Course, Media, Lesson

from rest_framework import serializers


class CourseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'img']


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = '__all__'


class LessonSerializer(serializers.ModelSerializer):
    medias = MediaSerializer(many=True, read_only=True)

    @staticmethod
    def get_img_abs_url(obj):
        img = obj.img.url
        return img

    class Meta:
        model = Lesson
        fields = ['lesson_number', 'course']


class CourseSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return Course.objects.create(**validated_data)

    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'img', 'lessons']

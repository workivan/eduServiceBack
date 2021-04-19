from .models import Course, Media, MediaType

from rest_framework import serializers


class CourseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['course_id', 'name', 'img']


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    medias = MediaSerializer(many=True, read_only=True)

    def create(self, validated_data):
        return Course.objects.create(**validated_data)

    class Meta:
        model = Course
        fields = ['course_id', 'name', 'description', 'img', 'medias']

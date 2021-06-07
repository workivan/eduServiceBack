import uuid

from django.db import models

from service_auth.models import Student


def upload_to(instance, filename):
    return '/'.join(['cards', str(instance.id)])


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=512, null=False)
    img = models.ImageField(upload_to=upload_to, null=True)
    students = models.ManyToManyField("service_auth.Student")
    description = models.TextField(max_length=1024, null=True)

    objects = models.Manager()


class Test(models.Model):
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, default=uuid.uuid4)
    question = models.TextField(max_length=1024, null=False, default="?")
    test_number = models.SmallIntegerField(default=0)

    objects = models.Manager()


class Answer(models.Model):
    number = models.SmallIntegerField(default=1)
    text = models.TextField(max_length=1024, null=False, default="ок")
    correct = models.BooleanField(default=False)
    cases = models.ForeignKey(Test, related_name="answers", on_delete=models.DO_NOTHING)

    objects = models.Manager()


class Lesson(models.Model):
    lesson_number = models.SmallIntegerField(default=0)
    course = models.ForeignKey("Course", related_name="lessons", on_delete=models.DO_NOTHING)


class Media(models.Model):
    title = models.TextField(max_length=128, null=False, default="empty")
    body = models.TextField(null=False, default="empty")
    lesson = models.OneToOneField(Lesson, related_name="content", default=1, on_delete=models.DO_NOTHING)

    objects = models.Manager()


class CourseProgress(models.Model):
    course = models.OneToOneField(Course, on_delete=models.DO_NOTHING, null=False)
    student = models.OneToOneField(Student, on_delete=models.DO_NOTHING, null=False)
    test_passed = models.BooleanField(default=False)
    current_lesson = models.SmallIntegerField(default=0)
    current_test = models.SmallIntegerField(default=0)

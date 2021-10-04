import uuid

from django.db import models

from service_auth.models import Student


class CourseProgress(models.Model):
    course = models.ForeignKey("Course", on_delete=models.CASCADE, related_name="course_progresses", null=False)
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING, related_name="st_progresses", null=False)
    test_passed = models.BooleanField(default=False)
    current_lesson = models.SmallIntegerField(default=1)
    display = models.BooleanField(default=True)
    current_test = models.SmallIntegerField(default=1)
    test_result = models.SmallIntegerField(default=0)



def upload_to(instance, filename):
    return '/'.join(['cards', str(instance.id)])


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=512, null=True)
    img = models.ImageField(upload_to=upload_to)
    description = models.TextField(max_length=1024, null=True)

    objects = models.Manager()


class Test(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="tests")
    question = models.TextField(max_length=1024, null=False)
    test_number = models.SmallIntegerField()

    objects = models.Manager()


class Answer(models.Model):
    number = models.SmallIntegerField(default=1)
    text = models.TextField(max_length=1024)
    correct = models.BooleanField(default=False)
    cases = models.ForeignKey(Test, related_name="answers", on_delete=models.CASCADE)

    objects = models.Manager()


class Lesson(models.Model):
    name = models.CharField(max_length=100, null=False, default="Урок")
    lesson_number = models.SmallIntegerField(default=0)
    course = models.ForeignKey("Course", related_name="lessons", on_delete=models.CASCADE)


class Media(models.Model):
    title = models.TextField(max_length=128, null=False, default="empty")
    body = models.TextField(null=False, default="empty")
    lesson = models.OneToOneField(Lesson, related_name="content", default=1, on_delete=models.CASCADE)
    objects = models.Manager()

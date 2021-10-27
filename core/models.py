import uuid

from django.db import models

from service_auth.models import Student


class CourseProgress(models.Model):
    course = models.ForeignKey("Course", on_delete=models.CASCADE, related_name="course_progresses", null=False)
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING, related_name="st_progresses", null=False)
    test_passed = models.BooleanField(default=False, verbose_name="сдан тест")
    current_lesson = models.SmallIntegerField(default=1)
    display = models.BooleanField(default=True)
    current_test = models.SmallIntegerField(default=1)
    test_result = models.SmallIntegerField(default=0, verbose_name="кол-во верных ответов")

    def __str__(self):
        return "прогресс по курсу - " + self.course.__str__() + " для студента - " + self.student.__str__()

    class Meta:
        verbose_name_plural = "Прогресс учащихся"


def upload_to(instance, filename):
    return '/'.join(['cards', str(instance.id)])


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=512, null=True, verbose_name="название")
    img = models.ImageField(upload_to=upload_to, verbose_name="изображение")
    description = models.TextField(max_length=1024, null=True)

    objects = models.Manager()

    def __str__(self):
        return "название курса - " + self.name

    class Meta:
        verbose_name_plural = "Курсы"


class Test(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="tests")
    question = models.TextField(max_length=1024, null=False, verbose_name="вопрос")
    test_number = models.SmallIntegerField()

    objects = models.Manager()

    def __str__(self):
        return "вопрос - " + self.question

    class Meta:
        verbose_name_plural = "Тестирование"


class Answer(models.Model):
    number = models.SmallIntegerField(default=1)
    text = models.TextField(max_length=1024)
    correct = models.BooleanField(default=False)
    cases = models.ForeignKey(Test, related_name="answers", on_delete=models.CASCADE)

    objects = models.Manager()

    class Meta:
        verbose_name_plural = "Ответы на тестирование"


class Lesson(models.Model):
    name = models.CharField(max_length=100, null=False, default="Урок")
    lesson_number = models.SmallIntegerField(default=0)
    course = models.ForeignKey("Course", related_name="lessons", on_delete=models.CASCADE)

    def __str__(self):
        return "название урока - " + self.name

    class Meta:
        verbose_name_plural = "Уроки"


class Media(models.Model):
    title = models.TextField(max_length=128, null=False, default="empty")
    body = models.TextField(null=False, default="empty")
    lesson = models.OneToOneField(Lesson, related_name="content", default=1, on_delete=models.CASCADE)
    objects = models.Manager()

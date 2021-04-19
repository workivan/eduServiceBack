import uuid

from django.db import models

from service_auth.models import Student


class Course(models.Model):
    course_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=512, null=False)
    img = models.ImageField(upload_to="cards")
    students = models.ManyToManyField("service_auth.Student")
    description = models.TextField(max_length=1024, null=False)

    objects = models.Manager()


class Test(models.Model):
    student = models.OneToOneField("service_auth.Student", on_delete=models.DO_NOTHING)
    date = models.DateField(auto_created=True)
    success = models.BooleanField()

    objects = models.Manager()


class Case(models.Model):
    course = models.ForeignKey("Course", on_delete=models.DO_NOTHING)
    question = models.TextField(max_length=1024, null=False)
    answers = models.ForeignKey("Answer", on_delete=models.DO_NOTHING)

    objects = models.Manager()


class Answer(models.Model):
    text = models.TextField(max_length=1024, null=False)
    correct = models.BooleanField(default=False)
    cases = models.ForeignKey("Case", on_delete=models.DO_NOTHING)

    objects = models.Manager()


class MediaType(models.TextChoices):
    pdf = "PDF"
    video = "VIDEO"


class Media(models.Model):
    name = models.TextField(max_length=128, null=False)
    type = models.CharField(max_length=10, choices=MediaType.choices, default=MediaType.pdf)
    file = models.FileField(upload_to="files")
    course = models.ForeignKey("Course", related_name="medias", on_delete=models.DO_NOTHING)

    objects = models.Manager()

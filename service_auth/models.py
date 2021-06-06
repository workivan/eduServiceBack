import jwt
from datetime import datetime
from datetime import timedelta

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)


class UserManager(BaseUserManager):
    def _create_user(self, username, password=None, name=None, **extra_fields):
        if not username:
            raise ValueError('username is empty')

        user = self.model(name=name, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, username, password=None, name=None, **extra_fields):
        extra_fields.setdefault('is_admin', False)

        return self._create_user(username, password, name, **extra_fields)

    def create_superuser(self, username, password, name=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)

        if extra_fields.get('is_admin') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')

        return self._create_user(username, password, name, **extra_fields)


class UserType(models.TextChoices):
    keeper = "KP", _("KEEPER")
    student = "ST", _("STUDENT")
    owner = "OW", _("OWNER")


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        max_length=255,
        primary_key=True,
        unique=True,
        verbose_name="login"
    )
    name = models.CharField(
        max_length=64,
        verbose_name="name",
        null=False
    )
    surname = models.CharField(
        max_length=64,
        verbose_name="surname",
        null=False
    )
    user_type = models.CharField(max_length=50, choices=UserType.choices, default=UserType.keeper)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'username'

    @property
    def token(self):
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        dt = datetime.now() + timedelta(days=60)
        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')
        return token.decode('utf-8')


class Personal(models.Model):
    personal = models.OneToOneField(CustomUser, on_delete=models.CASCADE, rel="user")


class Keeper(Personal):
    pass


class Student(Personal):
    city = models.CharField(
        max_length=64,
        verbose_name="Город",
        null=False
    )
    last_name = models.CharField(
        max_length=64,
        verbose_name="Отчество",
        null=False,
        default="empty"
    )
    job = models.TextField(
        null=False,
        default="empty",
        verbose_name="Место работы"
    )
    position = models.TextField(
        null=False,
        default="empty",
        verbose_name="Должность"
    )

    @property
    def full_name(self):
        return self.personal.name + " " + self.personal.surname + " " + self.last_name


class Owner(Personal):
    pass

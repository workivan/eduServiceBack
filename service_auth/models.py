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
        user = self._create_user(username, password, name, **extra_fields)
        return user

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
        verbose_name="логин"
    )
    name = models.CharField(
        max_length=64,
        verbose_name="имя",
        null=False
    )
    surname = models.CharField(
        max_length=64,
        verbose_name="фамилия",
        null=False
    )
    user_type = models.CharField(max_length=50,
                                 choices=UserType.choices,
                                 default=UserType.keeper,
                                 verbose_name="тип пользователя")
    is_admin = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'username'

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        if self.is_admin:
            return True
        return False

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        if self.is_admin:
            return True
        return False

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

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

    def __str__(self):
        return self.name + " " + self.surname + " " + self.user.last_name

    class Meta:
        verbose_name_plural = "Пользователи"


class Student(models.Model):
    personal = models.OneToOneField(CustomUser, on_delete=models.DO_NOTHING, related_name="user")
    city = models.CharField(
        max_length=64,
        verbose_name="Город",
        null=False,
        default="-"
    )
    last_name = models.CharField(
        max_length=64,
        verbose_name="Отчество",
        null=False,
        default="-"
    )
    place = models.TextField(
        null=False,
        default="-",
        verbose_name="Место работы"
    )
    job = models.TextField(
        null=False,
        default="-",
        verbose_name="Должность"
    )
    control = models.CharField(
        max_length=64,
        null=False,
        default="-"
    )

    def __str__(self):
        return self.personal.name + " " + self.last_name

    @property
    def full_name(self):
        return self.personal.name + " " + self.personal.surname + " " + self.last_name

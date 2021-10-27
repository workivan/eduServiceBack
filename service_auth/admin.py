from django.contrib import admin

from service_auth.models import Student, CustomUser


class StudentInline(admin.StackedInline):
    model = Student


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    inlines = [StudentInline]
    fields = ("username", "name", "surname", "user_type")

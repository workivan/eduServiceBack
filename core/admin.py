from django.contrib import admin

from core.models import CourseProgress, Course, Test, Answer, Lesson


@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    list_display = ('course', 'student')
    fields = ('test_passed', 'test_result')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    fields = ('name', 'img')


class AnswerInline(admin.TabularInline):
    model = Answer


@admin.register(Test)
class TestInlines(admin.ModelAdmin):
    inlines = [AnswerInline]
    fields = ('question',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('course', "lesson_number")
    fields = ('name',)

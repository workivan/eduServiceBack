import mammoth
import re

from .models import CourseProgress, Course, Test


def get_content_from_file(file):
    result = mammoth.convert_to_html(file)
    return {
        "title":
            re.sub("docx", "", file.name),
        "body": result.value
    }


def set_lessons_content(content):
    return {
        "title": content.title,
        "body": content.body
    }


def get_current_test_number(course_id, username):
    progress = CourseProgress.objects.get(course=course_id, student__personal__username=username)
    count_of_test = Course.objects.get(id=course_id).tests.count()
    if progress.current_test < count_of_test + 1:
        return progress.current_test
    return None


def check_answr_correct(course_id, test_number, answer_id):
    test = Test.objects.get(course__id=course_id, test_number=test_number)
    answer = test.answers.get(correct=True)
    if answer.id == answer_id:
        return True
    return False


def update_result(correct, progress, count_of_test):
    if correct:
        progress.test_result += 1
    if progress.test_result > count_of_test * 0.65:
        progress.test_passed = True
    progress.current_test += 1
    progress.save()

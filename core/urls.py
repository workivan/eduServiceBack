"""eduService URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from .views import CourseListAPIView, CourseAPIView, StudentListAPIView, CourseProgressAPIView, TestAPIView, \
    LessonAPIView, CheckAnswerAPI, StudentRetrieveAPIView

urlpatterns = [
    path('courses_list/', CourseListAPIView.as_view()),
    path('course/', CourseAPIView.as_view()),
    path('course/lessons/edit/', LessonAPIView.as_view()),
    path('course/tests/edit/', TestAPIView.as_view()),
    path('course/tests/check/', CheckAnswerAPI.as_view()),
    path('course/students/', StudentListAPIView.as_view()),
    path('course/student/', StudentRetrieveAPIView.as_view()),
    path('progress/', CourseProgressAPIView.as_view())
]

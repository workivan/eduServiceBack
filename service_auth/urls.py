from django.urls import path

from .views import LoginAPIView, RegistrationAPIView, UserRetrieveAPIView, StudentsCreationAPIView, \
    StudentUpdateAPIView, StudentDeleteAPIView

urlpatterns = [
    path('login/', LoginAPIView.as_view()),
    path('get_user/', UserRetrieveAPIView.as_view()),
    path('add_user/', RegistrationAPIView.as_view()),
    path('edit_student/', StudentUpdateAPIView.as_view()),
    path('del_student/', StudentDeleteAPIView.as_view()),
    path('add_student/', StudentsCreationAPIView.as_view()),
]

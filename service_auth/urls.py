from django.urls import path

from .views import LoginAPIView, RegistrationAPIView, UserRetrieveAPIView, StudentsCreationAPIView

urlpatterns = [
    path('login/', LoginAPIView.as_view()),
    path('get_user/', UserRetrieveAPIView.as_view()),
    path('add_user/', RegistrationAPIView.as_view()),
    path('add_student/', StudentsCreationAPIView.as_view()),
]

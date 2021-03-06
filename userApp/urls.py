from .views import UserSignupView, LoginAPI, CompanyListAPIView, GoalView
from django.urls import path


urlpatterns = [
    path('companylist/', CompanyListAPIView.as_view()),
    path('signup/', UserSignupView.as_view()),
    path('signup/<int:pk>/', UserSignupView.as_view()),
    path('login/', LoginAPI),
    path('goal/', GoalView.as_view()),
    path('goal/<int:pk>/', GoalView.as_view()),
]
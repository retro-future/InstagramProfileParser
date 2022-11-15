from django.urls import path

from user_profile.views import ProfilePage

urlpatterns = [
    path('profiles/<str:username>/', ProfilePage.as_view()),
]


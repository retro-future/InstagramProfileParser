from django.urls import path

from user_profile.views import ProfilePage, ParserPage, done

urlpatterns = [
    path('profiles/<str:username>/', ProfilePage.as_view()),
    path('profiles/', ProfilePage.as_view()),
    path('parser/', ParserPage.as_view()),
    path('done/', done),
]


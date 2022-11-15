from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from user_profile.services.profile_service import ProfileService


class ProfilePage(View):
    def get(self, request: HttpRequest, username: str) -> HttpResponse:
        profile_service = ProfileService()
        profile, posts = profile_service.get_profile_and_posts(username=username)
        context = {"username": username, "posts": posts, "avatar": profile.avatar}
        return render(request, "user_profile/profile.html", context=context)


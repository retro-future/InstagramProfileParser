from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from instagram_parser.tasks import processParsing
from user_profile.services.profile_service import ProfileService


class ProfilePage(View):

    def __init__(self, *args, **kwargs):
        self.profile_service = ProfileService()
        super().__init__(*args, **kwargs)

    def get(self, request: HttpRequest, username: str) -> HttpResponse:
        profile, posts = self.profile_service.get_profile_and_posts(username=username)
        context = {"username": username, "posts": posts, "avatar": profile.avatar}
        return render(request, "user_profile/profile.html", context=context)

    def post(self, request: HttpRequest):
        username = request.POST.get("username")
        parse_task = processParsing.delay(username)
        task_id = parse_task.task_id
        print(f'Celery Task ID: {task_id}')
        return render(request, "user_profile/done.html", {"task_id": task_id})


class ParserPage(View):
    def get(self, request):
        return render(request, "user_profile/parser.html")


def done(request):
    return render(request, "user_profile/done.html")

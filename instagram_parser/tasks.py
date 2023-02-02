from functools import partial
from typing import Callable

from environs import Env
from celery import shared_task
from celery_progress.backend import ProgressRecorder
from selenium import webdriver

from instagram_parser.ig_authorization import InstagramAuth
from instagram_parser.parsers.header_parser import HeaderParse
from instagram_parser.parsers.user_posts_parser import PostsParser
from user_profile.services.profile_service import ProfileService

env = Env()
env.read_env()


@shared_task(bind=True)
def processParsing(self, username: str) -> None:
    profile_service = ProfileService()
    UserIG = InstagramAuth(webdriver.Chrome())
    UserIG.login(env.str("IG_USERNAME"), env.str("IG_PASSWORD"))
    user_page = UserIG.get_profile_page(f"https://www.instagram.com/{username}/")
    user_header = HeaderParse(user_page)
    basic_info = user_header.get_basic_info()
    Posts = PostsParser(UserIG.driver, partial(update_progress_v2, total=basic_info.posts_count, task_instance=self,
                                               description="Parsing posts"))
    srcs = Posts.parse_posts_links()
    UserIG.close_browser()
    profile_service.save_posts_to_db(username, basic_info.avatar_url, srcs,
                                     partial(update_progress_v2, total=basic_info.posts_count, task_instance=self,
                                             description="Parsing posts"))


def update_progress_v2(current: int, total: int, task_instance, description: str = "") -> None:
    progress_recorder = ProgressRecorder(task_instance)
    progress_recorder.set_progress(current, total, description=description)

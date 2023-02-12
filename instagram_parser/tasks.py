import asyncio
import dataclasses
from dataclasses import dataclass
from functools import partial
from typing import Iterable

from celery import shared_task
from celery_progress.backend import ProgressRecorder

from insta_clone import env
from instagram_parser.instagram_auth import InstagramAuth
from instagram_parser.parsers.header_parser import HeaderParse
from instagram_parser.parsers.user_posts_parser import PostsParser
from user_profile.services.profile_service import ProfileService, AsyncDownloader


@dataclass
class ParsedData:
    username: str
    avatar_url: str
    posts_urls: Iterable[str]


@shared_task(bind=True)
def processParsing(self, username: str):
    Instagram_bot = InstagramAuth(env.str("IG_USERNAME"), env.str("IG_PASSWORD"))
    Instagram_bot.login()
    user_page = Instagram_bot.get_profile_page(f"https://www.instagram.com/{username}/")
    user_header = HeaderParse(user_page)
    basic_info = user_header.get_basic_info()
    Posts = PostsParser(Instagram_bot.driver, partial(update_progress_v2,
                                                      total=basic_info.posts_count,
                                                      task_instance=self,
                                                      description="Parsing posts"))
    urls = Posts.parse_posts()
    Instagram_bot.close_browser()
    return dataclasses.asdict(ParsedData(username=username, avatar_url=basic_info.avatar_url, posts_urls=urls))


@shared_task(bind=True)
def process_save_to_db(self, data: dict) -> None:
    username = data.get("username")
    avatar_url = data.get("avatar_url")
    posts_urls = data.get("posts_urls")
    downloader = AsyncDownloader()
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(downloader.async_download_images(posts_urls))
    profile_service = ProfileService(partial(update_progress_v2,
                                             total=len(posts_urls),
                                             task_instance=self,
                                             description="Downloading posts"))
    profile_service.save_to_db(username, avatar_url, result)


def update_progress_v2(current: int, total: int, task_instance, description: str = "") -> None:
    progress_recorder = ProgressRecorder(task_instance)
    progress_recorder.set_progress(current, total, description=description)

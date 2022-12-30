from collections import namedtuple
from io import BytesIO
from typing import List

import requests
from django.utils.crypto import get_random_string
from environs import Env
from loguru import logger
from selenium import webdriver

from instagram_parser.ig_authorization import InstagramAuth
from instagram_parser.parsers.header_parser import HeaderParse
from instagram_parser.parsers.user_posts_parser import PostsParser

try:
    from instagram_parser import setup_django_orm  # should be before models import
except RuntimeError:
    pass

from user_profile.models import Profile, Post
from django.core.files.images import ImageFile

env = Env()
env.read_env()


class CannotLoadImage(Exception):
    pass


def download_image(url: str) -> bytes:
    response = requests.get(url)
    if response.status_code != 200:
        raise CannotLoadImage
    return response.content


class ProfileService:

    @staticmethod
    def _create_profile_instance(username: str, avatar_url: str) -> Profile:
        instance, _ = Profile.objects.get_or_create(username=username)
        avatar = ImageFile(BytesIO(download_image(avatar_url)), name="avatar.jpg")
        instance.avatar = avatar
        instance.save()
        return instance

    @staticmethod
    def _create_posts(profile_instance: Profile, url_list: List[str]) -> List[Post]:
        posts: List[Post] = []
        if url_list:
            for index, url in enumerate(url_list):
                filename = f"{index}_{get_random_string(30)}.jpg"
                image = ImageFile(BytesIO(download_image(url)), name=filename)
                posts.append(Post(author=profile_instance, image_url=url, image=image))
        return posts

    def save_posts_to_db(self, username: str, avatar_url: str, url_list: List[str]) -> Profile:
        profile_instance = self._create_profile_instance(username, avatar_url)
        posts = self._create_posts(profile_instance=profile_instance, url_list=url_list)
        Post.objects.bulk_create(posts)
        logger.info("Created")
        return profile_instance

    def get_profile_and_posts(self, username: str) -> tuple:
        profile = Profile.objects.get(username=username)
        posts = profile.user_images.all()
        return profile, posts

    def parse_profile(self, username: str):
        UserIG = InstagramAuth(webdriver.Chrome())
        UserIG.login(env.str("IG_USERNAME"), env.str("IG_PASSWORD"))
        user_page = UserIG.get_profile_page(f"https://www.instagram.com/{username}/")
        Posts = PostsParser(UserIG.driver)
        srcs = Posts.parse_posts_links()
        user_header = HeaderParse(user_page)
        avatar_url = user_header.parse_avatar_url()
        UserIG.close_browser()
        print(user_header.get_basic_info())
        print(srcs)
        print(len(srcs))
        return avatar_url, srcs

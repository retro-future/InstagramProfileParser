from io import BytesIO
from typing import List, Callable

import requests
from django.utils.crypto import get_random_string
from loguru import logger

try:
    from instagram_parser import setup_django_orm  # should be before models import
except RuntimeError:
    pass

from user_profile.models import Profile, Post
from django.core.files.images import ImageFile


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
        return instance

    @staticmethod
    def _create_posts(profile_instance: Profile, url_list: List[str], progress_function: Callable) -> List[Post]:
        posts: List[Post] = []
        if url_list:
            for index, url in enumerate(url_list):
                filename = f"{index}_{get_random_string(30)}.jpg"
                image = ImageFile(BytesIO(download_image(url)), name=filename)
                progress_function(index)
                posts.append(Post(author=profile_instance, image_url=url, image=image))
        return posts

    def save_posts_to_db(self, username: str, avatar_url: str, url_list: List[str],
                         progress_function: Callable) -> Profile:
        profile_instance = self._create_profile_instance(username, avatar_url)
        posts = self._create_posts(profile_instance=profile_instance, url_list=url_list,
                                   progress_function=progress_function)
        profile_instance.save()
        Post.objects.bulk_create(posts)
        logger.info("Created")
        return profile_instance

    def get_profile_and_posts(self, username: str) -> tuple:
        profile = Profile.objects.prefetch_related("user_posts").get(username=username)
        posts = profile.user_posts.all()
        return profile, posts

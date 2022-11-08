import requests
from io import BytesIO
from typing import List

from django.core.files.images import ImageFile
from django.utils.crypto import get_random_string
from loguru import logger

from instagram_parser import setup_django_orm

from user_profile.models import Profile, Post


def download_image(url: str) -> BytesIO:
    response = requests.get(url)
    if response.status_code == 200:
        return BytesIO(response.content)


def save_posts_to_db(username: str, avatar_url: str, url_list: List[str]) -> Profile:
    profile_instance = _create_profile_instance(username, avatar_url)
    _create_posts(profile_instance=profile_instance, url_list=url_list)
    return profile_instance


def _create_profile_instance(username: str, avatar_url: str) -> Profile:
    instance, status = Profile.objects.get_or_create(username=username)
    if status:
        image = ImageFile(download_image(avatar_url), name="avatar.jpg")
        instance.avatar = image
        instance.save()
    return instance


def _create_posts(profile_instance: Profile, url_list: List[str]) -> None:
    if url_list:
        for index, url in enumerate(url_list):
            filename = f"{index}_{get_random_string(30)}.jpg"
            image = ImageFile(download_image(url), name=filename)
            Post.objects.create(author=profile_instance, image_url=url, image=image)
    logger.info("Created")



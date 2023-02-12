import asyncio
from io import BytesIO
import time
from typing import List, Callable, Dict

import aiohttp
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

    def __init__(self, progress_updater: Callable[[int], None] = None):
        self.progress_updater = progress_updater
        self.posts: List[Post] = list()

    @staticmethod
    def _create_profile_instance(username: str, avatar_url: str) -> Profile:
        instance, _ = Profile.objects.get_or_create(username=username)
        avatar = ImageFile(BytesIO(download_image(avatar_url)), name="avatar.jpg")
        instance.avatar = avatar
        return instance

    def _create_posts(self, profile_instance: Profile, images: Dict[str, bytes]) -> None:
        for index, (url, image_bytes) in enumerate(images.items()):
            filename = f"{index}_{get_random_string(30)}.jpg"
            image = ImageFile(BytesIO(image_bytes), name=filename)
            self.posts.append(Post(author=profile_instance, image_url=url, image=image))
            self.progress_updater(index)

    def save_to_db(self, username: str, avatar_url: str, images: Dict[str, bytes]) -> None:
        profile_instance = self._create_profile_instance(username, avatar_url)
        self._create_posts(profile_instance=profile_instance, images=images)
        profile_instance.save()
        Post.objects.bulk_create(self.posts)
        logger.info("Created")

    def get_profile_and_posts(self, username: str) -> tuple:
        profile = Profile.objects.prefetch_related("user_posts").get(username=username)
        posts = profile.user_posts.all()
        return profile, posts


class AsyncDownloader:
    def __init__(self, semaphore_init: int = 15):
        self.downloaded_images: Dict[str, bytes] = dict()
        self.semaphore = asyncio.Semaphore(semaphore_init)

    async def async_download_image(self, image_url: str) -> None:
        async with self.semaphore:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as res:
                    self.downloaded_images[image_url] = await res.read()

    async def async_download_images(self, image_urls: List[str]) -> Dict[str, bytes]:
        tasks = [asyncio.create_task(self.async_download_image(url)) for url in image_urls]
        s = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - s
        print("*" * 50)
        print(f"{__file__} executed in {elapsed:0.2f} seconds.")
        print("*" * 50)
        return self.downloaded_images

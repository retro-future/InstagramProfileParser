from django.contrib.auth.models import User
from django.db import models
from django.utils.crypto import get_random_string
from datetime import datetime


def user_posts_directory(self, filename) -> str:
    date = datetime.utcnow().strftime("%d-%m-%Y")
    return f'profile_pictures/{self.author.username}/posts/{date}/{filename}'


def profile_avatars_directory(self, filename) -> str:
    date = datetime.utcnow().strftime("%d-%m-%Y")
    return f'profile_pictures/{self.username}/avatars/{date}/{filename}'


class Profile(models.Model):
    username = models.CharField(max_length=50)
    avatar = models.ImageField(default="default.jpg", upload_to=profile_avatars_directory)

    def __str__(self):
        return f"{self.username}"


class Post(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="user_posts")
    image_url = models.TextField()
    image = models.ImageField(upload_to=user_posts_directory)

    def __str__(self):
        return str(self.id)


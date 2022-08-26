from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default="default.jpg", upload_to="profile_pics")
    bio = models.CharField(max_length=150, blank=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"


class Follower(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    being_followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name="being_followed")
    date_followed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.follower.username, self.being_followed.username} follower -> follows"


class Post(models.Model):
    caption = models.CharField(max_length=2500, blank=True)
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.caption


class PostImage(models.Model):
    post = models.ForeignKey(Post, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to="post_images")


class Comments(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    content = models.CharField(max_length=500, blank=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content


class Like(models.Model):
    liker = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    date_created = models.DateTimeField(auto_now_add=True)

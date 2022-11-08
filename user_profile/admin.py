from django.contrib import admin

from user_profile.models import Profile, Post


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "username")
    list_display_links = ("username",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("author", "image_url")
    list_display_links = ("author",)

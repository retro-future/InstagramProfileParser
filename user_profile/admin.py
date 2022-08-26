from django.contrib import admin

from user_profile.models import Profile, Follower


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "first_name", "last_name")
    list_display_links = ("user",)


@admin.register(Follower)
class FollowerAdmin(admin.ModelAdmin):
    list_display = ("id", "follower", "being_followed")

from celery import shared_task

from user_profile.services.profile_service import ProfileService


@shared_task(bind=True)
def processParsing(self, username: str):
    profile_service = ProfileService()
    avatar_url, posts_url = profile_service.parse_profile(username)
    profile_service.save_posts_to_db(username, avatar_url, posts_url)

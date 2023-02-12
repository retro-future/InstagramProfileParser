# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery_setup import app as celery_app
from .config import env

__all__ = ('celery_app', 'env')
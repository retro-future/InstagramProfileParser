import django
from django.conf import settings
from environs import Env

from insta_clone.settings import BASE_DIR, DATABASE, PGUSER, PGPASSWORD, DB_Ip

settings.configure(
    DATABASES={

        'default': {

            'ENGINE': 'django.db.backends.postgresql_psycopg2',

            'NAME': DATABASE,

            'USER': PGUSER,

            'PASSWORD': PGPASSWORD,

            'HOST': DB_Ip,

            'PORT': 5432,

        }

    },

    INSTALLED_APPS=[
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'user_profile',
    ],
    MEDIA_URL="/media/",
    MEDIA_ROOT=BASE_DIR / 'media'
)

django.setup()
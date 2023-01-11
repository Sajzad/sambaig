import os
from .settings import *



INTERNAL_IP='127.0.0.1'

DEBUG = False

SECRET_KEY = os.environ["SECRET_KEY"]

ALLOWED_HOSTS = [".faxsmart.net", "faxsmart.net", "67.223.117.189", "127.0.0.1"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DATABASES = {
    "default": {
        "ENGINE": 'django.db.backends.postgresql_psycopg2',
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        # "ATOMIC_REQUESTS": True,
        "HOST": "localhost",
        "PORT": "",
        "CONN_MAX_AGE": 2000,
    }
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        # "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "base.context.unread_count",
                "base.context.notifications",
            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
        },
    },
]

# custom timezone
TIME_ZONE = 'America/Panama'
USE_TZ = False

# Cron job
CRONJOBS = [
    ('*/5 * * * *', 'responder.cron.my_scheduled_job', '>> /tmp/scheduled_job.log'),
    ('*/3 * * * *', 'responder.cron.send_bulk', '>> /tmp/scheduled_job.log')
]

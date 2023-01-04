import os
from .settings import *



INTERNAL_IP='127.0.0.1'

DEBUG = True

# SECRET_KEY = os.environ["SECRET_KEY"]
SECRET_KEY='zd&sdao_m16cgkyd-_n1ff-8lx*!b9g81olr_^qfp7jk#lavca'

ALLOWED_HOSTS = ["7a94-103-85-158-33.ngrok.io", ".7a94-103-85-158-33.ngrok.io", "127.0.0.1"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": 'django.db.backends.postgresql_psycopg2',
        "NAME": 'zapier',
        "USER": 'zapier',
        "PASSWORD": 'Et133016',
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
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "base.context.unread_count",
                "base.context.notifications",
            ],
            # 'loaders': [
            #     ('django.template.loaders.cached.Loader', [
            #         'django.template.loaders.filesystem.Loader',
            #         'django.template.loaders.app_directories.Loader',
            #     ]),
            # ],
        },
    },
]

TIME_ZONE = 'Asia/Dhaka'
USE_TZ = False

# Cron job
CRONJOBS = [
    ('*/1 * * * *', 'responder.cron.my_scheduled_job', '>> /tmp/scheduled_job.log'),
    ('*/1 * * * *', 'responder.cron.send_bulk', '>> /tmp/scheduled_job.log')
]

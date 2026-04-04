# ==============================================================================
# Docker
# ==============================================================================

import os
import dj_database_url

ALLOWED_HOSTS = ["*"]

if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'tabbycat',
            'USER': 'tabbycat',
            'PASSWORD': 'tabbycat',
            'HOST': 'db',
            'PORT': 5432,
        }
    }

redis_url = os.environ.get('REDIS_URL', 'redis://redis:6379')

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": redis_url + "/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 60,
        },
    },
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [redis_url],
            "group_expiry": 10800,
        },
    },
}
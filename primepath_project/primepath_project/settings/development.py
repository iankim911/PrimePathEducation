"""
Development settings for PrimePath project.
"""
from .base import *

# Override any settings for development
DEBUG = True

# Development database (can use SQLite for simplicity)
if config('USE_SQLITE_DEV', default=True, cast=bool):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Disable security features for development
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# Development email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Debug toolbar configuration (optional)
# if DEBUG:
#     INSTALLED_APPS += ['django_extensions']
    
# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# Disable caching in development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# More verbose logging in development
# LOGGING['handlers']['console']['level'] = 'DEBUG'
# LOGGING['loggers']['core']['level'] = 'DEBUG'
# LOGGING['loggers']['placement_test']['level'] = 'DEBUG'
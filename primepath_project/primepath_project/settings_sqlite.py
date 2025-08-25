"""
Django settings for primepath_project - SQLite version for easy setup
"""

from pathlib import Path
import os

# Import StatReloader fix configuration
try:
    from . import statreloader_config  # noqa
except ImportError:
    pass  # Config file might not exist yet

BASE_DIR = Path(__file__).resolve().parent.parent

# Security Configuration - Use environment variables in production
import os
from django.core.management.utils import get_random_secret_key
import warnings

# PHASE 8 SECURITY IMPROVEMENTS
# Generate a new secret key if not provided
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-your-secret-key-here-change-in-production')
if not os.environ.get('SECRET_KEY'):
    warnings.warn("WARNING: Using default SECRET_KEY. Set SECRET_KEY environment variable in production!", UserWarning)

# Debug should be False in production - PHASE 8 ENHANCED
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
if DEBUG:
    warnings.warn("WARNING: DEBUG is True. Set DEBUG=False in production!", UserWarning)

# Properly configure allowed hosts - PHASE 8 SECURITY
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
# Only add wildcard in DEBUG mode for development
if DEBUG:
    ALLOWED_HOSTS.append('*')
elif '*' in ALLOWED_HOSTS:
    warnings.warn("WARNING: ALLOWED_HOSTS contains '*' in production mode!", UserWarning)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Required for allauth
    'placement_test',
    'primepath_routinetest',  # New separate routine test app
    'primepath_student',  # Student interface app
    'core',
    'api',  # API app
    'rest_framework',  # Django REST Framework
    'django_filters',  # Django Filter
    'corsheaders',  # CORS Headers
    
    # Django-allauth apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS middleware (must be before CommonMiddleware)
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # Required for django-allauth
    'primepath_project.url_redirect_middleware.URLRedirectMiddleware',  # NEW: Handle /PlacementTest/ and /RoutineTest/ redirects
    'core.middleware.URLRedirectMiddleware',  # URL redirect handling (early in chain)
    'core.middleware.FeatureFlagMiddleware',  # Add feature flags
    'core.middleware.APIVersionMiddleware',  # Add API versioning
    'core.middleware.SecurityHeadersMiddleware',  # Security headers
    'core.middleware.RateLimitMiddleware',  # Rate limiting
    # REMOVED: MatrixTabInjectionMiddleware - Matrix tab replaced by Classes & Exams unified view
]


ROOT_URLCONF = 'primepath_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'primepath_routinetest.context_processors.routinetest_context',  # RoutineTest theme context
            ],
        },
    },
]

WSGI_APPLICATION = 'primepath_project.wsgi.application'

# Using SQLite for easier setup
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Cache configuration for rate limiting and performance
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# Rate limiting configuration
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# Password validation - Essential for security
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django-allauth settings
SITE_ID = 1

# Allauth settings
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'none'  # Set to 'mandatory' in production
ACCOUNT_ADAPTER = 'core.adapters.AccountAdapter'  # Custom adapter
SOCIALACCOUNT_ADAPTER = 'core.adapters.SocialAccountAdapter'  # Custom social adapter

# Google OAuth2 settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    }
}

# Redirect URLs after social login
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/login/'

FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  

SESSION_COOKIE_AGE = 86400  
SESSION_SAVE_EVERY_REQUEST = True

# Security Settings
X_FRAME_OPTIONS = 'SAMEORIGIN'  # Allow PDFs in iframes from same origin

# Authentication Settings
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# Session Settings for Authentication
SESSION_COOKIE_NAME = 'primepath_sessionid'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Keep session after browser close
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript to read CSRF token for AJAX
CSRF_COOKIE_SECURE = False  # Set to True in production with HTTPS

# Authentication Backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Default Django auth
    'allauth.account.auth_backends.AuthenticationBackend',  # allauth backend
]

# Logging for Authentication
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'primepath.log',
            'maxBytes': 1024 * 1024 * 5,  # 5MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'core': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'placement_test': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Additional Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

# File Upload Security
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_AUDIO_EXTENSIONS = ['mp3', 'wav', 'm4a', 'ogg']
ALLOWED_PDF_EXTENSIONS = ['pdf']
ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']

# Content Security Policy (Basic)
SECURE_REFERRER_POLICY = 'same-origin'

# Feature flags for safe modularization
FEATURE_FLAGS = {
    'USE_V2_TEMPLATES': True,  # Use modular V2 templates (fixes multiple short answers)
    'USE_SERVICE_LAYER': True,  # Services working well
    'USE_JS_MODULES': True,  # JS modules active
    'ENABLE_CACHING': True,  # Improves performance
    'ENABLE_API_V2': True,  # New organized API endpoints
}

# Data format standardization
DATA_SEPARATOR_FORMAT = 'comma'  # Standardize on comma for new data
LEGACY_SEPARATOR_SUPPORT = True  # Support pipe separators for existing data

# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'core.permissions.SmartAPIPermission',  # Use our intelligent permission system
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',  # For API testing
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # Provides web interface for API
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ['v1', 'v2'],
}

# Social OAuth Configuration - Removed
# This is an in-house tool, social login not needed

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React development server
    "http://localhost:8000",  # Django development server
    "http://127.0.0.1:8000",  # Alternative Django dev server
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Celery Configuration
# Note: Redis server must be running for Celery to work
# Install Redis: https://redis.io/download
# Or use Docker: docker run -d -p 6379:6379 redis

# Celery settings
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Message broker
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'  # Result storage
CELERY_ACCEPT_CONTENT = ['json']  # Allowed content types

# Logging Configuration for debugging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'primepath.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'placement_test': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'core': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}
CELERY_TASK_SERIALIZER = 'json'  # Task serialization format
CELERY_RESULT_SERIALIZER = 'json'  # Result serialization format
CELERY_TIMEZONE = TIME_ZONE  # Use Django's timezone
CELERY_TASK_TRACK_STARTED = True  # Track when tasks start
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes max per task
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # Soft limit at 25 minutes
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'  # For periodic tasks

# Celery Beat Schedule (periodic tasks)
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'cleanup-old-sessions': {
        'task': 'core.tasks.cleanup_old_sessions',
        'schedule': crontab(hour=2, minute=0),  # Run at 2 AM daily
        'kwargs': {'days': 30}
    },
    'cleanup-orphaned-files': {
        'task': 'core.tasks.cleanup_orphaned_files',
        'schedule': crontab(hour=3, minute=0),  # Run at 3 AM daily
    },
    'generate-daily-report': {
        'task': 'core.tasks.generate_daily_report',
        'schedule': crontab(hour=7, minute=0),  # Run at 7 AM daily
    },
    'update-placement-analytics': {
        'task': 'core.tasks.update_placement_analytics',
        'schedule': crontab(minute='*/30'),  # Run every 30 minutes
    },
}

# ============================================================================
# PHASE 8 CONFIGURATION IMPROVEMENTS - Added 2025-08-13
# ============================================================================

# Enhanced Security Settings
if not DEBUG:
    # Security middleware settings for production
    SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False').lower() == 'true'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
    CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'True').lower() == 'true'
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Phase 8 Console Monitoring Configuration
CONSOLE_MONITORING = {
    'enabled': True,
    'log_level': 'DEBUG' if DEBUG else 'INFO',
    'track_database_queries': DEBUG,
    'track_template_rendering': DEBUG,
    'track_static_serving': DEBUG,
    'preserve_relationships': True,
    'monitor_endpoints': [
        '/api/PlacementTest/exams/',
        '/api/PlacementTest/sessions/',
        '/PlacementTest/teacher/dashboard/',
        '/placement-rules/',
        '/exam-mapping/',
    ],
    'log_to_console': True,
    'log_to_file': True,
    'max_log_size': 10485760,  # 10MB
    'backup_count': 5,
}

# Preserve all model relationships
PRESERVE_RELATIONSHIPS = True

# Phase 8 Feature Flags
PHASE8_FEATURES = {
    'enhanced_monitoring': True,
    'security_headers': not DEBUG,
    'relationship_preservation': True,
    'console_debugging': DEBUG,
    'performance_tracking': True,
    'error_tracking': True,
}

# Environment-based configuration
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development' if DEBUG else 'production')

# Log Phase 8 Configuration Status
import logging
logger = logging.getLogger(__name__)
logger.info(f"[PHASE8] Configuration loaded for environment: {ENVIRONMENT}")
logger.info(f"[PHASE8] DEBUG={DEBUG}, ALLOWED_HOSTS={ALLOWED_HOSTS}")
logger.info(f"[PHASE8] Console monitoring: {CONSOLE_MONITORING['enabled']}")
logger.info(f"[PHASE8] Relationship preservation: {PRESERVE_RELATIONSHIPS}")
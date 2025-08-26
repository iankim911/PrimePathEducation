"""
Configuration Service Layer
Centralized configuration management to eliminate hardcoding
Created: August 26, 2025

This service provides:
- Dynamic date/year management
- Environment-based URL resolution
- Academic year calculations
- System-wide constants
"""

import os
from datetime import datetime, date
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class ConfigurationService:
    """
    Central configuration service for all dynamic and environment-specific values
    Eliminates hardcoding throughout the application
    """
    
    # Cache timeout in seconds (1 hour)
    CACHE_TIMEOUT = 3600
    
    # Academic year starts in September
    ACADEMIC_YEAR_START_MONTH = 9
    
    @classmethod
    def get_current_year(cls):
        """
        Get the current calendar year dynamically
        Used for: Database queries, file naming, logging
        """
        year = timezone.now().year
        logger.debug(f"[CONFIG] Current year resolved: {year}")
        return year
    
    @classmethod
    def get_current_academic_year(cls):
        """
        Get current academic year string (e.g., "2025-2026")
        Academic year runs September to August
        """
        cache_key = 'config:academic_year'
        academic_year = cache.get(cache_key)
        
        if not academic_year:
            now = timezone.now()
            if now.month >= cls.ACADEMIC_YEAR_START_MONTH:
                # September-December: current year - next year
                academic_year = f"{now.year}-{now.year + 1}"
            else:
                # January-August: previous year - current year
                academic_year = f"{now.year - 1}-{now.year}"
            
            cache.set(cache_key, academic_year, cls.CACHE_TIMEOUT)
            logger.debug(f"[CONFIG] Academic year calculated: {academic_year}")
        
        return academic_year
    
    @classmethod
    def get_academic_year_start(cls):
        """Get the start year of current academic year"""
        academic_year = cls.get_current_academic_year()
        return int(academic_year.split('-')[0])
    
    @classmethod
    def get_academic_year_end(cls):
        """Get the end year of current academic year"""
        academic_year = cls.get_current_academic_year()
        return int(academic_year.split('-')[1])
    
    @classmethod
    def get_base_url(cls, request=None):
        """
        Get the base URL dynamically based on environment
        Handles: development, staging, production
        """
        cache_key = 'config:base_url'
        base_url = cache.get(cache_key)
        
        if not base_url:
            # Priority order:
            # 1. Environment variable
            # 2. Request object
            # 3. Django settings
            # 4. Default fallback
            
            if os.environ.get('BASE_URL'):
                base_url = os.environ.get('BASE_URL')
                logger.debug(f"[CONFIG] Base URL from environment: {base_url}")
            elif request and request.META.get('HTTP_HOST'):
                scheme = 'https' if request.is_secure() else 'http'
                base_url = f"{scheme}://{request.META['HTTP_HOST']}"
                logger.debug(f"[CONFIG] Base URL from request: {base_url}")
            elif hasattr(settings, 'BASE_URL'):
                base_url = settings.BASE_URL
                logger.debug(f"[CONFIG] Base URL from settings: {base_url}")
            else:
                # Intelligent default based on DEBUG setting
                if settings.DEBUG:
                    base_url = 'http://127.0.0.1:8000'
                else:
                    base_url = 'https://primepath.example.com'
                logger.debug(f"[CONFIG] Base URL using default: {base_url}")
            
            cache.set(cache_key, base_url, cls.CACHE_TIMEOUT)
        
        return base_url
    
    @classmethod
    def get_api_base_url(cls, request=None):
        """Get the API base URL"""
        base = cls.get_base_url(request)
        return f"{base}/api"
    
    @classmethod
    def get_media_url(cls, request=None):
        """Get the media files URL"""
        if hasattr(settings, 'MEDIA_URL') and settings.MEDIA_URL.startswith('http'):
            return settings.MEDIA_URL
        base = cls.get_base_url(request)
        return f"{base}{settings.MEDIA_URL}"
    
    @classmethod
    def get_static_url(cls, request=None):
        """Get the static files URL"""
        if hasattr(settings, 'STATIC_URL') and settings.STATIC_URL.startswith('http'):
            return settings.STATIC_URL
        base = cls.get_base_url(request)
        return f"{base}{settings.STATIC_URL}"
    
    @classmethod
    def get_timeout(cls, key='default'):
        """
        Get timeout values dynamically
        Replaces hardcoded timeout values throughout the app
        """
        timeouts = {
            'default': 30,
            'api': int(os.environ.get('API_TIMEOUT', '30')),
            'cache': int(os.environ.get('CACHE_TIMEOUT', '3600')),
            'session': int(os.environ.get('SESSION_TIMEOUT', '1800')),
            'file_upload': int(os.environ.get('UPLOAD_TIMEOUT', '120')),
            'test_duration': int(os.environ.get('TEST_DURATION', '7200')),  # 2 hours
            'audio_duration': int(os.environ.get('AUDIO_MAX_DURATION', '300')),  # 5 minutes
        }
        timeout = timeouts.get(key, timeouts['default'])
        logger.debug(f"[CONFIG] Timeout for '{key}': {timeout} seconds")
        return timeout
    
    @classmethod
    def get_pagination_limit(cls, key='default'):
        """
        Get pagination limits dynamically
        Replaces hardcoded pagination values
        """
        limits = {
            'default': 20,
            'students': int(os.environ.get('PAGINATION_STUDENTS', '20')),
            'exams': int(os.environ.get('PAGINATION_EXAMS', '10')),
            'questions': int(os.environ.get('PAGINATION_QUESTIONS', '20')),
            'results': int(os.environ.get('PAGINATION_RESULTS', '50')),
            'api': int(os.environ.get('API_PAGE_SIZE', '100')),
        }
        limit = limits.get(key, limits['default'])
        logger.debug(f"[CONFIG] Pagination limit for '{key}': {limit}")
        return limit
    
    @classmethod
    def get_max_file_size(cls, file_type='default'):
        """
        Get maximum file sizes dynamically (in MB)
        Replaces hardcoded file size limits
        """
        sizes = {
            'default': 10,
            'pdf': int(os.environ.get('MAX_PDF_SIZE_MB', '50')),
            'audio': int(os.environ.get('MAX_AUDIO_SIZE_MB', '100')),
            'image': int(os.environ.get('MAX_IMAGE_SIZE_MB', '10')),
            'excel': int(os.environ.get('MAX_EXCEL_SIZE_MB', '20')),
            'csv': int(os.environ.get('MAX_CSV_SIZE_MB', '10')),
        }
        size_mb = sizes.get(file_type, sizes['default'])
        logger.debug(f"[CONFIG] Max file size for '{file_type}': {size_mb}MB")
        return size_mb * 1024 * 1024  # Return in bytes
    
    @classmethod
    def get_feature_flag(cls, flag_name, default=False):
        """
        Get feature flags dynamically
        Allows toggling features without code changes
        """
        # Check environment variables first
        env_key = f"FEATURE_{flag_name.upper()}"
        if env_key in os.environ:
            value = os.environ.get(env_key, '').lower() in ('true', '1', 'yes', 'on')
            logger.debug(f"[CONFIG] Feature flag '{flag_name}': {value} (from env)")
            return value
        
        # Check Django settings
        if hasattr(settings, 'FEATURE_FLAGS'):
            value = settings.FEATURE_FLAGS.get(flag_name, default)
            logger.debug(f"[CONFIG] Feature flag '{flag_name}': {value} (from settings)")
            return value
        
        logger.debug(f"[CONFIG] Feature flag '{flag_name}': {default} (default)")
        return default
    
    @classmethod
    def get_system_constants(cls):
        """
        Get all system constants for client-side use
        Returns a dictionary safe for JSON serialization
        """
        return {
            'current_year': cls.get_current_year(),
            'academic_year': cls.get_current_academic_year(),
            'academic_year_start': cls.get_academic_year_start(),
            'academic_year_end': cls.get_academic_year_end(),
            'timeouts': {
                'api': cls.get_timeout('api'),
                'session': cls.get_timeout('session'),
                'test_duration': cls.get_timeout('test_duration'),
            },
            'pagination': {
                'default': cls.get_pagination_limit('default'),
                'students': cls.get_pagination_limit('students'),
                'exams': cls.get_pagination_limit('exams'),
            },
            'features': {
                'v2_templates': cls.get_feature_flag('USE_V2_TEMPLATES'),
                'debug_mode': settings.DEBUG,
                'allow_audio': cls.get_feature_flag('ALLOW_AUDIO', True),
                'allow_pdf': cls.get_feature_flag('ALLOW_PDF', True),
            }
        }
    
    @classmethod
    def validate_year(cls, year_value):
        """
        Validate if a year value is reasonable
        Helps catch hardcoded year issues
        """
        try:
            year = int(year_value)
            current_year = cls.get_current_year()
            
            # Allow years within reasonable range (past 10 years to next 5 years)
            min_year = current_year - 10
            max_year = current_year + 5
            
            if min_year <= year <= max_year:
                return True
            else:
                logger.warning(f"[CONFIG] Year validation failed: {year} not in range {min_year}-{max_year}")
                return False
        except (ValueError, TypeError):
            logger.error(f"[CONFIG] Year validation failed: Invalid year value {year_value}")
            return False
    
    @classmethod
    def log_config_usage(cls, component, config_type, value):
        """
        Log configuration usage for debugging
        Helps track where configurations are being used
        """
        logger.info(f"[CONFIG_USAGE] Component: {component} | Type: {config_type} | Value: {value}")
    
    @classmethod
    def get_environment(cls):
        """
        Get current environment (development/staging/production)
        """
        env = os.environ.get('ENVIRONMENT', 'development' if settings.DEBUG else 'production')
        logger.debug(f"[CONFIG] Environment: {env}")
        return env
    
    @classmethod
    def clear_cache(cls):
        """
        Clear configuration cache
        Useful after environment changes
        """
        cache.delete_many([
            'config:academic_year',
            'config:base_url',
        ])
        logger.info("[CONFIG] Configuration cache cleared")


# Convenience functions for common operations
def get_current_year():
    """Shorthand for getting current year"""
    return ConfigurationService.get_current_year()

def get_academic_year():
    """Shorthand for getting academic year"""
    return ConfigurationService.get_current_academic_year()

def get_base_url(request=None):
    """Shorthand for getting base URL"""
    return ConfigurationService.get_base_url(request)

def get_config_for_frontend(request=None):
    """Get configuration suitable for frontend JavaScript"""
    config = ConfigurationService.get_system_constants()
    config['base_url'] = ConfigurationService.get_base_url(request)
    config['api_base_url'] = ConfigurationService.get_api_base_url(request)
    return config


# Validation decorator for views
def validate_year_param(param_name='year'):
    """
    Decorator to validate year parameters in views
    Usage: @validate_year_param('academic_year')
    """
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            year_value = request.GET.get(param_name) or request.POST.get(param_name)
            if year_value and not ConfigurationService.validate_year(year_value):
                logger.warning(f"[CONFIG] Invalid year parameter in {func.__name__}: {year_value}")
                # Continue with current year as fallback
                request.GET._mutable = True
                request.GET[param_name] = str(ConfigurationService.get_current_year())
                request.GET._mutable = False
            return func(request, *args, **kwargs)
        return wrapper
    return decorator
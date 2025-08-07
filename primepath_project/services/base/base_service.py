"""
Base service class for all service layer components.
Provides common functionality and patterns.
"""
import logging
from typing import Any, Dict, Optional
from django.core.cache import cache
from django.db import transaction


class BaseService:
    """Base service with common patterns."""
    
    cache_prefix = None
    cache_timeout = 300  # 5 minutes default
    
    @classmethod
    def get_logger(cls):
        """Get logger for service."""
        return logging.getLogger(f"{cls.__module__}.{cls.__name__}")
    
    @classmethod
    def get_cache_key(cls, *args):
        """Generate cache key."""
        if not cls.cache_prefix:
            cls.cache_prefix = cls.__name__.lower()
        parts = [cls.cache_prefix] + [str(arg) for arg in args]
        return ":".join(parts)
    
    @classmethod
    def get_cached(cls, key_parts, getter_func, timeout=None):
        """Get from cache or execute getter function."""
        cache_key = cls.get_cache_key(*key_parts)
        result = cache.get(cache_key)
        
        if result is None:
            result = getter_func()
            cache.set(cache_key, result, timeout or cls.cache_timeout)
        
        return result
    
    @classmethod
    def invalidate_cache(cls, *key_parts):
        """Invalidate cache for given key parts."""
        cache_key = cls.get_cache_key(*key_parts)
        cache.delete(cache_key)
    
    @classmethod
    @transaction.atomic
    def execute_in_transaction(cls, func, *args, **kwargs):
        """Execute function in database transaction."""
        return func(*args, **kwargs)
    
    @classmethod
    def validate_required_fields(cls, data: Dict[str, Any], required: list):
        """Validate required fields are present."""
        missing = [field for field in required if not data.get(field)]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
        return True
    
    @classmethod
    def sanitize_input(cls, data: Dict[str, Any], allowed_fields: list):
        """Sanitize input to only allowed fields."""
        return {k: v for k, v in data.items() if k in allowed_fields}
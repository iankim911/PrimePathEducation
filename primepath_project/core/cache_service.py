"""
Cache Service - Phase 7
Manages application-wide caching strategies
"""
from django.core.cache import cache
from django.conf import settings
from functools import wraps
from typing import Any, Optional, Callable, Dict, List
import hashlib
import json
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)


class CacheService:
    """Centralized caching service for the application."""
    
    # Cache key prefixes
    PREFIXES = {
        'exam': 'exam:',
        'session': 'session:',
        'student': 'student:',
        'dashboard': 'dashboard:',
        'curriculum': 'curriculum:',
        'template': 'template:',
        'query': 'query:',
    }
    
    # Default cache timeouts (in seconds)
    TIMEOUTS = {
        'exam': 3600,        # 1 hour
        'session': 1800,     # 30 minutes
        'student': 900,      # 15 minutes
        'dashboard': 300,    # 5 minutes
        'curriculum': 7200,  # 2 hours
        'template': 3600,    # 1 hour
        'query': 600,        # 10 minutes
    }
    
    @classmethod
    def get(cls, key: str, prefix: str = None) -> Any:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            prefix: Optional prefix type
            
        Returns:
            Cached value or None
        """
        full_key = cls._build_key(key, prefix)
        value = cache.get(full_key)
        
        if value is not None:
            logger.debug(f"Cache hit: {full_key}")
        else:
            logger.debug(f"Cache miss: {full_key}")
            
        return value
    
    @classmethod
    def set(cls, key: str, value: Any, prefix: str = None, 
            timeout: Optional[int] = None) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            prefix: Optional prefix type
            timeout: Optional timeout in seconds
            
        Returns:
            Success status
        """
        full_key = cls._build_key(key, prefix)
        
        if timeout is None and prefix in cls.TIMEOUTS:
            timeout = cls.TIMEOUTS[prefix]
        elif timeout is None:
            timeout = 3600  # Default 1 hour
        
        success = cache.set(full_key, value, timeout)
        
        if success:
            logger.debug(f"Cache set: {full_key} (timeout: {timeout}s)")
        else:
            logger.warning(f"Cache set failed: {full_key}")
            
        return success
    
    @classmethod
    def delete(cls, key: str, prefix: str = None) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
            prefix: Optional prefix type
            
        Returns:
            Success status
        """
        full_key = cls._build_key(key, prefix)
        success = cache.delete(full_key)
        
        if success:
            logger.debug(f"Cache deleted: {full_key}")
            
        return success
    
    @classmethod
    def delete_pattern(cls, pattern: str, prefix: str = None):
        """
        Delete all keys matching pattern.
        
        Args:
            pattern: Pattern to match
            prefix: Optional prefix type
        """
        if prefix:
            pattern = f"{cls.PREFIXES.get(prefix, '')}{pattern}"
        
        # Check if cache backend supports delete_pattern
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern(pattern)
            logger.info(f"Cache pattern deleted: {pattern}")
        else:
            # Fallback for backends that don't support pattern deletion
            logger.warning(f"Cache backend doesn't support delete_pattern: {pattern}")
    
    @classmethod
    def _build_key(cls, key: str, prefix: str = None) -> str:
        """Build full cache key with prefix."""
        if prefix and prefix in cls.PREFIXES:
            return f"{cls.PREFIXES[prefix]}{key}"
        return key
    
    @classmethod
    def get_or_set(cls, key: str, callable_or_value: Any, 
                   prefix: str = None, timeout: Optional[int] = None) -> Any:
        """
        Get from cache or set if not exists.
        
        Args:
            key: Cache key
            callable_or_value: Callable to generate value or direct value
            prefix: Optional prefix type
            timeout: Optional timeout
            
        Returns:
            Cached or generated value
        """
        value = cls.get(key, prefix)
        
        if value is None:
            if callable(callable_or_value):
                value = callable_or_value()
            else:
                value = callable_or_value
            
            if value is not None:
                cls.set(key, value, prefix, timeout)
        
        return value
    
    @classmethod
    def clear_exam_cache(cls, exam_id: str):
        """Clear all cache related to an exam."""
        patterns = [
            f"exam:{exam_id}*",
            f"query:exam_{exam_id}*",
            f"template:*exam_{exam_id}*",
        ]
        
        for pattern in patterns:
            cls.delete_pattern(pattern)
        
        logger.info(f"Cleared exam cache: {exam_id}")
    
    @classmethod
    def clear_session_cache(cls, session_id: str):
        """Clear all cache related to a session."""
        patterns = [
            f"session:{session_id}*",
            f"student:*session_{session_id}*",
        ]
        
        for pattern in patterns:
            cls.delete_pattern(pattern)
        
        logger.info(f"Cleared session cache: {session_id}")
    
    @classmethod
    def clear_dashboard_cache(cls):
        """Clear dashboard-related cache."""
        cls.delete_pattern("dashboard:*")
        logger.info("Cleared dashboard cache")
    
    @classmethod
    def get_cache_stats(cls) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary of cache stats
        """
        # This would need Redis or Memcached specific implementation
        # For now, return basic info
        return {
            'backend': settings.CACHES['default']['BACKEND'],
            'prefixes': list(cls.PREFIXES.keys()),
            'timeouts': cls.TIMEOUTS,
        }


def cache_result(prefix: str = 'query', timeout: Optional[int] = None,
                 key_builder: Optional[Callable] = None):
    """
    Decorator to cache function results.
    
    Args:
        prefix: Cache key prefix
        timeout: Cache timeout in seconds
        key_builder: Optional function to build cache key
        
    Usage:
        @cache_result(prefix='exam', timeout=3600)
        def get_exam_data(exam_id):
            return expensive_operation()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Default key builder
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = ":".join(key_parts)
            
            # Try to get from cache
            cached = CacheService.get(cache_key, prefix)
            if cached is not None:
                return cached
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            CacheService.set(cache_key, result, prefix, timeout)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(patterns: List[str]):
    """
    Decorator to invalidate cache patterns after function execution.
    
    Args:
        patterns: List of cache patterns to invalidate
        
    Usage:
        @invalidate_cache(['exam:*', 'dashboard:*'])
        def update_exam(exam_id, data):
            # Update exam
            return exam
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Invalidate specified patterns
            for pattern in patterns:
                CacheService.delete_pattern(pattern)
                logger.debug(f"Invalidated cache pattern: {pattern}")
            
            return result
        
        return wrapper
    return decorator


class QueryCache:
    """Specialized cache for database queries."""
    
    @staticmethod
    def cache_queryset(queryset, key: str, timeout: int = 600):
        """
        Cache a queryset result.
        
        Args:
            queryset: Django queryset
            key: Cache key
            timeout: Timeout in seconds
        """
        # Evaluate queryset and cache
        result = list(queryset)
        CacheService.set(key, result, 'query', timeout)
        return result
    
    @staticmethod
    def get_or_execute(queryset, key: str, timeout: int = 600):
        """
        Get cached queryset or execute and cache.
        
        Args:
            queryset: Django queryset
            key: Cache key
            timeout: Timeout in seconds
        """
        cached = CacheService.get(key, 'query')
        if cached is not None:
            return cached
        
        return QueryCache.cache_queryset(queryset, key, timeout)
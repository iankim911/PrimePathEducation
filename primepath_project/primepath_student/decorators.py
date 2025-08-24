"""
Security decorators for student views
"""
from functools import wraps
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
import hashlib


def rate_limit(max_requests=10, time_window=60):
    """
    Rate limiting decorator
    
    Args:
        max_requests: Maximum number of requests allowed
        time_window: Time window in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Get client IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            # Create cache key
            cache_key = f"rate_limit_{func.__name__}_{hashlib.md5(ip.encode()).hexdigest()}"
            
            # Get current request count
            requests = cache.get(cache_key, 0)
            
            if requests >= max_requests:
                return JsonResponse({
                    'success': False, 
                    'error': 'Rate limit exceeded. Please try again later.',
                    'retry_after': time_window
                }, status=429)
            
            # Increment counter
            cache.set(cache_key, requests + 1, time_window)
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def student_required(func):
    """
    Decorator to ensure user has a valid student profile
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            student_profile = request.user.primepath_student_profile
        except AttributeError:
            return JsonResponse({
                'success': False,
                'error': 'Student profile required'
            }, status=403)
        
        # Add student profile to request for easy access
        request.student_profile = student_profile
        
        return func(request, *args, **kwargs)
    return wrapper
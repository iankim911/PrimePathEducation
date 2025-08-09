"""
Custom middleware for PrimePath project.
Includes feature flags, API versioning, security headers, and rate limiting.
"""
import hashlib
import logging
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse

logger = logging.getLogger(__name__)


class FeatureFlagMiddleware:
    """
    Middleware to add feature flags to request context.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Add feature flags to request
        request.feature_flags = settings.FEATURE_FLAGS
        
        # Determine which template to use based on feature flags
        # Note: Views must check if modular template exists before using
        if request.feature_flags.get('USE_MODULAR_TEMPLATES'):
            request.use_modular_templates = True
        else:
            request.use_modular_templates = False
        
        response = self.get_response(request)
        return response


class APIVersionMiddleware:
    """
    Middleware to handle API versioning.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Determine API version from path
        if '/api/v2/' in request.path:
            request.api_version = 2
        else:
            request.api_version = 1
            
        response = self.get_response(request)
        return response


class SecurityHeadersMiddleware:
    """
    Middleware to add security headers to responses.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Add referrer policy
        response['Referrer-Policy'] = 'same-origin'
        
        # Add permissions policy
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response


class RateLimitMiddleware:
    """
    Simple rate limiting middleware using Django's cache.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.enable_rate_limit = getattr(settings, 'RATELIMIT_ENABLE', True)
        self.default_limit = 60  # requests per minute
        self.api_limit = 100  # API requests per minute
        self.window_seconds = 60  # 1 minute window
    
    def get_client_ip(self, request):
        """Get the client's IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def __call__(self, request):
        # Skip rate limiting if disabled or for static files
        if not self.enable_rate_limit:
            return self.get_response(request)
        
        if request.path.startswith(('/static/', '/media/')):
            return self.get_response(request)
        
        # Skip for superusers
        if request.user.is_authenticated and request.user.is_superuser:
            return self.get_response(request)
        
        # Check rate limit
        is_api = request.path.startswith('/api/')
        limit = self.api_limit if is_api else self.default_limit
        
        # Generate cache key
        ip = self.get_client_ip(request)
        cache_key = f"ratelimit:{hashlib.md5(ip.encode()).hexdigest()[:10]}"
        
        try:
            request_count = cache.get(cache_key, 0)
            
            if request_count >= limit:
                logger.warning(f"Rate limit exceeded for {ip}")
                
                if is_api:
                    return JsonResponse({
                        'error': 'Rate limit exceeded',
                        'message': f'Maximum {limit} requests per minute'
                    }, status=429)
                else:
                    return HttpResponse(
                        "Too many requests. Please try again later.",
                        status=429
                    )
            
            # Increment counter
            cache.set(cache_key, request_count + 1, self.window_seconds)
            
        except Exception as e:
            logger.error(f"Rate limit middleware error: {e}")
        
        return self.get_response(request)
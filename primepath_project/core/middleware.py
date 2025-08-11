"""
Custom middleware for PrimePath project.
Includes feature flags, API versioning, security headers, and rate limiting.
"""
import hashlib
import json
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

class URLRedirectMiddleware:
    """
    Middleware to handle legacy URL redirects without breaking existing functionality.
    This ensures backward compatibility while guiding users to new URL patterns.
    """
    
    # Define redirect mappings - Old URL -> New URL/View Name
    REDIRECT_MAPPINGS = {
        # Legacy placement test URLs to new API structure
        '/placement/start-test/': '/api/placement/start/',
        '/placement/create-exam/': '/api/placement/exams/create/',
        '/placement/exam-list/': '/api/placement/exams/',
        '/placement/sessions/': '/api/placement/sessions/',
        
        # Core app redirects
        '/core/': '/',  # Core dashboard is now homepage
        '/core/dashboard/': '/',
        
        # Legacy API endpoints
        '/api/core/schools/': '/api/schools/',
        '/api/core/programs/': '/api/programs/',
    }
    
    # Dynamic redirect patterns (require parameter extraction)
    DYNAMIC_PATTERNS = {
        '/placement/exam/': '/api/placement/exams/',  # + exam_id
        '/placement/session/': '/api/placement/session/',  # + session_id
        '/placement/result/': '/api/placement/session/',  # + session_id + /result/
    }
    
    def __init__(self, get_response):
        self.get_response = get_response
        import logging
        self.logger = logging.getLogger(__name__)
        self.logger.info("URLRedirectMiddleware initialized with %d static and %d dynamic mappings", 
                   len(self.REDIRECT_MAPPINGS), len(self.DYNAMIC_PATTERNS))
        
        # Log all registered redirects for debugging
        if settings.DEBUG:
            console_log = {
                "middleware": "URLRedirectMiddleware",
                "action": "initialized",
                "static_redirects": list(self.REDIRECT_MAPPINGS.keys()),
                "dynamic_patterns": list(self.DYNAMIC_PATTERNS.keys())
            }
            print(f"[URL_REDIRECT_INIT] {json.dumps(console_log, indent=2)}")
    
    def __call__(self, request):
        """
        Process each request and redirect if it matches a legacy pattern
        """
        from django.http import HttpResponsePermanentRedirect
        path = request.path
        
        # Console logging for debugging
        if settings.DEBUG and ('/placement/' in path or '/core/' in path):
            console_log = {
                "middleware": "URLRedirectMiddleware",
                "action": "checking_path",
                "path": path,
                "method": request.method,
                "query_params": dict(request.GET) if request.GET else {}
            }
            print(f"[URL_REDIRECT_CHECK] {json.dumps(console_log)}")
        
        # Check static redirects first (exact matches)
        if path in self.REDIRECT_MAPPINGS:
            new_url = self.REDIRECT_MAPPINGS[path]
            
            # Preserve query parameters
            if request.GET:
                query_string = request.GET.urlencode()
                new_url = f"{new_url}?{query_string}"
            
            if settings.DEBUG:
                console_log = {
                    "middleware": "URLRedirectMiddleware",
                    "action": "redirecting",
                    "from": path,
                    "to": new_url,
                    "type": "static_redirect",
                    "status": 301
                }
                print(f"[URL_REDIRECT] {json.dumps(console_log)}")
            self.logger.info("Redirecting %s -> %s (static)", path, new_url)
            
            return HttpResponsePermanentRedirect(new_url)
        
        # Check dynamic patterns (partial matches)
        for pattern, replacement in self.DYNAMIC_PATTERNS.items():
            if path.startswith(pattern) and len(path) > len(pattern):
                # Extract the dynamic part
                dynamic_part = path[len(pattern):]
                new_url = replacement + dynamic_part
                
                # Preserve query parameters
                if request.GET:
                    query_string = request.GET.urlencode()
                    new_url = f"{new_url}?{query_string}"
                
                if settings.DEBUG:
                    console_log = {
                        "middleware": "URLRedirectMiddleware",
                        "action": "redirecting",
                        "from": path,
                        "to": new_url,
                        "type": "dynamic_redirect",
                        "pattern": pattern,
                        "dynamic_part": dynamic_part,
                        "status": 301
                    }
                    print(f"[URL_REDIRECT] {json.dumps(console_log)}")
                self.logger.info("Redirecting %s -> %s (dynamic)", path, new_url)
                
                return HttpResponsePermanentRedirect(new_url)
        
        # No redirect needed, continue normal processing
        response = self.get_response(request)
        
        # Log 404 errors for unhandled legacy URLs
        if settings.DEBUG and response.status_code == 404 and ('/placement/' in path or '/core/' in path):
            console_log = {
                "middleware": "URLRedirectMiddleware",
                "action": "404_not_redirected",
                "path": path,
                "message": "Consider adding redirect mapping for this URL"
            }
            print(f"[URL_REDIRECT_404] {json.dumps(console_log)}")
            self.logger.warning("404 for potential legacy URL: %s", path)
        
        return response

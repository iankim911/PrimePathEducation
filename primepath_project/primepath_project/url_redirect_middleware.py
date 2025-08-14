"""
URL Redirect Middleware for PrimePath Project
Provides comprehensive URL redirection from old paths to new paths
Includes extensive console logging for debugging
"""
import logging
import json
from django.shortcuts import redirect
from django.urls import reverse
from urllib.parse import urlparse, urlunparse

logger = logging.getLogger('url_redirect_middleware')


class URLRedirectMiddleware:
    """
    Middleware to handle URL redirects from old patterns to new ones.
    Preserves query strings and fragments.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Define comprehensive redirect mappings
        self.redirects = {
            # Placement Test redirects
            '/placement/': '/PlacementTest/',
            '/api/placement/': '/api/PlacementTest/',
            '/api/v2/placement/': '/api/v2/PlacementTest/',
            
            # Routine Test redirects
            '/routine/': '/RoutineTest/',
            '/api/routine/': '/api/RoutineTest/',
            
            # Teacher dashboard redirect
            '/teacher/dashboard/': '/PlacementTest/teacher/dashboard/',
            '/teacher/': '/PlacementTest/teacher/',
            
            # Legacy patterns - Fixed to redirect correctly
            # NOTE: '/placement/test/' removed - it was causing incorrect redirects
            '/placement/start/': '/PlacementTest/start/',
            '/placement/exams/': '/PlacementTest/exams/',
            '/placement/sessions/': '/PlacementTest/sessions/',
        }
        
        # Log initialization
        print(f"""
        ╔══════════════════════════════════════════════════════════════╗
        ║     URL REDIRECT MIDDLEWARE INITIALIZED                     ║
        ║     Redirecting old URLs to new structure                   ║
        ╠══════════════════════════════════════════════════════════════╣
        ║  Old Pattern → New Pattern                                  ║
        ║  /placement/ → /PlacementTest/                             ║
        ║  /routine/ → /RoutineTest/                                 ║
        ║  /teacher/ → /PlacementTest/teacher/                       ║
        ╚══════════════════════════════════════════════════════════════╝
        """)
        
        logger.info("URLRedirectMiddleware initialized with %d redirect rules", len(self.redirects))
    
    def __call__(self, request):
        """
        Process each request and redirect if necessary
        """
        original_path = request.path
        redirect_url = None
        
        # Console logging for debugging
        if any(pattern in original_path for pattern in ['/placement', '/routine', '/teacher']):
            console_log = {
                "event": "URL_REQUEST",
                "original_path": original_path,
                "method": request.method,
                "timestamp": str(request.META.get('REQUEST_TIME', '')),
                "user_agent": request.META.get('HTTP_USER_AGENT', '')[:50]
            }
            print(f"[URL_REDIRECT_CHECK] {json.dumps(console_log, indent=2)}")
        
        # Check for exact matches first
        for old_pattern, new_pattern in self.redirects.items():
            if original_path == old_pattern:
                redirect_url = new_pattern
                break
            # Check for prefix matches
            elif original_path.startswith(old_pattern):
                redirect_url = original_path.replace(old_pattern, new_pattern, 1)
                break
        
        # If we found a redirect, handle it
        if redirect_url:
            # Preserve query string and fragments
            parsed_url = urlparse(request.get_full_path())
            new_url = urlunparse((
                '',  # scheme
                '',  # netloc
                redirect_url,  # path
                parsed_url.params,
                parsed_url.query,
                parsed_url.fragment
            ))
            
            # Log the redirect
            redirect_log = {
                "event": "URL_REDIRECT",
                "from": original_path,
                "to": redirect_url,
                "full_redirect": new_url,
                "status": "302_TEMPORARY"
            }
            print(f"[URL_REDIRECT_APPLIED] {json.dumps(redirect_log, indent=2)}")
            logger.info("Redirecting %s to %s", original_path, new_url)
            
            # Return redirect response
            return redirect(new_url, permanent=False)
        
        # No redirect needed, continue with normal processing
        response = self.get_response(request)
        
        # Log successful non-redirected requests for new URLs
        if any(pattern in original_path for pattern in ['/PlacementTest', '/RoutineTest']):
            success_log = {
                "event": "NEW_URL_SUCCESS",
                "path": original_path,
                "status": response.status_code,
                "content_type": response.get('Content-Type', '')
            }
            print(f"[NEW_URL_PATTERN] {json.dumps(success_log, indent=2)}")
        
        return response
    
    def process_exception(self, request, exception):
        """
        Log any exceptions that occur during URL processing
        """
        error_log = {
            "event": "URL_REDIRECT_ERROR",
            "path": request.path,
            "error": str(exception),
            "type": type(exception).__name__
        }
        print(f"[URL_REDIRECT_ERROR] {json.dumps(error_log, indent=2)}")
        logger.error("Error processing URL redirect for %s: %s", request.path, str(exception))
        return None
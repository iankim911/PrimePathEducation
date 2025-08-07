"""
Custom middleware for PrimePath project.
"""
from django.conf import settings


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
        if request.feature_flags.get('USE_MODULAR_TEMPLATES'):
            request.template_suffix = '_modular'
        else:
            request.template_suffix = ''
        
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
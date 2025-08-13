"""
Utility functions for the core module.
"""
import os
from django.conf import settings
from django.template.loader import get_template
from django.template import TemplateDoesNotExist


def get_template_name(request, base_template_name):
    """
    Get the appropriate template name based on feature flags.
    Falls back to base template if modular version doesn't exist.
    
    Args:
        request: The HTTP request object
        base_template_name: The base template name (e.g., 'placement_test/student_test.html')
    
    Returns:
        The template name to use
    """
    if hasattr(request, 'use_modular_templates') and request.use_modular_templates:
        # Try to use modular template
        base_path, ext = os.path.splitext(base_template_name)
        modular_template_name = f"{base_path}_modular{ext}"
        
        try:
            # Check if modular template exists
            get_template(modular_template_name)
            return modular_template_name
        except TemplateDoesNotExist:
            # Fall back to base template
            pass
    
    return base_template_name


def get_api_version(request):
    """
    Get the API version to use based on feature flags and request.
    
    Args:
        request: The HTTP request object
    
    Returns:
        The API version (1 or 2)
    """
    if hasattr(request, 'feature_flags') and request.feature_flags.get('ENABLE_API_V2'):
        return 2
    return 1


def should_use_cache(request):
    """
    Determine if caching should be used based on feature flags.
    
    Args:
        request: The HTTP request object
    
    Returns:
        Boolean indicating if caching should be used
    """
    if hasattr(request, 'feature_flags') and request.feature_flags.get('ENABLE_CACHING'):
        return True
    return False
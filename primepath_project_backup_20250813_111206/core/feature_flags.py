"""
Feature Flag System for Phase 6 View Refactoring
Allows gradual migration from old views to refactored views.
"""
from django.conf import settings


class FeatureFlags:
    """Centralized feature flag management."""
    
    # View refactoring flags
    USE_REFACTORED_VIEWS = getattr(settings, 'USE_REFACTORED_VIEWS', False)
    USE_REFACTORED_CORE_VIEWS = getattr(settings, 'USE_REFACTORED_CORE_VIEWS', False)
    USE_REFACTORED_PLACEMENT_VIEWS = getattr(settings, 'USE_REFACTORED_PLACEMENT_VIEWS', False)
    
    # Individual view flags for granular control
    USE_REFACTORED_DASHBOARD = getattr(settings, 'USE_REFACTORED_DASHBOARD', False)
    USE_REFACTORED_CURRICULUM = getattr(settings, 'USE_REFACTORED_CURRICULUM', False)
    USE_REFACTORED_PLACEMENT_RULES = getattr(settings, 'USE_REFACTORED_PLACEMENT_RULES', False)
    USE_REFACTORED_START_TEST = getattr(settings, 'USE_REFACTORED_START_TEST', False)
    USE_REFACTORED_SUBMIT_ANSWER = getattr(settings, 'USE_REFACTORED_SUBMIT_ANSWER', False)
    
    @classmethod
    def is_enabled(cls, flag_name):
        """Check if a feature flag is enabled."""
        # Check global flag first
        if cls.USE_REFACTORED_VIEWS:
            return True
        
        # Check specific flags
        return getattr(cls, flag_name, False)
    
    @classmethod
    def get_view_function(cls, original_view, refactored_view, flag_name):
        """
        Return the appropriate view function based on feature flag.
        
        Args:
            original_view: The original view function
            refactored_view: The refactored view function
            flag_name: The feature flag name to check
            
        Returns:
            The appropriate view function
        """
        if cls.is_enabled(flag_name):
            return refactored_view
        return original_view
    
    @classmethod
    def get_all_flags(cls):
        """Get all feature flags and their status."""
        flags = {}
        for attr in dir(cls):
            if attr.startswith('USE_'):
                flags[attr] = getattr(cls, attr)
        return flags


def conditional_view(flag_name):
    """
    Decorator to conditionally use refactored views.
    
    Usage:
        @conditional_view('USE_REFACTORED_DASHBOARD')
        def dashboard(request):
            # This will use refactored version if flag is enabled
            pass
    """
    def decorator(original_view):
        def wrapper(request, *args, **kwargs):
            # Try to import refactored view
            try:
                module_name = original_view.__module__
                if 'core.views' in module_name:
                    from core import views_refactored
                    refactored_view = getattr(views_refactored, original_view.__name__, None)
                elif 'placement_test.views' in module_name:
                    from placement_test import views_refactored
                    refactored_view = getattr(views_refactored, original_view.__name__, None)
                else:
                    refactored_view = None
                
                if refactored_view and FeatureFlags.is_enabled(flag_name):
                    return refactored_view(request, *args, **kwargs)
            except ImportError:
                pass
            
            # Fall back to original view
            return original_view(request, *args, **kwargs)
        
        wrapper.__name__ = original_view.__name__
        wrapper.__doc__ = original_view.__doc__
        return wrapper
    
    return decorator
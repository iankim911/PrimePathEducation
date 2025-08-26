"""
Phase 3: Template Compatibility Layer
Date: August 26, 2025
Purpose: Provides backward compatibility during migration from base.html and routinetest_base.html to unified_base.html
"""

import logging
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.http import HttpResponse
from pathlib import Path

logger = logging.getLogger(__name__)

class TemplateCompatibilityMiddleware:
    """
    Middleware to handle template migration compatibility.
    Maps old base templates to new unified_base.html during transition period.
    """
    
    # Templates that have been migrated to use unified_base.html
    MIGRATED_TEMPLATES = set([
        'test_unified_placement.html',
        'test_unified_routine.html',
        # Add templates here as they're migrated
    ])
    
    # Map of old base templates to new unified base
    BASE_TEMPLATE_MAP = {
        'base.html': 'unified_base.html',
        'routinetest_base.html': 'unified_base.html',
    }
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.compatibility_mode = True  # Can be toggled via settings
        
    def __call__(self, request):
        """Process the request and response."""
        
        # Add compatibility flag to request
        request.template_compatibility = {
            'mode': self.compatibility_mode,
            'migrated': self.MIGRATED_TEMPLATES,
            'mapping': self.BASE_TEMPLATE_MAP
        }
        
        # Process the response
        response = self.get_response(request)
        
        # Log template usage for migration tracking
        if hasattr(request, 'template_used'):
            self._log_template_usage(request.template_used)
            
        return response
    
    def _log_template_usage(self, template_name):
        """Log which base template is being used for migration tracking."""
        if template_name in self.MIGRATED_TEMPLATES:
            logger.debug(f"✅ {template_name} using unified_base.html")
        else:
            logger.debug(f"⏳ {template_name} still using old base template")

    @classmethod
    def is_template_migrated(cls, template_name):
        """Check if a template has been migrated to unified base."""
        return template_name in cls.MIGRATED_TEMPLATES
    
    @classmethod
    def mark_template_migrated(cls, template_name):
        """Mark a template as migrated (for use in migration scripts)."""
        cls.MIGRATED_TEMPLATES.add(template_name)
        logger.info(f"Marked {template_name} as migrated to unified_base.html")


class TemplateContextProcessor:
    """
    Context processor to inject compatibility data into template context.
    """
    
    def __init__(self, request):
        self.request = request
        
    def get_context_data(self):
        """Return compatibility context data."""
        context = {
            'using_unified_base': False,
            'template_module': 'core',
            'compatibility_mode': True,
        }
        
        # Check if current template is using unified base
        if hasattr(self.request, 'template_compatibility'):
            template_name = getattr(self.request, 'template_name', None)
            if template_name:
                context['using_unified_base'] = TemplateCompatibilityMiddleware.is_template_migrated(template_name)
                
        # Detect module from URL
        if '/placement/' in self.request.path:
            context['template_module'] = 'placement_test'
        elif '/RoutineTest/' in self.request.path:
            context['template_module'] = 'primepath_routinetest'
            
        return context


def template_compatibility(request):
    """
    Context processor function for template compatibility.
    Add to TEMPLATES['OPTIONS']['context_processors'] in settings.
    """
    processor = TemplateContextProcessor(request)
    return processor.get_context_data()
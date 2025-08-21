"""
Template filter for displaying access levels with better clarity
"""
from django import template

register = template.Library()

@register.filter
def display_access_level(access_level):
    """
    Convert access level codes to user-friendly display text
    
    Args:
        access_level: The access level code (FULL, VIEW, CO_TEACHER, etc.)
    
    Returns:
        User-friendly display text
    """
    ACCESS_LEVEL_DISPLAY = {
        'FULL': 'FULL ACCESS',
        'FULL ACCESS': 'FULL ACCESS',
        'VIEW': 'VIEW ONLY',
        'VIEW ONLY': 'VIEW ONLY',
        'CO_TEACHER': 'CO-TEACHER',
        'SUBSTITUTE': 'SUBSTITUTE',
        'OWNER': 'OWNER',
        'ADMIN': 'ADMIN',
        'EDIT': 'EDIT',
        'ASSIGNED': 'ASSIGNED',
    }
    
    return ACCESS_LEVEL_DISPLAY.get(access_level, access_level)

@register.filter
def access_level_class(access_level):
    """
    Get CSS class for access level styling
    
    Args:
        access_level: The access level code
    
    Returns:
        CSS class name
    """
    # Convert to lowercase and replace underscores with hyphens
    return access_level.lower().replace('_', '-')
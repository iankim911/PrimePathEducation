"""
Template filters for the Schedule Matrix
"""
from django import template
import logging

# Create template library
register = template.Library()

# Setup logging
logger = logging.getLogger(__name__)
logger.info("[MATRIX_FILTERS] Loading matrix_filters template tags")
print("[MATRIX_FILTERS] Loading matrix_filters template tags")


@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Get an item from a dictionary using a variable as key.
    Usage: {{ dict|get_item:variable }}
    """
    if dictionary is None:
        return None
    try:
        result = dictionary.get(key)
        return result
    except (AttributeError, TypeError) as e:
        logger.warning(f"[MATRIX_FILTERS] get_item filter error: {e}")
        return None


@register.filter(name='dict_get')
def dict_get(dictionary, key):
    """
    Alternative filter for dictionary access.
    Usage: {{ dict|dict_get:key }}
    """
    if not dictionary:
        return None
    try:
        return dictionary.get(key, None)
    except (AttributeError, TypeError):
        return None


# Matrix-specific filters removed - visual component eliminated
# Removed filters: matrix_cell, count_exams, exam_count_class, exam_count_label_class


@register.filter(name='lookup')
def lookup(dictionary, key):
    """
    Enhanced dictionary lookup filter for Answer Keys Library.
    Usage: {{ dict|lookup:key }}
    """
    if not dictionary:
        return None
    
    try:
        # Handle different types of containers
        if hasattr(dictionary, 'get'):
            # Dictionary-like object
            return dictionary.get(key, None)
        elif hasattr(dictionary, '__getitem__'):
            # List-like or dict-like with __getitem__
            try:
                return dictionary[key]
            except (KeyError, IndexError, TypeError):
                return None
        else:
            return None
    except Exception as e:
        logger.warning(f"[MATRIX_FILTERS] lookup filter error: {e}")
        return None


@register.filter(name='has_key')
def has_key(dictionary, key):
    """
    Check if dictionary has a specific key.
    Usage: {{ dict|has_key:key }}
    """
    if not dictionary:
        return False
    
    try:
        if hasattr(dictionary, 'get'):
            return key in dictionary
        elif hasattr(dictionary, '__contains__'):
            return key in dictionary
        else:
            return False
    except Exception:
        return False


@register.filter(name='keys')
def keys(dictionary):
    """
    Get keys from a dictionary.
    Usage: {{ dict|keys }}
    """
    if not dictionary:
        return []
    
    try:
        if hasattr(dictionary, 'keys'):
            return list(dictionary.keys())
        else:
            return []
    except Exception:
        return []


# Debug log to confirm the module loaded
logger.info(f"[MATRIX_FILTERS] Registered filters: {list(register.filters.keys())}")
print(f"[MATRIX_FILTERS] Registered filters: {list(register.filters.keys())}")

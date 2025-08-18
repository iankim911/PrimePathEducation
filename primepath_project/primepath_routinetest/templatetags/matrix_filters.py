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


@register.filter(name='matrix_cell')
def matrix_cell(row_data, column_key):
    """
    Get a matrix cell from row data.
    Usage: {{ row|matrix_cell:column }}
    """
    if not row_data or not hasattr(row_data, 'get'):
        return None
    
    cells = row_data.get('cells', {})
    if not cells:
        return None
    
    return cells.get(column_key, None)


# Debug log to confirm the module loaded
logger.info(f"[MATRIX_FILTERS] Registered filters: {list(register.filters.keys())}")
print(f"[MATRIX_FILTERS] Registered filters: {list(register.filters.keys())}")

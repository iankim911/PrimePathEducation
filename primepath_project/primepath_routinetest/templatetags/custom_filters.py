"""
Custom template filters for RoutineTest
"""
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Get item from dictionary using key"""
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def replace(value, arg):
    """Replace string occurrences"""
    if not value:
        return value
    old, new = arg.split(':')
    return value.replace(old, new)


@register.filter
def split(value, delimiter=' '):
    """Split string by delimiter"""
    if not value:
        return []
    return value.split(delimiter)
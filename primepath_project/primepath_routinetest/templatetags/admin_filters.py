"""
Admin Template Filters for Teacher Management Dashboard
Provides utility filters for complex template operations
"""
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Template filter to access dictionary items with dynamic keys
    Usage: {{ my_dict|get_item:key_variable }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def get_teacher_classes(matrix_data, teacher_id):
    """
    Get all class data for a specific teacher from matrix
    Usage: {{ matrix_data|get_teacher_classes:teacher.id }}
    """
    if matrix_data is None or teacher_id is None:
        return {}
    return matrix_data.get(str(teacher_id), {})


@register.filter
def has_access_to_class(matrix_data, teacher_class_key):
    """
    Check if teacher has access to a specific class
    Usage: {{ matrix_data|has_access_to_class:"teacher_id_class_code" }}
    """
    if matrix_data is None or teacher_class_key is None:
        return False
    
    try:
        teacher_id, class_code = teacher_class_key.split('_', 1)
        teacher_data = matrix_data.get(str(teacher_id), {})
        class_data = teacher_data.get(class_code, {})
        return class_data.get('has_access', False)
    except:
        return False


@register.filter
def get_access_level(matrix_data, teacher_class_key):
    """
    Get access level for teacher-class combination
    Usage: {{ matrix_data|get_access_level:"teacher_id_class_code" }}
    """
    if matrix_data is None or teacher_class_key is None:
        return None
    
    try:
        teacher_id, class_code = teacher_class_key.split('_', 1)
        teacher_data = matrix_data.get(str(teacher_id), {})
        class_data = teacher_data.get(class_code, {})
        return class_data.get('access_level')
    except:
        return None


@register.filter
def pluralize_smart(value, text):
    """
    Smart pluralization filter
    Usage: {{ count|pluralize_smart:"teacher,teachers" }}
    """
    try:
        count = int(value)
        singular, plural = text.split(',')
        return singular if count == 1 else plural
    except:
        return text


@register.filter
def class_teacher_count_class(count):
    """
    Get CSS class for teacher count badge
    Usage: {{ teacher_count|class_teacher_count_class }}
    """
    if count == 0:
        return "zero"
    elif count > 1:
        return "multi"
    else:
        return ""


@register.filter
def format_access_badge_class(access_level):
    """
    Get CSS class for access level badge
    Usage: {{ access_level|format_access_badge_class }}
    """
    if access_level == 'FULL':
        return "full"
    elif access_level == 'VIEW':
        return "view"
    else:
        return ""


@register.filter
def days_since(date_value):
    """
    Calculate days since a date
    Usage: {{ request.requested_at|days_since }}
    """
    try:
        from django.utils import timezone
        from datetime import datetime
        
        if date_value is None:
            return 0
        
        if isinstance(date_value, str):
            # Parse ISO format or common date formats
            try:
                date_value = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
            except:
                return 0
        
        now = timezone.now()
        if hasattr(date_value, 'tzinfo') and date_value.tzinfo is None:
            date_value = timezone.make_aware(date_value)
        
        delta = now - date_value
        return delta.days
    except:
        return 0


@register.filter
def format_percentage(value, total):
    """
    Format a percentage from value and total
    Usage: {{ completed|format_percentage:total }}
    """
    try:
        value = float(value)
        total = float(total)
        if total == 0:
            return "0%"
        percentage = (value / total) * 100
        return f"{percentage:.1f}%"
    except:
        return "0%"


@register.simple_tag
def get_matrix_cell(matrix_data, teacher_id, class_code):
    """
    Get matrix cell data for teacher-class combination
    Usage: {% get_matrix_cell matrix_data teacher.id class.code as cell_data %}
    """
    if matrix_data is None or teacher_id is None or class_code is None:
        return {
            'has_access': False,
            'access_level': None,
            'assignment_id': None,
            'assigned_date': None
        }
    
    teacher_data = matrix_data.get(str(teacher_id), {})
    return teacher_data.get(class_code, {
        'has_access': False,
        'access_level': None,
        'assignment_id': None,
        'assigned_date': None
    })


@register.inclusion_tag('primepath_routinetest/includes/access_level_badge.html')
def access_level_badge(access_level, size='normal'):
    """
    Render an access level badge
    Usage: {% access_level_badge assignment.access_level %}
    """
    return {
        'access_level': access_level,
        'size': size,
        'css_class': format_access_badge_class(access_level)
    }


@register.inclusion_tag('primepath_routinetest/includes/teacher_count_badge.html')
def teacher_count_badge(count):
    """
    Render a teacher count badge
    Usage: {% teacher_count_badge class.teacher_count %}
    """
    return {
        'count': count,
        'css_class': class_teacher_count_class(count),
        'text': f"{count} Teacher{'s' if count != 1 else ''}"
    }


# Debug filters for development
@register.filter
def debug_type(value):
    """Debug filter to check type of value"""
    return type(value).__name__


@register.filter
def debug_length(value):
    """Debug filter to check length of value"""
    try:
        return len(value)
    except:
        return "No length"


@register.filter
def debug_keys(value):
    """Debug filter to check keys of dictionary"""
    try:
        if hasattr(value, 'keys'):
            return list(value.keys())[:5]  # First 5 keys
        return "Not a dict"
    except:
        return "Error getting keys"
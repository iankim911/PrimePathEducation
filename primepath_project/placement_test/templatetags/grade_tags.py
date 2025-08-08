from django import template

register = template.Library()

@register.filter
def split(value, delimiter=','):
    """
    Split a string by delimiter and return a list
    Usage: {{ value|split:',' }}
    """
    if value is None:
        return []
    return [item.strip() for item in str(value).split(delimiter)]

@register.filter
def format_grade(grade):
    """Format grade number to Korean school system format"""
    try:
        grade = int(grade)
        if 1 <= grade <= 6:
            return f"Primary {grade}"
        elif 7 <= grade <= 9:
            return f"Middle School {grade - 6}"
        elif 10 <= grade <= 12:
            return f"High School {grade - 9}"
        else:
            return f"Grade {grade}"
    except (ValueError, TypeError):
        return str(grade)
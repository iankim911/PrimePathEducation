"""
Phone number utilities for internationalization support
Provides configurable phone validation and formatting based on locale
"""
from django.core.validators import RegexValidator
from django.conf import settings
import re

# Default phone number configurations by country
PHONE_CONFIGS = {
    'KR': {  # South Korea
        'regex': r'^01[0-9]-?[0-9]{3,4}-?[0-9]{4}$',
        'message': 'Korean phone format: 010-XXXX-XXXX',
        'placeholder': '+82 10-XXXX-XXXX',
        'example': '010-1234-5678'
    },
    'US': {  # United States
        'regex': r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$',
        'message': 'US phone format: (XXX) XXX-XXXX',
        'placeholder': '+1 (XXX) XXX-XXXX',
        'example': '(555) 123-4567'
    },
    'GB': {  # United Kingdom
        'regex': r'^(\+44\s?7\d{3}|\(?07\d{3}\)?)\s?\d{3}\s?\d{3}$',
        'message': 'UK mobile format: 07XXX XXXXXX',
        'placeholder': '+44 7XXX XXXXXX',
        'example': '07123 456789'
    },
    'CA': {  # Canada
        'regex': r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$',
        'message': 'Canadian phone format: (XXX) XXX-XXXX',
        'placeholder': '+1 (XXX) XXX-XXXX',
        'example': '(416) 123-4567'
    },
    'INTERNATIONAL': {  # Generic international
        'regex': r'^\+?[1-9]\d{1,14}$',
        'message': 'International format: +[country code][number]',
        'placeholder': '+[country code] [number]',
        'example': '+82 10-1234-5678'
    }
}

def get_current_locale():
    """
    Get the current locale from Django settings.
    Falls back to KR (Korean) if not specified or invalid.
    """
    # Check for custom phone locale setting
    phone_locale = getattr(settings, 'PHONE_LOCALE', None)
    if phone_locale and phone_locale in PHONE_CONFIGS:
        return phone_locale
    
    # Check standard Django language code
    language_code = getattr(settings, 'LANGUAGE_CODE', 'ko-kr')
    country_code = language_code.split('-')[-1].upper() if '-' in language_code else 'KR'
    
    # Return valid country code or default to Korea
    return country_code if country_code in PHONE_CONFIGS else 'KR'

def get_phone_config(locale=None):
    """
    Get phone configuration for a specific locale.
    
    Args:
        locale: Country code (e.g., 'KR', 'US'). If None, uses current locale.
        
    Returns:
        dict: Phone configuration with regex, message, placeholder, example
    """
    if locale is None:
        locale = get_current_locale()
    
    return PHONE_CONFIGS.get(locale, PHONE_CONFIGS['KR'])

def get_phone_validator(locale=None):
    """
    Get a Django RegexValidator for phone numbers based on locale.
    
    Args:
        locale: Country code (e.g., 'KR', 'US'). If None, uses current locale.
        
    Returns:
        RegexValidator: Configured validator for the locale
    """
    config = get_phone_config(locale)
    return RegexValidator(
        regex=config['regex'],
        message=config['message']
    )

def get_phone_placeholder(locale=None):
    """
    Get the placeholder text for phone input fields.
    
    Args:
        locale: Country code (e.g., 'KR', 'US'). If None, uses current locale.
        
    Returns:
        str: Placeholder text
    """
    config = get_phone_config(locale)
    return config['placeholder']

def get_phone_example(locale=None):
    """
    Get an example phone number for the locale.
    
    Args:
        locale: Country code (e.g., 'KR', 'US'). If None, uses current locale.
        
    Returns:
        str: Example phone number
    """
    config = get_phone_config(locale)
    return config['example']

def format_phone_number(phone_number, locale=None):
    """
    Format a phone number according to the locale's standard format.
    Basic implementation - can be enhanced with more sophisticated formatting.
    
    Args:
        phone_number: Raw phone number string
        locale: Country code (e.g., 'KR', 'US'). If None, uses current locale.
        
    Returns:
        str: Formatted phone number or original if formatting fails
    """
    if not phone_number:
        return phone_number
    
    if locale is None:
        locale = get_current_locale()
    
    # Remove all non-digit characters for processing
    digits = re.sub(r'[^\d]', '', phone_number)
    
    try:
        if locale == 'KR':
            # Korean format: 010-XXXX-XXXX
            if len(digits) == 11 and digits.startswith('01'):
                return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
        elif locale in ['US', 'CA']:
            # US/Canadian format: (XXX) XXX-XXXX
            if len(digits) == 10:
                return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            elif len(digits) == 11 and digits.startswith('1'):
                return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        elif locale == 'GB':
            # UK format: 07XXX XXXXXX
            if len(digits) == 11 and digits.startswith('07'):
                return f"{digits[:5]} {digits[5:]}"
    except (IndexError, ValueError):
        pass
    
    # Return original if formatting fails
    return phone_number

def validate_phone_number(phone_number, locale=None):
    """
    Validate a phone number against the locale's format.
    
    Args:
        phone_number: Phone number to validate
        locale: Country code (e.g., 'KR', 'US'). If None, uses current locale.
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not phone_number:
        return True, None
    
    validator = get_phone_validator(locale)
    
    try:
        validator(phone_number)
        return True, None
    except Exception as e:
        return False, str(e)

# For backward compatibility - maintains existing Korean phone validator
def get_korean_phone_validator():
    """
    Legacy function for backward compatibility.
    Returns the Korean phone validator.
    """
    return get_phone_validator('KR')

# Export the current locale's validator as default
phone_validator = get_phone_validator()
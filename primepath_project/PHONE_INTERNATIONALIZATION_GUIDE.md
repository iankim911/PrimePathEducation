# Phone Number Internationalization Guide

## Overview
The phone number system has been refactored to support multiple countries and regions, replacing the hardcoded Korean phone format with a configurable system.

## What Was Fixed

### Before (Hardcoded Korean)
```python
# Old hardcoded approach
korean_phone_regex = RegexValidator(
    regex=r'^01[0-9]-?[0-9]{3,4}-?[0-9]{4}$',
    message="Korean phone format: 010-XXXX-XXXX"
)

# Hardcoded placeholder in forms
'placeholder': '+82 10-XXXX-XXXX'
```

### After (Configurable International)
```python
# New configurable approach
from core.utils.phone_utils import get_phone_validator, get_phone_placeholder

phone_validator = get_phone_validator()  # Uses current locale
placeholder = get_phone_placeholder()    # Dynamic based on locale
```

## Configuration

### Setting the Phone Locale

**Option 1: Django Settings**
```python
# In settings.py
PHONE_LOCALE = 'KR'  # South Korea (default)
# or
PHONE_LOCALE = 'US'  # United States
# or 
PHONE_LOCALE = 'GB'  # United Kingdom
# or
PHONE_LOCALE = 'INTERNATIONAL'  # Generic international
```

**Option 2: Language Code Detection (Automatic)**
If `PHONE_LOCALE` is not set, the system uses Django's `LANGUAGE_CODE`:
- `ko-kr` → Korean format
- `en-us` → US format  
- `en-gb` → UK format
- Other → Korean (fallback)

## Supported Countries

| Country | Code | Format | Example | Placeholder |
|---------|------|--------|---------|-------------|
| South Korea | KR | 010-XXXX-XXXX | 010-1234-5678 | +82 10-XXXX-XXXX |
| United States | US | (XXX) XXX-XXXX | (555) 123-4567 | +1 (XXX) XXX-XXXX |
| United Kingdom | GB | 07XXX XXXXXX | 07123 456789 | +44 7XXX XXXXXX |
| Canada | CA | (XXX) XXX-XXXX | (416) 123-4567 | +1 (XXX) XXX-XXXX |
| International | INTERNATIONAL | +[code][number] | +82 10-1234-5678 | +[country code] [number] |

## Usage Examples

### In Models
```python
from core.utils.phone_utils import get_phone_validator

class MyModel(models.Model):
    phone = models.CharField(
        max_length=20,
        validators=[get_phone_validator()]  # Uses current locale
    )
    
    # Or for specific locale
    us_phone = models.CharField(
        max_length=20,
        validators=[get_phone_validator('US')]
    )
```

### In Forms
```python
from core.utils.phone_utils import get_phone_placeholder

class MyForm(forms.Form):
    phone = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': get_phone_placeholder()  # Dynamic
        })
    )
```

### Validation in Views
```python
from core.utils.phone_utils import validate_phone_number

def my_view(request):
    phone = request.POST.get('phone')
    is_valid, error = validate_phone_number(phone)
    if not is_valid:
        messages.error(request, f"Invalid phone: {error}")
```

### Formatting Phone Numbers
```python
from core.utils.phone_utils import format_phone_number

# Format according to current locale
formatted = format_phone_number('5551234567')  # → (555) 123-4567 (if US)

# Format for specific locale
korean_format = format_phone_number('01012345678', 'KR')  # → 010-1234-5678
```

## Test Results

✅ **Current System Status**:
- Korean validation: Working correctly
- US validation: Working correctly  
- UK validation: Working correctly
- International format: Working correctly
- Form placeholders: Dynamic based on locale
- Backward compatibility: Maintained

## Files Modified

1. **`core/utils/phone_utils.py`** - New phone utilities module
2. **`core/models/user_profile.py`** - Updated to use configurable validators
3. **`core/forms/registration.py`** - Updated placeholders to be dynamic
4. **`primepath_project/settings_phone.py`** - Configuration examples

## Adding New Countries

To add support for a new country:

1. Add configuration to `PHONE_CONFIGS` in `core/utils/phone_utils.py`:
```python
'FR': {  # France
    'regex': r'^0[1-9](?:[0-9]{8})$',
    'message': 'French phone format: 0X XX XX XX XX',
    'placeholder': '+33 X XX XX XX XX',
    'example': '01 23 45 67 89'
}
```

2. Set the locale in settings:
```python
PHONE_LOCALE = 'FR'
```

## Migration Notes

- **Backward Compatible**: Existing Korean phone validation still works
- **No Database Changes**: Only validation and display logic changed
- **Existing Data**: All existing phone numbers remain valid
- **Forms**: Automatically show appropriate placeholder for current locale

## Deployment Recommendations

### For Korean Schools (Current)
```python
PHONE_LOCALE = 'KR'
```

### For International Schools
```python
PHONE_LOCALE = 'INTERNATIONAL'
```

### For US/Canadian Schools  
```python
PHONE_LOCALE = 'US'  # or 'CA'
```

## Testing

Run the test script to verify functionality:
```bash
python test_phone_utils.py
```

Expected output shows validation working for all supported formats with appropriate formatting and error messages.

## Benefits

1. **Internationalization Ready**: Easy to deploy in different countries
2. **Configurable**: Change locale without code changes
3. **Backward Compatible**: Existing code continues to work
4. **Extensible**: Easy to add new countries
5. **User Friendly**: Appropriate placeholders and examples
6. **Validation**: Proper format validation per country
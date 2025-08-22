#!/usr/bin/env python
"""
Test the phone utilities functionality
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from core.utils.phone_utils import (
    get_phone_config, get_phone_validator, get_phone_placeholder,
    get_phone_example, format_phone_number, validate_phone_number,
    get_current_locale, PHONE_CONFIGS
)

def test_phone_utils():
    """Test phone utilities functionality"""
    print("\n" + "="*70)
    print("TESTING PHONE UTILITIES")
    print("="*70)
    
    # Test current locale detection
    current_locale = get_current_locale()
    print(f"✅ Current locale: {current_locale}")
    
    # Test configurations for different locales
    print(f"\n📱 Available phone configurations:")
    for locale, config in PHONE_CONFIGS.items():
        print(f"  {locale}: {config['placeholder']} (example: {config['example']})")
    
    # Test Korean phone validation (current default)
    print(f"\n🧪 Testing Korean phone validation:")
    korean_examples = [
        '010-1234-5678',  # Valid
        '01012345678',    # Valid (no dashes)
        '02-123-4567',    # Invalid (landline)
        '123-456-7890',   # Invalid format
        '+82-10-1234-5678'  # International format
    ]
    
    for phone in korean_examples:
        is_valid, error = validate_phone_number(phone, 'KR')
        status = "✅ VALID" if is_valid else f"❌ INVALID ({error})"
        formatted = format_phone_number(phone, 'KR')
        print(f"  {phone:15} -> {status:30} | Formatted: {formatted}")
    
    # Test US phone validation
    print(f"\n🧪 Testing US phone validation:")
    us_examples = [
        '(555) 123-4567',  # Valid
        '555-123-4567',    # Valid
        '5551234567',      # Valid
        '+1-555-123-4567', # Valid international
        '123-45-6789',     # Invalid (too short)
    ]
    
    for phone in us_examples:
        is_valid, error = validate_phone_number(phone, 'US')
        status = "✅ VALID" if is_valid else f"❌ INVALID ({error})"
        formatted = format_phone_number(phone, 'US')
        print(f"  {phone:15} -> {status:30} | Formatted: {formatted}")
    
    # Test placeholder and example generation
    print(f"\n📝 Testing placeholder generation:")
    for locale in ['KR', 'US', 'GB', 'INTERNATIONAL']:
        placeholder = get_phone_placeholder(locale)
        example = get_phone_example(locale)
        print(f"  {locale:12} -> Placeholder: {placeholder:20} | Example: {example}")
    
    # Test validator generation
    print(f"\n⚡ Testing validator generation:")
    try:
        validator = get_phone_validator('KR')
        # Test with valid Korean number
        validator('010-1234-5678')
        print(f"  ✅ Korean validator works correctly")
    except Exception as e:
        print(f"  ❌ Korean validator failed: {e}")
    
    try:
        validator = get_phone_validator('US')
        # Test with valid US number
        validator('(555) 123-4567')
        print(f"  ✅ US validator works correctly")
    except Exception as e:
        print(f"  ❌ US validator failed: {e}")
    
    print(f"\n🔧 Testing backward compatibility:")
    from core.models.user_profile import korean_phone_regex, phone_validator
    try:
        korean_phone_regex('010-1234-5678')
        print(f"  ✅ Legacy korean_phone_regex works")
    except Exception as e:
        print(f"  ❌ Legacy korean_phone_regex failed: {e}")
    
    try:
        phone_validator('010-1234-5678')
        print(f"  ✅ Default phone_validator works")
    except Exception as e:
        print(f"  ❌ Default phone_validator failed: {e}")
    
    return True

if __name__ == '__main__':
    try:
        success = test_phone_utils()
        if success:
            print("\n✅ Phone utilities test completed successfully")
        else:
            print("\n❌ Test encountered issues")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
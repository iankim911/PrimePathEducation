"""
Phone number localization settings
Add this to your main settings file or import specific values
"""

# Phone number locale configuration
# Set this to the country code for your primary user base
PHONE_LOCALE = 'KR'  # South Korea

# Alternative configurations for different deployments:

# For US deployment:
# PHONE_LOCALE = 'US'

# For UK deployment:
# PHONE_LOCALE = 'GB'

# For international deployment (most flexible):
# PHONE_LOCALE = 'INTERNATIONAL'

# For multiple country support, you can also set per-user preferences
# This would require extending the user model with a locale preference field

PHONE_VALIDATION_SETTINGS = {
    'STRICT_VALIDATION': True,  # Set to False for more lenient validation
    'ALLOW_INTERNATIONAL': True,  # Allow international format even with specific locale
    'DEFAULT_COUNTRY_CODE': '+82',  # Default country code for display
}

# Usage examples:
# 1. To change from Korean to US phone format:
#    PHONE_LOCALE = 'US'
#
# 2. To allow any international format:
#    PHONE_LOCALE = 'INTERNATIONAL'
#
# 3. To add custom validation messages:
#    Add custom configuration to core/utils/phone_utils.py PHONE_CONFIGS
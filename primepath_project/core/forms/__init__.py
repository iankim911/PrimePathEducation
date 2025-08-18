"""
Core Forms Package
"""
from .registration import (
    BasicRegistrationForm,
    PersonalInfoForm,
    AddressForm,
    EducationalInfoForm,
    ParentGuardianForm,
    AdditionalInfoForm,
    SocialAuthCompleteProfileForm,
)

__all__ = [
    'BasicRegistrationForm',
    'PersonalInfoForm',
    'AddressForm',
    'EducationalInfoForm',
    'ParentGuardianForm',
    'AdditionalInfoForm',
    'SocialAuthCompleteProfileForm',
]
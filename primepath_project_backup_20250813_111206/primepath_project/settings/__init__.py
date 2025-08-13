"""
Settings module for PrimePath project.
Loads appropriate settings based on environment.
"""
import os

# Determine which settings to use based on environment
env = os.environ.get('DJANGO_SETTINGS_ENV', 'development')

if env == 'production':
    from .production import *
elif env == 'development':
    from .development import *
else:
    from .base import *
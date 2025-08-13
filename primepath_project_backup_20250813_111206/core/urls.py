"""
Core URLs

This file maintains 100% backward compatibility.
All existing URL patterns are preserved and continue to work exactly as before.

The URLs have been organized into logical modules:
- dashboard_urls.py: Main navigation and dashboard URLs
- admin_urls.py: Administrative function URLs
- api_urls.py: Core API endpoint URLs
- auth_urls.py: Authentication URLs (login/logout/profile)

All URL patterns are imported here to maintain compatibility.
"""
from django.urls import path
from .dashboard_urls import urlpatterns as dashboard_patterns
from .admin_urls import urlpatterns as admin_patterns
from .api_urls import urlpatterns as api_patterns
from .auth_urls import urlpatterns as auth_patterns

app_name = 'core'

# Combine all URL patterns from modular files
urlpatterns = []
urlpatterns.extend(dashboard_patterns)
urlpatterns.extend(admin_patterns)
urlpatterns.extend(api_patterns)
urlpatterns.extend(auth_patterns)
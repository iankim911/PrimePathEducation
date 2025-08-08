"""
Main API URLs with versioning support
Part of Phase 11: Final Integration & Testing

This file routes API requests to appropriate versions.
Currently supports:
- v1: Current stable API (default)
- Legacy: Backward compatibility with non-versioned endpoints
"""
from django.urls import path, include

app_name = 'api'

urlpatterns = [
    # Version 1 API (current)
    path('v1/', include('api.v1.urls')),
    
    # Default to v1 for backward compatibility
    # This allows existing integrations to continue working
    path('', include('api.v1.urls')),
]
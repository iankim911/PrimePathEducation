"""
URL configuration for primepath_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/placement/', include('placement_test.urls')),
    path('api/v2/placement/', include('placement_test.api_urls')),  # New modular API
    path('api/', include('api.urls')),  # API with versioning support (includes v1 and backward compatibility)
    path('api-auth/', include('rest_framework.urls')),  # DRF login/logout views
    
    # BACKWARD COMPATIBILITY: Legacy URL patterns
    # Maps /placement/test/{id}/ to existing views for backward compatibility
    path('placement/', include('placement_test.legacy_urls')),
    
    # Authentication URLs - redirect /accounts/ to core auth
    path('accounts/login/', RedirectView.as_view(url='/login/', permanent=False), name='login'),
    path('accounts/logout/', RedirectView.as_view(url='/logout/', permanent=False), name='logout'),
    path('accounts/profile/', RedirectView.as_view(url='/profile/', permanent=False), name='profile'),
    
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
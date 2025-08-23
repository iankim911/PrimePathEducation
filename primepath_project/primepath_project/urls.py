"""
URL configuration for primepath_project project.
UPDATED: Clear URL structure with /PlacementTest/ and /RoutineTest/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from core.kakao_urls import kakao_urlpatterns
import json

# Log URL configuration changes
print("""
╔═══════════════════════════════════════════════════════════════════╗
║   URL STRUCTURE UPDATE - CLEAR TEST TYPE IDENTIFICATION          ║
╠═══════════════════════════════════════════════════════════════════╣
║   Phase 1: /PlacementTest/ - Placement Testing System            ║
║   Phase 2: /RoutineTest/   - Routine Testing System              ║
╚═══════════════════════════════════════════════════════════════════╝
""")

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ============= PHASE 1: PLACEMENT TEST URLs =============
    # Main Placement Test URLs (NEW STRUCTURE)
    path('PlacementTest/', include('placement_test.urls')),
    path('api/PlacementTest/', include('placement_test.api_urls')),
    path('api/v2/PlacementTest/', include('placement_test.api_urls')),  # V2 API
    
    # ============= PHASE 2: ROUTINE TEST URLs =============
    # Main Routine Test URLs (NEW STRUCTURE)
    path('RoutineTest/', include('primepath_routinetest.urls')),
    path('api/RoutineTest/', include('primepath_routinetest.api_urls')),
    
    # ============= BACKWARD COMPATIBILITY REDIRECTS =============
    # These ensure old URLs still work by redirecting to new structure
    path('placement/', RedirectView.as_view(url='/PlacementTest/', permanent=False)),
    path('api/placement/', RedirectView.as_view(url='/api/PlacementTest/', permanent=False)),
    path('api/v2/placement/', RedirectView.as_view(url='/api/v2/PlacementTest/', permanent=False)),
    path('routine/', RedirectView.as_view(url='/RoutineTest/', permanent=False)),
    path('api/routine/', RedirectView.as_view(url='/api/RoutineTest/', permanent=False)),
    path('teacher/', RedirectView.as_view(url='/PlacementTest/teacher/', permanent=False)),
    
    # Legacy URLs for maximum compatibility
    # REMOVED: This was causing '/placement/test/session/{uuid}/' to become '/PlacementTest/test/session/{uuid}/'
    # which doesn't match any URL pattern. The correct URL should be '/PlacementTest/session/{uuid}/'
    
    # ============= CORE SYSTEM URLs =============
    path('api/', include('api.urls')),  # API with versioning support
    path('api-auth/', include('rest_framework.urls')),  # DRF login/logout views
    
    # Authentication URLs - redirect /accounts/ to core auth
    path('accounts/login/', RedirectView.as_view(url='/login/', permanent=False), name='login'),
    path('accounts/logout/', RedirectView.as_view(url='/logout/', permanent=False), name='logout'),
    path('accounts/profile/', RedirectView.as_view(url='/profile/', permanent=False), name='profile'),
    
    # Django-allauth URLs for social authentication
    path('accounts/', include('allauth.urls')),
    
    path('', include('core.urls')),
] + kakao_urlpatterns  # Add Kakao OAuth URLs

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
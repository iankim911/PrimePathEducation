"""
API v1 URLs
Version 1 of the PrimePath API endpoints
Part of Phase 11: Final Integration & Testing
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ExamViewSet, StudentSessionViewSet, SchoolViewSet,
    ProgramViewSet,
    DashboardAPIView, HealthCheckAPIView
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'exams', ExamViewSet)
router.register(r'sessions', StudentSessionViewSet)
router.register(r'schools', SchoolViewSet)
router.register(r'programs', ProgramViewSet)

app_name = 'core_api_v1'

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Custom API views
    path('dashboard/', DashboardAPIView.as_view(), name='dashboard'),
    path('health/', HealthCheckAPIView.as_view(), name='health'),
    
    # Core placement endpoints
    path('PlacementTest/start/', StudentSessionViewSet.as_view({'post': 'create'}), name='start_test'),
    path('PlacementTest/session/<uuid:pk>/submit/', 
         StudentSessionViewSet.as_view({'post': 'submit_answer'}), 
         name='submit_answer'),
    path('PlacementTest/session/<uuid:pk>/complete/', 
         StudentSessionViewSet.as_view({'post': 'complete'}), 
         name='complete_test'),
]
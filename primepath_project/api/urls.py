"""
API URLs - Phase 8
URL routing for RESTful API endpoints
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

app_name = 'api'

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Custom API views
    path('dashboard/', DashboardAPIView.as_view(), name='dashboard'),
    path('health/', HealthCheckAPIView.as_view(), name='health'),
    
    # Backward compatibility endpoints
    path('placement/start/', StudentSessionViewSet.as_view({'post': 'create'}), name='start_test'),
    path('placement/session/<uuid:pk>/submit/', 
         StudentSessionViewSet.as_view({'post': 'submit_answer'}), 
         name='submit_answer'),
    path('placement/session/<uuid:pk>/complete/', 
         StudentSessionViewSet.as_view({'post': 'complete'}), 
         name='complete_test'),
]
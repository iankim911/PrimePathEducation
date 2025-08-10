"""
Legacy URL patterns for backward compatibility
Provides aliases for old URL patterns to prevent 404 errors
"""
from django.urls import path
from .views import student as views

# Legacy URL patterns - these map old URLs to existing views
legacy_patterns = [
    # Legacy student test URLs
    # Maps /placement/test/{id}/ to the same view as /api/placement/session/{id}/
    path('test/<uuid:session_id>/', views.take_test, name='take_test_legacy'),
    
    # Additional legacy patterns if needed in the future
    # path('test/<uuid:session_id>/submit/', views.submit_answer, name='submit_answer_legacy'),
    # path('test/<uuid:session_id>/complete/', views.complete_test, name='complete_test_legacy'),
    # path('test/<uuid:session_id>/result/', views.test_result, name='test_result_legacy'),
]

# Export for inclusion in main URL config
urlpatterns = legacy_patterns
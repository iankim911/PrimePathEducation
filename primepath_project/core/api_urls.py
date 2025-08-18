"""
Core API URLs
URLs for core API endpoints and AJAX functionality
"""
from django.urls import path
from .views import (
    get_placement_rules, save_placement_rules,
    save_exam_mappings, save_difficulty_levels
)

urlpatterns = [
    # API endpoints
    path('api/placement-rules/', get_placement_rules, name='get_placement_rules'),
    path('api/placement-rules/save/', save_placement_rules, name='save_placement_rules'),
    path('api/exam-mappings/save/', save_exam_mappings, name='save_exam_mappings'),
    path('api/difficulty-levels/save/', save_difficulty_levels, name='save_difficulty_levels'),
]
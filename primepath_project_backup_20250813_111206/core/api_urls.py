"""
Core API URLs
URLs for core API endpoints and AJAX functionality
"""
from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path('api/placement-rules/', views.get_placement_rules, name='get_placement_rules'),
    path('api/placement-rules/save/', views.save_placement_rules, name='save_placement_rules'),
    path('api/exam-mappings/save/', views.save_exam_mappings, name='save_exam_mappings'),
    path('api/difficulty-levels/save/', views.save_difficulty_levels, name='save_difficulty_levels'),
]
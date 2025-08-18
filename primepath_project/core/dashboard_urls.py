"""
Dashboard URLs
URLs for main navigation and teacher dashboard functionality
"""
from django.urls import path
from .views import index, teacher_dashboard, curriculum_levels

urlpatterns = [
    # Main navigation and dashboard
    path('', index, name='index'),
    path('teacher/dashboard/', teacher_dashboard, name='teacher_dashboard'),
    path('curriculum/levels/', curriculum_levels, name='curriculum_levels'),
]
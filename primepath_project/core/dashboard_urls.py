"""
Dashboard URLs
URLs for main navigation and teacher dashboard functionality
"""
from django.urls import path
from . import views

urlpatterns = [
    # Main navigation and dashboard
    path('', views.index, name='index'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('curriculum/levels/', views.curriculum_levels, name='curriculum_levels'),
]
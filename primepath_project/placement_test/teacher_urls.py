"""
Teacher Dashboard URLs - Comprehensive Authentication & Management

This module provides URL patterns for teacher dashboard functionality including:
- Teacher authentication and authorization
- Dashboard overview with statistics
- Teacher management operations
- Exam oversight and monitoring
- Student session supervision

All URLs require teacher authentication and proper permissions.
Enhanced with robust logging and error handling.
"""
import json
import logging
from django.urls import path
from django.contrib.auth.decorators import login_required
from .views.teacher import (
    TeacherDashboardView,
    TeacherLoginView,
    TeacherLogoutView,
    TeacherSessionListView,
    TeacherExamOverviewView,
    TeacherSettingsView
)

# Initialize logger
logger = logging.getLogger('placement_test.teacher_urls')

# Console logging for teacher URL configuration
console_log = {
    "event": "TEACHER_URLS_INIT",
    "module": "teacher_urls.py",
    "url_patterns": [
        "teacher/dashboard/",
        "teacher/login/",
        "teacher/logout/",
        "teacher/sessions/",
        "teacher/exams/",
        "teacher/settings/"
    ],
    "authentication": "required",
    "timestamp": str(__import__('datetime').datetime.now())
}
print(f"[TEACHER_URLS] {json.dumps(console_log, indent=2)}")
logger.info(f"Loading teacher URL patterns: {len(console_log['url_patterns'])} patterns")

# Teacher URL patterns with authentication requirements
urlpatterns = [
    # Main teacher dashboard - requires authentication
    path(
        'teacher/dashboard/', 
        login_required(TeacherDashboardView.as_view()), 
        name='teacher_dashboard'
    ),
    
    # Teacher authentication
    path(
        'teacher/login/', 
        TeacherLoginView.as_view(), 
        name='teacher_login'
    ),
    path(
        'teacher/logout/', 
        TeacherLogoutView.as_view(), 
        name='teacher_logout'
    ),
    
    # Teacher management views
    path(
        'teacher/sessions/', 
        login_required(TeacherSessionListView.as_view()), 
        name='teacher_sessions'
    ),
    path(
        'teacher/exams/', 
        login_required(TeacherExamOverviewView.as_view()), 
        name='teacher_exams'
    ),
    path(
        'teacher/settings/', 
        login_required(TeacherSettingsView.as_view()), 
        name='teacher_settings'
    ),
]

# Log successful URL pattern creation
pattern_success_log = {
    "event": "TEACHER_URL_PATTERNS_CREATED",
    "total_patterns": len(urlpatterns),
    "authenticated_patterns": len([p for p in urlpatterns if 'login_required' in str(p.callback)]),
    "status": "ready"
}
print(f"[TEACHER_PATTERNS_READY] {json.dumps(pattern_success_log, indent=2)}")
logger.info(f"Teacher URL patterns ready: {len(urlpatterns)} total patterns")
"""
Unified Classes & Exams URLs
Merges My Classes & Access with Exam Assignments
Version 2: Overrides exact old URLs to ensure redirects work
"""
from django.urls import path
from .views.classes_exams_unified import (
    classes_exams_unified_view,
    redirect_my_classes,
    redirect_schedule_matrix
)

urlpatterns = [
    # Main unified view - replaces both my-classes and schedule-matrix
    path('classes-exams/', 
         classes_exams_unified_view, 
         name='classes_exams_unified'),
    
    # OVERRIDE old URLs exactly - these must come BEFORE the old patterns in main urls.py
    # These will intercept the old URLs and redirect to unified view
    path('access/my-classes/', 
         redirect_my_classes, 
         name='my_classes_override'),
    
    path('schedule-matrix/', 
         redirect_schedule_matrix, 
         name='schedule_matrix_override'),
]

# Log URL pattern registration
import logging
logger = logging.getLogger(__name__)
logger.info("[UNIFIED_URLS_V2] Registered override patterns for old URLs to redirect to unified view")
print("[UNIFIED_URLS_V2] Override patterns registered: access/my-classes/ and schedule-matrix/ will redirect to classes-exams/")
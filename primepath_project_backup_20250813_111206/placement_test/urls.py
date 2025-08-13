"""
Placement Test URLs

This file maintains 100% backward compatibility.
All existing URL patterns are preserved and continue to work exactly as before.

The URLs have been organized into logical modules:
- student_urls.py: Student test-taking workflow URLs
- exam_urls.py: Exam management URLs  
- session_urls.py: Session management URLs
- api_urls.py: AJAX endpoint URLs

All URL patterns are imported here to maintain compatibility.
"""
from django.urls import path
from .student_urls import urlpatterns as student_patterns
from .exam_urls import urlpatterns as exam_patterns
from .session_urls import urlpatterns as session_patterns
from .api_urls import urlpatterns as api_patterns

app_name = 'placement_test'

# Combine all URL patterns from modular files
urlpatterns = []
urlpatterns.extend(student_patterns)
urlpatterns.extend(exam_patterns)
urlpatterns.extend(session_patterns)
urlpatterns.extend(api_patterns)
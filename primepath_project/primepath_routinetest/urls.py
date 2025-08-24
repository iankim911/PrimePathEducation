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
from .legacy_urls import urlpatterns as legacy_patterns  # Legacy URL patterns for backward compatibility
# Roster management removed - not needed for Answer Keys functionality
from .access_urls import urlpatterns as access_patterns  # Teacher class access management
# Matrix URLs removed - visual component eliminated
from .curriculum_urls import urlpatterns as curriculum_patterns  # Admin curriculum mapping
from .unified_urls import urlpatterns as unified_patterns  # NEW: Unified Classes & Exams
from .assessment_urls import urlpatterns as assessment_patterns  # NEW: Teacher Assessment Module (Admin Only)
from .auth_urls import urlpatterns as auth_patterns  # BUILDER: Day 1 - Authentication
from .class_code_urls import urlpatterns as class_code_patterns  # Class Code Management
from .class_urls import urlpatterns as class_patterns  # BUILDER: Day 2 - Class Management
from .exam_management_urls import urlpatterns as exam_mgmt_patterns  # BUILDER: Day 4 - Exam Management
from .student_management_urls import urlpatterns as student_mgmt_patterns  # Phase 2 - Student Management
from .views import index

app_name = 'RoutineTest'

# Add index/landing page
index_patterns = [
    path('', index.index, name='index'),  # Main landing page at /RoutineTest/
]

# Combine all URL patterns from modular files
urlpatterns = []
urlpatterns.extend(index_patterns)  # Index must come first
urlpatterns.extend(auth_patterns)  # BUILDER: Authentication routes (Day 1)
urlpatterns.extend(class_patterns)  # BUILDER: Class Management (Day 2)
urlpatterns.extend(exam_mgmt_patterns)  # BUILDER: Exam Management (Day 4)
urlpatterns.extend(student_mgmt_patterns)  # Phase 2: Student Management
urlpatterns.extend(unified_patterns)  # NEW: Unified Classes & Exams (should come early for priority)
urlpatterns.extend(student_patterns)
urlpatterns.extend(exam_patterns)
urlpatterns.extend(session_patterns)
urlpatterns.extend(api_patterns)
# Roster patterns removed - not needed for Answer Keys functionality
urlpatterns.extend(access_patterns)  # Teacher class access management URLs (kept for backward compatibility)
# Matrix patterns removed - visual component eliminated
urlpatterns.extend(curriculum_patterns)  # Admin curriculum mapping URLs
urlpatterns.extend(class_code_patterns)  # Class Code Management URLs
urlpatterns.extend(assessment_patterns)  # Teacher Assessment Module URLs (Admin Only)
urlpatterns.extend(legacy_patterns)  # Legacy URL patterns added last for backward compatibility

# Console logging for debugging URL resolution
import json
url_debug_info = {
    "module": "RoutineTest URLs",
    "total_patterns": len(urlpatterns),
    "pattern_sources": {
        "index": len(index_patterns),
        "unified": len(unified_patterns),
        "student": len(student_patterns),
        "exam": len(exam_patterns),
        "session": len(session_patterns),
        "api": len(api_patterns),
        "access": len(access_patterns),
        "curriculum": len(curriculum_patterns),
        "assessment": len(assessment_patterns),
        "legacy": len(legacy_patterns)
    },
    "legacy_urls_included": True,
    "create_exam_patterns": [
        str(p.pattern) for p in urlpatterns 
        if hasattr(p, 'pattern') and 'create' in str(p.pattern)
    ][:5]  # Show first 5 create patterns
}
print(f"[ROUTINETEST_URLS_LOADED] {json.dumps(url_debug_info, indent=2)}")
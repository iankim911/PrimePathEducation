"""
Student Test-Taking URLs
URLs for student test workflow and test session management
Enhanced with comprehensive URL aliases for backward compatibility
"""
from django.urls import path
from .views import student as views
import json
import logging

logger = logging.getLogger(__name__)

# Console logging for debugging
def log_student_urls_init():
    """Log URL initialization for debugging"""
    console_log = {
        "module": "student_urls",
        "action": "initialized",
        "message": "Student URLs configured with comprehensive aliases",
        "aliases_added": [
            "submit-answer variants",
            "sessions (plural) variants",
            "backward compatibility patterns"
        ]
    }
    print(f"[STUDENT_URLS_INIT] {json.dumps(console_log, indent=2)}")

urlpatterns = [
    # Student test workflow
    path('start/', views.start_test, name='start_test'),
    path('session/<uuid:session_id>/', views.take_test, name='take_test'),
    
    # === ANSWER SUBMISSION ENDPOINTS WITH COMPREHENSIVE ALIASES ===
    # Primary pattern
    path('session/<uuid:session_id>/submit/', views.submit_answer, name='submit_answer'),
    
    # Alias 1: Hyphenated version (common in frontend)
    path('session/<uuid:session_id>/submit-answer/', views.submit_answer, name='submit_answer_hyphen'),
    
    # Alias 2: Plural 'sessions' with submit
    path('sessions/<uuid:session_id>/submit/', views.submit_answer, name='submit_answer_plural'),
    
    # Alias 3: Plural 'sessions' with submit-answer (covers test cases)
    path('sessions/<uuid:session_id>/submit-answer/', views.submit_answer, name='submit_answer_plural_hyphen'),
    
    # Alias 4: Alternative patterns for maximum compatibility
    path('session/<uuid:session_id>/save-answer/', views.submit_answer, name='save_answer'),
    path('sessions/<uuid:session_id>/save-answer/', views.submit_answer, name='save_answer_plural'),
    
    # === OTHER STUDENT WORKFLOW ENDPOINTS ===
    path('session/<uuid:session_id>/adjust-difficulty/', views.adjust_difficulty, name='adjust_difficulty'),
    path('session/<uuid:session_id>/manual-adjust/', views.manual_adjust_difficulty, name='manual_adjust_difficulty'),
    path('session/<uuid:session_id>/complete/', views.complete_test, name='complete_test'),
    path('session/<uuid:session_id>/post-submit-difficulty/', views.post_submit_difficulty_choice, name='post_submit_difficulty_choice'),
    path('session/<uuid:session_id>/result/', views.test_result, name='test_result'),
    path('request-difficulty-change/', views.request_difficulty_change, name='request_difficulty_change'),
    
    # === ADDITIONAL COMPATIBILITY ALIASES ===
    # Support plural forms for other endpoints too
    path('sessions/<uuid:session_id>/', views.take_test, name='take_test_plural'),
    path('sessions/<uuid:session_id>/complete/', views.complete_test, name='complete_test_plural'),
    path('sessions/<uuid:session_id>/result/', views.test_result, name='test_result_plural'),
]

# Initialize and log
log_student_urls_init()

# Log pattern count for verification
URL_COUNT = len(urlpatterns)
logger.info(f"Student URLs: {URL_COUNT} patterns registered")

# Development mode detailed logging
import sys
if 'runserver' in sys.argv or 'test' in sys.argv:
    submit_patterns = [p for p in urlpatterns if 'submit' in str(p.pattern) or 'save' in str(p.pattern)]
    console_log = {
        "module": "student_urls",
        "total_patterns": URL_COUNT,
        "submit_patterns": len(submit_patterns),
        "submit_urls": [
            "/api/placement/session/{id}/submit/",
            "/api/placement/session/{id}/submit-answer/",
            "/api/placement/sessions/{id}/submit/",
            "/api/placement/sessions/{id}/submit-answer/",
            "/api/placement/session/{id}/save-answer/",
            "/api/placement/sessions/{id}/save-answer/"
        ]
    }
    print(f"[STUDENT_URL_PATTERNS] {json.dumps(console_log, indent=2)}")
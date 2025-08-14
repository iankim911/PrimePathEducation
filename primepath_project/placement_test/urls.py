"""
Placement Test URLs - Enhanced with Comprehensive Integration

This file maintains 100% backward compatibility while adding robust logging.
All existing URL patterns are preserved and continue to work exactly as before.

The URLs have been organized into logical modules:
- student_urls.py: Student test-taking workflow URLs
- exam_urls.py: Exam management URLs  
- session_urls.py: Session management URLs
- api_urls.py: AJAX endpoint URLs
- legacy_urls.py: Legacy patterns for backward compatibility (includes index page)

All URL patterns are imported here with conflict detection and comprehensive logging.
"""
import json
import logging
from django.urls import path
from .student_urls import urlpatterns as student_patterns
from .exam_urls import urlpatterns as exam_patterns
from .session_urls import urlpatterns as session_patterns
from .api_urls import urlpatterns as api_patterns
from .legacy_urls import urlpatterns as legacy_patterns
from .url_integration import integrate_url_patterns, URLIntegrationLogger

# Initialize logger
logger = logging.getLogger('placement_test.urls')

# App namespace
app_name = 'PlacementTest'

# Console logging for URL configuration
console_log = {
    "event": "PLACEMENT_TEST_URLS_INIT",
    "app_name": app_name,
    "modules_loading": [
        "student_urls",
        "exam_urls",
        "session_urls",
        "api_urls",
        "legacy_urls"
    ],
    "timestamp": str(__import__('datetime').datetime.now())
}
print(f"[PLACEMENT_TEST_URLS] {json.dumps(console_log, indent=2)}")

# Log pattern counts before integration
pattern_counts = {
    "student": len(student_patterns),
    "exam": len(exam_patterns),
    "session": len(session_patterns),
    "api": len(api_patterns),
    "legacy": len(legacy_patterns)
}

print(f"[PATTERN_COUNTS] {json.dumps(pattern_counts, indent=2)}")
logger.info(f"Loading URL patterns: {pattern_counts}")

# Use integration module to combine patterns with conflict detection
try:
    # Start with empty list
    urlpatterns = []
    
    # Define the order of pattern integration
    # Legacy patterns go LAST to avoid conflicts with more specific patterns
    pattern_sources = {
        "student": student_patterns,
        "exam": exam_patterns,
        "session": session_patterns,
        "api": api_patterns,
        "legacy": legacy_patterns  # Includes index page
    }
    
    # Integrate all patterns with logging and conflict detection
    urlpatterns = integrate_url_patterns([], pattern_sources)
    
    # Log successful integration
    success_log = {
        "event": "URL_INTEGRATION_SUCCESS",
        "total_patterns": len(urlpatterns),
        "app_name": app_name,
        "index_page": "enabled",
        "status": "ready"
    }
    print(f"[PLACEMENT_TEST_READY] {json.dumps(success_log, indent=2)}")
    logger.info(f"PlacementTest URLs ready with {len(urlpatterns)} patterns")
    
except Exception as e:
    # Log any errors during integration
    error_log = {
        "event": "URL_INTEGRATION_ERROR",
        "error": str(e),
        "fallback": "Using basic pattern extension"
    }
    print(f"[URL_ERROR] {json.dumps(error_log, indent=2)}")
    logger.error(f"Error during URL integration: {e}")
    
    # Fallback to simple extension if integration fails
    urlpatterns = []
    urlpatterns.extend(student_patterns)
    urlpatterns.extend(exam_patterns)
    urlpatterns.extend(session_patterns)
    urlpatterns.extend(api_patterns)
    urlpatterns.extend(legacy_patterns)  # Still include legacy for index page
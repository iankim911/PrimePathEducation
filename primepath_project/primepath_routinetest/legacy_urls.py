"""
Legacy URL patterns for backward compatibility
Provides aliases for old URL patterns to prevent 404 errors
Enhanced with comprehensive redirect views for smooth migration
"""
from django.urls import path
from django.views.generic import RedirectView
from django.shortcuts import redirect
from .views import student as student_views
from .views import exam as exam_views
import json
import logging

logger = logging.getLogger(__name__)

def log_redirect(from_url, to_url, request):
    """Helper to log redirects for debugging"""
    console_log = {
        "redirect": "legacy_url",
        "from": from_url,
        "to": to_url,
        "method": request.method,
        "user": str(request.user) if request.user.is_authenticated else "anonymous"
    }
    print(f"[LEGACY_URL_REDIRECT] {json.dumps(console_log)}")
    logger.info("Legacy redirect: %s -> %s", from_url, to_url)

# Custom redirect views with logging
class LoggingRedirectView(RedirectView):
    """RedirectView with console logging for debugging"""
    permanent = False  # Use 302 for now, can change to 301 later
    
    def get(self, request, *args, **kwargs):
        log_redirect(request.path, self.get_redirect_url(*args, **kwargs), request)
        return super().get(request, *args, **kwargs)

# Legacy URL patterns - these map old URLs to existing views
legacy_patterns = [
    # Direct view mappings (these work without redirect)
    path('test/<uuid:session_id>/', student_views.take_test, name='take_test_legacy'),
    
    # Redirect-based mappings for expected URLs
    # These handle the URLs that QA tests expect
    path('', LoggingRedirectView.as_view(url='/'), name='placement_home_redirect'),
    path('start-test/', LoggingRedirectView.as_view(pattern_name='RoutineTest:start_test'), name='start_test_redirect'),
    path('create-exam/', exam_views.create_exam, name='create_exam_legacy'),  # Direct mapping
    path('exam-list/', LoggingRedirectView.as_view(pattern_name='RoutineTest:exam_list'), name='exam_list_redirect'),
    
    # Session management redirects
    path('sessions/', LoggingRedirectView.as_view(url='/api/RoutineTest/sessions/'), name='sessions_redirect'),
    path('session/<uuid:session_id>/', LoggingRedirectView.as_view(url='/api/RoutineTest/session/%(session_id)s/'), name='session_detail_redirect'),
    path('session/<uuid:session_id>/submit/', LoggingRedirectView.as_view(url='/api/RoutineTest/session/%(session_id)s/submit/'), name='session_submit_redirect'),
    path('session/<uuid:session_id>/result/', student_views.test_result, name='test_result_legacy'),
    
    # Exam management redirects
    path('exams/', LoggingRedirectView.as_view(url='/api/RoutineTest/exams/'), name='exams_redirect'),
    path('exam/<uuid:exam_id>/', LoggingRedirectView.as_view(url='/api/RoutineTest/exams/%(exam_id)s/'), name='exam_detail_redirect'),
    path('exam/<uuid:exam_id>/edit/', LoggingRedirectView.as_view(url='/api/RoutineTest/exams/%(exam_id)s/edit/'), name='exam_edit_redirect'),
]

# Export for inclusion in main URL config
urlpatterns = legacy_patterns

# Log initialization
console_log = {
    "module": "legacy_urls",
    "action": "initialized",
    "patterns_count": len(urlpatterns),
    "patterns": [p.name for p in urlpatterns if hasattr(p, 'name')]
}
print(f"[LEGACY_URLS_INIT] {json.dumps(console_log, indent=2)}")
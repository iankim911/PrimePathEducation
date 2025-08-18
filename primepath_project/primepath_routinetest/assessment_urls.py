"""
Teacher Assessment Module URLs - Admin Only
Part of RoutineTest module

Provides URL patterns for:
- Teacher assessment dashboard (main view)
- Request approval/denial endpoints
- Direct assignment endpoints
- Bulk operations
- Revocation endpoints

Created: August 18, 2025
"""
from django.urls import path
from .views import teacher_assessment

# NO app_name here - follows existing RoutineTest pattern
# These URLs will be accessed as 'RoutineTest:xxx' not 'assessment:xxx'

urlpatterns = [
    # Main assessment dashboard - Admin only
    path('assessment/dashboard/', 
         teacher_assessment.teacher_assessment_view, 
         name='teacher_assessment'),
    
    # Request management
    path('assessment/approve/<uuid:request_id>/', 
         teacher_assessment.approve_teacher_request, 
         name='approve_teacher_request'),
    
    path('assessment/deny/<uuid:request_id>/', 
         teacher_assessment.deny_teacher_request, 
         name='deny_teacher_request'),
    
    # Direct assignment management
    path('assessment/direct-assign/', 
         teacher_assessment.direct_assign_teacher, 
         name='direct_assign_teacher'),
    
    path('assessment/revoke/', 
         teacher_assessment.revoke_teacher_access, 
         name='revoke_teacher_access'),
    
    # Bulk operations
    path('assessment/bulk-approve/', 
         teacher_assessment.bulk_approve_requests, 
         name='bulk_approve_requests'),
]

# Console logging for URL registration
import logging
import json

logger = logging.getLogger(__name__)

console_log = {
    "module": "assessment_urls",
    "action": "url_patterns_registered", 
    "pattern_count": len(urlpatterns),
    "patterns": [str(pattern.pattern) for pattern in urlpatterns],
    "note": "Teacher Assessment Module - Admin Only URLs"
}

logger.info(f"[ASSESSMENT_URLS] {json.dumps(console_log)}")
print(f"[ASSESSMENT_URLS] {json.dumps(console_log)}")
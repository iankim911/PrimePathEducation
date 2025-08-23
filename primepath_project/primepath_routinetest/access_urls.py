"""
Teacher Class Access Management URLs
Part of RoutineTest module

Provides URL patterns for:
- Teacher class access view (My Classes & Access tab)
- Request submission endpoints
- Admin approval endpoints
- AJAX endpoints for real-time updates

NOTE: Following RoutineTest URL pattern - no app_name, direct urlpatterns export
This matches roster_urls.py, exam_urls.py pattern for consistency
"""
from django.urls import path
from .views import class_access

# NO app_name here - follows existing RoutineTest pattern
# These URLs will be accessed as 'RoutineTest:xxx' not 'class_access:xxx'

urlpatterns = [
    # Main teacher view - single tab with split view
    path('access/my-classes/', 
         class_access.my_classes_view, 
         name='my_classes'),
    
    # Request management
    path('access/request-access/', 
         class_access.request_access, 
         name='request_access'),
    
    path('access/request/<uuid:request_id>/withdraw/', 
         class_access.withdraw_request, 
         name='withdraw_request'),
    
    # Admin approval endpoints
    path('access/admin/pending-requests/', 
         class_access.admin_pending_requests, 
         name='admin_pending_requests'),
    
    path('access/admin/request/<uuid:request_id>/approve/', 
         class_access.approve_request, 
         name='approve_request'),
    
    path('access/admin/request/<uuid:request_id>/deny/', 
         class_access.deny_request, 
         name='deny_request'),
    
    path('access/admin/bulk-approve/', 
         class_access.bulk_approve_requests, 
         name='bulk_approve'),
    
    # AJAX endpoints for dynamic updates
    path('access/api/my-classes/', 
         class_access.api_my_classes, 
         name='api_my_classes'),
    
    path('access/api/available-classes/', 
         class_access.api_available_classes, 
         name='api_available_classes'),
    
    path('access/api/my-requests/', 
         class_access.api_my_requests, 
         name='api_my_requests'),
    
    path('access/api/class/<str:class_code>/current-teachers/', 
         class_access.api_class_current_teachers, 
         name='api_class_teachers'),
    
    # Admin management - Legacy endpoints (kept for compatibility)
    path('access/admin/teacher-assignments/', 
         class_access.admin_teacher_assignments, 
         name='admin_teacher_assignments'),
    
    path('access/admin/direct-assign/', 
         class_access.admin_direct_assign, 
         name='admin_direct_assign'),
    
    path('access/admin/revoke-access/', 
         class_access.admin_revoke_access, 
         name='admin_revoke_access'),
    
    # NEW: Comprehensive Teacher Management Dashboard
    path('access/admin/teacher-management/', 
         lambda request: __import__('primepath_routinetest.views.admin_teacher_management', fromlist=['teacher_access_management_dashboard']).teacher_access_management_dashboard(request), 
         name='admin_teacher_management_dashboard'),
    
    path('access/admin/direct-assign-teacher/', 
         lambda request: __import__('primepath_routinetest.views.admin_teacher_management', fromlist=['admin_direct_assign_teacher']).admin_direct_assign_teacher(request), 
         name='admin_direct_assign_teacher'),
    
    path('access/admin/revoke-teacher-access/', 
         lambda request: __import__('primepath_routinetest.views.admin_teacher_management', fromlist=['admin_revoke_teacher_access']).admin_revoke_teacher_access(request), 
         name='admin_revoke_teacher_access'),
    
    path('access/admin/bulk-assign-teachers/', 
         lambda request: __import__('primepath_routinetest.views.admin_teacher_management', fromlist=['admin_bulk_assign_teachers']).admin_bulk_assign_teachers(request), 
         name='admin_bulk_assign_teachers'),
    
    # API endpoints for admin dashboard
    path('access/api/teacher-class-matrix/', 
         lambda request: __import__('primepath_routinetest.views.admin_teacher_management', fromlist=['api_teacher_class_matrix']).api_teacher_class_matrix(request), 
         name='api_teacher_class_matrix'),
    
    path('access/api/class/<str:class_code>/teacher-summary/', 
         lambda request, class_code: __import__('primepath_routinetest.views.admin_teacher_management', fromlist=['api_class_teacher_summary']).api_class_teacher_summary(request, class_code), 
         name='api_class_teacher_summary'),
]

# Console logging for URL registration
import logging
import json

logger = logging.getLogger(__name__)

console_log = {
    "module": "access_urls",
    "action": "url_patterns_registered", 
    "pattern_count": len(urlpatterns),
    "patterns": [str(pattern.pattern) for pattern in urlpatterns],
    "note": "Following RoutineTest pattern - no separate namespace, uses RoutineTest: prefix"
}

logger.info(f"[ACCESS_URLS_FIXED] {json.dumps(console_log)}")
print(f"[ACCESS_URLS_FIXED] {json.dumps(console_log)}")
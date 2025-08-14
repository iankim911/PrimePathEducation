"""
Custom Permission Classes for PrimePath
Provides granular control over API access with comprehensive logging
"""

from rest_framework import permissions
import json
import logging

logger = logging.getLogger(__name__)

class SmartAPIPermission(permissions.BasePermission):
    """
    Intelligent permission class that:
    - Allows anonymous access to student test endpoints
    - Requires authentication for admin/teacher endpoints
    - Logs all permission checks for debugging
    """
    
    # Define anonymous-allowed endpoints
    ANONYMOUS_ALLOWED_PATTERNS = [
        '/api/PlacementTest/start/',  # Students can start tests
        '/api/PlacementTest/session/',  # Students can access their sessions
        '/api/PlacementTest/sessions/<uuid:session_id>/',  # Specific session access
        '/api/v1/PlacementTest/start/',  # v1 compatibility
        '/api/v2/PlacementTest/session/',  # v2 compatibility
    ]
    
    # Define read-only patterns (GET allowed for all)
    READ_ONLY_PATTERNS = [
        '/api/PlacementTest/exams/',  # Can view exam list
        '/api/exams/',  # Legacy exam list
    ]
    
    # Define admin-only patterns
    ADMIN_ONLY_PATTERNS = [
        '/api/PlacementTest/exams/create/',
        '/api/PlacementTest/exams/<uuid:exam_id>/edit/',
        '/api/PlacementTest/exams/<uuid:exam_id>/delete/',
        '/api/PlacementTest/exams/<uuid:exam_id>/update',
        '/api/PlacementTest/questions/',
        '/api/placement-rules/',
    ]
    
    def has_permission(self, request, view):
        """
        Check if request should be permitted
        """
        path = request.path
        method = request.method
        user = request.user
        
        # Console logging for debugging
        console_log = {
            "permission_check": "SmartAPIPermission",
            "path": path,
            "method": method,
            "user": str(user) if user.is_authenticated else "anonymous",
            "authenticated": user.is_authenticated
        }
        
        # Check anonymous allowed patterns
        for pattern in self.ANONYMOUS_ALLOWED_PATTERNS:
            if self._path_matches_pattern(path, pattern):
                console_log["result"] = "allowed"
                console_log["reason"] = "anonymous_allowed_pattern"
                print(f"[PERMISSION] {json.dumps(console_log)}")
                return True
        
        # Check read-only patterns
        if method in permissions.SAFE_METHODS:
            for pattern in self.READ_ONLY_PATTERNS:
                if self._path_matches_pattern(path, pattern):
                    console_log["result"] = "allowed"
                    console_log["reason"] = "read_only_pattern"
                    print(f"[PERMISSION] {json.dumps(console_log)}")
                    return True
        
        # Check admin-only patterns
        for pattern in self.ADMIN_ONLY_PATTERNS:
            if self._path_matches_pattern(path, pattern):
                if user.is_authenticated and (user.is_staff or hasattr(user, 'teacher')):
                    console_log["result"] = "allowed"
                    console_log["reason"] = "admin_pattern_authenticated"
                    print(f"[PERMISSION] {json.dumps(console_log)}")
                    return True
                else:
                    console_log["result"] = "denied"
                    console_log["reason"] = "admin_pattern_not_authenticated"
                    print(f"[PERMISSION_DENIED] {json.dumps(console_log)}")
                    return False
        
        # Default: require authentication for write operations
        if method not in permissions.SAFE_METHODS:
            if not user.is_authenticated:
                console_log["result"] = "denied"
                console_log["reason"] = "write_operation_not_authenticated"
                print(f"[PERMISSION_DENIED] {json.dumps(console_log)}")
                return False
        
        # Allow authenticated users for other endpoints
        if user.is_authenticated:
            console_log["result"] = "allowed"
            console_log["reason"] = "authenticated_user"
            print(f"[PERMISSION] {json.dumps(console_log)}")
            return True
        
        # Allow read-only for non-authenticated users by default
        if method in permissions.SAFE_METHODS:
            console_log["result"] = "allowed"
            console_log["reason"] = "read_only_default"
            print(f"[PERMISSION] {json.dumps(console_log)}")
            return True
        
        console_log["result"] = "denied"
        console_log["reason"] = "default_deny"
        print(f"[PERMISSION_DENIED] {json.dumps(console_log)}")
        return False
    
    def _path_matches_pattern(self, path, pattern):
        """
        Check if a path matches a pattern (supporting UUID placeholders)
        """
        import re
        
        # Convert pattern to regex
        # Replace <uuid:name> with UUID regex
        regex_pattern = pattern.replace('<uuid:', '(?P<')
        regex_pattern = regex_pattern.replace('>', '>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})')
        regex_pattern = f"^{regex_pattern}$"
        
        return bool(re.match(regex_pattern, path))


class StudentTestPermission(permissions.BasePermission):
    """
    Special permission class for student test taking
    Allows anonymous users to take tests but tracks their session
    """
    
    def has_permission(self, request, view):
        """
        Allow all users to access student test views
        """
        console_log = {
            "permission_check": "StudentTestPermission",
            "path": request.path,
            "method": request.method,
            "session_key": request.session.session_key if hasattr(request.session, 'session_key') else None,
            "result": "allowed",
            "reason": "student_test_always_allowed"
        }
        print(f"[STUDENT_PERMISSION] {json.dumps(console_log)}")
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Ensure students can only access their own test sessions
        """
        # Check if this is a StudentSession object
        if hasattr(obj, 'session_key'):
            # Compare session keys
            if request.session.session_key == obj.session_key:
                return True
        
        # Check if user owns the session (for authenticated users)
        if request.user.is_authenticated:
            if hasattr(obj, 'student_email') and obj.student_email == request.user.email:
                return True
        
        # Allow staff to access any session
        if request.user.is_authenticated and request.user.is_staff:
            return True
        
        console_log = {
            "permission_check": "StudentTestPermission",
            "action": "object_permission_denied",
            "object_id": str(obj.id) if hasattr(obj, 'id') else None,
            "user": str(request.user) if request.user.is_authenticated else "anonymous"
        }
        print(f"[STUDENT_PERMISSION_DENIED] {json.dumps(console_log)}")
        
        return False


class TeacherPermission(permissions.BasePermission):
    """
    Permission class for teacher-specific operations
    """
    
    def has_permission(self, request, view):
        """
        Only teachers can access teacher views
        """
        if not request.user.is_authenticated:
            console_log = {
                "permission_check": "TeacherPermission",
                "result": "denied",
                "reason": "not_authenticated"
            }
            print(f"[TEACHER_PERMISSION_DENIED] {json.dumps(console_log)}")
            return False
        
        # Check if user is a teacher or staff
        if request.user.is_staff or hasattr(request.user, 'teacher'):
            console_log = {
                "permission_check": "TeacherPermission",
                "result": "allowed",
                "user": str(request.user),
                "is_staff": request.user.is_staff,
                "is_teacher": hasattr(request.user, 'teacher')
            }
            print(f"[TEACHER_PERMISSION] {json.dumps(console_log)}")
            return True
        
        console_log = {
            "permission_check": "TeacherPermission",
            "result": "denied",
            "reason": "not_teacher",
            "user": str(request.user)
        }
        print(f"[TEACHER_PERMISSION_DENIED] {json.dumps(console_log)}")
        return False
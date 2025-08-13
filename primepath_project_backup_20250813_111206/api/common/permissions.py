"""
API Permissions - Phase 8
Custom permission classes for API endpoints
"""
from rest_framework import permissions


class IsTeacherOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow teachers to edit.
    Students and anonymous users get read-only access.
    """
    
    def has_permission(self, request, view):
        # Read permissions for all
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for authenticated teachers
        return request.user and request.user.is_staff


class IsOwnerOrTeacher(permissions.BasePermission):
    """
    Custom permission to only allow owners or teachers to edit.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for all
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Teachers can edit anything
        if request.user and request.user.is_staff:
            return True
        
        # Check if user owns the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'student_name'):
            # For StudentSession, check session ID
            session_id = request.session.get('session_id')
            return str(obj.id) == session_id
        
        return False


class IsSessionOwner(permissions.BasePermission):
    """
    Permission to only allow session owners to access their data.
    """
    
    def has_object_permission(self, request, view, obj):
        # Teachers can access all sessions
        if request.user and request.user.is_staff:
            return True
        
        # Check if session ID matches
        session_id = request.session.get('session_id')
        return str(obj.id) == session_id
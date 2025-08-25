"""
Decorators for RoutineTest system security
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)


def teacher_required(view_func):
    """
    Decorator to ensure only teachers can access a view.
    Blocks students and unauthorized users.
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access this page.")
            return redirect('core:index')
        
        # Check if user is a student
        if hasattr(request.user, 'primepath_student_profile'):
            logger.warning(
                f"SECURITY: Student {request.user.username} blocked from accessing {view_func.__name__}"
            )
            messages.error(
                request, 
                "Students cannot access this page. Please use the student portal."
            )
            return redirect('primepath_student:dashboard')
        
        # Check if user is a teacher or admin
        is_authorized = (
            request.user.is_superuser or 
            request.user.is_staff or
            hasattr(request.user, 'teacher_profile')
        )
        
        if not is_authorized:
            logger.warning(
                f"SECURITY: Unauthorized user {request.user.username} blocked from {view_func.__name__}"
            )
            raise PermissionDenied("You do not have permission to access this page.")
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view


def admin_or_head_teacher_required(view_func):
    """
    Decorator to ensure only admins or head teachers can access a view.
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access this page.")
            return redirect('core:index')
        
        # Block students immediately
        if hasattr(request.user, 'primepath_student_profile'):
            logger.warning(
                f"SECURITY: Student {request.user.username} blocked from admin area"
            )
            messages.error(request, "Students cannot access administrative functions.")
            return redirect('primepath_student:dashboard')
        
        # Check for admin/head teacher status
        is_admin = request.user.is_superuser or request.user.is_staff
        is_head_teacher = False
        
        if hasattr(request.user, 'teacher_profile'):
            is_head_teacher = request.user.teacher_profile.is_head_teacher
        
        if not (is_admin or is_head_teacher):
            logger.warning(
                f"SECURITY: Non-admin user {request.user.username} blocked from admin function"
            )
            raise PermissionDenied("Administrative access required.")
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view
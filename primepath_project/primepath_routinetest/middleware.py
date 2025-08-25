"""
Middleware to protect teacher system from unauthorized access
"""
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


class TeacherSystemProtectionMiddleware:
    """
    Middleware to ensure only teachers can access the RoutineTest system.
    Students should be blocked from accessing teacher areas.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Check if this is a RoutineTest URL
        if request.path.startswith('/RoutineTest/'):
            # Skip check for logout URL
            if '/logout/' in request.path:
                return self.get_response(request)
                
            # Check if user is authenticated
            if request.user.is_authenticated:
                # Check if user has a student profile (which means they're a student)
                if hasattr(request.user, 'primepath_student_profile'):
                    # This is a student trying to access teacher system!
                    logger.warning(
                        f"SECURITY: Student {request.user.username} (ID: {request.user.primepath_student_profile.student_id}) "
                        f"attempted to access teacher system at {request.path}"
                    )
                    
                    messages.error(
                        request, 
                        "Students cannot access the teacher system. Please use the student portal instead."
                    )
                    
                    # Redirect to student dashboard
                    return redirect('primepath_student:dashboard')
                
                # Check if user has teacher profile or is admin
                is_teacher = (
                    request.user.is_superuser or 
                    request.user.is_staff or
                    hasattr(request.user, 'teacher_profile')
                )
                
                if not is_teacher:
                    # User is neither student nor teacher - suspicious
                    logger.warning(
                        f"SECURITY: Non-teacher user {request.user.username} "
                        f"attempted to access teacher system at {request.path}"
                    )
                    
                    messages.error(
                        request, 
                        "You do not have permission to access the teacher system."
                    )
                    
                    # Redirect to main index
                    return redirect('core:index')
        
        # Process the request normally
        response = self.get_response(request)
        return response
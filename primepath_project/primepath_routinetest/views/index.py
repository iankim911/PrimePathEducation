"""
Index view for PrimePath Routine Test app
Provides a landing page for the routine test module
"""
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from ..models import Exam, StudentSession
from ..error_handlers import handle_view_errors
import logging

logger = logging.getLogger('primepath_routinetest.index')


@handle_view_errors
@require_http_methods(["GET"])
def index(request):
    """
    Main landing page for the routine test app.
    Provides options to start a test or manage exams.
    """
    context = {
        'active_exams': Exam.objects.filter(is_active=True).count(),
        'total_sessions': StudentSession.objects.count(),
        'recent_sessions': StudentSession.objects.filter(
            completed_at__isnull=False
        ).order_by('-completed_at')[:5]
    }
    
    # Check if user is a teacher/staff
    if request.user.is_authenticated and (request.user.is_staff or 
                                          hasattr(request.user, 'groups') and 
                                          request.user.groups.filter(name='Teachers').exists()):
        context['is_teacher'] = True
        context['pending_sessions'] = StudentSession.objects.filter(
            completed_at__isnull=False,
            score__isnull=True
        ).count()
    
    return render(request, 'primepath_routinetest/index.html', context)


@handle_view_errors
@require_http_methods(["GET"])
def redirect_to_start(request):
    """
    Simple redirect to the start test page.
    Used as a convenience redirect.
    """
    return redirect('primepath_routinetest:start_test')
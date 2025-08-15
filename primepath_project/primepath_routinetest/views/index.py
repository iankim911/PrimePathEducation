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
    # Console logging for theme tracking
    logger.info("=" * 60)
    logger.info("[RoutineTest] Index page accessed")
    logger.info(f"[RoutineTest] User: {request.user if request.user.is_authenticated else 'Anonymous'}")
    logger.info("[RoutineTest] Theme: BCG Green (#00A65E)")
    logger.info("[RoutineTest] Module: RoutineTest v2.0")
    logger.info("=" * 60)
    
    context = {
        'active_exams': Exam.objects.filter(is_active=True).count(),
        'total_sessions': StudentSession.objects.count(),
        'recent_sessions': StudentSession.objects.filter(
            completed_at__isnull=False
        ).order_by('-completed_at')[:5],
        # Add theme debugging info
        'debug_info': {
            'module': 'RoutineTest',
            'theme': 'BCG Green',
            'version': '2.0.0',
            'primary_color': '#00A65E'
        }
    }
    
    # Log statistics
    logger.debug(f"[RoutineTest Stats] Active Exams: {context['active_exams']}")
    logger.debug(f"[RoutineTest Stats] Total Sessions: {context['total_sessions']}")
    logger.debug(f"[RoutineTest Stats] Recent Sessions: {len(context['recent_sessions'])}")
    
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
    return redirect('RoutineTest:start_test')
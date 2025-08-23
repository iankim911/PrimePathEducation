"""
Index view for PrimePath Routine Test app
Provides a landing page for the routine test module
"""
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from ..models import Exam, StudentSession
from ..error_handlers import handle_view_errors
import logging

logger = logging.getLogger('primepath_routinetest.index')


@login_required(login_url='/RoutineTest/login/')
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
    
    # Check if user is a teacher/staff - Enhanced detection
    context['is_teacher'] = False
    context['is_admin'] = False
    
    if request.user.is_authenticated:
        # Multiple ways to detect teacher status
        is_teacher_by_staff = request.user.is_staff
        is_teacher_by_group = (hasattr(request.user, 'groups') and 
                               request.user.groups.filter(name='Teachers').exists())
        is_teacher_by_profile = hasattr(request.user, 'teacher_profile')
        is_admin = request.user.is_superuser
        
        # Set teacher status if ANY condition is true
        if is_teacher_by_staff or is_teacher_by_group or is_teacher_by_profile:
            context['is_teacher'] = True
            context['pending_sessions'] = StudentSession.objects.filter(
                completed_at__isnull=False,
                score__isnull=True
            ).count()
            
        context['is_admin'] = is_admin
        
        # Debug logging
        logger.info(f"[Teacher Detection] User: {request.user.username}")
        logger.info(f"  - is_staff: {is_teacher_by_staff}")
        logger.info(f"  - has Teachers group: {is_teacher_by_group}")
        logger.info(f"  - has teacher_profile: {is_teacher_by_profile}")
        logger.info(f"  - is_superuser: {is_admin}")
        logger.info(f"  - Final is_teacher: {context['is_teacher']}")
    
    return render(request, 'primepath_routinetest/index.html', context)


@handle_view_errors
@require_http_methods(["GET"])
def redirect_to_start(request):
    """
    Simple redirect to the start test page.
    Used as a convenience redirect.
    """
    return redirect('RoutineTest:start_test')
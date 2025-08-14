"""
Index view for PrimePath Placement Test app
Provides a landing page for the placement test module
Enhanced with comprehensive logging for debugging
"""
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from ..models import Exam, StudentSession
import json
import logging
from datetime import datetime

logger = logging.getLogger('placement_test.index')


@require_http_methods(["GET"])
def index(request):
    """
    Main landing page for the placement test app.
    Provides options to start a test or manage exams.
    Enhanced with comprehensive logging.
    """
    # Log the request
    request_log = {
        "event": "PLACEMENT_INDEX_ACCESS",
        "path": request.path,
        "method": request.method,
        "user": str(request.user) if request.user.is_authenticated else "anonymous",
        "timestamp": str(datetime.now()),
        "user_agent": request.META.get('HTTP_USER_AGENT', '')[:100]
    }
    print(f"[PLACEMENT_INDEX] {json.dumps(request_log, indent=2)}")
    logger.info(f"PlacementTest index accessed by {request.user}")
    
    # Gather context data with error handling
    try:
        active_exams = Exam.objects.filter(is_active=True).count()
        total_sessions = StudentSession.objects.count()
        recent_sessions = StudentSession.objects.filter(
            completed_at__isnull=False
        ).order_by('-completed_at')[:5]
        
        context = {
            'active_exams': active_exams,
            'total_sessions': total_sessions,
            'recent_sessions': recent_sessions
        }
        
        # Log context data
        context_log = {
            "event": "INDEX_CONTEXT_PREPARED",
            "active_exams": active_exams,
            "total_sessions": total_sessions,
            "recent_sessions_count": len(recent_sessions)
        }
        print(f"[INDEX_CONTEXT] {json.dumps(context_log, indent=2)}")
        
    except Exception as e:
        # Log any errors
        error_log = {
            "event": "INDEX_CONTEXT_ERROR",
            "error": str(e),
            "error_type": type(e).__name__
        }
        print(f"[INDEX_ERROR] {json.dumps(error_log, indent=2)}")
        logger.error(f"Error preparing index context: {e}")
        
        # Provide fallback context
        context = {
            'active_exams': 0,
            'total_sessions': 0,
            'recent_sessions': []
        }
    
    # Check if user is a teacher/staff with logging
    if request.user.is_authenticated:
        is_staff = request.user.is_staff
        is_teacher = hasattr(request.user, 'groups') and request.user.groups.filter(name='Teachers').exists()
        
        if is_staff or is_teacher:
            context['is_teacher'] = True
            try:
                pending_sessions = StudentSession.objects.filter(
                    completed_at__isnull=False,
                    score__isnull=True
                ).count()
                context['pending_sessions'] = pending_sessions
                
                teacher_log = {
                    "event": "TEACHER_ACCESS",
                    "user": str(request.user),
                    "is_staff": is_staff,
                    "is_teacher": is_teacher,
                    "pending_sessions": pending_sessions
                }
                print(f"[TEACHER_INDEX] {json.dumps(teacher_log, indent=2)}")
                
            except Exception as e:
                logger.error(f"Error getting pending sessions: {e}")
                context['pending_sessions'] = 0
    
    # Log the render
    render_log = {
        "event": "INDEX_RENDER",
        "template": "placement_test/index.html",
        "context_keys": list(context.keys()),
        "user_type": "teacher" if context.get('is_teacher') else "student"
    }
    print(f"[INDEX_RENDER] {json.dumps(render_log, indent=2)}")
    
    return render(request, 'placement_test/index.html', context)


@require_http_methods(["GET"])
def redirect_to_start(request):
    """
    Simple redirect to the start test page.
    Used as a convenience redirect.
    Enhanced with logging.
    """
    redirect_log = {
        "event": "INDEX_REDIRECT_TO_START",
        "from": request.path,
        "to": "PlacementTest:start_test",
        "user": str(request.user) if request.user.is_authenticated else "anonymous"
    }
    print(f"[INDEX_REDIRECT] {json.dumps(redirect_log, indent=2)}")
    logger.info(f"Redirecting to start_test from index")
    
    return redirect('PlacementTest:start_test')
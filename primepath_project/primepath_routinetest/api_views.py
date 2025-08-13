"""
API views for placement test application.
Centralized API endpoints using service layer.
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.conf import settings
import json
import logging

from .models import Exam, StudentSession, Question, AudioFile
from .services import ExamService, SessionService, GradingService, PlacementService
from .error_handlers import (
    handle_api_errors, safe_get_or_404,
    log_activity, RoutineTestError
)

logger = logging.getLogger('primepath_routinetest.api')


@require_http_methods(["GET"])
def api_exam_list(request):
    """Get list of active exams."""
    try:
        exams = Exam.objects.filter(is_active=True).select_related('curriculum_level')
        data = [{
            'id': exam.id,
            'name': exam.name,
            'level': exam.curriculum_level.full_name if exam.curriculum_level else None,
            'duration': exam.timer_minutes,
            'questions': exam.total_questions
        } for exam in exams]
        
        return JsonResponse({'status': 'success', 'exams': data})
    except Exception as e:
        logger.error(f"Error fetching exams: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_http_methods(["GET"])
def api_exam_detail(request, exam_id):
    """Get detailed exam information."""
    try:
        exam = get_object_or_404(Exam, id=exam_id)
        data = {
            'id': exam.id,
            'name': exam.name,
            'pdf_url': exam.pdf_file.url if exam.pdf_file else None,
            'duration_minutes': exam.timer_minutes,
            'total_questions': exam.total_questions,
            'passing_score': exam.passing_score,
            'has_audio': exam.audio_files.exists(),
            'audio_count': exam.audio_files.count()
        }
        
        return JsonResponse({'status': 'success', 'exam': data})
    except Exception as e:
        logger.error(f"Error fetching exam {exam_id}: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_submit_answer(request):
    """Submit student answer."""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        question_id = data.get('question_id')
        answer = data.get('answer')
        
        session = get_object_or_404(StudentSession, id=session_id)
        
        if session.is_completed:
            return JsonResponse({
                'status': 'error',
                'message': 'Session already completed'
            }, status=400)
        
        student_answer = SessionService.submit_answer(
            session=session,
            question_id=question_id,
            answer=answer
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Answer saved',
            'answer_id': student_answer.id
        })
        
    except Exception as e:
        logger.error(f"Error submitting answer: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_complete_session(request):
    """Complete test session and get results."""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        
        session = get_object_or_404(StudentSession, id=session_id)
        
        if session.is_completed:
            return JsonResponse({
                'status': 'success',
                'already_completed': True,
                'score': float(session.percentage_score or 0)
            })
        
        results = SessionService.complete_session(session)
        
        return JsonResponse({
            'status': 'success',
            'results': results,
            'redirect_url': f'/routine-test/result/{session.id}/'
        })
        
    except Exception as e:
        logger.error(f"Error completing session: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_http_methods(["GET"])
def api_session_status(request, session_id):
    """Get current session status."""
    try:
        session = get_object_or_404(StudentSession, id=session_id)
        
        answered_count = session.answers.exclude(answer='').count()
        total_questions = session.exam.total_questions
        
        data = {
            'session_id': str(session.id),
            'is_completed': session.is_completed,
            'answered_count': answered_count,
            'total_questions': total_questions,
            'percentage_complete': (answered_count / total_questions * 100) if total_questions > 0 else 0,
            'time_spent': session.time_spent_seconds or 0
        }
        
        return JsonResponse({'status': 'success', 'session': data})
        
    except Exception as e:
        logger.error(f"Error fetching session status: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_http_methods(["GET"])
def api_placement_rules(request):
    """Get placement rules for display."""
    try:
        from core.models import PlacementRule
        
        rules = PlacementRule.objects.filter(is_active=True).select_related(
            'curriculum_level'
        ).order_by('curriculum_level__order', 'min_score')
        
        data = [{
            'id': rule.id,
            'level': rule.curriculum_level.full_name,
            'grade': rule.grade,
            'rank': rule.academic_rank,
            'min_score': rule.min_score,
            'max_score': rule.max_score
        } for rule in rules]
        
        return JsonResponse({'status': 'success', 'rules': data})
        
    except Exception as e:
        logger.error(f"Error fetching placement rules: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
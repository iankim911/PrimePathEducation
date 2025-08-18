"""
Student test-taking views
Handles the student experience: starting, taking, and completing tests
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import datetime
from django.db import transaction
from django.contrib import messages
from ..models import Exam, AudioFile, Question, StudentSession, StudentAnswer, DifficultyAdjustment
from core.models import School, PlacementRule, CurriculumLevel
from core.exceptions import (
    PlacementRuleException, ExamNotFoundException, SessionAlreadyCompletedException,
    ValidationException, FileProcessingException, AudioFileException, ExamConfigurationException
)
from core.decorators import handle_errors, validate_request_data
from ..services import PlacementService, SessionService, ExamService, GradingService
from ..error_handlers import (
    handle_view_errors, handle_api_errors, 
    validate_session_access, validate_exam_access,
    log_activity, RoutineTestError
)
import json
import uuid
import logging

logger = logging.getLogger('primepath_routinetest.student')


@handle_errors(template_name='primepath_routinetest/error.html')
def start_test(request):
    if request.method == 'POST':
        try:
            # Validate required fields
            required_fields = ['student_name', 'grade', 'academic_rank']
            missing_fields = [field for field in required_fields if not request.POST.get(field)]
            if missing_fields:
                raise ValidationException(
                    f"Missing required fields: {', '.join(missing_fields)}",
                    code="MISSING_FIELDS"
                )
            
            # Collect and validate student data
            student_data = {
                'student_name': request.POST.get('student_name'),
                'parent_phone': request.POST.get('parent_phone', '').replace('-', '').replace(' ', ''),  # Remove hyphens and spaces
                'school_name': request.POST.get('school_name'),
                'academic_rank': request.POST.get('academic_rank'),
            }
            
            # Validate grade
            try:
                grade = int(request.POST.get('grade'))
                if not 1 <= grade <= 12:
                    raise ValueError("Grade must be between 1 and 12")
                student_data['grade'] = grade
            except (ValueError, TypeError) as e:
                raise ValidationException("Invalid grade value", code="INVALID_GRADE")
            
            # Use PlacementService to match student to exam
            exam, curriculum_level = PlacementService.match_student_to_exam(
                grade=grade,
                academic_rank=student_data['academic_rank']
            )
            
            # Use SessionService to create the session
            session = SessionService.create_session(
                student_data=student_data,
                exam=exam,
                curriculum_level_id=curriculum_level.id,
                request_meta=request.META
            )
            
            return redirect('RoutineTest:take_test', session_id=session.id)
            
        except Exception as e:
            logger.error(f"Error creating test session: {str(e)}", exc_info=True)
            raise
    
    schools = School.objects.all().order_by('name')
    return render(request, 'primepath_routinetest/start_test.html', {
        'schools': schools,
        'grades': range(1, 13),
        'academic_ranks': StudentSession.ACADEMIC_RANKS
    })


def take_test(request, session_id):
    session = get_object_or_404(StudentSession, id=session_id)
    
    if session.is_completed:
        return redirect('RoutineTest:test_result', session_id=session_id)
    
    exam = session.exam
    questions = exam.routine_questions.select_related('audio_file').all()
    audio_files = exam.routine_audio_files.all()
    student_answers = {sa.question_id: sa for sa in session.answers.all()}
    
    # Prepare JavaScript configuration data (properly serialized)
    import json
    js_config = {
        'session': {
            'id': str(session.id),
            'examId': str(exam.id),
            'timerMinutes': exam.timer_minutes,
            'totalQuestions': exam.total_questions
        },
        'exam': {
            'id': str(exam.id),
            'name': exam.name,
            'totalQuestions': exam.total_questions,
            'timerMinutes': exam.timer_minutes,
            'pdfUrl': exam.pdf_file.url if exam.pdf_file else None,
            'pdfRotation': getattr(exam, 'pdf_rotation', 0)  # Include PDF rotation
        },
        'questions': [
            {
                'id': str(q.id),
                'number': q.question_number,
                'type': q.question_type,
                'optionsCount': q.options_count,
                'audioFileId': str(q.audio_file.id) if q.audio_file else None
            }
            for q in questions
        ],
        'audioFiles': [
            {
                'id': str(audio.id),
                'name': audio.name,
                'startQuestion': audio.start_question,
                'endQuestion': audio.end_question
            }
            for audio in audio_files
        ],
        'studentAnswers': {
            str(sa.question_id): sa.answer
            for sa in student_answers.values()
        }
    }
    
    # Use the standard V2 template (component-based)
    template_name = 'primepath_routinetest/student_test_v2.html'
    
    return render(request, template_name, {
        'session': session,
        'exam': exam,
        'questions': questions,
        'audio_files': audio_files,
        'student_answers': student_answers,
        'timer_seconds': exam.timer_minutes * 60,
        'js_config': js_config  # Pass as dict, not JSON string - json_script filter will handle encoding
    })


@handle_errors(ajax_only=True)
@require_POST
def submit_answer(request, session_id):
    """
    Submit an answer for a question in a test session.
    Supports multiple URL patterns for backward compatibility.
    """
    # Comprehensive logging for debugging
    console_log = {
        "view": "submit_answer",
        "action": "request_received",
        "session_id": str(session_id),
        "method": request.method,
        "path": request.path,
        "content_type": request.content_type,
        "user": str(request.user) if request.user.is_authenticated else "anonymous",
        "timestamp": timezone.now().isoformat()
    }
    print(f"[SUBMIT_ANSWER] {json.dumps(console_log)}")
    logger.info(f"Submit answer request for session {session_id} from path {request.path}")
    
    try:
        # Get and validate session
        session = get_object_or_404(StudentSession, id=session_id)
        
        # Log session state
        session_log = {
            "view": "submit_answer",
            "action": "session_loaded",
            "session_id": str(session_id),
            "exam_id": str(session.exam.id),
            "completed": session.completed_at is not None,
            "timer_expired": session.is_timer_expired() if hasattr(session, 'is_timer_expired') else None,
            "in_grace_period": session.is_in_grace_period() if hasattr(session, 'is_in_grace_period') else None
        }
        print(f"[SUBMIT_ANSWER_SESSION] {json.dumps(session_log)}")
        logger.debug(f"Session state: {session_log}")
        
        # Check if session can accept answers (handles timer expiry and grace period automatically)
        if not session.can_accept_answers():
            if session.exam.timer_minutes and session.is_timer_expired():
                if session.is_in_grace_period():
                    # This should not happen due to can_accept_answers logic, but log for debugging
                    logger.warning(f"Session {session_id} rejected despite being in grace period")
                    
                # Log the rejection with timing details
                timer_expiry_time = session.get_timer_expiry_time()
                time_since_expiry = timezone.now() - timer_expiry_time if timer_expiry_time else None
                logger.info(f"Answer submission rejected for session {session_id}: timer expired {time_since_expiry.total_seconds():.1f}s ago")
            else:
                logger.info(f"Answer submission rejected for session {session_id}: session completed")
                
            raise SessionAlreadyCompletedException("Cannot submit answers to a completed test")
        
        # Log grace period saves for monitoring
        if session.exam.timer_minutes and session.is_timer_expired() and session.is_in_grace_period():
            timer_expiry_time = session.get_timer_expiry_time()
            time_since_expiry = timezone.now() - timer_expiry_time
            logger.info(f"Grace period save for session {session_id}: {time_since_expiry.total_seconds():.1f}s after timer expiry")
        
        # Parse request data
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                raise ValidationException("Invalid JSON data", code="INVALID_JSON")
        else:
            data = request.POST
        
        # Get question and answer
        question_id = data.get('question_id')
        answer = data.get('answer', '').strip()
        
        # Log received data
        data_log = {
            "view": "submit_answer",
            "action": "data_received",
            "session_id": str(session_id),
            "question_id": str(question_id) if question_id else None,
            "answer_length": len(answer) if answer else 0,
            "answer_preview": answer[:50] if answer else None
        }
        print(f"[SUBMIT_ANSWER_DATA] {json.dumps(data_log)}")
        logger.debug(f"Answer data: {data_log}")
        
        if not question_id:
            raise ValidationException("Question ID is required", code="MISSING_QUESTION_ID")
        
        # Validate question exists and belongs to the exam
        try:
            question = Question.objects.get(id=question_id, exam=session.exam)
        except Question.DoesNotExist:
            raise ValidationException("Invalid question ID", code="INVALID_QUESTION")
        
        # Save or update the answer using SessionService
        student_answer = SessionService.submit_answer(
            session=session,
            question_id=question_id,
            answer=answer
        )
        
        if student_answer:
            # Check if this completes the test
            answered_count = session.answers.count()
            if answered_count >= session.exam.total_questions:
                # All questions answered
                return JsonResponse({
                    'success': True,
                    'message': 'Answer saved. Test complete!',
                    'allAnswered': True,
                    'answeredCount': answered_count,
                    'totalQuestions': session.exam.total_questions
                })
            
            return JsonResponse({
                'success': True,
                'message': 'Answer saved successfully',
                'answeredCount': answered_count,
                'totalQuestions': session.exam.total_questions
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to save answer',
                'code': 'SAVE_FAILED'
            }, status=400)
            
    except Exception as e:
        logger.error(f"PrimePath exception in submit_answer: {str(e)}", exc_info=True)
        raise


@require_POST
def adjust_difficulty(request, session_id):
    """Handles difficulty adjustment based on student performance"""
    session = get_object_or_404(StudentSession, id=session_id)
    
    if session.completed_at:
        return JsonResponse({'error': 'Test already completed'}, status=400)
    
    # Get current performance
    correct_count = session.answers.filter(is_correct=True).count()
    total_answered = session.answers.count()
    
    if total_answered < 5:  # Need minimum answers to adjust
        return JsonResponse({'adjusted': False, 'reason': 'Insufficient answers'})
    
    performance_rate = correct_count / total_answered
    
    # Determine adjustment
    adjustment_made = False
    new_level = None
    
    if performance_rate < 0.3 and session.difficulty_adjustments < 2:
        # Too difficult, adjust down
        new_level = PlacementService.adjust_difficulty(session, direction='down')
        adjustment_made = True
    elif performance_rate > 0.8 and session.difficulty_adjustments < 2:
        # Too easy, adjust up
        new_level = PlacementService.adjust_difficulty(session, direction='up')
        adjustment_made = True
    
    if adjustment_made and new_level:
        # Record adjustment
        DifficultyAdjustment.objects.create(
            session=session,
            from_level=session.current_curriculum_level,
            to_level=new_level,
            reason=f"Performance rate: {performance_rate:.1%}"
        )
        
        session.current_curriculum_level = new_level
        session.difficulty_adjustments += 1
        session.save()
        
        return JsonResponse({
            'adjusted': True,
            'new_level': str(new_level),
            'adjustment_count': session.difficulty_adjustments
        })
    
    return JsonResponse({'adjusted': False})


@require_POST
def manual_adjust_difficulty(request, session_id):
    """
    Manual difficulty adjustment by student request.
    This resets the exam with a new difficulty level.
    """
    try:
        session = get_object_or_404(StudentSession, id=session_id)
        
        # Check if session is already completed
        if session.is_completed:
            return JsonResponse({
                'success': False,
                'error': 'Cannot adjust difficulty for a completed test'
            }, status=400)
        
        # Parse request data
        data = json.loads(request.body)
        direction = data.get('direction')  # 'up' or 'down'
        
        if direction not in ['up', 'down']:
            return JsonResponse({
                'success': False,
                'error': 'Invalid direction. Must be "up" or "down"'
            }, status=400)
        
        adjustment = 1 if direction == 'up' else -1
        
        # Get current curriculum level
        current_level = session.final_curriculum_level or session.original_curriculum_level
        if not current_level:
            return JsonResponse({
                'success': False,
                'error': 'No curriculum level associated with current session'
            }, status=400)
        
        # Try to adjust difficulty using PlacementService
        result = PlacementService.adjust_difficulty(current_level, adjustment)
        
        if not result:
            # No level available in that direction
            if direction == 'up':
                message = "You're already at the most advanced level available."
            else:
                message = "You're already at the foundational level."
            
            return JsonResponse({
                'success': False,
                'error': message,
                'at_boundary': True
            }, status=200)
        
        new_level, new_exam = result
        
        with transaction.atomic():
            # Track the adjustment
            DifficultyAdjustment.objects.create(
                session=session,
                from_level=current_level,
                to_level=new_level,
                adjustment=adjustment
            )
            
            # Update session with new exam and level
            session.exam = new_exam
            session.final_curriculum_level = new_level
            session.difficulty_adjustments += 1
            
            # Clear all existing answers (reset progress)
            session.answers.all().delete()
            
            # Reset timer by updating started_at
            session.started_at = timezone.now()
            
            session.save()
        
        # Get difficulty info for both levels
        old_difficulty_info = PlacementService.get_difficulty_info(current_level)
        new_difficulty_info = PlacementService.get_difficulty_info(new_level)
        
        logger.info(
            f"Manual difficulty adjusted for session {session_id}: "
            f"{current_level.full_name} (diff {old_difficulty_info['current_difficulty']}) -> "
            f"{new_level.full_name} (diff {new_difficulty_info['current_difficulty']})"
        )
        
        print(f"[STUDENT_DIFFICULTY_SUCCESS] {{\"session\": \"{session_id}\", \"from_level\": \"{current_level.full_name}\", \"to_level\": \"{new_level.full_name}\", \"from_difficulty\": {old_difficulty_info['current_difficulty']}, \"to_difficulty\": {new_difficulty_info['current_difficulty']}, \"new_exam\": \"{new_exam.name}\"}}")
        
        return JsonResponse({
            'success': True,
            'new_level': new_level.full_name,
            'new_exam_id': str(new_exam.id),
            'new_exam_name': new_exam.name,
            'difficulty_info': new_difficulty_info,
            'difficulty_jump': new_difficulty_info['current_difficulty'] - old_difficulty_info['current_difficulty'],
            'message': f'Difficulty adjusted to {new_level.full_name} (Level {new_difficulty_info["current_difficulty"]})'
        })
        
    except Exception as e:
        logger.error(f"Error in manual difficulty adjustment: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while adjusting difficulty'
        }, status=500)


@require_POST
def complete_test(request, session_id):
    """Completes the test and calculates final score"""
    session = get_object_or_404(StudentSession, id=session_id)
    
    if session.completed_at:
        if request.content_type == 'application/json':
            return JsonResponse({
                'success': True,
                'redirect_url': reverse('RoutineTest:test_result', kwargs={'session_id': session_id})
            })
        return redirect('RoutineTest:test_result', session_id=session_id)
    
    # Check if this was triggered by timer expiry
    timer_expired = False
    unsaved_count = 0
    skip_difficulty_choice = False
    
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            timer_expired = data.get('timer_expired', False)
            unsaved_count = data.get('unsaved_count', 0)
            skip_difficulty_choice = data.get('skip_difficulty_choice', False)
            
            if timer_expired:
                logger.info(f"Session {session_id} completed due to timer expiry. Unsaved answers: {unsaved_count}")
        except json.JSONDecodeError:
            pass
    
    # Use GradingService to calculate final score
    results = GradingService.grade_session(session)
    
    # Mark session as complete
    session.completed_at = timezone.now()
    session.save()
    
    if timer_expired and unsaved_count > 0:
        messages.warning(request, f'Test time expired. {unsaved_count} answer(s) may not have been saved.')
    else:
        messages.success(request, 'Test completed successfully!')
    
    # For AJAX requests, return JSON response
    if request.content_type == 'application/json':
        # Check if we should show difficulty choice modal
        # Don't show for timer expiry or if explicitly skipped
        show_difficulty_choice = not timer_expired and not skip_difficulty_choice
        
        # Check if alternative difficulty levels are available
        if show_difficulty_choice:
            current_level = session.final_curriculum_level or session.original_curriculum_level
            if current_level:
                # Check if there are other difficulty levels available
                easier_available = PlacementService.find_alternate_difficulty_exam(current_level, -1) is not None
                harder_available = PlacementService.find_alternate_difficulty_exam(current_level, 1) is not None
                show_difficulty_choice = easier_available or harder_available
        
        return JsonResponse({
            'success': True,
            'show_difficulty_choice': show_difficulty_choice,
            'session_id': str(session_id),
            'redirect_url': reverse('RoutineTest:test_result', kwargs={'session_id': session_id})
        })
    
    return redirect('RoutineTest:test_result', session_id=session_id)


@require_POST
def post_submit_difficulty_choice(request, session_id):
    """
    Handle difficulty choice immediately after submitting the test.
    This is different from request_difficulty_change which is used on the results page.
    """
    session = get_object_or_404(StudentSession, id=session_id)
    
    # Ensure test is completed
    if not session.completed_at:
        return JsonResponse({'success': False, 'error': 'Test not completed'}, status=400)
    
    # Parse request data
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    else:
        data = request.POST
    
    adjustment = int(data.get('adjustment', 0))
    
    # If adjustment is 0, just go to results
    if adjustment == 0:
        return JsonResponse({
            'success': True,
            'action': 'show_results',
            'redirect_url': reverse('RoutineTest:test_result', kwargs={'session_id': session_id})
        })
    
    # Find appropriate difficulty level
    current_level = session.final_curriculum_level or session.original_curriculum_level
    
    if not current_level:
        return JsonResponse({
            'success': False,
            'error': 'No curriculum level assigned',
            'redirect_url': reverse('RoutineTest:test_result', kwargs={'session_id': session_id})
        }, status=400)
    
    # Use PlacementService to find an exam from a different difficulty tier
    result = PlacementService.find_alternate_difficulty_exam(current_level, adjustment)
    
    if not result:
        # No alternate difficulty available, show results
        messages.info(request, 'No alternative difficulty level available.')
        return JsonResponse({
            'success': True,
            'action': 'show_results',
            'message': 'No alternative difficulty level available',
            'redirect_url': reverse('RoutineTest:test_result', kwargs={'session_id': session_id})
        })
    
    new_level, new_exam = result
    
    # Create a new session with the new exam
    try:
        new_session = StudentSession.objects.create(
            student_name=session.student_name,
            parent_phone=session.parent_phone,
            school=session.school,
            grade=session.grade,
            academic_rank=session.academic_rank,
            exam=new_exam,
            original_curriculum_level=new_level,
            # Track that this is a difficulty adjustment
            notes=f"Post-submit difficulty adjustment from {current_level.full_name} (adjustment: {adjustment:+d})"
        )
        
        # Log the difficulty change
        logger.info(f"Created new session {new_session.id} for post-submit difficulty adjustment. "
                   f"Student: {session.student_name}, "
                   f"Previous level: {current_level.full_name}, "
                   f"New level: {new_level.full_name}, "
                   f"Adjustment: {adjustment:+d}")
        
        # Return success with new test URL
        return JsonResponse({
            'success': True,
            'action': 'start_new_test',
            'message': f'Starting {"easier" if adjustment < 0 else "harder"} test...',
            'redirect_url': reverse('RoutineTest:take_test', kwargs={'session_id': new_session.id})
        })
        
    except Exception as e:
        logger.error(f"Error creating new session for difficulty adjustment: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to create new test session',
            'redirect_url': reverse('RoutineTest:test_result', kwargs={'session_id': session_id})
        }, status=500)


def test_result(request, session_id):
    """Displays test results to the student"""
    session = get_object_or_404(StudentSession, id=session_id)
    
    if not session.completed_at:
        return redirect('RoutineTest:take_test', session_id=session_id)
    
    # Get detailed results
    results = GradingService.get_detailed_results(session_id)
    
    return render(request, 'primepath_routinetest/test_result.html', {
        'session': session,
        'results': results,
        'exam': session.exam,
        'final_level': session.final_curriculum_level
    })


@require_POST
def request_difficulty_change(request):
    """
    Handle request to try a different difficulty level after completing an exam.
    Creates a new session with an exam from a different difficulty tier.
    """
    from ..services import PlacementService
    from django.contrib import messages
    
    session_id = request.POST.get('session_id')
    adjustment = int(request.POST.get('adjustment', 0))  # +1 for harder, -1 for easier
    
    if not session_id or adjustment not in [-1, 1]:
        messages.error(request, "Invalid difficulty adjustment request")
        return redirect('RoutineTest:start_test')
    
    # Get the original session
    original_session = get_object_or_404(StudentSession, id=session_id)
    
    if not original_session.completed_at:
        messages.error(request, "Please complete the current test first")
        return redirect('RoutineTest:take_test', session_id=session_id)
    
    # Get the original curriculum level
    original_level = original_session.original_curriculum_level
    if not original_level:
        original_level = original_session.final_curriculum_level
    
    if not original_level:
        messages.error(request, "Unable to determine difficulty level")
        return redirect('RoutineTest:test_result', session_id=session_id)
    
    try:
        # Find an exam from a different difficulty tier
        result = PlacementService.find_alternate_difficulty_exam(original_level, adjustment)
        
        if not result:
            if adjustment > 0:
                messages.info(request, "No harder difficulty level available. You're already at an advanced level!")
            else:
                messages.info(request, "No easier difficulty level available. You're already at a basic level!")
            return redirect('RoutineTest:test_result', session_id=session_id)
        
        new_level, new_exam = result
        
        # Create a new session with the alternate difficulty exam
        new_session = StudentSession.objects.create(
            student_name=original_session.student_name,
            parent_phone=original_session.parent_phone,
            school=original_session.school,
            school_name_manual=original_session.school_name_manual,
            grade=original_session.grade,
            academic_rank=original_session.academic_rank,
            exam=new_exam,
            original_curriculum_level=new_level,
            difficulty_adjustments=adjustment,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Log the difficulty change
        logger.info(
            f"Created new session {new_session.id} with {['easier', '', 'harder'][adjustment + 1]} "
            f"difficulty for student {new_session.student_name}"
        )
        
        messages.success(request, f"Starting {'easier' if adjustment < 0 else 'harder'} difficulty test!")
        return redirect('RoutineTest:take_test', session_id=new_session.id)
        
    except Exception as e:
        logger.error(f"Error creating alternate difficulty session: {e}", exc_info=True)
        messages.error(request, "Unable to load alternate difficulty test. Please try again.")
        return redirect('RoutineTest:test_result', session_id=session_id)
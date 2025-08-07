"""
Student test-taking views
Handles the student experience: starting, taking, and completing tests
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
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
from core.utils import get_template_name
import json
import uuid
import logging

logger = logging.getLogger(__name__)


@handle_errors(template_name='placement_test/error.html')
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
            
            return redirect('placement_test:take_test', session_id=session.id)
            
        except Exception as e:
            logger.error(f"Error creating test session: {str(e)}", exc_info=True)
            raise
    
    schools = School.objects.all().order_by('name')
    return render(request, 'placement_test/start_test.html', {
        'schools': schools,
        'grades': range(1, 13),
        'academic_ranks': StudentSession.ACADEMIC_RANKS
    })


def take_test(request, session_id):
    session = get_object_or_404(StudentSession, id=session_id)
    
    if session.is_completed:
        return redirect('placement_test:test_result', session_id=session_id)
    
    exam = session.exam
    questions = exam.questions.select_related('audio_file').all()
    audio_files = exam.audio_files.all()
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
            'pdfUrl': exam.pdf_file.url if exam.pdf_file else None
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
    
    template_name = get_template_name('placement_test/student_test.html', 'placement_test/take_test.html')
    
    return render(request, template_name, {
        'session': session,
        'exam': exam,
        'questions': questions,
        'audio_files': audio_files,
        'student_answers': student_answers,
        'js_config': json.dumps(js_config)  # Pass as JSON string
    })


@handle_errors(ajax_only=True)
@require_POST
def submit_answer(request, session_id):
    try:
        # Get and validate session
        session = get_object_or_404(StudentSession, id=session_id)
        
        # Check if session is completed
        if session.completed_at:
            raise SessionAlreadyCompletedException("Cannot submit answers to a completed test")
        
        # Check if session has exceeded time limit
        if session.exam.timer_minutes:
            time_elapsed = (timezone.now() - session.started_at).total_seconds() / 60
            if time_elapsed > session.exam.timer_minutes:
                # Mark session as complete due to timeout
                session.completed_at = timezone.now()
                session.save()
                raise SessionAlreadyCompletedException("Test time has expired")
        
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
        
        if not question_id:
            raise ValidationException("Question ID is required", code="MISSING_QUESTION_ID")
        
        # Validate question exists and belongs to the exam
        try:
            question = Question.objects.get(id=question_id, exam=session.exam)
        except Question.DoesNotExist:
            raise ValidationException("Invalid question ID", code="INVALID_QUESTION")
        
        # Save or update the answer using SessionService
        student_answer = SessionService.save_answer(
            session_id=session_id,
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
def complete_test(request, session_id):
    """Completes the test and calculates final score"""
    session = get_object_or_404(StudentSession, id=session_id)
    
    if session.completed_at:
        return redirect('placement_test:test_result', session_id=session_id)
    
    # Use GradingService to calculate final score
    results = GradingService.grade_session(session)
    
    # Mark session as complete
    session.completed_at = timezone.now()
    session.save()
    
    messages.success(request, 'Test completed successfully!')
    return redirect('placement_test:test_result', session_id=session_id)


def test_result(request, session_id):
    """Displays test results to the student"""
    session = get_object_or_404(StudentSession, id=session_id)
    
    if not session.completed_at:
        return redirect('placement_test:take_test', session_id=session_id)
    
    # Get detailed results
    results = GradingService.get_detailed_results(session_id)
    
    return render(request, 'placement_test/test_result.html', {
        'session': session,
        'results': results,
        'exam': session.exam,
        'final_level': session.final_curriculum_level
    })
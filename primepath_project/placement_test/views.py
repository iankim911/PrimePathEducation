from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404, FileResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, Count, Avg
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Exam, AudioFile, Question, StudentSession, StudentAnswer, DifficultyAdjustment
from core.models import School, PlacementRule, CurriculumLevel
from core.exceptions import (
    PlacementRuleException, ExamNotFoundException, SessionAlreadyCompletedException,
    ValidationException, FileProcessingException, AudioFileException, ExamConfigurationException
)
from core.decorators import handle_errors, validate_request_data, teacher_required
from .services import PlacementService, SessionService, ExamService, GradingService
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
    
    context = {
        'session': session,
        'exam': exam,
        'questions': questions,
        'audio_files': audio_files,
        'student_answers': student_answers,
        'timer_seconds': exam.timer_minutes * 60,
    }
    
    response = render(request, 'placement_test/student_test.html', context)
    
    # Add no-cache headers to prevent browser caching of dynamic question content
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response


@require_http_methods(["POST"])
@handle_errors(ajax_only=True)
def submit_answer(request, session_id):
    """Submit an answer for a specific question."""
    try:
        session = get_object_or_404(StudentSession, id=session_id)
        
        data = json.loads(request.body)
        question_id = data.get('question_id')
        answer = data.get('answer', '')
        
        if not question_id:
            raise ValidationException(
                "Question ID is required",
                code="MISSING_QUESTION_ID"
            )
        
        # Use SessionService to submit the answer
        SessionService.submit_answer(
            session=session,
            question_id=question_id,
            answer=answer
        )
        
        return JsonResponse({'success': True})
        
    except json.JSONDecodeError:
        raise ValidationException("Invalid JSON data", code="INVALID_JSON")


@require_http_methods(["POST"])
@handle_errors(ajax_only=True)
def adjust_difficulty(request, session_id):
    """Adjust the difficulty level of a test session."""
    session = get_object_or_404(StudentSession, id=session_id)
    
    try:
        data = json.loads(request.body)
        adjustment = int(data.get('adjustment', 0))
        
        # Use PlacementService to find new level and exam
        result = PlacementService.adjust_difficulty(
            current_level=session.final_curriculum_level,
            adjustment=adjustment
        )
        
        if not result:
            return JsonResponse({
                'success': False,
                'error': 'No exam available at the requested difficulty level'
            })
        
        new_level, new_exam = result
        
        # Use SessionService to update the session
        SessionService.adjust_session_difficulty(
            session=session,
            adjustment=adjustment,
            new_level=new_level,
            new_exam=new_exam
        )
        
        return JsonResponse({
            'success': True,
            'redirect_url': f'/api/placement/session/{session_id}/'
        })
        
    except json.JSONDecodeError:
        raise ValidationException("Invalid JSON data", code="INVALID_JSON")


@require_http_methods(["POST"])
@handle_errors(ajax_only=True)
def complete_test(request, session_id):
    """Complete a test session and calculate final scores."""
    session = get_object_or_404(StudentSession, id=session_id)
    
    # Use SessionService to complete the session
    completion_results = SessionService.complete_session(session)
    
    return JsonResponse({
        'success': True,
        'redirect_url': f'/api/placement/session/{session_id}/result/',
        'results': completion_results
    })


def test_result(request, session_id):
    session = get_object_or_404(StudentSession, id=session_id)
    
    if not session.is_completed:
        return redirect('placement_test:take_test', session_id=session_id)
    
    context = {
        'session': session,
        'exam': session.exam,
        'answers': session.answers.select_related('question').all(),
        'curriculum_recommendation': session.final_curriculum_level,
    }
    return render(request, 'placement_test/test_result.html', context)


def exam_list(request):
    exams = Exam.objects.select_related('curriculum_level__subprogram__program').all()
    return render(request, 'placement_test/exam_list.html', {'exams': exams})


@handle_errors(ajax_only=True)
def check_exam_version(request):
    """API endpoint to get the next available version for a curriculum level"""
    curriculum_level_id = request.GET.get('curriculum_level')
    if not curriculum_level_id:
        raise ValidationException(
            "curriculum_level parameter is required",
            code="MISSING_PARAM"
        )
    
    try:
        next_version = ExamService.get_next_version_letter(int(curriculum_level_id))
        return JsonResponse({'next_version': next_version})
    except ExamConfigurationException as e:
        return JsonResponse({
            'error': str(e),
            'next_version': None
        }, status=400)


@handle_errors(template_name='placement_test/create_exam.html')
def create_exam(request):
    if request.method == 'POST':
        # Prepare exam data
        exam_data = {
            'name': request.POST.get('name'),
            'curriculum_level_id': request.POST.get('curriculum_level', '').strip() or None,
            'timer_minutes': int(request.POST.get('timer_minutes', 60)),
            'total_questions': int(request.POST.get('total_questions')),
            'default_options_count': int(request.POST.get('default_options_count', 5)),
            'passing_score': 0,
            'created_by': None,  # No auth required as per PRD
            'is_active': True,
            'skip_first_left_half': bool(request.POST.get('skip_first_left_half'))
        }
        
        # Use ExamService to create exam with files
        exam = ExamService.create_exam(
            exam_data=exam_data,
            pdf_file=request.FILES.get('pdf_file'),
            audio_files=request.FILES.getlist('audio_files'),
            audio_names=request.POST.getlist('audio_names[]')
        )
        
        messages.success(request, f'Exam "{exam.name}" uploaded successfully!')
        return redirect('placement_test:create_exam')
    
    # Get curriculum levels with version info
    curriculum_levels = CurriculumLevel.objects.select_related('subprogram__program').all()
    
    # Add version info to each level using ExamService
    levels_with_versions = []
    for level in curriculum_levels:
        try:
            next_version = ExamService.get_next_version_letter(level.id)
        except ExamConfigurationException:
            next_version = 'N/A'  # All versions used
        
        # Get existing versions for display
        existing_exams = Exam.objects.filter(
            curriculum_level=level,
            name__regex=r'^\[PlacementTest\].*_v_[a-z]$'
        ).values_list('name', flat=True)
        
        used_versions = []
        for exam_name in existing_exams:
            if '_v_' in exam_name:
                version = exam_name.split('_v_')[-1]
                if len(version) == 1 and version.isalpha() and version.islower():
                    used_versions.append(version)
        
        levels_with_versions.append({
            'id': level.id,
            'full_name': level.full_name,
            'next_version': next_version,
            'existing_versions': ', '.join(used_versions) if used_versions else 'none'
        })
    
    return render(request, 'placement_test/create_exam.html', {
        'curriculum_levels': levels_with_versions
    })


def exam_detail(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = exam.questions.all()
    audio_files = exam.audio_files.all()
    
    context = {
        'exam': exam,
        'questions': questions,
        'audio_files': audio_files,
    }
    return render(request, 'placement_test/exam_detail.html', context)


def edit_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    return render(request, 'placement_test/edit_exam.html', {'exam': exam})


def preview_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    
    # Get or create questions for the exam with audio files prefetched
    questions = exam.questions.select_related('audio_file').all().order_by('question_number')
    
    # If no questions exist, create them based on total_questions
    if not questions.exists():
        for i in range(1, exam.total_questions + 1):
            Question.objects.create(
                exam=exam,
                question_number=i,
                question_type='MCQ',  # Default to MCQ since PDF contains the questions
                correct_answer='',
                points=1,
                options_count=exam.default_options_count
            )
        questions = exam.questions.all().order_by('question_number')
    
    # Process questions to add response lists for short and long answers
    for question in questions:
        # For SHORT questions, prioritize options_count over existing correct_answer
        if question.question_type == 'SHORT':
            if question.options_count and question.options_count >= 1:
                # Use options_count - don't populate response_list so template uses options_count logic
                question.response_list = []
            elif question.correct_answer:
                # Fallback to existing correct_answer data
                question.response_list = question.correct_answer.split('|')
            else:
                question.response_list = []
        else:
            question.response_list = []
            
        if question.question_type == 'LONG' and question.correct_answer:
            question.long_response_list = question.correct_answer.split('|||')
        else:
            question.long_response_list = []
            
        # Ensure options_count has a reasonable value (should already be set from database)
        if not question.options_count or question.options_count < 1:
            question.options_count = 5
    
    # Debug logging
    logger.info(f"Preview exam view - Exam: {exam.name}")
    logger.info(f"Questions count: {questions.count()}")
    questions_with_audio = questions.filter(audio_file__isnull=False)
    logger.info(f"Questions with audio: {questions_with_audio.count()}")
    for q in questions_with_audio:
        logger.info(f"  Q{q.question_number} -> Audio {q.audio_file.id} ({q.audio_file.name})")
    
    context = {
        'exam': exam,
        'questions': questions,
    }
    
    response = render(request, 'placement_test/preview_and_answers.html', context)
    
    # Add no-cache headers to prevent browser caching of dynamic admin content
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response


def add_audio(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    
    if request.method == 'POST':
        pass
    
    return render(request, 'placement_test/add_audio.html', {'exam': exam})


def manage_questions(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = exam.questions.all()
    
    return render(request, 'placement_test/manage_questions.html', {
        'exam': exam,
        'questions': questions
    })


@require_http_methods(["POST"])
def update_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    
    try:
        question.correct_answer = request.POST.get('correct_answer', '')
        question.points = int(request.POST.get('points', 1))
        question.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["POST"])
def create_questions(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    
    try:
        # Get existing question numbers
        existing_numbers = set(exam.questions.values_list('question_number', flat=True))
        
        # Create missing questions
        questions_created = 0
        for num in range(1, exam.total_questions + 1):
            if num not in existing_numbers:
                # Default to MCQ for now
                Question.objects.create(
                    exam=exam,
                    question_number=num,
                    question_type='MCQ',
                    correct_answer='',
                    points=1
                )
                questions_created += 1
        
        return JsonResponse({
            'success': True,
            'questions_created': questions_created
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def session_list(request):
    """List all placement test sessions with filtering options."""
    sessions = StudentSession.objects.select_related('exam', 'original_curriculum_level', 'school').all()
    
    # Apply search filter
    search_query = request.GET.get('search')
    if search_query:
        sessions = sessions.filter(
            Q(student_name__icontains=search_query) |
            Q(school__name__icontains=search_query) |
            Q(school_name_manual__icontains=search_query)
        )
    
    # Apply filters
    status_filter = request.GET.get('status')
    if status_filter:
        if status_filter == 'completed':
            sessions = sessions.filter(completed_at__isnull=False)
        elif status_filter == 'in_progress':
            sessions = sessions.filter(completed_at__isnull=True)
    
    grade_filter = request.GET.get('grade')
    if grade_filter:
        sessions = sessions.filter(grade=grade_filter)
    
    academic_rank_filter = request.GET.get('academic_rank')
    if academic_rank_filter:
        sessions = sessions.filter(academic_rank=academic_rank_filter)
    
    date_from = request.GET.get('date_from')
    if date_from:
        sessions = sessions.filter(started_at__date__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        sessions = sessions.filter(started_at__date__lte=date_to)
    
    # Calculate statistics
    total_sessions = sessions.count()
    completed_sessions = sessions.filter(completed_at__isnull=False).count()
    in_progress_sessions = sessions.filter(completed_at__isnull=True).count()
    not_started_sessions = 0  # Sessions are started when created
    
    # Order by most recent first
    sessions = sessions.order_by('-started_at')
    
    # Check if there are any in-progress sessions (for auto-refresh)
    has_in_progress = in_progress_sessions > 0
    
    context = {
        'sessions': sessions[:50],  # Show latest 50 sessions
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'in_progress_sessions': in_progress_sessions,
        'not_started_sessions': not_started_sessions,
        'has_in_progress': has_in_progress,
    }
    
    return render(request, 'placement_test/session_list.html', context)


def session_detail(request, session_id):
    """Display detailed information about a specific session."""
    session = get_object_or_404(StudentSession, id=session_id)
    answers = StudentAnswer.objects.filter(session=session).select_related('question').order_by('question__question_number')
    
    context = {
        'session': session,
        'answers': answers,
    }
    return render(request, 'placement_test/session_detail.html', context)


def grade_session(request, session_id):
    session = get_object_or_404(StudentSession, id=session_id)
    return render(request, 'placement_test/grade_session.html', {'session': session})


def export_result(request, session_id):
    """Export session results as PDF or CSV."""
    session = get_object_or_404(StudentSession, id=session_id)
    
    # For now, return a simple CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="placement_test_result_{session_id}.csv"'
    
    import csv
    writer = csv.writer(response)
    writer.writerow(['Student Name', 'Grade', 'School', 'Test Date', 'Score', 'Assigned Level'])
    writer.writerow([
        session.student_name,
        session.grade,
        session.school.name if session.school else session.school_name_manual or 'N/A',
        session.started_at.strftime('%Y-%m-%d %H:%M') if session.started_at else 'N/A',
        f"{session.score}%" if session.score else 'N/A',
        session.original_curriculum_level.full_name if session.original_curriculum_level else 'N/A'
    ])
    
    return response


@require_http_methods(["POST"])
@handle_errors(ajax_only=True)


@require_http_methods(["POST"])
@login_required
@teacher_required
def update_exam_name(request, exam_id):
    """Update exam name."""
    try:
        exam = get_object_or_404(Exam, id=exam_id)
        data = json.loads(request.body)
        new_name = data.get('name', '').strip()
        
        if not new_name:
            return JsonResponse({
                'success': False,
                'error': 'Exam name cannot be empty'
            }, status=400)
        
        exam.name = new_name
        exam.save()
        
        return JsonResponse({
            'success': True,
            'name': exam.name
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@handle_errors()
def get_audio(request, audio_id):
    """Stream audio file instead of loading into memory."""
    audio = get_object_or_404(AudioFile, id=audio_id)
    
    try:
        # Check if file exists
        if not audio.audio_file:
            raise AudioFileException(
                "Audio file reference is missing",
                code="NO_FILE_REFERENCE",
                details={'audio_id': audio_id}
            )
        
        # Use FileResponse for efficient file streaming
        response = FileResponse(
            audio.audio_file.open('rb'),
            content_type='audio/mpeg'
        )
        response['Content-Disposition'] = f'inline; filename="{audio.audio_file.name}"'
        response['Content-Length'] = audio.audio_file.size
        return response
    except (FileNotFoundError, IOError) as e:
        logger.error(f"Audio file error: {e}, path: {audio.audio_file.path if audio.audio_file else 'No file'}")
        raise AudioFileException(
            "Audio file not found on disk",
            code="FILE_NOT_FOUND",
            details={'audio_id': audio_id, 'path': audio.audio_file.path if audio.audio_file else 'No file'}
        )


@require_http_methods(["POST"])
@csrf_exempt
@handle_errors(ajax_only=True)
def save_exam_answers(request, exam_id):
    """Save exam questions and answers configuration."""
    exam = get_object_or_404(Exam, id=exam_id)
    
    try:
        data = json.loads(request.body)
        questions_data = data.get('questions', [])
        audio_assignments = data.get('audio_assignments', {})
        
        # Use ExamService to update questions
        results = ExamService.update_exam_questions(exam, questions_data)
        
        # Handle audio assignments if provided
        audio_results = {}
        if audio_assignments:
            audio_results = ExamService.update_audio_assignments(exam, audio_assignments)
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully saved {len(questions_data)} questions',
            'details': results,
            'audio_assignments_saved': len(audio_assignments),
            'audio_results': audio_results
        })
        
    except json.JSONDecodeError:
        raise ValidationException("Invalid JSON data", code="INVALID_JSON")


@require_http_methods(["POST"])
@handle_errors(template_name='placement_test/exam_list.html')
def delete_exam(request, exam_id):
    """Delete an exam and all associated files."""
    exam = get_object_or_404(Exam, id=exam_id)
    exam_name = exam.name
    
    # Use ExamService to delete exam
    ExamService.delete_exam(exam)
    
    messages.success(request, f'Exam "{exam_name}" has been deleted successfully.')
    return redirect('placement_test:exam_list')


@login_required
@teacher_required
def update_audio_names(request, exam_id):
    """API endpoint to update audio file names."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        exam = get_object_or_404(Exam, id=exam_id)
        data = json.loads(request.body)
        audio_files = data.get('audio_files', [])
        
        updated_count = 0
        for audio_data in audio_files:
            audio_id = audio_data.get('id')
            new_name = audio_data.get('name', '').strip()
            
            if audio_id and new_name:
                try:
                    audio = AudioFile.objects.get(id=audio_id, exam=exam)
                    audio.name = new_name
                    audio.save()
                    updated_count += 1
                except AudioFile.DoesNotExist:
                    logger.warning(f"Audio file {audio_id} not found for exam {exam_id}")
        
        return JsonResponse({
            'success': True,
            'updated_count': updated_count
        })
        
    except Exception as e:
        logger.error(f"Error updating audio names: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@teacher_required
def delete_audio_from_exam(request, exam_id, audio_id):
    """Delete audio file from an exam."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        exam = get_object_or_404(Exam, id=exam_id)
        audio = get_object_or_404(AudioFile, id=audio_id, exam=exam)
        
        # Delete the audio file
        audio.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Audio file removed from exam successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting audio file: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_POST
def update_skip_first_left_half(request, exam_id):
    """Update the skip_first_left_half setting for an exam."""
    try:
        exam = get_object_or_404(Exam, id=exam_id)
        
        import json
        data = json.loads(request.body)
        skip_first_left_half = data.get('skip_first_left_half', False)
        
        # Validate the boolean value
        if not isinstance(skip_first_left_half, bool):
            return JsonResponse({
                'success': False, 
                'error': 'skip_first_left_half must be a boolean value'
            }, status=400)
        
        exam.skip_first_left_half = skip_first_left_half
        exam.save()
        
        return JsonResponse({
            'success': True,
            'skip_first_left_half': exam.skip_first_left_half,
            'message': f'Skip first left half {"enabled" if skip_first_left_half else "disabled"} for exam: {exam.name}'
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False, 
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        }, status=500)



"""
Exam management views
Handles exam creation, editing, preview, and deletion
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from ..models import Exam, AudioFile, Question
from core.models import CurriculumLevel
from core.exceptions import ValidationException, ExamConfigurationException
from core.decorators import handle_errors
from ..services import ExamService
import logging
import json

logger = logging.getLogger(__name__)


@login_required
def exam_list(request):
    """List all exams (requires authentication)"""
    # Log authentication check
    console_log = {
        "view": "exam_list",
        "user": str(request.user),
        "authenticated": request.user.is_authenticated,
        "method": request.method
    }
    logger.info(f"[EXAM_LIST] {json.dumps(console_log)}")
    
    exams = Exam.objects.select_related('curriculum_level__subprogram__program').all()
    return render(request, 'placement_test/exam_list.html', {'exams': exams})


@handle_errors(ajax_only=True)
def check_exam_version(request):
    """API endpoint to get the next available version for a curriculum level"""
    from datetime import datetime
    
    curriculum_level_id = request.GET.get('curriculum_level')
    if not curriculum_level_id:
        raise ValidationException(
            "curriculum_level parameter is required",
            code="MISSING_PARAM"
        )
    
    try:
        # Get today's date in YYMMDD format
        date_str = datetime.now().strftime('%y%m%d')
        
        # Get next version number (will be None if no same-day uploads)
        next_version = ExamService.get_next_version_number(int(curriculum_level_id), date_str)
        
        return JsonResponse({
            'next_version': next_version,
            'date_str': date_str
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'next_version': None,
            'date_str': datetime.now().strftime('%y%m%d')
        }, status=400)


@login_required
@handle_errors(template_name='placement_test/create_exam.html')
def create_exam(request):
    """Create a new exam (requires authentication)"""
    # Log authentication check
    console_log = {
        "view": "create_exam",
        "user": str(request.user),
        "authenticated": request.user.is_authenticated,
        "method": request.method
    }
    logger.info(f"[CREATE_EXAM] {json.dumps(console_log)}")
    print(f"[CREATE_EXAM_AUTH] {json.dumps(console_log)}")
    
    if request.method == 'POST':
        try:
            # Validate required fields
            exam_name = request.POST.get('name')
            if not exam_name:
                raise ValidationException("Exam name is required", code="MISSING_NAME")
            
            total_questions = request.POST.get('total_questions')
            if not total_questions:
                raise ValidationException("Total number of questions is required", code="MISSING_QUESTIONS")
            
            # Prepare exam data with validation
            exam_data = {
                'name': exam_name,
                'curriculum_level_id': request.POST.get('curriculum_level', '').strip() or None,
                'timer_minutes': int(request.POST.get('timer_minutes', 60)),
                'total_questions': int(total_questions),
                'default_options_count': int(request.POST.get('default_options_count', 5)),
                'passing_score': 0,
                'pdf_rotation': int(request.POST.get('pdf_rotation', 0)),  # Add rotation from form
                'created_by': request.user if request.user.is_authenticated else None,  # Track who created the exam
                'is_active': True
            }
            
            # Validate PDF file
            pdf_file = request.FILES.get('pdf_file')
            if not pdf_file:
                raise ValidationException("PDF file is required", code="MISSING_PDF")
            
            # Use ExamService to create exam with files
            exam = ExamService.create_exam(
                exam_data=exam_data,
                pdf_file=pdf_file,
                audio_files=request.FILES.getlist('audio_files'),
                audio_names=request.POST.getlist('audio_names[]')
            )
            
            messages.success(request, f'Exam "{exam.name}" uploaded successfully!')
            return redirect('placement_test:create_exam')
            
        except ValueError as e:
            messages.error(request, f"Invalid input: {str(e)}")
            # Fall through to render the form again with error message
        except ValidationException as e:
            messages.error(request, e.message)
            # Fall through to render the form again with error message
    
    # Get curriculum levels with version info
    from datetime import datetime
    curriculum_levels = CurriculumLevel.objects.select_related('subprogram__program').all()
    
    # Get today's date for checking same-day uploads
    today_str = datetime.now().strftime('%y%m%d')
    
    # Add version info to each level using new naming convention
    levels_with_versions = []
    for level in curriculum_levels:
        # Check if there are existing uploads today for this level
        next_version = ExamService.get_next_version_number(level.id, today_str)
        
        # Get count of existing exams for this level (for info display)
        existing_count = Exam.objects.filter(curriculum_level=level).count()
        
        levels_with_versions.append({
            'id': level.id,
            'display_name': level.display_name,  # Use new display_name property
            'exam_base_name': level.exam_base_name,  # Use new exam_base_name property
            'next_version': next_version,
            'existing_count': existing_count,
            'date_str': today_str
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
        # For SHORT questions, populate response_list with saved values
        if question.question_type == 'SHORT':
            if question.correct_answer:
                # Check which separator is used
                if '|' in question.correct_answer:
                    # Pipe-separated values
                    question.response_list = question.correct_answer.split('|')
                elif ',' in question.correct_answer and question.options_count and question.options_count > 1:
                    # Comma-separated values with multiple fields expected
                    question.response_list = [s.strip() for s in question.correct_answer.split(',')]
                else:
                    # Single value or no special separator
                    question.response_list = [question.correct_answer] if question.correct_answer else []
            else:
                # No saved answer yet
                question.response_list = []
        else:
            question.response_list = []
            
        if question.question_type == 'LONG' and question.correct_answer:
            question.response_list = question.correct_answer.split('|')
        
        # For checkbox questions
        if question.question_type == 'CHECKBOX' and question.correct_answer:
            question.checked_values = question.correct_answer.split(',')
        else:
            question.checked_values = []
    
    # Get audio files
    audio_files = exam.audio_files.all()
    
    return render(request, 'placement_test/preview_and_answers.html', {
        'exam': exam,
        'questions': questions,
        'audio_files': audio_files,
    })


def manage_questions(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = exam.questions.all().order_by('question_number')
    
    if request.method == 'POST':
        # Process question updates
        for question in questions:
            question_type = request.POST.get(f'question_type_{question.id}')
            correct_answer = request.POST.get(f'correct_answer_{question.id}', '')
            points = request.POST.get(f'points_{question.id}', 1)
            
            if question_type:
                question.question_type = question_type
            question.correct_answer = correct_answer
            question.points = int(points)
            question.save()
        
        messages.success(request, 'Questions updated successfully!')
        return redirect('placement_test:manage_questions', exam_id=exam_id)
    
    return render(request, 'placement_test/manage_questions.html', {
        'exam': exam,
        'questions': questions,
    })


@require_http_methods(["POST"])
def delete_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    exam_name = exam.name
    
    try:
        # Delete associated files
        if exam.pdf_file:
            exam.pdf_file.delete()
        
        # Delete audio files
        for audio in exam.audio_files.all():
            if audio.audio_file:
                audio.audio_file.delete()
            audio.delete()
        
        # Delete the exam (questions will cascade)
        exam.delete()
        
        messages.success(request, f'Exam "{exam_name}" deleted successfully!')
        
    except Exception as e:
        logger.error(f"Error deleting exam: {str(e)}")
        messages.error(request, f'Error deleting exam: {str(e)}')
    
    return redirect('placement_test:exam_list')
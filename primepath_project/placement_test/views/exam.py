"""
Exam management views
Handles exam creation, editing, preview, and deletion
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import transaction
from ..models import Exam, AudioFile, Question
from core.models import CurriculumLevel
from core.exceptions import ValidationException, ExamConfigurationException
from core.decorators import handle_errors
from ..services import ExamService
import logging

logger = logging.getLogger(__name__)


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
                'created_by': None,  # No auth required as per PRD
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
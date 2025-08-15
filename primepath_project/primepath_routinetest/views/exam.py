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
from django.utils import timezone
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
    
    # Fetch exams with related data and prefetch questions for answer mapping check
    exams = Exam.objects.select_related(
        'curriculum_level__subprogram__program'
    ).prefetch_related(
        'questions',  # Prefetch questions to avoid N+1 queries
        'audio_files',  # Also prefetch audio files for display
        'student_roster'  # Phase 5: Prefetch roster for stats
    ).all()
    
    # Add answer mapping status and roster stats to each exam
    exams_with_status = []
    for exam in exams:
        # Get answer mapping status
        mapping_status = exam.get_answer_mapping_status()
        
        # Phase 5: Get roster statistics
        roster_stats = exam.get_roster_stats()
        
        # Log the mapping status for each exam
        console_log = {
            "view": "exam_list",
            "action": "answer_mapping_check",
            "exam_id": str(exam.id),
            "exam_name": exam.name,
            "total_questions": mapping_status['total_questions'],
            "mapped_questions": mapping_status['mapped_questions'],
            "unmapped_questions": mapping_status['unmapped_questions'],
            "percentage_complete": mapping_status['percentage_complete'],
            "status": mapping_status['status_label'],
            "roster_total": roster_stats['total_assigned'],  # Phase 5
            "roster_completed": roster_stats['completed']  # Phase 5
        }
        logger.info(f"[EXAM_LIST_MAPPING] {json.dumps(console_log)}")
        
        # Add the status to the exam object for template access
        exam.answer_mapping_status = mapping_status
        exam.roster_stats = roster_stats  # Phase 5: Add roster stats
        exams_with_status.append(exam)
    
    # Log summary of answer mapping statuses
    complete_count = sum(1 for e in exams_with_status if e.answer_mapping_status['is_complete'])
    partial_count = sum(1 for e in exams_with_status if e.answer_mapping_status['status_label'] == 'Partial')
    not_started_count = sum(1 for e in exams_with_status if e.answer_mapping_status['status_label'] == 'Not Started')
    
    console_log = {
        "view": "exam_list",
        "action": "answer_mapping_summary",
        "total_exams": len(exams_with_status),
        "complete": complete_count,
        "partial": partial_count,
        "not_started": not_started_count
    }
    logger.info(f"[EXAM_LIST_SUMMARY] {json.dumps(console_log)}")
    
    return render(request, 'primepath_routinetest/exam_list.html', {
        'exams': exams_with_status,
        'mapping_summary': {
            'total': len(exams_with_status),
            'complete': complete_count,
            'partial': partial_count,
            'not_started': not_started_count
        }
    })


@handle_errors(ajax_only=True)
@login_required
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
@handle_errors(template_name='primepath_routinetest/create_exam.html')
def create_exam(request):
    """Create a new exam (requires authentication)"""
    # Get Teacher profile for the authenticated user
    teacher_profile = None
    if request.user.is_authenticated:
        try:
            teacher_profile = request.user.teacher_profile
            console_log = {
                "view": "create_exam",
                "action": "teacher_profile_found",
                "user": str(request.user),
                "teacher_id": teacher_profile.id,
                "teacher_name": teacher_profile.name,
                "is_head_teacher": teacher_profile.is_head_teacher
            }
            logger.info(f"[CREATE_EXAM_TEACHER] {json.dumps(console_log)}")
            print(f"[CREATE_EXAM_TEACHER] {json.dumps(console_log)}")
        except AttributeError as e:
            # Handle case where teacher_profile doesn't exist
            # Create a Teacher profile on-the-fly for authenticated users
            from core.models import Teacher
            teacher_profile = Teacher.objects.create(
                user=request.user,
                name=request.user.get_full_name() or request.user.username,
                email=request.user.email or f"{request.user.username}@example.com",
                is_head_teacher=request.user.is_superuser
            )
            console_log = {
                "view": "create_exam",
                "action": "teacher_profile_created",
                "user": str(request.user),
                "teacher_id": teacher_profile.id,
                "teacher_name": teacher_profile.name,
                "reason": "Profile did not exist, created automatically"
            }
            logger.warning(f"[CREATE_EXAM_TEACHER_CREATED] {json.dumps(console_log)}")
            print(f"[CREATE_EXAM_TEACHER_CREATED] {json.dumps(console_log)}")
    
    # Log authentication check
    console_log = {
        "view": "create_exam",
        "user": str(request.user),
        "authenticated": request.user.is_authenticated,
        "has_teacher_profile": teacher_profile is not None,
        "teacher_id": teacher_profile.id if teacher_profile else None,
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
            
            # Get auto-generation components (for logging)
            generated_base_name = request.POST.get('generated_base_name', '')
            user_comment = request.POST.get('user_comment', '')
            
            # Log the auto-generated name components
            console_log = {
                "view": "create_exam",
                "action": "auto_name_received",
                "full_name": exam_name,
                "base_name": generated_base_name,
                "user_comment": user_comment,
                "has_comment": bool(user_comment),
                "timestamp": timezone.now().isoformat()
            }
            logger.info(f"[AUTO_NAME_GEN_BACKEND] {json.dumps(console_log)}")
            print(f"[AUTO_NAME_GEN_BACKEND] {json.dumps(console_log)}")
            
            total_questions = request.POST.get('total_questions')
            if not total_questions:
                raise ValidationException("Total number of questions is required", code="MISSING_QUESTIONS")
            
            # Get exam type from form
            exam_type = request.POST.get('exam_type', 'REVIEW')
            
            # Phase 2: Get time period fields based on exam type
            time_period_month = None
            time_period_quarter = None
            academic_year = request.POST.get('academic_year', '').strip() or None
            
            if exam_type == 'REVIEW':
                time_period_month = request.POST.get('time_period_month', '').strip() or None
            elif exam_type == 'QUARTERLY':
                time_period_quarter = request.POST.get('time_period_quarter', '').strip() or None
            
            
            # Phase 3: Get selected class codes
            class_codes = request.POST.getlist('class_codes[]')  # Get array of selected class codes
            
            # Get general instructions (kept at exam level)
            instructions = request.POST.get('instructions', '').strip()
            # Note: Scheduling is now handled per-class via ClassExamSchedule
            
            # Log exam creation attempt with all phases data
            console_log = {
                "view": "create_exam",
                "action": "exam_creation_attempt",
                "exam_name": exam_name,
                "exam_type": exam_type,
                "time_period_month": time_period_month,
                "time_period_quarter": time_period_quarter,
                "academic_year": academic_year,
                "class_codes": class_codes,  # Phase 3: Log selected classes
                "class_codes_count": len(class_codes),
                "has_instructions": bool(instructions),
                "total_questions": total_questions,
                "created_by_teacher_id": teacher_profile.id if teacher_profile else None,
                "created_by_teacher_name": teacher_profile.name if teacher_profile else None,
                "note": "Class-specific scheduling will be set separately after exam creation"
            }
            logger.info(f"[CREATE_EXAM_ATTEMPT] {json.dumps(console_log)}")
            print(f"[CREATE_EXAM_ATTEMPT] {json.dumps(console_log)}")
            
            # Prepare exam data with validation
            exam_data = {
                'name': exam_name,
                'exam_type': exam_type,  # Add exam type to data
                'time_period_month': time_period_month,  # Phase 2: Add month
                'time_period_quarter': time_period_quarter,  # Phase 2: Add quarter
                'academic_year': academic_year,  # Phase 2: Add academic year
                'class_codes': class_codes,  # Phase 3: Add selected class codes
                'instructions': instructions,  # General instructions (kept at exam level)
                'curriculum_level_id': request.POST.get('curriculum_level', '').strip() or None,
                'timer_minutes': int(request.POST.get('timer_minutes', 60)),
                'total_questions': int(total_questions),
                'default_options_count': int(request.POST.get('default_options_count', 5)),
                'passing_score': 0,
                'pdf_rotation': int(request.POST.get('pdf_rotation', 0)),  # Add rotation from form
                'created_by': teacher_profile,  # Use Teacher instance, not User instance
                'is_active': True
            }
            
            # Validate PDF file
            pdf_file = request.FILES.get('pdf_file')
            if not pdf_file:
                raise ValidationException("PDF file is required", code="MISSING_PDF")
            
            # Log the file upload details
            console_log = {
                "view": "create_exam",
                "action": "file_upload_details",
                "pdf_file_name": pdf_file.name if pdf_file else None,
                "pdf_file_size": pdf_file.size if pdf_file else 0,
                "pdf_file_content_type": pdf_file.content_type if pdf_file else None,
                "audio_files_count": len(request.FILES.getlist('audio_files')),
                "audio_names_count": len(request.POST.getlist('audio_names[]'))
            }
            logger.info(f"[CREATE_EXAM_FILES] {json.dumps(console_log)}")
            print(f"[CREATE_EXAM_FILES] {json.dumps(console_log)}")
            
            # Use ExamService to create exam with files
            exam = ExamService.create_exam(
                exam_data=exam_data,
                pdf_file=pdf_file,
                audio_files=request.FILES.getlist('audio_files'),
                audio_names=request.POST.getlist('audio_names[]')
            )
            
            # Log successful exam creation
            console_log = {
                "view": "create_exam",
                "action": "exam_created_successfully",
                "exam_id": str(exam.id),
                "exam_name": exam.name,
                "exam_type": exam.exam_type,
                "created_by_teacher_id": exam.created_by.id if exam.created_by else None,
                "created_by_teacher_name": exam.created_by.name if exam.created_by else None,
                "total_questions": exam.total_questions,
                "pdf_file": exam.pdf_file.name if exam.pdf_file else None
            }
            logger.info(f"[CREATE_EXAM_SUCCESS] {json.dumps(console_log)}")
            print(f"[CREATE_EXAM_SUCCESS] {json.dumps(console_log)}")
            
            messages.success(request, f'Exam "{exam.name}" uploaded successfully!')
            return redirect('RoutineTest:create_exam')
            
        except ValueError as e:
            console_log = {
                "view": "create_exam",
                "action": "value_error",
                "error": str(e),
                "user": str(request.user)
            }
            logger.error(f"[CREATE_EXAM_ERROR] {json.dumps(console_log)}")
            print(f"[CREATE_EXAM_ERROR] {json.dumps(console_log)}")
            messages.error(request, f"Invalid input: {str(e)}")
            # Fall through to render the form again with error message
        except ValidationException as e:
            console_log = {
                "view": "create_exam",
                "action": "validation_error",
                "error_code": e.code if hasattr(e, 'code') else None,
                "error_message": e.message if hasattr(e, 'message') else str(e),
                "user": str(request.user)
            }
            logger.error(f"[CREATE_EXAM_VALIDATION_ERROR] {json.dumps(console_log)}")
            print(f"[CREATE_EXAM_VALIDATION_ERROR] {json.dumps(console_log)}")
            messages.error(request, e.message if hasattr(e, 'message') else str(e))
            # Fall through to render the form again with error message
        except Exception as e:
            console_log = {
                "view": "create_exam",
                "action": "unexpected_error",
                "error_type": type(e).__name__,
                "error": str(e),
                "user": str(request.user)
            }
            logger.exception(f"[CREATE_EXAM_UNEXPECTED_ERROR] {json.dumps(console_log)}")
            print(f"[CREATE_EXAM_UNEXPECTED_ERROR] {json.dumps(console_log)}")
            messages.error(request, f"An unexpected error occurred: {str(e)}")
            # Fall through to render the form again with error message
    
    # Get RoutineTest curriculum levels using ExamService
    # This uses the ROUTINETEST_CURRICULUM_WHITELIST from constants.py
    from datetime import datetime
    
    # Log curriculum levels retrieval start
    console_log = {
        "view": "create_exam",
        "action": "getting_routinetest_curriculum_levels",
        "message": "Using ExamService to get filtered RoutineTest curriculum levels"
    }
    logger.info(f"[CREATE_EXAM_CURRICULUM] {json.dumps(console_log)}")
    print(f"[CREATE_EXAM_CURRICULUM] {json.dumps(console_log)}")
    
    # Get RoutineTest curriculum levels from ExamService
    curriculum_levels_data = ExamService.get_routinetest_curriculum_levels()
    
    # Get today's date for version checking
    today_str = datetime.now().strftime('%y%m%d')
    
    # Add version info to each level for RoutineTest naming
    levels_with_versions = []
    for level_data in curriculum_levels_data:
        curriculum_level = level_data['curriculum_level']
        
        # Check if there are existing uploads today for this level
        next_version = ExamService.get_next_version_number(curriculum_level.id, today_str)
        
        # Get count of existing exams for this level (for info display)
        existing_count = Exam.objects.filter(curriculum_level=curriculum_level).count()
        
        # Create RoutineTest specific display name using [RT]/[QTR] format
        # Format: "[RT/QTR] - [Time Period] - PROGRAM SUBPROGRAM Level X"
        rt_display_name = level_data['routinetest_display_preview']
        
        # Clean base name for file generation (used in exam name)
        # Format: "PROGRAM_SUBPROGRAM_LvX"
        program_name = level_data['program_name']
        subprogram_name = level_data['subprogram_name']
        level_number = level_data['level_number']
        rt_base_name = f"{program_name}_{subprogram_name}_Lv{level_number}".replace(" ", "_")
        
        levels_with_versions.append({
            'id': curriculum_level.id,
            'display_name': rt_display_name,  # Use RT-specific display name
            'exam_base_name': rt_base_name,  # Use RT-specific base name
            'next_version': next_version,
            'existing_count': existing_count,
            'date_str': today_str,
            'program_name': program_name,
            'subprogram_name': subprogram_name,
            'level_number': level_number
        })
        
        # Log each level being added
        console_log = {
            "view": "create_exam",
            "action": "routinetest_level_added",
            "level_id": curriculum_level.id,
            "rt_display_name": rt_display_name,
            "rt_base_name": rt_base_name,
            "existing_count": existing_count
        }
        logger.debug(f"[CREATE_EXAM_RT_LEVEL] {json.dumps(console_log)}")
        print(f"[CREATE_EXAM_RT_LEVEL] {json.dumps(console_log)}")
    
    # Log final results
    console_log = {
        "view": "create_exam",
        "action": "routinetest_curriculum_levels_loaded",
        "total_levels": len(levels_with_versions),
        "programs": list(set(level['program_name'] for level in levels_with_versions))
    }
    logger.info(f"[CREATE_EXAM_RT_FINAL] {json.dumps(console_log)}")
    print(f"[CREATE_EXAM_RT_FINAL] {json.dumps(console_log)}")
    
    return render(request, 'primepath_routinetest/create_exam.html', {
        'curriculum_levels': levels_with_versions
    })


@login_required
def exam_detail(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = exam.routine_questions.all()
    audio_files = exam.audio_files.all()
    
    context = {
        'exam': exam,
        'questions': questions,
        'audio_files': audio_files,
    }
    return render(request, 'primepath_routinetest/exam_detail.html', context)


@login_required
def edit_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    return render(request, 'primepath_routinetest/edit_exam.html', {'exam': exam})


@login_required
def preview_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    
    # Get or create questions for the exam with audio files prefetched
    questions = exam.routine_questions.select_related('audio_file').all().order_by('question_number')
    
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
        questions = exam.routine_questions.all().order_by('question_number')
    
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
    
    return render(request, 'primepath_routinetest/preview_and_answers.html', {
        'exam': exam,
        'questions': questions,
        'audio_files': audio_files,
    })


@login_required
def manage_questions(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = exam.routine_questions.all().order_by('question_number')
    
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
        return redirect('RoutineTest:manage_questions', exam_id=exam_id)
    
    return render(request, 'primepath_routinetest/manage_questions.html', {
        'exam': exam,
        'questions': questions,
    })


@require_http_methods(["POST"])
@login_required
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
    
    return redirect('RoutineTest:exam_list')
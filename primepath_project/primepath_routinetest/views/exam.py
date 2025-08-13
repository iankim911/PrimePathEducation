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
    
    # Fetch exams with related data and prefetch questions for answer mapping check
    exams = Exam.objects.select_related(
        'curriculum_level__subprogram__program'
    ).prefetch_related(
        'questions',  # Prefetch questions to avoid N+1 queries
        'audio_files'  # Also prefetch audio files for display
    ).all()
    
    # Add answer mapping status to each exam
    exams_with_status = []
    for exam in exams:
        # Get answer mapping status
        mapping_status = exam.get_answer_mapping_status()
        
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
            "status": mapping_status['status_label']
        }
        logger.info(f"[EXAM_LIST_MAPPING] {json.dumps(console_log)}")
        
        # Add the status to the exam object for template access
        exam.answer_mapping_status = mapping_status
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
            
            total_questions = request.POST.get('total_questions')
            if not total_questions:
                raise ValidationException("Total number of questions is required", code="MISSING_QUESTIONS")
            
            # Log exam creation attempt
            console_log = {
                "view": "create_exam",
                "action": "exam_creation_attempt",
                "exam_name": exam_name,
                "total_questions": total_questions,
                "created_by_teacher_id": teacher_profile.id if teacher_profile else None,
                "created_by_teacher_name": teacher_profile.name if teacher_profile else None
            }
            logger.info(f"[CREATE_EXAM_ATTEMPT] {json.dumps(console_log)}")
            print(f"[CREATE_EXAM_ATTEMPT] {json.dumps(console_log)}")
            
            # Prepare exam data with validation
            exam_data = {
                'name': exam_name,
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
                "created_by_teacher_id": exam.created_by.id if exam.created_by else None,
                "created_by_teacher_name": exam.created_by.name if exam.created_by else None,
                "total_questions": exam.total_questions,
                "pdf_file": exam.pdf_file.name if exam.pdf_file else None
            }
            logger.info(f"[CREATE_EXAM_SUCCESS] {json.dumps(console_log)}")
            print(f"[CREATE_EXAM_SUCCESS] {json.dumps(console_log)}")
            
            messages.success(request, f'Exam "{exam.name}" uploaded successfully!')
            return redirect('primepath_routinetest:create_exam')
            
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
    
    # Get curriculum levels with version info
    from datetime import datetime
    
    # Define whitelist of allowed placement test curriculum levels
    # Format: (program_name, subprogram_name, level_number)
    # IMPORTANT: SubProgram names must match EXACTLY what's in the database
    # Database stores: 'Phonics', 'Sigma', 'Elite' (WITHOUT program prefix)
    # Updated: 2025-08-13 - Fixed to match actual database values
    PLACEMENT_TEST_WHITELIST = [
        # CORE Program - SubProgram names WITHOUT 'CORE' prefix
        ('CORE', 'Phonics', 1), ('CORE', 'Phonics', 2), ('CORE', 'Phonics', 3),
        ('CORE', 'Sigma', 1), ('CORE', 'Sigma', 2), ('CORE', 'Sigma', 3),
        ('CORE', 'Elite', 1), ('CORE', 'Elite', 2), ('CORE', 'Elite', 3),
        ('CORE', 'Pro', 1), ('CORE', 'Pro', 2), ('CORE', 'Pro', 3),
        # ASCENT Program - SubProgram names WITHOUT 'ASCENT' prefix
        ('ASCENT', 'Nova', 1), ('ASCENT', 'Nova', 2), ('ASCENT', 'Nova', 3),
        ('ASCENT', 'Drive', 1), ('ASCENT', 'Drive', 2), ('ASCENT', 'Drive', 3),
        ('ASCENT', 'Flex', 1), ('ASCENT', 'Flex', 2), ('ASCENT', 'Flex', 3),  # Added Flex
        ('ASCENT', 'Pro', 1), ('ASCENT', 'Pro', 2), ('ASCENT', 'Pro', 3),
        # EDGE Program - SubProgram names WITHOUT 'EDGE' prefix
        ('EDGE', 'Spark', 1), ('EDGE', 'Spark', 2), ('EDGE', 'Spark', 3),
        ('EDGE', 'Rise', 1), ('EDGE', 'Rise', 2), ('EDGE', 'Rise', 3),
        ('EDGE', 'Pursuit', 1), ('EDGE', 'Pursuit', 2), ('EDGE', 'Pursuit', 3),
        ('EDGE', 'Pro', 1), ('EDGE', 'Pro', 2), ('EDGE', 'Pro', 3),
        # PINNACLE Program - SubProgram names WITHOUT 'PINNACLE' prefix
        ('PINNACLE', 'Vision', 1), ('PINNACLE', 'Vision', 2),
        ('PINNACLE', 'Endeavor', 1), ('PINNACLE', 'Endeavor', 2),
        ('PINNACLE', 'Success', 1), ('PINNACLE', 'Success', 2),
        ('PINNACLE', 'Pro', 1), ('PINNACLE', 'Pro', 2),
    ]
    
    # Log whitelist configuration
    console_log = {
        "view": "create_exam",
        "action": "whitelist_configured",
        "total_allowed_levels": len(PLACEMENT_TEST_WHITELIST),
        "programs": list(set(item[0] for item in PLACEMENT_TEST_WHITELIST))
    }
    logger.info(f"[CREATE_EXAM_WHITELIST] {json.dumps(console_log)}")
    print(f"[CREATE_EXAM_WHITELIST] {json.dumps(console_log)}")
    
    # Get all curriculum levels but filter to whitelist
    all_levels = CurriculumLevel.objects.select_related('subprogram__program').all()
    curriculum_levels = []
    
    # Enhanced debugging for whitelist filtering
    debug_samples = []
    rejected_samples = []
    
    for level in all_levels:
        # Check if this level is in the whitelist
        program_name = level.subprogram.program.name
        subprogram_name = level.subprogram.name
        level_number = level.level_number
        
        # Create tuple for checking
        level_tuple = (program_name, subprogram_name, level_number)
        
        # Log first few samples for debugging
        if len(debug_samples) < 5:
            debug_samples.append({
                "program": program_name,
                "subprogram": subprogram_name,
                "level": level_number,
                "tuple": str(level_tuple)
            })
        
        if level_tuple in PLACEMENT_TEST_WHITELIST:
            curriculum_levels.append(level)
            # Log successful match
            logger.debug(f"[WHITELIST_MATCH] ✅ Matched: {level_tuple}")
        else:
            # Track rejected items for debugging
            if len(rejected_samples) < 5 and '[INACTIVE]' not in subprogram_name and 'Test' not in subprogram_name:
                rejected_samples.append({
                    "program": program_name,
                    "subprogram": subprogram_name,
                    "level": level_number,
                    "reason": "Not in whitelist"
                })
                logger.debug(f"[WHITELIST_REJECT] ❌ Rejected: {level_tuple}")
    
    # Comprehensive logging of filtering results
    console_log = {
        "view": "create_exam",
        "action": "levels_filtered",
        "total_levels_in_db": all_levels.count(),
        "levels_after_filter": len(curriculum_levels),
        "filtered_programs": list(set(level.subprogram.program.name for level in curriculum_levels)),
        "sample_db_levels": debug_samples,
        "sample_rejected": rejected_samples,
        "whitelist_size": len(PLACEMENT_TEST_WHITELIST)
    }
    logger.info(f"[CREATE_EXAM_FILTER] {json.dumps(console_log)}")
    print(f"[CREATE_EXAM_FILTER] {json.dumps(console_log)}")
    
    # Additional console warning if no levels passed filter
    if len(curriculum_levels) == 0:
        console_error = {
            "view": "create_exam",
            "action": "ERROR_NO_LEVELS",
            "error": "No curriculum levels passed whitelist filter!",
            "check_whitelist": "Verify PLACEMENT_TEST_WHITELIST matches database values",
            "sample_from_db": debug_samples[:3] if debug_samples else []
        }
        logger.error(f"[CREATE_EXAM_ERROR] {json.dumps(console_error)}")
        print(f"[CREATE_EXAM_ERROR] {json.dumps(console_error)}")
    
    # Get today's date for checking same-day uploads
    today_str = datetime.now().strftime('%y%m%d')
    
    # Add version info to each level using new naming convention
    levels_with_versions = []
    for level in curriculum_levels:
        # Check if there are existing uploads today for this level
        next_version = ExamService.get_next_version_number(level.id, today_str)
        
        # Get count of existing exams for this level (for info display)
        existing_count = Exam.objects.filter(curriculum_level=level).count()
        
        # Create placement test specific display name
        # Format: "[PT] PROGRAM, SUBPROGRAM, Level X"
        program_name = level.subprogram.program.name
        subprogram_name = level.subprogram.name
        level_number = level.level_number
        
        # Remove program prefix from subprogram name if it exists
        # e.g., "CORE PHONICS" -> "Phonics"
        clean_subprogram = subprogram_name
        if subprogram_name.startswith(program_name + ' '):
            clean_subprogram = subprogram_name[len(program_name) + 1:]
        
        # Clean display name for placement tests (no "SubProgram" text)
        pt_display_name = f"[PT] {program_name}, {clean_subprogram}, Level {level_number}"
        
        # Clean base name for file generation (used in exam name)
        # Format: "PROGRAM_SUBPROGRAM_LvX"
        pt_base_name = f"{program_name}_{clean_subprogram}_Lv{level_number}".replace(" ", "_")
        
        levels_with_versions.append({
            'id': level.id,
            'display_name': pt_display_name,  # Use PT-specific display name
            'exam_base_name': pt_base_name,  # Use PT-specific base name
            'next_version': next_version,
            'existing_count': existing_count,
            'date_str': today_str
        })
        
        # Log each level being added
        console_log = {
            "view": "create_exam",
            "action": "level_added",
            "level_id": level.id,
            "pt_display_name": pt_display_name,
            "pt_base_name": pt_base_name,
            "existing_count": existing_count
        }
        logger.debug(f"[CREATE_EXAM_LEVEL] {json.dumps(console_log)}")
        print(f"[CREATE_EXAM_LEVEL] {json.dumps(console_log)}")
    
    return render(request, 'primepath_routinetest/create_exam.html', {
        'curriculum_levels': levels_with_versions
    })


@login_required
def exam_detail(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = exam.questions.all()
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
    
    return render(request, 'primepath_routinetest/preview_and_answers.html', {
        'exam': exam,
        'questions': questions,
        'audio_files': audio_files,
    })


@login_required
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
        return redirect('primepath_routinetest:manage_questions', exam_id=exam_id)
    
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
    
    return redirect('primepath_routinetest:exam_list')
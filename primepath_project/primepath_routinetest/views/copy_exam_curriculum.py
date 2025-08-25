"""
Copy Exam with Curriculum Level Selection - FIXED VERSION
This module handles copying exams based on curriculum level selection
FIXED: Only uses Exam model, not RoutineExam (which lacks required fields)
"""
import json
import logging
import uuid
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from core.models import CurriculumLevel
from ..models import Exam

logger = logging.getLogger(__name__)

@login_required
@require_http_methods(["POST"])
@csrf_protect
def copy_exam_with_curriculum(request):
    """
    Copy an exam with curriculum level selection.
    This endpoint is specifically designed for the Copy Exam modal that uses curriculum dropdowns.
    
    FIXED VERSION:
    - Only works with Exam model (not RoutineExam)
    - Properly handles all required fields including default_options_count
    - Extensive logging for debugging
    - Proper error handling and recovery
    """
    log_prefix = "[COPY_EXAM_FIXED]"
    
    try:
        # Parse request data
        data = json.loads(request.body)
        
        # COMPREHENSIVE DEBUG LOGGING
        logger.info(f"{log_prefix} ============================================")
        logger.info(f"{log_prefix} COPY EXAM REQUEST RECEIVED")
        logger.info(f"{log_prefix} ============================================")
        logger.info(f"{log_prefix} Request User: {request.user.username}")
        logger.info(f"{log_prefix} Request Data: {json.dumps(data, indent=2)}")
        
        # Console output for real-time debugging
        print(f"\n{'='*80}")
        print(f"{log_prefix} COPY EXAM REQUEST")
        print(f"{'='*80}")
        print(f"User: {request.user.username}")
        print(f"Data received:")
        for key, value in data.items():
            print(f"  {key}: {value}")
        print(f"{'='*80}\n")
        
        # Extract parameters
        source_exam_id = data.get('source_exam_id')
        curriculum_level_id = data.get('curriculum_level_id')
        custom_suffix = data.get('custom_suffix', '').strip()
        
        # Additional parameters that might be sent
        exam_type = data.get('exam_type')
        time_slot = data.get('timeslot')
        academic_year = data.get('academic_year')
        
        # Validate required fields
        if not source_exam_id:
            error_msg = "Missing source_exam_id"
            logger.error(f"{log_prefix} {error_msg}")
            print(f"{log_prefix} ERROR: {error_msg}")
            return JsonResponse({
                'success': False, 
                'error': error_msg,
                'details': 'No source exam ID provided in request'
            }, status=400)
        
        if not curriculum_level_id:
            error_msg = "Missing curriculum_level_id"
            logger.error(f"{log_prefix} {error_msg}")
            print(f"{log_prefix} ERROR: {error_msg}")
            return JsonResponse({
                'success': False, 
                'error': error_msg,
                'details': 'No curriculum level selected'
            }, status=400)
        
        # CRITICAL FIX: Only search in Exam model, NOT RoutineExam
        logger.info(f"{log_prefix} Searching for exam ID: {source_exam_id} in Exam model ONLY")
        print(f"{log_prefix} Looking up exam: {source_exam_id}")
        
        try:
            # Use ONLY the Exam model - this is what's displayed in the UI
            source_exam = Exam.objects.select_related(
                'curriculum_level__subprogram__program',
                'created_by'
            ).prefetch_related(
                'routine_questions',
                'routine_audio_files'
            ).get(id=source_exam_id)
            
            logger.info(f"{log_prefix} ✅ Found source exam: {source_exam.name}")
            print(f"{log_prefix} ✅ Found exam: {source_exam.name}")
            
            # Log exam details for debugging
            exam_details = {
                'id': str(source_exam.id),
                'name': source_exam.name,
                'exam_type': source_exam.exam_type,
                'timer_minutes': source_exam.timer_minutes,
                'total_questions': source_exam.total_questions,
                'default_options_count': source_exam.default_options_count,
                'has_pdf': bool(source_exam.pdf_file),
                'questions_count': source_exam.routine_questions.count(),
                'audio_files_count': source_exam.routine_audio_files.count()
            }
            logger.info(f"{log_prefix} Source exam details: {json.dumps(exam_details, indent=2)}")
            print(f"{log_prefix} Exam details:")
            for key, value in exam_details.items():
                print(f"  {key}: {value}")
                
        except Exam.DoesNotExist:
            error_msg = f"Source exam not found: {source_exam_id}"
            logger.error(f"{log_prefix} {error_msg}")
            print(f"{log_prefix} ❌ ERROR: Exam not found in database")
            
            # Debug: Check what exams exist
            existing_count = Exam.objects.count()
            logger.error(f"{log_prefix} Total exams in database: {existing_count}")
            
            return JsonResponse({
                'success': False, 
                'error': 'Exam not found',
                'details': f'The exam with ID {source_exam_id} does not exist in the database',
                'debug_info': {
                    'searched_id': source_exam_id,
                    'total_exams_in_db': existing_count
                }
            }, status=404)
        
        # Get curriculum level
        logger.info(f"{log_prefix} Looking up curriculum level: {curriculum_level_id}")
        try:
            curriculum_level = CurriculumLevel.objects.select_related(
                'subprogram__program'
            ).get(id=curriculum_level_id)
            
            # Extract program and subprogram names
            program_name = curriculum_level.subprogram.program.name if curriculum_level.subprogram and curriculum_level.subprogram.program else "Unknown"
            subprogram_name = curriculum_level.subprogram.name if curriculum_level.subprogram else "Unknown"
            
            logger.info(f"{log_prefix} ✅ Found curriculum level: {program_name} {subprogram_name} Level {curriculum_level.level_number}")
            print(f"{log_prefix} ✅ Curriculum: {program_name} {subprogram_name} Level {curriculum_level.level_number}")
            
        except CurriculumLevel.DoesNotExist:
            error_msg = f"Curriculum level not found: {curriculum_level_id}"
            logger.error(f"{log_prefix} {error_msg}")
            print(f"{log_prefix} ❌ ERROR: Curriculum level not found")
            return JsonResponse({
                'success': False, 
                'error': 'Curriculum level not found',
                'details': f'The selected curriculum level does not exist'
            }, status=404)
        
        # Generate new exam name based on curriculum
        base_name = f"{program_name} {subprogram_name} Level {curriculum_level.level_number}"
        
        # Determine exam type for naming
        exam_type_label = "Review"
        if hasattr(source_exam, 'exam_type'):
            if source_exam.exam_type == 'QUARTERLY':
                exam_type_label = "Quarterly"
            elif source_exam.exam_type == 'REVIEW':
                exam_type_label = "Review"
        
        # Create the new exam name
        new_exam_name = f"{base_name} - {exam_type_label} {timezone.now().year}"
        if custom_suffix:
            new_exam_name = f"{new_exam_name} ({custom_suffix})"
        
        logger.info(f"{log_prefix} Generated new exam name: {new_exam_name}")
        print(f"{log_prefix} New exam name: {new_exam_name}")
        
        # CREATE THE COPY - Using transaction for data integrity
        with transaction.atomic():
            try:
                logger.info(f"{log_prefix} Creating exam copy...")
                print(f"{log_prefix} Creating copy...")
                
                # Create new exam with ALL required fields
                new_exam = Exam.objects.create(
                    id=uuid.uuid4(),
                    name=new_exam_name,
                    curriculum_level=curriculum_level,
                    
                    # Copy exam type and time period fields
                    exam_type=source_exam.exam_type,
                    time_period_month=source_exam.time_period_month,
                    time_period_quarter=source_exam.time_period_quarter,
                    academic_year=academic_year or source_exam.academic_year or str(timezone.now().year),
                    
                    # Copy configuration fields - INCLUDING default_options_count!
                    timer_minutes=source_exam.timer_minutes,
                    total_questions=source_exam.total_questions,
                    default_options_count=source_exam.default_options_count,  # CRITICAL FIELD
                    passing_score=source_exam.passing_score,
                    pdf_rotation=source_exam.pdf_rotation,
                    
                    # Copy other fields
                    instructions=source_exam.instructions,
                    class_code=source_exam.class_code,  # Keep same class code initially
                    
                    # Set creator
                    created_by=request.user.teacher_profile if hasattr(request.user, 'teacher_profile') else None,
                    
                    # Set as active
                    is_active=True
                )
                
                # Copy PDF file if exists
                if source_exam.pdf_file:
                    new_exam.pdf_file = source_exam.pdf_file
                    new_exam.save()
                    logger.info(f"{log_prefix} Copied PDF file")
                    print(f"{log_prefix} ✅ Copied PDF file")
                
                # Copy questions
                questions_copied = 0
                for source_question in source_exam.routine_questions.all():
                    # Create new question (don't modify the original)
                    new_question = source_question
                    new_question.pk = None  # Reset primary key
                    new_question.id = uuid.uuid4()
                    new_question.exam = new_exam
                    new_question.save()
                    questions_copied += 1
                
                logger.info(f"{log_prefix} Copied {questions_copied} questions")
                print(f"{log_prefix} ✅ Copied {questions_copied} questions")
                
                # Copy audio files
                audio_files_copied = 0
                for source_audio in source_exam.routine_audio_files.all():
                    new_audio = source_audio
                    new_audio.pk = None
                    new_audio.id = uuid.uuid4()
                    new_audio.exam = new_exam
                    new_audio.save()
                    audio_files_copied += 1
                
                if audio_files_copied > 0:
                    logger.info(f"{log_prefix} Copied {audio_files_copied} audio files")
                    print(f"{log_prefix} ✅ Copied {audio_files_copied} audio files")
                
                # SUCCESS - Log the complete details
                success_details = {
                    'new_exam_id': str(new_exam.id),
                    'new_exam_name': new_exam.name,
                    'curriculum': f"{program_name} {subprogram_name} Level {curriculum_level.level_number}",
                    'exam_type': new_exam.exam_type,
                    'questions_copied': questions_copied,
                    'audio_files_copied': audio_files_copied,
                    'created_by': str(new_exam.created_by) if new_exam.created_by else 'System'
                }
                
                logger.info(f"{log_prefix} ============================================")
                logger.info(f"{log_prefix} COPY SUCCESS!")
                logger.info(f"{log_prefix} Details: {json.dumps(success_details, indent=2)}")
                logger.info(f"{log_prefix} ============================================")
                
                print(f"\n{'='*80}")
                print(f"{log_prefix} ✅ COPY SUCCESSFUL!")
                print(f"{'='*80}")
                print(f"New exam ID: {new_exam.id}")
                print(f"New exam name: {new_exam.name}")
                print(f"Questions: {questions_copied}")
                print(f"Audio files: {audio_files_copied}")
                print(f"{'='*80}\n")
                
                # Return success response
                return JsonResponse({
                    'success': True,
                    'new_exam_id': str(new_exam.id),
                    'new_exam_name': new_exam.name,
                    'message': f'Exam copied successfully as "{new_exam.name}"',
                    'details': success_details
                })
                
            except Exception as e:
                # Transaction will rollback automatically
                error_msg = f"Failed to create exam copy: {str(e)}"
                logger.error(f"{log_prefix} {error_msg}", exc_info=True)
                print(f"{log_prefix} ❌ ERROR during copy: {str(e)}")
                
                # Check if it's the default_options_count error
                if 'default_options_count' in str(e):
                    return JsonResponse({
                        'success': False, 
                        'error': 'Failed to copy exam - missing required field',
                        'details': 'The exam is missing the default_options_count field. This is a data integrity issue.',
                        'technical_details': str(e)
                    }, status=500)
                
                return JsonResponse({
                    'success': False, 
                    'error': 'Failed to create exam copy',
                    'details': str(e)
                }, status=500)
        
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON data: {str(e)}"
        logger.error(f"{log_prefix} {error_msg}")
        print(f"{log_prefix} ❌ ERROR: Invalid JSON")
        return JsonResponse({
            'success': False, 
            'error': 'Invalid request data',
            'details': 'The request body is not valid JSON'
        }, status=400)
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"{log_prefix} {error_msg}", exc_info=True)
        print(f"{log_prefix} ❌ UNEXPECTED ERROR: {str(e)}")
        return JsonResponse({
            'success': False, 
            'error': 'An unexpected error occurred',
            'details': str(e)
        }, status=500)
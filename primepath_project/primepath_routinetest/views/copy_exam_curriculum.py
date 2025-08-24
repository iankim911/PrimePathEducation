"""
Copy Exam with Curriculum Level Selection
This module handles copying exams based on curriculum level selection
"""
import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils import timezone
from core.models import CurriculumLevel
from ..models import Exam, RoutineExam
import uuid

logger = logging.getLogger(__name__)

@login_required
@require_http_methods(["POST"])
@csrf_protect
def copy_exam_with_curriculum(request):
    """
    Copy an exam with curriculum level selection.
    This endpoint is specifically designed for the Copy Exam modal that uses curriculum dropdowns.
    """
    log_prefix = "[COPY_EXAM_CURRICULUM]"
    
    try:
        # Parse request data
        data = json.loads(request.body)
        logger.info(f"{log_prefix} Request received: {data}")
        print(f"{log_prefix} ============================================")
        print(f"{log_prefix} COPY EXAM REQUEST RECEIVED")
        print(f"{log_prefix} ============================================")
        print(f"{log_prefix} Data: {json.dumps(data, indent=2)}")
        
        # Extract parameters
        source_exam_id = data.get('source_exam_id')
        curriculum_level_id = data.get('curriculum_level_id')
        custom_suffix = data.get('custom_suffix', '').strip()
        
        # Validate required fields
        if not source_exam_id:
            error_msg = "Missing source_exam_id"
            logger.error(f"{log_prefix} {error_msg}")
            return JsonResponse({'success': False, 'error': error_msg}, status=400)
        
        if not curriculum_level_id:
            error_msg = "Missing curriculum_level_id"
            logger.error(f"{log_prefix} {error_msg}")
            return JsonResponse({'success': False, 'error': error_msg}, status=400)
        
        # Get source exam (try both models)
        source_exam = None
        exam_model_used = None
        
        # Try RoutineExam first
        try:
            from ..models.exam_management import RoutineExam
            source_exam = RoutineExam.objects.get(id=source_exam_id)
            exam_model_used = "RoutineExam"
            logger.info(f"{log_prefix} Found source exam in RoutineExam model")
        except (RoutineExam.DoesNotExist, ImportError):
            pass
        
        # Try regular Exam model if not found
        if not source_exam:
            try:
                source_exam = Exam.objects.get(id=source_exam_id)
                exam_model_used = "Exam"
                logger.info(f"{log_prefix} Found source exam in Exam model")
            except Exam.DoesNotExist:
                error_msg = f"Source exam not found: {source_exam_id}"
                logger.error(f"{log_prefix} {error_msg}")
                return JsonResponse({'success': False, 'error': error_msg}, status=404)
        
        print(f"{log_prefix} Source exam: {source_exam.name} (Model: {exam_model_used})")
        
        # Get curriculum level
        try:
            curriculum_level = CurriculumLevel.objects.get(id=curriculum_level_id)
            logger.info(f"{log_prefix} Found curriculum level: {curriculum_level}")
            # Access program through subprogram relationship
            program_name = curriculum_level.subprogram.program.name if curriculum_level.subprogram and curriculum_level.subprogram.program else "Unknown"
            subprogram_name = curriculum_level.subprogram.name if curriculum_level.subprogram else "Unknown"
            print(f"{log_prefix} Target curriculum: {program_name} {subprogram_name} Level {curriculum_level.level_number}")
        except CurriculumLevel.DoesNotExist:
            error_msg = f"Curriculum level not found: {curriculum_level_id}"
            logger.error(f"{log_prefix} {error_msg}")
            return JsonResponse({'success': False, 'error': error_msg}, status=404)
        
        # Generate new exam name based on curriculum
        program_name = curriculum_level.subprogram.program.name if curriculum_level.subprogram and curriculum_level.subprogram.program else "Unknown"
        subprogram_name = curriculum_level.subprogram.name if curriculum_level.subprogram else "Unknown"
        base_name = f"{program_name} {subprogram_name} Level {curriculum_level.level_number}"
        
        # Determine exam type from source
        exam_type = "Review"  # Default
        if hasattr(source_exam, 'exam_type'):
            if source_exam.exam_type == 'quarterly':
                exam_type = "Quarterly"
            elif source_exam.exam_type == 'monthly_review':
                exam_type = "Review"
        elif 'quarterly' in source_exam.name.lower():
            exam_type = "Quarterly"
        
        # Create the new exam name
        new_exam_name = f"{base_name} - {exam_type} {timezone.now().year}"
        if custom_suffix:
            new_exam_name = f"{new_exam_name} ({custom_suffix})"
        
        logger.info(f"{log_prefix} Generated new exam name: {new_exam_name}")
        print(f"{log_prefix} New exam name: {new_exam_name}")
        
        # Create the copy
        try:
            # Copy based on model type
            if exam_model_used == "RoutineExam":
                # Create RoutineExam copy
                from ..models.exam_management import RoutineExam as ExamModel
                new_exam = ExamModel.objects.create(
                    id=uuid.uuid4(),
                    name=new_exam_name,
                    exam_type=source_exam.exam_type if hasattr(source_exam, 'exam_type') else 'monthly_review',
                    academic_year=str(timezone.now().year),
                    time_period='',  # Will be set when assigned to class
                    created_by=request.user,
                    created_at=timezone.now(),
                    curriculum_level=curriculum_level,
                    # Copy other fields
                    total_questions=source_exam.total_questions if hasattr(source_exam, 'total_questions') else 0,
                    duration_minutes=source_exam.duration_minutes if hasattr(source_exam, 'duration_minutes') else 60,
                )
            else:
                # Create regular Exam copy
                new_exam = Exam.objects.create(
                    id=uuid.uuid4(),
                    name=new_exam_name,
                    exam_type=exam_type.lower(),
                    academic_year=str(timezone.now().year),
                    curriculum_level=curriculum_level,
                    # Copy fields from source
                    timer_minutes=source_exam.timer_minutes if hasattr(source_exam, 'timer_minutes') else 60,
                    passing_score=source_exam.passing_score if hasattr(source_exam, 'passing_score') else 70,
                )
                
                # Set created_by if user has teacher profile
                if hasattr(request.user, 'teacher_profile'):
                    new_exam.created_by = request.user.teacher_profile
                    new_exam.save()
            
            # Copy questions if they exist
            if hasattr(source_exam, 'questions'):
                for source_question in source_exam.questions.all():
                    # Create question copy
                    new_question = source_question
                    new_question.pk = None  # Reset primary key
                    new_question.id = uuid.uuid4()
                    new_question.exam = new_exam
                    new_question.save()
                    logger.info(f"{log_prefix} Copied question {source_question.question_number}")
            
            # Copy answer keys if they exist
            if hasattr(source_exam, 'answer_keys'):
                for answer_key in source_exam.answer_keys.all():
                    new_key = answer_key
                    new_key.pk = None
                    new_key.exam = new_exam
                    new_key.save()
                    logger.info(f"{log_prefix} Copied answer key for question {answer_key.question_number}")
            
            logger.info(f"{log_prefix} Successfully created exam copy: {new_exam.id}")
            print(f"{log_prefix} ============================================")
            print(f"{log_prefix} COPY SUCCESS!")
            print(f"{log_prefix} New exam ID: {new_exam.id}")
            print(f"{log_prefix} New exam name: {new_exam.name}")
            print(f"{log_prefix} ============================================")
            
            # Return success response
            return JsonResponse({
                'success': True,
                'new_exam_id': str(new_exam.id),
                'new_exam_name': new_exam.name,
                'message': f'Exam copied successfully as "{new_exam.name}"',
                'details': {
                    'curriculum': f"{program_name} {subprogram_name} Level {curriculum_level.level_number}",
                    'exam_type': exam_type,
                    'model_used': exam_model_used
                }
            })
            
        except Exception as e:
            error_msg = f"Failed to create exam copy: {str(e)}"
            logger.error(f"{log_prefix} {error_msg}", exc_info=True)
            print(f"{log_prefix} ERROR: {error_msg}")
            return JsonResponse({'success': False, 'error': error_msg}, status=500)
        
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON data: {str(e)}"
        logger.error(f"{log_prefix} {error_msg}")
        return JsonResponse({'success': False, 'error': error_msg}, status=400)
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"{log_prefix} {error_msg}", exc_info=True)
        return JsonResponse({'success': False, 'error': error_msg}, status=500)
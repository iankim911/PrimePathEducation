"""
AJAX views
Handles asynchronous requests from JavaScript frontend
"""
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from ..models import Exam, AudioFile, Question
from core.exceptions import ValidationException, AudioFileException
from core.decorators import handle_errors, teacher_required
from ..services import ExamService
import json
import logging

logger = logging.getLogger(__name__)


def add_audio(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    
    if request.method == 'POST':
        pass
    
    return JsonResponse({'success': False, 'message': 'Not implemented'})


@require_http_methods(["POST"])
def update_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    
    try:
        # Update basic fields
        question.correct_answer = request.POST.get('correct_answer', '')
        question.points = int(request.POST.get('points', 1))
        
        # Handle options_count update for MCQ/CHECKBOX questions
        if 'options_count' in request.POST:
            new_options_count = int(request.POST.get('options_count'))
            
            # Validate options_count range
            if not (2 <= new_options_count <= 10):
                return JsonResponse({
                    'success': False, 
                    'error': 'Options count must be between 2 and 10'
                })
            
            # For MCQ and CHECKBOX questions, validate that answers are within range
            if question.question_type in ['MCQ', 'CHECKBOX']:
                old_count = question.options_count
                
                # If reducing options, check if current answer is still valid
                if new_options_count < old_count and question.correct_answer:
                    # Get letter options based on new count
                    valid_letters = "ABCDEFGHIJ"[:new_options_count]
                    
                    if question.question_type == 'MCQ':
                        # Single answer - check if it's still valid
                        if question.correct_answer and question.correct_answer not in valid_letters:
                            return JsonResponse({
                                'success': False,
                                'error': f'Current answer "{question.correct_answer}" would be invalid with {new_options_count} options. Please update the answer first.',
                                'requires_answer_update': True
                            })
                    else:  # CHECKBOX
                        # Multiple answers - check each one
                        if question.correct_answer:
                            answers = [a.strip() for a in question.correct_answer.split(',')]
                            invalid_answers = [a for a in answers if a and a not in valid_letters]
                            if invalid_answers:
                                return JsonResponse({
                                    'success': False,
                                    'error': f'Answers {", ".join(invalid_answers)} would be invalid with {new_options_count} options. Please update the answer first.',
                                    'requires_answer_update': True
                                })
                
                # Set the options_count and bypass clean() method's auto-calculation
                question.options_count = new_options_count
            
            # For MIXED questions, validate MCQ components if they exist
            elif question.question_type == 'MIXED':
                # Check if MIXED question has MCQ components that would be affected
                if question.correct_answer:
                    try:
                        parsed = json.loads(question.correct_answer)
                        mcq_components = [comp for comp in parsed if comp.get('type') == 'Multiple Choice']
                        
                        # If reducing options, validate MCQ component answers
                        if new_options_count < question.options_count and mcq_components:
                            valid_letters = "ABCDEFGHIJ"[:new_options_count]
                            invalid_mcq_answers = []
                            
                            for i, comp in enumerate(mcq_components):
                                value = comp.get('value', '')
                                if value:
                                    answers = [a.strip() for a in value.split(',') if a.strip()]
                                    for answer in answers:
                                        if answer and answer not in valid_letters:
                                            invalid_mcq_answers.append(f"MCQ component {i+1}: {answer}")
                            
                            if invalid_mcq_answers:
                                return JsonResponse({
                                    'success': False,
                                    'error': f'These MCQ component answers would be invalid with {new_options_count} options: {", ".join(invalid_mcq_answers[:3])}. Please update the answers first.',
                                    'requires_answer_update': True
                                })
                        
                        # Set the options_count - this will affect MCQ component rendering
                        question.options_count = new_options_count
                        
                    except:
                        # If JSON parsing fails, still update options_count
                        question.options_count = new_options_count
                else:
                    question.options_count = new_options_count
            else:
                # For other question types, just update the count
                question.options_count = new_options_count
        
        # Save the question - the model's save() method now preserves options_count for MIXED questions
        question.save()
        
        return JsonResponse({
            'success': True,
            'options_count': question.options_count
        })
    except ValueError as e:
        return JsonResponse({'success': False, 'error': f'Invalid value: {str(e)}'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["POST"])
def create_questions(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    
    try:
        # Get existing question numbers
        existing_numbers = set(exam.routine_questions.values_list('question_number', flat=True))
        
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
        pdf_rotation = data.get('pdf_rotation', None)
        
        # Save PDF rotation if provided
        if pdf_rotation is not None:
            # Ensure rotation is valid (0, 90, 180, or 270)
            if pdf_rotation in [0, 90, 180, 270]:
                exam.pdf_rotation = pdf_rotation
                exam.save(update_fields=['pdf_rotation'])
                logger.info(f"Updated PDF rotation for exam {exam_id} to {pdf_rotation} degrees")
            else:
                logger.warning(f"Invalid PDF rotation value: {pdf_rotation}")
        
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
            'audio_assignments_saved': len(audio_assignments) if audio_assignments else 0,
            'audio_results': audio_results,
            'pdf_rotation_saved': pdf_rotation if pdf_rotation is not None else exam.pdf_rotation
        })
        
    except json.JSONDecodeError:
        raise ValidationException("Invalid JSON data", code="INVALID_JSON")


# UPDATE NAME REMOVED: Names are systematically generated from exam type and curriculum
# This function has been commented out as exam names are now automatically generated
"""
@require_http_methods(["POST"])
def update_exam_name(request, exam_id):
    # REMOVED - Update exam name.
    # Names are now systematically generated from:
    # - Exam type (REVIEW/QUARTERLY)
    # - Time period (Month or Quarter)
    # - Curriculum level
    # Example: "[REVIEW | January] - CORE Phonics Level 1"
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
"""


@require_http_methods(["POST"])
def update_audio_names(request, exam_id):
    """API endpoint to update audio file names."""
    try:
        exam = get_object_or_404(Exam, id=exam_id)
        data = json.loads(request.body)
        audio_names = data.get('audio_names', {})
        
        logger.info(f"[UPDATE_AUDIO_NAMES] Updating audio names for exam {exam_id}")
        logger.info(f"[UPDATE_AUDIO_NAMES] Names to update: {audio_names}")
        
        updated_count = 0
        for audio_id, new_name in audio_names.items():
            if new_name and new_name.strip():
                try:
                    audio = AudioFile.objects.get(id=audio_id, exam=exam)
                    old_name = audio.name
                    audio.name = new_name.strip()
                    audio.save()
                    updated_count += 1
                    logger.info(f"[UPDATE_AUDIO_NAMES] Updated audio {audio_id}: '{old_name}' -> '{new_name.strip()}'")
                except AudioFile.DoesNotExist:
                    logger.warning(f"[UPDATE_AUDIO_NAMES] Audio file {audio_id} not found for exam {exam_id}")
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully updated {updated_count} audio file names',
            'updated_count': updated_count
        })
        
    except Exception as e:
        logger.error(f"[UPDATE_AUDIO_NAMES] Error: {str(e)}")
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
def update_audio_names(request, exam_id):
    """API endpoint to update audio file names."""
    try:
        exam = get_object_or_404(Exam, id=exam_id)
        data = json.loads(request.body)
        audio_names = data.get('audio_names', {})
        
        updated_count = 0
        for audio_id, new_name in audio_names.items():
            if new_name and new_name.strip():
                try:
                    audio = AudioFile.objects.get(id=audio_id, exam=exam)
                    audio.name = new_name.strip()
                    audio.save()
                    updated_count += 1
                except AudioFile.DoesNotExist:
                    logger.warning(f"Audio file {audio_id} not found for exam {exam_id}")
        
        # Return redirect response for non-AJAX requests
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            messages.success(request, f'Updated {updated_count} audio file names')
            return redirect('RoutineTest:preview_exam', exam_id=exam_id)
        
        return JsonResponse({
            'success': True,
            'updated_count': updated_count
        })
        
    except Exception as e:
        logger.error(f"Error updating audio names: {e}")
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            messages.error(request, f'Error updating audio names: {str(e)}')
            return redirect('RoutineTest:preview_exam', exam_id=exam_id)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
def delete_audio_from_exam(request, exam_id, audio_id):
    """Delete audio file from an exam."""
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


@require_http_methods(["GET"])
@handle_errors(ajax_only=True)
def get_curriculum_hierarchy(request):
    """
    Get hierarchical curriculum data for cascading dropdowns.
    Returns programs, subprograms, and levels in a structured format.
    """
    from core.models import Program, SubProgram, CurriculumLevel
    from ..constants import ROUTINETEST_CURRICULUM_WHITELIST
    
    try:
        # Log the request
        logger.info("[CASCADE_API] Fetching curriculum hierarchy for RoutineTest")
        print("[CASCADE_API] Fetching curriculum hierarchy for RoutineTest")
        
        # Build whitelist lookup for filtering
        whitelist_set = set(ROUTINETEST_CURRICULUM_WHITELIST)
        
        # Get all programs available in RoutineTest
        program_names = list(set(item[0] for item in ROUTINETEST_CURRICULUM_WHITELIST))
        programs = Program.objects.filter(name__in=program_names).order_by('order')
        
        hierarchy = {
            'programs': [],
            'subprograms': {},
            'levels': {}
        }
        
        for program in programs:
            # Add program to list
            hierarchy['programs'].append({
                'id': program.id,
                'name': program.name,
                'display_name': program.get_name_display()
            })
            
            # Get subprograms for this program that are in whitelist
            subprogram_names = list(set(
                item[1] for item in ROUTINETEST_CURRICULUM_WHITELIST 
                if item[0] == program.name
            ))
            
            subprograms = SubProgram.objects.filter(
                program=program,
                name__in=subprogram_names
            ).order_by('order')
            
            hierarchy['subprograms'][program.name] = []
            
            for subprogram in subprograms:
                # Add subprogram to program's list
                hierarchy['subprograms'][program.name].append({
                    'id': subprogram.id,
                    'name': subprogram.name,
                    'display_name': subprogram.name  # Just the subprogram name
                })
                
                # Get levels for this subprogram that are in whitelist
                level_numbers = [
                    item[2] for item in ROUTINETEST_CURRICULUM_WHITELIST
                    if item[0] == program.name and item[1] == subprogram.name
                ]
                
                levels = CurriculumLevel.objects.filter(
                    subprogram=subprogram,
                    level_number__in=level_numbers
                ).order_by('level_number')
                
                # Create key for subprogram levels
                subprogram_key = f"{program.name}_{subprogram.name}"
                hierarchy['levels'][subprogram_key] = []
                
                for level in levels:
                    hierarchy['levels'][subprogram_key].append({
                        'id': level.id,
                        'level_number': level.level_number,
                        'display_name': f"Lv{level.level_number}",  # Changed to Lv abbreviation
                        'full_name': f"{program.name} {subprogram.name} Lv{level.level_number}"  # Changed to Lv
                    })
        
        # Log the hierarchy structure
        console_log = {
            "action": "curriculum_hierarchy_fetched",
            "programs_count": len(hierarchy['programs']),
            "subprograms_count": sum(len(v) for v in hierarchy['subprograms'].values()),
            "levels_count": sum(len(v) for v in hierarchy['levels'].values()),
            "timestamp": str(timezone.now())
        }
        logger.info(f"[CASCADE_API] {json.dumps(console_log)}")
        print(f"[CASCADE_API] {json.dumps(console_log)}")
        
        return JsonResponse({
            'success': True,
            'data': hierarchy
        })
        
    except Exception as e:
        logger.error(f"[CASCADE_API_ERROR] Error fetching curriculum hierarchy: {str(e)}")
        print(f"[CASCADE_API_ERROR] Error fetching curriculum hierarchy: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
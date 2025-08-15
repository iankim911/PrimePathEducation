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
from ..models import Exam, AudioFile, Question
from core.exceptions import ValidationException, AudioFileException
from core.decorators import handle_errors, teacher_required
from ..services import ExamService
from ..services.points_service import PointsService
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
    """
    ENHANCED: Update question with comprehensive validation, logging, and PointsService integration.
    
    This endpoint now provides:
    - Enterprise-grade points validation via PointsService
    - Comprehensive error handling and logging
    - Session recalculation for affected students
    - Audit trail for all changes
    - Progressive enhancement for frontend
    """
    
    # Enhanced logging for debugging
    logger.info(f"[update_question] Processing update for question {question_id}")
    logger.debug(f"[update_question] POST data: {dict(request.POST)}")
    
    # Verify question exists
    question = get_object_or_404(Question, id=question_id)
    
    # Track what fields are being updated for comprehensive logging
    update_fields = []
    response_data = {
        'success': True,
        'question_id': question_id,
        'question_number': question.question_number,
        'updates_applied': {},
        'warnings': [],
        'debug_info': {}
    }
    
    try:
        # ===== POINTS UPDATE WITH POINTSSERVICE INTEGRATION =====
        if 'points' in request.POST:
            new_points = request.POST.get('points')
            logger.info(f"[update_question] Points update requested: Q{question.question_number} -> {new_points}")
            
            # Use PointsService for robust points validation and updating
            points_result = PointsService.update_question_points(
                question_id=question_id,
                new_points=new_points,
                user_id=request.user.id if request.user.is_authenticated else None,
                recalculate_sessions=True  # Always recalculate for data integrity
            )
            
            if points_result['success']:
                # Points updated successfully
                update_fields.append('points')
                response_data['updates_applied']['points'] = {
                    'old_value': points_result['old_points'],
                    'new_value': points_result['new_points'],
                    'delta': points_result['points_delta']
                }
                
                # Add session recalculation info
                if points_result.get('affected_sessions'):
                    response_data['updates_applied']['sessions_recalculated'] = len(points_result['affected_sessions'])
                    response_data['debug_info']['affected_sessions'] = points_result['affected_sessions']
                    logger.info(f"[update_question] Recalculated {len(points_result['affected_sessions'])} student sessions")
                
                # Add performance metrics
                if points_result.get('performance'):
                    response_data['debug_info']['performance'] = points_result['performance']
                
                logger.info(f"[update_question] ✅ Points updated successfully: {points_result['message']}")
                
            else:
                # Points update failed - return error immediately
                logger.error(f"[update_question] Points update failed: {points_result['error']}")
                return JsonResponse({
                    'success': False,
                    'error': f"Points update failed: {points_result['error']}",
                    'field': 'points',
                    'validated_points': points_result.get('validated_points', 1),
                    'debug_info': points_result.get('audit_log', {}),
                    # CRITICAL: Include question info for frontend compatibility
                    'question_id': question_id,
                    'question_number': question.question_number,
                    'question': {
                        'id': question.id,
                        'number': question.question_number,
                        'type': question.question_type
                    }
                }, status=400)
        
        # ===== CORRECT ANSWER UPDATE =====
        if 'correct_answer' in request.POST:
            old_answer = question.correct_answer
            new_answer = request.POST.get('correct_answer', '').strip()
            
            if old_answer != new_answer:
                question.correct_answer = new_answer
                update_fields.append('correct_answer')
                response_data['updates_applied']['correct_answer'] = {
                    'old_value': old_answer[:50] + '...' if len(old_answer) > 50 else old_answer,
                    'new_value': new_answer[:50] + '...' if len(new_answer) > 50 else new_answer,
                    'length_change': len(new_answer) - len(old_answer)
                }
                logger.info(f"[update_question] Correct answer updated for Q{question.question_number}")
        
        # ===== OPTIONS COUNT UPDATE WITH VALIDATION =====
        if 'options_count' in request.POST:
            try:
                new_options_count = int(request.POST.get('options_count'))
                old_options_count = question.options_count
                
                logger.info(f"[update_question] Options count update: Q{question.question_number} {old_options_count} -> {new_options_count}")
                
                # Validate options_count range
                if not (2 <= new_options_count <= 10):
                    logger.warning(f"[update_question] Invalid options count: {new_options_count}")
                    return JsonResponse({
                        'success': False, 
                        'error': 'Options count must be between 2 and 10',
                        'field': 'options_count',
                        'provided_value': new_options_count,
                        # Include question info for frontend compatibility
                        'question_id': question_id,
                        'question_number': question.question_number
                    }, status=400)
                
                # For MCQ and CHECKBOX questions, validate that answers are within range
                if question.question_type in ['MCQ', 'CHECKBOX']:
                    # If reducing options, check if current answer is still valid
                    if new_options_count < old_options_count and question.correct_answer:
                        # Get letter options based on new count
                        valid_letters = "ABCDEFGHIJ"[:new_options_count]
                        
                        if question.question_type == 'MCQ':
                            # Single answer - check if it's still valid
                            if question.correct_answer and question.correct_answer not in valid_letters:
                                logger.warning(f"[update_question] MCQ answer would be invalid: {question.correct_answer} not in {valid_letters}")
                                return JsonResponse({
                                    'success': False,
                                    'error': f'Current answer "{question.correct_answer}" would be invalid with {new_options_count} options. Please update the answer first.',
                                    'field': 'options_count',
                                    'requires_answer_update': True,
                                    'current_answer': question.correct_answer,
                                    'valid_options': list(valid_letters),
                                    # Include question info for frontend compatibility
                                    'question_id': question_id,
                                    'question_number': question.question_number
                                }, status=400)
                        else:  # CHECKBOX
                            # Multiple answers - check each one
                            if question.correct_answer:
                                answers = [a.strip() for a in question.correct_answer.split(',')]
                                invalid_answers = [a for a in answers if a and a not in valid_letters]
                                if invalid_answers:
                                    logger.warning(f"[update_question] CHECKBOX answers would be invalid: {invalid_answers}")
                                    return JsonResponse({
                                        'success': False,
                                        'error': f'Answers {", ".join(invalid_answers)} would be invalid with {new_options_count} options. Please update the answer first.',
                                        'field': 'options_count',
                                        'requires_answer_update': True,
                                        'invalid_answers': invalid_answers,
                                        'valid_options': list(valid_letters),
                                        # Include question info for frontend compatibility
                                        'question_id': question_id,
                                        'question_number': question.question_number
                                    }, status=400)
                    
                    # Set the options_count
                    question.options_count = new_options_count
                
                # For MIXED questions, validate MCQ components if they exist
                elif question.question_type == 'MIXED':
                    # Check if MIXED question has MCQ components that would be affected
                    if question.correct_answer:
                        try:
                            parsed = json.loads(question.correct_answer)
                            mcq_components = [comp for comp in parsed if comp.get('type') == 'Multiple Choice']
                            
                            # If reducing options, validate MCQ component answers
                            if new_options_count < old_options_count and mcq_components:
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
                                    logger.warning(f"[update_question] MIXED MCQ components would be invalid: {invalid_mcq_answers}")
                                    return JsonResponse({
                                        'success': False,
                                        'error': f'These MCQ component answers would be invalid with {new_options_count} options: {", ".join(invalid_mcq_answers[:3])}. Please update the answers first.',
                                        'field': 'options_count',
                                        'requires_answer_update': True,
                                        'invalid_mcq_components': invalid_mcq_answers,
                                        # Include question info for frontend compatibility
                                        'question_id': question_id,
                                        'question_number': question.question_number
                                    }, status=400)
                            
                            # Set the options_count - this will affect MCQ component rendering
                            question.options_count = new_options_count
                            
                        except json.JSONDecodeError:
                            # If JSON parsing fails, still update options_count
                            question.options_count = new_options_count
                            response_data['warnings'].append('Could not parse MIXED question format, updated options_count anyway')
                    else:
                        question.options_count = new_options_count
                else:
                    # For other question types, just update the count
                    question.options_count = new_options_count
                
                if old_options_count != new_options_count:
                    update_fields.append('options_count')
                    response_data['updates_applied']['options_count'] = {
                        'old_value': old_options_count,
                        'new_value': new_options_count,
                        'delta': new_options_count - old_options_count
                    }
                    logger.info(f"[update_question] Options count updated: {old_options_count} -> {new_options_count}")
                
            except ValueError as ve:
                logger.error(f"[update_question] Invalid options_count value: {ve}")
                return JsonResponse({
                    'success': False, 
                    'error': f'Invalid options count: {str(ve)}',
                    'field': 'options_count',
                    # Include question info for frontend compatibility
                    'question_id': question_id,
                    'question_number': question.question_number
                }, status=400)
        
        # ===== SAVE QUESTION WITH ERROR HANDLING =====
        if update_fields:
            try:
                # Save the question with only the fields that were updated
                question.save(update_fields=update_fields)
                logger.info(f"[update_question] ✅ Question {question.question_number} saved successfully")
                logger.debug(f"[update_question] Updated fields: {update_fields}")
                
                # Add success metadata
                response_data['updates_applied']['total_fields'] = len(update_fields)
                response_data['updates_applied']['saved_fields'] = update_fields
                
            except Exception as save_error:
                logger.error(f"[update_question] Database save failed: {save_error}")
                return JsonResponse({
                    'success': False,
                    'error': f'Failed to save question: {str(save_error)}',
                    'attempted_fields': update_fields,
                    # Include question info for frontend compatibility
                    'question_id': question_id,
                    'question_number': question.question_number
                }, status=500)
        
        # ===== FINAL RESPONSE PREPARATION =====
        
        # Add question metadata to response
        response_data['question'] = {
            'id': question.id,
            'number': question.question_number,
            'type': question.question_type,
            'exam_id': question.exam.id,
            'exam_name': question.exam.name
        }
        
        # Add current values for frontend reference
        response_data['current_values'] = {
            'points': question.points,
            'options_count': question.options_count,
            'correct_answer_length': len(question.correct_answer),
        }
        
        # Add performance info
        response_data['debug_info']['updated_fields_count'] = len(update_fields)
        response_data['debug_info']['warnings_count'] = len(response_data['warnings'])
        
        logger.info(f"[update_question] ✅ Update completed successfully: {len(update_fields)} fields updated")
        
        return JsonResponse(response_data)
    
    except ValueError as ve:
        error_msg = f"Invalid value provided: {str(ve)}"
        logger.error(f"[update_question] ValueError: {error_msg}")
        return JsonResponse({
            'success': False, 
            'error': error_msg,
            'error_type': 'validation_error',
            # Include question info for frontend compatibility
            'question_id': question_id,
            'question_number': question.question_number if 'question' in locals() else None
        }, status=400)
        
    except ValidationError as ve:
        error_msg = f"Validation failed: {str(ve)}"
        logger.error(f"[update_question] ValidationError: {error_msg}")
        return JsonResponse({
            'success': False, 
            'error': error_msg,
            'error_type': 'model_validation_error',
            # Include question info for frontend compatibility
            'question_id': question_id,
            'question_number': question.question_number if 'question' in locals() else None
        }, status=400)
        
    except Exception as e:
        error_msg = f"Unexpected error updating question: {str(e)}"
        logger.error(f"[update_question] Unexpected error: {error_msg}", exc_info=True)
        return JsonResponse({
            'success': False, 
            'error': error_msg,
            'error_type': 'server_error',
            'question_id': question_id,
            'question_number': question.question_number if 'question' in locals() else None
        }, status=500)


@require_http_methods(["GET"])
def get_points_analytics(request, exam_id=None):
    """
    NEW ENDPOINT: Get comprehensive points analytics for questions and exams.
    Provides insights into points distribution, recommendations, and performance metrics.
    """
    logger.info(f"[get_points_analytics] Generating analytics for exam_id={exam_id}")
    
    try:
        # Use PointsService for analytics generation
        analytics_result = PointsService.get_points_analytics(exam_id=exam_id)
        
        if analytics_result['success']:
            logger.info(f"[get_points_analytics] ✅ Analytics generated successfully")
            return JsonResponse({
                'success': True,
                'analytics': analytics_result,
                'generated_at': analytics_result['timestamp']
            })
        else:
            logger.warning(f"[get_points_analytics] Analytics generation failed: {analytics_result['error']}")
            return JsonResponse({
                'success': False,
                'error': analytics_result['error']
            }, status=400)
            
    except Exception as e:
        error_msg = f"Failed to generate points analytics: {str(e)}"
        logger.error(f"[get_points_analytics] {error_msg}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': error_msg
        }, status=500)


@require_http_methods(["GET"])
def get_points_impact_preview(request, question_id):
    """
    NEW ENDPOINT: Preview the impact of changing a question's points.
    Shows which student sessions would be affected before making changes.
    """
    logger.info(f"[get_points_impact_preview] Analyzing impact for question {question_id}")
    
    try:
        # Use PointsService to get impact analysis
        impact_result = PointsService.get_affected_sessions_preview(question_id=question_id)
        
        if impact_result['success']:
            logger.info(f"[get_points_impact_preview] ✅ Impact analysis completed")
            return JsonResponse({
                'success': True,
                'impact_analysis': impact_result
            })
        else:
            logger.warning(f"[get_points_impact_preview] Impact analysis failed: {impact_result['error']}")
            return JsonResponse({
                'success': False,
                'error': impact_result['error']
            }, status=400)
            
    except Exception as e:
        error_msg = f"Failed to analyze points impact: {str(e)}"
        logger.error(f"[get_points_impact_preview] {error_msg}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': error_msg
        }, status=500)


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


@require_http_methods(["POST"])
@csrf_exempt
@handle_errors(ajax_only=True)
def save_exam_answers(request, exam_id):
    """Save exam questions and answers configuration."""
    exam = get_object_or_404(Exam, id=exam_id)
    
    logger.info(f"[save_exam_answers] ========== SAVE ALL REQUEST ==========")
    logger.info(f"[save_exam_answers] Exam: {exam.name} (ID: {exam_id})")
    
    try:
        data = json.loads(request.body)
        questions_data = data.get('questions', [])
        audio_assignments = data.get('audio_assignments', {})
        pdf_rotation = data.get('pdf_rotation', None)
        
        # Enhanced logging for points tracking
        logger.info(f"[save_exam_answers] Received {len(questions_data)} questions")
        
        # Log points summary
        points_summary = []
        for q in questions_data:
            points_info = {
                'num': q.get('question_number'),
                'points': q.get('points', 'not provided'),
                'type': q.get('question_type')
            }
            points_summary.append(points_info)
            if 'points' in q:
                logger.info(f"[save_exam_answers] Q{q['question_number']}: points={q['points']}")
        
        logger.debug(f"[save_exam_answers] Points summary: {json.dumps(points_summary, indent=2)}")
        
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
        
        # Log completion
        logger.info(f"[save_exam_answers] Update results: {results}")
        logger.info(f"[save_exam_answers] ========== SAVE ALL COMPLETE ==========")
        
        # Enhanced response with points tracking
        response_data = {
            'success': True,
            'message': f'Successfully saved {len(questions_data)} questions',
            'details': results,
            'audio_assignments_saved': len(audio_assignments) if audio_assignments else 0,
            'audio_results': audio_results,
            'pdf_rotation_saved': pdf_rotation if pdf_rotation is not None else exam.pdf_rotation,
            'points_updated': sum(1 for q in questions_data if 'points' in q),
            'debug_info': {
                'total_questions': len(questions_data),
                'points_provided': [q.get('question_number') for q in questions_data if 'points' in q]
            }
        }
        
        logger.info(f"[save_exam_answers] Points updated for {response_data['points_updated']} questions")
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        raise ValidationException("Invalid JSON data", code="INVALID_JSON")


@require_http_methods(["POST"])
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
            return redirect('PlacementTest:preview_exam', exam_id=exam_id)
        
        return JsonResponse({
            'success': True,
            'updated_count': updated_count
        })
        
    except Exception as e:
        logger.error(f"Error updating audio names: {e}")
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            messages.error(request, f'Error updating audio names: {str(e)}')
            return redirect('PlacementTest:preview_exam', exam_id=exam_id)
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
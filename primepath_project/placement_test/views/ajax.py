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
            return redirect('placement_test:preview_exam', exam_id=exam_id)
        
        return JsonResponse({
            'success': True,
            'updated_count': updated_count
        })
        
    except Exception as e:
        logger.error(f"Error updating audio names: {e}")
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            messages.error(request, f'Error updating audio names: {str(e)}')
            return redirect('placement_test:preview_exam', exam_id=exam_id)
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
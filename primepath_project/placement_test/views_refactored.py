"""
Refactored placement test views using service layer.
Phase 6 implementation - Gradual replacement of views.py
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Exam, AudioFile, Question, StudentSession, StudentAnswer
from core.models import School, PlacementRule, CurriculumLevel
from core.exceptions import (
    PlacementRuleException, ExamNotFoundException, 
    SessionAlreadyCompletedException, ValidationException
)
from core.decorators import handle_errors, validate_request_data
from .services import PlacementService, SessionService, ExamService, GradingService
from core.services import FileService
from common.mixins import AjaxResponseMixin
from core.utils import get_template_name

import json
import uuid
import logging

logger = logging.getLogger(__name__)


class RefactoredViewsMixin(AjaxResponseMixin):
    """Mixin for refactored views to ensure consistency."""
    pass


@handle_errors(template_name='placement_test/error.html')
def start_test(request):
    """Start a new test session using services."""
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
            
            # Collect student data
            student_data = {
                'student_name': request.POST.get('student_name'),
                'parent_phone': request.POST.get('parent_phone', '').replace('-', '').replace(' ', ''),
                'school_name': request.POST.get('school_name'),
                'academic_rank': request.POST.get('academic_rank'),
            }
            
            # Validate and convert grade
            try:
                grade = int(request.POST.get('grade'))
                if not 1 <= grade <= 12:
                    raise ValidationException("Grade must be between 1 and 12", code="INVALID_GRADE")
            except (ValueError, TypeError):
                raise ValidationException("Invalid grade value", code="INVALID_GRADE")
            
            # Use PlacementService to match student to exam
            exam, curriculum_level = PlacementService.match_student_to_exam(
                grade=grade,
                academic_rank=student_data['academic_rank']
            )
            
            # Use SessionService to create session
            session = SessionService.create_session(
                student_data=student_data,
                grade=grade,
                exam=exam,
                curriculum_level=curriculum_level
            )
            
            # Store session info
            request.session['session_id'] = str(session.id)
            request.session['exam_id'] = str(exam.id)
            request.session['current_question'] = 1
            
            logger.info(f"Test session created: {session.id} for student: {student_data['student_name']}")
            
            # Redirect to test page
            return redirect('placement_test:take_test', session_id=session.id)
            
        except PlacementRuleException as e:
            logger.warning(f"No placement rule found for grade={grade}, rank={student_data.get('academic_rank')}")
            messages.error(request, str(e))
            return render(request, 'placement_test/start_test.html', {'error': str(e)})
            
        except Exception as e:
            logger.error(f"Error creating test session: {e}", exc_info=True)
            messages.error(request, "An error occurred while starting the test. Please try again.")
            return render(request, 'placement_test/start_test.html', {'error': str(e)})
    
    # GET request - show form
    schools = School.objects.all().order_by('name')
    return render(request, 'placement_test/start_test.html', {'schools': schools})


def take_test(request, session_id):
    """Display test interface using services."""
    try:
        # Use SessionService to get session with all related data
        session = SessionService.get_session_with_related(session_id)
        
        if not session:
            raise Http404("Test session not found")
        
        # Check if session is already completed
        if session.completed_at:
            messages.info(request, "This test has already been completed.")
            return redirect('placement_test:test_complete', session_id=session_id)
        
        # Get exam with optimized queries
        exam = ExamService.get_exam_with_questions(session.exam_id)
        
        # Get questions
        questions = exam.questions.all().order_by('question_number')
        
        # Get existing answers
        existing_answers = {
            answer.question_id: answer 
            for answer in session.answers.select_related('question').all()
        }
        
        # Prepare template context
        context = {
            'session': session,
            'exam': exam,
            'questions': questions,
            'existing_answers': existing_answers,
            'total_questions': exam.total_questions,
            'timer_minutes': exam.timer_minutes,
            # Use feature flag for template selection
            'use_v2_template': get_template_name('') == 'v2',
        }
        
        template_name = get_template_name('placement_test/student_test.html')
        return render(request, template_name, context)
        
    except Exception as e:
        logger.error(f"Error loading test: {e}", exc_info=True)
        messages.error(request, "Error loading test. Please contact support.")
        return redirect('placement_test:start_test')


@require_POST
@csrf_exempt  # Handle CSRF in AJAX
def submit_answer(request, session_id):
    """Submit an answer using SessionService."""
    try:
        # Parse request data
        data = json.loads(request.body)
        question_id = data.get('question_id')
        answer = data.get('answer')
        
        if not question_id:
            return JsonResponse({'success': False, 'error': 'Question ID required'}, status=400)
        
        # Use SessionService to save answer
        result = SessionService.save_answer(
            session_id=session_id,
            question_id=question_id,
            answer=answer
        )
        
        if result:
            return JsonResponse({
                'success': True,
                'message': 'Answer saved',
                'question_id': question_id
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Could not save answer'
            }, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error submitting answer: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_POST
def complete_test(request, session_id):
    """Complete test and calculate results using GradingService."""
    try:
        # Get session
        session = StudentSession.objects.get(id=session_id)
        
        if session.completed_at:
            return JsonResponse({
                'success': False,
                'error': 'Test already completed'
            }, status=400)
        
        # Use GradingService to grade the session
        results = GradingService.grade_session(session_id)
        
        # Mark session as complete
        session.completed_at = timezone.now()
        session.save()
        
        # Get analytics
        analytics = GradingService.get_session_analytics(session_id)
        
        return JsonResponse({
            'success': True,
            'results': {
                'total_questions': results['total_questions'],
                'answered': results['answered'],
                'correct': results['correct'],
                'score': results['score'],
                'percentage': results['percentage'],
                'placement_level': str(session.final_curriculum_level) if session.final_curriculum_level else None,
                'analytics': analytics
            }
        })
        
    except StudentSession.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Session not found'}, status=404)
    except Exception as e:
        logger.error(f"Error completing test: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def exam_list(request):
    """List all exams using ExamService."""
    try:
        # Use service to get exams with statistics
        exams = ExamService.get_all_exams_with_stats()
        
        context = {
            'exams': exams,
            'total_exams': len(exams),
            'active_exams': sum(1 for e in exams if e.get('is_active', False))
        }
        
        return render(request, 'placement_test/exam_list.html', context)
        
    except Exception as e:
        logger.error(f"Error listing exams: {e}", exc_info=True)
        messages.error(request, "Error loading exams.")
        return render(request, 'placement_test/exam_list.html', {'exams': []})


@login_required
def create_exam(request):
    """Create a new exam using ExamService and FileService."""
    if request.method == 'POST':
        try:
            # Validate required fields
            required_fields = ['name', 'total_questions', 'timer_minutes']
            missing_fields = [f for f in required_fields if not request.POST.get(f)]
            
            if missing_fields:
                raise ValidationException(f"Missing required fields: {', '.join(missing_fields)}")
            
            # Handle PDF file upload
            pdf_info = None
            if 'pdf_file' in request.FILES:
                pdf_file = request.FILES['pdf_file']
                pdf_info = FileService.save_exam_pdf(pdf_file, 'temp')
            
            # Prepare exam data
            exam_data = {
                'name': request.POST.get('name'),
                'curriculum_level_id': request.POST.get('curriculum_level'),
                'total_questions': int(request.POST.get('total_questions')),
                'timer_minutes': int(request.POST.get('timer_minutes', 60)),
                'default_options_count': int(request.POST.get('default_options_count', 5)),
                'passing_score': request.POST.get('passing_score'),
                'pdf_info': pdf_info,
                'created_by': request.user if request.user.is_authenticated else None
            }
            
            # Use ExamService to create exam
            exam = ExamService.create_exam(exam_data)
            
            messages.success(request, f"Exam '{exam.name}' created successfully!")
            return redirect('placement_test:exam_detail', exam_id=exam.id)
            
        except ValidationException as e:
            messages.error(request, str(e))
        except Exception as e:
            logger.error(f"Error creating exam: {e}", exc_info=True)
            messages.error(request, "Error creating exam. Please try again.")
            
            # Clean up uploaded file if exam creation failed
            if pdf_info:
                FileService.delete_file(pdf_info['path'])
    
    # GET request - show form
    from core.services import CurriculumService
    curriculum_levels = CurriculumService.get_all_levels()
    
    context = {
        'curriculum_levels': curriculum_levels
    }
    return render(request, 'placement_test/create_exam.html', context)


@login_required
def edit_exam(request, exam_id):
    """Edit an existing exam using ExamService."""
    try:
        exam = ExamService.get_exam_with_questions(exam_id)
        
        if not exam:
            raise Http404("Exam not found")
        
        if request.method == 'POST':
            # Handle PDF file update
            pdf_info = None
            if 'pdf_file' in request.FILES:
                pdf_file = request.FILES['pdf_file']
                
                # Delete old PDF if exists
                if exam.pdf_file:
                    FileService.delete_file(exam.pdf_file.name)
                
                # Save new PDF
                pdf_info = FileService.save_exam_pdf(pdf_file, exam_id)
            
            # Prepare update data
            update_data = {
                'name': request.POST.get('name', exam.name),
                'curriculum_level_id': request.POST.get('curriculum_level', exam.curriculum_level_id),
                'total_questions': int(request.POST.get('total_questions', exam.total_questions)),
                'timer_minutes': int(request.POST.get('timer_minutes', exam.timer_minutes)),
                'default_options_count': int(request.POST.get('default_options_count', exam.default_options_count)),
                'passing_score': request.POST.get('passing_score', exam.passing_score),
                'is_active': request.POST.get('is_active') == 'on',
                'pdf_info': pdf_info
            }
            
            # Use ExamService to update exam
            updated_exam = ExamService.update_exam(exam_id, update_data)
            
            messages.success(request, f"Exam '{updated_exam.name}' updated successfully!")
            return redirect('placement_test:exam_detail', exam_id=exam.id)
        
        # GET request - show form
        from core.services import CurriculumService
        curriculum_levels = CurriculumService.get_all_levels()
        
        context = {
            'exam': exam,
            'curriculum_levels': curriculum_levels
        }
        return render(request, 'placement_test/edit_exam.html', context)
        
    except Http404:
        raise
    except Exception as e:
        logger.error(f"Error editing exam: {e}", exc_info=True)
        messages.error(request, "Error editing exam.")
        return redirect('placement_test:exam_list')


@login_required
@require_POST
def delete_exam(request, exam_id):
    """Delete an exam using ExamService."""
    try:
        # Use service to delete exam
        success = ExamService.delete_exam(exam_id)
        
        if success:
            messages.success(request, "Exam deleted successfully!")
        else:
            messages.error(request, "Could not delete exam.")
        
        return redirect('placement_test:exam_list')
        
    except Exception as e:
        logger.error(f"Error deleting exam: {e}", exc_info=True)
        messages.error(request, "Error deleting exam.")
        return redirect('placement_test:exam_list')


def preview_exam(request, exam_id):
    """Preview an exam PDF using FileService."""
    try:
        exam = Exam.objects.get(id=exam_id)
        
        if not exam.pdf_file:
            messages.warning(request, "This exam has no PDF file.")
            return redirect('placement_test:exam_detail', exam_id=exam_id)
        
        # Use FileService to get file URL
        file_url = FileService.get_file_url(exam.pdf_file.name)
        
        if not file_url:
            messages.error(request, "Could not access PDF file.")
            return redirect('placement_test:exam_detail', exam_id=exam_id)
        
        context = {
            'exam': exam,
            'pdf_url': file_url
        }
        return render(request, 'placement_test/preview_exam.html', context)
        
    except Exam.DoesNotExist:
        raise Http404("Exam not found")
    except Exception as e:
        logger.error(f"Error previewing exam: {e}", exc_info=True)
        messages.error(request, "Error loading exam preview.")
        return redirect('placement_test:exam_list')
"""
Phase 3: Student exam-taking views
Adapts the placement test interface for routine tests
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from primepath_student.models import StudentProfile, StudentClassAssignment, StudentExamSession
from primepath_routinetest.models.exam_management import RoutineExam, ExamLaunchSession
import json


@login_required
def start_exam(request, launch_id):
    """Start an exam from a launch session"""
    try:
        student_profile = request.user.primepath_student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found")
        return redirect('primepath_student:dashboard')
    
    # Get the launch session
    launch = get_object_or_404(ExamLaunchSession, id=launch_id)
    
    # Check if launch is still active
    if not launch.is_active or launch.expires_at < timezone.now():
        messages.error(request, "This exam is no longer available")
        return redirect('primepath_student:dashboard')
    
    # Check if student is in the class for this exam
    class_assignment = StudentClassAssignment.objects.filter(
        student=student_profile,
        class_code=launch.class_code,
        is_active=True
    ).first()
    
    if not class_assignment:
        messages.error(request, "You are not enrolled in the class for this exam")
        return redirect('primepath_student:dashboard')
    
    # Check if student is allowed to take this exam
    if launch.excluded_students.filter(id=student_profile.id).exists():
        messages.error(request, "You are not allowed to take this exam")
        return redirect('primepath_student:class_detail', class_code=launch.class_code)
    
    # Get or create exam session
    session, created = StudentExamSession.get_or_create_session(
        student=student_profile,
        exam=launch.exam,
        class_assignment=class_assignment
    )
    
    if created:
        # Set IP and user agent
        session.ip_address = request.META.get('REMOTE_ADDR')
        session.user_agent = request.META.get('HTTP_USER_AGENT', '')
        session.save()
    
    # Redirect to exam taking interface
    return redirect('primepath_student:take_exam', session_id=session.id)


@login_required
def take_exam(request, session_id):
    """Main exam-taking interface (adapts placement test interface)"""
    try:
        student_profile = request.user.primepath_student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found")
        return redirect('primepath_student:dashboard')
    
    # Get the exam session
    session = get_object_or_404(
        StudentExamSession,
        id=session_id,
        student=student_profile
    )
    
    # Check if exam is expired
    if session.is_expired() and session.status == 'in_progress':
        session.expire()
        messages.warning(request, "Your exam time has expired. Your answers have been submitted.")
        return redirect('primepath_student:exam_result', session_id=session.id)
    
    # Check if exam is already completed
    if session.status in ['completed', 'expired']:
        return redirect('primepath_student:exam_result', session_id=session.id)
    
    # Start the exam if not started
    if session.status == 'not_started':
        session.start()
    
    # Get exam questions from answer_key
    answer_key = session.exam.answer_key if session.exam.answer_key else {}
    questions = []
    
    # Prepare exam data for the interface
    exam_data = {
        'id': str(session.exam.id),
        'name': session.exam.name,
        'duration': session.duration_minutes,
        'total_questions': len(answer_key),
        'pdf_url': session.exam.pdf_file.url if session.exam.pdf_file else None,
        'instructions': session.exam.instructions or '',
    }
    
    # Prepare session data
    session_data = {
        'id': str(session.id),
        'status': session.status,
        'started_at': session.started_at.isoformat() if session.started_at else None,
        'expires_at': session.expires_at.isoformat() if session.expires_at else None,
        'time_remaining': session.get_time_remaining(),
        'current_question': session.current_question,
        'answers': session.answers,
        'auto_saved_at': session.auto_saved_at.isoformat() if session.auto_saved_at else None,
    }
    
    # Prepare questions data from answer_key
    questions_data = []
    for question_num, correct_answer in answer_key.items():
        question_data = {
            'id': question_num,
            'question_number': int(question_num),
            'question_text': f'Question {question_num}',  # Questions are in PDF
            'question_type': 'multiple_choice',
            'option_1': 'A',
            'option_2': 'B', 
            'option_3': 'C',
            'option_4': 'D',
            'points': 1,
            'has_audio': False,
        }
        questions_data.append(question_data)
    
    # Sort by question number
    questions_data.sort(key=lambda x: x['question_number'])
    
    context = {
        'session': session,
        'exam': exam_data,
        'session_data': session_data,
        'questions': questions_data,
        'student': student_profile,
    }
    
    # Use the placement test template (will be adapted)
    return render(request, 'primepath_student/exam/take_exam.html', context)


@login_required
@csrf_protect
@require_http_methods(["POST"])
def save_answer(request, session_id):
    """Save a single answer (AJAX endpoint)"""
    try:
        student_profile = request.user.primepath_student_profile
    except StudentProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Student profile not found'})
    
    session = get_object_or_404(
        StudentExamSession,
        id=session_id,
        student=student_profile
    )
    
    if session.status != 'in_progress':
        return JsonResponse({'success': False, 'error': 'Exam is not in progress'})
    
    if session.is_expired():
        session.expire()
        return JsonResponse({'success': False, 'error': 'Exam has expired', 'redirect': True})
    
    try:
        data = json.loads(request.body)
        question_number = data.get('question_number')
        answer = data.get('answer')
        
        if not question_number:
            return JsonResponse({'success': False, 'error': 'Question number required'})
        
        session.save_answer(question_number, answer)
        
        return JsonResponse({
            'success': True,
            'auto_saved_at': session.auto_saved_at.isoformat(),
            'time_remaining': session.get_time_remaining()
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_protect
@require_http_methods(["POST"])
def auto_save(request, session_id):
    """Auto-save multiple answers (AJAX endpoint)"""
    try:
        student_profile = request.user.primepath_student_profile
    except StudentProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Student profile not found'})
    
    session = get_object_or_404(
        StudentExamSession,
        id=session_id,
        student=student_profile
    )
    
    if session.status != 'in_progress':
        return JsonResponse({'success': False, 'error': 'Exam is not in progress'})
    
    if session.is_expired():
        session.expire()
        return JsonResponse({'success': False, 'error': 'Exam has expired', 'expired': True})
    
    try:
        data = json.loads(request.body)
        answers = data.get('answers', {})
        
        success = session.save_answers_batch(answers)
        
        if success:
            return JsonResponse({
                'success': True,
                'auto_saved_at': session.auto_saved_at.isoformat(),
                'time_remaining': session.get_time_remaining()
            })
        else:
            return JsonResponse({'success': False, 'error': 'Could not save answers'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_protect
@require_http_methods(["POST"])
def submit_exam(request, session_id):
    """Submit the exam for grading"""
    try:
        student_profile = request.user.primepath_student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found")
        return redirect('primepath_student:dashboard')
    
    session = get_object_or_404(
        StudentExamSession,
        id=session_id,
        student=student_profile
    )
    
    if session.status in ['completed', 'expired']:
        messages.info(request, "This exam has already been submitted")
        return redirect('primepath_student:exam_result', session_id=session.id)
    
    # Save any final answers if provided
    if request.method == 'POST' and request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            final_answers = data.get('answers', {})
            if final_answers:
                session.save_answers_batch(final_answers)
        except:
            pass
    
    # Complete the exam
    try:
        session.complete()
        messages.success(request, "Exam submitted successfully!")
        
        # Send notification about results
        try:
            from primepath_student.services import NotificationService
            NotificationService.notify_exam_results(session)
        except Exception as e:
            # Don't fail submission if notification fails
            pass
            
    except Exception as e:
        messages.error(request, f"Error submitting exam: {str(e)}")
    
    return redirect('primepath_student:exam_result', session_id=session.id)


@login_required
def exam_result(request, session_id):
    """View exam results"""
    try:
        student_profile = request.user.primepath_student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found")
        return redirect('primepath_student:dashboard')
    
    session = get_object_or_404(
        StudentExamSession,
        id=session_id,
        student=student_profile
    )
    
    # Ensure exam is completed
    if session.status not in ['completed', 'expired']:
        messages.warning(request, "This exam is not yet completed")
        return redirect('primepath_student:take_exam', session_id=session.id)
    
    # Get questions with correct answers from answer_key
    answer_key = session.exam.answer_key if session.exam.answer_key else {}
    
    # Prepare results data
    results = []
    for question_num, correct_answer in answer_key.items():
        student_answer = session.answers.get(str(question_num))
        is_correct = student_answer == correct_answer if student_answer else False
        
        results.append({
            'question_number': int(question_num),
            'question_text': f'Question {question_num}',
            'student_answer': student_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'option_1': 'A',
            'option_2': 'B',
            'option_3': 'C', 
            'option_4': 'D',
        })
    
    # Sort results by question number
    results.sort(key=lambda x: x['question_number'])
    
    context = {
        'session': session,
        'exam': session.exam,
        'results': results,
        'score': session.score,
        'correct_answers': session.correct_answers,
        'total_questions': session.total_questions,
        'percentage': round(session.score) if session.score else 0,
        'completed_at': session.completed_at,
        'student': student_profile,
    }
    
    return render(request, 'primepath_student/exam/exam_result.html', context)


@login_required
def exam_history(request):
    """View all past exams"""
    try:
        student_profile = request.user.primepath_student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found")
        return redirect('primepath_student:dashboard')
    
    # Get all exam sessions for this student
    sessions = StudentExamSession.objects.filter(
        student=student_profile,
        status__in=['completed', 'expired']
    ).select_related('exam', 'class_assignment').order_by('-completed_at')
    
    context = {
        'sessions': sessions,
        'student': student_profile,
    }
    
    return render(request, 'primepath_student/exam/exam_history.html', context)
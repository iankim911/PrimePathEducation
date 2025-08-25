from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from primepath_student.models import StudentProfile
from primepath_student.models import StudentExamSession
from django.db.models import Q


@login_required
def exam_history(request):
    """View for displaying student's exam history"""
    # Check if user has student profile
    try:
        student_profile = request.user.primepath_student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, "You don't have a student profile. Please contact support.")
        return redirect('primepath_student:login')
    
    # Get all exam sessions for this student
    exam_sessions = StudentExamSession.objects.filter(
        student=student_profile
    ).select_related('exam').order_by('-started_at')
    
    # Process sessions for display
    exam_history_data = []
    for session in exam_sessions:
        exam_history_data.append({
            'exam_name': session.exam.name if session.exam else 'Unknown Exam',
            'class_code': session.class_assignment.class_code if session.class_assignment else '--',
            'start_time': session.started_at,
            'submit_time': session.completed_at,
            'score': session.score,
            'total_questions': session.total_questions,
            'is_completed': session.status == 'completed',
            'status': 'Completed' if session.status == 'completed' else 'In Progress'
        })
    
    context = {
        'student': student_profile,
        'exam_history': exam_history_data,
        'total_exams': len(exam_history_data)
    }
    
    return render(request, 'primepath_student/exam_history.html', context)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from primepath_student.models import StudentProfile, StudentClassAssignment, StudentExamSession
from primepath_routinetest.models.exam_management import ExamLaunchSession
from primepath_routinetest.models.class_constants import CLASS_CODE_CHOICES
from django.utils import timezone


@login_required
def class_detail(request, class_code):
    """View details of a specific class"""
    # Check if user has student profile
    try:
        student_profile = request.user.primepath_student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, "You don't have a student profile. Please contact support.")
        return redirect('primepath_student:login')
    
    # Check if student is assigned to this class
    try:
        assignment = StudentClassAssignment.objects.get(
            student=student_profile,
            class_code=class_code,
            is_active=True
        )
    except StudentClassAssignment.DoesNotExist:
        messages.error(request, "You are not enrolled in this class")
        return redirect('primepath_student:dashboard')
    
    # Get class display name
    class_display = dict(CLASS_CODE_CHOICES).get(class_code, class_code)
    
    # Get active exam launches for this class
    active_launches = ExamLaunchSession.objects.filter(
        class_code=class_code,
        is_active=True,
        expires_at__gt=timezone.now()
    ).select_related('exam').order_by('-launched_at')
    
    # Get past exam sessions for this student in this class
    past_exams = StudentExamSession.objects.filter(
        student=student_profile,
        class_assignment=assignment,
        status__in=['completed', 'expired']
    ).select_related('exam').order_by('-completed_at')[:5]  # Show last 5
    
    context = {
        'student': student_profile,
        'assignment': assignment,
        'class_code': class_code,
        'class_display': class_display,
        'active_exams': active_launches,
        'past_exams': past_exams,
        'has_active_exam': active_launches.exists()
    }
    
    return render(request, 'primepath_student/class_detail.html', context)
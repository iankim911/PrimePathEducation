from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from primepath_student.models import StudentProfile, StudentClassAssignment
from primepath_routinetest.models.exam import Exam
from primepath_routinetest.models.exam_management import ExamLaunchSession
from django.utils import timezone


@login_required
def student_dashboard(request):
    """Student dashboard showing My Classes"""
    # Check if user has student profile
    try:
        student_profile = request.user.primepath_student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, "You don't have a student profile. Please contact support.")
        return redirect('primepath_student:login')
    
    # Get active class assignments
    active_assignments = student_profile.active_classes
    
    # For each class, check if there are any active exams
    classes_with_exams = []
    for assignment in active_assignments:
        # Get active exam launches for this class
        active_launches = ExamLaunchSession.objects.filter(
            class_code=assignment.class_code,
            is_active=True,
            expires_at__gt=timezone.now()
        ).select_related('exam')
        
        classes_with_exams.append({
            'assignment': assignment,
            'class_code': assignment.class_code,
            'class_display': dict(StudentClassAssignment._meta.get_field('class_code').choices).get(
                assignment.class_code, assignment.class_code
            ),
            'active_exams': active_launches,
            'has_active_exam': active_launches.exists()
        })
    
    context = {
        'student': student_profile,
        'classes': classes_with_exams,
        'total_classes': len(classes_with_exams)
    }
    
    return render(request, 'primepath_student/dashboard.html', context)
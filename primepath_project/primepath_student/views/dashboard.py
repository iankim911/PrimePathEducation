from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Prefetch, Q
from primepath_student.models import StudentProfile, StudentClassAssignment
from primepath_routinetest.models.exam import Exam
from primepath_routinetest.models.exam_management import ExamLaunchSession
from django.utils import timezone
from collections import defaultdict


@login_required
def student_dashboard(request):
    """Student dashboard showing My Classes"""
    # Check if user has student profile
    try:
        student_profile = request.user.primepath_student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, "You don't have a student profile. Please contact support.")
        return redirect('primepath_student:login')
    
    # Get active class assignments with optimized query
    active_assignments = student_profile.class_assignments.filter(is_active=True)
    
    # Get all class codes in one query to reduce N+1
    class_codes = list(active_assignments.values_list('class_code', flat=True))
    
    # Fetch all active exam launches for all classes in one query
    current_time = timezone.now()
    all_launches = ExamLaunchSession.objects.filter(
        class_code__in=class_codes,
        is_active=True,
        expires_at__gt=current_time
    ).select_related('exam')
    
    # Group launches by class code for efficient lookup
    launches_by_class = defaultdict(list)
    for launch in all_launches:
        launches_by_class[launch.class_code].append(launch)
    
    # Pre-compute class choices for display
    class_choices = dict(StudentClassAssignment._meta.get_field('class_code').choices)
    
    # Build the response data efficiently
    classes_with_exams = []
    for assignment in active_assignments:
        active_launches = launches_by_class[assignment.class_code]
        
        classes_with_exams.append({
            'assignment': assignment,
            'class_code': assignment.class_code,
            'class_display': class_choices.get(assignment.class_code, assignment.class_code),
            'active_exams': active_launches,
            'has_active_exam': len(active_launches) > 0
        })
    
    context = {
        'student': student_profile,
        'classes': classes_with_exams,
        'total_classes': len(classes_with_exams)
    }
    
    return render(request, 'primepath_student/dashboard.html', context)
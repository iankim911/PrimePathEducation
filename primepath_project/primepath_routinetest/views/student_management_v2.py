"""
Phase 2: Teacher views for managing students in classes
Using the new StudentProfile model from primepath_student app
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.db import transaction
from django.db.models import Q, Count
from django.contrib.auth.models import User

from core.models import Teacher
from primepath_student.models import StudentProfile, StudentClassAssignment
from primepath_routinetest.models.class_access import TeacherClassAssignment
from primepath_routinetest.models.class_constants import CLASS_CODE_CHOICES
import json


@login_required
@require_http_methods(["GET", "POST"])
def manage_class_students(request, class_code):
    """View and manage students in a specific class"""
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        messages.error(request, "Teacher profile not found")
        return redirect('primepath_routinetest:classes_exams')
    
    # Check if teacher has access to this class
    has_access = TeacherClassAssignment.objects.filter(
        teacher=teacher,
        class_code=class_code,
        is_active=True
    ).exists() or teacher.is_head_teacher
    
    if not has_access:
        messages.error(request, "You don't have access to manage this class")
        return redirect('primepath_routinetest:classes_exams')
    
    # Get class display name
    class_display = dict(CLASS_CODE_CHOICES).get(class_code, class_code)
    
    # Get current students in this class
    current_assignments = StudentClassAssignment.objects.filter(
        class_code=class_code,
        is_active=True
    ).select_related('student', 'student__user').order_by('student__user__last_name')
    
    # Get all students for assignment dropdown
    all_students = StudentProfile.objects.exclude(
        class_assignments__class_code=class_code,
        class_assignments__is_active=True
    ).select_related('user').order_by('user__last_name')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_student':
            student_id = request.POST.get('student_id')
            try:
                student = StudentProfile.objects.get(id=student_id)
                # Check if already assigned (including inactive)
                assignment, created = StudentClassAssignment.objects.get_or_create(
                    student=student,
                    class_code=class_code,
                    defaults={
                        'assigned_by': teacher,
                        'is_active': True
                    }
                )
                
                if not created:
                    if not assignment.is_active:
                        assignment.reactivate()
                        messages.success(request, f"{student.user.get_full_name()} re-added to class")
                    else:
                        messages.warning(request, f"{student.user.get_full_name()} is already in this class")
                else:
                    messages.success(request, f"{student.user.get_full_name()} added to class")
                    
            except StudentProfile.DoesNotExist:
                messages.error(request, "Student not found")
                
        elif action == 'remove_student':
            assignment_id = request.POST.get('assignment_id')
            try:
                assignment = StudentClassAssignment.objects.get(
                    id=assignment_id,
                    class_code=class_code
                )
                student_name = assignment.student.user.get_full_name()
                assignment.deactivate()
                messages.success(request, f"{student_name} removed from class")
            except StudentClassAssignment.DoesNotExist:
                messages.error(request, "Assignment not found")
        
        return redirect('primepath_routinetest:manage_class_students', class_code=class_code)
    
    context = {
        'teacher': teacher,
        'class_code': class_code,
        'class_display': class_display,
        'current_students': current_assignments,
        'available_students': all_students,
        'student_count': current_assignments.count()
    }
    
    return render(request, 'primepath_routinetest/student_management/class_students.html', context)


@login_required
@csrf_protect
@require_http_methods(["POST"])
def bulk_assign_students(request, class_code):
    """Bulk assign students to a class"""
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Teacher profile not found'})
    
    # Check access
    has_access = TeacherClassAssignment.objects.filter(
        teacher=teacher,
        class_code=class_code,
        is_active=True
    ).exists() or teacher.is_head_teacher
    
    if not has_access:
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    try:
        data = json.loads(request.body)
        student_ids = data.get('student_ids', [])
        
        if not student_ids:
            return JsonResponse({'success': False, 'error': 'No students selected'})
        
        added_count = 0
        reactivated_count = 0
        
        with transaction.atomic():
            for student_id in student_ids:
                try:
                    student = StudentProfile.objects.get(id=student_id)
                    assignment, created = StudentClassAssignment.objects.get_or_create(
                        student=student,
                        class_code=class_code,
                        defaults={
                            'assigned_by': teacher,
                            'is_active': True
                        }
                    )
                    
                    if created:
                        added_count += 1
                    elif not assignment.is_active:
                        assignment.reactivate()
                        reactivated_count += 1
                        
                except StudentProfile.DoesNotExist:
                    continue
        
        message = f"Successfully added {added_count} new students"
        if reactivated_count:
            message += f" and reactivated {reactivated_count} students"
            
        return JsonResponse({
            'success': True,
            'message': message,
            'added': added_count,
            'reactivated': reactivated_count
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def search_students(request):
    """Search for students by name, ID, or phone number"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'students': []})
    
    students = StudentProfile.objects.filter(
        Q(student_id__icontains=query) |
        Q(phone_number__icontains=query) |
        Q(user__first_name__icontains=query) |
        Q(user__last_name__icontains=query)
    ).select_related('user')[:20]
    
    results = []
    for student in students:
        # Get current classes
        active_classes = student.class_assignments.filter(
            is_active=True
        ).values_list('class_code', flat=True)
        
        class_names = [dict(CLASS_CODE_CHOICES).get(code, code) for code in active_classes]
        
        results.append({
            'id': student.id,
            'student_id': student.student_id,
            'name': student.user.get_full_name(),
            'phone': student.phone_number,
            'classes': class_names
        })
    
    return JsonResponse({'students': results})


@login_required
def create_student_account(request):
    """Create a new student account (for teachers/admins)"""
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        messages.error(request, "Teacher profile not found")
        return redirect('primepath_routinetest:classes_exams')
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '').strip()
        student_id = request.POST.get('student_id', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '')
        class_codes = request.POST.getlist('class_codes')
        
        # Validation
        errors = []
        
        if StudentProfile.objects.filter(phone_number=phone_number).exists():
            errors.append("This phone number is already registered")
        
        if not student_id:
            student_id = StudentProfile.generate_student_id()
        elif StudentProfile.objects.filter(student_id=student_id).exists():
            errors.append("This student ID already exists")
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters")
        
        if not first_name or not last_name:
            errors.append("Please provide both first and last name")
        
        if errors:
            return render(request, 'primepath_routinetest/student_management/create_student.html', {
                'errors': errors,
                'form_data': request.POST,
                'all_classes': CLASS_CODE_CHOICES
            })
        
        try:
            with transaction.atomic():
                # Create user account
                username = f"student_{phone_number}"
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # Create student profile
                student_profile = StudentProfile.objects.create(
                    user=user,
                    student_id=student_id,
                    phone_number=phone_number
                )
                
                # Assign to classes if specified
                for class_code in class_codes:
                    if class_code in dict(CLASS_CODE_CHOICES):
                        StudentClassAssignment.objects.create(
                            student=student_profile,
                            class_code=class_code,
                            assigned_by=teacher,
                            is_active=True
                        )
                
                messages.success(request, f"Student account created: {student_id}")
                
                # Redirect based on context
                if len(class_codes) == 1:
                    return redirect('primepath_routinetest:manage_class_students', class_code=class_codes[0])
                else:
                    return redirect('primepath_routinetest:student_list')
                    
        except Exception as e:
            messages.error(request, f"Error creating student: {str(e)}")
    
    # Get classes teacher has access to
    if teacher.is_head_teacher:
        available_classes = CLASS_CODE_CHOICES
    else:
        teacher_classes = TeacherClassAssignment.objects.filter(
            teacher=teacher,
            is_active=True
        ).values_list('class_code', flat=True)
        available_classes = [(code, name) for code, name in CLASS_CODE_CHOICES if code in teacher_classes]
    
    return render(request, 'primepath_routinetest/student_management/create_student.html', {
        'all_classes': available_classes
    })


@login_required
def student_list(request):
    """View all students (for admins/head teachers)"""
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        messages.error(request, "Teacher profile not found")
        return redirect('primepath_routinetest:classes_exams')
    
    # Only head teachers can see all students
    if not teacher.is_head_teacher:
        # Regular teachers see only students in their classes
        teacher_classes = TeacherClassAssignment.objects.filter(
            teacher=teacher,
            is_active=True
        ).values_list('class_code', flat=True)
        
        students = StudentProfile.objects.filter(
            class_assignments__class_code__in=teacher_classes,
            class_assignments__is_active=True
        ).distinct().select_related('user').annotate(
            class_count=Count('class_assignments', filter=Q(class_assignments__is_active=True))
        ).order_by('user__last_name')
    else:
        # Head teachers see all students
        students = StudentProfile.objects.all().select_related('user').annotate(
            class_count=Count('class_assignments', filter=Q(class_assignments__is_active=True))
        ).order_by('user__last_name')
    
    context = {
        'students': students,
        'is_head_teacher': teacher.is_head_teacher
    }
    
    return render(request, 'primepath_routinetest/student_management/student_list.html', context)
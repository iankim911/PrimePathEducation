"""
BUILDER: Day 3 - Student Management Views
Teacher views for managing students in their classes
"""
import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError, transaction
from django.core.paginator import Paginator
from django.db.models import Q
from core.models import Teacher, Student
from primepath_routinetest.models import Class, StudentEnrollment
from common.mixins import TeacherRequiredMixin


def teacher_required(view_func):
    """Decorator to ensure user is a teacher"""
    @login_required
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
        
        # Check if user has teacher profile
        try:
            teacher = request.user.teacher_profile
        except:
            return JsonResponse({'status': 'error', 'message': 'Teacher profile not found'}, status=403)
        
        # Add teacher to request for convenience
        request.teacher = teacher
        return view_func(request, *args, **kwargs)
    
    return wrapped


@teacher_required
def view_class_students(request, class_id):
    """View students enrolled in a specific class"""
    # Get the class and verify teacher has access
    class_obj = get_object_or_404(Class, id=class_id)
    
    # Check if teacher is assigned to this class
    if request.teacher not in class_obj.assigned_teachers.all():
        return JsonResponse({
            'status': 'error',
            'message': 'You do not have permission to view this class'
        }, status=403)
    
    # Get enrolled students
    enrollments = StudentEnrollment.objects.filter(
        class_assigned=class_obj,
        status='active'
    ).select_related('student')
    
    # Prepare student data
    students = []
    for enrollment in enrollments:
        students.append({
            'id': str(enrollment.student.id),
            'name': enrollment.student.name,
            'grade_level': enrollment.student.current_grade_level,
            'parent_email': enrollment.student.parent_email,
            'parent_phone': enrollment.student.parent_phone,
            'enrollment_date': enrollment.enrollment_date.isoformat(),
            'enrollment_id': str(enrollment.id)
        })
    
    return JsonResponse({
        'status': 'success',
        'class': {
            'id': str(class_obj.id),
            'name': class_obj.name,
            'grade_level': class_obj.grade_level,
            'section': class_obj.section
        },
        'students': students,
        'total_count': len(students)
    })


@teacher_required
@require_http_methods(["POST"])
def enroll_student(request):
    """Enroll a student in a class"""
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        class_id = data.get('class_id')
        academic_year = data.get('academic_year', '2024-2025')
        
        # Validate required fields
        if not student_id or not class_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Student ID and Class ID are required'
            }, status=400)
        
        # Get student and class
        student = get_object_or_404(Student, id=student_id)
        class_obj = get_object_or_404(Class, id=class_id)
        
        # Check teacher permission
        if request.teacher not in class_obj.assigned_teachers.all():
            return JsonResponse({
                'status': 'error',
                'message': 'You do not have permission to manage this class'
            }, status=403)
        
        # Check for existing enrollment
        existing = StudentEnrollment.objects.filter(
            student=student,
            class_assigned=class_obj,
            academic_year=academic_year
        ).first()
        
        if existing:
            if existing.status == 'active':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Student is already enrolled in this class'
                }, status=400)
            else:
                # Reactivate enrollment
                existing.status = 'active'
                existing.save()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Student enrollment reactivated',
                    'enrollment_id': str(existing.id)
                })
        
        # Create new enrollment
        enrollment = StudentEnrollment.objects.create(
            student=student,
            class_assigned=class_obj,
            academic_year=academic_year,
            created_by=request.user
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Student enrolled successfully',
            'enrollment_id': str(enrollment.id)
        })
        
    except IntegrityError as e:
        return JsonResponse({
            'status': 'error',
            'message': 'Student is already enrolled in this class for this academic year'
        }, status=400)
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        }, status=500)


@teacher_required
@require_http_methods(["DELETE"])
def unenroll_student(request, enrollment_id):
    """Remove a student from a class (soft delete)"""
    enrollment = get_object_or_404(StudentEnrollment, id=enrollment_id)
    
    # Check teacher permission
    if request.teacher not in enrollment.class_assigned.assigned_teachers.all():
        return JsonResponse({
            'status': 'error',
            'message': 'You do not have permission to manage this class'
        }, status=403)
    
    # Soft delete - change status to inactive
    enrollment.status = 'inactive'
    enrollment.save()
    
    return JsonResponse({
        'status': 'success',
        'message': 'Student removed from class'
    })


@teacher_required
@require_http_methods(["PUT"])
def update_student(request, student_id):
    """Update student information"""
    try:
        data = json.loads(request.body)
        student = get_object_or_404(Student, id=student_id)
        
        # Check if teacher has access to at least one class the student is in
        teacher_classes = Class.objects.filter(assigned_teachers=request.teacher)
        student_classes = student.enrolled_classes.all()
        
        if not teacher_classes.filter(id__in=student_classes.values_list('id', flat=True)).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'You do not have permission to update this student'
            }, status=403)
        
        # Update allowed fields
        if 'parent_email' in data:
            student.parent_email = data['parent_email']
        if 'parent_phone' in data:
            student.parent_phone = data['parent_phone']
        if 'notes' in data:
            student.notes = data['notes']
        if 'current_grade_level' in data:
            student.current_grade_level = data['current_grade_level']
        
        student.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Student information updated'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)


@teacher_required
def search_students(request):
    """Search for students"""
    query = request.GET.get('query', '')
    grade_level = request.GET.get('grade_level', '')
    page = request.GET.get('page', 1)
    
    # Base queryset
    students = Student.objects.filter(is_active=True)
    
    # Apply filters
    if query:
        students = students.filter(
            Q(name__icontains=query) |
            Q(parent_email__icontains=query)
        )
    
    if grade_level:
        students = students.filter(current_grade_level=grade_level)
    
    # For teachers, optionally filter to only students in their classes
    if not request.user.is_superuser:
        # Get teacher's classes
        teacher_classes = Class.objects.filter(assigned_teachers=request.teacher)
        # Filter students to those in teacher's classes
        students = students.filter(
            enrollments__class_assigned__in=teacher_classes,
            enrollments__status='active'
        ).distinct()
    
    # Paginate results
    paginator = Paginator(students, 20)
    page_obj = paginator.get_page(page)
    
    # Prepare results
    results = []
    for student in page_obj:
        results.append({
            'id': str(student.id),
            'name': student.name,
            'current_grade_level': student.current_grade_level,
            'parent_email': student.parent_email,
            'parent_phone': student.parent_phone
        })
    
    return JsonResponse({
        'status': 'success',
        'results': results,
        'total_count': paginator.count,
        'page': page_obj.number,
        'total_pages': paginator.num_pages
    })


@teacher_required
@require_http_methods(["POST"])
def bulk_enroll_students(request):
    """Bulk enroll multiple students in a class"""
    try:
        data = json.loads(request.body)
        class_id = data.get('class_id')
        student_ids = data.get('student_ids', [])
        academic_year = data.get('academic_year', '2024-2025')
        
        if not class_id or not student_ids:
            return JsonResponse({
                'status': 'error',
                'message': 'Class ID and student IDs are required'
            }, status=400)
        
        class_obj = get_object_or_404(Class, id=class_id)
        
        # Check teacher permission
        if request.teacher not in class_obj.assigned_teachers.all():
            return JsonResponse({
                'status': 'error',
                'message': 'You do not have permission to manage this class'
            }, status=403)
        
        enrolled_count = 0
        skipped_count = 0
        errors = []
        
        with transaction.atomic():
            for student_id in student_ids:
                try:
                    student = Student.objects.get(id=student_id)
                    
                    # Check for existing enrollment
                    existing = StudentEnrollment.objects.filter(
                        student=student,
                        class_assigned=class_obj,
                        academic_year=academic_year
                    ).first()
                    
                    if existing:
                        if existing.status != 'active':
                            existing.status = 'active'
                            existing.save()
                            enrolled_count += 1
                        else:
                            skipped_count += 1
                    else:
                        StudentEnrollment.objects.create(
                            student=student,
                            class_assigned=class_obj,
                            academic_year=academic_year,
                            created_by=request.user
                        )
                        enrolled_count += 1
                        
                except Student.DoesNotExist:
                    errors.append(f"Student {student_id} not found")
                except Exception as e:
                    errors.append(f"Error enrolling student {student_id}: {str(e)}")
        
        return JsonResponse({
            'status': 'success',
            'enrolled_count': enrolled_count,
            'skipped_count': skipped_count,
            'errors': errors,
            'message': f'Successfully enrolled {enrolled_count} students'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)


@teacher_required
def teacher_dashboard(request):
    """Teacher dashboard showing their classes and students"""
    teacher = request.teacher
    
    # Get teacher's classes
    classes = Class.objects.filter(
        assigned_teachers=teacher,
        is_active=True
    ).prefetch_related('enrollments__student')
    
    # Prepare dashboard data
    dashboard_data = {
        'teacher_name': teacher.name,
        'classes': []
    }
    
    for class_obj in classes:
        active_enrollments = class_obj.enrollments.filter(status='active')
        dashboard_data['classes'].append({
            'id': str(class_obj.id),
            'name': class_obj.name,
            'grade_level': class_obj.grade_level,
            'section': class_obj.section,
            'student_count': active_enrollments.count()
        })
    
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse(dashboard_data)
    
    return render(request, 'primepath_routinetest/teacher_dashboard.html', dashboard_data)


@teacher_required
def teacher_classes(request):
    """View all classes assigned to the teacher"""
    teacher = request.teacher
    
    classes = Class.objects.filter(
        assigned_teachers=teacher,
        is_active=True
    ).order_by('grade_level', 'section', 'name')
    
    if request.headers.get('Accept') == 'application/json':
        classes_data = []
        for class_obj in classes:
            classes_data.append({
                'id': str(class_obj.id),
                'name': class_obj.name,
                'grade_level': class_obj.grade_level,
                'section': class_obj.section,
                'student_count': class_obj.student_count
            })
        return JsonResponse({'classes': classes_data})
    
    return render(request, 'primepath_routinetest/teacher_classes.html', {'classes': classes})
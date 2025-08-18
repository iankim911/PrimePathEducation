"""
BUILDER: Day 4 - Exam Management Views
Views for exam upload, assignment, and administration
"""

import json
from datetime import datetime
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.utils import timezone
from django.db.models import Q, Avg, Max, Min, Count
from django.contrib import messages

from core.models import Teacher, Student
from primepath_routinetest.models import (
    Class, StudentEnrollment,
    RoutineExam, ExamAssignment, StudentExamAssignment, ExamAttempt
)


def is_admin(user):
    """Check if user is admin"""
    return user.is_superuser or user.is_staff


def is_teacher(user):
    """Check if user is a teacher"""
    return hasattr(user, 'teacher_profile')


def admin_required(view_func):
    """Decorator to require admin access"""
    def wrapper(request, *args, **kwargs):
        if not is_admin(request.user):
            return HttpResponseForbidden("Admin access required")
        return view_func(request, *args, **kwargs)
    return login_required(wrapper)


def teacher_required(view_func):
    """Decorator to require teacher access"""
    def wrapper(request, *args, **kwargs):
        if not is_teacher(request.user) and not is_admin(request.user):
            return HttpResponseForbidden("Teacher access required")
        return view_func(request, *args, **kwargs)
    return login_required(wrapper)


# ==================== ADMIN VIEWS ====================

@admin_required
@require_http_methods(["POST"])
def upload_exam(request):
    """Admin uploads a new exam PDF"""
    try:
        name = request.POST.get('name')
        exam_type = request.POST.get('exam_type')
        curriculum_level = request.POST.get('curriculum_level')
        academic_year = request.POST.get('academic_year')
        quarter = request.POST.get('quarter')
        pdf_file = request.FILES.get('pdf_file')
        
        # Validate required fields
        if not all([name, exam_type, curriculum_level, academic_year, quarter]):
            return HttpResponseBadRequest("Missing required fields")
        
        # Create exam
        exam = RoutineExam.objects.create(
            name=name,
            exam_type=exam_type,
            curriculum_level=curriculum_level,
            academic_year=academic_year,
            quarter=quarter,
            pdf_file=pdf_file,
            created_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'exam_id': str(exam.id),
            'message': 'Exam uploaded successfully'
        }, status=201)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@admin_required
@require_http_methods(["POST"])
def set_answer_key(request, exam_id):
    """Admin sets answer key for an exam"""
    try:
        exam = get_object_or_404(RoutineExam, id=exam_id)
        data = json.loads(request.body)
        answer_key = data.get('answer_key', {})
        
        # Validate answer key format
        if not isinstance(answer_key, dict):
            return HttpResponseBadRequest("Invalid answer key format")
        
        exam.answer_key = answer_key
        exam.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Answer key saved successfully'
        })
        
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


# ==================== TEACHER VIEWS ====================

@teacher_required
def list_available_exams(request):
    """Teacher views available exams"""
    try:
        # Get filter parameters
        curriculum_level = request.GET.get('curriculum_level')
        exam_type = request.GET.get('exam_type')
        quarter = request.GET.get('quarter')
        
        # Build query
        exams = RoutineExam.objects.filter(is_active=True)
        
        if curriculum_level:
            exams = exams.filter(curriculum_level=curriculum_level)
        if exam_type:
            exams = exams.filter(exam_type=exam_type)
        if quarter:
            exams = exams.filter(quarter=quarter)
        
        # Serialize exams
        exam_list = []
        for exam in exams:
            exam_list.append({
                'id': str(exam.id),
                'name': exam.name,
                'exam_type': exam.exam_type,
                'curriculum_level': exam.curriculum_level,
                'quarter': exam.quarter,
                'academic_year': exam.academic_year,
                'has_answer_key': bool(exam.answer_key)
            })
        
        return JsonResponse({
            'exams': exam_list,
            'count': len(exam_list)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@teacher_required
@require_http_methods(["POST"])
def assign_exam_to_class(request):
    """Teacher assigns exam to entire class"""
    try:
        data = json.loads(request.body)
        exam_id = data.get('exam_id')
        class_id = data.get('class_id')
        deadline_str = data.get('deadline')
        is_bulk = data.get('is_bulk', True)
        
        # Parse deadline
        deadline_dt = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
        # Make aware only if naive
        if timezone.is_naive(deadline_dt):
            deadline = timezone.make_aware(deadline_dt)
        else:
            deadline = deadline_dt
        
        # Get objects
        exam = get_object_or_404(RoutineExam, id=exam_id)
        class_obj = get_object_or_404(Class, id=class_id)
        
        # Verify teacher has access to this class
        teacher = request.user.teacher_profile
        if not is_admin(request.user) and teacher not in class_obj.assigned_teachers.all():
            return HttpResponseForbidden("You don't have access to this class")
        
        # Create assignment
        assignment = ExamAssignment.objects.create(
            exam=exam,
            class_assigned=class_obj,
            assigned_by=teacher,
            deadline=deadline,
            is_bulk_assignment=is_bulk
        )
        
        # Create individual student assignments for all enrolled students
        enrollments = StudentEnrollment.objects.filter(
            class_assigned=class_obj,
            status='active'
        )
        
        for enrollment in enrollments:
            StudentExamAssignment.objects.create(
                student=enrollment.student,
                exam_assignment=assignment,
                status='assigned'
            )
        
        return JsonResponse({
            'success': True,
            'assignment_id': str(assignment.id),
            'students_assigned': enrollments.count()
        }, status=201)
        
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@teacher_required
@require_http_methods(["POST"])
def assign_exam_to_students(request):
    """Teacher assigns different exams to individual students"""
    try:
        data = json.loads(request.body)
        assignments = data.get('assignments', [])
        
        created_count = 0
        teacher = request.user.teacher_profile
        
        for assignment_data in assignments:
            student_id = assignment_data.get('student_id')
            exam_id = assignment_data.get('exam_id')
            deadline_str = assignment_data.get('deadline')
            
            # Parse deadline
            deadline_dt = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
            # Make aware only if naive
            if timezone.is_naive(deadline_dt):
                deadline = timezone.make_aware(deadline_dt)
            else:
                deadline = deadline_dt
            
            # Get objects
            student = get_object_or_404(Student, id=student_id)
            exam = get_object_or_404(RoutineExam, id=exam_id)
            
            # Find student's class
            enrollment = StudentEnrollment.objects.filter(
                student=student,
                status='active'
            ).first()
            
            if not enrollment:
                continue
            
            class_obj = enrollment.class_assigned
            
            # Verify teacher has access
            if not is_admin(request.user) and teacher not in class_obj.assigned_teachers.all():
                continue
            
            # Create or get assignment
            assignment, created = ExamAssignment.objects.get_or_create(
                exam=exam,
                class_assigned=class_obj,
                deadline=deadline,
                defaults={
                    'assigned_by': teacher,
                    'is_bulk_assignment': False
                }
            )
            
            # Create student assignment
            StudentExamAssignment.objects.get_or_create(
                student=student,
                exam_assignment=assignment,
                defaults={'status': 'assigned'}
            )
            
            created_count += 1
        
        return JsonResponse({
            'success': True,
            'assignments_created': created_count
        }, status=201)
        
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@teacher_required
@require_http_methods(["POST"])
def extend_deadline(request, assignment_id):
    """Teacher extends deadline for an assignment"""
    try:
        assignment = get_object_or_404(ExamAssignment, id=assignment_id)
        
        # Verify teacher has access
        teacher = request.user.teacher_profile
        if not is_admin(request.user) and teacher not in assignment.class_assigned.assigned_teachers.all():
            return HttpResponseForbidden("You don't have access to this assignment")
        
        data = json.loads(request.body)
        new_deadline_str = data.get('new_deadline')
        new_deadline_dt = datetime.fromisoformat(new_deadline_str.replace('Z', '+00:00'))
        # Make aware only if naive
        if timezone.is_naive(new_deadline_dt):
            new_deadline = timezone.make_aware(new_deadline_dt)
        else:
            new_deadline = new_deadline_dt
        
        if assignment.extend_deadline(new_deadline):
            return JsonResponse({
                'success': True,
                'message': 'Deadline extended successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'New deadline must be later than current deadline'
            }, status=400)
            
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


# ==================== STUDENT VIEWS ====================

@login_required
def view_assigned_exams(request):
    """Student views their assigned exams"""
    try:
        # Get student profile
        if not hasattr(request.user, 'student_profile'):
            return JsonResponse({'exams': []})
        
        student = request.user.student_profile
        
        # Get assignments
        assignments = StudentExamAssignment.objects.filter(
            student=student
        ).select_related('exam_assignment__exam', 'exam_assignment__class_assigned')
        
        exam_list = []
        for assignment in assignments:
            exam_list.append({
                'id': str(assignment.exam_assignment.exam.id),
                'name': assignment.exam_assignment.exam.name,
                'exam_type': assignment.exam_assignment.exam.exam_type,
                'class': assignment.exam_assignment.class_assigned.name,
                'deadline': assignment.exam_assignment.deadline.isoformat(),
                'status': assignment.status,
                'can_take': assignment.can_take_exam()
            })
        
        return JsonResponse({
            'exams': exam_list
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def start_exam(request, exam_id):
    """Student starts taking an exam"""
    try:
        # Get student profile
        if not hasattr(request.user, 'student_profile'):
            return HttpResponseForbidden("Student access required")
        
        student = request.user.student_profile
        exam = get_object_or_404(RoutineExam, id=exam_id)
        
        # Find student's assignment for this exam
        student_assignment = StudentExamAssignment.objects.filter(
            student=student,
            exam_assignment__exam=exam
        ).first()
        
        if not student_assignment:
            return HttpResponseForbidden("You are not assigned this exam")
        
        if not student_assignment.can_take_exam():
            return HttpResponseForbidden("Cannot take exam - deadline passed or already completed")
        
        # Mark as started
        student_assignment.mark_as_started()
        
        # Get or create attempt
        attempt_count = ExamAttempt.objects.filter(
            student=student,
            exam=exam
        ).count()
        
        attempt = ExamAttempt.objects.create(
            student=student,
            exam=exam,
            assignment=student_assignment,
            attempt_number=attempt_count + 1
        )
        
        return JsonResponse({
            'success': True,
            'attempt_id': str(attempt.id),
            'attempt_number': attempt.attempt_number
        }, status=201)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def auto_save_progress(request, exam_id):
    """Auto-save student's exam progress"""
    try:
        # Get student profile
        if not hasattr(request.user, 'student_profile'):
            return HttpResponseForbidden("Student access required")
        
        student = request.user.student_profile
        
        data = json.loads(request.body)
        attempt_id = data.get('attempt_id')
        answers = data.get('answers', {})
        
        attempt = get_object_or_404(ExamAttempt, id=attempt_id, student=student)
        
        if attempt.is_submitted:
            return HttpResponseBadRequest("Cannot modify submitted exam")
        
        attempt.auto_save(answers)
        
        return JsonResponse({
            'success': True,
            'message': 'Progress saved'
        })
        
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def submit_exam(request, exam_id):
    """Student submits completed exam"""
    try:
        # Get student profile
        if not hasattr(request.user, 'student_profile'):
            return HttpResponseForbidden("Student access required")
        
        student = request.user.student_profile
        
        data = json.loads(request.body)
        attempt_id = data.get('attempt_id')
        
        attempt = get_object_or_404(ExamAttempt, id=attempt_id, student=student)
        
        if attempt.is_submitted:
            return HttpResponseBadRequest("Exam already submitted")
        
        # Use auto-saved answers as final answers if not provided
        if attempt.auto_saved_data and not attempt.answers:
            attempt.answers = attempt.auto_saved_data
        
        # Submit attempt
        attempt.submit()
        
        return JsonResponse({
            'success': True,
            'score': float(attempt.score),
            'message': 'Exam submitted successfully'
        })
        
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
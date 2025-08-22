"""
Class Details View with Student Management and Exam Schedule Tabs
Implements comprehensive class management interface
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.db.models import Q, Count, Prefetch
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
import json
import logging
import uuid
from datetime import datetime, timedelta

from core.models import Teacher, Student
from primepath_routinetest.models import (
    Class, StudentEnrollment, RoutineExam, 
    ExamScheduleMatrix, StudentSession,
    TeacherClassAssignment
)
from primepath_routinetest.services import ExamService

logger = logging.getLogger(__name__)


@login_required
def class_details(request, class_code):
    """
    Main class details view with tabs for Student Management and Exam Schedule
    """
    console_log = {
        "view": "class_details",
        "user": request.user.username,
        "class_code": class_code,
        "timestamp": timezone.now().isoformat(),
        "request_path": request.path,
        "method": request.method
    }
    logger.info(f"[CLASS_DETAILS_VIEW] Starting view: {json.dumps(console_log)}")
    logger.debug(f"[CLASS_DETAILS_VIEW] Full request path: {request.get_full_path()}")
    
    # Check user permissions
    is_admin = request.user.is_superuser or request.user.is_staff
    teacher_profile = getattr(request.user, 'teacher_profile', None)
    
    # Get teacher's access level for this class
    access_level = None
    if teacher_profile and not is_admin:
        assignment = TeacherClassAssignment.objects.filter(
            teacher=teacher_profile,
            class_code=class_code,
            is_active=True
        ).first()
        if assignment:
            access_level = assignment.access_level
        else:
            messages.error(request, "You don't have access to this class.")
            return redirect('RoutineTest:classes_exams_unified')
    
    # For admins, always full access
    if is_admin:
        access_level = 'FULL'
    
    # Get class information (using the class_code as identifier)
    try:
        # Get class display name from ExamService
        class_display = ExamService.get_class_display_name(class_code)
        
        # Try to get or create an actual Class object
        class_obj = None
        try:
            class_obj = Class.objects.get(name=class_code)
        except Class.DoesNotExist:
            # Create a virtual class object for display
            pass
            
    except Exception as e:
        logger.error(f"Error getting class details: {e}")
        messages.error(request, "Class not found.")
        return redirect('RoutineTest:classes_exams_unified')
    
    # Get enrolled students
    enrolled_students = []
    if class_obj:
        enrollments = StudentEnrollment.objects.filter(
            class_assigned=class_obj,
            status='active'
        ).select_related('student').order_by('student__name')
        
        for enrollment in enrollments:
            student_data = {
                'id': str(enrollment.student.id),
                'enrollment_id': str(enrollment.id),
                'name': enrollment.student.name,
                'grade_level': enrollment.student.current_grade_level,
                'enrollment_date': enrollment.enrollment_date,
                'parent_phone': enrollment.student.parent_phone,
                'parent_email': enrollment.student.parent_email,
                'exam_history': get_student_exam_history(enrollment.student, class_code)
            }
            enrolled_students.append(student_data)
    
    # Get exam schedule for this class
    current_year = str(datetime.now().year)
    
    # Get monthly (Review) schedules
    monthly_schedules = ExamScheduleMatrix.objects.filter(
        class_code=class_code,
        academic_year=current_year,
        time_period_type='MONTHLY'
    ).prefetch_related('exams').order_by('time_period_value')
    
    # Get quarterly schedules
    quarterly_schedules = ExamScheduleMatrix.objects.filter(
        class_code=class_code,
        academic_year=current_year,
        time_period_type='QUARTERLY'
    ).prefetch_related('exams').order_by('time_period_value')
    
    # Process schedules for display
    logger.info(f"[CLASS_DETAILS] Processing schedules for class {class_code}")
    monthly_data = []
    for schedule in monthly_schedules:
        try:
            logger.debug(f"[CLASS_DETAILS] Processing monthly schedule: {schedule.time_period_value}")
            exam_list = schedule.get_detailed_exam_list()
            logger.debug(f"[CLASS_DETAILS] Retrieved {len(exam_list)} exams for {schedule.time_period_value}")
            
            schedule_data = {
                'id': str(schedule.id),
                'month': schedule.time_period_value,
                'month_display': schedule.get_time_period_display(),
                'exam_count': schedule.get_exam_count(),
                'exams': exam_list,
                'status': schedule.status,
                'status_icon': schedule.get_status_icon(),
                'scheduled_date': schedule.scheduled_date,
                'scheduled_time': f"{schedule.scheduled_start_time} - {schedule.scheduled_end_time}" if schedule.scheduled_start_time else None,
                'can_edit': access_level in ['FULL', 'CO_TEACHER'] or is_admin
            }
            monthly_data.append(schedule_data)
            
        except Exception as e:
            logger.error(f"[CLASS_DETAILS] Error processing monthly schedule {schedule.time_period_value}: {str(e)}")
            # Add minimal data on error
            monthly_data.append({
                'id': str(schedule.id),
                'month': schedule.time_period_value,
                'month_display': 'Error loading',
                'exam_count': 0,
                'exams': [],
                'status': 'ERROR',
                'status_icon': '❌',
                'scheduled_date': None,
                'scheduled_time': None,
                'can_edit': False
            })
    
    quarterly_data = []
    for schedule in quarterly_schedules:
        try:
            logger.debug(f"[CLASS_DETAILS] Processing quarterly schedule: {schedule.time_period_value}")
            exam_list = schedule.get_detailed_exam_list()
            logger.debug(f"[CLASS_DETAILS] Retrieved {len(exam_list)} exams for {schedule.time_period_value}")
            
            schedule_data = {
                'id': str(schedule.id),
                'quarter': schedule.time_period_value,
                'quarter_display': schedule.get_time_period_display(),
                'exam_count': schedule.get_exam_count(),
                'exams': exam_list,
                'status': schedule.status,
                'status_icon': schedule.get_status_icon(),
                'scheduled_date': schedule.scheduled_date,
                'scheduled_time': f"{schedule.scheduled_start_time} - {schedule.scheduled_end_time}" if schedule.scheduled_start_time else None,
                'can_edit': access_level in ['FULL', 'CO_TEACHER'] or is_admin
            }
            quarterly_data.append(schedule_data)
            
        except Exception as e:
            logger.error(f"[CLASS_DETAILS] Error processing quarterly schedule {schedule.time_period_value}: {str(e)}")
            # Add minimal data on error
            quarterly_data.append({
                'id': str(schedule.id),
                'quarter': schedule.time_period_value,
                'quarter_display': 'Error loading',
                'exam_count': 0,
                'exams': [],
                'status': 'ERROR',
                'status_icon': '❌',
                'scheduled_date': None,
                'scheduled_time': None,
                'can_edit': False
            })
    
    # Get available students to add (not enrolled in this class)
    available_students = []
    if class_obj:
        enrolled_student_ids = enrollments.values_list('student_id', flat=True)
        available = Student.objects.filter(
            is_active=True
        ).exclude(id__in=enrolled_student_ids).order_by('name')
        
        for student in available:
            available_students.append({
                'id': str(student.id),
                'name': student.name,
                'grade_level': student.current_grade_level
            })
    
    # Context for template
    context = {
        'class_code': class_code,
        'class_display': class_display,
        'class_obj': class_obj,
        'is_admin': is_admin,
        'access_level': access_level,
        'can_edit': access_level in ['FULL', 'CO_TEACHER'] or is_admin,
        
        # Student Management Tab
        'enrolled_students': enrolled_students,
        'available_students': available_students,
        'student_count': len(enrolled_students),
        
        # Exam Schedule Tab
        'monthly_schedules': monthly_data,
        'quarterly_schedules': quarterly_data,
        'current_year': current_year,
        
        # For debugging
        'debug_info': {
            'user': request.user.username,
            'is_admin': is_admin,
            'access_level': access_level,
            'class_exists': class_obj is not None
        }
    }
    
    return render(request, 'primepath_routinetest/class_details.html', context)


def get_student_exam_history(student, class_code):
    """Get exam history for a student in a specific class"""
    # StudentSession uses student_name, not a foreign key to Student
    sessions = StudentSession.objects.filter(
        student_name=student.name,
        exam__class_codes__contains=[class_code]
    ).select_related('exam').order_by('-started_at')[:5]
    
    history = []
    for session in sessions:
        history.append({
            'exam_name': session.exam.name,
            'started_at': session.started_at,
            'completed_at': session.completed_at,
            'score': session.score if hasattr(session, 'score') else None,
            'status': 'Completed' if session.completed_at else 'In Progress'
        })
    
    return history


@login_required
@require_http_methods(["POST"])
def add_student_to_class(request, class_code):
    """Add a student to a class"""
    console_log = {
        "view": "add_student_to_class",
        "user": request.user.username,
        "class_code": class_code,
        "method": request.method
    }
    logger.info(f"[ADD_STUDENT] {json.dumps(console_log)}")
    
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        
        # Check permissions
        is_admin = request.user.is_superuser or request.user.is_staff
        if not is_admin:
            teacher_profile = getattr(request.user, 'teacher_profile', None)
            if not teacher_profile:
                return JsonResponse({'success': False, 'error': 'No teacher profile'}, status=403)
            
            assignment = TeacherClassAssignment.objects.filter(
                teacher=teacher_profile,
                class_code=class_code,
                is_active=True,
                access_level__in=['FULL', 'CO_TEACHER']
            ).first()
            
            if not assignment:
                return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
        
        # Get or create class
        class_obj, created = Class.objects.get_or_create(
            name=class_code,
            defaults={
                'grade_level': ExamService.get_class_display_name(class_code),
                'created_by': request.user
            }
        )
        
        # Get student
        student = Student.objects.get(id=student_id)
        
        # Create enrollment
        enrollment, created = StudentEnrollment.objects.get_or_create(
            student=student,
            class_assigned=class_obj,
            defaults={
                'status': 'active',
                'created_by': request.user
            }
        )
        
        if not created:
            enrollment.status = 'active'
            enrollment.save()
        
        return JsonResponse({
            'success': True,
            'message': f'{student.name} added to class',
            'student': {
                'id': str(student.id),
                'name': student.name,
                'enrollment_id': str(enrollment.id)
            }
        })
        
    except Student.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Student not found'}, status=404)
    except Exception as e:
        logger.error(f"Error adding student to class: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def remove_student_from_class(request, class_code):
    """Remove a student from a class"""
    console_log = {
        "view": "remove_student_from_class",
        "user": request.user.username,
        "class_code": class_code
    }
    logger.info(f"[REMOVE_STUDENT] {json.dumps(console_log)}")
    
    try:
        data = json.loads(request.body)
        enrollment_id = data.get('enrollment_id')
        
        # Check permissions (similar to add_student)
        is_admin = request.user.is_superuser or request.user.is_staff
        if not is_admin:
            teacher_profile = getattr(request.user, 'teacher_profile', None)
            if not teacher_profile:
                return JsonResponse({'success': False, 'error': 'No teacher profile'}, status=403)
            
            assignment = TeacherClassAssignment.objects.filter(
                teacher=teacher_profile,
                class_code=class_code,
                is_active=True,
                access_level__in=['FULL', 'CO_TEACHER']
            ).first()
            
            if not assignment:
                return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
        
        # Update enrollment status
        enrollment = StudentEnrollment.objects.get(id=enrollment_id)
        enrollment.status = 'inactive'
        enrollment.save()
        
        return JsonResponse({
            'success': True,
            'message': f'{enrollment.student.name} removed from class'
        })
        
    except StudentEnrollment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Enrollment not found'}, status=404)
    except Exception as e:
        logger.error(f"Error removing student from class: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def start_exam_for_class(request, class_code):
    """Start an exam for all students in a class"""
    console_log = {
        "view": "start_exam_for_class",
        "user": request.user.username,
        "class_code": class_code
    }
    logger.info(f"[START_EXAM] {json.dumps(console_log)}")
    
    try:
        data = json.loads(request.body)
        exam_id = data.get('exam_id')
        schedule_id = data.get('schedule_id')
        
        # Get exam
        exam = RoutineExam.objects.get(id=exam_id)
        
        # Get class and enrolled students
        class_obj = Class.objects.get(name=class_code)
        enrollments = StudentEnrollment.objects.filter(
            class_assigned=class_obj,
            status='active'
        ).select_related('student')
        
        # Create exam sessions for all students
        sessions_created = []
        with transaction.atomic():
            for enrollment in enrollments:
                # StudentSession uses student_name, not a foreign key
                session, created = StudentSession.objects.get_or_create(
                    student_name=enrollment.student.name,
                    exam=exam,
                    defaults={
                        'started_at': timezone.now(),
                        'parent_phone': enrollment.student.parent_phone or '',
                        'grade': int(enrollment.student.current_grade_level[1:]) if enrollment.student.current_grade_level[1:].isdigit() else 1,
                        'academic_rank': 'TOP_50',  # Default rank
                        'school': None  # Will be set if available
                    }
                )
                
                if created:
                    sessions_created.append({
                        'student_name': enrollment.student.name,
                        'session_id': str(session.id)
                    })
            
            # Update schedule status
            if schedule_id:
                schedule = ExamScheduleMatrix.objects.get(id=schedule_id)
                schedule.status = 'IN_PROGRESS'
                schedule.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Exam started for {len(sessions_created)} students',
            'sessions': sessions_created
        })
        
    except Exception as e:
        logger.error(f"Error starting exam: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def delete_exam_from_schedule(request, class_code):
    """Delete an exam from the schedule"""
    console_log = {
        "view": "delete_exam_from_schedule",
        "user": request.user.username,
        "class_code": class_code
    }
    logger.info(f"[DELETE_EXAM_SCHEDULE] {json.dumps(console_log)}")
    
    try:
        data = json.loads(request.body)
        exam_id = data.get('exam_id')
        schedule_id = data.get('schedule_id')
        
        # Check permissions
        is_admin = request.user.is_superuser or request.user.is_staff
        if not is_admin:
            teacher_profile = getattr(request.user, 'teacher_profile', None)
            if not teacher_profile:
                return JsonResponse({'success': False, 'error': 'No teacher profile'}, status=403)
            
            assignment = TeacherClassAssignment.objects.filter(
                teacher=teacher_profile,
                class_code=class_code,
                is_active=True,
                access_level='FULL'
            ).first()
            
            if not assignment:
                return JsonResponse({'success': False, 'error': 'Only full access teachers can delete exams'}, status=403)
        
        # Remove exam from schedule
        schedule = ExamScheduleMatrix.objects.get(id=schedule_id)
        exam = RoutineExam.objects.get(id=exam_id)
        
        schedule.remove_exam(exam, request.user)
        
        return JsonResponse({
            'success': True,
            'message': f'Exam removed from schedule'
        })
        
    except Exception as e:
        logger.error(f"Error deleting exam from schedule: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def get_student_details(request, student_id):
    """Get detailed information about a student"""
    try:
        student = Student.objects.get(id=student_id)
        
        # Get exam history - StudentSession uses student_name
        sessions = StudentSession.objects.filter(
            student_name=student.name
        ).select_related('exam').order_by('-started_at')[:10]
        
        exam_history = []
        for session in sessions:
            exam_history.append({
                'exam_name': session.exam.name,
                'exam_type': session.exam.exam_type,
                'started_at': session.started_at.isoformat() if session.started_at else None,
                'completed_at': session.completed_at.isoformat() if session.completed_at else None,
                'duration': str(session.completed_at - session.started_at) if session.completed_at and session.started_at else None,
                'status': 'Completed' if session.completed_at else 'In Progress'
            })
        
        return JsonResponse({
            'success': True,
            'student': {
                'id': str(student.id),
                'name': student.name,
                'grade_level': student.current_grade_level,
                'date_of_birth': student.date_of_birth.isoformat() if student.date_of_birth else None,
                'age': student.get_age(),
                'parent_phone': student.parent_phone,
                'parent_email': student.parent_email,
                'notes': student.notes,
                'created_at': student.created_at.isoformat(),
                'exam_history': exam_history
            }
        })
        
    except Student.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Student not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting student details: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
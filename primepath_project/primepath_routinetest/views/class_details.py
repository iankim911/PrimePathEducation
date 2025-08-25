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
    Class, StudentEnrollment, RoutineExam, Exam,
    ExamScheduleMatrix, StudentSession,
    TeacherClassAssignment, ExamLaunchSession
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
            # Look for class by section (C5) rather than full name 
            class_obj = Class.objects.get(section=class_code)
        except Class.DoesNotExist:
            # Create a virtual class object for display
            logger.warning(f"Class with section {class_code} not found in database")
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
                'can_edit': access_level == 'FULL' or is_admin
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
                'can_edit': access_level == 'FULL' or is_admin
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
        'can_edit': access_level == 'FULL' or is_admin,
        
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
    # SQLite doesn't support contains lookup on JSON fields, so we'll filter in Python
    all_sessions = StudentSession.objects.filter(
        student_name=student.name
    ).select_related('exam').order_by('-started_at')
    
    # Filter sessions where class_code is in exam's class_codes
    sessions = []
    for session in all_sessions:
        if session.exam and session.exam.class_codes:
            if isinstance(session.exam.class_codes, list) and class_code in session.exam.class_codes:
                sessions.append(session)
                if len(sessions) >= 5:  # Only need top 5
                    break
    
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
                access_level='FULL'
            ).first()
            
            if not assignment:
                return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
        
        # Get or create class (look by section, not name)
        class_obj, created = Class.objects.get_or_create(
            section=class_code,
            defaults={
                'name': f'{class_code} - {ExamService.get_class_display_name(class_code)}',
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
                access_level='FULL'
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
    """Enhanced exam launch with student selection and duration modification"""
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
        
        # Enhanced: Get duration and selected students from request
        custom_duration = data.get('duration_minutes')
        selected_student_ids = data.get('selected_students', [])
        
        logger.info(f"[START_EXAM_ENHANCED] Custom duration: {custom_duration}, Selected students: {len(selected_student_ids)}")
        
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
                return JsonResponse({'success': False, 'error': 'Only full access teachers can launch exams'}, status=403)
        
        # Get exam - Use RoutineExam model which is what ExamScheduleMatrix uses
        exam = RoutineExam.objects.get(id=exam_id)
        
        # Get class and enrolled students
        class_obj = Class.objects.get(section=class_code)
        enrollments = StudentEnrollment.objects.filter(
            class_assigned=class_obj,
            status='active'
        ).select_related('student')
        
        # Check if students were selected
        if not selected_student_ids:
            return JsonResponse({'success': False, 'error': 'No students selected for exam'}, status=400)
        
        # Filter enrollments based on selected students
        enrollments = enrollments.filter(student_id__in=selected_student_ids)
        logger.info(f"[START_EXAM_FILTER] Filtered to {enrollments.count()} students")
        
        if not enrollments.exists():
            return JsonResponse({'success': False, 'error': 'Selected students not found in this class'}, status=400)
        
        # Create ExamLaunchSession for student portal access
        launch_session = ExamLaunchSession.objects.create(
            exam=exam,
            class_code=class_code,
            launched_by=request.user,
            duration_minutes=custom_duration or exam.duration,
            expires_at=timezone.now() + timedelta(hours=24),  # 24 hour expiry
            selected_student_ids=[str(sid) for sid in selected_student_ids] if selected_student_ids else [],
            metadata={
                'schedule_id': str(schedule_id) if schedule_id else None,
                'launched_from': 'teacher_interface',
                'original_duration': exam.duration
            }
        )
        
        logger.info(f"[EXAM_LAUNCH] Created ExamLaunchSession {launch_session.id} for class {class_code}")
        
        # Send notifications to students
        try:
            from primepath_student.services import NotificationService
            notifications = NotificationService.notify_exam_launch(launch_session, selected_student_ids)
            NotificationService.schedule_exam_reminders(launch_session)
            logger.info(f"[EXAM_LAUNCH] Sent notifications to students")
        except Exception as e:
            logger.warning(f"[EXAM_LAUNCH] Could not send notifications: {e}")
        
        # Create exam sessions for selected students
        sessions_created = []
        
        # Also create StudentExamSession records for the new student portal
        from primepath_student.models import StudentProfile, StudentClassAssignment, StudentExamSession
        
        with transaction.atomic():
            for enrollment in enrollments:
                # Skip StudentSession creation for RoutineExam as it expects placement_test.Exam objects
                # The ExamLaunchSession will handle student access for RoutineExam
                session = None
                created = False
                
                # Log that we're creating access through ExamLaunchSession instead
                logger.info(f"[EXAM_LAUNCH] Student {enrollment.student.name} will access via ExamLaunchSession {launch_session.id}")
                
                # Track student for launch session
                sessions_created.append({
                    'student_name': enrollment.student.name,
                    'student_id': str(enrollment.student.id),
                    'launch_session_id': str(launch_session.id),
                    'duration': custom_duration or exam.duration
                })
                
                # Also create/update StudentExamSession for new student portal if student has profile
                try:
                    # Try to find student profile by phone number (from parent_phone)
                    if enrollment.student.parent_phone:
                        student_profile = StudentProfile.objects.filter(
                            phone_number=enrollment.student.parent_phone
                        ).first()
                        
                        if student_profile:
                            # Check if student is assigned to this class
                            class_assignment = StudentClassAssignment.objects.filter(
                                student=student_profile,
                                class_code=class_code,
                                is_active=True
                            ).first()
                            
                            if class_assignment:
                                # Create or get StudentExamSession
                                student_exam_session, created = StudentExamSession.get_or_create_session(
                                    student=student_profile,
                                    exam=exam,
                                    class_assignment=class_assignment
                                )
                                
                                if created:
                                    logger.info(f"[STUDENT_PORTAL] Created StudentExamSession for {student_profile.name}")
                                else:
                                    # Reset if restarting
                                    student_exam_session.status = 'not_started'
                                    student_exam_session.started_at = None
                                    student_exam_session.completed_at = None
                                    student_exam_session.save()
                                    logger.info(f"[STUDENT_PORTAL] Reset StudentExamSession for {student_profile.name}")
                except Exception as e:
                    logger.warning(f"[STUDENT_PORTAL] Could not create StudentExamSession: {e}")
                    # Don't fail the whole launch if student portal integration fails
                    pass
            
            # Update schedule status
            if schedule_id:
                schedule = ExamScheduleMatrix.objects.get(id=schedule_id)
                schedule.status = 'IN_PROGRESS'
                schedule.metadata = schedule.metadata or {}
                schedule.metadata['last_launched'] = timezone.now().isoformat()
                schedule.metadata['launched_by'] = request.user.username
                if custom_duration:
                    schedule.metadata['custom_duration'] = custom_duration
                schedule.save()
        
        total_sessions = len(sessions_created)
        response_message = f'Exam launched for {total_sessions} student(s)'
        
        if custom_duration:
            response_message += f' with {custom_duration} minute duration'
        
        return JsonResponse({
            'success': True,
            'message': response_message,
            'sessions_created': sessions_created,
            'sessions_updated': [],
            'total_students': total_sessions,
            'custom_duration': custom_duration,
            'exam_name': exam.name,
            'launch_session_id': str(launch_session.id),
            'student_portal_accessible': True
        })
        
    except RoutineExam.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Exam not found'}, status=404)
    except Class.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Class not found'}, status=404)
    except Exception as e:
        logger.error(f"Error starting exam: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def launch_teacher_preview(request, class_code):
    """
    Launch Teacher Exam Preview - Teacher experiences the same interface as students
    Creates a preview session and redirects teacher to the exam-taking interface
    """
    console_log = {
        "view": "launch_teacher_preview",
        "user": request.user.username,
        "class_code": class_code,
        "timestamp": timezone.now().isoformat()
    }
    logger.info(f"[TEACHER_PREVIEW_INIT] {json.dumps(console_log)}")
    print(f"\n{'='*80}")
    print(f"[TEACHER_PREVIEW] Launching exam preview for teacher: {request.user.username}")
    print(f"{'='*80}\n")
    
    try:
        data = json.loads(request.body)
        exam_id = data.get('exam_id')
        duration_minutes = data.get('duration_minutes', 60)
        
        logger.info(f"[TEACHER_PREVIEW] Exam ID: {exam_id}, Duration: {duration_minutes} minutes")
        
        # Verify teacher has permission
        is_admin = request.user.is_superuser or request.user.is_staff
        teacher_profile = getattr(request.user, 'teacher_profile', None)
        
        if not is_admin and not teacher_profile:
            logger.error(f"[TEACHER_PREVIEW] No teacher profile for user {request.user.username}")
            return JsonResponse({'success': False, 'error': 'Teacher profile not found'}, status=403)
        
        # Verify access to this class (if not admin)
        if not is_admin:
            assignment = TeacherClassAssignment.objects.filter(
                teacher=teacher_profile,
                class_code=class_code,
                is_active=True
            ).first()
            
            if not assignment:
                logger.error(f"[TEACHER_PREVIEW] Teacher {teacher_profile.name} has no access to class {class_code}")
                return JsonResponse({'success': False, 'error': 'No access to this class'}, status=403)
        
        # Get the exam (try both RoutineExam and Exam models)
        exam = None
        exam_model_type = None
        
        # First try RoutineExam (what the schedule uses)
        try:
            exam = RoutineExam.objects.get(id=exam_id)
            exam_model_type = 'RoutineExam'
            logger.info(f"[TEACHER_PREVIEW] Found RoutineExam: {exam.name}")
        except RoutineExam.DoesNotExist:
            # Try regular Exam model
            try:
                exam = Exam.objects.get(id=exam_id)
                exam_model_type = 'Exam'
                logger.info(f"[TEACHER_PREVIEW] Found Exam: {exam.name}")
            except Exam.DoesNotExist:
                logger.error(f"[TEACHER_PREVIEW] Exam {exam_id} not found in either model")
                return JsonResponse({'success': False, 'error': 'Exam not found'}, status=404)
        
        # For RoutineExam, we need to use the related Exam model for StudentSession
        if exam_model_type == 'RoutineExam':
            # RoutineExam might not have all fields needed for StudentSession
            # Create or find corresponding Exam object
            try:
                # Try to find existing Exam with same ID
                actual_exam = Exam.objects.get(id=exam.id)
            except Exam.DoesNotExist:
                # Create a minimal Exam object for the preview
                actual_exam = Exam.objects.create(
                    id=exam.id,
                    name=exam.name,
                    curriculum_level=exam.curriculum_level,
                    timer_minutes=duration_minutes,
                    total_questions=getattr(exam, 'total_questions', 20),
                    default_options_count=getattr(exam, 'default_options_count', 4),
                    is_active=True,
                    created_by=teacher_profile if teacher_profile else None
                )
                logger.info(f"[TEACHER_PREVIEW] Created Exam object for preview: {actual_exam.id}")
        else:
            actual_exam = exam
        
        # Create a teacher preview session
        preview_session = StudentSession.objects.create(
            # Basic info (use teacher's name)
            student_name=f"TEACHER PREVIEW: {request.user.get_full_name() or request.user.username}",
            parent_phone="N/A",
            grade=1,  # Default grade for preview
            academic_rank='TOP_10',  # Default rank for preview
            
            # Exam reference
            exam=actual_exam,
            
            # Curriculum tracking (use exam's curriculum if available)
            original_curriculum_level=actual_exam.curriculum_level if hasattr(actual_exam, 'curriculum_level') else None,
            
            # Mark as teacher preview
            is_teacher_preview=True,
            preview_teacher=teacher_profile,
            
            # Session metadata
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        logger.info(f"[TEACHER_PREVIEW] Created preview session: {preview_session.id}")
        print(f"[TEACHER_PREVIEW] ✅ Preview session created:")
        print(f"  Session ID: {preview_session.id}")
        print(f"  Exam: {actual_exam.name}")
        print(f"  Duration: {duration_minutes} minutes")
        print(f"  Teacher: {request.user.username}")
        
        # Return the session URL for redirect
        test_url = f'/RoutineTest/session/{preview_session.id}/'
        
        logger.info(f"[TEACHER_PREVIEW] Redirecting teacher to: {test_url}")
        print(f"[TEACHER_PREVIEW] 🚀 Redirecting to exam interface: {test_url}")
        print(f"{'='*80}\n")
        
        return JsonResponse({
            'success': True,
            'message': 'Teacher preview session created',
            'session_id': str(preview_session.id),
            'redirect_url': test_url,
            'exam_name': actual_exam.name,
            'duration_minutes': duration_minutes,
            'is_preview': True,
            'debug_info': {
                'exam_model_type': exam_model_type,
                'exam_id': str(exam.id),
                'actual_exam_id': str(actual_exam.id),
                'teacher': request.user.username,
                'timestamp': timezone.now().isoformat()
            }
        })
        
    except json.JSONDecodeError as e:
        logger.error(f"[TEACHER_PREVIEW] Invalid JSON: {e}")
        return JsonResponse({'success': False, 'error': 'Invalid request data'}, status=400)
    except Exception as e:
        logger.error(f"[TEACHER_PREVIEW] Unexpected error: {e}", exc_info=True)
        print(f"[TEACHER_PREVIEW] ❌ Error: {str(e)}")
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
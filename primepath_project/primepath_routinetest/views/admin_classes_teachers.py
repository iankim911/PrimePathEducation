"""
Admin Classes & Teachers Management View
Comprehensive admin interface for managing classes, teachers, and access requests
Located below Class Management in Classes & Exams tab
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.db.models import Q, Count, Prefetch
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import json
import logging
import uuid
from datetime import datetime

from core.models import Teacher, CurriculumLevel, Program, SubProgram
from primepath_routinetest.models import (
    Class, TeacherClassAssignment, ClassAccessRequest,
    AccessAuditLog, StudentEnrollment
)
from primepath_routinetest.services import ExamService

logger = logging.getLogger(__name__)


def is_admin(user):
    """Check if user is admin"""
    return user.is_superuser or user.is_staff


@login_required
@user_passes_test(is_admin)
def admin_classes_teachers(request):
    """
    Main admin view for Classes & Teachers management
    Includes class CRUD, teacher allocation, and access requests
    """
    console_log = {
        "view": "admin_classes_teachers",
        "user": request.user.username,
        "timestamp": timezone.now().isoformat()
    }
    logger.info(f"[ADMIN_CLASSES_TEACHERS] {json.dumps(console_log)}")
    print(f"[ADMIN_CLASSES_TEACHERS] Admin accessing Classes & Teachers management")
    
    # Get all class codes from ExamService
    all_class_codes = []
    for program, classes in ExamService.PROGRAM_CLASS_MAPPING.items():
        all_class_codes.extend(classes)
    
    # Get or create Class objects for all class codes
    existing_classes = {}
    for class_code in all_class_codes:
        class_obj, created = Class.objects.get_or_create(
            name=class_code,
            defaults={
                'grade_level': ExamService.get_class_display_name(class_code),
                'academic_year': str(datetime.now().year),
                'created_by': request.user
            }
        )
        existing_classes[class_code] = class_obj
        if created:
            print(f"[ADMIN_CLASSES_TEACHERS] Created Class object for {class_code}")
    
    # Get all teachers
    teachers = Teacher.objects.all().select_related('user').order_by('name')
    
    # Get teacher assignments
    assignments = TeacherClassAssignment.objects.filter(
        is_active=True
    ).select_related('teacher').order_by('class_code', 'teacher__name')
    
    # Organize assignments by class
    class_assignments = {}
    for assignment in assignments:
        if assignment.class_code not in class_assignments:
            class_assignments[assignment.class_code] = []
        class_assignments[assignment.class_code].append({
            'teacher': assignment.teacher,
            'access_level': assignment.access_level,
            'assignment_id': str(assignment.id)
        })
    
    # Get pending access requests
    pending_requests = ClassAccessRequest.objects.filter(
        status='PENDING'
    ).select_related('teacher').order_by('-created_at')
    
    # Count statistics
    request_stats = {
        'pending': pending_requests.count(),
        'approved_today': ClassAccessRequest.objects.filter(
            status='APPROVED',
            reviewed_at__date=timezone.now().date()
        ).count(),
        'denied_today': ClassAccessRequest.objects.filter(
            status='DENIED',
            reviewed_at__date=timezone.now().date()
        ).count()
    }
    
    # Get curriculum levels for recommendation
    curriculum_levels = CurriculumLevel.objects.select_related(
        'subprogram__program'
    ).order_by('subprogram__program__name', 'subprogram__name', 'level_number')
    
    # Organize curriculum by program
    curriculum_by_program = {}
    for level in curriculum_levels:
        program_name = level.subprogram.program.name if level.subprogram and level.subprogram.program else 'Unknown'
        if program_name not in curriculum_by_program:
            curriculum_by_program[program_name] = []
        curriculum_by_program[program_name].append({
            'id': str(level.id),
            'full_name': level.full_name,
            'program': program_name,
            'subprogram': level.subprogram.name if level.subprogram else '',
            'level': level.level_number
        })
    
    # Build class data with all information
    classes_data = []
    for program, class_codes in ExamService.PROGRAM_CLASS_MAPPING.items():
        for class_code in class_codes:
            class_obj = existing_classes.get(class_code)
            
            # Get student count
            student_count = StudentEnrollment.objects.filter(
                class_assigned=class_obj,
                status='active'
            ).count() if class_obj else 0
            
            # Get assigned teachers
            assigned_teachers = class_assignments.get(class_code, [])
            
            # Get recommended curriculum
            recommended_curriculum = None
            if class_obj and hasattr(class_obj, 'recommended_curriculum'):
                recommended_curriculum = class_obj.recommended_curriculum
            
            classes_data.append({
                'program': program,
                'class_code': class_code,
                'class_display': ExamService.get_class_display_name(class_code),
                'class_obj': class_obj,
                'student_count': student_count,
                'assigned_teachers': assigned_teachers,
                'teacher_count': len(assigned_teachers),
                'recommended_curriculum': recommended_curriculum,
                'has_full_teacher': any(t['access_level'] == 'FULL' for t in assigned_teachers)
            })
    
    # Organize classes by program for display
    classes_by_program = {}
    for class_data in classes_data:
        program = class_data['program']
        if program not in classes_by_program:
            classes_by_program[program] = []
        classes_by_program[program].append(class_data)
    
    # Context for template
    context = {
        'classes_by_program': classes_by_program,
        'all_teachers': teachers,
        'pending_requests': pending_requests,
        'request_stats': request_stats,
        'curriculum_by_program': curriculum_by_program,
        'curriculum_levels': curriculum_levels,
        'total_classes': len(classes_data),
        'total_teachers': teachers.count(),
        'access_levels': TeacherClassAssignment.ACCESS_LEVELS,
        'debug_info': {
            'user': request.user.username,
            'timestamp': timezone.now().isoformat(),
            'class_count': len(classes_data),
            'teacher_count': teachers.count(),
            'pending_requests': pending_requests.count()
        }
    }
    
    return render(request, 'primepath_routinetest/admin_classes_teachers.html', context)


@login_required
@user_passes_test(is_admin)
@require_http_methods(['POST'])
def create_class(request):
    """Create a new class with curriculum recommendation"""
    console_log = {
        "view": "create_class",
        "user": request.user.username,
        "timestamp": timezone.now().isoformat()
    }
    logger.info(f"[CREATE_CLASS] {json.dumps(console_log)}")
    
    try:
        data = json.loads(request.body)
        class_code = data.get('class_code')
        curriculum_id = data.get('curriculum_id')
        
        if not class_code:
            return JsonResponse({
                'success': False,
                'error': 'Class code is required'
            }, status=400)
        
        # Check if class already exists
        if Class.objects.filter(name=class_code).exists():
            return JsonResponse({
                'success': False,
                'error': f'Class {class_code} already exists'
            }, status=400)
        
        # Create the class
        class_obj = Class.objects.create(
            name=class_code,
            grade_level=ExamService.get_class_display_name(class_code),
            academic_year=str(datetime.now().year),
            created_by=request.user
        )
        
        # Set recommended curriculum if provided
        if curriculum_id:
            try:
                curriculum = CurriculumLevel.objects.get(id=curriculum_id)
                class_obj.recommended_curriculum = curriculum
                class_obj.save()
                print(f"[CREATE_CLASS] Set recommended curriculum: {curriculum.full_name}")
            except CurriculumLevel.DoesNotExist:
                print(f"[CREATE_CLASS] Warning: Curriculum {curriculum_id} not found")
        
        # Log the action
        AccessAuditLog.objects.create(
            action='CREATE_CLASS',
            user=request.user,
            details={
                'class_code': class_code,
                'curriculum_id': curriculum_id
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Class {class_code} created successfully',
            'class_id': str(class_obj.id)
        })
        
    except Exception as e:
        logger.error(f"[CREATE_CLASS] Error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@user_passes_test(is_admin)
@require_http_methods(['POST'])
def delete_class(request):
    """Delete a class (soft delete)"""
    console_log = {
        "view": "delete_class",
        "user": request.user.username,
        "timestamp": timezone.now().isoformat()
    }
    logger.info(f"[DELETE_CLASS] {json.dumps(console_log)}")
    
    try:
        data = json.loads(request.body)
        class_code = data.get('class_code')
        
        if not class_code:
            return JsonResponse({
                'success': False,
                'error': 'Class code is required'
            }, status=400)
        
        # Get the class
        class_obj = Class.objects.get(name=class_code)
        
        # Check for active enrollments
        active_students = StudentEnrollment.objects.filter(
            class_assigned=class_obj,
            status='active'
        ).count()
        
        if active_students > 0 and not data.get('force', False):
            return JsonResponse({
                'success': False,
                'error': f'Class has {active_students} active students. Use force=true to delete anyway.',
                'active_students': active_students
            }, status=400)
        
        # Soft delete
        class_obj.is_active = False
        class_obj.save()
        
        # Deactivate all teacher assignments
        TeacherClassAssignment.objects.filter(
            class_code=class_code,
            is_active=True
        ).update(is_active=False, end_date=timezone.now())
        
        # Log the action
        AccessAuditLog.objects.create(
            action='DELETE_CLASS',
            user=request.user,
            details={
                'class_code': class_code,
                'had_active_students': active_students
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Class {class_code} deleted successfully'
        })
        
    except Class.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'Class {class_code} not found'
        }, status=404)
    except Exception as e:
        logger.error(f"[DELETE_CLASS] Error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@user_passes_test(is_admin)
@require_http_methods(['POST'])
def set_curriculum_recommendation(request):
    """Set recommended curriculum level for a class"""
    console_log = {
        "view": "set_curriculum_recommendation",
        "user": request.user.username,
        "timestamp": timezone.now().isoformat()
    }
    logger.info(f"[SET_CURRICULUM] {json.dumps(console_log)}")
    
    try:
        data = json.loads(request.body)
        class_code = data.get('class_code')
        curriculum_id = data.get('curriculum_id')
        
        if not class_code:
            return JsonResponse({
                'success': False,
                'error': 'Class code is required'
            }, status=400)
        
        # Get or create the class
        class_obj, created = Class.objects.get_or_create(
            name=class_code,
            defaults={
                'grade_level': ExamService.get_class_display_name(class_code),
                'academic_year': str(datetime.now().year),
                'created_by': request.user
            }
        )
        
        # Set the curriculum
        if curriculum_id:
            try:
                curriculum = CurriculumLevel.objects.get(id=curriculum_id)
                # Add recommended_curriculum field if it doesn't exist
                if not hasattr(class_obj, 'recommended_curriculum'):
                    # This would need a migration, for now store in a JSON field
                    pass
                class_obj.recommended_curriculum = curriculum
                class_obj.save()
                
                message = f'Recommended curriculum set to {curriculum.full_name}'
            except CurriculumLevel.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Curriculum level not found'
                }, status=404)
        else:
            # Clear recommendation
            class_obj.recommended_curriculum = None
            class_obj.save()
            message = 'Curriculum recommendation cleared'
        
        # Log the action
        AccessAuditLog.objects.create(
            action='SET_CURRICULUM',
            user=request.user,
            details={
                'class_code': class_code,
                'curriculum_id': curriculum_id
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        logger.error(f"[SET_CURRICULUM] Error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@user_passes_test(is_admin)
@require_http_methods(['POST'])
def assign_teacher_to_class(request):
    """Assign a teacher to a class with access level"""
    console_log = {
        "view": "assign_teacher_to_class",
        "user": request.user.username,
        "timestamp": timezone.now().isoformat()
    }
    logger.info(f"[ASSIGN_TEACHER] {json.dumps(console_log)}")
    
    try:
        data = json.loads(request.body)
        class_code = data.get('class_code')
        teacher_id = data.get('teacher_id')
        access_level = data.get('access_level', 'VIEW')
        
        if not class_code or not teacher_id:
            return JsonResponse({
                'success': False,
                'error': 'Class code and teacher ID are required'
            }, status=400)
        
        # Get teacher
        teacher = Teacher.objects.get(id=teacher_id)
        
        # Check if assignment already exists
        existing = TeacherClassAssignment.objects.filter(
            teacher=teacher,
            class_code=class_code,
            is_active=True
        ).first()
        
        if existing:
            # Update access level
            existing.access_level = access_level
            existing.save()
            message = f'Updated {teacher.name} access to {access_level}'
        else:
            # Create new assignment
            TeacherClassAssignment.objects.create(
                teacher=teacher,
                class_code=class_code,
                access_level=access_level,
                assigned_by=request.user,
                assignment_type='PERMANENT',
                is_active=True
            )
            message = f'Assigned {teacher.name} to {class_code} with {access_level} access'
        
        # Log the action
        AccessAuditLog.objects.create(
            action='ASSIGN_TEACHER',
            user=request.user,
            teacher=teacher,
            class_code=class_code,
            details={
                'access_level': access_level
            }
        )
        
        print(f"[ASSIGN_TEACHER] {message}")
        
        return JsonResponse({
            'success': True,
            'message': message
        })
        
    except Teacher.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Teacher not found'
        }, status=404)
    except Exception as e:
        logger.error(f"[ASSIGN_TEACHER] Error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@user_passes_test(is_admin)
@require_http_methods(['POST'])
def remove_teacher_from_class(request):
    """Remove a teacher from a class"""
    console_log = {
        "view": "remove_teacher_from_class",
        "user": request.user.username,
        "timestamp": timezone.now().isoformat()
    }
    logger.info(f"[REMOVE_TEACHER] {json.dumps(console_log)}")
    
    try:
        data = json.loads(request.body)
        assignment_id = data.get('assignment_id')
        
        if not assignment_id:
            return JsonResponse({
                'success': False,
                'error': 'Assignment ID is required'
            }, status=400)
        
        # Get and deactivate assignment
        assignment = TeacherClassAssignment.objects.get(id=assignment_id)
        teacher_name = assignment.teacher.name
        class_code = assignment.class_code
        
        assignment.is_active = False
        assignment.end_date = timezone.now()
        assignment.save()
        
        # Log the action
        AccessAuditLog.objects.create(
            action='REMOVE_TEACHER',
            user=request.user,
            teacher=assignment.teacher,
            class_code=class_code,
            details={
                'previous_access_level': assignment.access_level
            }
        )
        
        message = f'Removed {teacher_name} from {class_code}'
        print(f"[REMOVE_TEACHER] {message}")
        
        return JsonResponse({
            'success': True,
            'message': message
        })
        
    except TeacherClassAssignment.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Assignment not found'
        }, status=404)
    except Exception as e:
        logger.error(f"[REMOVE_TEACHER] Error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@user_passes_test(is_admin)
@require_http_methods(['POST'])
def handle_access_request(request):
    """Approve or deny an access request"""
    console_log = {
        "view": "handle_access_request",
        "user": request.user.username,
        "timestamp": timezone.now().isoformat()
    }
    logger.info(f"[HANDLE_REQUEST] {json.dumps(console_log)}")
    
    try:
        data = json.loads(request.body)
        request_id = data.get('request_id')
        action = data.get('action')  # 'approve' or 'deny'
        access_level = data.get('access_level', 'VIEW')
        notes = data.get('notes', '')
        
        if not request_id or not action:
            return JsonResponse({
                'success': False,
                'error': 'Request ID and action are required'
            }, status=400)
        
        # Get the request
        access_request = ClassAccessRequest.objects.get(id=request_id)
        
        if action == 'approve':
            # Create teacher assignment
            assignment = TeacherClassAssignment.objects.create(
                teacher=access_request.teacher,
                class_code=access_request.class_code,
                access_level=access_level,
                assigned_by=request.user,
                assignment_type=access_request.request_type,
                is_active=True
            )
            
            # Update request status
            access_request.status = 'APPROVED'
            access_request.reviewed_by = request.user
            access_request.reviewed_at = timezone.now()
            access_request.admin_notes = notes
            access_request.save()
            
            message = f'Approved access for {access_request.teacher.name} to {access_request.class_code}'
            
        elif action == 'deny':
            # Update request status
            access_request.status = 'DENIED'
            access_request.reviewed_by = request.user
            access_request.reviewed_at = timezone.now()
            access_request.admin_notes = notes
            access_request.save()
            
            message = f'Denied access for {access_request.teacher.name} to {access_request.class_code}'
        
        else:
            return JsonResponse({
                'success': False,
                'error': 'Invalid action. Use "approve" or "deny"'
            }, status=400)
        
        # Log the action
        AccessAuditLog.objects.create(
            action=f'REQUEST_{action.upper()}',
            user=request.user,
            teacher=access_request.teacher,
            class_code=access_request.class_code,
            details={
                'request_id': str(request_id),
                'access_level': access_level if action == 'approve' else None,
                'notes': notes
            }
        )
        
        print(f"[HANDLE_REQUEST] {message}")
        
        return JsonResponse({
            'success': True,
            'message': message
        })
        
    except ClassAccessRequest.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Request not found'
        }, status=404)
    except Exception as e:
        logger.error(f"[HANDLE_REQUEST] Error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@user_passes_test(is_admin)
def get_pending_requests_count(request):
    """Get count of pending access requests for notification badge"""
    try:
        count = ClassAccessRequest.objects.filter(status='PENDING').count()
        return JsonResponse({
            'success': True,
            'count': count
        })
    except Exception as e:
        logger.error(f"[PENDING_COUNT] Error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
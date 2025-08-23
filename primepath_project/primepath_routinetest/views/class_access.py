"""
Teacher Class Access Management Views - ADMIN FIX VERSION
Ensures admins/head teachers have automatic access to ALL classes

CRITICAL FIX:
- Admins no longer need to request access
- They automatically have FULL ACCESS to ALL classes
- Proper UI for unlimited admin access
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Count
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
import json
import logging
from datetime import datetime

from primepath_routinetest.models import (
    TeacherClassAssignment,
    ClassAccessRequest,
    AccessAuditLog,
    Exam
    # StudentRoster removed - not needed for Answer Keys functionality
)
from core.models import Teacher
from ..class_code_mapping import CLASS_CODE_CURRICULUM_MAPPING

logger = logging.getLogger(__name__)


def is_admin_or_head_teacher(user):
    """
    Comprehensive check if user is admin/head teacher
    Returns tuple: (is_admin, teacher_obj)
    """
    console_log = {
        "function": "is_admin_or_head_teacher",
        "user": user.username,
        "timestamp": datetime.now().isoformat()
    }
    
    # Check 1: Is superuser?
    if user.is_superuser:
        console_log["is_superuser"] = True
        print(f"[ADMIN_CHECK] ✅ User {user.username} is SUPERUSER")
        
        # Get or create teacher profile for superuser
        try:
            teacher = Teacher.objects.get(user=user)
        except Teacher.DoesNotExist:
            # Create teacher profile for superuser
            teacher = Teacher.objects.create(
                user=user,
                email=user.email or f"{user.username}_{user.id}@primepath.com",
                name=user.get_full_name() or user.username,
                is_head_teacher=True
            )
            print(f"[ADMIN_CHECK] Created head teacher profile for superuser {user.username}")
        
        console_log["result"] = "ADMIN_SUPERUSER"
        logger.info(json.dumps(console_log))
        return True, teacher
    
    # Check 2: Is staff?
    if user.is_staff:
        console_log["is_staff"] = True
        print(f"[ADMIN_CHECK] User {user.username} is STAFF")
    
    # Check 3: Has teacher profile with head teacher status?
    try:
        teacher = Teacher.objects.get(user=user)
        if teacher.is_head_teacher:
            console_log["is_head_teacher"] = True
            console_log["result"] = "ADMIN_HEAD_TEACHER"
            print(f"[ADMIN_CHECK] ✅ User {user.username} is HEAD TEACHER")
            logger.info(json.dumps(console_log))
            return True, teacher
        else:
            console_log["is_head_teacher"] = False
            console_log["result"] = "REGULAR_TEACHER"
            print(f"[ADMIN_CHECK] User {user.username} is regular teacher")
            logger.info(json.dumps(console_log))
            return False, teacher
    except Teacher.DoesNotExist:
        console_log["has_teacher_profile"] = False
        console_log["result"] = "NO_TEACHER_PROFILE"
        print(f"[ADMIN_CHECK] ❌ User {user.username} has no teacher profile")
        logger.info(json.dumps(console_log))
        return False, None


@login_required
def my_classes_view(request):
    """
    Enhanced view with PROPER ADMIN ACCESS
    Admins get AUTOMATIC access to ALL classes
    """
    # Comprehensive debugging
    debug_log = {
        "view": "my_classes_view_admin_fix",
        "timestamp": datetime.now().isoformat(),
        "user": request.user.username,
        "user_id": request.user.id,
        "is_authenticated": request.user.is_authenticated,
        "is_staff": request.user.is_staff,
        "is_superuser": request.user.is_superuser,
        "request_path": request.path,
        "get_params": dict(request.GET),
        "session_id": request.session.session_key
    }
    
    print("\n" + "="*80)
    print(f"[MY_CLASSES_VIEW] STARTING - User: {request.user.username}")
    print("="*80)
    print(json.dumps(debug_log, indent=2))
    
    try:
        # Check if user is admin/head teacher
        is_admin, teacher = is_admin_or_head_teacher(request.user)
        
        if not teacher:
            # Try to get or create teacher profile
            try:
                teacher = Teacher.objects.get(user=request.user)
            except Teacher.DoesNotExist:
                # Create teacher profile
                teacher = Teacher.objects.create(
                    user=request.user,
                    email=request.user.email or f"{request.user.username}@primepath.com",
                    name=request.user.get_full_name() or request.user.username,
                    is_head_teacher=request.user.is_superuser
                )
                print(f"[MY_CLASSES_VIEW] Created teacher profile for {request.user.username}")
                is_admin = teacher.is_head_teacher
        
        # Determine view mode
        admin_view_param = request.GET.get('admin_view', '').lower()
        switch_to_admin = admin_view_param == 'true'
        switch_to_teacher = admin_view_param == 'false'
        
        # For admins, default to showing ALL CLASSES unless explicitly switched
        if is_admin:
            if switch_to_teacher:
                show_admin_view = False
                print(f"[MY_CLASSES_VIEW] Admin {request.user.username} switched to TEACHER VIEW")
            else:
                show_admin_view = True
                print(f"[MY_CLASSES_VIEW] Admin {request.user.username} using ADMIN VIEW (full access)")
        else:
            show_admin_view = False
            print(f"[MY_CLASSES_VIEW] Regular teacher {request.user.username} using TEACHER VIEW")
        
        context = {
            'is_admin': is_admin,
            'is_head_teacher': is_admin,
            'show_admin_view': show_admin_view,
            'can_switch_view': is_admin,  # Only admins can switch views
            'teacher': teacher,
            'current_user': request.user,
            'debug_mode': request.GET.get('debug', 'false') == 'true'
        }
        
        if is_admin and show_admin_view:
            # ADMIN VIEW: FULL ACCESS TO EVERYTHING
            print(f"[ADMIN_VIEW] 🔓 GRANTING FULL ACCESS TO {request.user.username}")
            
            # Get ALL class codes from PrimePath curriculum mapping
            all_class_codes = list(CLASS_CODE_CURRICULUM_MAPPING.keys())
            
            # Create virtual assignments for ALL classes (admin has implicit access)
            admin_classes = []
            for class_code in all_class_codes:
                # Get actual teachers assigned (excluding admin's virtual access)
                actual_assignments = TeacherClassAssignment.objects.filter(
                    class_code=class_code,
                    is_active=True
                ).exclude(teacher=teacher).select_related('teacher')
                
                # StudentRoster removed - returning 0 for student count
                student_count = 0  # Roster functionality removed
                
                # Get active exams
                try:
                    active_exams = Exam.objects.filter(
                        class_codes__contains=class_code,
                        is_active=True
                    ).count()
                except:
                    # SQLite fallback
                    all_exams = Exam.objects.filter(is_active=True)
                    active_exams = sum(1 for exam in all_exams if class_code in (exam.class_codes or []))
                
                # Get class display name from curriculum mapping
                class_name = f"{class_code} - {CLASS_CODE_CURRICULUM_MAPPING.get(class_code, class_code)}"
                
                admin_classes.append({
                    'class_code': class_code,
                    'class_name': class_name,
                    'student_count': student_count,
                    'active_exams': active_exams,
                    'access_level': 'ADMIN FULL ACCESS',
                    'is_full_access': True,
                    'is_admin_access': True,
                    'assigned_teachers': [
                        {
                            'name': t.teacher.name,
                            'email': t.teacher.email,
                            'access_level': t.get_access_level_display()
                        } for t in actual_assignments
                    ],
                    'teacher_count': actual_assignments.count(),
                    'assigned_date': None  # Admin always had access
                })
            
            # Get all pending access requests (for admin to approve)
            all_pending_requests = ClassAccessRequest.objects.filter(
                status='PENDING'
            ).select_related('teacher').order_by('-requested_at')
            
            # Get all teacher assignments for management
            all_assignments = TeacherClassAssignment.objects.filter(
                is_active=True
            ).select_related('teacher').order_by('class_code', 'teacher__name')
            
            # Group assignments by class for admin overview
            assignments_by_class = {}
            for assignment in all_assignments:
                if assignment.class_code not in assignments_by_class:
                    assignments_by_class[assignment.class_code] = []
                assignments_by_class[assignment.class_code].append(assignment)
            
            context.update({
                'my_classes': admin_classes,  # Admin has ALL classes
                'all_classes': admin_classes,  # Duplicate for compatibility
                'my_class_count': len(admin_classes),
                'total_classes': len(all_class_codes),
                'is_admin_full_access': True,
                'pending_requests': all_pending_requests,
                'pending_count': all_pending_requests.count(),
                'assignments_by_class': assignments_by_class,
                'available_classes': [],  # Admin doesn't need to request
                'my_requests': [],  # Admin doesn't make requests
            })
            
            admin_log = {
                "view": "ADMIN_FULL_ACCESS",
                "user": request.user.username,
                "total_classes_accessible": len(admin_classes),
                "pending_requests_to_review": all_pending_requests.count(),
                "message": "ADMIN HAS UNLIMITED ACCESS TO ALL CLASSES"
            }
            print(f"[ADMIN_ACCESS] {json.dumps(admin_log, indent=2)}")
            logger.info(f"[ADMIN_ACCESS] {json.dumps(admin_log)}")
            
        else:
            # TEACHER VIEW (regular or admin in teacher mode)
            print(f"[TEACHER_VIEW] Showing teacher view for {request.user.username}")
            
            # Get teacher's actual assignments
            my_assignments = TeacherClassAssignment.objects.filter(
                teacher=teacher,
                is_active=True
            ).order_by('class_code')
            
            my_classes = []
            my_class_codes = []
            
            for assignment in my_assignments:
                # StudentRoster removed - returning 0 for student count
                student_count = 0  # Roster functionality removed
                
                # Get active exams
                try:
                    active_exams = Exam.objects.filter(
                        class_codes__contains=assignment.class_code,
                        is_active=True
                    ).count()
                except:
                    all_exams = Exam.objects.filter(is_active=True)
                    active_exams = sum(1 for exam in all_exams if assignment.class_code in (exam.class_codes or []))
                
                my_classes.append({
                    'class_code': assignment.class_code,
                    'class_name': assignment.get_class_code_display(),
                    'student_count': student_count,
                    'active_exams': active_exams,
                    'access_level': assignment.get_access_level_display(),
                    'is_full_access': assignment.access_level == 'FULL',
                    'assigned_date': assignment.assigned_date,
                })
                my_class_codes.append(assignment.class_code)
            
            # Get available classes from PrimePath curriculum mapping
            all_class_codes = list(CLASS_CODE_CURRICULUM_MAPPING.keys())
            available_class_codes = [code for code in all_class_codes if code not in my_class_codes]
            
            # Check pending requests
            pending_requests = ClassAccessRequest.objects.filter(
                teacher=teacher,
                status='PENDING'
            )
            pending_class_codes = [req.class_code for req in pending_requests]
            
            available_classes = []
            for class_code in available_class_codes:
                current_assignments = TeacherClassAssignment.objects.filter(
                    class_code=class_code,
                    is_active=True
                ).select_related('teacher')
                
                class_name = f"{class_code} - {CLASS_CODE_CURRICULUM_MAPPING.get(class_code, class_code)}"
                is_pending = class_code in pending_class_codes
                
                available_classes.append({
                    'class_code': class_code,
                    'class_name': class_name,
                    'current_teachers': current_assignments,
                    'teacher_count': current_assignments.count(),
                    'is_pending': is_pending,
                })
            
            # Get recent requests
            my_requests = ClassAccessRequest.objects.filter(
                teacher=teacher
            ).order_by('-requested_at')[:10]
            
            context.update({
                'my_classes': my_classes,
                'available_classes': available_classes,
                'my_requests': my_requests,
                'pending_requests': pending_requests,
                'my_class_count': len(my_classes),
                'available_count': len(available_classes),
                'is_admin_full_access': False,
            })
            
            teacher_log = {
                "view": "TEACHER_LIMITED_ACCESS",
                "user": request.user.username,
                "assigned_classes": len(my_classes),
                "available_to_request": len(available_classes),
                "pending_requests": pending_requests.count()
            }
            print(f"[TEACHER_ACCESS] {json.dumps(teacher_log, indent=2)}")
            logger.info(f"[TEACHER_ACCESS] {json.dumps(teacher_log)}")
        
        # Final logging
        final_log = {
            "view_completed": "my_classes_view",
            "user": request.user.username,
            "is_admin": is_admin,
            "show_admin_view": show_admin_view,
            "classes_shown": context.get('my_class_count', 0),
            "timestamp": datetime.now().isoformat()
        }
        print(f"\n[VIEW_COMPLETE] {json.dumps(final_log, indent=2)}")
        print("="*80 + "\n")
        
        return render(request, 'primepath_routinetest/class_access_admin.html', context)
        
    except Exception as e:
        error_log = {
            "error": "my_classes_view_exception",
            "user": request.user.username,
            "exception": str(e),
            "type": type(e).__name__,
            "timestamp": datetime.now().isoformat()
        }
        print(f"[ERROR] {json.dumps(error_log, indent=2)}")
        logger.error(f"[CLASS_ACCESS_ERROR] {json.dumps(error_log)}")
        
        messages.error(request, "An error occurred. Admin support has been notified.")
        return redirect('RoutineTest:index')


# Additional helper functions for admin operations

def grant_admin_full_access(user):
    """
    Explicitly grant admin full access to all classes
    Creates virtual assignments if needed
    """
    print(f"[GRANT_ADMIN_ACCESS] Granting full access to {user.username}")
    
    is_admin, teacher = is_admin_or_head_teacher(user)
    if not is_admin:
        print(f"[GRANT_ADMIN_ACCESS] User {user.username} is not admin, skipping")
        return False
    
    # Log the grant
    log_entry = {
        "action": "GRANT_ADMIN_FULL_ACCESS",
        "admin": user.username,
        "timestamp": datetime.now().isoformat(),
        "message": "Admin granted automatic full access to all classes"
    }
    logger.info(json.dumps(log_entry))
    
    return True


def check_admin_access(user, class_code):
    """
    Check if user has admin access to a specific class
    Admins ALWAYS have access
    """
    is_admin, teacher = is_admin_or_head_teacher(user)
    
    if is_admin:
        print(f"[ACCESS_CHECK] ✅ Admin {user.username} has AUTOMATIC access to {class_code}")
        return True
    
    # Check regular teacher assignment
    if teacher:
        has_access = TeacherClassAssignment.objects.filter(
            teacher=teacher,
            class_code=class_code,
            is_active=True
        ).exists()
        
        if has_access:
            print(f"[ACCESS_CHECK] ✅ Teacher {user.username} has assigned access to {class_code}")
        else:
            print(f"[ACCESS_CHECK] ❌ Teacher {user.username} has NO access to {class_code}")
        
        return has_access
    
    print(f"[ACCESS_CHECK] ❌ User {user.username} has no teacher profile")
    return False


# API Functions for Class Access Management

@login_required
@require_POST
def request_access(request):
    """Request access to a class - handles both JSON and form data"""
    try:
        # Handle both JSON and form data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            # Form data from frontend
            data = {
                'class_code': request.POST.get('class_code'),
                'requested_access_level': request.POST.get('requested_access_level'),
                'reason': request.POST.get('reason'),
                'notes': request.POST.get('notes', '')
            }
        
        class_code = data.get('class_code')
        access_level = data.get('requested_access_level', 'FULL')
        reason = data.get('reason')
        notes = data.get('notes', '')
        
        if not class_code:
            return JsonResponse({'success': False, 'error': 'Class code required'})
        
        if not access_level:
            return JsonResponse({'success': False, 'error': 'Access level required'})
            
        if not reason:
            return JsonResponse({'success': False, 'error': 'Reason required'})
        
        # Check if admin (admins don't need to request)
        is_admin, teacher = is_admin_or_head_teacher(request.user)
        if is_admin:
            return JsonResponse({
                'success': False, 
                'error': 'Admins have automatic access to all classes'
            })
        
        if not teacher:
            return JsonResponse({'success': False, 'error': 'Teacher profile not found'})
        
        # Check if already has access
        if TeacherClassAssignment.objects.filter(
            teacher=teacher,
            class_code=class_code,
            is_active=True
        ).exists():
            return JsonResponse({'success': False, 'error': 'Already have access'})
        
        # Check if request already pending
        if ClassAccessRequest.objects.filter(
            teacher=teacher,
            class_code=class_code,
            status='PENDING'
        ).exists():
            return JsonResponse({'success': False, 'error': 'Request already pending'})
        
        # Create request with full details
        access_request = ClassAccessRequest.objects.create(
            teacher=teacher,
            class_code=class_code,
            requested_access_level=access_level,
            reason=reason,
            notes=notes,
            status='PENDING'
        )
        
        # Log the request
        AccessAuditLog.objects.create(
            teacher=teacher,
            action='REQUEST_ACCESS',
            details=f'Requested access to {class_code}'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Access request submitted successfully',
            'request_id': str(access_request.id),
            'refresh_page': True  # Signal frontend to refresh to show pending count
        })
        
    except Exception as e:
        logger.error(f"Error in request_access: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
def withdraw_request(request, request_id):
    """Withdraw an access request"""
    try:
        teacher = Teacher.objects.get(user=request.user)
        access_request = get_object_or_404(
            ClassAccessRequest,
            id=request_id,
            teacher=teacher,
            status='PENDING'
        )
        
        access_request.status = 'WITHDRAWN'
        access_request.save()
        
        # Log the withdrawal
        AccessAuditLog.objects.create(
            teacher=teacher,
            action='WITHDRAW_REQUEST',
            details=f'Withdrew request for {access_request.class_code}'
        )
        
        return JsonResponse({'success': True, 'message': 'Request withdrawn'})
        
    except Teacher.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Teacher profile not found'})
    except Exception as e:
        logger.error(f"Error in withdraw_request: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def admin_pending_requests(request):
    """View pending access requests (admin only)"""
    # Check admin access
    is_admin, teacher = is_admin_or_head_teacher(request.user)
    if not is_admin:
        messages.error(request, 'Admin access required')
        return redirect('RoutineTest:my_classes')
    
    # Get all pending requests
    pending_requests = ClassAccessRequest.objects.filter(
        status='PENDING'
    ).select_related('teacher').order_by('-requested_at')
    
    context = {
        'pending_requests': pending_requests,
        'is_admin': True,
        'is_head_teacher': True
    }
    
    return render(request, 'primepath_routinetest/admin_pending_requests.html', context)


@login_required
@require_POST
def approve_request(request, request_id):
    """Approve an access request (admin only)"""
    # Check admin access
    is_admin, admin_teacher = is_admin_or_head_teacher(request.user)
    if not is_admin:
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        access_request = get_object_or_404(ClassAccessRequest, id=request_id)
        
        # Create assignment
        assignment, created = TeacherClassAssignment.objects.get_or_create(
            teacher=access_request.teacher,
            class_code=access_request.class_code,
            defaults={
                'access_level': 'VIEW',
                'is_active': True,
                'assigned_by': request.user
            }
        )
        
        if not created:
            assignment.is_active = True
            assignment.save()
        
        # Update request status
        access_request.status = 'APPROVED'
        access_request.reviewed_by = request.user
        access_request.reviewed_at = timezone.now()
        access_request.save()
        
        # Log the approval
        AccessAuditLog.objects.create(
            teacher=access_request.teacher,
            action='ACCESS_APPROVED',
            details=f'Access to {access_request.class_code} approved by {request.user.username}',
            performed_by=request.user
        )
        
        return JsonResponse({'success': True, 'message': 'Request approved'})
        
    except Exception as e:
        logger.error(f"Error in approve_request: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
def deny_request(request, request_id):
    """Deny an access request (admin only)"""
    # Check admin access
    is_admin, admin_teacher = is_admin_or_head_teacher(request.user)
    if not is_admin:
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        data = json.loads(request.body)
        access_request = get_object_or_404(ClassAccessRequest, id=request_id)
        
        # Update request status
        access_request.status = 'DENIED'
        access_request.reviewed_by = request.user
        access_request.reviewed_at = timezone.now()
        access_request.admin_notes = data.get('reason', 'No reason provided')
        access_request.save()
        
        # Log the denial
        AccessAuditLog.objects.create(
            teacher=access_request.teacher,
            action='ACCESS_DENIED',
            details=f'Access to {access_request.class_code} denied by {request.user.username}',
            performed_by=request.user
        )
        
        return JsonResponse({'success': True, 'message': 'Request denied'})
        
    except Exception as e:
        logger.error(f"Error in deny_request: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
def bulk_approve_requests(request):
    """Bulk approve multiple requests (admin only)"""
    # Check admin access
    is_admin, admin_teacher = is_admin_or_head_teacher(request.user)
    if not is_admin:
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        data = json.loads(request.body)
        request_ids = data.get('request_ids', [])
        
        approved_count = 0
        for request_id in request_ids:
            try:
                access_request = ClassAccessRequest.objects.get(id=request_id, status='PENDING')
                
                # Create assignment
                assignment, created = TeacherClassAssignment.objects.get_or_create(
                    teacher=access_request.teacher,
                    class_code=access_request.class_code,
                    defaults={
                        'access_level': 'VIEW',
                        'is_active': True,
                        'assigned_by': request.user
                    }
                )
                
                if not created:
                    assignment.is_active = True
                    assignment.save()
                
                # Update request
                access_request.status = 'APPROVED'
                access_request.reviewed_by = request.user
                access_request.reviewed_at = timezone.now()
                access_request.save()
                
                approved_count += 1
                
            except ClassAccessRequest.DoesNotExist:
                continue
        
        return JsonResponse({
            'success': True,
            'message': f'Approved {approved_count} requests'
        })
        
    except Exception as e:
        logger.error(f"Error in bulk_approve_requests: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


# API Endpoints for AJAX calls

@login_required
def api_my_classes(request):
    """API endpoint to get teacher's classes"""
    try:
        is_admin, teacher = is_admin_or_head_teacher(request.user)
        
        if is_admin:
            # Admin gets all classes from PrimePath curriculum mapping
            all_class_codes = list(CLASS_CODE_CURRICULUM_MAPPING.keys())
            classes = []
            for class_code in all_class_codes:
                class_name = f"{class_code} - {CLASS_CODE_CURRICULUM_MAPPING.get(class_code, class_code)}"
                classes.append({
                    'class_code': class_code,
                    'class_name': class_name,
                    'access_level': 'ADMIN FULL ACCESS',
                    'is_admin': True
                })
        else:
            # Regular teacher gets assigned classes
            if not teacher:
                return JsonResponse({'success': False, 'error': 'Teacher profile not found'})
            
            assignments = TeacherClassAssignment.objects.filter(
                teacher=teacher,
                is_active=True
            )
            
            classes = [{
                'class_code': a.class_code,
                'class_name': a.get_class_code_display(),
                'access_level': a.get_access_level_display(),
                'assigned_date': a.assigned_date.isoformat() if a.assigned_date else None
            } for a in assignments]
        
        return JsonResponse({
            'success': True,
            'classes': classes,
            'is_admin': is_admin
        })
        
    except Exception as e:
        logger.error(f"Error in api_my_classes: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def api_available_classes(request):
    """API endpoint to get available classes for request"""
    try:
        is_admin, teacher = is_admin_or_head_teacher(request.user)
        
        if is_admin:
            # Admins don't need to request
            return JsonResponse({
                'success': True,
                'classes': [],
                'message': 'Admins have automatic access to all classes'
            })
        
        if not teacher:
            return JsonResponse({'success': False, 'error': 'Teacher profile not found'})
        
        # Get teacher's current classes
        my_classes = TeacherClassAssignment.objects.filter(
            teacher=teacher,
            is_active=True
        ).values_list('class_code', flat=True)
        
        # Get all available classes from PrimePath curriculum mapping
        all_class_codes = list(CLASS_CODE_CURRICULUM_MAPPING.keys())
        
        available = []
        for class_code in all_class_codes:
            if class_code not in my_classes:
                # Check if request pending
                is_pending = ClassAccessRequest.objects.filter(
                    teacher=teacher,
                    class_code=class_code,
                    status='PENDING'
                ).exists()
                
                class_name = f"{class_code} - {CLASS_CODE_CURRICULUM_MAPPING.get(class_code, class_code)}"
                available.append({
                    'class_code': class_code,
                    'class_name': class_name,
                    'is_pending': is_pending
                })
        
        return JsonResponse({
            'success': True,
            'classes': available
        })
        
    except Exception as e:
        logger.error(f"Error in api_available_classes: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def api_my_requests(request):
    """API endpoint to get teacher's access requests"""
    try:
        teacher = Teacher.objects.get(user=request.user)
        
        requests = ClassAccessRequest.objects.filter(
            teacher=teacher
        ).order_by('-requested_at')
        
        # Import curriculum mapping for proper class names
        
        request_data = [{
            'id': r.id,
            'class_code': r.class_code,
            'class_name': f"{r.class_code} - {CLASS_CODE_CURRICULUM_MAPPING.get(r.class_code, r.class_code)}",
            'status': r.status,
            'status_display': r.get_status_display(),
            'requested_at': r.requested_at.isoformat(),
            'approved_at': r.approved_at.isoformat() if r.approved_at else None
        } for r in requests]
        
        return JsonResponse({
            'success': True,
            'requests': request_data
        })
        
    except Teacher.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Teacher profile not found'})
    except Exception as e:
        logger.error(f"Error in api_my_requests: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def api_class_current_teachers(request, class_code):
    """API endpoint to get current teachers for a class"""
    try:
        assignments = TeacherClassAssignment.objects.filter(
            class_code=class_code,
            is_active=True
        ).select_related('teacher')
        
        teachers = [{
            'id': a.teacher.id,
            'name': a.teacher.name,
            'email': a.teacher.email,
            'access_level': a.get_access_level_display()
        } for a in assignments]
        
        return JsonResponse({
            'success': True,
            'teachers': teachers,
            'class_code': class_code
        })
        
    except Exception as e:
        logger.error(f"Error in api_class_current_teachers: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def admin_teacher_assignments(request):
    """Admin view for managing all teacher assignments"""
    # Check admin access
    is_admin, teacher = is_admin_or_head_teacher(request.user)
    if not is_admin:
        messages.error(request, 'Admin access required')
        return redirect('RoutineTest:my_classes')
    
    # Get all assignments
    assignments = TeacherClassAssignment.objects.filter(
        is_active=True
    ).select_related('teacher').order_by('class_code', 'teacher__name')
    
    # Group by class
    assignments_by_class = {}
    for assignment in assignments:
        if assignment.class_code not in assignments_by_class:
            assignments_by_class[assignment.class_code] = []
        assignments_by_class[assignment.class_code].append(assignment)
    
    # Get all teachers
    all_teachers = Teacher.objects.all().order_by('name')
    
    context = {
        'assignments_by_class': assignments_by_class,
        'all_teachers': all_teachers,
        'class_choices': TeacherClassAssignment._meta.get_field('class_code').choices,
        'is_admin': True,
        'is_head_teacher': True
    }
    
    return render(request, 'primepath_routinetest/admin_teacher_assignments.html', context)


@login_required
@require_POST
def admin_direct_assign(request):
    """Admin directly assigns teacher to class"""
    # Check admin access
    is_admin, admin_teacher = is_admin_or_head_teacher(request.user)
    if not is_admin:
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        data = json.loads(request.body)
        teacher_id = data.get('teacher_id')
        class_code = data.get('class_code')
        access_level = data.get('access_level', 'VIEW')
        
        teacher = get_object_or_404(Teacher, id=teacher_id)
        
        # Create or update assignment
        assignment, created = TeacherClassAssignment.objects.get_or_create(
            teacher=teacher,
            class_code=class_code,
            defaults={
                'access_level': access_level,
                'is_active': True,
                'assigned_by': admin_teacher
            }
        )
        
        if not created:
            assignment.access_level = access_level
            assignment.is_active = True
            assignment.assigned_by = admin_teacher
            assignment.save()
        
        # Log the assignment
        AccessAuditLog.objects.create(
            teacher=teacher,
            action='ADMIN_DIRECT_ASSIGN',
            details=f'Assigned to {class_code} with {access_level} access by {request.user.username}',
            performed_by=admin_teacher
        )
        
        return JsonResponse({
            'success': True,
            'message': f'{teacher.name} assigned to {class_code}',
            'created': created
        })
        
    except Exception as e:
        logger.error(f"Error in admin_direct_assign: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
def admin_revoke_access(request):
    """Admin revokes teacher's class access"""
    # Check admin access
    is_admin, admin_teacher = is_admin_or_head_teacher(request.user)
    if not is_admin:
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        data = json.loads(request.body)
        assignment_id = data.get('assignment_id')
        
        assignment = get_object_or_404(TeacherClassAssignment, id=assignment_id)
        
        # Deactivate assignment
        assignment.is_active = False
        assignment.save()
        
        # Log the revocation
        AccessAuditLog.objects.create(
            teacher=assignment.teacher,
            action='ACCESS_REVOKED',
            details=f'Access to {assignment.class_code} revoked by {request.user.username}',
            performed_by=admin_teacher
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Access revoked for {assignment.teacher.name}'
        })
        
    except Exception as e:
        logger.error(f"Error in admin_revoke_access: {e}")
        return JsonResponse({'success': False, 'error': str(e)})
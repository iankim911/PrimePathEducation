"""
Teacher Class Assessment Module - Admin Only
Manages teacher-class assignments, requests, and access control
Created: August 18, 2025

Features:
1. List of all teachers and their current class assignments
2. Pending class assignment requests from teachers (approve/reject)
3. Direct assignment management with revoke access capability
4. Comprehensive audit logging
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.db.models import Q, Count, F, Prefetch
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.models import User
import json
import logging
import random
from datetime import datetime, timedelta

from primepath_routinetest.models import (
    TeacherClassAssignment,
    ClassAccessRequest,
    AccessAuditLog
)
from core.models import Teacher

logger = logging.getLogger(__name__)


def is_admin_user(user):
    """Check if user is admin (superuser or head teacher)"""
    if user.is_superuser:
        return True
    try:
        teacher = user.teacher_profile
        return teacher.is_head_teacher
    except:
        return False


@login_required
@user_passes_test(is_admin_user)
def teacher_assessment_view(request):
    """
    Main view for Teacher Class Assessment (Admin Only)
    Shows:
    - All teachers and their assignments (left side)
    - Pending requests (right side)
    - Assignment management controls
    """
    console_log = {
        "view": "teacher_assessment",
        "user": request.user.username,
        "timestamp": datetime.now().isoformat(),
        "action": "view_load"
    }
    
    # Get view mode from session
    view_mode = request.session.get('view_mode', 'Teacher')
    
    # Double-check admin access
    if view_mode != 'Admin':
        console_log["error"] = "Access denied - not in Admin mode"
        logger.warning(f"[TEACHER_ASSESSMENT] {json.dumps(console_log)}")
        messages.error(request, "This feature is only available in Admin mode.")
        return redirect('RoutineTest:classes_exams_unified')
    
    print(f"\n{'='*80}")
    print(f"[TEACHER_ASSESSMENT] Loading Teacher Assessment Module")
    print(f"  User: {request.user.username}")
    print(f"  Mode: {view_mode}")
    print(f"  Timestamp: {datetime.now()}")
    print(f"{'='*80}\n")
    
    # Get all teachers with their assignments
    teachers = Teacher.objects.all().prefetch_related(
        Prefetch(
            'class_assignments',
            queryset=TeacherClassAssignment.objects.filter(is_active=True).order_by('class_code'),
            to_attr='active_assignments'
        ),
        Prefetch(
            'access_requests',
            queryset=ClassAccessRequest.objects.filter(status='PENDING').order_by('-requested_at'),
            to_attr='pending_requests'
        )
    ).order_by('name')
    
    # Get pending requests
    pending_requests = ClassAccessRequest.objects.filter(
        status='PENDING'
    ).select_related('teacher').order_by('-requested_at')
    
    # Get recent audit logs - Phase 3: Dynamic limit using DataService
    try:
        from core.services.data_service import get_query_limit
        audit_limit = get_query_limit('dashboard_recent')
    except ImportError:
        audit_limit = 20  # Fallback
    
    recent_logs = AccessAuditLog.objects.all()[:audit_limit]
    
    # Statistics
    stats = {
        'total_teachers': teachers.count(),
        'teachers_with_classes': teachers.filter(class_assignments__is_active=True).distinct().count(),
        'total_assignments': TeacherClassAssignment.objects.filter(is_active=True).count(),
        'pending_requests': pending_requests.count(),
        'approved_today': ClassAccessRequest.objects.filter(
            status='APPROVED',
            reviewed_at__date=timezone.now().date()
        ).count(),
        'denied_today': ClassAccessRequest.objects.filter(
            status='DENIED',
            reviewed_at__date=timezone.now().date()
        ).count()
    }
    
    # Import class choices from constants
    from ..models.class_constants import CLASS_CODE_CHOICES
    CLASS_CHOICES = CLASS_CODE_CHOICES
    
    # Build class assignment matrix
    class_matrix = {}
    for class_code, class_name in CLASS_CHOICES:
        assignments = TeacherClassAssignment.objects.filter(
            class_code=class_code,
            is_active=True
        ).select_related('teacher')
        class_matrix[class_code] = {
            'name': class_name,
            'teachers': assignments,
            'count': assignments.count()
        }
    
    console_log["stats"] = stats
    logger.info(f"[TEACHER_ASSESSMENT] {json.dumps(console_log)}")
    print(f"[TEACHER_ASSESSMENT] Stats: {json.dumps(stats, indent=2)}")
    
    context = {
        'teachers': teachers,
        'pending_requests': pending_requests,
        'recent_logs': recent_logs,
        'stats': stats,
        'class_matrix': class_matrix,
        'class_choices': CLASS_CHOICES,
        'current_view_mode': view_mode,
        'page_title': 'Teacher Class Assessment',
        'is_admin_view': True
    }
    
    return render(request, 'primepath_routinetest/teacher_assessment.html', context)


@login_required
@user_passes_test(is_admin_user)
@require_POST
def approve_teacher_request(request, request_id):
    """Approve a teacher's class access request"""
    try:
        access_request = get_object_or_404(ClassAccessRequest, id=request_id, status='PENDING')
        
        # Log the approval
        console_log = {
            "action": "approve_request",
            "request_id": str(request_id),
            "teacher": access_request.teacher.name,
            "class": access_request.class_code,
            "approved_by": request.user.username,
            "timestamp": datetime.now().isoformat()
        }
        
        # Approve the request
        assignment = access_request.approve(request.user, "Approved via Teacher Assessment module")
        
        # Create audit log
        AccessAuditLog.log_action(
            action='REQUEST_APPROVED',
            teacher=access_request.teacher,
            class_code=access_request.class_code,
            user=request.user,
            details={'reason': 'Approved via Teacher Assessment module'},
            request=access_request,
            assignment=assignment
        )
        
        console_log["status"] = "success"
        console_log["assignment_id"] = str(assignment.id)
        logger.info(f"[TEACHER_ASSESSMENT_APPROVE] {json.dumps(console_log)}")
        print(f"[TEACHER_ASSESSMENT] ✅ Approved: {access_request.teacher.name} for {access_request.get_class_code_display()}")
        
        messages.success(request, f"Approved {access_request.teacher.name}'s request for {access_request.get_class_code_display()}")
        
        return JsonResponse({'success': True, 'message': 'Request approved successfully'})
        
    except Exception as e:
        logger.error(f"[TEACHER_ASSESSMENT_ERROR] Error approving request: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
@user_passes_test(is_admin_user)
@require_POST
def deny_teacher_request(request, request_id):
    """Deny a teacher's class access request"""
    try:
        access_request = get_object_or_404(ClassAccessRequest, id=request_id, status='PENDING')
        
        # Get denial reason from request
        data = json.loads(request.body)
        reason = data.get('reason', 'No reason provided')
        
        # Log the denial
        console_log = {
            "action": "deny_request",
            "request_id": str(request_id),
            "teacher": access_request.teacher.name,
            "class": access_request.class_code,
            "denied_by": request.user.username,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        
        # Deny the request
        access_request.deny(request.user, reason)
        
        # Create audit log
        AccessAuditLog.log_action(
            action='REQUEST_DENIED',
            teacher=access_request.teacher,
            class_code=access_request.class_code,
            user=request.user,
            details={'reason': reason},
            request=access_request
        )
        
        console_log["status"] = "success"
        logger.info(f"[TEACHER_ASSESSMENT_DENY] {json.dumps(console_log)}")
        print(f"[TEACHER_ASSESSMENT] ❌ Denied: {access_request.teacher.name} for {access_request.get_class_code_display()}")
        
        messages.warning(request, f"Denied {access_request.teacher.name}'s request for {access_request.get_class_code_display()}")
        
        return JsonResponse({'success': True, 'message': 'Request denied'})
        
    except Exception as e:
        logger.error(f"[TEACHER_ASSESSMENT_ERROR] Error denying request: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
@user_passes_test(is_admin_user)
@require_POST
def revoke_teacher_access(request):
    """Revoke a teacher's access to a class"""
    try:
        data = json.loads(request.body)
        assignment_id = data.get('assignment_id')
        reason = data.get('reason', 'Access revoked by admin')
        
        assignment = get_object_or_404(TeacherClassAssignment, id=assignment_id, is_active=True)
        
        # Log the revocation
        console_log = {
            "action": "revoke_access",
            "assignment_id": str(assignment_id),
            "teacher": assignment.teacher.name,
            "class": assignment.class_code,
            "revoked_by": request.user.username,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        
        # Revoke the assignment
        assignment.is_active = False
        assignment.notes = f"Revoked: {reason} (by {request.user.username} on {timezone.now()})"
        assignment.save()
        
        # Create audit log
        AccessAuditLog.log_action(
            action='ASSIGNMENT_REVOKED',
            teacher=assignment.teacher,
            class_code=assignment.class_code,
            user=request.user,
            details={'reason': reason},
            assignment=assignment
        )
        
        console_log["status"] = "success"
        logger.info(f"[TEACHER_ASSESSMENT_REVOKE] {json.dumps(console_log)}")
        print(f"[TEACHER_ASSESSMENT] 🚫 Revoked: {assignment.teacher.name} from {assignment.get_class_code_display()}")
        
        messages.info(request, f"Revoked {assignment.teacher.name}'s access to {assignment.get_class_code_display()}")
        
        return JsonResponse({'success': True, 'message': 'Access revoked successfully'})
        
    except Exception as e:
        logger.error(f"[TEACHER_ASSESSMENT_ERROR] Error revoking access: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
@user_passes_test(is_admin_user)
@require_POST
def direct_assign_teacher(request):
    """Directly assign a teacher to a class without a request"""
    try:
        data = json.loads(request.body)
        teacher_id = data.get('teacher_id')
        class_code = data.get('class_code')
        access_level = data.get('access_level', 'FULL')
        notes = data.get('notes', '')
        
        teacher = get_object_or_404(Teacher, id=teacher_id)
        
        # Check if assignment already exists
        existing = TeacherClassAssignment.objects.filter(
            teacher=teacher,
            class_code=class_code,
            is_active=True
        ).first()
        
        if existing:
            return JsonResponse({
                'success': False,
                'message': f'{teacher.name} already has access to this class'
            }, status=400)
        
        # Log the assignment
        console_log = {
            "action": "direct_assign",
            "teacher": teacher.name,
            "class": class_code,
            "access_level": access_level,
            "assigned_by": request.user.username,
            "timestamp": datetime.now().isoformat()
        }
        
        # Create the assignment
        assignment = TeacherClassAssignment.objects.create(
            teacher=teacher,
            class_code=class_code,
            access_level=access_level,
            assigned_by=request.user,
            notes=f"Direct assignment: {notes}" if notes else "Direct assignment by admin",
            is_active=True
        )
        
        # Create audit log
        AccessAuditLog.log_action(
            action='ASSIGNMENT_CREATED',
            teacher=teacher,
            class_code=class_code,
            user=request.user,
            details={'access_level': access_level, 'notes': notes},
            assignment=assignment
        )
        
        console_log["status"] = "success"
        console_log["assignment_id"] = str(assignment.id)
        logger.info(f"[TEACHER_ASSESSMENT_ASSIGN] {json.dumps(console_log)}")
        print(f"[TEACHER_ASSESSMENT] ✅ Assigned: {teacher.name} to {assignment.get_class_code_display()}")
        
        messages.success(request, f"Assigned {teacher.name} to {assignment.get_class_code_display()}")
        
        return JsonResponse({'success': True, 'message': 'Teacher assigned successfully'})
        
    except Exception as e:
        logger.error(f"[TEACHER_ASSESSMENT_ERROR] Error assigning teacher: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
@user_passes_test(is_admin_user)
@require_POST
def bulk_approve_requests(request):
    """Bulk approve multiple requests"""
    try:
        data = json.loads(request.body)
        request_ids = data.get('request_ids', [])
        
        approved_count = 0
        errors = []
        
        for request_id in request_ids:
            try:
                access_request = ClassAccessRequest.objects.get(id=request_id, status='PENDING')
                access_request.approve(request.user, "Bulk approved via Teacher Assessment")
                approved_count += 1
                
                print(f"[BULK_APPROVE] ✅ {access_request.teacher.name} for {access_request.get_class_code_display()}")
                
            except Exception as e:
                errors.append(f"Failed to approve {request_id}: {str(e)}")
        
        # Log bulk action
        AccessAuditLog.log_action(
            action='BULK_APPROVAL',
            teacher=None,
            class_code='MULTIPLE',
            user=request.user,
            details={'approved_count': approved_count, 'request_ids': request_ids}
        )
        
        if errors:
            return JsonResponse({
                'success': False,
                'message': f'Approved {approved_count} requests. Errors: {", ".join(errors)}'
            }, status=207)
        
        messages.success(request, f"Successfully approved {approved_count} requests")
        return JsonResponse({'success': True, 'message': f'Approved {approved_count} requests'})
        
    except Exception as e:
        logger.error(f"[TEACHER_ASSESSMENT_ERROR] Error in bulk approval: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
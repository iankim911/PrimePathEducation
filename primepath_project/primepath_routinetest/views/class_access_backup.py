"""
Teacher Class Access Management Views
Part of RoutineTest module

Provides views for:
- Teacher class access management (single tab with split view)
- Request submission and management
- Admin approval workflow
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

from primepath_routinetest.models import (
    TeacherClassAssignment,
    ClassAccessRequest,
    AccessAuditLog,
    Exam,
    StudentRoster
)
from core.models import Teacher

logger = logging.getLogger(__name__)


@login_required
def my_classes_view(request):
    """
    Main view for teacher's "My Classes & Access" tab.
    Shows current classes on left (60%) and request section on right (40%).
    Admins see a different view with all teacher assignments.
    """
    # Enhanced console logging for debugging
    print(f"[CLASS_ACCESS_VIEW_DEBUG] ========== Starting my_classes_view ==========")
    print(f"[CLASS_ACCESS_VIEW_DEBUG] User: {request.user.username}")
    print(f"[CLASS_ACCESS_VIEW_DEBUG] Is authenticated: {request.user.is_authenticated}")
    print(f"[CLASS_ACCESS_VIEW_DEBUG] Is staff: {request.user.is_staff}")
    print(f"[CLASS_ACCESS_VIEW_DEBUG] Is superuser: {request.user.is_superuser}")
    print(f"[CLASS_ACCESS_VIEW_DEBUG] Request path: {request.path}")
    
    try:
        # Try to get teacher profile - create if doesn't exist for staff users
        teacher = None
        if hasattr(request.user, 'teacher_profile'):
            teacher = request.user.teacher_profile
        elif request.user.is_staff or request.user.is_superuser:
            # Auto-create teacher profile for staff users if it doesn't exist
            from core.models import Teacher
            teacher, created = Teacher.objects.get_or_create(
                email=request.user.email or f"{request.user.username}@example.com",
                defaults={
                    'name': request.user.get_full_name() or request.user.username,
                    'user': request.user,
                    'is_head_teacher': request.user.is_superuser
                }
            )
            if created:
                print(f"[CLASS_ACCESS_VIEW_DEBUG] Created teacher profile for {request.user.username}")
            # Link to user if not already linked
            if not teacher.user:
                teacher.user = request.user
                teacher.save()
        
        if not teacher:
            print(f"[CLASS_ACCESS_VIEW_DEBUG] No teacher profile found, redirecting")
            messages.warning(request, "Teacher profile required to access this page.")
            return redirect('RoutineTest:index')
            
        # Determine if user should see admin view
        # For now, prioritize teacher view unless explicitly superuser
        show_admin_view = request.user.is_superuser and request.GET.get('admin_view', 'false') == 'true'
        
        print(f"[CLASS_ACCESS_VIEW_DEBUG] Teacher found: {teacher.name}")
        print(f"[CLASS_ACCESS_VIEW_DEBUG] Show admin view: {show_admin_view}")
        print(f"[CLASS_ACCESS_VIEW_DEBUG] ==========================================")
        
        context = {
            'is_admin': show_admin_view,
            'teacher': teacher,
            'show_teacher_view': not show_admin_view,  # Explicitly show teacher view by default
        }
        
        if show_admin_view:
            # Admin view: show all teacher assignments and pending requests
            all_assignments = TeacherClassAssignment.objects.filter(
                is_active=True
            ).select_related('teacher').order_by('class_code', 'teacher__name')
            
            # Group assignments by class
            assignments_by_class = {}
            for assignment in all_assignments:
                class_code = assignment.class_code
                if class_code not in assignments_by_class:
                    assignments_by_class[class_code] = {
                        'class_name': assignment.get_class_code_display(),
                        'teachers': [],
                        'student_count': assignment.get_student_count()
                    }
                assignments_by_class[class_code]['teachers'].append({
                    'teacher': assignment.teacher,
                    'access_level': assignment.get_access_level_display(),
                    'assigned_date': assignment.assigned_date,
                    'assignment_id': assignment.id
                })
            
            # Get pending requests
            pending_requests = ClassAccessRequest.objects.filter(
                status='PENDING'
            ).select_related('teacher').order_by('-requested_at')
            
            context.update({
                'assignments_by_class': assignments_by_class,
                'pending_requests': pending_requests,
                'pending_count': pending_requests.count(),
            })
            
            # Log admin access
            console_log = {
                "view": "my_classes_view",
                "user": request.user.username,
                "is_admin": True,
                "total_assignments": all_assignments.count(),
                "pending_requests": pending_requests.count()
            }
            
        else:
            # Teacher view: show their classes and available classes
            # Get teacher's current class assignments
            my_assignments = TeacherClassAssignment.objects.filter(
                teacher=teacher,
                is_active=True
            ).order_by('class_code')
            
            # Process assignments for display
            my_classes = []
            my_class_codes = []
            for assignment in my_assignments:
                # Get student count for this class
                student_count = StudentRoster.objects.filter(
                    class_code=assignment.class_code
                ).values('student_name').distinct().count()
                
                # Get active exams for this class
                # Note: class_codes__contains doesn't work on SQLite, use alternative approach
                try:
                    active_exams = Exam.objects.filter(
                        class_codes__contains=assignment.class_code,
                        is_active=True
                    ).count()
                except:
                    # Fallback for SQLite - fetch all and filter in Python
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
            
            # Get available classes (not assigned to this teacher)
            all_class_codes = [choice[0] for choice in TeacherClassAssignment._meta.get_field('class_code').choices]
            available_class_codes = [code for code in all_class_codes if code not in my_class_codes]
            
            # Check for pending requests
            pending_requests = ClassAccessRequest.objects.filter(
                teacher=teacher,
                status='PENDING'
            )
            pending_class_codes = [req.class_code for req in pending_requests]
            
            # Process available classes
            available_classes = []
            for class_code in available_class_codes:
                # Get current teachers for this class
                current_assignments = TeacherClassAssignment.objects.filter(
                    class_code=class_code,
                    is_active=True
                ).select_related('teacher')
                
                # Get class display name
                class_name = dict(TeacherClassAssignment._meta.get_field('class_code').choices).get(class_code, class_code)
                
                # Check if request is pending
                is_pending = class_code in pending_class_codes
                
                available_classes.append({
                    'class_code': class_code,
                    'class_name': class_name,
                    'current_teachers': current_assignments,
                    'teacher_count': current_assignments.count(),
                    'is_pending': is_pending,
                })
            
            # Get teacher's recent requests (all statuses)
            my_requests = ClassAccessRequest.objects.filter(
                teacher=teacher
            ).order_by('-requested_at')[:10]  # Last 10 requests
            
            context.update({
                'my_classes': my_classes,
                'available_classes': available_classes,
                'my_requests': my_requests,
                'pending_requests': pending_requests,
                'my_class_count': len(my_classes),
                'available_count': len(available_classes),
            })
            
            # Log teacher access
            console_log = {
                "view": "my_classes_view",
                "user": request.user.username,
                "teacher": teacher.name,
                "is_admin": False,
                "my_classes": len(my_classes),
                "available_classes": len(available_classes),
                "pending_requests": pending_requests.count()
            }
        
        logger.info(f"[CLASS_ACCESS_VIEW] {json.dumps(console_log)}")
        print(f"[CLASS_ACCESS_VIEW] {json.dumps(console_log)}")
        
        return render(request, 'primepath_routinetest/class_access.html', context)
        
    except Exception as e:
        # Check if it's a Teacher.DoesNotExist error
        if 'Teacher' in str(type(e).__name__):
            messages.error(request, "Teacher profile not found. Please contact admin.")
        else:
            logger.error(f"[CLASS_ACCESS_ERROR] Error in my_classes_view: {str(e)}")
            messages.error(request, "An error occurred. Please try again.")
        return redirect('RoutineTest:index')


@login_required
@require_POST
def request_access(request):
    """Submit a new class access request"""
    try:
        teacher = request.user.teacher_profile
        
        # Get form data
        class_code = request.POST.get('class_code')
        request_type = request.POST.get('request_type', 'PERMANENT')
        reason_code = request.POST.get('reason_code', 'NEW_ASSIGNMENT')
        reason_text = request.POST.get('reason_text', '')
        access_level = request.POST.get('access_level', 'FULL')
        
        # Parse dates for temporary requests
        duration_start = request.POST.get('duration_start')
        duration_end = request.POST.get('duration_end')
        
        # Validate class code
        valid_classes = [choice[0] for choice in TeacherClassAssignment._meta.get_field('class_code').choices]
        if class_code not in valid_classes:
            return JsonResponse({'error': 'Invalid class code'}, status=400)
        
        # Check if teacher already has access
        existing_assignment = TeacherClassAssignment.objects.filter(
            teacher=teacher,
            class_code=class_code,
            is_active=True
        ).first()
        
        if existing_assignment:
            return JsonResponse({'error': 'You already have access to this class'}, status=400)
        
        # Check for pending request
        pending_request = ClassAccessRequest.objects.filter(
            teacher=teacher,
            class_code=class_code,
            status='PENDING'
        ).first()
        
        if pending_request:
            return JsonResponse({'error': 'You already have a pending request for this class'}, status=400)
        
        # Create the request
        access_request = ClassAccessRequest.objects.create(
            teacher=teacher,
            class_code=class_code,
            request_type=request_type,
            reason_code=reason_code,
            reason_text=reason_text,
            requested_access_level=access_level,
            duration_start=duration_start if request_type == 'TEMPORARY' and duration_start else None,
            duration_end=duration_end if request_type == 'TEMPORARY' and duration_end else None,
        )
        
        # Create audit log
        AccessAuditLog.log_action(
            action='REQUEST_CREATED',
            teacher=teacher,
            class_code=class_code,
            user=request.user,
            details={
                'request_type': request_type,
                'reason': reason_code,
                'access_level': access_level
            },
            request=access_request
        )
        
        # Log successful request
        console_log = {
            "view": "request_access",
            "action": "request_created",
            "teacher": teacher.name,
            "class_code": class_code,
            "request_id": str(access_request.id)
        }
        logger.info(f"[ACCESS_REQUEST] {json.dumps(console_log)}")
        print(f"[ACCESS_REQUEST] {json.dumps(console_log)}")
        
        return JsonResponse({
            'success': True,
            'message': 'Access request submitted successfully',
            'request_id': str(access_request.id)
        })
        
    except Exception as e:
        logger.error(f"[ACCESS_REQUEST_ERROR] {str(e)}")
        return JsonResponse({'error': 'Failed to submit request'}, status=500)


@login_required
@require_POST
def withdraw_request(request, request_id):
    """Withdraw a pending access request"""
    try:
        teacher = request.user.teacher_profile
        access_request = get_object_or_404(
            ClassAccessRequest,
            id=request_id,
            teacher=teacher,
            status='PENDING'
        )
        
        access_request.withdraw()
        
        # Create audit log
        AccessAuditLog.log_action(
            action='REQUEST_WITHDRAWN',
            teacher=teacher,
            class_code=access_request.class_code,
            user=request.user,
            request=access_request
        )
        
        messages.success(request, 'Request withdrawn successfully')
        return redirect('RoutineTest:my_classes')
        
    except Exception as e:
        logger.error(f"[WITHDRAW_ERROR] {str(e)}")
        messages.error(request, 'Failed to withdraw request')
        return redirect('RoutineTest:my_classes')


@login_required
def admin_pending_requests(request):
    """Admin view for all pending requests"""
    if not (request.user.is_superuser or request.user.teacher_profile.is_head_teacher):
        messages.error(request, 'Admin access required')
        return redirect('RoutineTest:index')
    
    pending_requests = ClassAccessRequest.objects.filter(
        status='PENDING'
    ).select_related('teacher').order_by('-requested_at')
    
    # Add current teacher info for each request
    for req in pending_requests:
        req.current_teachers = TeacherClassAssignment.objects.filter(
            class_code=req.class_code,
            is_active=True
        ).select_related('teacher')
    
    context = {
        'pending_requests': pending_requests,
        'pending_count': pending_requests.count(),
    }
    
    return render(request, 'primepath_routinetest/admin_pending_requests.html', context)


@login_required
@require_POST
def approve_request(request, request_id):
    """Approve an access request"""
    if not (request.user.is_superuser or request.user.teacher_profile.is_head_teacher):
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    try:
        access_request = get_object_or_404(ClassAccessRequest, id=request_id, status='PENDING')
        admin_notes = request.POST.get('admin_notes', '')
        
        # Approve the request (creates assignment automatically)
        assignment = access_request.approve(request.user, admin_notes)
        
        # Create audit log
        AccessAuditLog.log_action(
            action='REQUEST_APPROVED',
            teacher=access_request.teacher,
            class_code=access_request.class_code,
            user=request.user,
            details={'admin_notes': admin_notes},
            request=access_request,
            assignment=assignment
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Request approved. {access_request.teacher.name} now has access to {access_request.get_class_code_display()}'
        })
        
    except Exception as e:
        logger.error(f"[APPROVE_ERROR] {str(e)}")
        return JsonResponse({'error': 'Failed to approve request'}, status=500)


@login_required
@require_POST
def deny_request(request, request_id):
    """Deny an access request"""
    if not (request.user.is_superuser or request.user.teacher_profile.is_head_teacher):
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    try:
        access_request = get_object_or_404(ClassAccessRequest, id=request_id, status='PENDING')
        reason = request.POST.get('reason', 'No reason provided')
        
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
        
        return JsonResponse({
            'success': True,
            'message': f'Request denied for {access_request.teacher.name}'
        })
        
    except Exception as e:
        logger.error(f"[DENY_ERROR] {str(e)}")
        return JsonResponse({'error': 'Failed to deny request'}, status=500)


@login_required
@require_POST
def bulk_approve_requests(request):
    """Bulk approve multiple requests"""
    if not (request.user.is_superuser or request.user.teacher_profile.is_head_teacher):
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    try:
        request_ids = request.POST.getlist('request_ids[]')
        approved_count = 0
        
        for request_id in request_ids:
            try:
                access_request = ClassAccessRequest.objects.get(id=request_id, status='PENDING')
                assignment = access_request.approve(request.user, 'Bulk approved')
                
                # Create audit log
                AccessAuditLog.log_action(
                    action='BULK_APPROVAL',
                    teacher=access_request.teacher,
                    class_code=access_request.class_code,
                    user=request.user,
                    request=access_request,
                    assignment=assignment
                )
                
                approved_count += 1
            except Exception as e:
                logger.error(f"[BULK_APPROVE_ERROR] Failed to approve request {request_id}: {str(e)}")
                continue
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully approved {approved_count} requests'
        })
        
    except Exception as e:
        logger.error(f"[BULK_APPROVE_ERROR] {str(e)}")
        return JsonResponse({'error': 'Failed to bulk approve'}, status=500)


# AJAX API endpoints for dynamic updates

@login_required
def api_my_classes(request):
    """API endpoint to get teacher's current classes"""
    try:
        teacher = request.user.teacher_profile
        assignments = TeacherClassAssignment.objects.filter(
            teacher=teacher,
            is_active=True
        ).order_by('class_code')
        
        classes = []
        for assignment in assignments:
            classes.append({
                'class_code': assignment.class_code,
                'class_name': assignment.get_class_code_display(),
                'access_level': assignment.access_level,
                'student_count': assignment.get_student_count(),
                'assigned_date': assignment.assigned_date.isoformat(),
            })
        
        return JsonResponse({'classes': classes})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_available_classes(request):
    """API endpoint to get available classes for request"""
    try:
        teacher = request.user.teacher_profile
        
        # Get teacher's current classes
        my_class_codes = TeacherClassAssignment.objects.filter(
            teacher=teacher,
            is_active=True
        ).values_list('class_code', flat=True)
        
        # Get all class codes
        all_class_codes = [choice[0] for choice in TeacherClassAssignment._meta.get_field('class_code').choices]
        
        # Filter available classes
        available_classes = []
        for class_code in all_class_codes:
            if class_code not in my_class_codes:
                class_name = dict(TeacherClassAssignment._meta.get_field('class_code').choices).get(class_code)
                
                # Check for pending request
                has_pending = ClassAccessRequest.objects.filter(
                    teacher=teacher,
                    class_code=class_code,
                    status='PENDING'
                ).exists()
                
                available_classes.append({
                    'class_code': class_code,
                    'class_name': class_name,
                    'has_pending_request': has_pending
                })
        
        return JsonResponse({'available_classes': available_classes})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_my_requests(request):
    """API endpoint to get teacher's access requests"""
    try:
        teacher = request.user.teacher_profile
        
        requests_list = []
        my_requests = ClassAccessRequest.objects.filter(
            teacher=teacher
        ).order_by('-requested_at')[:20]
        
        for req in my_requests:
            requests_list.append({
                'id': str(req.id),
                'class_code': req.class_code,
                'class_name': req.get_class_code_display(),
                'status': req.status,
                'status_display': req.get_status_display(),
                'requested_at': req.requested_at.isoformat(),
                'reason': req.reason_text,
            })
        
        return JsonResponse({'requests': requests_list})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_class_current_teachers(request, class_code):
    """API endpoint to get current teachers for a class"""
    try:
        assignments = TeacherClassAssignment.objects.filter(
            class_code=class_code,
            is_active=True
        ).select_related('teacher')
        
        teachers = []
        for assignment in assignments:
            teachers.append({
                'name': assignment.teacher.name,
                'access_level': assignment.get_access_level_display(),
            })
        
        return JsonResponse({'teachers': teachers})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Admin management views

@login_required
def admin_teacher_assignments(request):
    """Admin view to see all teacher assignments"""
    if not (request.user.is_superuser or request.user.teacher_profile.is_head_teacher):
        messages.error(request, 'Admin access required')
        return redirect('RoutineTest:index')
    
    assignments = TeacherClassAssignment.objects.filter(
        is_active=True
    ).select_related('teacher').order_by('class_code', 'teacher__name')
    
    context = {
        'assignments': assignments,
        'total_assignments': assignments.count(),
    }
    
    return render(request, 'primepath_routinetest/admin_teacher_assignments.html', context)


@login_required
@require_POST
def admin_direct_assign(request):
    """Admin directly assigns a teacher to a class"""
    if not (request.user.is_superuser or request.user.teacher_profile.is_head_teacher):
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    try:
        teacher_id = request.POST.get('teacher_id')
        class_code = request.POST.get('class_code')
        access_level = request.POST.get('access_level', 'FULL')
        notes = request.POST.get('notes', '')
        
        teacher = get_object_or_404(Teacher, id=teacher_id)
        
        # Check for existing assignment
        existing = TeacherClassAssignment.objects.filter(
            teacher=teacher,
            class_code=class_code,
            is_active=True
        ).first()
        
        if existing:
            return JsonResponse({'error': 'Teacher already has access to this class'}, status=400)
        
        # Create assignment
        assignment = TeacherClassAssignment.objects.create(
            teacher=teacher,
            class_code=class_code,
            access_level=access_level,
            assigned_by=request.user,
            notes=notes
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
        
        return JsonResponse({
            'success': True,
            'message': f'{teacher.name} assigned to {assignment.get_class_code_display()}'
        })
        
    except Exception as e:
        logger.error(f"[DIRECT_ASSIGN_ERROR] {str(e)}")
        return JsonResponse({'error': 'Failed to assign teacher'}, status=500)


@login_required
@require_POST
def admin_revoke_access(request):
    """Admin revokes a teacher's access to a class"""
    if not (request.user.is_superuser or request.user.teacher_profile.is_head_teacher):
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    try:
        assignment_id = request.POST.get('assignment_id')
        reason = request.POST.get('reason', '')
        
        assignment = get_object_or_404(TeacherClassAssignment, id=assignment_id, is_active=True)
        
        # Deactivate the assignment
        assignment.is_active = False
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
        
        return JsonResponse({
            'success': True,
            'message': f'Access revoked for {assignment.teacher.name}'
        })
        
    except Exception as e:
        logger.error(f"[REVOKE_ERROR] {str(e)}")
        return JsonResponse({'error': 'Failed to revoke access'}, status=500)
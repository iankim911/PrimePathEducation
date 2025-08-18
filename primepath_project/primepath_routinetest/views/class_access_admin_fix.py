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
    Exam,
    StudentRoster
)
from core.models import Teacher

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
            
            # Get ALL class codes from the system
            all_class_codes = [choice[0] for choice in TeacherClassAssignment._meta.get_field('class_code').choices]
            
            # Create virtual assignments for ALL classes (admin has implicit access)
            admin_classes = []
            for class_code in all_class_codes:
                # Get actual teachers assigned (excluding admin's virtual access)
                actual_assignments = TeacherClassAssignment.objects.filter(
                    class_code=class_code,
                    is_active=True
                ).exclude(teacher=teacher).select_related('teacher')
                
                # Get student count
                student_count = StudentRoster.objects.filter(
                    class_code=class_code
                ).values('student_name').distinct().count()
                
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
                
                # Get class display name
                class_name = dict(TeacherClassAssignment._meta.get_field('class_code').choices).get(class_code, class_code)
                
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
                # Get student count
                student_count = StudentRoster.objects.filter(
                    class_code=assignment.class_code
                ).values('student_name').distinct().count()
                
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
            
            # Get available classes
            all_class_codes = [choice[0] for choice in TeacherClassAssignment._meta.get_field('class_code').choices]
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
                
                class_name = dict(TeacherClassAssignment._meta.get_field('class_code').choices).get(class_code, class_code)
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
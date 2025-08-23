"""
Comprehensive Teacher Access Management Dashboard
CRITICAL: Multi-Teacher Class Support with Complete Admin Interface

This module provides a comprehensive admin interface for managing teacher-class assignments:
1. View all teacher-class relationships in multiple formats
2. Direct assignment of teachers to classes (bypass request system)
3. Multi-teacher class management with visual indicators
4. Centralized request management with context
5. Access analytics and reporting

Created: August 22, 2025
Purpose: Complete teacher access control system for admins
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Count, Prefetch
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
import json
import logging
from datetime import datetime, timedelta
from collections import defaultdict

from primepath_routinetest.models import (
    TeacherClassAssignment,
    ClassAccessRequest,
    AccessAuditLog,
    Exam,
    Class
)
from core.models import Teacher

logger = logging.getLogger(__name__)


def is_admin_user(user):
    """Check if user has admin privileges"""
    return user.is_superuser or (hasattr(user, 'teacher_profile') and user.teacher_profile.is_head_teacher)


@login_required
def teacher_access_management_dashboard(request):
    """
    COMPREHENSIVE ADMIN DASHBOARD for Teacher Access Management
    
    Provides multiple views:
    1. Teacher Directory (all teachers with their class assignments)
    2. Class Directory (all classes with their assigned teachers)
    3. Matrix View (teacher × class grid)
    4. Request Management (pending requests with context)
    5. Analytics (summary statistics)
    """
    start_time = datetime.now()
    
    # Admin access check
    if not is_admin_user(request.user):
        messages.error(request, 'Admin access required for teacher management')
        return redirect('RoutineTest:classes_exams_unified')
    
    # Comprehensive logging
    console_log = {
        "view": "teacher_access_management_dashboard",
        "user": request.user.username,
        "timestamp": start_time.isoformat(),
        "action": "dashboard_start"
    }
    logger.info(f"[TEACHER_MGMT_DASHBOARD] {json.dumps(console_log)}")
    print(f"\n{'='*80}")
    print(f"[TEACHER_MGMT_DASHBOARD] Comprehensive Teacher Access Management")
    print(f"[TEACHER_MGMT_DASHBOARD] Admin: {request.user.username}")
    print(f"[TEACHER_MGMT_DASHBOARD] Time: {start_time}")
    print(f"{'='*80}\n")
    
    try:
        # Get view mode from request
        view_mode = request.GET.get('view', 'overview')  # overview, teachers, classes, matrix, requests
        
        # SECTION 1: Core Data Collection with Performance Optimization
        print(f"[TEACHER_MGMT] Loading core data...")
        
        # Get all teachers with optimized queries
        all_teachers = Teacher.objects.select_related('user').prefetch_related(
            Prefetch(
                'class_assignments',
                queryset=TeacherClassAssignment.objects.filter(is_active=True).select_related('teacher'),
                to_attr='active_assignments'
            ),
            Prefetch(
                'access_requests',
                queryset=ClassAccessRequest.objects.filter(status='PENDING').order_by('-requested_at'),
                to_attr='pending_requests'
            )
        ).filter(is_active=True).order_by('name')
        
        # Get all classes from the database
        try:
            all_classes = Class.objects.filter(is_active=True).prefetch_related(
                'assigned_teachers'
            ).order_by('grade_level', 'section')
            class_codes_from_db = [(cls.section, cls.name) for cls in all_classes if cls.section]
        except Exception as e:
            logger.warning(f"[TEACHER_MGMT] Could not load classes from database: {str(e)}")
            print(f"[TEACHER_MGMT] ⚠️  Database classes not available, using assignment choices")
            # Fallback to choices from TeacherClassAssignment model
            class_codes_from_db = list(TeacherClassAssignment._meta.get_field('class_code').choices)
            all_classes = []
        
        # Get all active assignments for matrix building
        all_assignments = TeacherClassAssignment.objects.filter(
            is_active=True
        ).select_related('teacher').order_by('class_code', 'teacher__name')
        
        # Get all pending requests
        pending_requests = ClassAccessRequest.objects.filter(
            status='PENDING'
        ).select_related('teacher').order_by('-requested_at')
        
        # SECTION 2: Teacher Directory Data
        print(f"[TEACHER_MGMT] Building teacher directory...")
        teacher_directory = []
        
        for teacher in all_teachers:
            # Count assignments
            assignment_count = len(teacher.active_assignments)
            pending_count = len(teacher.pending_requests)
            
            # Get classes with access levels
            teacher_classes = []
            for assignment in teacher.active_assignments:
                # Get class name from database or fallback to choices
                class_name = assignment.class_code
                for cls in all_classes:
                    if cls.section == assignment.class_code:
                        class_name = cls.name
                        break
                else:
                    # Fallback to choices
                    class_name = dict(class_codes_from_db).get(assignment.class_code, assignment.class_code)
                
                teacher_classes.append({
                    'class_code': assignment.class_code,
                    'class_name': class_name,
                    'access_level': assignment.access_level,
                    'assigned_date': assignment.assigned_date,
                    'assignment_id': str(assignment.id)
                })
            
            teacher_directory.append({
                'teacher': teacher,
                'assignment_count': assignment_count,
                'pending_requests_count': pending_count,
                'classes': teacher_classes,
                'global_access_level': teacher.global_access_level,
                'can_manage_exams': teacher.can_manage_exams(),
                'last_login': teacher.user.last_login if teacher.user else None
            })
        
        # SECTION 3: Class Directory Data
        print(f"[TEACHER_MGMT] Building class directory...")
        class_directory = []
        
        # Build class directory from actual assignments
        class_assignments_dict = defaultdict(list)
        for assignment in all_assignments:
            class_assignments_dict[assignment.class_code].append(assignment)
        
        for class_code, class_name in class_codes_from_db:
            assignments = class_assignments_dict.get(class_code, [])
            
            # Get class details from database if available
            class_obj = None
            for cls in all_classes:
                if cls.section == class_code:
                    class_obj = cls
                    break
            
            # Count exams for this class
            try:
                exam_count = Exam.objects.filter(
                    class_codes__contains=class_code,
                    is_active=True
                ).count()
            except:
                # SQLite fallback
                all_exams = Exam.objects.filter(is_active=True)
                exam_count = sum(1 for exam in all_exams if class_code in (exam.class_codes or []))
            
            # Get teacher assignments with full details
            class_teachers = []
            for assignment in assignments:
                class_teachers.append({
                    'teacher': assignment.teacher,
                    'access_level': assignment.access_level,
                    'assigned_date': assignment.assigned_date,
                    'assignment_id': str(assignment.id),
                    'global_access_level': assignment.teacher.global_access_level
                })
            
            # Check for pending requests for this class
            class_pending_requests = [req for req in pending_requests if req.class_code == class_code]
            
            class_directory.append({
                'class_code': class_code,
                'class_name': class_name,
                'class_obj': class_obj,
                'teacher_count': len(assignments),
                'teachers': class_teachers,
                'exam_count': exam_count,
                'pending_requests': class_pending_requests,
                'student_count': class_obj.student_count if class_obj else 0
            })
        
        # Sort class directory by class name
        class_directory.sort(key=lambda x: x['class_name'])
        
        # SECTION 4: Matrix View Data
        print(f"[TEACHER_MGMT] Building teacher-class matrix...")
        
        # Build matrix for first 20 teachers and 30 classes (performance limit)
        matrix_teachers = teacher_directory[:20]
        matrix_classes = class_directory[:30]
        
        # Create assignment lookup for quick matrix building
        assignment_lookup = {}
        for assignment in all_assignments:
            key = f"{assignment.teacher.id}_{assignment.class_code}"
            assignment_lookup[key] = assignment
        
        matrix_data = {}
        for teacher_data in matrix_teachers:
            teacher_id = teacher_data['teacher'].id
            matrix_data[teacher_id] = {}
            
            for class_data in matrix_classes:
                class_code = class_data['class_code']
                key = f"{teacher_id}_{class_code}"
                
                if key in assignment_lookup:
                    assignment = assignment_lookup[key]
                    matrix_data[teacher_id][class_code] = {
                        'has_access': True,
                        'access_level': assignment.access_level,
                        'assignment_id': str(assignment.id),
                        'assigned_date': assignment.assigned_date
                    }
                else:
                    matrix_data[teacher_id][class_code] = {
                        'has_access': False,
                        'access_level': None,
                        'assignment_id': None,
                        'assigned_date': None
                    }
        
        # SECTION 5: Request Management Data
        print(f"[TEACHER_MGMT] Processing access requests...")
        
        request_management_data = []
        for access_request in pending_requests:
            # Get current teachers for the requested class
            current_teachers = TeacherClassAssignment.objects.filter(
                class_code=access_request.class_code,
                is_active=True
            ).select_related('teacher')
            
            # Get class name
            class_name = access_request.class_code
            for class_data in class_directory:
                if class_data['class_code'] == access_request.class_code:
                    class_name = class_data['class_name']
                    break
            
            request_management_data.append({
                'request': access_request,
                'class_name': class_name,
                'current_teachers': current_teachers,
                'current_teacher_count': current_teachers.count(),
                'days_pending': (timezone.now() - access_request.requested_at).days
            })
        
        # SECTION 6: Analytics and Summary Statistics
        print(f"[TEACHER_MGMT] Calculating analytics...")
        
        analytics = {
            'total_teachers': len(all_teachers),
            'active_assignments': all_assignments.count(),
            'pending_requests': pending_requests.count(),
            'total_classes': len(class_codes_from_db),
            'classes_with_teachers': len([cd for cd in class_directory if cd['teacher_count'] > 0]),
            'classes_without_teachers': len([cd for cd in class_directory if cd['teacher_count'] == 0]),
            'multi_teacher_classes': len([cd for cd in class_directory if cd['teacher_count'] > 1]),
            'teachers_with_full_access': len([td for td in teacher_directory if td['global_access_level'] == 'FULL']),
            'teachers_with_view_access': len([td for td in teacher_directory if td['global_access_level'] == 'VIEW_ONLY']),
            'avg_classes_per_teacher': round(sum(td['assignment_count'] for td in teacher_directory) / len(teacher_directory), 1) if teacher_directory else 0,
            'avg_teachers_per_class': round(sum(cd['teacher_count'] for cd in class_directory) / len(class_directory), 1) if class_directory else 0
        }
        
        # Get recent activity (last 7 days)
        recent_activity = AccessAuditLog.objects.filter(
            timestamp__gte=timezone.now() - timedelta(days=7)
        ).select_related('teacher').order_by('-timestamp')[:20]
        
        # Calculate performance metrics
        duration = (datetime.now() - start_time).total_seconds()
        
        # Build context based on view mode
        context = {
            'view_mode': view_mode,
            'user': request.user,
            'is_admin': True,
            'teacher_directory': teacher_directory,
            'class_directory': class_directory,
            'matrix_data': matrix_data,
            'matrix_teachers': matrix_teachers,
            'matrix_classes': matrix_classes,
            'request_management_data': request_management_data,
            'analytics': analytics,
            'recent_activity': recent_activity,
            'pending_requests': pending_requests,
            'all_teachers_for_assignment': all_teachers,
            'all_classes_for_assignment': class_codes_from_db,
            'render_time': f"{duration:.2f}s",
            'timestamp': timezone.now()
        }
        
        # Final logging
        final_log = {
            "view": "teacher_access_management_dashboard",
            "action": "completed",
            "user": request.user.username,
            "view_mode": view_mode,
            "teachers_loaded": len(teacher_directory),
            "classes_loaded": len(class_directory),
            "assignments_processed": all_assignments.count(),
            "pending_requests": pending_requests.count(),
            "duration_seconds": duration,
            "analytics": analytics
        }
        logger.info(f"[TEACHER_MGMT_COMPLETE] {json.dumps(final_log)}")
        print(f"\n[TEACHER_MGMT] ✅ Dashboard completed in {duration:.2f} seconds")
        print(f"[TEACHER_MGMT] Teachers: {len(teacher_directory)}, Classes: {len(class_directory)}")
        print(f"[TEACHER_MGMT] Assignments: {all_assignments.count()}, Pending: {pending_requests.count()}")
        print(f"{'='*80}\n")
        
        return render(request, 'primepath_routinetest/admin_teacher_management.html', context)
        
    except Exception as e:
        # Comprehensive error handling
        error_details = {
            "view": "teacher_access_management_dashboard",
            "user": request.user.username,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "timestamp": datetime.now().isoformat()
        }
        logger.error(f"[TEACHER_MGMT_ERROR] {json.dumps(error_details)}", exc_info=True)
        print(f"\n[TEACHER_MGMT_ERROR] {json.dumps(error_details, indent=2)}")
        
        messages.error(request, f"Error loading teacher management dashboard: {str(e)}")
        return redirect('RoutineTest:classes_exams_unified')


@login_required
@require_POST
def admin_direct_assign_teacher(request):
    """
    DIRECT TEACHER ASSIGNMENT - Bypass request system
    
    Allows admin to directly assign any teacher to any class with any access level.
    This is the primary method for admins to manage teacher-class relationships.
    """
    if not is_admin_user(request.user):
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        data = json.loads(request.body)
        teacher_id = data.get('teacher_id')
        class_code = data.get('class_code')
        access_level = data.get('access_level', 'FULL')
        notes = data.get('notes', '')
        
        console_log = {
            "action": "admin_direct_assign_teacher",
            "admin": request.user.username,
            "teacher_id": teacher_id,
            "class_code": class_code,
            "access_level": access_level,
            "timestamp": datetime.now().isoformat()
        }
        print(f"[DIRECT_ASSIGN] {json.dumps(console_log)}")
        
        # Validate inputs
        if not teacher_id or not class_code:
            return JsonResponse({'success': False, 'error': 'Teacher and class required'})
        
        teacher = get_object_or_404(Teacher, id=teacher_id)
        
        # Get admin teacher profile
        admin_teacher = getattr(request.user, 'teacher_profile', None)
        
        # Check if assignment already exists
        existing_assignment = TeacherClassAssignment.objects.filter(
            teacher=teacher,
            class_code=class_code,
            is_active=True
        ).first()
        
        if existing_assignment:
            # Update existing assignment
            existing_assignment.access_level = access_level
            if notes:
                existing_assignment.notes = notes
            existing_assignment.save()
            
            action_taken = "updated"
            assignment = existing_assignment
        else:
            # Create new assignment
            assignment = TeacherClassAssignment.objects.create(
                teacher=teacher,
                class_code=class_code,
                access_level=access_level,
                assigned_by=request.user,
                notes=notes
            )
            action_taken = "created"
        
        # Log the action
        AccessAuditLog.log_action(
            action='ADMIN_DIRECT_ASSIGN',
            teacher=teacher,
            class_code=class_code,
            user=request.user,
            details={
                'access_level': access_level,
                'action_taken': action_taken,
                'notes': notes
            },
            assignment=assignment
        )
        
        # Get class name for response
        class_name = class_code
        try:
            class_obj = Class.objects.filter(section=class_code).first()
            if class_obj:
                class_name = class_obj.name
        except:
            pass
        
        success_log = {
            "action": "admin_direct_assign_success",
            "admin": request.user.username,
            "teacher": teacher.name,
            "class_code": class_code,
            "access_level": access_level,
            "assignment_id": str(assignment.id),
            "action_taken": action_taken
        }
        logger.info(f"[DIRECT_ASSIGN_SUCCESS] {json.dumps(success_log)}")
        print(f"[DIRECT_ASSIGN] ✅ {action_taken.title()} assignment: {teacher.name} -> {class_name}")
        
        return JsonResponse({
            'success': True,
            'message': f'{teacher.name} {action_taken} for {class_name} with {access_level} access',
            'assignment_id': str(assignment.id),
            'action_taken': action_taken,
            'teacher_name': teacher.name,
            'class_name': class_name,
            'access_level': access_level
        })
        
    except Exception as e:
        error_log = {
            "action": "admin_direct_assign_error",
            "admin": request.user.username,
            "error": str(e),
            "data": data if 'data' in locals() else None
        }
        logger.error(f"[DIRECT_ASSIGN_ERROR] {json.dumps(error_log)}")
        print(f"[DIRECT_ASSIGN] ❌ Error: {str(e)}")
        
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
def admin_revoke_teacher_access(request):
    """
    REVOKE TEACHER ACCESS - Remove teacher from class
    
    Safely removes a teacher's access to a specific class while preserving
    other teachers' access to the same class.
    """
    if not is_admin_user(request.user):
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        data = json.loads(request.body)
        assignment_id = data.get('assignment_id')
        reason = data.get('reason', 'No reason provided')
        
        console_log = {
            "action": "admin_revoke_teacher_access",
            "admin": request.user.username,
            "assignment_id": assignment_id,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        print(f"[REVOKE_ACCESS] {json.dumps(console_log)}")
        
        assignment = get_object_or_404(TeacherClassAssignment, id=assignment_id, is_active=True)
        
        # Store info for logging before deactivating
        teacher_name = assignment.teacher.name
        class_code = assignment.class_code
        
        # Deactivate assignment (don't delete for audit trail)
        assignment.is_active = False
        assignment.notes = f"{assignment.notes}\n\nRevoked by {request.user.username}: {reason}".strip()
        assignment.save()
        
        # Log the revocation
        AccessAuditLog.log_action(
            action='ACCESS_REVOKED',
            teacher=assignment.teacher,
            class_code=class_code,
            user=request.user,
            details={
                'reason': reason,
                'previous_access_level': assignment.access_level
            },
            assignment=assignment
        )
        
        # Get class name for response
        class_name = class_code
        try:
            class_obj = Class.objects.filter(section=class_code).first()
            if class_obj:
                class_name = class_obj.name
        except:
            pass
        
        success_log = {
            "action": "admin_revoke_success",
            "admin": request.user.username,
            "teacher": teacher_name,
            "class_code": class_code,
            "assignment_id": str(assignment.id),
            "reason": reason
        }
        logger.info(f"[REVOKE_SUCCESS] {json.dumps(success_log)}")
        print(f"[REVOKE_ACCESS] ✅ Revoked: {teacher_name} from {class_name}")
        
        return JsonResponse({
            'success': True,
            'message': f'Revoked {teacher_name} access to {class_name}',
            'teacher_name': teacher_name,
            'class_name': class_name
        })
        
    except Exception as e:
        error_log = {
            "action": "admin_revoke_error",
            "admin": request.user.username,
            "error": str(e),
            "assignment_id": assignment_id if 'assignment_id' in locals() else None
        }
        logger.error(f"[REVOKE_ERROR] {json.dumps(error_log)}")
        print(f"[REVOKE_ACCESS] ❌ Error: {str(e)}")
        
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
def admin_bulk_assign_teachers(request):
    """
    BULK ASSIGNMENT OPERATIONS
    
    Allows admin to assign multiple teachers to multiple classes at once.
    Useful for setting up new academic year or mass transfers.
    """
    if not is_admin_user(request.user):
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        data = json.loads(request.body)
        teacher_ids = data.get('teacher_ids', [])
        class_codes = data.get('class_codes', [])
        access_level = data.get('access_level', 'FULL')
        notes = data.get('notes', 'Bulk assignment by admin')
        
        console_log = {
            "action": "admin_bulk_assign_teachers",
            "admin": request.user.username,
            "teacher_count": len(teacher_ids),
            "class_count": len(class_codes),
            "access_level": access_level,
            "timestamp": datetime.now().isoformat()
        }
        print(f"[BULK_ASSIGN] {json.dumps(console_log)}")
        
        if not teacher_ids or not class_codes:
            return JsonResponse({'success': False, 'error': 'Teachers and classes required'})
        
        # Get teachers
        teachers = Teacher.objects.filter(id__in=teacher_ids)
        if teachers.count() != len(teacher_ids):
            return JsonResponse({'success': False, 'error': 'Some teachers not found'})
        
        # Validate class codes
        valid_class_codes = [choice[0] for choice in TeacherClassAssignment._meta.get_field('class_code').choices]
        invalid_codes = [code for code in class_codes if code not in valid_class_codes]
        if invalid_codes:
            return JsonResponse({'success': False, 'error': f'Invalid class codes: {invalid_codes}'})
        
        assignments_created = 0
        assignments_updated = 0
        assignments_skipped = 0
        
        # Process each teacher-class combination
        for teacher in teachers:
            for class_code in class_codes:
                try:
                    # Check if assignment already exists
                    existing = TeacherClassAssignment.objects.filter(
                        teacher=teacher,
                        class_code=class_code,
                        is_active=True
                    ).first()
                    
                    if existing:
                        # Update existing
                        existing.access_level = access_level
                        existing.notes = f"{existing.notes}\n\nBulk updated: {notes}".strip()
                        existing.save()
                        assignments_updated += 1
                    else:
                        # Create new
                        TeacherClassAssignment.objects.create(
                            teacher=teacher,
                            class_code=class_code,
                            access_level=access_level,
                            assigned_by=request.user,
                            notes=notes
                        )
                        assignments_created += 1
                    
                    # Log individual assignment
                    AccessAuditLog.log_action(
                        action='BULK_ASSIGNMENT',
                        teacher=teacher,
                        class_code=class_code,
                        user=request.user,
                        details={
                            'access_level': access_level,
                            'bulk_operation': True,
                            'notes': notes
                        }
                    )
                    
                except Exception as individual_error:
                    logger.warning(f"[BULK_ASSIGN] Failed for {teacher.name} -> {class_code}: {individual_error}")
                    assignments_skipped += 1
                    continue
        
        success_log = {
            "action": "admin_bulk_assign_success",
            "admin": request.user.username,
            "assignments_created": assignments_created,
            "assignments_updated": assignments_updated,
            "assignments_skipped": assignments_skipped,
            "total_operations": len(teacher_ids) * len(class_codes)
        }
        logger.info(f"[BULK_ASSIGN_SUCCESS] {json.dumps(success_log)}")
        print(f"[BULK_ASSIGN] ✅ Created: {assignments_created}, Updated: {assignments_updated}, Skipped: {assignments_skipped}")
        
        return JsonResponse({
            'success': True,
            'message': f'Bulk assignment completed: {assignments_created} created, {assignments_updated} updated, {assignments_skipped} skipped',
            'assignments_created': assignments_created,
            'assignments_updated': assignments_updated,
            'assignments_skipped': assignments_skipped,
            'total_operations': len(teacher_ids) * len(class_codes)
        })
        
    except Exception as e:
        error_log = {
            "action": "admin_bulk_assign_error",
            "admin": request.user.username,
            "error": str(e)
        }
        logger.error(f"[BULK_ASSIGN_ERROR] {json.dumps(error_log)}")
        print(f"[BULK_ASSIGN] ❌ Error: {str(e)}")
        
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def api_teacher_class_matrix(request):
    """
    API endpoint for dynamic matrix view updates
    Returns teacher-class relationship data for AJAX updates
    """
    if not is_admin_user(request.user):
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        # Get parameters
        teacher_limit = int(request.GET.get('teacher_limit', 20))
        class_limit = int(request.GET.get('class_limit', 30))
        
        # Get teachers and classes
        teachers = Teacher.objects.filter(is_active=True).order_by('name')[:teacher_limit]
        class_codes = [choice[0] for choice in TeacherClassAssignment._meta.get_field('class_code').choices][:class_limit]
        
        # Get all relevant assignments
        assignments = TeacherClassAssignment.objects.filter(
            teacher__in=teachers,
            class_code__in=class_codes,
            is_active=True
        ).select_related('teacher')
        
        # Build matrix data
        matrix = {}
        for teacher in teachers:
            matrix[str(teacher.id)] = {
                'teacher_name': teacher.name,
                'teacher_id': str(teacher.id),
                'global_access': teacher.global_access_level,
                'classes': {}
            }
            
            for class_code in class_codes:
                matrix[str(teacher.id)]['classes'][class_code] = {
                    'has_access': False,
                    'access_level': None,
                    'assignment_id': None
                }
        
        # Fill in actual assignments
        for assignment in assignments:
            teacher_id = str(assignment.teacher.id)
            class_code = assignment.class_code
            
            if teacher_id in matrix and class_code in matrix[teacher_id]['classes']:
                matrix[teacher_id]['classes'][class_code] = {
                    'has_access': True,
                    'access_level': assignment.access_level,
                    'assignment_id': str(assignment.id)
                }
        
        return JsonResponse({
            'success': True,
            'matrix': matrix,
            'teacher_count': len(teachers),
            'class_count': len(class_codes)
        })
        
    except Exception as e:
        logger.error(f"[MATRIX_API_ERROR] {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def api_class_teacher_summary(request, class_code):
    """
    API endpoint to get detailed teacher summary for a specific class
    Used for modal displays and detailed views
    """
    if not is_admin_user(request.user):
        return JsonResponse({'success': False, 'error': 'Admin access required'})
    
    try:
        # Get all teachers assigned to this class
        assignments = TeacherClassAssignment.objects.filter(
            class_code=class_code,
            is_active=True
        ).select_related('teacher').order_by('teacher__name')
        
        # Get class information
        class_name = class_code
        try:
            class_obj = Class.objects.filter(section=class_code).first()
            if class_obj:
                class_name = class_obj.name
        except:
            # Fallback to choices
            class_name = dict(TeacherClassAssignment._meta.get_field('class_code').choices).get(class_code, class_code)
        
        # Get pending requests for this class
        pending_requests = ClassAccessRequest.objects.filter(
            class_code=class_code,
            status='PENDING'
        ).select_related('teacher').order_by('-requested_at')
        
        # Build teacher data
        teachers = []
        for assignment in assignments:
            teachers.append({
                'teacher_id': str(assignment.teacher.id),
                'teacher_name': assignment.teacher.name,
                'access_level': assignment.access_level,
                'global_access_level': assignment.teacher.global_access_level,
                'assigned_date': assignment.assigned_date.isoformat(),
                'assignment_id': str(assignment.id),
                'can_manage_exams': assignment.teacher.can_manage_exams()
            })
        
        # Build pending request data
        requests = []
        for access_request in pending_requests:
            requests.append({
                'request_id': str(access_request.id),
                'teacher_name': access_request.teacher.name,
                'requested_access_level': access_request.requested_access_level,
                'reason': access_request.get_reason_display(),
                'requested_at': access_request.requested_at.isoformat(),
                'days_pending': (timezone.now() - access_request.requested_at).days
            })
        
        return JsonResponse({
            'success': True,
            'class_code': class_code,
            'class_name': class_name,
            'teacher_count': len(teachers),
            'teachers': teachers,
            'pending_requests_count': len(requests),
            'pending_requests': requests
        })
        
    except Exception as e:
        logger.error(f"[CLASS_SUMMARY_API_ERROR] {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})
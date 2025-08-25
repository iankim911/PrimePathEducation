"""
Unified Classes & Exams View - Merges My Classes & Access with Exam Assignments
Implements Option A: Single page with scroll (Overview at top, Classes below)
Created: August 17, 2025

This view combines:
1. Exam Assignments Overview (top section)
2. My Classes & Access details (scrollable below)
"""
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, F
from django.utils import timezone
from django.core.cache import cache
import json
import logging
from datetime import datetime, timedelta
from collections import defaultdict

from primepath_routinetest.models import (
    TeacherClassAssignment,
    ClassAccessRequest,
    AccessAuditLog,
    Exam,
    ExamScheduleMatrix,
    ClassCurriculumMapping,
    StudentSession
)
from core.models import Teacher
from ..decorators import teacher_required

logger = logging.getLogger(__name__)


def get_teacher_profile(user):
    """Get or create teacher profile for user"""
    try:
        return user.teacher_profile
    except:
        # Create teacher profile if doesn't exist
        if user.is_superuser:
            return Teacher.objects.get_or_create(
                user=user,
                defaults={
                    'name': user.get_full_name() or user.username,
                    'email': user.email or f"{user.username}@example.com",
                    'is_head_teacher': True
                }
            )[0]
        return None


def get_exam_statistics(class_codes, academic_year):
    """Get comprehensive exam statistics for overview dashboard"""
    stats = {
        'total_exams': 0,
        'active_exams': 0,
        'upcoming_exams': 0,
        'completed_sessions': 0,
        'pending_sessions': 0,
        'by_exam_type': defaultdict(int),
        'by_time_period': defaultdict(int),
        'recent_assignments': [],
        'upcoming_deadlines': []
    }
    
    # Get all exams for these classes
    # Note: For SQLite compatibility, we filter in Python rather than DB
    all_exams = Exam.objects.filter(
        academic_year=academic_year,
        is_active=True
    ).prefetch_related('routine_questions', 'routine_sessions')
    
    # Filter exams that match any of the teacher's class codes
    exams = []
    for exam in all_exams:
        if exam.class_codes and any(code in exam.class_codes for code in class_codes):
            exams.append(exam)
    
    now = timezone.now()
    one_week_ahead = now + timedelta(days=7)
    
    for exam in exams:
        stats['total_exams'] += 1
        
        if exam.is_active:
            stats['active_exams'] += 1
            
        # Count by exam type
        stats['by_exam_type'][exam.get_exam_type_display()] += 1
        
        # Count sessions
        sessions = exam.routine_sessions.all()
        for session in sessions:
            if session.completed_at:
                stats['completed_sessions'] += 1
            else:
                stats['pending_sessions'] += 1
        
        # Get recent assignments (last 7 days)
        if exam.created_at and exam.created_at > now - timedelta(days=7):
            stats['recent_assignments'].append({
                'exam_name': exam.get_routinetest_display_name(),
                'created': exam.created_at,
                'classes': exam.class_codes,
                'type': exam.get_exam_type_display()
            })
        
        # Check for upcoming deadlines
        if hasattr(exam, 'timeslot') and exam.timeslot:
            exam_date = exam.timeslot.get('date')
            if exam_date:
                try:
                    deadline = datetime.strptime(exam_date, '%Y-%m-%d')
                    if now.date() <= deadline.date() <= one_week_ahead.date():
                        stats['upcoming_deadlines'].append({
                            'exam_name': exam.get_routinetest_display_name(),
                            'deadline': deadline,
                            'classes': exam.class_codes,
                            'days_remaining': (deadline.date() - now.date()).days
                        })
                except:
                    pass
    
    # Sort recent assignments and deadlines
    stats['recent_assignments'].sort(key=lambda x: x['created'], reverse=True)
    stats['upcoming_deadlines'].sort(key=lambda x: x['deadline'])
    
    # Limit to top 5 for display
    stats['recent_assignments'] = stats['recent_assignments'][:5]
    stats['upcoming_deadlines'] = stats['upcoming_deadlines'][:5]
    
    return stats


@login_required
@teacher_required
def classes_exams_unified_view(request):
    """
    Unified view combining Classes & Exams functionality
    Replaces both my_classes_view and schedule_matrix_view
    """
    start_time = datetime.now()
    
    # Comprehensive logging
    console_log = {
        "view": "classes_exams_unified",
        "user": request.user.username,
        "is_superuser": request.user.is_superuser,
        "timestamp": start_time.isoformat(),
        "action": "view_start"
    }
    logger.info(f"[UNIFIED_VIEW_START] {json.dumps(console_log)}")
    print(f"\n{'='*80}")
    print(f"[UNIFIED_VIEW] Classes & Exams - Unified View")
    print(f"[UNIFIED_VIEW] User: {request.user.username}")
    print(f"[UNIFIED_VIEW] Time: {start_time}")
    print(f"{'='*80}\n")
    
    try:
        # Get teacher profile
        teacher = get_teacher_profile(request.user)
        is_admin = request.user.is_superuser or (teacher and teacher.is_head_teacher)
        
        # Get academic year
        current_year = request.GET.get('year', timezone.now().year)
        
        # Initialize context
        context = {
            'user': request.user,
            'teacher': teacher,
            'is_admin': is_admin,
            'current_year': current_year,
            'view_type': 'unified',
            'tab_name': 'Classes & Exams',
            'cache_bust': timezone.now().timestamp()
        }
        
        # Add available classes for the class access request modal - will be populated later after we know user's assignments
        # We need to wait until we get my_class_codes to filter properly
        context['available_classes'] = []  # Initialize empty, populate after getting assignments
        
        # SECTION 1: Get teacher's class assignments
        if is_admin:
            # Admin has access to all classes - get from actual Class model
            from primepath_routinetest.models.class_model import Class
            from primepath_routinetest.class_code_mapping import CLASS_CODE_CURRICULUM_MAPPING
            
            try:
                # Get all active classes from database
                active_classes = Class.objects.filter(is_active=True).order_by('section')
                all_class_codes = [cls.section for cls in active_classes if cls.section]
                
                logger.info(f"[CLASSES_EXAMS_UNIFIED] Admin mode: Retrieved {len(all_class_codes)} PrimePath classes from database")
                print(f"[CLASSES_EXAMS_UNIFIED] Admin class codes (sample): {all_class_codes[:5] if all_class_codes else 'None'}")
            except Exception as e:
                logger.error(f"[CLASSES_EXAMS_UNIFIED] Error accessing classes: {str(e)}")
                print(f"[CLASSES_EXAMS_UNIFIED] ERROR: Could not access class codes: {str(e)}")
                # No fallback - let it properly show no classes
                all_class_codes = []
            
            # Create virtual assignments for display with robust error handling
            my_assignments = []
            class_lookup = {}
            
            # Build lookup table for class names
            for cls in active_classes:
                if cls.section:
                    # Use curriculum mapping if available, otherwise use class name
                    if cls.section in CLASS_CODE_CURRICULUM_MAPPING:
                        class_lookup[cls.section] = CLASS_CODE_CURRICULUM_MAPPING[cls.section]
                    else:
                        class_lookup[cls.section] = cls.name
            
            for class_code in all_class_codes:
                try:
                    # Create mock assignment object with proper closure handling
                    class MockAssignment:
                        def __init__(self, code, display_name):
                            self.class_code = code
                            self.access_level = 'FULL'
                            self.is_virtual = True
                            # Pre-calculate display name to avoid closure issues
                            self._display_name = display_name
                        
                        def get_class_code_display(self):
                            return self._display_name
                    
                    display_name = class_lookup.get(class_code, class_code)
                    mock_assignment = MockAssignment(class_code, display_name)
                    my_assignments.append(mock_assignment)
                    logger.debug(f"[CLASSES_EXAMS_UNIFIED] Created mock assignment for {class_code}")
                    
                except Exception as e:
                    logger.error(f"[CLASSES_EXAMS_UNIFIED] Error creating mock assignment for {class_code}: {str(e)}")
                    print(f"[CLASSES_EXAMS_UNIFIED] ERROR: Mock assignment failed for {class_code}: {str(e)}")
                    continue
            
            my_class_codes = all_class_codes
            context['admin_all_access'] = True
            
            console_log["admin_mode"] = True
            console_log["total_classes"] = len(all_class_codes)
            
        else:
            # Regular teacher - check GLOBAL access level first
            # CRITICAL: Global access setting determines what they can see/do
            if teacher.has_view_only_access():
                # VIEW ONLY teachers can only see classes but cannot manage them
                my_assignments = TeacherClassAssignment.objects.filter(
                    teacher=teacher,
                    is_active=True
                ).select_related('teacher')
                
                # Add global access indicator to assignments
                for assignment in my_assignments:
                    assignment.effective_access = 'VIEW_ONLY'  # Override with global setting
                
                context['is_view_only_teacher'] = True
                context['global_access_message'] = "View Only Access - You can view class data but cannot create/edit/delete exams"
                
                logger.info(f"[GLOBAL_ACCESS] Teacher {teacher.name} has VIEW ONLY global access - showing all assigned classes in read-only mode")
                print(f"[GLOBAL_ACCESS] VIEW ONLY teacher: {teacher.name} - {len(my_assignments)} classes (read-only)")
                
            else:
                # FULL ACCESS teachers can manage classes
                my_assignments = TeacherClassAssignment.objects.filter(
                    teacher=teacher,
                    is_active=True
                ).select_related('teacher')
                
                # Add global access indicator to assignments
                for assignment in my_assignments:
                    assignment.effective_access = 'FULL'  # Global setting allows full access
                
                context['is_view_only_teacher'] = False
                context['global_access_message'] = "Full Access - You can create, edit, and delete exams in your assigned classes"
                
                logger.info(f"[GLOBAL_ACCESS] Teacher {teacher.name} has FULL global access - can manage all assigned classes")
                print(f"[GLOBAL_ACCESS] FULL ACCESS teacher: {teacher.name} - {len(my_assignments)} classes (full management)")
            
            my_class_codes = [a.class_code for a in my_assignments]
            context['admin_all_access'] = False
            context['teacher_global_access'] = teacher.global_access_level
            
            # Log the global access system
            total_assignments = TeacherClassAssignment.objects.filter(
                teacher=teacher,
                is_active=True
            ).count()
            logger.info(f"[GLOBAL_ACCESS_SYSTEM] Teacher {teacher.name}: Global={teacher.global_access_level}, Assignments={total_assignments}, CanManage={teacher.can_manage_exams()}")
            print(f"[GLOBAL_ACCESS_SYSTEM] {teacher.name}: {teacher.global_access_level} access level, {total_assignments} classes")
            
            console_log["admin_mode"] = False
            console_log["assigned_classes"] = my_class_codes
        
        # SECTION 2: Get exam statistics for overview dashboard
        exam_stats = get_exam_statistics(my_class_codes, current_year)
        context['exam_stats'] = exam_stats
        
        console_log["stats"] = {
            "total_exams": exam_stats['total_exams'],
            "active_exams": exam_stats['active_exams'],
            "completed_sessions": exam_stats['completed_sessions'],
            "pending_sessions": exam_stats['pending_sessions']
        }
        
        # SECTION 2.5: Populate available classes for Request Access modal (excluding classes user already has access to)
        from primepath_routinetest.class_code_mapping import CLASS_CODE_CURRICULUM_MAPPING
        available_classes = []
        
        # Get existing pending/approved requests to also exclude them
        existing_requests = set()
        if teacher and not is_admin:
            existing_request_codes = ClassAccessRequest.objects.filter(
                teacher=teacher,
                status__in=['PENDING', 'APPROVED']
            ).values_list('class_code', flat=True)
            existing_requests = set(existing_request_codes)
        
        # Filter out classes user already has access to + pending/approved requests
        for code, curriculum in CLASS_CODE_CURRICULUM_MAPPING.items():
            # Skip if user already has access to this class
            if code not in my_class_codes and code not in existing_requests:
                available_classes.append({
                    'class_code': code,
                    'class_name': f"{code} - {curriculum}"
                })
        
        # Update context with filtered available classes
        context['available_classes'] = available_classes
        
        logger.info(f"[REQUEST_ACCESS_FILTER] User has access to {len(my_class_codes)} classes, {len(existing_requests)} pending/approved requests, showing {len(available_classes)} available classes for request")
        print(f"[REQUEST_ACCESS_FILTER] Filtered dropdown: User classes: {len(my_class_codes)}, Available for request: {len(available_classes)}")
        
        # SECTION 3: Build schedule matrix data (RESTORED FULL FUNCTIONALITY)
        # Matrix uses months (JAN-DEC) for Review exams and quarters (Q1-Q4) for Quarterly exams
        months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
                  'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        quarters = ['Q1', 'Q2', 'Q3', 'Q4']
        timeslots = months + quarters  # Combined matrix with both monthly and quarterly periods
        
        # Build comprehensive matrix structure with robust error handling
        matrix_data = {}
        matrix_performance_log = {
            "total_classes": len(my_class_codes),
            "total_timeslots": len(timeslots),
            "successful_cells": 0,
            "failed_cells": 0,
            "cached_cells": 0,
            "errors": []
        }
        
        logger.info(f"[MATRIX_RESTORE] Building matrix for {len(my_class_codes)} classes across {len(timeslots)} time periods")
        print(f"[MATRIX_RESTORE] Starting matrix build: {len(my_class_codes)} classes × {len(timeslots)} periods = {len(my_class_codes) * len(timeslots)} cells")
        
        for class_code in my_class_codes[:20]:  # Limit to 20 classes for performance
            try:
                # Add curriculum mapping for this class - Matrix optimization removed
                # from primepath_routinetest.views.schedule_matrix_optimized import get_class_curriculum_mapping_cached
                curriculum_mapping = None  # Matrix optimization removed, handled via unified view now
                
                matrix_data[class_code] = {
                    'curriculum_mapping': curriculum_mapping
                }
                
                for timeslot in timeslots:
                    try:
                        # Check cache first for performance
                        cache_key = f"matrix_cell_v2_{class_code}_{timeslot}_{current_year}"
                        cached_cell = cache.get(cache_key)
                        
                        if cached_cell:
                            matrix_data[class_code][timeslot] = cached_cell
                            matrix_performance_log["cached_cells"] += 1
                            continue
                        
                        # Determine time period type based on timeslot format
                        if timeslot in months:
                            time_period_type = 'MONTHLY'
                            time_period_value = timeslot
                        elif timeslot in quarters:
                            time_period_type = 'QUARTERLY' 
                            time_period_value = timeslot
                        else:
                            logger.warning(f"[MATRIX_RESTORE] Unknown timeslot format: {timeslot}")
                            continue
                        
                        # Query ExamScheduleMatrix for this specific cell
                        try:
                            matrix_cell = ExamScheduleMatrix.objects.filter(
                                class_code=class_code,
                                academic_year=current_year,
                                time_period_type=time_period_type,
                                time_period_value=time_period_value
                            ).prefetch_related('exams').first()
                            
                        except Exception as query_error:
                            logger.error(f"[MATRIX_RESTORE] Database query failed for {class_code}-{timeslot}: {str(query_error)}")
                            matrix_performance_log["errors"].append(f"DB_QUERY:{class_code}-{timeslot}:{str(query_error)}")
                            matrix_cell = None
                        
                        # Build cell data structure
                        cell_data = {
                            'has_exam': False,
                            'review': None,
                            'quarterly': None,
                            'cell_id': None,
                            'exam_count': 0,
                            'status': 'EMPTY'
                        }
                        
                        if matrix_cell:
                            try:
                                exams = matrix_cell.exams.all()
                                exam_count = len(exams)
                                
                                cell_data.update({
                                    'cell_id': str(matrix_cell.id),
                                    'exam_count': exam_count,
                                    'status': matrix_cell.status,
                                    'has_exam': exam_count > 0
                                })
                                
                                # Categorize exams by type
                                review_exams = []
                                quarterly_exams = []
                                
                                for exam in exams:
                                    try:
                                        if exam.exam_type == 'REVIEW':
                                            review_exams.append({
                                                'id': str(exam.id),
                                                'name': exam.name[:30],  # Truncate for display
                                                'curriculum': exam.curriculum_level.full_name if exam.curriculum_level else 'N/A'
                                            })
                                        elif exam.exam_type == 'QUARTERLY':
                                            quarterly_exams.append({
                                                'id': str(exam.id),
                                                'name': exam.name[:30],
                                                'curriculum': exam.curriculum_level.full_name if exam.curriculum_level else 'N/A'
                                            })
                                    except Exception as exam_error:
                                        logger.warning(f"[MATRIX_RESTORE] Error processing exam {exam.id}: {str(exam_error)}")
                                        continue
                                
                                # Set exam data based on type
                                if review_exams:
                                    cell_data['review'] = review_exams[0] if len(review_exams) == 1 else {
                                        'id': 'multiple',
                                        'name': f"{len(review_exams)} Review Exams",
                                        'curriculum': 'Multiple'
                                    }
                                
                                if quarterly_exams:
                                    cell_data['quarterly'] = quarterly_exams[0] if len(quarterly_exams) == 1 else {
                                        'id': 'multiple', 
                                        'name': f"{len(quarterly_exams)} Quarterly Exams",
                                        'curriculum': 'Multiple'
                                    }
                                
                                matrix_performance_log["successful_cells"] += 1
                                
                            except Exception as cell_processing_error:
                                logger.error(f"[MATRIX_RESTORE] Error processing matrix cell {matrix_cell.id}: {str(cell_processing_error)}")
                                matrix_performance_log["errors"].append(f"CELL_PROCESSING:{class_code}-{timeslot}:{str(cell_processing_error)}")
                                matrix_performance_log["failed_cells"] += 1
                        else:
                            # No matrix cell exists - this is normal for empty periods
                            matrix_performance_log["successful_cells"] += 1
                        
                        matrix_data[class_code][timeslot] = cell_data
                        
                        # Cache successful results for 10 minutes
                        cache.set(cache_key, cell_data, 600)
                        
                    except Exception as timeslot_error:
                        logger.error(f"[MATRIX_RESTORE] Error processing timeslot {timeslot} for class {class_code}: {str(timeslot_error)}")
                        matrix_performance_log["errors"].append(f"TIMESLOT:{class_code}-{timeslot}:{str(timeslot_error)}")
                        matrix_performance_log["failed_cells"] += 1
                        
                        # Provide fallback empty cell
                        matrix_data[class_code][timeslot] = {
                            'has_exam': False,
                            'review': None,
                            'quarterly': None,
                            'cell_id': None,
                            'exam_count': 0,
                            'status': 'ERROR'
                        }
                        continue
                        
            except Exception as class_error:
                logger.error(f"[MATRIX_RESTORE] Error processing class {class_code}: {str(class_error)}")
                matrix_performance_log["errors"].append(f"CLASS:{class_code}:{str(class_error)}")
                continue
        
        # Log comprehensive performance metrics
        console_log.update({
            "matrix_performance": matrix_performance_log,
            "matrix_classes_loaded": len(matrix_data),
            "matrix_restoration": "COMPLETED"
        })
        
        logger.info(f"[MATRIX_RESTORE_COMPLETE] {json.dumps(matrix_performance_log)}")
        print(f"[MATRIX_RESTORE] ✅ Matrix restoration completed!")
        print(f"[MATRIX_RESTORE] Classes: {len(matrix_data)}, Successful cells: {matrix_performance_log['successful_cells']}")
        print(f"[MATRIX_RESTORE] Failed cells: {matrix_performance_log['failed_cells']}, Cached cells: {matrix_performance_log['cached_cells']}")
        if matrix_performance_log["errors"]:
            print(f"[MATRIX_RESTORE] ⚠️ Errors encountered: {len(matrix_performance_log['errors'])}")
            for error in matrix_performance_log["errors"][:5]:  # Show first 5 errors
                print(f"[MATRIX_RESTORE] Error: {error}")
        else:
            print(f"[MATRIX_RESTORE] 🎉 No errors encountered!")
        
        context['matrix_data'] = matrix_data
        context['timeslots'] = timeslots
        
        # SECTION 4: Organize classes by program for new Class Management section
        from collections import defaultdict
        from primepath_routinetest.class_code_mapping import CLASS_CODE_CURRICULUM_MAPPING
        
        # Define program mapping
        PROGRAM_MAPPING = {
            'CORE': [],
            'ASCENT': [],
            'EDGE': [],
            'PINNACLE': []
        }
        
        # Map class codes to programs based on curriculum mapping
        for code, curriculum in CLASS_CODE_CURRICULUM_MAPPING.items():
            if 'CORE' in curriculum:
                PROGRAM_MAPPING['CORE'].append(code)
            elif 'ASCENT' in curriculum:
                PROGRAM_MAPPING['ASCENT'].append(code)
            elif 'EDGE' in curriculum:
                PROGRAM_MAPPING['EDGE'].append(code)
            elif 'PINNACLE' in curriculum:
                PROGRAM_MAPPING['PINNACLE'].append(code)
        
        # Get all exams for counting
        all_class_exams = Exam.objects.filter(
            is_active=True,
            academic_year=current_year
        )
        
        # Build program-organized data structure
        programs_data = []
        
        for program_name in ['CORE', 'ASCENT', 'EDGE', 'PINNACLE']:
            program_classes = []
            total_students = 0
            total_exams = 0
            incomplete_assignments = 0
            
            # Get classes for this program that the user has access to
            for assignment in my_assignments[:20]:  # Limit for performance
                if assignment.class_code in PROGRAM_MAPPING[program_name]:
                    # Get class details
                    class_name = assignment.get_class_code_display() if hasattr(assignment, 'get_class_code_display') else assignment.class_code
                    
                    # Get full curriculum information from mapping
                    curriculum_full = CLASS_CODE_CURRICULUM_MAPPING.get(assignment.class_code, '')
                    
                    # Parse curriculum components (e.g., "CORE Phonics Level 1")
                    if curriculum_full:
                        parts = curriculum_full.split()
                        if len(parts) >= 3:
                            # Format: "CORE • Phonics • Level 1"
                            curriculum_display = f"{parts[0]} • {' '.join(parts[1:-1])} • {parts[-1]}"
                        else:
                            curriculum_display = curriculum_full
                    else:
                        curriculum_display = "Level 1"
                    
                    curriculum_level = curriculum_full.split(' ')[-1] if curriculum_full else 'Level 1'
                    
                    # Count active exams for this class
                    class_exam_count = 0
                    for exam in all_class_exams:
                        if exam.class_codes and assignment.class_code in exam.class_codes:
                            class_exam_count += 1
                    
                    # Check if all required exams are assigned (simplified logic)
                    # Assuming 12 months + 4 quarters = 16 required assignments per year
                    required_assignments = 16
                    all_exams_assigned = class_exam_count >= required_assignments
                    
                    # Get student sessions for this class
                    completed_sessions = 0
                    pending_sessions = 0
                    total_score = 0
                    score_count = 0
                    
                    # For SQLite compatibility, we'll use simplified counts
                    try:
                        sessions = StudentSession.objects.filter(
                            exam__class_codes__contains=assignment.class_code
                        )[:100]  # Limit for performance
                        
                        for session in sessions:
                            if session.completed_at:
                                completed_sessions += 1
                                if hasattr(session, 'final_score') and session.final_score:
                                    total_score += session.final_score
                                    score_count += 1
                            else:
                                pending_sessions += 1
                    except:
                        pass
                    
                    avg_score = round(total_score / score_count) if score_count > 0 else None
                    
                    class_data = {
                        'class_code': assignment.class_code,
                        'class_name': class_name,
                        'access_level': 'FULL ACCESS',  # CLASS ACCESS: You either have access or you don't - no "VIEW ONLY" for class access
                        'curriculum_level': curriculum_level,
                        'curriculum_full': curriculum_display,  # Full curriculum display
                        'student_count': 0,  # Simplified for now
                        'active_exams': class_exam_count,
                        'all_exams_assigned': all_exams_assigned,
                        'completed_sessions': completed_sessions,
                        'pending_sessions': pending_sessions,
                        'avg_score': avg_score
                    }
                    
                    program_classes.append(class_data)
                    total_students += class_data['student_count']
                    total_exams += class_data['active_exams']
                    if not all_exams_assigned:
                        incomplete_assignments += 1
            
            # Only add program if it has classes
            if program_classes or is_admin:
                programs_data.append({
                    'name': program_name,
                    'classes': program_classes,
                    'total_students': total_students,
                    'total_exams': total_exams,
                    'incomplete_assignments': incomplete_assignments
                })
        
        context['programs_data'] = programs_data
        
        # SECTION 4.5: Build Access Summary Data - UPDATED FOR GLOBAL ACCESS SYSTEM
        # NEW: Use GLOBAL access level instead of per-class access levels
        assigned_classes = []
        total_assigned_students = 0
        total_assigned_exams = 0
        
        if is_admin:
            # Admin stats
            total_classes = len(all_class_codes) if 'all_class_codes' in locals() else 0
            total_students = StudentSession.objects.values('student_name').distinct().count()
            total_exams = Exam.objects.filter(is_active=True).count()
            
            context['total_classes'] = total_classes
            context['total_students'] = total_students
            context['total_exams'] = total_exams
        else:
            # Teacher stats - ALL classes shown with GLOBAL access level
            # This is the key change: show all assigned classes with global access level
            for assignment in my_assignments:
                class_info = {
                    'class_code': assignment.class_code,
                    'class_name': assignment.get_class_code_display() if hasattr(assignment, 'get_class_code_display') else assignment.class_code,
                    'global_access_level': teacher.global_access_level  # Use teacher's global setting
                }
                
                # ALL classes go into the same list - no more categorization by per-class access
                assigned_classes.append(class_info)
                
                # Count students for assigned classes
                try:
                    class_students = StudentSession.objects.filter(
                        exam__class_codes__contains=assignment.class_code
                    ).values('student_name').distinct().count()
                    total_assigned_students += class_students
                except:
                    pass
                
                # Count exams for assigned classes
                try:
                    class_exams = Exam.objects.filter(
                        is_active=True,
                        class_codes__contains=assignment.class_code
                    ).count()
                    total_assigned_exams += class_exams
                except:
                    pass
            
            # NEW: Single list of assigned classes with global access level
            context['assigned_classes'] = assigned_classes
            context['total_assigned_classes'] = len(my_assignments)
            context['total_assigned_students'] = total_assigned_students
            context['total_assigned_exams'] = total_assigned_exams
            context['global_access_level'] = teacher.global_access_level
            context['can_manage_exams'] = teacher.can_manage_exams()
            
            # Log the new simplified access structure
            logger.info(f"[GLOBAL_ACCESS_SUMMARY] Teacher {teacher.name}: {len(assigned_classes)} classes, global access: {teacher.global_access_level}")
            print(f"[GLOBAL_ACCESS_SUMMARY] Simplified access structure: {len(assigned_classes)} classes with {teacher.global_access_level} access")
        
        # Add current date for the header
        context['current_date'] = timezone.now()
        
        # SECTION 5: My Classes detailed information (keep for backward compatibility)
        classes_info = []
        for assignment in my_assignments[:20]:  # Limit for performance
            class_info = {
                'class_code': assignment.class_code,
                'class_name': assignment.get_class_code_display() if hasattr(assignment, 'get_class_code_display') else assignment.class_code,
                'access_level': 'FULL ACCESS',  # CLASS ACCESS: Binary - you either can access/teach the class or you can't
                'student_count': 0,  # Roster removed
                'active_exams': 0,
                'recent_activity': []
            }
            
            # Get active exams for this class
            # For SQLite compatibility, filter in Python
            all_class_exams = Exam.objects.filter(
                is_active=True,
                academic_year=current_year
            )
            class_exam_count = 0
            for exam in all_class_exams:
                if exam.class_codes and assignment.class_code in exam.class_codes:
                    class_exam_count += 1
            class_info['active_exams'] = class_exam_count
            
            # Get recent activity (last 3 sessions)
            # For SQLite compatibility, we need to get all sessions and filter in Python
            all_sessions = StudentSession.objects.select_related('exam').order_by('-started_at')
            recent_sessions = []
            for session in all_sessions:
                if session.exam and session.exam.class_codes and assignment.class_code in session.exam.class_codes:
                    recent_sessions.append(session)
                    if len(recent_sessions) >= 3:
                        break
            
            for session in recent_sessions:
                class_info['recent_activity'].append({
                    'student': session.student_name if hasattr(session, 'student_name') else 'Student',
                    'exam': session.exam.name[:30] if session.exam else 'Unknown',
                    'started': session.started_at,
                    'completed': session.completed_at is not None
                })
            
            classes_info.append(class_info)
        
        context['classes_info'] = classes_info
        context['my_assignments'] = my_assignments
        
        # SECTION 5: Pending access requests
        if not is_admin and teacher:
            # For teachers - their own pending requests
            pending_requests = ClassAccessRequest.objects.filter(
                teacher=teacher,
                status='PENDING'
            ).count()
            context['pending_requests_count'] = pending_requests
        else:
            context['pending_requests_count'] = 0
        
        # For admins - all pending requests to approve
        if is_admin:
            admin_pending_requests = ClassAccessRequest.objects.filter(
                status='PENDING'
            ).count()
            context['admin_pending_requests_count'] = admin_pending_requests
        else:
            context['admin_pending_requests_count'] = 0
        
        # Add view mode information to context
        view_mode = request.session.get('view_mode', 'Teacher')
        context['view_mode'] = view_mode
        context['is_admin_mode'] = view_mode == 'Admin' and request.user.is_staff
        
        # Calculate view rendering time
        duration = (datetime.now() - start_time).total_seconds()
        context['render_time'] = f"{duration:.2f}s"
        
        # Final logging
        console_log = {
            "view": "classes_exams_unified",
            "action": "view_complete",
            "user": request.user.username,
            "duration_seconds": duration,
            "classes_shown": len(classes_info),
            "exams_found": exam_stats['total_exams'],
            "cache_hits": "enabled",
            "timestamp": datetime.now().isoformat()
        }
        logger.info(f"[UNIFIED_VIEW_COMPLETE] {json.dumps(console_log)}")
        print(f"\n[UNIFIED_VIEW] Completed in {duration:.2f} seconds")
        print(f"[UNIFIED_VIEW] Classes: {len(classes_info)}, Exams: {exam_stats['total_exams']}")
        print(f"{'='*80}\n")
        
        return render(request, 'primepath_routinetest/classes_exams_unified.html', context)
        
    except Exception as e:
        # Enhanced error handling with detailed logging
        error_details = {
            "view": "classes_exams_unified",
            "user": request.user.username,
            "is_superuser": request.user.is_superuser,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "timestamp": datetime.now().isoformat(),
            "request_path": request.path,
            "request_method": request.method
        }
        
        logger.error(f"[CLASSES_EXAMS_UNIFIED_ERROR] {json.dumps(error_details)}", exc_info=True)
        print(f"\n{'='*80}")
        print(f"[CLASSES_EXAMS_UNIFIED_ERROR] CRITICAL ERROR OCCURRED")
        print(f"[ERROR] Type: {type(e).__name__}")
        print(f"[ERROR] Message: {str(e)}")
        print(f"[ERROR] User: {request.user.username} (Admin: {request.user.is_superuser})")
        print(f"[ERROR] Time: {datetime.now()}")
        print(f"{'='*80}\n")
        
        # Specific handling for variable scoping errors
        if "referenced before assignment" in str(e) and "Exam" in str(e):
            print(f"[ERROR_DIAGNOSIS] This appears to be the variable scoping issue we fixed!")
            print(f"[ERROR_DIAGNOSIS] Check if the fix was applied correctly on line 181-193")
        
        context = {
            'error': True,
            'error_message': f"Error Loading Classes & Exams: {str(e)}",
            'error_type': type(e).__name__,
            'user': request.user,
            'tab_name': 'Classes & Exams',
            'error_timestamp': datetime.now().isoformat(),
            'debug_info': error_details if request.user.is_superuser else None
        }
        
        return render(request, 'primepath_routinetest/classes_exams_unified.html', context)

# Redirect views for backward compatibility
@login_required
@teacher_required
def redirect_my_classes(request):
    """Redirect old my-classes URL to unified view - Version 2"""
    logger.info(f"[REDIRECT_V2] my-classes -> classes-exams for user {request.user.username}")
    print(f"\n{'='*80}")
    print(f"[REDIRECT_V2] Intercepted old URL: /RoutineTest/access/my-classes/")
    print(f"[REDIRECT_V2] Redirecting to: /RoutineTest/classes-exams/")
    print(f"[REDIRECT_V2] User: {request.user.username}")
    print(f"[REDIRECT_V2] Time: {datetime.now()}")
    print(f"{'='*80}\n")
    return redirect('RoutineTest:classes_exams_unified')


@login_required
@teacher_required
def redirect_schedule_matrix(request):
    """Redirect old schedule-matrix URL to unified view - Version 2"""
    logger.info(f"[REDIRECT_V2] schedule-matrix -> classes-exams for user {request.user.username}")
    print(f"\n{'='*80}")
    print(f"[REDIRECT_V2] Intercepted old URL: /RoutineTest/schedule-matrix/")
    print(f"[REDIRECT_V2] Redirecting to: /RoutineTest/classes-exams/")
    print(f"[REDIRECT_V2] User: {request.user.username}")
    print(f"[REDIRECT_V2] Time: {datetime.now()}")
    print(f"{'='*80}\n")
    return redirect('RoutineTest:classes_exams_unified')
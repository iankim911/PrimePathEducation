"""
Optimized Schedule Matrix View - Fixes 504 Gateway Timeout
Reduces database queries and improves performance
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
import json
import logging
from datetime import datetime

from primepath_routinetest.models import (
    Exam, ExamScheduleMatrix, TeacherClassAssignment, ClassCurriculumMapping
)
from core.models import Teacher

logger = logging.getLogger(__name__)


def get_class_curriculum_mapping_cached(class_code, academic_year):
    """
    Cached version of curriculum mapping using the new ClassCurriculumMapping model
    MUCH MORE EFFICIENT - Direct lookup instead of iterating through all exams
    """
    cache_key = f"curriculum_map_v2_{class_code}_{academic_year}"
    cached = cache.get(cache_key)
    if cached:
        logger.debug(f"[SCHEDULE_MATRIX] Using cached curriculum mapping for {class_code}")
        return cached
    
    curriculum_info = {
        'review': None,
        'quarterly': None,
        'combined': 'Not Assigned',
        'primary': None,
        'secondary': None,
        'all_mappings': []
    }
    
    # Use the new ClassCurriculumMapping model - SINGLE efficient query!
    mappings = ClassCurriculumMapping.objects.filter(
        class_code=class_code.upper(),
        academic_year=academic_year,
        is_active=True
    ).select_related(
        'curriculum_level__subprogram__program'
    ).order_by('priority')
    
    # Process mappings by priority
    for mapping in mappings:
        level = mapping.curriculum_level
        if level and level.subprogram:
            mapping_info = {
                'program': level.subprogram.program.name,
                'subprogram': level.subprogram.name,
                'level': level.level_number,
                'display': f"{level.subprogram.program.name} {level.subprogram.name} L{level.level_number}",
                'priority': mapping.priority
            }
            
            curriculum_info['all_mappings'].append(mapping_info)
            
            # Set primary (priority 1) and secondary (priority 2)
            if mapping.priority == 1:
                curriculum_info['primary'] = mapping_info
                curriculum_info['review'] = mapping_info  # For backward compatibility
                curriculum_info['combined'] = mapping_info['display']
            elif mapping.priority == 2:
                curriculum_info['secondary'] = mapping_info
                curriculum_info['quarterly'] = mapping_info  # For backward compatibility
    
    # If no mappings found, keep 'Not Assigned'
    if not mappings:
        logger.info(f"[SCHEDULE_MATRIX] No curriculum mapping found for {class_code} in {academic_year}")
    else:
        logger.info(f"[SCHEDULE_MATRIX] Found {len(mappings)} curriculum mappings for {class_code}")
    
    # Cache for 5 minutes
    cache.set(cache_key, curriculum_info, 300)
    return curriculum_info


# For backward compatibility, import the original function name
get_class_curriculum_mapping = get_class_curriculum_mapping_cached


@login_required
@transaction.atomic
def schedule_matrix_view(request):
    """
    Optimized schedule matrix view with reduced database queries
    ENHANCED: Proper access control for teachers with assigned classes
    """
    start_time = datetime.now()
    
    # ========== COMPREHENSIVE CONSOLE LOGGING ==========
    console_log = {
        "view": "schedule_matrix_view_ENHANCED",
        "module": "RoutineTest - Class Exam Management",
        "user": request.user.username,
        "user_id": request.user.id,
        "is_authenticated": request.user.is_authenticated,
        "is_staff": request.user.is_staff,
        "is_superuser": request.user.is_superuser,
        "method": request.method,
        "timestamp": start_time.isoformat(),
        "request_path": request.path,
        "request_params": dict(request.GET)
    }
    
    print("=" * 80)
    print("[MATRIX_VIEW] ENTRY POINT - Schedule Matrix View")
    print(f"[MATRIX_VIEW] User: {request.user.username} (ID: {request.user.id})")
    print(f"[MATRIX_VIEW] Timestamp: {start_time.isoformat()}")
    print("=" * 80)
    
    logger.info(f"[MATRIX_VIEW_ENTRY] {json.dumps(console_log)}")
    
    # ========== STEP 1: GET TEACHER INSTANCE ==========
    print("\n[MATRIX_VIEW] STEP 1: Checking Teacher Profile...")
    
    try:
        teacher = Teacher.objects.get(user=request.user)
        console_log["teacher_found"] = True
        console_log["teacher_id"] = str(teacher.id)
        console_log["teacher_name"] = teacher.name
        console_log["teacher_is_head"] = teacher.is_head_teacher
        
        print(f"[MATRIX_VIEW] ✅ Teacher profile found: {teacher.name}")
        print(f"[MATRIX_VIEW]    - Teacher ID: {teacher.id}")
        print(f"[MATRIX_VIEW]    - Is Head Teacher: {teacher.is_head_teacher}")
        
    except Teacher.DoesNotExist:
        console_log["teacher_found"] = False
        console_log["error"] = "Teacher profile not found"
        
        print(f"[MATRIX_VIEW] ❌ NO TEACHER PROFILE for user {request.user.username}")
        print(f"[MATRIX_VIEW] Redirecting to index...")
        
        logger.error(f"[MATRIX_VIEW_ERROR] {json.dumps(console_log)}")
        messages.error(request, "Teacher profile not found. Please contact administrator.")
        return redirect('RoutineTest:index')
    
    # ========== STEP 2: CHECK ADMIN/HEAD TEACHER STATUS ==========
    print("\n[MATRIX_VIEW] STEP 2: Checking Admin/Head Teacher Status...")
    
    from primepath_routinetest.views.class_access import is_admin_or_head_teacher
    is_admin, admin_teacher = is_admin_or_head_teacher(request.user)
    
    console_log["is_admin"] = is_admin
    console_log["admin_check_result"] = "ADMIN" if is_admin else "REGULAR_TEACHER"
    
    print(f"[MATRIX_VIEW] Admin check result: {'ADMIN ACCESS' if is_admin else 'REGULAR TEACHER'}")
    
    # ========== STEP 3: DETERMINE CLASS ACCESS ==========
    print("\n[MATRIX_VIEW] STEP 3: Determining Class Access...")
    
    if is_admin:
        # Admin gets ALL classes
        print("[MATRIX_VIEW] 👑 ADMIN MODE - Granting access to ALL classes")
        
        # Get all possible class codes
        choice_class_codes = [choice[0] for choice in TeacherClassAssignment._meta.get_field('class_code').choices]
        
        # Also get any class codes that exist in the database
        db_class_codes = list(TeacherClassAssignment.objects.values_list('class_code', flat=True).distinct())
        db_matrix_codes = list(ExamScheduleMatrix.objects.values_list('class_code', flat=True).distinct())
        
        # Combine and deduplicate
        all_class_codes = sorted(list(set(choice_class_codes + db_class_codes + db_matrix_codes)))
        
        print(f"[MATRIX_VIEW] Found {len(all_class_codes)} total class codes:")
        for code in all_class_codes:
            print(f"[MATRIX_VIEW]    - {code}")
        
        # Create virtual assignments for admin
        assigned_classes = []
        class_choices_dict = dict(TeacherClassAssignment._meta.get_field('class_code').choices)
        
        for class_code in all_class_codes:
            # Create a mock assignment object with proper display name
            class MockAssignment:
                def __init__(self, code):
                    self.class_code = code
                    self.access_level = 'FULL'
                    self.is_virtual = True  # Mark as virtual for debugging
                
                def get_class_code_display(self):
                    return class_choices_dict.get(self.class_code, self.class_code)
            
            mock_assignment = MockAssignment(class_code)
            assigned_classes.append(mock_assignment)
        
        console_log["access_type"] = "ADMIN_FULL_ACCESS"
        console_log["total_classes"] = len(assigned_classes)
        console_log["class_codes"] = all_class_codes
        
        print(f"[MATRIX_VIEW] ✅ Admin has access to {len(assigned_classes)} classes")
        logger.info(f"[MATRIX_VIEW_ADMIN] Admin {request.user.username} granted full access to {len(assigned_classes)} classes")
        
    else:
        # Regular teacher - get their assigned classes
        print("[MATRIX_VIEW] 👩‍🏫 TEACHER MODE - Checking assigned classes...")
        
        assigned_classes = list(TeacherClassAssignment.objects.filter(
            teacher=teacher,
            is_active=True
        ).order_by('class_code'))
        
        console_log["access_type"] = "TEACHER_ASSIGNED_CLASSES"
        console_log["assigned_classes_count"] = len(assigned_classes)
        
        if assigned_classes:
            print(f"[MATRIX_VIEW] ✅ Teacher has {len(assigned_classes)} assigned classes:")
            class_list = []
            for assignment in assigned_classes:
                class_info = {
                    "code": assignment.class_code,
                    "display": assignment.get_class_code_display(),
                    "access_level": assignment.access_level
                }
                class_list.append(class_info)
                print(f"[MATRIX_VIEW]    - {class_info['display']} ({class_info['access_level']})")
            
            console_log["assigned_classes_detail"] = class_list
            
        else:
            print(f"[MATRIX_VIEW] ⚠️ Teacher {teacher.name} has NO assigned classes")
            print("[MATRIX_VIEW] Redirecting to My Classes page...")
            
            console_log["redirect_reason"] = "no_assigned_classes"
            logger.warning(f"[MATRIX_VIEW_REDIRECT] {json.dumps(console_log)}")
            
            messages.warning(request, "You have no assigned classes. Please request access to classes first.")
            return redirect('RoutineTest:my_classes')
    
    print(f"\n[MATRIX_VIEW] STEP 3 COMPLETE - Proceeding with {len(assigned_classes)} classes")
    
    # ========== STEP 4: FETCH AND BUILD MATRIX DATA ==========
    print("\n[MATRIX_VIEW] STEP 4: Building Matrix Data...")
    
    current_year = request.GET.get('year', str(datetime.now().year))
    console_log["current_year"] = current_year
    
    print(f"[MATRIX_VIEW] Academic Year: {current_year}")
    
    # Bulk fetch all matrix cells for this teacher's classes
    class_codes = [a.class_code for a in assigned_classes]
    
    print(f"[MATRIX_VIEW] Fetching matrix cells for {len(class_codes)} classes...")
    
    # Get all cells in one query with proper prefetching
    existing_cells = ExamScheduleMatrix.objects.filter(
        class_code__in=class_codes,
        academic_year=current_year
    ).select_related('created_by').prefetch_related(
        'exams__curriculum_level__subprogram__program'
    )
    
    print(f"[MATRIX_VIEW] Found {existing_cells.count()} existing matrix cells")
    
    # Index cells for quick lookup
    cell_index = {}
    for cell in existing_cells:
        key = f"{cell.class_code}_{cell.time_period_type}_{cell.time_period_value}"
        cell_index[key] = cell
    
    # Prepare cells to create (if any missing)
    cells_to_create = []
    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
              'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    
    # Check for missing cells
    for assignment in assigned_classes:
        class_code = assignment.class_code
        
        # Check monthly cells
        for month in months:
            key = f"{class_code}_MONTHLY_{month}"
            if key not in cell_index:
                cells_to_create.append(ExamScheduleMatrix(
                    class_code=class_code,
                    academic_year=current_year,
                    time_period_type='MONTHLY',
                    time_period_value=month,
                    created_by=teacher,  # Use teacher instance, not user
                    status='PENDING'
                ))
        
        # Check quarterly cells
        for quarter in quarters:
            key = f"{class_code}_QUARTERLY_{quarter}"
            if key not in cell_index:
                cells_to_create.append(ExamScheduleMatrix(
                    class_code=class_code,
                    academic_year=current_year,
                    time_period_type='QUARTERLY',
                    time_period_value=quarter,
                    created_by=teacher,  # Use teacher instance, not user
                    status='PENDING'
                ))
    
    # Bulk create missing cells
    if cells_to_create:
        ExamScheduleMatrix.objects.bulk_create(cells_to_create, ignore_conflicts=True)
        
        # Re-fetch all cells after creation with proper prefetching
        existing_cells = ExamScheduleMatrix.objects.filter(
            class_code__in=class_codes,
            academic_year=current_year
        ).select_related('created_by').prefetch_related(
            'exams__curriculum_level__subprogram__program'
        )
        
        # Re-index
        cell_index = {}
        for cell in existing_cells:
            key = f"{cell.class_code}_{cell.time_period_type}_{cell.time_period_value}"
            cell_index[key] = cell
    
    # Build matrix data efficiently
    monthly_matrix = {}
    quarterly_matrix = {}
    
    for assignment in assigned_classes:
        class_code = assignment.class_code
        
        # Get cached curriculum mapping
        curriculum_info = get_class_curriculum_mapping_cached(class_code, current_year)
        
        # Monthly matrix
        monthly_matrix[class_code] = {
            'display_name': assignment.get_class_code_display(),
            'access_level': assignment.access_level,
            'curriculum_mapping': curriculum_info,
            'cells': {}
        }
        
        for month in months:
            key = f"{class_code}_MONTHLY_{month}"
            cell = cell_index.get(key)
            if cell:
                # Get exam details for display
                exam_details = []
                for exam in cell.exams.all():
                    exam_details.append({
                        'id': str(exam.id),
                        'name': exam.name,
                        'type': exam.exam_type,
                        'curriculum': f"{exam.curriculum_level.subprogram.program.name} {exam.curriculum_level.subprogram.name} L{exam.curriculum_level.level_number}" if exam.curriculum_level and exam.curriculum_level.subprogram else 'N/A'
                    })
                
                monthly_matrix[class_code]['cells'][month] = {
                    'id': str(cell.id),
                    'status': cell.status,
                    'exam_count': cell.exams.count(),  # Prefetched
                    'exams': exam_details,  # Add exam details
                    'color': cell.get_status_color(),
                    'icon': cell.get_status_icon(),
                    'scheduled_date': cell.scheduled_date.isoformat() if cell.scheduled_date else None,
                    'can_edit': cell.can_teacher_edit(teacher)
                }
            else:
                # Add empty cell for consistency
                monthly_matrix[class_code]['cells'][month] = {
                    'id': None,
                    'status': 'empty',
                    'exam_count': 0,
                    'exams': [],
                    'color': '#FFEBEE',
                    'icon': '➖',
                    'scheduled_date': None,
                    'can_edit': True
                }
        
        # Quarterly matrix
        quarterly_matrix[class_code] = {
            'display_name': assignment.get_class_code_display(),
            'access_level': assignment.access_level,
            'curriculum_mapping': curriculum_info,
            'cells': {}
        }
        
        for quarter in quarters:
            key = f"{class_code}_QUARTERLY_{quarter}"
            cell = cell_index.get(key)
            if cell:
                # Get exam details for display
                exam_details = []
                for exam in cell.exams.all():
                    exam_details.append({
                        'id': str(exam.id),
                        'name': exam.name,
                        'type': exam.exam_type,
                        'curriculum': f"{exam.curriculum_level.subprogram.program.name} {exam.curriculum_level.subprogram.name} L{exam.curriculum_level.level_number}" if exam.curriculum_level and exam.curriculum_level.subprogram else 'N/A'
                    })
                
                quarterly_matrix[class_code]['cells'][quarter] = {
                    'id': str(cell.id),
                    'status': cell.status,
                    'exam_count': cell.exams.count(),  # Prefetched
                    'exams': exam_details,  # Add exam details
                    'color': cell.get_status_color(),
                    'icon': cell.get_status_icon(),
                    'scheduled_date': cell.scheduled_date.isoformat() if cell.scheduled_date else None,
                    'can_edit': cell.can_teacher_edit(teacher)
                }
            else:
                # Add empty cell for consistency
                quarterly_matrix[class_code]['cells'][quarter] = {
                    'id': None,
                    'status': 'empty',
                    'exam_count': 0,
                    'exams': [],
                    'color': '#FFEBEE',
                    'icon': '➖',
                    'scheduled_date': None,
                    'can_edit': True
                }
    
    # Static data
    available_years = ['2025', '2026', '2027', '2028', '2029', '2030']
    month_names = {
        'JAN': 'January', 'FEB': 'February', 'MAR': 'March',
        'APR': 'April', 'MAY': 'May', 'JUN': 'June',
        'JUL': 'July', 'AUG': 'August', 'SEP': 'September',
        'OCT': 'October', 'NOV': 'November', 'DEC': 'December'
    }
    quarter_names = {
        'Q1': 'Q1 (Jan-Mar)', 'Q2': 'Q2 (Apr-Jun)',
        'Q3': 'Q3 (Jul-Sep)', 'Q4': 'Q4 (Oct-Dec)'
    }
    
    # ========== STEP 5: PREPARE CONTEXT AND RENDER ==========
    print("\n[MATRIX_VIEW] STEP 5: Preparing Template Context...")
    
    context = {
        'teacher': teacher,
        'current_year': current_year,
        'available_years': available_years,
        'monthly_matrix': monthly_matrix,
        'quarterly_matrix': quarterly_matrix,
        'months': months,
        'quarters': quarters,
        'month_names': month_names,
        'quarter_names': quarter_names,
        'assigned_classes': assigned_classes,
        'is_admin': is_admin,  # Add admin flag for template
        'total_classes': len(assigned_classes),
        'user_type': 'Admin' if is_admin else 'Teacher',
    }
    
    # Summarize matrix data for logging
    matrix_summary = {
        "monthly_classes": len(monthly_matrix),
        "quarterly_classes": len(quarterly_matrix),
        "total_cells_created": cells_to_create if 'cells_to_create' in locals() else 0,
        "is_admin": is_admin,
        "user_type": context['user_type']
    }
    
    console_log["matrix_summary"] = matrix_summary
    
    print(f"[MATRIX_VIEW] Context prepared:")
    print(f"[MATRIX_VIEW]    - User Type: {context['user_type']}")
    print(f"[MATRIX_VIEW]    - Total Classes: {context['total_classes']}")
    print(f"[MATRIX_VIEW]    - Monthly Matrix Classes: {matrix_summary['monthly_classes']}")
    print(f"[MATRIX_VIEW]    - Quarterly Matrix Classes: {matrix_summary['quarterly_classes']}")
    
    # Log performance
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    console_log["duration_seconds"] = duration
    console_log["performance_status"] = "OK" if duration < 2 else "SLOW"
    
    print(f"\n[MATRIX_VIEW] PERFORMANCE: View rendered in {duration:.2f} seconds")
    
    if duration > 2:
        print(f"[MATRIX_VIEW] ⚠️ Performance warning: {duration:.2f}s exceeds 2s threshold")
        logger.warning(f"[MATRIX_VIEW_PERFORMANCE] Schedule matrix took {duration:.2f}s - consider caching")
    else:
        print(f"[MATRIX_VIEW] ✅ Performance OK: {duration:.2f}s")
    
    # Final log entry
    console_log["status"] = "SUCCESS"
    console_log["template"] = "primepath_routinetest/schedule_matrix.html"
    
    logger.info(f"[MATRIX_VIEW_SUCCESS] {json.dumps(console_log)}")
    
    print("\n" + "=" * 80)
    print("[MATRIX_VIEW] SUCCESS - Rendering template")
    print(f"[MATRIX_VIEW] Template: primepath_routinetest/schedule_matrix.html")
    print(f"[MATRIX_VIEW] User: {request.user.username}")
    print(f"[MATRIX_VIEW] Classes: {len(assigned_classes)}")
    print("=" * 80 + "\n")
    
    return render(request, 'primepath_routinetest/schedule_matrix.html', context)


# Import all other views from original schedule_matrix module
from .schedule_matrix import (
    matrix_cell_detail,
    bulk_assign_exams,
    get_matrix_data,
    clone_schedule,
    matrix_test_view
)
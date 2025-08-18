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
    """
    start_time = datetime.now()
    
    console_log = {
        "view": "exam_assignments_view_optimized",
        "module": "RoutineTest - Exam Management",
        "user": request.user.username,
        "method": request.method,
        "timestamp": start_time.isoformat()
    }
    logger.info(f"[EXAM_ASSIGNMENTS_OPTIMIZED] {json.dumps(console_log)}")
    
    # Get teacher instance
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        messages.error(request, "Teacher profile not found")
        return redirect('RoutineTest:index')
    
    # Check if user is admin/head teacher
    from primepath_routinetest.views.class_access import is_admin_or_head_teacher
    is_admin, admin_teacher = is_admin_or_head_teacher(request.user)
    
    if is_admin:
        # Admin gets ALL classes
        logger.info(f"[EXAM_ASSIGNMENTS] Admin {request.user.username} accessing matrix with full access")
        
        # Get all class codes from both model choices AND database
        choice_class_codes = [choice[0] for choice in TeacherClassAssignment._meta.get_field('class_code').choices]
        
        # Also get any class codes that exist in the database but not in choices
        db_class_codes = list(TeacherClassAssignment.objects.values_list('class_code', flat=True).distinct())
        db_class_codes.extend(list(ExamScheduleMatrix.objects.values_list('class_code', flat=True).distinct()))
        
        # Combine and deduplicate
        all_class_codes = sorted(list(set(choice_class_codes + db_class_codes)))
        
        # Create virtual assignments for admin
        assigned_classes = []
        class_choices_dict = dict(TeacherClassAssignment._meta.get_field('class_code').choices)
        
        for class_code in all_class_codes:
            # Create a mock assignment object with proper display name
            class MockAssignment:
                def __init__(self, code):
                    self.class_code = code
                    self.access_level = 'FULL'
                
                def get_class_code_display(self):
                    return class_choices_dict.get(self.class_code, self.class_code)
            
            mock_assignment = MockAssignment(class_code)
            assigned_classes.append(mock_assignment)
            
        logger.info(f"[EXAM_ASSIGNMENTS] Admin has access to {len(assigned_classes)} classes")
    else:
        # Regular teacher - get their assigned classes
        assigned_classes = list(TeacherClassAssignment.objects.filter(
            teacher=teacher,
            is_active=True
        ).order_by('class_code'))
        
        if not assigned_classes:
            messages.warning(request, "You have no assigned classes")
            return redirect('RoutineTest:my_classes')
    
    current_year = request.GET.get('year', str(datetime.now().year))
    
    # Bulk fetch all matrix cells for this teacher's classes
    class_codes = [a.class_code for a in assigned_classes]
    
    # Get all cells in one query with proper prefetching
    existing_cells = ExamScheduleMatrix.objects.filter(
        class_code__in=class_codes,
        academic_year=current_year
    ).select_related('created_by').prefetch_related(
        'exams__curriculum_level__subprogram__program'
    )
    
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
    }
    
    # Log performance
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logger.info(f"[EXAM_ASSIGNMENTS_OPTIMIZED] Rendered in {duration:.2f} seconds")
    
    if duration > 2:
        logger.warning(f"[PERFORMANCE] Schedule matrix took {duration:.2f}s - consider caching")
    
    return render(request, 'primepath_routinetest/schedule_matrix.html', context)


# Import all other views from original schedule_matrix module
from .schedule_matrix import (
    matrix_cell_detail,
    bulk_assign_exams,
    get_matrix_data,
    clone_schedule,
    matrix_test_view
)
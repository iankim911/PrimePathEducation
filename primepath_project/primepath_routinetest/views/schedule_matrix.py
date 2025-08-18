"""
Schedule Matrix Views
Manages the Class × Timeslot matrix interface for exam scheduling
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import PermissionDenied
import json
import logging
from datetime import datetime

from primepath_routinetest.models import (
    Exam, ExamScheduleMatrix, TeacherClassAssignment,
    ClassExamSchedule, ClassCurriculumMapping
)
from core.models import Teacher
from django.db.models import Q, Prefetch

logger = logging.getLogger(__name__)


def get_class_curriculum_mapping(class_code, academic_year):
    """
    Get the curriculum (Program × SubProgram × Level) mapping for a class.
    First checks ClassCurriculumMapping table, then falls back to recent exam data.
    """
    curriculum_info = {
        'review': None,
        'quarterly': None,
        'combined': None
    }
    
    # First check if there's a direct curriculum mapping for this class
    primary_mapping = ClassCurriculumMapping.get_primary_curriculum(class_code, academic_year)
    
    if primary_mapping:
        # Use the mapped curriculum
        level = primary_mapping
        formatted_display = f"{level.subprogram.program.name} × {level.subprogram.name} × Level {level.level_number}"
        curriculum_info['review'] = {
            'program': level.subprogram.program.name,
            'subprogram': level.subprogram.name,
            'level': level.level_number,
            'display': formatted_display
        }
        curriculum_info['quarterly'] = curriculum_info['review']
        curriculum_info['combined'] = formatted_display
    else:
        # Fall back to checking recent exams for curriculum info
        # Get most recent Review exam for this class
        review_exams = Exam.objects.filter(
            exam_type='REVIEW',
            academic_year=academic_year,
            curriculum_level__isnull=False
        ).select_related(
            'curriculum_level__subprogram__program'
        ).order_by('-created_at')
        
        # Find the exam that includes this class
        review_exam = None
        for exam in review_exams:
            if exam.class_codes and class_code in exam.class_codes:
                review_exam = exam
                break
        
        if review_exam and review_exam.curriculum_level:
            level = review_exam.curriculum_level
            curriculum_info['review'] = {
                'program': level.subprogram.program.name if level.subprogram else '',
                'subprogram': level.subprogram.name if level.subprogram else '',
                'level': level.level_number,
                'display': f"{level.subprogram.program.name} × {level.subprogram.name} × Level {level.level_number}" if level.subprogram else ''
            }
        
        # Get most recent Quarterly exam for this class
        quarterly_exams = Exam.objects.filter(
            exam_type='QUARTERLY',
            academic_year=academic_year,
            curriculum_level__isnull=False
        ).select_related(
            'curriculum_level__subprogram__program'
        ).order_by('-created_at')
        
        # Find the exam that includes this class
        quarterly_exam = None
        for exam in quarterly_exams:
            if exam.class_codes and class_code in exam.class_codes:
                quarterly_exam = exam
                break
        
        if quarterly_exam and quarterly_exam.curriculum_level:
            level = quarterly_exam.curriculum_level
            curriculum_info['quarterly'] = {
                'program': level.subprogram.program.name if level.subprogram else '',
                'subprogram': level.subprogram.name if level.subprogram else '',
                'level': level.level_number,
                'display': f"{level.subprogram.program.name} × {level.subprogram.name} × Level {level.level_number}" if level.subprogram else ''
            }
        
        # Combined display (prefer Review if available, otherwise Quarterly)
        if curriculum_info['review']:
            curriculum_info['combined'] = curriculum_info['review']['display']
        elif curriculum_info['quarterly']:
            curriculum_info['combined'] = curriculum_info['quarterly']['display']
        else:
            curriculum_info['combined'] = 'Unassigned'
    
    return curriculum_info


@login_required
def schedule_matrix_view(request):
    """
    Main view for displaying the Class × Timeslot matrix.
    Shows both monthly and quarterly matrices.
    """
    console_log = {
        "view": "exam_assignments_view",  # Updated name
        "module": "RoutineTest - Exam Management",
        "user": request.user.username,
        "method": request.method,
        "purpose": "Display exam assignment matrix for classes and time periods",
        "timestamp": datetime.now().isoformat()
    }
    logger.info(f"[EXAM_ASSIGNMENTS] {json.dumps(console_log)}")
    print(f"\n{'='*60}")
    print(f"[EXAM_ASSIGNMENTS] View accessed")
    print(f"  User: {request.user.username}")
    print(f"  Purpose: Managing exam assignments across classes")
    print(f"{'='*60}\n")
    
    # Get teacher instance
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        messages.error(request, "Teacher profile not found")
        return redirect('RoutineTest:index')
    
    # Get teacher's assigned classes
    assigned_classes = TeacherClassAssignment.objects.filter(
        teacher=teacher,
        is_active=True
    ).order_by('class_code')
    
    if not assigned_classes:
        messages.warning(request, "You have no assigned classes")
        return redirect('RoutineTest:my_classes')
    
    # Get current academic year (default to current year)
    current_year = request.GET.get('year', str(datetime.now().year))
    
    # Build matrix data for monthly view
    monthly_matrix = {}
    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
              'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    
    for assignment in assigned_classes:
        class_code = assignment.class_code
        # Get curriculum mappings for this class
        curriculum_info = get_class_curriculum_mapping(class_code, current_year)
        
        # DEBUG: Log curriculum data being passed to template
        print(f"\n[CURRICULUM_DEBUG] Monthly Matrix - Class: {class_code}")
        print(f"[CURRICULUM_DEBUG] Curriculum Info: {curriculum_info}")
        print(f"[CURRICULUM_DEBUG] Combined: {curriculum_info.get('combined', 'None')}")
        
        monthly_matrix[class_code] = {
            'display_name': assignment.get_class_code_display(),
            'access_level': assignment.access_level,
            'curriculum_mapping': curriculum_info,
            'cells': {}
        }
        
        for month in months:
            # Get or create matrix cell
            matrix_cell, created = ExamScheduleMatrix.get_or_create_cell(
                class_code=class_code,
                academic_year=current_year,
                time_period_type='MONTHLY',
                time_period_value=month,
                user=request.user
            )
            
            monthly_matrix[class_code]['cells'][month] = {
                'id': str(matrix_cell.id),
                'status': matrix_cell.status,
                'exam_count': matrix_cell.get_exam_count(),
                'color': matrix_cell.get_status_color(),
                'icon': matrix_cell.get_status_icon(),
                'scheduled_date': matrix_cell.scheduled_date.isoformat() if matrix_cell.scheduled_date else None,
                'can_edit': matrix_cell.can_teacher_edit(teacher)
            }
    
    # Build matrix data for quarterly view
    quarterly_matrix = {}
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    
    for assignment in assigned_classes:
        class_code = assignment.class_code
        # Get curriculum mappings for this class
        curriculum_info = get_class_curriculum_mapping(class_code, current_year)
        
        quarterly_matrix[class_code] = {
            'display_name': assignment.get_class_code_display(),
            'access_level': assignment.access_level,
            'curriculum_mapping': curriculum_info,
            'cells': {}
        }
        
        for quarter in quarters:
            # Get or create matrix cell
            matrix_cell, created = ExamScheduleMatrix.get_or_create_cell(
                class_code=class_code,
                academic_year=current_year,
                time_period_type='QUARTERLY',
                time_period_value=quarter,
                user=request.user
            )
            
            quarterly_matrix[class_code]['cells'][quarter] = {
                'id': str(matrix_cell.id),
                'status': matrix_cell.status,
                'exam_count': matrix_cell.get_exam_count(),
                'color': matrix_cell.get_status_color(),
                'icon': matrix_cell.get_status_icon(),
                'scheduled_date': matrix_cell.scheduled_date.isoformat() if matrix_cell.scheduled_date else None,
                'can_edit': matrix_cell.can_teacher_edit(teacher)
            }
    
    # Get available years for the dropdown
    available_years = ['2025', '2026', '2027', '2028', '2029', '2030']
    
    # Get month names for display
    month_names = {
        'JAN': 'January', 'FEB': 'February', 'MAR': 'March',
        'APR': 'April', 'MAY': 'May', 'JUN': 'June',
        'JUL': 'July', 'AUG': 'August', 'SEP': 'September',
        'OCT': 'October', 'NOV': 'November', 'DEC': 'December'
    }
    
    quarter_names = {
        'Q1': 'Q1 (Jan-Mar)',
        'Q2': 'Q2 (Apr-Jun)',
        'Q3': 'Q3 (Jul-Sep)',
        'Q4': 'Q4 (Oct-Dec)'
    }
    
    # DEBUG: Log monthly matrix data being passed to template
    print(f"\n[TEMPLATE_DEBUG] Final monthly_matrix keys: {list(monthly_matrix.keys())}")
    for class_code, class_data in monthly_matrix.items():
        curriculum = class_data.get('curriculum_mapping', {})
        print(f"[TEMPLATE_DEBUG] {class_code}: curriculum_mapping = {curriculum}")
        print(f"[TEMPLATE_DEBUG] {class_code}: combined = {curriculum.get('combined', 'NOT_SET')}")
    
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
    
    return render(request, 'primepath_routinetest/schedule_matrix.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def matrix_cell_detail(request, matrix_id):
    """
    View/Edit details of a specific matrix cell.
    Shows assigned exams and allows management operations.
    """
    console_log = {
        "view": "matrix_cell_detail",
        "matrix_id": str(matrix_id),  # Convert UUID to string for JSON serialization
        "user": request.user.username,
        "method": request.method
    }
    logger.info(f"[MATRIX_CELL_DETAIL] {json.dumps(console_log)}")
    print(f"[MATRIX_CELL_DETAIL] {json.dumps(console_log)}")
    
    # Get teacher and matrix cell
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        if request.method == 'POST':
            return JsonResponse({'error': 'Teacher profile not found'}, status=403)
        messages.error(request, "Teacher profile not found")
        return redirect('RoutineTest:schedule_matrix')
    
    matrix_cell = get_object_or_404(ExamScheduleMatrix, id=matrix_id)
    
    # Check permissions
    if not matrix_cell.can_teacher_edit(teacher):
        if request.method == 'POST':
            return JsonResponse({'error': 'Permission denied'}, status=403)
        raise PermissionDenied("You don't have permission to edit this schedule")
    
    if request.method == 'POST':
        # Handle various operations via AJAX
        action = request.POST.get('action')
        
        if action == 'add_exam':
            exam_id = request.POST.get('exam_id')
            try:
                exam = Exam.objects.get(id=exam_id)
                matrix_cell.add_exam(exam, request.user)
                return JsonResponse({
                    'success': True,
                    'message': f'Exam "{exam.name}" added successfully',
                    'exam_count': matrix_cell.get_exam_count()
                })
            except Exam.DoesNotExist:
                return JsonResponse({'error': 'Exam not found'}, status=404)
        
        elif action == 'remove_exam':
            exam_id = request.POST.get('exam_id')
            try:
                exam = Exam.objects.get(id=exam_id)
                matrix_cell.remove_exam(exam, request.user)
                return JsonResponse({
                    'success': True,
                    'message': f'Exam "{exam.name}" removed successfully',
                    'exam_count': matrix_cell.get_exam_count()
                })
            except Exam.DoesNotExist:
                return JsonResponse({'error': 'Exam not found'}, status=404)
        
        elif action == 'update_schedule':
            scheduled_date = request.POST.get('scheduled_date')
            scheduled_start_time = request.POST.get('scheduled_start_time')
            scheduled_end_time = request.POST.get('scheduled_end_time')
            
            # Parse dates and times
            if scheduled_date:
                scheduled_date = datetime.strptime(scheduled_date, '%Y-%m-%d').date()
            if scheduled_start_time:
                scheduled_start_time = datetime.strptime(scheduled_start_time, '%H:%M').time()
            if scheduled_end_time:
                scheduled_end_time = datetime.strptime(scheduled_end_time, '%H:%M').time()
            
            matrix_cell.update_schedule(
                date=scheduled_date,
                start_time=scheduled_start_time,
                end_time=scheduled_end_time,
                user=request.user
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Schedule updated successfully'
            })
        
        elif action == 'share_with_class':
            target_class = request.POST.get('target_class')
            shared_matrix = matrix_cell.share_with_class(target_class, request.user)
            
            if shared_matrix:
                return JsonResponse({
                    'success': True,
                    'message': f'Schedule shared with {shared_matrix.get_class_display()}'
                })
            else:
                return JsonResponse({
                    'error': 'Schedule already shared with this class'
                }, status=400)
        
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)
    
    # GET request - show detail view
    # Get available exams for adding
    available_exams = Exam.objects.filter(
        is_active=True,
        exam_type='REVIEW' if matrix_cell.time_period_type == 'MONTHLY' else 'QUARTERLY'
    ).exclude(
        id__in=matrix_cell.exams.values_list('id', flat=True)
    )
    
    # Get other classes for sharing
    other_classes = TeacherClassAssignment.objects.filter(
        teacher=teacher,
        is_active=True
    ).exclude(class_code=matrix_cell.class_code)
    
    # Get completion stats
    completion_stats = matrix_cell.get_completion_stats()
    
    # Get detailed exam information for modular display
    detailed_exams = matrix_cell.get_detailed_exam_list()
    
    context = {
        'matrix_cell': matrix_cell,
        'assigned_exams': matrix_cell.get_exam_list(),
        'detailed_exams': detailed_exams,  # Enhanced exam data for modular cards
        'available_exams': available_exams,
        'other_classes': other_classes,
        'completion_stats': completion_stats,
        'can_edit': matrix_cell.can_teacher_edit(teacher),
        'cell_info': {
            'id': str(matrix_cell.id),
            'class_code': matrix_cell.class_code,
            'class_display': matrix_cell.get_class_display(),
            'period': matrix_cell.time_period_value,
            'period_display': matrix_cell.get_time_period_display(),
            'academic_year': matrix_cell.academic_year,
            'status': matrix_cell.status,
            'exam_count': matrix_cell.get_exam_count()
        }
    }
    
    return render(request, 'primepath_routinetest/matrix_cell_detail_modular.html', context)


@login_required
@require_http_methods(["POST"])
def bulk_assign_exams(request):
    """
    Bulk assign exams to multiple matrix cells.
    """
    console_log = {
        "view": "bulk_assign_exams",
        "user": request.user.username,
        "method": request.method
    }
    logger.info(f"[BULK_ASSIGN] {json.dumps(console_log)}")
    print(f"[BULK_ASSIGN] {json.dumps(console_log)}")
    
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        return JsonResponse({'error': 'Teacher profile not found'}, status=403)
    
    # Parse request data
    data = json.loads(request.body)
    exam_ids = data.get('exam_ids', [])
    cell_ids = data.get('cell_ids', [])
    
    if not exam_ids or not cell_ids:
        return JsonResponse({'error': 'No exams or cells selected'}, status=400)
    
    success_count = 0
    error_count = 0
    errors = []
    
    with transaction.atomic():
        for cell_id in cell_ids:
            try:
                matrix_cell = ExamScheduleMatrix.objects.get(id=cell_id)
                
                # Check permission
                if not matrix_cell.can_teacher_edit(teacher):
                    errors.append(f"No permission for {matrix_cell.get_class_display()}")
                    error_count += 1
                    continue
                
                # Add each exam
                for exam_id in exam_ids:
                    try:
                        exam = Exam.objects.get(id=exam_id)
                        matrix_cell.add_exam(exam, request.user)
                        success_count += 1
                    except Exam.DoesNotExist:
                        errors.append(f"Exam {exam_id} not found")
                        error_count += 1
                        
            except ExamScheduleMatrix.DoesNotExist:
                errors.append(f"Matrix cell {cell_id} not found")
                error_count += 1
    
    response_data = {
        'success': success_count > 0,
        'success_count': success_count,
        'error_count': error_count,
        'message': f'Successfully assigned {success_count} exams'
    }
    
    if errors:
        response_data['errors'] = errors[:5]  # Limit error messages
    
    return JsonResponse(response_data)


@login_required
@require_http_methods(["GET"])
def get_matrix_data(request):
    """
    API endpoint to get matrix data for a specific class and year.
    Used for AJAX updates without full page reload.
    """
    class_code = request.GET.get('class_code')
    academic_year = request.GET.get('year', str(datetime.now().year))
    time_period_type = request.GET.get('type', 'MONTHLY')
    
    if not class_code:
        return JsonResponse({'error': 'Class code required'}, status=400)
    
    try:
        teacher = Teacher.objects.get(user=request.user)
        
        # Check permission
        assignment = TeacherClassAssignment.objects.filter(
            teacher=teacher,
            class_code=class_code,
            is_active=True
        ).first()
        
        if not assignment:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # Get matrix cells
        matrix_cells = ExamScheduleMatrix.objects.filter(
            class_code=class_code,
            academic_year=academic_year,
            time_period_type=time_period_type
        ).prefetch_related('exams')
        
        # Build response data
        matrix_data = {}
        for cell in matrix_cells:
            matrix_data[cell.time_period_value] = {
                'id': str(cell.id),
                'status': cell.status,
                'exam_count': cell.get_exam_count(),
                'exams': cell.get_exam_list(),
                'color': cell.get_status_color(),
                'icon': cell.get_status_icon(),
                'scheduled_date': cell.scheduled_date.isoformat() if cell.scheduled_date else None,
                'completion_stats': cell.get_completion_stats()
            }
        
        return JsonResponse({
            'success': True,
            'matrix_data': matrix_data,
            'class_code': class_code,
            'class_name': assignment.get_class_code_display(),
            'academic_year': academic_year,
            'time_period_type': time_period_type
        })
        
    except Teacher.DoesNotExist:
        return JsonResponse({'error': 'Teacher profile not found'}, status=403)
    except Exception as e:
        logger.error(f"[MATRIX_DATA_ERROR] {str(e)}")
        return JsonResponse({'error': 'An error occurred'}, status=500)


@login_required
@require_http_methods(["POST"])
def clone_schedule(request):
    """
    Clone a schedule from one time period to another.
    """
    console_log = {
        "view": "clone_schedule",
        "user": request.user.username,
        "method": request.method
    }
    logger.info(f"[CLONE_SCHEDULE] {json.dumps(console_log)}")
    print(f"[CLONE_SCHEDULE] {json.dumps(console_log)}")
    
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        return JsonResponse({'error': 'Teacher profile not found'}, status=403)
    
    # Parse request data
    data = json.loads(request.body)
    source_cell_id = data.get('source_cell_id')
    target_cells = data.get('target_cells', [])
    
    if not source_cell_id or not target_cells:
        return JsonResponse({'error': 'Source and target cells required'}, status=400)
    
    try:
        source_cell = ExamScheduleMatrix.objects.get(id=source_cell_id)
        
        # Check permission
        if not source_cell.can_teacher_edit(teacher):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        success_count = 0
        
        with transaction.atomic():
            for target_info in target_cells:
                target_cell = ExamScheduleMatrix.get_or_create_cell(
                    class_code=target_info['class_code'],
                    academic_year=target_info['year'],
                    time_period_type=target_info['type'],
                    time_period_value=target_info['period'],
                    user=request.user
                )[0]
                
                # Clone exams
                for exam in source_cell.exams.all():
                    target_cell.add_exam(exam, request.user)
                
                # Clone schedule details
                target_cell.scheduled_date = source_cell.scheduled_date
                target_cell.scheduled_start_time = source_cell.scheduled_start_time
                target_cell.scheduled_end_time = source_cell.scheduled_end_time
                target_cell.save()
                
                success_count += 1
        
        return JsonResponse({
            'success': True,
            'message': f'Schedule cloned to {success_count} cells'
        })
        
    except ExamScheduleMatrix.DoesNotExist:
        return JsonResponse({'error': 'Source cell not found'}, status=404)
    except Exception as e:
        logger.error(f"[CLONE_SCHEDULE_ERROR] {str(e)}")
        return JsonResponse({'error': 'An error occurred'}, status=500)


@login_required
def matrix_test_view(request):
    """
    Simple test view to verify matrix rendering functionality.
    Used for debugging display issues.
    """
    console_log = {
        "view": "matrix_test_view",
        "user": request.user.username,
        "method": request.method,
        "timestamp": datetime.now().isoformat()
    }
    logger.info(f"[MATRIX_TEST] {json.dumps(console_log)}")
    print(f"[MATRIX_TEST] {json.dumps(console_log)}")
    
    # Get teacher instance
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        messages.error(request, "Teacher profile not found")
        return redirect('RoutineTest:index')
    
    # Get teacher's assigned classes (limited for testing)
    assigned_classes = TeacherClassAssignment.objects.filter(
        teacher=teacher,
        is_active=True
    ).order_by('class_code')[:3]  # Limit to 3 classes for testing
    
    # Get current academic year
    current_year = str(datetime.now().year)
    
    # Build minimal matrix data for testing
    monthly_matrix = {}
    months = ['JAN', 'FEB', 'MAR']  # Limited for testing
    
    for assignment in assigned_classes:
        class_code = assignment.class_code
        # Get curriculum mappings for this class
        curriculum_info = get_class_curriculum_mapping(class_code, current_year)
        
        monthly_matrix[class_code] = {
            'display_name': assignment.get_class_code_display(),
            'access_level': assignment.access_level,
            'curriculum_mapping': curriculum_info,
            'cells': {}
        }
        
        for month in months:
            # Get or create matrix cell
            matrix_cell, created = ExamScheduleMatrix.get_or_create_cell(
                class_code=class_code,
                academic_year=current_year,
                time_period_type='MONTHLY',
                time_period_value=month,
                user=request.user
            )
            
            monthly_matrix[class_code]['cells'][month] = {
                'id': str(matrix_cell.id),
                'status': matrix_cell.status,
                'exam_count': matrix_cell.get_exam_count(),
                'color': matrix_cell.get_status_color(),
                'icon': matrix_cell.get_status_icon(),
                'scheduled_date': matrix_cell.scheduled_date.isoformat() if matrix_cell.scheduled_date else None,
                'can_edit': matrix_cell.can_teacher_edit(teacher)
            }
    
    # Month names for display
    month_names = {
        'JAN': 'January', 'FEB': 'February', 'MAR': 'March'
    }
    
    context = {
        'teacher': teacher,
        'current_year': current_year,
        'monthly_matrix': monthly_matrix,
        'months': months,
        'month_names': month_names,
        'assigned_classes': assigned_classes,
    }
    
    return render(request, 'primepath_routinetest/matrix_test.html', context)
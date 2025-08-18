"""
Curriculum Mapping Views
Admin-only interface for mapping class codes to curriculum levels
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.db.models import Q, Count, Prefetch
from django.core.exceptions import PermissionDenied
from django.utils import timezone
import json
import logging
from datetime import datetime

from primepath_routinetest.models import (
    ClassCurriculumMapping, TeacherClassAssignment
)
from core.models import Teacher, CurriculumLevel, Program, SubProgram

logger = logging.getLogger(__name__)


def is_admin_teacher(user):
    """Check if user is an admin/head teacher or in Admin mode"""
    # First check if user is in Admin mode
    if hasattr(user, 'session') and user.session.get('view_mode') == 'Admin':
        return user.is_staff
    
    # Otherwise check traditional head teacher status
    try:
        teacher = Teacher.objects.get(user=user)
        return teacher.is_head_teacher
    except Teacher.DoesNotExist:
        return False


@login_required
def curriculum_mapping_view(request):
    """
    Main view for curriculum mapping interface
    Admin-only: Maps class codes to curriculum levels
    """
    # Check if user is in Admin mode or is a head teacher
    view_mode = request.session.get('view_mode', 'Teacher')
    is_admin_mode = view_mode == 'Admin' and request.user.is_staff
    
    # Also allow traditional head teachers
    is_head_teacher = False
    try:
        teacher = Teacher.objects.get(user=request.user)
        is_head_teacher = teacher.is_head_teacher
    except Teacher.DoesNotExist:
        pass
    
    # Deny access if neither condition is met
    if not (is_admin_mode or is_head_teacher):
        messages.error(request, 'Access denied. Admin mode or head teacher privileges required.')
        return redirect('RoutineTest:index')
    
    start_time = datetime.now()
    
    console_log = {
        "view": "curriculum_mapping_view",
        "module": "RoutineTest - Curriculum Mapping",
        "user": request.user.username,
        "method": request.method,
        "timestamp": start_time.isoformat(),
        "is_admin": True
    }
    logger.info(f"[CURRICULUM_MAPPING_VIEW] {json.dumps(console_log)}")
    print(f"\n{'='*60}")
    print(f"[CURRICULUM_MAPPING] Admin accessing curriculum mapping")
    print(f"  User: {request.user.username}")
    print(f"  Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Get current academic year
    current_year = request.GET.get('year', str(timezone.now().year))
    
    # Get all unique class codes from TeacherClassAssignment
    all_class_codes = TeacherClassAssignment.objects.values_list(
        'class_code', flat=True
    ).distinct().order_by('class_code')
    
    # Convert to list and ensure uppercase
    class_codes = [code.upper() for code in all_class_codes]
    
    # Get existing mappings for current year
    existing_mappings = ClassCurriculumMapping.objects.filter(
        academic_year=current_year,
        is_active=True
    ).select_related(
        'curriculum_level__subprogram__program'
    ).order_by('class_code', 'priority')
    
    # Group mappings by class code
    mappings_by_class = {}
    for mapping in existing_mappings:
        if mapping.class_code not in mappings_by_class:
            mappings_by_class[mapping.class_code] = []
        mappings_by_class[mapping.class_code].append(mapping)
    
    # Build display data
    class_mapping_data = []
    for class_code in class_codes:
        mappings = mappings_by_class.get(class_code, [])
        
        class_data = {
            'class_code': class_code,
            'mappings': [],
            'has_mappings': len(mappings) > 0,
            'primary_curriculum': None
        }
        
        for mapping in mappings:
            mapping_info = {
                'id': str(mapping.id),
                'curriculum_level': mapping.curriculum_level,
                'priority': mapping.priority,
                'display_name': mapping.curriculum_level.display_name,
                'program': mapping.curriculum_level.subprogram.program.name,
                'subprogram': mapping.curriculum_level.subprogram.name,
                'level': mapping.curriculum_level.level_number
            }
            class_data['mappings'].append(mapping_info)
            
            if mapping.priority == 1:
                class_data['primary_curriculum'] = mapping_info
        
        class_mapping_data.append(class_data)
    
    # Get all curriculum levels for selection
    curriculum_levels = CurriculumLevel.objects.select_related(
        'subprogram__program'
    ).order_by(
        'subprogram__program__name',
        'subprogram__name',
        'level_number'
    )
    
    # Group curriculum by program for organized display
    curriculum_by_program = {}
    for level in curriculum_levels:
        program_name = level.subprogram.program.name
        if program_name not in curriculum_by_program:
            curriculum_by_program[program_name] = {
                'program': level.subprogram.program,
                'subprograms': {}
            }
        
        subprogram_name = level.subprogram.name
        if subprogram_name not in curriculum_by_program[program_name]['subprograms']:
            curriculum_by_program[program_name]['subprograms'][subprogram_name] = {
                'subprogram': level.subprogram,
                'levels': []
            }
        
        curriculum_by_program[program_name]['subprograms'][subprogram_name]['levels'].append(level)
    
    # Get available years
    available_years = [str(year) for year in range(2025, 2031)]
    
    # Statistics
    stats = {
        'total_classes': len(class_codes),
        'mapped_classes': len(mappings_by_class),
        'unmapped_classes': len(class_codes) - len(mappings_by_class),
        'total_mappings': existing_mappings.count(),
        'programs_count': Program.objects.count(),
        'curriculum_levels_count': curriculum_levels.count()
    }
    
    context = {
        'current_year': current_year,
        'available_years': available_years,
        'class_mapping_data': class_mapping_data,
        'curriculum_by_program': curriculum_by_program,
        'stats': stats,
        'is_admin': True
    }
    
    # Log performance
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logger.info(f"[CURRICULUM_MAPPING_VIEW] Rendered in {duration:.2f} seconds")
    
    return render(request, 'primepath_routinetest/curriculum_mapping.html', context)


@login_required
@user_passes_test(is_admin_teacher)
@require_http_methods(["POST"])
def add_curriculum_mapping(request):
    """
    AJAX endpoint to add a curriculum mapping
    """
    console_log = {
        "view": "add_curriculum_mapping",
        "user": request.user.username,
        "method": request.method
    }
    logger.info(f"[ADD_CURRICULUM_MAPPING] {json.dumps(console_log)}")
    
    try:
        data = json.loads(request.body)
        class_code = data.get('class_code')
        curriculum_level_id = data.get('curriculum_level_id')
        academic_year = data.get('academic_year', str(timezone.now().year))
        priority = data.get('priority', 1)
        notes = data.get('notes', '')
        
        if not class_code or not curriculum_level_id:
            return JsonResponse({
                'success': False,
                'error': 'Class code and curriculum level are required'
            }, status=400)
        
        # Check if mapping already exists
        existing = ClassCurriculumMapping.objects.filter(
            class_code=class_code.upper(),
            curriculum_level_id=curriculum_level_id,
            academic_year=academic_year
        ).first()
        
        if existing:
            if not existing.is_active:
                # Reactivate if inactive
                existing.is_active = True
                existing.modified_by = request.user
                existing.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Mapping reactivated',
                    'mapping_id': str(existing.id)
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'This mapping already exists'
                }, status=400)
        
        # Create new mapping
        mapping = ClassCurriculumMapping.objects.create(
            class_code=class_code.upper(),
            curriculum_level_id=curriculum_level_id,
            academic_year=academic_year,
            priority=priority,
            notes=notes,
            created_by=request.user,
            modified_by=request.user
        )
        
        # Get curriculum info for response
        curriculum_level = mapping.curriculum_level
        
        response_data = {
            'success': True,
            'message': f'Mapping added for {class_code}',
            'mapping': {
                'id': str(mapping.id),
                'class_code': mapping.class_code,
                'curriculum': {
                    'id': curriculum_level.id,
                    'display_name': curriculum_level.display_name,
                    'program': curriculum_level.subprogram.program.name,
                    'subprogram': curriculum_level.subprogram.name,
                    'level': curriculum_level.level_number
                },
                'priority': mapping.priority,
                'academic_year': mapping.academic_year
            }
        }
        
        print(f"[CURRICULUM_MAPPING] Added: {class_code} → {curriculum_level.display_name}")
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"[ADD_CURRICULUM_MAPPING_ERROR] {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while adding the mapping'
        }, status=500)


@login_required
@user_passes_test(is_admin_teacher)
@require_http_methods(["POST"])
def remove_curriculum_mapping(request):
    """
    AJAX endpoint to remove a curriculum mapping
    """
    console_log = {
        "view": "remove_curriculum_mapping",
        "user": request.user.username,
        "method": request.method
    }
    logger.info(f"[REMOVE_CURRICULUM_MAPPING] {json.dumps(console_log)}")
    
    try:
        data = json.loads(request.body)
        mapping_id = data.get('mapping_id')
        
        if not mapping_id:
            return JsonResponse({
                'success': False,
                'error': 'Mapping ID is required'
            }, status=400)
        
        mapping = get_object_or_404(ClassCurriculumMapping, id=mapping_id)
        
        # Soft delete by marking inactive
        mapping.is_active = False
        mapping.modified_by = request.user
        mapping.save()
        
        print(f"[CURRICULUM_MAPPING] Removed: {mapping.class_code} → {mapping.curriculum_level.display_name}")
        
        return JsonResponse({
            'success': True,
            'message': f'Mapping removed for {mapping.class_code}'
        })
        
    except Exception as e:
        logger.error(f"[REMOVE_CURRICULUM_MAPPING_ERROR] {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while removing the mapping'
        }, status=500)


@login_required
@user_passes_test(is_admin_teacher)
@require_http_methods(["POST"])
def update_mapping_priority(request):
    """
    AJAX endpoint to update mapping priority
    """
    console_log = {
        "view": "update_mapping_priority",
        "user": request.user.username,
        "method": request.method
    }
    logger.info(f"[UPDATE_MAPPING_PRIORITY] {json.dumps(console_log)}")
    
    try:
        data = json.loads(request.body)
        mapping_id = data.get('mapping_id')
        new_priority = data.get('priority')
        
        if not mapping_id or new_priority is None:
            return JsonResponse({
                'success': False,
                'error': 'Mapping ID and priority are required'
            }, status=400)
        
        mapping = get_object_or_404(ClassCurriculumMapping, id=mapping_id)
        
        # Update priority
        old_priority = mapping.priority
        mapping.priority = new_priority
        mapping.modified_by = request.user
        mapping.save()
        
        print(f"[CURRICULUM_MAPPING] Priority updated: {mapping.class_code} from {old_priority} to {new_priority}")
        
        return JsonResponse({
            'success': True,
            'message': f'Priority updated for {mapping.class_code}'
        })
        
    except Exception as e:
        logger.error(f"[UPDATE_MAPPING_PRIORITY_ERROR] {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while updating priority'
        }, status=500)


@login_required
@user_passes_test(is_admin_teacher)
@require_http_methods(["POST"])
def bulk_add_mappings(request):
    """
    AJAX endpoint to bulk add curriculum mappings
    """
    console_log = {
        "view": "bulk_add_mappings",
        "user": request.user.username,
        "method": request.method
    }
    logger.info(f"[BULK_ADD_MAPPINGS] {json.dumps(console_log)}")
    
    try:
        data = json.loads(request.body)
        mappings = data.get('mappings', [])
        academic_year = data.get('academic_year', str(timezone.now().year))
        
        if not mappings:
            return JsonResponse({
                'success': False,
                'error': 'No mappings provided'
            }, status=400)
        
        created_count = 0
        updated_count = 0
        errors = []
        
        with transaction.atomic():
            for mapping_data in mappings:
                class_code = mapping_data.get('class_code')
                curriculum_level_id = mapping_data.get('curriculum_level_id')
                priority = mapping_data.get('priority', 1)
                
                if not class_code or not curriculum_level_id:
                    errors.append(f"Invalid data for {class_code}")
                    continue
                
                # Check if exists
                existing = ClassCurriculumMapping.objects.filter(
                    class_code=class_code.upper(),
                    curriculum_level_id=curriculum_level_id,
                    academic_year=academic_year
                ).first()
                
                if existing:
                    if not existing.is_active:
                        existing.is_active = True
                        existing.priority = priority
                        existing.modified_by = request.user
                        existing.save()
                        updated_count += 1
                else:
                    ClassCurriculumMapping.objects.create(
                        class_code=class_code.upper(),
                        curriculum_level_id=curriculum_level_id,
                        academic_year=academic_year,
                        priority=priority,
                        created_by=request.user,
                        modified_by=request.user
                    )
                    created_count += 1
        
        response_data = {
            'success': True,
            'message': f'Created {created_count}, updated {updated_count} mappings',
            'created': created_count,
            'updated': updated_count
        }
        
        if errors:
            response_data['errors'] = errors
        
        print(f"[CURRICULUM_MAPPING] Bulk operation: Created {created_count}, Updated {updated_count}")
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"[BULK_ADD_MAPPINGS_ERROR] {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred during bulk operation'
        }, status=500)


@login_required
@user_passes_test(is_admin_teacher)
@require_http_methods(["GET"])
def get_class_mappings(request, class_code):
    """
    AJAX endpoint to get all mappings for a specific class
    """
    console_log = {
        "view": "get_class_mappings",
        "class_code": class_code,
        "user": request.user.username
    }
    logger.info(f"[GET_CLASS_MAPPINGS] {json.dumps(console_log)}")
    
    academic_year = request.GET.get('year', str(timezone.now().year))
    
    mappings = ClassCurriculumMapping.objects.filter(
        class_code=class_code.upper(),
        academic_year=academic_year,
        is_active=True
    ).select_related(
        'curriculum_level__subprogram__program'
    ).order_by('priority')
    
    mappings_data = []
    for mapping in mappings:
        mappings_data.append({
            'id': str(mapping.id),
            'curriculum': {
                'id': mapping.curriculum_level.id,
                'display_name': mapping.curriculum_level.display_name,
                'program': mapping.curriculum_level.subprogram.program.name,
                'subprogram': mapping.curriculum_level.subprogram.name,
                'level': mapping.curriculum_level.level_number
            },
            'priority': mapping.priority,
            'notes': mapping.notes
        })
    
    return JsonResponse({
        'success': True,
        'class_code': class_code,
        'academic_year': academic_year,
        'mappings': mappings_data
    })
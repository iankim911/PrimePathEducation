"""
Curriculum Admin API Views
Admin-only endpoints for managing class-curriculum mappings
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
import json
import logging

from ..models import ClassCurriculumMapping
from ..models.class_constants import CLASS_CODE_CHOICES, get_class_category, get_class_stream
from core.models import Program, SubProgram, CurriculumLevel

logger = logging.getLogger(__name__)

@login_required
@require_http_methods(["GET"])
def get_all_classes_admin(request):
    """Get all classes with curriculum mappings for admin management"""
    # Check if user is admin
    if not request.user.is_staff:
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    try:
        classes_data = []
        
        # Get all class codes from constants
        for class_code, class_name in CLASS_CODE_CHOICES:
            # Get curriculum mapping if exists
            mapping = ClassCurriculumMapping.get_primary_curriculum(
                class_code, 
                request.GET.get('year', 2024)
            )
            
            class_data = {
                'code': class_code,
                'name': class_name,
                'category': get_class_category(class_code),
                'stream': get_class_stream(class_code),
                'curriculum': None,
                'program': None,
                'subprogram': None,
                'level': None
            }
            
            if mapping:
                # Format curriculum display
                class_data['curriculum'] = f"{mapping.subprogram.program.name} × {mapping.subprogram.name} × Level {mapping.level_number}"
                # Use program name, extract short code from it (e.g., 'PRIME CORE' -> 'CORE')
                program_name = mapping.subprogram.program.name
                class_data['program'] = program_name.replace('PRIME ', '') if program_name.startswith('PRIME ') else program_name
                class_data['subprogram'] = mapping.subprogram.name
                class_data['level'] = mapping.level_number
            
            classes_data.append(class_data)
        
        return JsonResponse({'classes': classes_data})
        
    except Exception as e:
        logger.error(f"Error getting classes for admin: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_class_details(request, class_code):
    """Get details of a specific class"""
    # Check if user is admin
    if not request.user.is_staff:
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    try:
        # Find class in the constants
        class_name = None
        for code, name in CLASS_CODE_CHOICES:
            if code == class_code:
                class_name = name
                break
        
        if not class_name:
            return JsonResponse({'error': 'Class not found'}, status=404)
        
        # Get curriculum mapping
        mapping = ClassCurriculumMapping.get_primary_curriculum(
            class_code,
            request.GET.get('year', 2024)
        )
        
        class_data = {
            'code': class_code,
            'name': class_name,
            'category': get_class_category(class_code),
            'stream': get_class_stream(class_code),
            'program': None,
            'subprogram': None,
            'level': None
        }
        
        if mapping:
            # Use program name, extract short code from it
            program_name = mapping.subprogram.program.name
            class_data['program'] = program_name.replace('PRIME ', '') if program_name.startswith('PRIME ') else program_name
            class_data['subprogram'] = mapping.subprogram.name
            class_data['level'] = mapping.level_number
        
        return JsonResponse(class_data)
        
    except Exception as e:
        logger.error(f"Error getting class details: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def create_class(request):
    """Create a new class mapping"""
    # Check if user is admin
    if not request.user.is_staff:
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    try:
        data = json.loads(request.body)
        code = data.get('code')
        
        if not code:
            return JsonResponse({'error': 'Class code is required'}, status=400)
        
        # Check if class code exists in constants
        class_exists = any(c[0] == code for c in CLASS_CODE_CHOICES)
        if not class_exists:
            return JsonResponse({'error': 'Invalid class code. Use predefined class codes.'}, status=400)
        
        # Create curriculum mapping if provided
        program_code = data.get('program')
        subprogram_name = data.get('subprogram')
        level_number = data.get('level')
        
        if program_code and subprogram_name and level_number:
            # Get or create program
            # Map program codes to full names and grade ranges
            program_info = {
                'CORE': {'name': 'PRIME CORE', 'grade_start': 1, 'grade_end': 6},
                'ASCENT': {'name': 'PRIME ASCENT', 'grade_start': 4, 'grade_end': 9},
                'EDGE': {'name': 'PRIME EDGE', 'grade_start': 7, 'grade_end': 12},
                'PINNACLE': {'name': 'PRIME PINNACLE', 'grade_start': 10, 'grade_end': 12}
            }
            
            info = program_info.get(program_code, {'name': f'PRIME {program_code}', 'grade_start': 1, 'grade_end': 12})
            program, _ = Program.objects.get_or_create(
                name=info['name'],
                defaults={
                    'grade_range_start': info['grade_start'],
                    'grade_range_end': info['grade_end'],
                    'order': list(program_info.keys()).index(program_code) + 1 if program_code in program_info else 99
                }
            )
            
            # Get or create subprogram
            # Map subprogram order
            subprogram_orders = {
                'Phonics': 1, 'Sigma': 2, 'Elite': 3, 'Pro': 4,
                'Nova': 1, 'Drive': 2, 'Plus': 3,
                'Spark': 1, 'Rise': 2, 'Pursuit': 3,
                'Vision': 1, 'Endeavor': 2, 'Success': 3
            }
            
            subprogram, _ = SubProgram.objects.get_or_create(
                name=subprogram_name,
                program=program,
                defaults={
                    'order': subprogram_orders.get(subprogram_name, 99)
                }
            )
            
            # Get or create curriculum level
            curriculum_level, _ = CurriculumLevel.objects.get_or_create(
                subprogram=subprogram,
                level_number=int(level_number),
                defaults={
                    'description': f"{subprogram.name} Level {level_number}",
                    'internal_difficulty': int(level_number)  # Use level number as default difficulty
                }
            )
            
            # Create curriculum mapping
            ClassCurriculumMapping.objects.create(
                class_code=code,
                curriculum_level=curriculum_level,
                academic_year='2024',
                priority=1,
                is_active=True,
                created_by=request.user,
                modified_by=request.user
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Class mapping created successfully',
            'class_code': code
        })
        
    except Exception as e:
        logger.error(f"Error creating class: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["PUT"])
def update_class(request, class_code):
    """Update an existing class mapping"""
    # Check if user is admin
    if not request.user.is_staff:
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    try:
        # Verify class exists in constants
        class_exists = any(c[0] == class_code for c in CLASS_CODE_CHOICES)
        if not class_exists:
            return JsonResponse({'error': 'Class not found'}, status=404)
        
        data = json.loads(request.body)
        
        # Update curriculum mapping
        program_code = data.get('program')
        subprogram_name = data.get('subprogram')
        level_number = data.get('level')
        
        if program_code and subprogram_name and level_number:
            # Get or create program
            # Map program codes to full names and grade ranges
            program_info = {
                'CORE': {'name': 'PRIME CORE', 'grade_start': 1, 'grade_end': 6},
                'ASCENT': {'name': 'PRIME ASCENT', 'grade_start': 4, 'grade_end': 9},
                'EDGE': {'name': 'PRIME EDGE', 'grade_start': 7, 'grade_end': 12},
                'PINNACLE': {'name': 'PRIME PINNACLE', 'grade_start': 10, 'grade_end': 12}
            }
            
            info = program_info.get(program_code, {'name': f'PRIME {program_code}', 'grade_start': 1, 'grade_end': 12})
            program, _ = Program.objects.get_or_create(
                name=info['name'],
                defaults={
                    'grade_range_start': info['grade_start'],
                    'grade_range_end': info['grade_end'],
                    'order': list(program_info.keys()).index(program_code) + 1 if program_code in program_info else 99
                }
            )
            
            # Get or create subprogram
            # Map subprogram order
            subprogram_orders = {
                'Phonics': 1, 'Sigma': 2, 'Elite': 3, 'Pro': 4,
                'Nova': 1, 'Drive': 2, 'Plus': 3,
                'Spark': 1, 'Rise': 2, 'Pursuit': 3,
                'Vision': 1, 'Endeavor': 2, 'Success': 3
            }
            
            subprogram, _ = SubProgram.objects.get_or_create(
                name=subprogram_name,
                program=program,
                defaults={
                    'order': subprogram_orders.get(subprogram_name, 99)
                }
            )
            
            # Get or create curriculum level
            curriculum_level, _ = CurriculumLevel.objects.get_or_create(
                subprogram=subprogram,
                level_number=int(level_number),
                defaults={
                    'description': f"{subprogram.name} Level {level_number}",
                    'internal_difficulty': int(level_number)  # Use level number as default difficulty
                }
            )
            
            # Update or create curriculum mapping
            mapping, created = ClassCurriculumMapping.objects.update_or_create(
                class_code=class_code,
                academic_year='2024',
                defaults={
                    'curriculum_level': curriculum_level,
                    'priority': 1,
                    'is_active': True,
                    'modified_by': request.user
                }
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Class updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating class: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_class(request, class_code):
    """Delete class mappings"""
    # Check if user is admin
    if not request.user.is_staff:
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    try:
        # Delete curriculum mappings for this class
        deleted_count = ClassCurriculumMapping.objects.filter(class_code=class_code).delete()[0]
        
        return JsonResponse({
            'success': True,
            'message': f'Class mappings deleted successfully',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        logger.error(f"Error deleting class: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def save_curriculum_mapping(request):
    """Save curriculum mapping for a class"""
    # Check if user is admin
    if not request.user.is_staff:
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    try:
        data = json.loads(request.body)
        class_code = data.get('class_code')
        program_code = data.get('program')
        subprogram_name = data.get('subprogram')
        level_number = data.get('level')
        
        if not class_code:
            return JsonResponse({'error': 'Class code is required'}, status=400)
        
        # Verify class exists in constants
        class_exists = any(c[0] == class_code for c in CLASS_CODE_CHOICES)
        if not class_exists:
            return JsonResponse({'error': 'Invalid class code'}, status=404)
        
        if program_code and subprogram_name and level_number:
            # Get or create program
            # Map program codes to full names and grade ranges
            program_info = {
                'CORE': {'name': 'PRIME CORE', 'grade_start': 1, 'grade_end': 6},
                'ASCENT': {'name': 'PRIME ASCENT', 'grade_start': 4, 'grade_end': 9},
                'EDGE': {'name': 'PRIME EDGE', 'grade_start': 7, 'grade_end': 12},
                'PINNACLE': {'name': 'PRIME PINNACLE', 'grade_start': 10, 'grade_end': 12}
            }
            
            info = program_info.get(program_code, {'name': f'PRIME {program_code}', 'grade_start': 1, 'grade_end': 12})
            program, _ = Program.objects.get_or_create(
                name=info['name'],
                defaults={
                    'grade_range_start': info['grade_start'],
                    'grade_range_end': info['grade_end'],
                    'order': list(program_info.keys()).index(program_code) + 1 if program_code in program_info else 99
                }
            )
            
            # Get or create subprogram
            # Map subprogram order
            subprogram_orders = {
                'Phonics': 1, 'Sigma': 2, 'Elite': 3, 'Pro': 4,
                'Nova': 1, 'Drive': 2, 'Plus': 3,
                'Spark': 1, 'Rise': 2, 'Pursuit': 3,
                'Vision': 1, 'Endeavor': 2, 'Success': 3
            }
            
            subprogram, _ = SubProgram.objects.get_or_create(
                name=subprogram_name,
                program=program,
                defaults={
                    'order': subprogram_orders.get(subprogram_name, 99)
                }
            )
            
            # Get or create curriculum level
            curriculum_level, _ = CurriculumLevel.objects.get_or_create(
                subprogram=subprogram,
                level_number=int(level_number),
                defaults={
                    'description': f"{subprogram.name} Level {level_number}",
                    'internal_difficulty': int(level_number)  # Use level number as default difficulty
                }
            )
            
            # Update or create curriculum mapping
            mapping, created = ClassCurriculumMapping.objects.update_or_create(
                class_code=class_code,
                academic_year='2024',
                defaults={
                    'curriculum_level': curriculum_level,
                    'priority': 1,
                    'is_active': True,
                    'modified_by': request.user
                }
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Curriculum mapping saved successfully',
                'created': created
            })
        else:
            # Remove mapping if incomplete
            ClassCurriculumMapping.objects.filter(
                class_code=class_code,
                academic_year='2024'
            ).delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Curriculum mapping removed'
            })
        
    except Exception as e:
        logger.error(f"Error saving curriculum mapping: {e}")
        return JsonResponse({'error': str(e)}, status=500)
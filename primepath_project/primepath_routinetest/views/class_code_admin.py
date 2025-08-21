"""
Class Code Administration Views
Provides UI for viewing and managing class code mappings
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from primepath_routinetest.models.class_model import Class
from primepath_routinetest.class_code_mapping import (
    CLASS_CODE_CURRICULUM_MAPPING,
    CLASS_CODE_CATEGORIES,
    get_curriculum_statistics,
    get_class_codes_by_program
)
import json


def is_admin_or_head_teacher(user):
    """Check if user is admin or head teacher"""
    if user.is_superuser:
        return True
    if hasattr(user, 'teacher'):
        return user.teacher.is_head_teacher
    return False


@login_required
@user_passes_test(is_admin_or_head_teacher)
def class_code_overview(request):
    """Display overview of all class codes and their curriculum mappings"""
    
    context = {
        'title': 'Class Code Curriculum Mapping',
        'mapping': CLASS_CODE_CURRICULUM_MAPPING,
        'categories': CLASS_CODE_CATEGORIES,
        'statistics': get_curriculum_statistics(),
        'programs': {}
    }
    
    # Organize by program
    for program in ['CORE', 'EDGE', 'ASCENT', 'PINNACLE']:
        program_codes = {}
        for code in get_class_codes_by_program(program):
            curriculum = CLASS_CODE_CURRICULUM_MAPPING[code]
            # Extract subprogram
            parts = curriculum.split()
            if len(parts) >= 2:
                subprogram = parts[1]
                if subprogram not in program_codes:
                    program_codes[subprogram] = []
                program_codes[subprogram].append({
                    'code': code,
                    'curriculum': curriculum,
                    'level': parts[-1] if parts[-2] == 'Level' else None
                })
        context['programs'][program] = program_codes
    
    # Check which codes exist in database
    existing_classes = Class.objects.values_list('section', flat=True)
    context['existing_codes'] = set(existing_classes)
    
    return render(request, 'primepath_routinetest/class_code_overview.html', context)


@login_required
@user_passes_test(is_admin_or_head_teacher)
@require_http_methods(["POST"])
def sync_class_codes(request):
    """Sync class codes with database"""
    
    try:
        from django.core.management import call_command
        from io import StringIO
        
        # Get parameters
        dry_run = request.POST.get('dry_run', 'false') == 'true'
        update_existing = request.POST.get('update_existing', 'false') == 'true'
        academic_year = request.POST.get('academic_year', '2025')
        
        # Capture command output
        output = StringIO()
        
        # Run the management command
        call_command(
            'update_class_codes',
            dry_run=dry_run,
            update_existing=update_existing,
            academic_year=academic_year,
            stdout=output
        )
        
        result = output.getvalue()
        
        # Parse results for summary
        created = updated = skipped = errors = 0
        for line in result.split('\n'):
            if 'Created:' in line:
                created = int(line.split('Created:')[1].split('classes')[0].strip())
            elif 'Updated:' in line:
                updated = int(line.split('Updated:')[1].split('classes')[0].strip())
            elif 'Skipped:' in line:
                skipped = int(line.split('Skipped:')[1].split('classes')[0].strip())
            elif 'Errors:' in line:
                errors = int(line.split('Errors:')[1].split('classes')[0].strip())
        
        return JsonResponse({
            'success': True,
            'message': 'Class codes synchronized successfully' if not dry_run else 'Dry run completed',
            'details': {
                'created': created,
                'updated': updated,
                'skipped': skipped,
                'errors': errors,
                'dry_run': dry_run
            },
            'output': result
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error syncing class codes: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_class_code_mapping(request):
    """API endpoint to get class code mapping data"""
    
    program_filter = request.GET.get('program', None)
    
    if program_filter:
        codes = get_class_codes_by_program(program_filter)
        mapping = {code: CLASS_CODE_CURRICULUM_MAPPING[code] for code in codes}
    else:
        mapping = CLASS_CODE_CURRICULUM_MAPPING
    
    # Check which codes exist in database
    existing_classes = list(Class.objects.values('section', 'name', 'id'))
    existing_map = {cls['section']: cls for cls in existing_classes}
    
    # Build response
    response_data = []
    for code, curriculum in mapping.items():
        entry = {
            'code': code,
            'curriculum': curriculum,
            'exists': code in existing_map
        }
        if code in existing_map:
            entry['class_id'] = str(existing_map[code]['id'])
            entry['class_name'] = existing_map[code]['name']
        response_data.append(entry)
    
    return JsonResponse({
        'mapping': response_data,
        'total': len(response_data),
        'statistics': get_curriculum_statistics()
    })


@login_required
@user_passes_test(is_admin_or_head_teacher)
def class_code_matrix(request):
    """Display class codes in a matrix view by program and level"""
    
    # Build matrix structure
    matrix = {
        'CORE': {
            'Phonics': {'Level 1': [], 'Level 2': [], 'Level 3': []},
            'Sigma': {'Level 1': [], 'Level 2': [], 'Level 3': []},
            'Elite': {'Level 1': [], 'Level 2': [], 'Level 3': []},
            'Pro': {'Level 1': [], 'Level 2': [], 'Level 3': []}
        },
        'ASCENT': {
            'Nova': {'Level 1': [], 'Level 2': [], 'Level 3': []},
            'Drive': {'Level 1': [], 'Level 2': [], 'Level 3': []},
            'Pro': {'Level 1': [], 'Level 2': [], 'Level 3': []}
        },
        'EDGE': {
            'Spark': {'Level 1': [], 'Level 2': [], 'Level 3': []},
            'Rise': {'Level 1': [], 'Level 2': [], 'Level 3': []},
            'Pursuit': {'Level 1': [], 'Level 2': [], 'Level 3': []},
            'Pro': {'Level 1': [], 'Level 2': [], 'Level 3': []}
        },
        'PINNACLE': {
            'Vision': {'Level 1': [], 'Level 2': []},
            'Endeavor': {'Level 1': [], 'Level 2': []},
            'Success': {'Level 1': [], 'Level 2': []},
            'Pro': {'Level 1': [], 'Level 2': []}
        }
    }
    
    # Populate matrix
    for code, curriculum in CLASS_CODE_CURRICULUM_MAPPING.items():
        parts = curriculum.split()
        if len(parts) >= 4:
            program = parts[0]
            subprogram = parts[1]
            level = f"Level {parts[3]}"
            
            if program in matrix and subprogram in matrix[program]:
                if level in matrix[program][subprogram]:
                    matrix[program][subprogram][level].append(code)
    
    # Check existing classes
    existing_classes = set(Class.objects.values_list('section', flat=True))
    
    context = {
        'title': 'Class Code Matrix View',
        'matrix': matrix,
        'existing_classes': existing_classes
    }
    
    return render(request, 'primepath_routinetest/class_code_matrix.html', context)
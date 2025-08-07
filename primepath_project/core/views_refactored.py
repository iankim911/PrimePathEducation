"""
Refactored core views using service layer and mixins.
This file will gradually replace views.py
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import transaction
from .services import CurriculumService, SchoolService, TeacherService
from common.mixins import AjaxResponseMixin
import json
import logging

logger = logging.getLogger(__name__)


def index(request):
    """Landing page."""
    return render(request, 'core/index.html')


def teacher_dashboard(request):
    """Teacher dashboard with statistics using DashboardService."""
    from .services import DashboardService
    
    # Use service to get dashboard data
    stats = DashboardService.get_dashboard_stats()
    recent_sessions = DashboardService.get_recent_sessions(limit=10)
    
    # Maintain exact same context structure for template compatibility
    context = {
        'recent_sessions': recent_sessions,
        'active_exams': stats['active_exams'],
        'total_sessions': stats['total_sessions'],
        # Additional stats available but not breaking existing template
        'completed_sessions': stats.get('completed_sessions', 0),
        'completion_rate': stats.get('completion_rate', 0),
        'recent_activity': stats.get('recent_sessions', 0),
    }
    return render(request, 'core/teacher_dashboard.html', context)


def curriculum_levels(request):
    """Display curriculum levels using CurriculumService."""
    # Use service to get programs with hierarchy
    programs = CurriculumService.get_programs_with_hierarchy()
    
    # Handle AJAX requests
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = CurriculumService.serialize_program_hierarchy(programs)
        return JsonResponse({'programs': data})
    
    return render(request, 'core/curriculum_levels.html', {'programs': programs})


def placement_rules(request):
    """Display placement rules matrix."""
    from placement_test.models import Exam
    
    # Use service to get programs
    programs = CurriculumService.get_programs_with_hierarchy()
    
    # Get all active exams for mapping
    all_exams = Exam.objects.filter(is_active=True).order_by('name')
    
    # Organize levels by program
    levels_by_program = {
        'CORE': [],
        'ASCENT': [],
        'EDGE': [],
        'PINNACLE': []
    }
    
    for program in programs:
        program_name = program.name
        if program_name in levels_by_program:
            for subprogram in program.subprograms.all():
                for level in subprogram.levels.all():
                    # Add available exams to each level
                    level.available_exams = all_exams
                    level.mapped_exams = Exam.objects.filter(
                        curriculum_level=level,
                        is_active=True
                    ).order_by('name')
                    levels_by_program[program_name].append(level)
    
    # Define rank options
    rank_options = [
        {'value': 'top_10', 'label': 'Top 10%'},
        {'value': 'top_20', 'label': 'Top 20%'},
        {'value': 'top_30', 'label': 'Top 30%'},
        {'value': 'average', 'label': 'Average (30-70%)'},
        {'value': 'below_average', 'label': 'Below Average (70-100%)'},
    ]
    
    context = {
        'grades': range(1, 13),
        'core_grades': range(1, 5),
        'ascent_grades': range(5, 7),
        'edge_grades': range(7, 10),
        'pinnacle_grades': range(10, 13),
        'rank_options': rank_options,
        'core_levels': levels_by_program['CORE'],
        'ascent_levels': levels_by_program['ASCENT'],
        'edge_levels': levels_by_program['EDGE'],
        'pinnacle_levels': levels_by_program['PINNACLE'],
    }
    return render(request, 'core/placement_rules_matrix.html', context)


@require_http_methods(["POST"])
def create_placement_rule(request):
    """Create a new placement rule using service."""
    try:
        data = json.loads(request.body)
        
        rule = CurriculumService.create_placement_rule({
            'grade': data['grade'],
            'min_rank_percentile': data['min_rank'],
            'max_rank_percentile': data['max_rank'],
            'curriculum_level_id': data['curriculum_level'],
            'priority': data.get('priority', 1)
        })
        
        return JsonResponse({
            'success': True,
            'rule': {
                'id': rule.id,
                'grade': rule.grade,
                'rank_range': f"Top {rule.max_rank_percentile}%",
                'curriculum': rule.curriculum_level.full_name,
                'priority': rule.priority
            }
        })
    except Exception as e:
        logger.error(f"Error creating placement rule: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["DELETE"])
def delete_placement_rule(request, pk):
    """Delete a placement rule."""
    try:
        from .models import PlacementRule
        rule = get_object_or_404(PlacementRule, pk=pk)
        rule.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Error deleting placement rule: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["GET"])
def get_placement_rules(request):
    """Get all placement rules in a format suitable for the matrix view."""
    from .models import PlacementRule
    
    rules = PlacementRule.objects.all()
    rules_data = []
    
    # Convert academic rank to our rank system
    rank_mapping = {
        10: 'top_10',
        20: 'top_20', 
        30: 'top_30',
        40: 'top_40',
        50: 'top_50',
        70: 'below_50',
    }
    
    for rule in rules:
        # Find the appropriate rank value
        rank_value = 'below_50'  # default
        for percentile, rank_key in rank_mapping.items():
            if rule.max_rank_percentile <= percentile:
                rank_value = rank_key
                break
                
        rules_data.append({
            'grade': rule.grade,
            'rank': rank_value,
            'curriculum_level_id': rule.curriculum_level_id,
        })
    
    return JsonResponse({'success': True, 'rules': rules_data})


@require_http_methods(["POST"]) 
def save_placement_rules(request):
    """Save placement rules from the matrix view."""
    try:
        from .models import PlacementRule
        
        data = json.loads(request.body)
        rules = data.get('rules', [])
        
        # Define percentile ranges for each rank
        rank_percentiles = {
            'top_10': (0, 10),
            'top_20': (10, 20),
            'top_30': (20, 30),
            'top_40': (30, 40),
            'top_50': (40, 50),
            'below_50': (50, 100),
        }
        
        with transaction.atomic():
            # Clear existing rules
            PlacementRule.objects.all().delete()
            
            # Create new rules
            for rule_data in rules:
                rank = rule_data['rank']
                min_perc, max_perc = rank_percentiles.get(rank, (0, 100))
                
                CurriculumService.create_placement_rule({
                    'grade': rule_data['grade'],
                    'min_rank_percentile': min_perc,
                    'max_rank_percentile': max_perc,
                    'curriculum_level_id': rule_data['curriculum_level_id'],
                    'priority': 1
                })
        
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Error saving placement rules: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def exam_mapping(request):
    """View for managing curriculum level to exam mappings."""
    from placement_test.models import Exam
    from .models import ExamLevelMapping
    
    # Use service to get programs
    programs = CurriculumService.get_programs_with_hierarchy()
    
    # Organize levels by program
    levels_by_program = {
        'CORE': [],
        'ASCENT': [],
        'EDGE': [],
        'PINNACLE': []
    }
    
    # Get all active exams
    all_exams = Exam.objects.filter(is_active=True).order_by('name')
    
    # Process exam names and check for PDF files
    processed_exams = []
    for exam in all_exams:
        display_name = exam.name.replace('PRIME ', '').replace('Level ', 'Lv ')
        has_pdf = bool(exam.pdf_file)
        processed_exams.append({
            'id': str(exam.id),
            'name': exam.name,
            'display_name': display_name,
            'has_pdf': has_pdf
        })
    
    for program in programs:
        program_name = program.name
        if program_name in levels_by_program:
            for subprogram in program.subprograms.all():
                for level in subprogram.levels.all():
                    # Get all available exams
                    level.available_exams = processed_exams
                    
                    # Get existing mappings for this level
                    existing_mappings = ExamLevelMapping.objects.filter(
                        curriculum_level=level
                    ).select_related('exam').order_by('slot')
                    
                    # Prepare mapped exams data
                    level.existing_mappings = []
                    for mapping in existing_mappings:
                        display_name = mapping.exam.name.replace('PRIME ', '').replace('Level ', 'Lv ')
                        level.existing_mappings.append({
                            'slot': mapping.slot,
                            'exam_id': str(mapping.exam.id),
                            'exam_name': mapping.exam.name,
                            'exam_display_name': display_name,
                            'has_pdf': bool(mapping.exam.pdf_file)
                        })
                    
                    levels_by_program[program_name].append(level)
    
    context = {
        'core_levels': levels_by_program['CORE'],
        'ascent_levels': levels_by_program['ASCENT'],
        'edge_levels': levels_by_program['EDGE'],
        'pinnacle_levels': levels_by_program['PINNACLE'],
    }
    
    return render(request, 'core/exam_mapping.html', context)


@require_http_methods(["POST"])
def save_exam_mappings(request):
    """Save curriculum level to exam mappings."""
    from .models import ExamLevelMapping
    
    try:
        data = json.loads(request.body)
        mappings = data.get('mappings', [])
        level_id = data.get('level_id')
        
        logger.info(f"Saving exam mappings: {len(mappings)} mappings")
        
        with transaction.atomic():
            if level_id:
                # Delete existing mappings for this level only
                ExamLevelMapping.objects.filter(curriculum_level_id=level_id).delete()
                
                # Create new mappings for this level
                for mapping in mappings:
                    if mapping['curriculum_level_id'] == int(level_id):
                        ExamLevelMapping.objects.create(
                            curriculum_level_id=mapping['curriculum_level_id'],
                            exam_id=mapping['exam_id'],
                            slot=mapping['slot']
                        )
            else:
                # Get all unique curriculum level IDs from mappings
                level_ids = set(m['curriculum_level_id'] for m in mappings)
                
                # Delete existing mappings for these levels
                ExamLevelMapping.objects.filter(curriculum_level_id__in=level_ids).delete()
                
                # Create new mappings
                for mapping in mappings:
                    ExamLevelMapping.objects.create(
                        curriculum_level_id=mapping['curriculum_level_id'],
                        exam_id=mapping['exam_id'],
                        slot=mapping['slot']
                    )
        
        return JsonResponse({'success': True})
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({'success': False, 'error': f'Invalid JSON: {str(e)}'}, status=400)
    except Exception as e:
        logger.error(f"Error saving exam mappings: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
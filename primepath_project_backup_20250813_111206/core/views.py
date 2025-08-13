from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import Teacher, Program, SubProgram, CurriculumLevel, PlacementRule
from .curriculum_constants import is_valid_subprogram, is_test_subprogram, log_filtered_subprograms
from .utils.curriculum_display import get_curriculum_level_display_data
import json
import logging

logger = logging.getLogger(__name__)


def index(request):
    return render(request, 'core/index.html')


@login_required
def teacher_dashboard(request):
    from placement_test.models import StudentSession, Exam
    
    # Log dashboard access
    logger.info(f"[DASHBOARD_ACCESS] User: {request.user.username}, Full Name: {request.user.get_full_name()}")
    print(f"[DASHBOARD_ACCESS] User: {request.user.username}, Full Name: {request.user.get_full_name()}")
    
    recent_sessions = StudentSession.objects.select_related('exam', 'school', 'original_curriculum_level', 'final_curriculum_level').order_by('-started_at')[:10]
    active_exams = Exam.objects.filter(is_active=True).count()
    total_sessions = StudentSession.objects.count()
    
    context = {
        'recent_sessions': recent_sessions,
        'active_exams': active_exams,
        'total_sessions': total_sessions,
    }
    return render(request, 'core/teacher_dashboard.html', context)


@login_required
def curriculum_levels(request):
    programs = Program.objects.prefetch_related('subprograms__levels').all()
    
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = []
        for program in programs:
            program_data = {
                'id': program.id,
                'name': program.get_name_display(),
                'grade_range': f"{program.grade_range_start}-{program.grade_range_end}",
                'subprograms': []
            }
            for subprogram in program.subprograms.all():
                subprogram_data = {
                    'id': subprogram.id,
                    'name': subprogram.name,
                    'levels': [
                        {
                            'id': level.id,
                            'number': level.level_number,
                            'full_name': level.full_name
                        }
                        for level in subprogram.levels.all()
                    ]
                }
                program_data['subprograms'].append(subprogram_data)
            data.append(program_data)
        return JsonResponse({'programs': data})
    
    return render(request, 'core/curriculum_levels.html', {'programs': programs})


@login_required
def placement_rules(request):
    from placement_test.models import Exam
    
    # Log the start of student levels loading
    logger.info("[STUDENT_LEVELS] Loading student levels matrix")
    console_log = {
        "view": "placement_rules",
        "action": "loading",
        "user": str(request.user),
        "timestamp": str(json.dumps(None, default=str))
    }
    print(f"[STUDENT_LEVELS_INIT] {json.dumps(console_log)}")
    
    # Get all programs
    programs = Program.objects.prefetch_related('subprograms__levels').all()
    
    # Get all active exams for mapping
    all_exams = Exam.objects.filter(is_active=True).order_by('name')
    
    # Track filtered subprograms for logging
    filtered_subprograms = []
    total_subprograms_checked = 0
    valid_subprograms_count = 0
    
    # Separate levels by program
    core_levels = []
    ascent_levels = []
    edge_levels = []
    pinnacle_levels = []
    
    for program in programs:
        for subprogram in program.subprograms.all():
            total_subprograms_checked += 1
            
            # Filter out test/QA subprograms
            if is_test_subprogram(subprogram.name):
                filtered_subprograms.append(f"{program.name} - {subprogram.name}")
                logger.debug(f"[STUDENT_LEVELS_FILTER] Filtering out test subprogram: {subprogram.name}")
                continue  # Skip this subprogram entirely
            
            # Only process valid subprograms
            if not is_valid_subprogram(subprogram.name):
                # Double-check: if it's not test and not valid, log warning
                logger.warning(f"[STUDENT_LEVELS_WARNING] Unknown subprogram (not test, not valid): {subprogram.name}")
                filtered_subprograms.append(f"{program.name} - {subprogram.name} (unknown)")
                continue
            
            valid_subprograms_count += 1
            
            for level in subprogram.levels.all():
                # Add display data for proper formatting
                level.display_data = get_curriculum_level_display_data(level)
                # Enhanced logging for display data
                if hasattr(level, 'display_data') and level.display_data:
                    logger.debug(f"[DISPLAY_DATA_SET] Level {level.id}: {level.display_data.get('subprogram_display')}")
                else:
                    logger.warning(f"[DISPLAY_DATA_MISSING] Level {level.id}: No display data!")

                
                # Add available exams to each level
                level.available_exams = all_exams
                level.mapped_exams = Exam.objects.filter(
                    curriculum_level=level,
                    is_active=True
                ).order_by('name')
                
                if program.name == 'CORE':
                    core_levels.append(level)
                elif program.name == 'ASCENT':
                    ascent_levels.append(level)
                elif program.name == 'EDGE':
                    edge_levels.append(level)
                elif program.name == 'PINNACLE':
                    pinnacle_levels.append(level)
    
    # Log filtering results
    if filtered_subprograms:
        log_filtered_subprograms(logger, filtered_subprograms)
    
    # Comprehensive logging of what's being displayed
    console_log = {
        "view": "placement_rules",
        "action": "subprograms_processed",
        "total_checked": total_subprograms_checked,
        "valid_count": valid_subprograms_count,
        "filtered_count": len(filtered_subprograms),
        "filtered_items": filtered_subprograms[:5] if filtered_subprograms else [],  # Show first 5 for debugging
        "levels_count": {
            "CORE": len(core_levels),
            "ASCENT": len(ascent_levels),
            "EDGE": len(edge_levels),
            "PINNACLE": len(pinnacle_levels)
        }
    }
    logger.info(f"[STUDENT_LEVELS_SUMMARY] {json.dumps(console_log)}")
    print(f"[STUDENT_LEVELS_SUMMARY] {json.dumps(console_log, indent=2)}")
    
    # Define rank options
    rank_options = [
        {'value': 'top_10', 'label': 'Top 10%'},
        {'value': 'top_20', 'label': 'Top 20%'},
        {'value': 'top_30', 'label': 'Top 30%'},
        {'value': 'average', 'label': 'Average (30-70%)'},
        {'value': 'below_average', 'label': 'Below Average (70-100%)'},
    ]
    
    context = {
        'grades': range(1, 13),  # Keep all grades for the full view
        'core_grades': range(1, 5),  # Grades 1-4 for PRIME CORE
        'ascent_grades': range(5, 7),  # Grades 5-6 for PRIME ASCENT
        'edge_grades': range(7, 10),  # Grades 7-9 for PRIME EDGE
        'pinnacle_grades': range(10, 13),  # Grades 10-12 for PRIME PINNACLE
        'rank_options': rank_options,
        'core_levels': core_levels,
        'ascent_levels': ascent_levels,
        'edge_levels': edge_levels,
        'pinnacle_levels': pinnacle_levels,
    }
    return render(request, 'core/placement_rules_matrix.html', context)


@require_http_methods(["POST"])
@login_required
def create_placement_rule(request):
    try:
        data = json.loads(request.body)
        
        rule = PlacementRule.objects.create(
            grade=data['grade'],
            min_rank_percentile=data['min_rank'],
            max_rank_percentile=data['max_rank'],
            curriculum_level_id=data['curriculum_level'],
            priority=data.get('priority', 1)
        )
        
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
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["DELETE"])
@login_required
def delete_placement_rule(request, pk):
    try:
        rule = get_object_or_404(PlacementRule, pk=pk)
        rule.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["GET"])
@login_required
def get_placement_rules(request):
    """Get all placement rules in a format suitable for the matrix view"""
    rules = PlacementRule.objects.all()
    rules_data = []
    
    # Convert academic rank to our rank system
    rank_mapping = {
        10: 'top_10',
        20: 'top_20', 
        30: 'top_30',
        40: 'top_40',
        50: 'top_50',
        70: 'below_50',  # Below average maps to below 50%
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
@login_required
def save_placement_rules(request):
    """Save placement rules from the matrix view"""
    try:
        data = json.loads(request.body)
        rules = data.get('rules', [])
        
        # Clear existing rules
        PlacementRule.objects.all().delete()
        
        # Define percentile ranges for each rank
        rank_percentiles = {
            'top_10': (0, 10),
            'top_20': (10, 20),
            'top_30': (20, 30),
            'top_40': (30, 40),
            'top_50': (40, 50),
            'below_50': (50, 100),
        }
        
        # Create new rules
        for rule_data in rules:
            rank = rule_data['rank']
            min_perc, max_perc = rank_percentiles.get(rank, (0, 100))
            
            PlacementRule.objects.create(
                grade=rule_data['grade'],
                min_rank_percentile=min_perc,
                max_rank_percentile=max_perc,
                curriculum_level_id=rule_data['curriculum_level_id'],
                priority=1  # Default priority
            )
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def exam_mapping(request):
    """View for managing curriculum level to exam mappings"""
    from placement_test.models import Exam
    from .models import ExamLevelMapping
    
    # Log the start of level exams loading
    logger.info("[LEVEL_EXAMS] Loading level exams configuration view")
    console_log = {
        "view": "exam_mapping",
        "action": "loading",
        "user": str(request.user),
        "timestamp": str(json.dumps(None, default=str))
    }
    print(f"[LEVEL_EXAMS_INIT] {json.dumps(console_log)}")
    
    # Get all programs
    programs = Program.objects.prefetch_related('subprograms__levels').all()
    
    # Track filtered subprograms for logging
    filtered_subprograms = []
    total_subprograms_checked = 0
    valid_subprograms_count = 0
    
    # Separate levels by program
    core_levels = []
    ascent_levels = []
    edge_levels = []
    pinnacle_levels = []
    
    # Get all active exams and annotate with PDF status
    all_exams = Exam.objects.filter(is_active=True).order_by('name')
    
    # Process exam names and check for PDF files
    processed_exams = []
    for exam in all_exams:
        # Remove 'PRIME' prefix and change 'Level' to 'Lv'
        display_name = exam.name.replace('PRIME ', '').replace('Level ', 'Lv ')
        has_pdf = bool(exam.pdf_file)
        processed_exams.append({
            'id': str(exam.id),  # Convert UUID to string
            'name': exam.name,
            'display_name': display_name,
            'has_pdf': has_pdf
        })
    
    for program in programs:
        for subprogram in program.subprograms.all():
            total_subprograms_checked += 1
            
            # Filter out test/QA subprograms - SAME AS placement_rules view
            if is_test_subprogram(subprogram.name):
                filtered_subprograms.append(f"{program.name} - {subprogram.name}")
                logger.debug(f"[LEVEL_EXAMS_FILTER] Filtering out test subprogram: {subprogram.name}")
                continue  # Skip this subprogram entirely
            
            # Only process valid subprograms
            if not is_valid_subprogram(subprogram.name):
                # Double-check: if it's not test and not valid, log warning
                logger.warning(f"[LEVEL_EXAMS_WARNING] Unknown subprogram (not test, not valid): {subprogram.name}")
                filtered_subprograms.append(f"{program.name} - {subprogram.name} (unknown)")
                continue
            
            valid_subprograms_count += 1
            
            for level in subprogram.levels.all():
                # Add display data for proper formatting
                level.display_data = get_curriculum_level_display_data(level)
                # Enhanced logging for display data
                if hasattr(level, 'display_data') and level.display_data:
                    logger.debug(f"[DISPLAY_DATA_SET] Level {level.id}: {level.display_data.get('subprogram_display')}")
                else:
                    logger.warning(f"[DISPLAY_DATA_MISSING] Level {level.id}: No display data!")

                
                # Get all available exams (not just those mapped to this level)
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
                
                # Add internal difficulty information
                level.internal_difficulty_value = level.internal_difficulty if hasattr(level, 'internal_difficulty') else None
                
                if program.name == 'CORE':
                    core_levels.append(level)
                elif program.name == 'ASCENT':
                    ascent_levels.append(level)
                elif program.name == 'EDGE':
                    edge_levels.append(level)
                elif program.name == 'PINNACLE':
                    pinnacle_levels.append(level)
    
    # Log filtering results  
    if filtered_subprograms:
        log_filtered_subprograms(logger, filtered_subprograms)
    
    # Comprehensive logging of what's being displayed
    console_log = {
        "view": "exam_mapping",
        "action": "subprograms_processed",
        "total_checked": total_subprograms_checked,
        "valid_count": valid_subprograms_count,
        "filtered_count": len(filtered_subprograms),
        "filtered_items": filtered_subprograms[:5] if filtered_subprograms else [],  # Show first 5 for debugging
        "levels_count": {
            "CORE": len(core_levels),
            "ASCENT": len(ascent_levels),
            "EDGE": len(edge_levels),
            "PINNACLE": len(pinnacle_levels)
        }
    }
    logger.info(f"[LEVEL_EXAMS_SUMMARY] {json.dumps(console_log)}")
    print(f"[LEVEL_EXAMS_SUMMARY] {json.dumps(console_log, indent=2)}")
    
    context = {
        'core_levels': core_levels,
        'ascent_levels': ascent_levels,
        'edge_levels': edge_levels,
        'pinnacle_levels': pinnacle_levels,
    }
    
    return render(request, 'core/exam_mapping.html', context)


@require_http_methods(["POST"])
@login_required
def save_exam_mappings(request):
    """Save curriculum level to exam mappings"""
    from .models import ExamLevelMapping
    from placement_test.models import Exam
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Log the raw request body for debugging
        logger.info(f"Request body: {request.body}")
        
        data = json.loads(request.body)
        mappings = data.get('mappings', [])
        level_id = data.get('level_id')  # If saving for specific level only
        
        logger.info(f"Parsed mappings: {mappings}")
        logger.info(f"Level ID: {level_id}")
        
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


@require_http_methods(["POST"])
@login_required
def save_difficulty_levels(request):
    """Save internal difficulty levels for curriculum levels"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        data = json.loads(request.body)
        difficulty_updates = data.get('difficulty_updates', [])
        
        logger.info(f"Updating difficulty levels: {difficulty_updates}")
        
        with transaction.atomic():
            for update in difficulty_updates:
                level_id = update.get('level_id')
                difficulty = update.get('difficulty')
                
                if level_id:
                    try:
                        level = CurriculumLevel.objects.get(id=level_id)
                        level.internal_difficulty = difficulty if difficulty else None
                        level.save()
                        logger.info(f"Updated level {level_id} with difficulty {difficulty}")
                    except CurriculumLevel.DoesNotExist:
                        logger.warning(f"CurriculumLevel {level_id} not found")
        
        return JsonResponse({'success': True, 'message': 'Difficulty levels updated successfully'})
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({'success': False, 'error': f'Invalid JSON: {str(e)}'}, status=400)
    except Exception as e:
        logger.error(f"Error saving difficulty levels: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
"""
Comprehensive fix for exam_mapping view AttributeError
This file contains the corrected exam_mapping function with extensive debugging
"""

import json
import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import transaction

logger = logging.getLogger(__name__)

@login_required
def exam_mapping(request):
    """View for managing curriculum level to exam mappings - FIXED VERSION"""
    from placement_test.models import Exam
    from .models import ExamLevelMapping, Program
    from .curriculum_constants import is_test_subprogram, is_valid_subprogram
    from .utils import get_curriculum_level_display_data, log_filtered_subprograms
    
    # === PHASE 1: INITIALIZATION AND LOGGING ===
    logger.info("[EXAM_MAPPING_FIX] Starting fixed exam_mapping view")
    console_log = {
        "view": "exam_mapping",
        "action": "loading",
        "user": str(request.user),
        "fix_version": "2.0",
        "debug_mode": True
    }
    print(f"[EXAM_MAPPING_INIT] {json.dumps(console_log, indent=2)}")
    
    # === PHASE 2: DATA RETRIEVAL ===
    # Get all programs with related data
    programs = Program.objects.prefetch_related('subprograms__levels').all()
    
    # Track filtered subprograms for logging
    filtered_subprograms = []
    total_subprograms_checked = 0
    valid_subprograms_count = 0
    
    # Initialize level containers
    core_levels = []
    ascent_levels = []
    edge_levels = []
    pinnacle_levels = []
    
    # === PHASE 3: EXAM PROCESSING ===
    # Get all active exams as QuerySet (keeping as objects, not dicts)
    all_exams = Exam.objects.filter(is_active=True).order_by('name')
    
    # Log exam retrieval
    console_log = {
        "action": "exams_retrieved",
        "total_exams": all_exams.count(),
        "exam_ids": [str(e.id) for e in all_exams[:5]]  # Log first 5 for debugging
    }
    print(f"[EXAM_RETRIEVAL] {json.dumps(console_log, indent=2)}")
    
    # Get all exam mappings upfront for efficiency
    all_exam_mappings = ExamLevelMapping.objects.select_related('curriculum_level').all()
    exam_to_level_map = {}
    for mapping in all_exam_mappings:
        exam_to_level_map[mapping.exam_id] = mapping.curriculum_level
    
    console_log = {
        "action": "mappings_loaded",
        "total_mappings": len(exam_to_level_map),
        "mapped_exam_ids": list(str(eid) for eid in list(exam_to_level_map.keys())[:5])
    }
    print(f"[MAPPING_LOAD] {json.dumps(console_log, indent=2)}")
    
    # === PHASE 4: PROCESS PROGRAMS AND LEVELS ===
    for program in programs:
        program_exam_count = 0
        
        for subprogram in program.subprograms.all():
            total_subprograms_checked += 1
            
            # Filter out test/QA subprograms
            if is_test_subprogram(subprogram.name):
                filtered_subprograms.append(f"{program.name} - {subprogram.name}")
                logger.debug(f"[FILTER] Filtering out test subprogram: {subprogram.name}")
                continue
            
            # Only process valid subprograms
            if not is_valid_subprogram(subprogram.name):
                logger.warning(f"[WARNING] Unknown subprogram: {subprogram.name}")
                filtered_subprograms.append(f"{program.name} - {subprogram.name} (unknown)")
                continue
            
            valid_subprograms_count += 1
            
            for level in subprogram.levels.all():
                # Add display data for proper formatting
                level.display_data = get_curriculum_level_display_data(level)
                
                # === CRITICAL FIX: Process exams correctly ===
                # Get exam IDs mapped to THIS specific level
                this_level_exam_ids = set(
                    ExamLevelMapping.objects.filter(
                        curriculum_level=level
                    ).values_list('exam_id', flat=True)
                )
                
                # Build available exams list with proper structure
                level.available_exams = []
                
                for exam in all_exams:
                    # Create exam info dictionary with all required fields
                    exam_info = {
                        'id': str(exam.id),  # Template expects string UUID
                        'name': exam.name,
                        'display_name': exam.name.replace('PRIME ', '').replace('Level ', 'Lv '),
                        'has_pdf': bool(exam.pdf_file),
                        'is_mapped_elsewhere': False,
                        'is_mapped_here': False,
                        'mapped_to_level': None
                    }
                    
                    # Check mapping status
                    exam_uuid = exam.id
                    if exam_uuid in this_level_exam_ids:
                        exam_info['is_mapped_here'] = True
                    elif exam_uuid in exam_to_level_map:
                        exam_info['is_mapped_elsewhere'] = True
                        exam_info['mapped_to_level'] = exam_to_level_map[exam_uuid].full_name
                    
                    level.available_exams.append(exam_info)
                    program_exam_count += 1
                
                # Debug log for first level of each program
                if program_exam_count == 1:
                    console_log = {
                        "action": "level_exams_processed",
                        "level_id": level.id,
                        "level_name": level.full_name,
                        "available_exams_count": len(level.available_exams),
                        "sample_exam": level.available_exams[0] if level.available_exams else None
                    }
                    print(f"[LEVEL_EXAMS_DEBUG] {json.dumps(console_log, indent=2)}")
                
                # Get existing mappings for this level
                existing_mappings = ExamLevelMapping.objects.filter(
                    curriculum_level=level
                ).select_related('exam').order_by('slot')
                
                # Prepare mapped exams data for display
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
                level.internal_difficulty_value = getattr(level, 'internal_difficulty', None)
                
                # Categorize by program
                if program.name == 'CORE':
                    core_levels.append(level)
                elif program.name == 'ASCENT':
                    ascent_levels.append(level)
                elif program.name == 'EDGE':
                    edge_levels.append(level)
                elif program.name == 'PINNACLE':
                    pinnacle_levels.append(level)
    
    # === PHASE 5: FINAL LOGGING AND CONTEXT PREPARATION ===
    if filtered_subprograms:
        log_filtered_subprograms(logger, filtered_subprograms)
    
    # Comprehensive summary logging
    console_log = {
        "view": "exam_mapping",
        "action": "processing_complete",
        "total_subprograms_checked": total_subprograms_checked,
        "valid_subprograms": valid_subprograms_count,
        "filtered_count": len(filtered_subprograms),
        "levels_count": {
            "CORE": len(core_levels),
            "ASCENT": len(ascent_levels),
            "EDGE": len(edge_levels),
            "PINNACLE": len(pinnacle_levels)
        },
        "total_exams_available": all_exams.count(),
        "total_mappings": len(exam_to_level_map),
        "fix_applied": True
    }
    logger.info(f"[EXAM_MAPPING_SUMMARY] {json.dumps(console_log)}")
    print(f"[EXAM_MAPPING_COMPLETE] {json.dumps(console_log, indent=2)}")
    
    # Validate data structure before sending to template
    validation_log = {
        "action": "template_data_validation",
        "core_first_level_check": None,
        "errors": []
    }
    
    if core_levels and core_levels[0].available_exams:
        first_exam = core_levels[0].available_exams[0]
        validation_log["core_first_level_check"] = {
            "has_id": 'id' in first_exam,
            "has_name": 'name' in first_exam,
            "has_display_name": 'display_name' in first_exam,
            "has_pdf": 'has_pdf' in first_exam,
            "id_type": type(first_exam.get('id', '')).__name__,
            "sample_id": first_exam.get('id', 'MISSING')[:8] + "..." if first_exam.get('id') else 'MISSING'
        }
    else:
        validation_log["errors"].append("No core levels or no available exams")
    
    print(f"[TEMPLATE_VALIDATION] {json.dumps(validation_log, indent=2)}")
    
    context = {
        'core_levels': core_levels,
        'ascent_levels': ascent_levels,
        'edge_levels': edge_levels,
        'pinnacle_levels': pinnacle_levels,
        'debug_info': {
            'total_exams': all_exams.count(),
            'total_mappings': len(exam_to_level_map),
            'fix_version': '2.0'
        }
    }
    
    return render(request, 'core/exam_mapping.html', context)
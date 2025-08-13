#!/usr/bin/env python
"""
Comprehensive Difficulty Progression Fix
Fixes the gap in difficulty tiers that prevents students from progressing
from CORE Phonics to harder exams.

This implements a logical difficulty progression across all 44 curriculum levels.
"""

import os
import sys
import django
from django.db import transaction
import json
from datetime import datetime

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from core.models import CurriculumLevel, Program, SubProgram
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Define comprehensive difficulty mapping
# Each program gets a range, each subprogram within gets progressive difficulties
DIFFICULTY_MAPPING = {
    'CORE': {
        # CORE spans difficulty 1-12 (grades 1-4)
        'Phonics': {1: 1, 2: 2, 3: 3},        # Entry level
        'Sigma': {1: 4, 2: 5, 3: 6},          # Intermediate
        'Elite': {1: 7, 2: 8, 3: 9},          # Advanced
        'Pro': {1: 10, 2: 11, 3: 12},         # Highest CORE
    },
    'ASCENT': {
        # ASCENT spans difficulty 13-24 (grades 5-6)
        'Nova': {1: 13, 2: 14, 3: 15},        # Entry ASCENT
        'Drive': {1: 16, 2: 17, 3: 18},       # Intermediate
        'Flex': {1: 19, 2: 20, 3: 21},        # Advanced
        'Pro': {1: 22, 2: 23, 3: 24},         # Highest ASCENT
    },
    'EDGE': {
        # EDGE spans difficulty 25-36 (grades 7-9)
        'Spark': {1: 25, 2: 26, 3: 27},       # Entry EDGE
        'Rise': {1: 28, 2: 29, 3: 30},        # Intermediate
        'Pursuit': {1: 31, 2: 32, 3: 33},     # Advanced
        'Pro': {1: 34, 2: 35, 3: 36},         # Highest EDGE
    },
    'PINNACLE': {
        # PINNACLE spans difficulty 37-44 (grades 10-12, only 2 levels each)
        'Vision': {1: 37, 2: 38},             # Entry PINNACLE
        'Endeavor': {1: 39, 2: 40},           # Intermediate
        'Success': {1: 41, 2: 42},            # Advanced
        'Pro': {1: 43, 2: 44},                # Highest overall
    }
}

def analyze_current_state():
    """Analyze current difficulty assignments"""
    logger.info("="*80)
    logger.info("ANALYZING CURRENT DIFFICULTY STATE")
    logger.info("="*80)
    
    all_levels = CurriculumLevel.objects.exclude(
        subprogram__name__contains='[INACTIVE]'
    ).select_related('subprogram__program').order_by(
        'subprogram__program__order', 'subprogram__order', 'level_number'
    )
    
    current_state = {}
    missing_difficulties = []
    
    for level in all_levels:
        program_name = level.subprogram.program.name
        subprogram_name = level.subprogram.name
        level_number = level.level_number
        current_difficulty = level.internal_difficulty
        
        key = f"{program_name}|{subprogram_name}|{level_number}"
        current_state[key] = {
            'level': level,
            'current': current_difficulty,
            'proposed': None
        }
        
        # Get proposed difficulty
        if program_name in DIFFICULTY_MAPPING:
            if subprogram_name in DIFFICULTY_MAPPING[program_name]:
                if level_number in DIFFICULTY_MAPPING[program_name][subprogram_name]:
                    proposed = DIFFICULTY_MAPPING[program_name][subprogram_name][level_number]
                    current_state[key]['proposed'] = proposed
                    
                    if current_difficulty != proposed:
                        missing_difficulties.append({
                            'level': level,
                            'current': current_difficulty,
                            'proposed': proposed
                        })
    
    # Log analysis results
    logger.info(f"Total curriculum levels: {len(current_state)}")
    logger.info(f"Levels needing updates: {len(missing_difficulties)}")
    
    # Show current gaps
    difficulties_assigned = set()
    for key, data in current_state.items():
        if data['current'] is not None:
            difficulties_assigned.add(data['current'])
    
    if difficulties_assigned:
        min_diff = min(difficulties_assigned)
        max_diff = max(difficulties_assigned)
        logger.info(f"Current difficulty range: {min_diff} to {max_diff}")
        
        gaps = []
        for i in range(min_diff, max_diff + 1):
            if i not in difficulties_assigned:
                gaps.append(i)
        
        if gaps:
            logger.info(f"Current gaps in progression: {gaps}")
    
    return current_state, missing_difficulties

def apply_difficulty_fixes(dry_run=False):
    """Apply the difficulty tier fixes"""
    logger.info("="*80)
    logger.info(f"APPLYING DIFFICULTY FIXES (Dry Run: {dry_run})")
    logger.info("="*80)
    
    current_state, missing_difficulties = analyze_current_state()
    
    if not missing_difficulties:
        logger.info("✅ All difficulties are already correctly assigned!")
        return
    
    # Group changes by program for better logging
    changes_by_program = {}
    for item in missing_difficulties:
        level = item['level']
        program_name = level.subprogram.program.name
        if program_name not in changes_by_program:
            changes_by_program[program_name] = []
        changes_by_program[program_name].append(item)
    
    # Log planned changes
    logger.info("\nPlanned Changes:")
    for program_name in ['CORE', 'ASCENT', 'EDGE', 'PINNACLE']:
        if program_name in changes_by_program:
            logger.info(f"\n{program_name} Program:")
            for item in changes_by_program[program_name]:
                level = item['level']
                logger.info(f"  {level.subprogram.name} Level {level.level_number}: "
                          f"{item['current']} → {item['proposed']}")
    
    if dry_run:
        logger.info("\n⚠️  DRY RUN - No changes applied")
        return
    
    # Apply changes in a transaction
    try:
        with transaction.atomic():
            update_count = 0
            for item in missing_difficulties:
                level = item['level']
                level.internal_difficulty = item['proposed']
                level.save()
                update_count += 1
                
                logger.debug(f"Updated {level} to difficulty {item['proposed']}")
            
            logger.info(f"\n✅ Successfully updated {update_count} curriculum levels")
            
            # Verify the fix
            verify_progression()
            
    except Exception as e:
        logger.error(f"❌ Error applying fixes: {e}")
        raise

def verify_progression():
    """Verify the difficulty progression is now smooth"""
    logger.info("\n" + "="*80)
    logger.info("VERIFYING DIFFICULTY PROGRESSION")
    logger.info("="*80)
    
    all_levels = CurriculumLevel.objects.exclude(
        subprogram__name__contains='[INACTIVE]'
    ).select_related('subprogram__program').order_by('internal_difficulty')
    
    difficulties = {}
    for level in all_levels:
        diff = level.internal_difficulty
        if diff is not None:
            if diff not in difficulties:
                difficulties[diff] = []
            difficulties[diff].append(f"{level.subprogram.program.name} {level.subprogram.name} L{level.level_number}")
    
    # Check for gaps
    if difficulties:
        min_diff = min(difficulties.keys())
        max_diff = max(difficulties.keys())
        
        gaps = []
        for i in range(min_diff, max_diff + 1):
            if i not in difficulties:
                gaps.append(i)
        
        if gaps:
            logger.warning(f"⚠️  Gaps still exist in progression: {gaps}")
        else:
            logger.info(f"✅ Smooth progression from {min_diff} to {max_diff} with no gaps!")
            
        # Show sample of progression
        logger.info("\nSample of difficulty progression:")
        for diff in sorted(difficulties.keys())[:10]:
            sample = difficulties[diff][:2]  # Show first 2 at each level
            logger.info(f"  Difficulty {diff}: {', '.join(sample)}")
            if len(difficulties[diff]) > 2:
                logger.info(f"    ... and {len(difficulties[diff])-2} more")

def test_harder_exam_navigation():
    """Test that 'Harder exams' button will now work"""
    logger.info("\n" + "="*80)
    logger.info("TESTING 'HARDER EXAMS' NAVIGATION")
    logger.info("="*80)
    
    from placement_test.services.placement_service import PlacementService
    
    # Test from CORE Phonics Level 1 (difficulty 1)
    phonics_level_1 = CurriculumLevel.objects.filter(
        subprogram__program__name='CORE',
        subprogram__name='Phonics',
        level_number=1
    ).first()
    
    if phonics_level_1:
        logger.info(f"Testing from: {phonics_level_1}")
        logger.info(f"Current difficulty: {phonics_level_1.internal_difficulty}")
        
        # Try to find harder exam
        result = PlacementService.find_alternate_difficulty_exam(phonics_level_1, +1)
        
        if result:
            new_level, new_exam = result
            logger.info(f"✅ SUCCESS! Found harder exam:")
            logger.info(f"   New level: {new_level} (Difficulty: {new_level.internal_difficulty})")
            logger.info(f"   New exam: {new_exam.name}")
        else:
            logger.warning("❌ Still can't find harder exam - may need to map exams to difficulty 2 levels")
            
            # Check what's at difficulty 2
            diff_2_levels = CurriculumLevel.objects.filter(internal_difficulty=2)
            if diff_2_levels.exists():
                logger.info(f"Difficulty 2 levels exist: {diff_2_levels.count()}")
                for level in diff_2_levels[:3]:
                    from core.models import ExamLevelMapping
                    mappings = ExamLevelMapping.objects.filter(curriculum_level=level)
                    logger.info(f"  - {level}: {mappings.count()} exams mapped")
            else:
                logger.error("No levels at difficulty 2!")

def main():
    """Main execution"""
    import argparse
    parser = argparse.ArgumentParser(description='Fix difficulty progression gaps')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without applying')
    parser.add_argument('--test-only', action='store_true', help='Only run tests, no changes')
    args = parser.parse_args()
    
    logger.info("🔧 DIFFICULTY PROGRESSION FIX TOOL")
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if args.test_only:
        # Just test current state
        analyze_current_state()
        test_harder_exam_navigation()
    else:
        # Apply fixes
        apply_difficulty_fixes(dry_run=args.dry_run)
        
        if not args.dry_run:
            # Test the fix
            test_harder_exam_navigation()
    
    logger.info("\n✅ Process complete!")

if __name__ == "__main__":
    main()
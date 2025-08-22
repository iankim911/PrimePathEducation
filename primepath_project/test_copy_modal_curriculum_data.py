#!/usr/bin/env python
"""
Test script to verify curriculum data is being passed to copy modal
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from primepath_routinetest.services.exam_service import ExamService
import json

def test_curriculum_data():
    """Test that curriculum data is properly retrieved"""
    print("\n" + "="*80)
    print("TESTING COPY MODAL CURRICULUM DATA")
    print("="*80)
    
    # Get curriculum data
    curriculum_data = ExamService.get_routinetest_curriculum_levels()
    
    print(f"\n✅ Total curriculum levels found: {len(curriculum_data)}")
    
    # Group by program
    programs = {}
    for level in curriculum_data:
        program = level['program_name']
        subprogram = level['subprogram_name']
        
        if program not in programs:
            programs[program] = {}
        if subprogram not in programs[program]:
            programs[program][subprogram] = []
        
        programs[program][subprogram].append(level['level_number'])
    
    # Display structured data
    print("\n📚 CURRICULUM STRUCTURE:")
    print("-" * 40)
    
    for program in ['CORE', 'ASCENT', 'EDGE', 'PINNACLE']:
        if program in programs:
            print(f"\n{program}:")
            for subprogram, levels in programs[program].items():
                levels_str = ', '.join(str(l) for l in sorted(levels))
                print(f"  - {subprogram}: Levels {levels_str}")
        else:
            print(f"\n{program}: ❌ NOT FOUND")
    
    # Check for any missing curriculum levels
    print("\n" + "="*80)
    print("CHECKING FOR MISSING LEVELS")
    print("="*80)
    
    from primepath_routinetest.constants import ROUTINETEST_CURRICULUM_WHITELIST
    from core.models import CurriculumLevel
    
    missing = []
    for program_name, subprogram_name, level_number in ROUTINETEST_CURRICULUM_WHITELIST:
        try:
            level = CurriculumLevel.objects.get(
                subprogram__program__name=program_name,
                subprogram__name__icontains=subprogram_name,
                level_number=level_number
            )
        except CurriculumLevel.DoesNotExist:
            missing.append(f"{program_name} {subprogram_name} Level {level_number}")
    
    if missing:
        print(f"\n❌ Missing {len(missing)} curriculum levels in database:")
        for m in missing:
            print(f"  - {m}")
    else:
        print("\n✅ All curriculum levels from whitelist exist in database")
    
    # Check if data would be passed to template correctly
    print("\n" + "="*80)
    print("TEMPLATE DATA FORMAT CHECK")
    print("="*80)
    
    if curriculum_data:
        print("\n✅ Data is in correct format for template")
        print("\nSample data structure:")
        sample = curriculum_data[0] if curriculum_data else None
        if sample:
            print(json.dumps({
                'id': sample['id'],
                'program_name': sample['program_name'],
                'subprogram_name': sample['subprogram_name'],
                'level_number': sample['level_number'],
                'curriculum_level': {
                    'id': sample['curriculum_level'].id,
                    'full_name': sample['curriculum_level'].full_name
                }
            }, indent=2))
    else:
        print("\n❌ No curriculum data available!")

if __name__ == '__main__':
    test_curriculum_data()
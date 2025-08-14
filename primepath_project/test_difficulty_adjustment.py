#!/usr/bin/env python3
"""
Test difficulty adjustment functionality
"""

import os
import sys
import django
import json

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from core.models import CurriculumLevel, ExamLevelMapping
from placement_test.services.placement_service import PlacementService

print("="*60)
print("TESTING DIFFICULTY ADJUSTMENT")
print("="*60)

# Test Case 1: CORE Sigma Level 3 → Harder
print("\n📚 Test Case 1: CORE Sigma Level 3 → Request Harder Exam")
print("-" * 40)

sigma_3 = CurriculumLevel.objects.filter(
    subprogram__name='Sigma',
    level_number=3
).first()

if sigma_3:
    print(f"Current Level: {sigma_3.full_name}")
    print(f"Current Difficulty: {sigma_3.internal_difficulty}")
    
    # Try to adjust difficulty up
    print("\n🔄 Attempting to find harder exam...")
    result = PlacementService.adjust_difficulty(sigma_3, 1)
    
    if result:
        new_level, new_exam = result
        print(f"✅ SUCCESS!")
        print(f"   New Level: {new_level.full_name}")
        print(f"   New Difficulty: {new_level.internal_difficulty}")
        print(f"   New Exam: {new_exam.name}")
        print(f"   Difficulty Jump: {new_level.internal_difficulty - sigma_3.internal_difficulty}")
    else:
        print("❌ FAILED: No harder exam found")
        print("\n🔍 Debugging with find_alternate_difficulty_exam...")
        # Try the alternate method directly for debugging
        result2 = PlacementService.find_alternate_difficulty_exam(sigma_3, 1)
        if result2:
            print("✅ find_alternate_difficulty_exam succeeded!")
            new_level, new_exam = result2
            print(f"   New Level: {new_level.full_name}")
            print(f"   New Difficulty: {new_level.internal_difficulty}")
            print(f"   New Exam: {new_exam.name}")
        else:
            print("❌ find_alternate_difficulty_exam also failed")

# Test Case 2: CORE Elite Level 2 → Easier
print("\n📚 Test Case 2: CORE Elite Level 2 → Request Easier Exam")
print("-" * 40)

elite_2 = CurriculumLevel.objects.filter(
    subprogram__name='Elite',
    level_number=2
).first()

if elite_2:
    print(f"Current Level: {elite_2.full_name}")
    print(f"Current Difficulty: {elite_2.internal_difficulty}")
    
    # Try to adjust difficulty down
    print("\n🔄 Attempting to find easier exam...")
    result = PlacementService.adjust_difficulty(elite_2, -1)
    
    if result:
        new_level, new_exam = result
        print(f"✅ SUCCESS!")
        print(f"   New Level: {new_level.full_name}")
        print(f"   New Difficulty: {new_level.internal_difficulty}")
        print(f"   New Exam: {new_exam.name}")
        print(f"   Difficulty Drop: {elite_2.internal_difficulty - new_level.internal_difficulty}")
    else:
        print("❌ FAILED: No easier exam found")

# Test Case 3: Check all levels with exams
print("\n📚 Test Case 3: Check Difficulty Adjustment for All Levels with Exams")
print("-" * 40)

levels_with_exams = []
for level in CurriculumLevel.objects.all():
    mapping = ExamLevelMapping.objects.filter(curriculum_level=level).first()
    if mapping and mapping.exam.is_active:
        levels_with_exams.append(level)

print(f"Found {len(levels_with_exams)} levels with active exams")

for level in levels_with_exams:
    print(f"\n{level.full_name} (Difficulty: {level.internal_difficulty})")
    
    # Try harder
    harder = PlacementService.adjust_difficulty(level, 1)
    if harder:
        print(f"  ↑ Harder: {harder[0].full_name} (Diff: {harder[0].internal_difficulty})")
    else:
        print(f"  ↑ Harder: Not available")
    
    # Try easier
    easier = PlacementService.adjust_difficulty(level, -1)
    if easier:
        print(f"  ↓ Easier: {easier[0].full_name} (Diff: {easier[0].internal_difficulty})")
    else:
        print(f"  ↓ Easier: Not available")

print("\n" + "="*60)
print("DIFFICULTY ADJUSTMENT TEST COMPLETE")
print("="*60)
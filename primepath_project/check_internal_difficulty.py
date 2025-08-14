#!/usr/bin/env python3
"""
Check internal_difficulty values for all curriculum levels
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from core.models import CurriculumLevel, ExamLevelMapping

print("="*60)
print("CHECKING INTERNAL DIFFICULTY VALUES")
print("="*60)

# Get all curriculum levels
levels = CurriculumLevel.objects.select_related(
    'subprogram__program'
).order_by('subprogram__program__order', 'subprogram__order', 'level_number')

print(f"\nTotal Curriculum Levels: {levels.count()}\n")

# Group by program
current_program = None
for level in levels:
    if level.subprogram.program.name != current_program:
        current_program = level.subprogram.program.name
        print(f"\n{current_program}:")
        print("-" * 40)
    
    # Check for exam mapping
    mapping = ExamLevelMapping.objects.filter(curriculum_level=level).first()
    exam_name = mapping.exam.name if mapping else "No exam mapped"
    
    print(f"  {level.full_name:30} | Difficulty: {level.internal_difficulty:3} | Exam: {exam_name}")

# Check for missing internal_difficulty values
missing_difficulty = levels.filter(internal_difficulty__isnull=True)
if missing_difficulty.exists():
    print("\n⚠️ WARNING: Levels with missing internal_difficulty:")
    for level in missing_difficulty:
        print(f"  - {level.full_name}")
else:
    print("\n✅ All levels have internal_difficulty values set")

# Check CORE Sigma specifically
print("\n" + "="*60)
print("CORE SIGMA PROGRESSION ANALYSIS")
print("="*60)

sigma_levels = CurriculumLevel.objects.filter(
    subprogram__name='Sigma'
).order_by('level_number')

for level in sigma_levels:
    mapping = ExamLevelMapping.objects.filter(curriculum_level=level).first()
    exam_info = f"Exam: {mapping.exam.name}" if mapping else "No exam"
    print(f"CORE Sigma Level {level.level_number}: Difficulty={level.internal_difficulty} | {exam_info}")

# Check what's available for harder difficulty from Sigma Level 3
sigma_3 = CurriculumLevel.objects.filter(
    subprogram__name='Sigma', 
    level_number=3
).first()

if sigma_3:
    print(f"\nCurrent: {sigma_3.full_name} (Difficulty: {sigma_3.internal_difficulty})")
    
    # Find harder options
    harder_levels = CurriculumLevel.objects.filter(
        internal_difficulty__gt=sigma_3.internal_difficulty
    ).order_by('internal_difficulty')[:5]
    
    print("\nAvailable harder levels:")
    for level in harder_levels:
        mapping = ExamLevelMapping.objects.filter(curriculum_level=level).first()
        has_exam = "✅ Has exam" if mapping else "❌ No exam"
        print(f"  - {level.full_name:30} | Difficulty: {level.internal_difficulty:3} | {has_exam}")

print("\n" + "="*60)
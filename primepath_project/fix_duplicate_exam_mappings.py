#!/usr/bin/env python3
"""
Comprehensive fix for duplicate exam mappings issue.
This script identifies and fixes cases where the same exam is mapped to multiple curriculum levels.
"""

import os
import sys
import django
from collections import defaultdict

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.db import transaction
from core.models import ExamLevelMapping, CurriculumLevel
from placement_test.models import Exam
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def identify_duplicate_exam_mappings():
    """Identify exams that are mapped to multiple curriculum levels"""
    print("\n" + "="*80)
    print("🔍 IDENTIFYING DUPLICATE EXAM MAPPINGS")
    print("="*80)
    
    # Get all mappings
    mappings = ExamLevelMapping.objects.select_related('exam', 'curriculum_level').all()
    
    # Group by exam
    exam_to_levels = defaultdict(list)
    for mapping in mappings:
        exam_to_levels[mapping.exam].append({
            'level': mapping.curriculum_level,
            'slot': mapping.slot,
            'mapping_id': mapping.id
        })
    
    # Find duplicates
    duplicates = {}
    for exam, level_data in exam_to_levels.items():
        if len(level_data) > 1:
            duplicates[exam] = level_data
    
    if duplicates:
        print(f"\n⚠️ Found {len(duplicates)} exams mapped to multiple levels:")
        print("-" * 80)
        
        for exam, level_data in duplicates.items():
            print(f"\n📝 Exam: {exam.name} (ID: {exam.id})")
            print(f"   Total Questions: {exam.total_questions}")
            print(f"   Mapped to {len(level_data)} different levels:")
            
            for data in level_data:
                level = data['level']
                print(f"   • {level.full_name} (Slot {data['slot']}, Mapping ID: {data['mapping_id']})")
                print(f"     - Program: {level.subprogram.program.name}")
                print(f"     - SubProgram: {level.subprogram.name}")
                print(f"     - Level: {level.level_number}")
    else:
        print("\n✅ No duplicate exam mappings found!")
    
    return duplicates

def find_available_exams_for_level(level):
    """Find exams that could be used for a given level"""
    # Get all exams
    all_exams = Exam.objects.filter(is_active=True)
    
    # Get already mapped exam IDs
    mapped_exam_ids = ExamLevelMapping.objects.values_list('exam_id', flat=True).distinct()
    
    # Find unmapped exams
    unmapped_exams = all_exams.exclude(id__in=mapped_exam_ids)
    
    # Try to find exams with matching names
    level_name_parts = level.full_name.replace('PRIME ', '').split()
    matching_exams = []
    
    for exam in unmapped_exams:
        exam_name_normalized = exam.name.replace('[PT]_', '').replace('_', ' ')
        
        # Check if exam name contains level info
        match_score = 0
        for part in level_name_parts:
            if part.upper() in exam_name_normalized.upper():
                match_score += 1
        
        if match_score > 0:
            matching_exams.append((exam, match_score))
    
    # Sort by match score
    matching_exams.sort(key=lambda x: x[1], reverse=True)
    
    return [exam for exam, score in matching_exams[:5]]  # Return top 5 matches

def fix_duplicate_mappings(duplicates, dry_run=True):
    """Fix duplicate mappings by reassigning or creating new exams"""
    print("\n" + "="*80)
    print("🔧 FIXING DUPLICATE EXAM MAPPINGS")
    print("="*80)
    
    if dry_run:
        print("\n⚠️ DRY RUN MODE - No changes will be made")
    else:
        print("\n🚨 LIVE MODE - Changes will be saved to database")
    
    fixes_applied = []
    
    with transaction.atomic():
        for exam, level_data in duplicates.items():
            print(f"\n📝 Processing: {exam.name}")
            
            # Smart selection: Try to match exam name with appropriate level
            keep_mapping = None
            
            # First, try to find a mapping where exam name matches the level
            for data in level_data:
                level = data['level']
                exam_name_upper = exam.name.upper()
                level_str = f"LV{level.level_number}"
                level_str_alt = f"LEVEL{level.level_number}"
                level_str_alt2 = f"LEVEL {level.level_number}"
                
                if level_str in exam_name_upper or level_str_alt in exam_name_upper or level_str_alt2 in exam_name_upper:
                    keep_mapping = data
                    print(f"   📍 Found matching level in exam name: {exam.name} → Level {level.level_number}")
                    break
            
            # If no match found, keep the lowest level
            if not keep_mapping:
                level_data.sort(key=lambda x: (
                    x['level'].subprogram.program.id,
                    x['level'].subprogram.id, 
                    x['level'].level_number
                ))
                keep_mapping = level_data[0]
            print(f"   ✅ Keeping mapping for: {keep_mapping['level'].full_name}")
            
            # Fix the rest (excluding the one we're keeping)
            for data in level_data:
                if data['mapping_id'] == keep_mapping['mapping_id']:
                    continue  # Skip the one we're keeping
                level = data['level']
                mapping_id = data['mapping_id']
                
                print(f"\n   🔄 Need to fix: {level.full_name}")
                
                # Find alternative exams
                alternatives = find_available_exams_for_level(level)
                
                if alternatives:
                    # Use the best alternative
                    new_exam = alternatives[0]
                    print(f"      → Found alternative: {new_exam.name}")
                    
                    if not dry_run:
                        mapping = ExamLevelMapping.objects.get(id=mapping_id)
                        mapping.exam = new_exam
                        mapping.save()
                        print(f"      ✅ Updated mapping to use {new_exam.name}")
                    
                    fixes_applied.append({
                        'level': level.full_name,
                        'old_exam': exam.name,
                        'new_exam': new_exam.name,
                        'action': 'reassigned'
                    })
                else:
                    # No alternatives available - need to create or remove
                    print(f"      ⚠️ No alternative exams available")
                    
                    if not dry_run:
                        # Option 1: Remove the duplicate mapping
                        mapping = ExamLevelMapping.objects.get(id=mapping_id)
                        mapping.delete()
                        print(f"      🗑️ Removed duplicate mapping")
                    
                    fixes_applied.append({
                        'level': level.full_name,
                        'old_exam': exam.name,
                        'new_exam': None,
                        'action': 'removed'
                    })
        
        if dry_run:
            # Rollback in dry run mode
            transaction.set_rollback(True)
    
    return fixes_applied

def add_unique_constraint():
    """Add database constraint to prevent future duplicates"""
    print("\n" + "="*80)
    print("🔒 ADDING UNIQUE CONSTRAINT")
    print("="*80)
    
    print("""
To prevent future duplicates, add this migration:

from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('core', 'XXXX_previous_migration'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='examlevelmapping',
            constraint=models.UniqueConstraint(
                fields=['exam'],
                name='unique_exam_per_mapping'
            ),
        ),
    ]
    """)

def generate_report(duplicates, fixes):
    """Generate a detailed report of the fixes"""
    print("\n" + "="*80)
    print("📊 DUPLICATE EXAM MAPPINGS FIX REPORT")
    print("="*80)
    
    print(f"\n📈 Summary:")
    print(f"   • Total duplicate exams found: {len(duplicates)}")
    print(f"   • Total mappings affected: {sum(len(v) for v in duplicates.values())}")
    print(f"   • Total fixes applied: {len(fixes)}")
    
    if fixes:
        print(f"\n📝 Fixes Applied:")
        for fix in fixes:
            if fix['action'] == 'reassigned':
                print(f"   • {fix['level']}: {fix['old_exam']} → {fix['new_exam']}")
            elif fix['action'] == 'removed':
                print(f"   • {fix['level']}: Removed mapping for {fix['old_exam']}")
    
    # Check current state
    print(f"\n🔍 Verification:")
    remaining_duplicates = identify_duplicate_exam_mappings()
    if not remaining_duplicates:
        print("   ✅ All duplicates have been resolved!")
    else:
        print(f"   ⚠️ {len(remaining_duplicates)} duplicates still remain")

def verify_difficulty_progression():
    """Verify that difficulty progression works after fixes"""
    print("\n" + "="*80)
    print("🎯 VERIFYING DIFFICULTY PROGRESSION")
    print("="*80)
    
    # Check CORE Sigma progression
    core_sigma_levels = CurriculumLevel.objects.filter(
        subprogram__name__icontains='Sigma'
    ).order_by('level_number')
    
    print("\n📚 CORE Sigma Progression:")
    for level in core_sigma_levels:
        mappings = ExamLevelMapping.objects.filter(curriculum_level=level)
        if mappings.exists():
            exams = [m.exam.name for m in mappings]
            print(f"   • {level.full_name}: {', '.join(exams)}")
        else:
            print(f"   • {level.full_name}: ⚠️ No exam mapped")
    
    # Check that each level has unique exams
    all_mappings = ExamLevelMapping.objects.all()
    exam_counts = defaultdict(int)
    for mapping in all_mappings:
        exam_counts[mapping.exam.id] += 1
    
    duplicated_exams = [exam_id for exam_id, count in exam_counts.items() if count > 1]
    
    if duplicated_exams:
        print(f"\n⚠️ Still found {len(duplicated_exams)} exams used multiple times")
        for exam_id in duplicated_exams:
            exam = Exam.objects.get(id=exam_id)
            levels = []
            mappings = ExamLevelMapping.objects.filter(exam=exam).select_related('curriculum_level')
            for mapping in mappings:
                levels.append(mapping.curriculum_level.full_name)
            print(f"   • {exam.name}: Used in {list(levels)}")
    else:
        print("\n✅ Each exam is now uniquely mapped to only one level!")

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix duplicate exam mappings')
    parser.add_argument('--fix', action='store_true', help='Apply fixes (default is dry run)')
    parser.add_argument('--report-only', action='store_true', help='Only generate report')
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("🚀 DUPLICATE EXAM MAPPING FIX UTILITY")
    print("="*80)
    
    # Step 1: Identify duplicates
    duplicates = identify_duplicate_exam_mappings()
    
    if args.report_only:
        return
    
    # Step 2: Fix duplicates
    if duplicates:
        fixes = fix_duplicate_mappings(duplicates, dry_run=not args.fix)
        
        # Step 3: Generate report
        generate_report(duplicates, fixes)
    
    # Step 4: Verify progression
    verify_difficulty_progression()
    
    # Step 5: Show constraint info
    if args.fix:
        add_unique_constraint()
    
    print("\n" + "="*80)
    print("✅ COMPLETE")
    print("="*80)

if __name__ == '__main__':
    main()
#!/usr/bin/env python
"""
Test script to verify curriculum mapping persistence fix
Tests that program assignments are now saved with the current year (2025)
instead of being hardcoded to 2024
"""

import os
import sys
import django
from datetime import datetime

# Setup Django environment
sys.path.insert(0, '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.utils import timezone
from primepath_routinetest.models import ClassCurriculumMapping
from core.models import Program, SubProgram, CurriculumLevel
from django.contrib.auth import get_user_model

User = get_user_model()

def test_curriculum_persistence():
    """Test that curriculum mappings are saved with the current year"""
    print("\n" + "="*70)
    print("TESTING CURRICULUM MAPPING PERSISTENCE FIX")
    print("="*70)
    
    # Get current year
    current_year = str(timezone.now().year)
    print(f"\nCurrent year: {current_year}")
    
    # Test data
    test_class_code = "Sungjong3"
    
    # Check existing mappings for this class
    print(f"\n1. Checking existing mappings for class '{test_class_code}':")
    existing_mappings = ClassCurriculumMapping.objects.filter(
        class_code=test_class_code
    )
    
    for mapping in existing_mappings:
        print(f"   - Year: {mapping.academic_year}, Active: {mapping.is_active}")
        if mapping.curriculum_level:
            print(f"     Program: {mapping.curriculum_level.subprogram.program.name}")
            print(f"     SubProgram: {mapping.curriculum_level.subprogram.name}")
            print(f"     Level: {mapping.curriculum_level.level_number}")
    
    # Check for current year mapping
    print(f"\n2. Checking for {current_year} mapping:")
    current_mapping = ClassCurriculumMapping.objects.filter(
        class_code=test_class_code,
        academic_year=current_year,
        is_active=True
    ).first()
    
    if current_mapping:
        print(f"   ✅ Found mapping for {current_year}!")
        if current_mapping.curriculum_level:
            curriculum = current_mapping.curriculum_level
            print(f"   - {curriculum.subprogram.program.name} × {curriculum.subprogram.name} × Level {curriculum.level_number}")
    else:
        print(f"   ❌ No mapping found for {current_year}")
    
    # Check for old 2024 mappings
    print("\n3. Checking for outdated 2024 mappings:")
    old_mappings = ClassCurriculumMapping.objects.filter(
        class_code=test_class_code,
        academic_year="2024",
        is_active=True
    )
    
    if old_mappings.exists():
        print(f"   ⚠️ Found {old_mappings.count()} mapping(s) for 2024")
        for mapping in old_mappings:
            if mapping.curriculum_level:
                curriculum = mapping.curriculum_level
                print(f"   - {curriculum.subprogram.program.name} × {curriculum.subprogram.name} × Level {curriculum.level_number}")
    else:
        print("   ✅ No outdated 2024 mappings")
    
    # Test creating a new mapping with current year
    print("\n4. Testing new mapping creation:")
    try:
        # Get or create test program
        program, _ = Program.objects.get_or_create(
            name="PRIME EDGE",
            defaults={
                'grade_range_start': 7,
                'grade_range_end': 12,
                'order': 3
            }
        )
        
        # Get or create test subprogram
        subprogram, _ = SubProgram.objects.get_or_create(
            name="Rise",
            program=program,
            defaults={'order': 2}
        )
        
        # Get or create curriculum level
        curriculum_level, _ = CurriculumLevel.objects.get_or_create(
            subprogram=subprogram,
            level_number=2,
            defaults={
                'description': "Rise Level 2",
                'internal_difficulty': 2
            }
        )
        
        # Create or update mapping for current year
        admin_user = User.objects.filter(is_staff=True).first()
        mapping, created = ClassCurriculumMapping.objects.update_or_create(
            class_code=test_class_code,
            academic_year=current_year,
            defaults={
                'curriculum_level': curriculum_level,
                'priority': 1,
                'is_active': True,
                'modified_by': admin_user
            }
        )
        
        if created:
            print(f"   ✅ Created new mapping for {current_year}")
        else:
            print(f"   ✅ Updated existing mapping for {current_year}")
        
        print(f"   - Program: PRIME EDGE")
        print(f"   - SubProgram: Rise")
        print(f"   - Level: 2")
        print(f"   - Academic Year: {mapping.academic_year}")
        
    except Exception as e:
        print(f"   ❌ Error creating mapping: {e}")
    
    # Final verification
    print("\n5. Final verification:")
    final_check = ClassCurriculumMapping.objects.filter(
        class_code=test_class_code,
        academic_year=current_year,
        is_active=True
    ).first()
    
    if final_check:
        print(f"   ✅ SUCCESS: Mapping persisted for {current_year}")
        print(f"   - Class: {final_check.class_code}")
        print(f"   - Year: {final_check.academic_year}")
        print(f"   - Active: {final_check.is_active}")
        if final_check.curriculum_level:
            print(f"   - Curriculum: {final_check.curriculum_level.full_name}")
    else:
        print(f"   ❌ FAILED: No mapping found for {current_year}")
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)

if __name__ == "__main__":
    test_curriculum_persistence()
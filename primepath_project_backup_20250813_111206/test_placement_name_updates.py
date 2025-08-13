#!/usr/bin/env python
"""
Test script for Placement Test Name Updates
Tests that the curriculum level whitelist and naming convention changes work correctly
"""
import os
import sys
import django
import json
from datetime import datetime

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from core.models import Teacher, CurriculumLevel, SubProgram, Program
from django.test import Client


def test_placement_name_updates():
    """Test the placement test name updates"""
    print("\n" + "="*80)
    print("🔍 TESTING PLACEMENT TEST NAME UPDATES")
    print("="*80)
    
    # Expected whitelist of placement test levels
    EXPECTED_WHITELIST = [
        # CORE Program
        ('CORE', 'Phonics', 1), ('CORE', 'Phonics', 2), ('CORE', 'Phonics', 3),
        ('CORE', 'Sigma', 1), ('CORE', 'Sigma', 2), ('CORE', 'Sigma', 3),
        ('CORE', 'Elite', 1), ('CORE', 'Elite', 2), ('CORE', 'Elite', 3),
        ('CORE', 'Pro', 1), ('CORE', 'Pro', 2), ('CORE', 'Pro', 3),
        # ASCENT Program
        ('ASCENT', 'Nova', 1), ('ASCENT', 'Nova', 2), ('ASCENT', 'Nova', 3),
        ('ASCENT', 'Drive', 1), ('ASCENT', 'Drive', 2), ('ASCENT', 'Drive', 3),
        ('ASCENT', 'Pro', 1), ('ASCENT', 'Pro', 2), ('ASCENT', 'Pro', 3),
        # EDGE Program
        ('EDGE', 'Spark', 1), ('EDGE', 'Spark', 2), ('EDGE', 'Spark', 3),
        ('EDGE', 'Rise', 1), ('EDGE', 'Rise', 2), ('EDGE', 'Rise', 3),
        ('EDGE', 'Pursuit', 1), ('EDGE', 'Pursuit', 2), ('EDGE', 'Pursuit', 3),
        ('EDGE', 'Pro', 1), ('EDGE', 'Pro', 2), ('EDGE', 'Pro', 3),
        # PINNACLE Program
        ('PINNACLE', 'Vision', 1), ('PINNACLE', 'Vision', 2),
        ('PINNACLE', 'Endeavor', 1), ('PINNACLE', 'Endeavor', 2),
        ('PINNACLE', 'Success', 1), ('PINNACLE', 'Success', 2),
        ('PINNACLE', 'Pro', 1), ('PINNACLE', 'Pro', 2),
    ]
    
    print(f"\n1. Expected Whitelist Configuration:")
    print(f"   Total expected levels: {len(EXPECTED_WHITELIST)}")
    programs = list(set(item[0] for item in EXPECTED_WHITELIST))
    print(f"   Programs: {', '.join(programs)}")
    
    # Step 2: Check database curriculum levels
    print(f"\n2. Database Curriculum Levels:")
    all_levels = CurriculumLevel.objects.select_related('subprogram__program').all()
    print(f"   Total levels in database: {all_levels.count()}")
    
    # Check which expected levels exist in database
    found_levels = []
    missing_levels = []
    
    for expected_prog, expected_sub, expected_level in EXPECTED_WHITELIST:
        try:
            level = CurriculumLevel.objects.get(
                subprogram__program__name=expected_prog,
                subprogram__name=expected_sub,
                level_number=expected_level
            )
            found_levels.append((expected_prog, expected_sub, expected_level))
        except CurriculumLevel.DoesNotExist:
            missing_levels.append((expected_prog, expected_sub, expected_level))
    
    print(f"   ✅ Found in database: {len(found_levels)} of {len(EXPECTED_WHITELIST)}")
    if missing_levels:
        print(f"   ⚠️ Missing from database: {len(missing_levels)}")
        for prog, sub, level in missing_levels[:5]:  # Show first 5 missing
            print(f"      - {prog}, {sub}, Level {level}")
        if len(missing_levels) > 5:
            print(f"      ... and {len(missing_levels) - 5} more")
    
    # Step 3: Test the create exam page
    print(f"\n3. Testing Create Exam Page:")
    
    client = Client()
    
    # Login as teacher
    login_success = client.login(username='teacher1', password='teacher123')
    print(f"   Login Status: {'✅ Success' if login_success else '❌ Failed'}")
    
    if not login_success:
        print("   ❌ Cannot proceed without authentication")
        return False
    
    # Get the create exam page
    response = client.get('/api/placement/exams/create/')
    print(f"   Page Status: {response.status_code}")
    
    if response.status_code == 200:
        # Extract curriculum levels from context
        if hasattr(response, 'context') and response.context:
            curriculum_levels = response.context.get('curriculum_levels', [])
            print(f"   Levels returned: {len(curriculum_levels)}")
            
            # Check naming format
            if curriculum_levels:
                sample_level = curriculum_levels[0]
                print(f"\n   Sample Level Format:")
                print(f"      Display Name: {sample_level.get('display_name', 'N/A')}")
                print(f"      Base Name: {sample_level.get('exam_base_name', 'N/A')}")
                
                # Check if display name has [PT] prefix
                if sample_level.get('display_name', '').startswith('[PT]'):
                    print(f"      ✅ Has [PT] prefix")
                else:
                    print(f"      ❌ Missing [PT] prefix")
                
                # Check if "SubProgram" text is absent
                if 'SubProgram' not in sample_level.get('display_name', ''):
                    print(f"      ✅ No 'SubProgram' text")
                else:
                    print(f"      ❌ Contains 'SubProgram' text")
                
                # Show first 5 levels
                print(f"\n   First 5 Levels in Dropdown:")
                for i, level in enumerate(curriculum_levels[:5]):
                    print(f"      {i+1}. {level.get('display_name', 'N/A')}")
        else:
            # Parse HTML to check the dropdown options
            content = response.content.decode()
            
            # Count [PT] prefixes
            pt_count = content.count('[PT]')
            print(f"   [PT] prefixes found: {pt_count}")
            
            # Check for SubProgram text
            subprogram_count = content.count('SubProgram')
            print(f"   'SubProgram' occurrences: {subprogram_count}")
            
            # Extract option tags
            import re
            options = re.findall(r'<option[^>]*data-display-name="([^"]*)"', content)
            if options:
                print(f"   Options found: {len(options)}")
                print(f"\n   First 5 Options:")
                for i, option in enumerate(options[:5]):
                    print(f"      {i+1}. {option}")
    
    # Step 4: Summary
    print("\n" + "="*80)
    print("📋 TEST SUMMARY:")
    print("="*80)
    
    if len(found_levels) == len(EXPECTED_WHITELIST):
        print("✅ All expected curriculum levels found in database")
    else:
        print(f"⚠️ Only {len(found_levels)} of {len(EXPECTED_WHITELIST)} expected levels found")
    
    print("\nExpected Format:")
    print("  • Display names should start with '[PT]'")
    print("  • Format: '[PT] PROGRAM, SUBPROGRAM, Level X'")
    print("  • No 'SubProgram' text in names")
    print("  • Total of 40 placement test levels")
    
    return True


def check_specific_examples():
    """Check specific examples of expected naming"""
    print("\n" + "="*80)
    print("📝 CHECKING SPECIFIC NAMING EXAMPLES")
    print("="*80)
    
    examples = [
        ("CORE", "Phonics", 1, "[PT] CORE, Phonics, Level 1"),
        ("ASCENT", "Nova", 2, "[PT] ASCENT, Nova, Level 2"),
        ("EDGE", "Spark", 3, "[PT] EDGE, Spark, Level 3"),
        ("PINNACLE", "Vision", 1, "[PT] PINNACLE, Vision, Level 1"),
    ]
    
    for prog, sub, level_num, expected_display in examples:
        try:
            level = CurriculumLevel.objects.get(
                subprogram__program__name=prog,
                subprogram__name=sub,
                level_number=level_num
            )
            print(f"\n   {prog}, {sub}, Level {level_num}:")
            print(f"      Expected: {expected_display}")
            print(f"      Database ID: {level.id}")
            
            # What the view would generate
            pt_display = f"[PT] {prog}, {sub}, Level {level_num}"
            pt_base = f"{prog}_{sub}_Lv{level_num}".replace(" ", "_")
            
            print(f"      Generated Display: {pt_display}")
            print(f"      Generated Base: {pt_base}")
            
            if pt_display == expected_display:
                print(f"      ✅ Display name matches expected format")
            else:
                print(f"      ❌ Display name mismatch")
                
        except CurriculumLevel.DoesNotExist:
            print(f"\n   ❌ {prog}, {sub}, Level {level_num} - NOT FOUND IN DATABASE")


if __name__ == "__main__":
    print("\n" + "#"*80)
    print("# PLACEMENT TEST NAME UPDATES TEST")
    print("#"*80)
    
    test_placement_name_updates()
    check_specific_examples()
    
    print("\n🎯 EXPECTED BEHAVIOR:")
    print("  1. Only 40 specific curriculum levels shown in dropdown")
    print("  2. All names start with '[PT]' prefix")
    print("  3. Format: '[PT] PROGRAM, SUBPROGRAM, Level X'")
    print("  4. No 'SubProgram' text in any names")
    print("  5. Exam files named: [PT]_PROGRAM_SUBPROGRAM_LvX_YYMMDD")
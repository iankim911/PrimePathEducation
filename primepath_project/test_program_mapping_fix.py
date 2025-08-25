#!/usr/bin/env python
"""
Test Program Mapping Fix
========================

Test script to verify that the program mapping fix correctly resolves
the "No classes available to display" issue.

Author: Claude Code Agent System
Date: August 25, 2025
"""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from core.models import Teacher
from primepath_routinetest.models import TeacherClassAssignment
from primepath_routinetest.class_code_mapping import get_class_codes_by_program

def test_program_mapping_fix():
    """Test the corrected program mapping logic"""
    
    print("="*80)
    print("TESTING PROGRAM MAPPING FIX")
    print("="*80)
    
    # Get teacher1 (the account from the screenshots)
    teacher = Teacher.objects.get(user__username='teacher1')
    print(f"Testing with teacher: {teacher.name} ({teacher.user.username})")
    
    # Get their assignments
    my_assignments = TeacherClassAssignment.objects.filter(teacher=teacher, is_active=True)
    my_class_codes = [a.class_code for a in my_assignments]
    
    print(f"Teacher's classes: {sorted(my_class_codes)} ({len(my_class_codes)} total)")
    
    # Test the FIXED program mapping logic
    print(f"\n🔧 TESTING FIXED PROGRAM MAPPING LOGIC...")
    
    PROGRAM_MAPPING = {
        'CORE': get_class_codes_by_program('CORE'),
        'ASCENT': get_class_codes_by_program('ASCENT'), 
        'EDGE': get_class_codes_by_program('EDGE'),
        'PINNACLE': get_class_codes_by_program('PINNACLE')
    }
    
    print(f"Fixed program mapping counts:")
    for program, classes in PROGRAM_MAPPING.items():
        print(f"  {program}: {len(classes)} classes - {classes[:5]}{'...' if len(classes) > 5 else ''}")
    
    # Test the programs_data building logic (same as view)
    programs_data = []
    
    for program_name in ['CORE', 'ASCENT', 'EDGE', 'PINNACLE']:
        program_classes = []
        
        print(f"\n🔍 Processing {program_name} program...")
        print(f"  Available {program_name} classes: {PROGRAM_MAPPING[program_name]}")
        
        # This is the exact loop from the view
        for assignment in my_assignments:
            if assignment.class_code in PROGRAM_MAPPING[program_name]:
                print(f"    ✅ Found match: {assignment.class_code}")
                program_classes.append({
                    'class_code': assignment.class_code,
                    'program': program_name
                })
        
        # Only add program if it has classes (exact condition from view)
        if program_classes:
            programs_data.append({
                'name': program_name,
                'classes': program_classes
            })
            print(f"    ✅ {program_name} program ADDED with {len(program_classes)} classes")
        else:
            print(f"    ❌ {program_name} program SKIPPED - no matching classes")
    
    print(f"\n📊 FINAL RESULTS:")
    print(f"   programs_data count: {len(programs_data)}")
    print(f"   Total classes distributed: {sum(len(p['classes']) for p in programs_data)}")
    
    if len(programs_data) > 0:
        print(f"   ✅ SUCCESS: programs_data is populated!")
        print(f"   ✅ Class Management should now display classes instead of 'No classes available'")
        
        for program in programs_data:
            class_codes = [c['class_code'] for c in program['classes']]
            print(f"      {program['name']}: {class_codes}")
    else:
        print(f"   ❌ FAILURE: programs_data is still empty")
        print(f"   ❌ 'No classes available to display' will still appear")
    
    return len(programs_data) > 0

def compare_old_vs_new():
    """Compare the broken vs fixed logic"""
    
    print(f"\n" + "="*80)
    print("COMPARING OLD (BROKEN) VS NEW (FIXED) LOGIC")
    print("="*80)
    
    teacher = Teacher.objects.get(user__username='teacher1')
    my_assignments = TeacherClassAssignment.objects.filter(teacher=teacher, is_active=True)
    my_class_codes = [a.class_code for a in my_assignments]
    
    # OLD BROKEN LOGIC
    from primepath_routinetest.class_code_mapping import CLASS_CODE_CURRICULUM_MAPPING
    
    OLD_PROGRAM_MAPPING = {
        'CORE': [],
        'ASCENT': [],
        'EDGE': [],
        'PINNACLE': []
    }
    
    # Simulate the old broken string matching
    for code, curriculum in CLASS_CODE_CURRICULUM_MAPPING.items():
        if 'CORE' in curriculum:
            OLD_PROGRAM_MAPPING['CORE'].append(code)
        elif 'ASCENT' in curriculum:
            OLD_PROGRAM_MAPPING['ASCENT'].append(code)
        elif 'EDGE' in curriculum:
            OLD_PROGRAM_MAPPING['EDGE'].append(code)
        elif 'PINNACLE' in curriculum:
            OLD_PROGRAM_MAPPING['PINNACLE'].append(code)
    
    print("OLD BROKEN MAPPING:")
    old_total = 0
    for program, classes in OLD_PROGRAM_MAPPING.items():
        print(f"  {program}: {len(classes)} classes")
        old_total += len(classes)
    print(f"  Total mapped: {old_total}")
    
    # NEW FIXED LOGIC
    NEW_PROGRAM_MAPPING = {
        'CORE': get_class_codes_by_program('CORE'),
        'ASCENT': get_class_codes_by_program('ASCENT'), 
        'EDGE': get_class_codes_by_program('EDGE'),
        'PINNACLE': get_class_codes_by_program('PINNACLE')
    }
    
    print("\nNEW FIXED MAPPING:")
    new_total = 0
    for program, classes in NEW_PROGRAM_MAPPING.items():
        print(f"  {program}: {len(classes)} classes")
        new_total += len(classes)
    print(f"  Total mapped: {new_total}")
    
    print(f"\n📈 IMPROVEMENT:")
    print(f"   Old logic mapped: {old_total} classes")
    print(f"   New logic maps: {new_total} classes")
    print(f"   Improvement: +{new_total - old_total} classes ({((new_total - old_total) / max(old_total, 1) * 100):.0f}% increase)")
    
    # Check teacher1's classes specifically
    teacher1_old_matches = 0
    teacher1_new_matches = 0
    
    for class_code in my_class_codes:
        # Old logic
        for program_classes in OLD_PROGRAM_MAPPING.values():
            if class_code in program_classes:
                teacher1_old_matches += 1
                break
        
        # New logic  
        for program_classes in NEW_PROGRAM_MAPPING.values():
            if class_code in program_classes:
                teacher1_new_matches += 1
                break
    
    print(f"\n👤 TEACHER1 SPECIFIC IMPACT:")
    print(f"   Teacher1 total classes: {len(my_class_codes)}")
    print(f"   Old logic would map: {teacher1_old_matches}/{len(my_class_codes)} ({teacher1_old_matches/len(my_class_codes)*100:.1f}%)")
    print(f"   New logic maps: {teacher1_new_matches}/{len(my_class_codes)} ({teacher1_new_matches/len(my_class_codes)*100:.1f}%)")

def main():
    success = test_program_mapping_fix()
    compare_old_vs_new()
    
    print(f"\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    if success:
        print("✅ PROGRAM MAPPING FIX SUCCESSFUL")
        print("✅ Class Management should now work correctly")
        print("✅ 'No classes available to display' issue resolved")
    else:
        print("❌ PROGRAM MAPPING FIX FAILED")
        print("❌ Further investigation required")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
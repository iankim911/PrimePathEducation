#!/usr/bin/env python
"""
Debug Current Session Issue
===========================

Debug script to understand exactly what's happening with the current user session
that's showing in the screenshots. This will help identify which account is having
the "No classes available to display" issue.

Author: Claude Code Agent System
Date: August 25, 2025
"""

import os
import sys
import django
import json

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from core.models import Teacher
from primepath_routinetest.models import TeacherClassAssignment, Class
from primepath_routinetest.class_code_mapping import CLASS_CODE_CURRICULUM_MAPPING

def debug_session_issue():
    """Debug the specific session issue from screenshots"""
    
    print("="*80)
    print("DEBUG: CURRENT SESSION ISSUE ANALYSIS")
    print("="*80)
    
    # The screenshots show 11 specific classes
    screenshot_classes = [
        'C5', 'Chung-cho1', 'HIGH_10E', 'HIGH_10F', 'HIGH_11D', 
        'MIDDLE_7A', 'PRIMARY_1D', 'PRIMARY_2A', 'SejongM', 'Sungjong4', 'TaejoE'
    ]
    
    print(f"Classes shown in screenshot: {screenshot_classes}")
    print(f"Total classes in screenshot: {len(screenshot_classes)}")
    
    # Find which teacher has exactly these 11 classes in TeacherClassAssignment
    print(f"\n🔍 SEARCHING FOR TEACHER WITH THESE EXACT CLASSES...")
    
    all_teachers = Teacher.objects.all()
    matching_teachers = []
    
    for teacher in all_teachers:
        tca_assignments = TeacherClassAssignment.objects.filter(teacher=teacher, is_active=True)
        tca_class_codes = set(tca_assignments.values_list('class_code', flat=True))
        
        # Check if this teacher's classes match the screenshot
        screenshot_set = set(screenshot_classes)
        
        if tca_class_codes == screenshot_set:
            matching_teachers.append({
                'teacher': teacher,
                'exact_match': True,
                'tca_count': len(tca_class_codes),
                'class_count': Class.objects.filter(is_active=True, assigned_teachers=teacher).count()
            })
            print(f"✅ EXACT MATCH: {teacher.name} (User: {teacher.user.username})")
            print(f"   TCA classes: {sorted(tca_class_codes)}")
            print(f"   Class.assigned_teachers count: {Class.objects.filter(is_active=True, assigned_teachers=teacher).count()}")
        elif len(tca_class_codes & screenshot_set) > 5:  # Significant overlap
            matching_teachers.append({
                'teacher': teacher,
                'exact_match': False,
                'overlap': len(tca_class_codes & screenshot_set),
                'tca_count': len(tca_class_codes),
                'class_count': Class.objects.filter(is_active=True, assigned_teachers=teacher).count()
            })
            print(f"⚠️  PARTIAL MATCH: {teacher.name} (User: {teacher.user.username})")
            print(f"   Overlap: {len(tca_class_codes & screenshot_set)} out of {len(screenshot_set)}")
            print(f"   TCA classes: {sorted(tca_class_codes)}")
    
    if not matching_teachers:
        print("❌ NO MATCHING TEACHERS FOUND")
        print("This suggests the session data doesn't match current database state")
    
    # Check which programs these classes belong to
    print(f"\n🔍 PROGRAM MAPPING ANALYSIS FOR SCREENSHOT CLASSES...")
    
    program_distribution = {
        'CORE': [],
        'ASCENT': [],
        'EDGE': [],
        'PINNACLE': [],
        'UNMAPPED': []
    }
    
    for class_code in screenshot_classes:
        curriculum = CLASS_CODE_CURRICULUM_MAPPING.get(class_code, '')
        if 'CORE' in curriculum:
            program_distribution['CORE'].append(class_code)
        elif 'ASCENT' in curriculum:
            program_distribution['ASCENT'].append(class_code)
        elif 'EDGE' in curriculum:
            program_distribution['EDGE'].append(class_code)
        elif 'PINNACLE' in curriculum:
            program_distribution['PINNACLE'].append(class_code)
        else:
            program_distribution['UNMAPPED'].append(class_code)
    
    print("Program distribution of screenshot classes:")
    for program, classes in program_distribution.items():
        if classes:
            print(f"   {program}: {classes} ({len(classes)} classes)")
    
    # Debug the specific view logic that creates programs_data
    print(f"\n🔍 SIMULATING VIEW LOGIC FOR programs_data GENERATION...")
    
    if matching_teachers:
        # Take the first matching teacher (should be the current user)
        current_teacher_data = matching_teachers[0]
        teacher = current_teacher_data['teacher']
        
        print(f"Simulating for teacher: {teacher.name}")
        
        # Get assignments like the view does
        my_assignments = TeacherClassAssignment.objects.filter(teacher=teacher, is_active=True)
        my_class_codes = [a.class_code for a in my_assignments]
        
        print(f"my_assignments count: {len(my_assignments)}")
        print(f"my_class_codes: {sorted(my_class_codes)}")
        
        # Build PROGRAM_MAPPING like the view does
        PROGRAM_MAPPING = {
            'CORE': [],
            'ASCENT': [],
            'EDGE': [],
            'PINNACLE': []
        }
        
        for code, curriculum in CLASS_CODE_CURRICULUM_MAPPING.items():
            if 'CORE' in curriculum:
                PROGRAM_MAPPING['CORE'].append(code)
            elif 'ASCENT' in curriculum:
                PROGRAM_MAPPING['ASCENT'].append(code)
            elif 'EDGE' in curriculum:
                PROGRAM_MAPPING['EDGE'].append(code)
            elif 'PINNACLE' in curriculum:
                PROGRAM_MAPPING['PINNACLE'].append(code)
        
        # Simulate the programs_data building logic
        programs_data = []
        
        for program_name in ['CORE', 'ASCENT', 'EDGE', 'PINNACLE']:
            program_classes = []
            
            # This is the key loop from the view
            for assignment in my_assignments:
                if assignment.class_code in PROGRAM_MAPPING[program_name]:
                    print(f"   Adding {assignment.class_code} to {program_name} program")
                    program_classes.append({
                        'class_code': assignment.class_code,
                        'program': program_name
                    })
            
            # Only add program if it has classes (this is the key condition)
            if program_classes:
                programs_data.append({
                    'name': program_name,
                    'classes': program_classes
                })
                print(f"✅ {program_name} program added with {len(program_classes)} classes")
            else:
                print(f"❌ {program_name} program SKIPPED - no classes")
        
        print(f"\nFinal programs_data count: {len(programs_data)}")
        
        if len(programs_data) == 0:
            print("\n🚨 ROOT CAUSE IDENTIFIED:")
            print("   programs_data is empty, which causes 'No classes available to display'")
            print("   This happens when none of the teacher's classes map to CORE/ASCENT/EDGE/PINNACLE")
            
            # Check what the unmapped classes are
            unmapped = program_distribution['UNMAPPED']
            if unmapped:
                print(f"   UNMAPPED CLASSES: {unmapped}")
                print("   These classes are not in the curriculum mapping!")
        else:
            print("✅ programs_data should be populated - view should work")
    
    return matching_teachers

def main():
    matching_teachers = debug_session_issue()
    
    print("\n" + "="*60)
    print("DEBUGGING SUMMARY")
    print("="*60)
    
    if matching_teachers:
        print(f"Found {len(matching_teachers)} teachers matching screenshot")
        for match in matching_teachers:
            teacher = match['teacher']
            if match['exact_match']:
                print(f"✅ {teacher.name} ({teacher.user.username}) - EXACT MATCH")
            else:
                print(f"⚠️  {teacher.name} ({teacher.user.username}) - PARTIAL MATCH")
    else:
        print("❌ No matching teachers found - session/database mismatch")
    
    return len(matching_teachers) > 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
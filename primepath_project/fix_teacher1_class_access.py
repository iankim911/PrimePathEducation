#!/usr/bin/env python
"""
Fix Teacher1 Class Access - COMPREHENSIVE SOLUTION
==================================================

Now that we found the actual teacher1 record:
- Name: "Taehyun Kim" 
- Username: "teacher1"
- Has 11 TeacherClassAssignment records
- Has 0 Class.assigned_teachers relationships

This script will synchronize the systems to fix the "No classes available" issue.

Author: Claude Code Agent System
Date: August 25, 2025
"""

import os
import sys
import django
from django.db import transaction

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from core.models import Teacher
from primepath_routinetest.models import TeacherClassAssignment, Class
from primepath_routinetest.class_code_mapping import CLASS_CODE_CURRICULUM_MAPPING

def main():
    print("="*80)
    print("FIXING TEACHER1 CLASS ACCESS ISSUE")
    print("="*80)
    
    # Get the actual teacher1 record
    teacher = Teacher.objects.get(user__username='teacher1')  # This is "Taehyun Kim"
    print(f"Found teacher: {teacher.name} (username: {teacher.user.username})")
    
    # Analyze current state
    tca_assignments = TeacherClassAssignment.objects.filter(teacher=teacher, is_active=True)
    class_assignments = Class.objects.filter(is_active=True, assigned_teachers=teacher)
    
    print(f"TeacherClassAssignment records: {tca_assignments.count()}")
    print(f"Class.assigned_teachers records: {class_assignments.count()}")
    
    # Get class codes that need to be synchronized
    tca_class_codes = set(tca_assignments.values_list('class_code', flat=True))
    class_sections = set(class_assignments.values_list('section', flat=True))
    
    missing_in_class_system = tca_class_codes - class_sections
    
    print(f"\nClasses missing from Class.assigned_teachers system: {len(missing_in_class_system)}")
    print("Missing classes:")
    for class_code in list(missing_in_class_system)[:10]:  # Show first 10
        print(f"  - {class_code}")
    
    if len(missing_in_class_system) > 10:
        print(f"  ... and {len(missing_in_class_system) - 10} more")
    
    # Ask for confirmation
    print(f"\n🔧 READY TO SYNCHRONIZE {len(missing_in_class_system)} CLASS ASSIGNMENTS")
    
    response = input("Proceed with synchronization? (yes/no): ").lower().strip()
    
    if response != 'yes':
        print("Synchronization cancelled.")
        return
    
    # Perform synchronization
    print("\n" + "="*60)
    print("STARTING SYNCHRONIZATION")
    print("="*60)
    
    created_classes = 0
    synchronized_assignments = 0
    errors = 0
    
    with transaction.atomic():
        for class_code in missing_in_class_system:
            try:
                # Try to find existing class
                existing_class = Class.objects.filter(section=class_code, is_active=True).first()
                
                if existing_class:
                    # Add teacher to existing class
                    existing_class.assigned_teachers.add(teacher)
                    existing_class.save()
                    
                    print(f"✓ Added teacher to existing class: {class_code}")
                    synchronized_assignments += 1
                    
                else:
                    # Create new class if it doesn't exist and we know about it
                    if class_code in CLASS_CODE_CURRICULUM_MAPPING:
                        # Parse class code
                        if '_' in class_code:
                            parts = class_code.split('_')
                            grade_level = parts[0].title()
                            section = '_'.join(parts[1:]) if len(parts) > 2 else parts[1]
                        else:
                            grade_level = class_code
                            section = class_code
                        
                        class_name = f"{grade_level} {section}"
                        
                        new_class = Class.objects.create(
                            name=class_name,
                            grade_level=grade_level,
                            section=class_code,  # Use full class_code as section for mapping
                            academic_year='2024-2025',
                            is_active=True
                        )
                        new_class.assigned_teachers.add(teacher)
                        new_class.save()
                        
                        print(f"✓ Created new class and assigned teacher: {class_code} -> {class_name}")
                        created_classes += 1
                        synchronized_assignments += 1
                        
                    else:
                        print(f"⚠ Skipped unknown class code: {class_code}")
                        
            except Exception as e:
                print(f"✗ Error processing {class_code}: {str(e)}")
                errors += 1
    
    print("\n" + "="*60)
    print("SYNCHRONIZATION COMPLETE")
    print("="*60)
    print(f"Classes created: {created_classes}")
    print(f"Assignments synchronized: {synchronized_assignments}")
    print(f"Errors: {errors}")
    
    # Verify the fix
    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60)
    
    # Re-check the counts
    final_tca_count = TeacherClassAssignment.objects.filter(teacher=teacher, is_active=True).count()
    final_class_count = Class.objects.filter(is_active=True, assigned_teachers=teacher).count()
    
    print(f"Final TeacherClassAssignment count: {final_tca_count}")
    print(f"Final Class.assigned_teachers count: {final_class_count}")
    
    if final_class_count > 0:
        synchronization_rate = (final_class_count / final_tca_count) * 100
        print(f"Synchronization rate: {synchronization_rate:.1f}%")
        
        if synchronization_rate >= 90:
            print(f"\n🎉 SUCCESS: Class access issue has been RESOLVED!")
            print(f"Teacher {teacher.name} should now see their classes in the Class Management interface.")
            print(f"\nNext steps:")
            print(f"1. Test the Class Management interface at the URL shown in screenshot 2")
            print(f"2. Verify that classes are now visible")
            print(f"3. Check that teacher can access class details and management features")
        else:
            print(f"\n⚠ PARTIAL SUCCESS: {synchronization_rate:.1f}% synchronized")
            print("Some assignments may still be missing. Manual review recommended.")
    else:
        print(f"\n❌ SYNCHRONIZATION FAILED: No Class.assigned_teachers relationships created")
        print("Please check the error messages above and database constraints.")

if __name__ == '__main__':
    main()
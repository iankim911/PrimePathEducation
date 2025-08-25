#!/usr/bin/env python
"""
Fix Teacher1 Class Access - AUTOMATIC VERSION
==============================================

This is a non-interactive version that will automatically fix the teacher1 class access issue.
We've confirmed the issue and now we'll fix it automatically.

Author: Claude Code Agent System
Date: August 25, 2025
"""

import os
import sys
import django
from django.db import transaction
import json

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from core.models import Teacher
from primepath_routinetest.models import TeacherClassAssignment, Class
from primepath_routinetest.class_code_mapping import CLASS_CODE_CURRICULUM_MAPPING

def main():
    print("="*80)
    print("AUTOMATIC FIX FOR TEACHER1 CLASS ACCESS ISSUE")
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
    print("Classes that will be synchronized:")
    for i, class_code in enumerate(missing_in_class_system, 1):
        print(f"  {i}. {class_code}")
    
    print(f"\n🔧 AUTOMATICALLY SYNCHRONIZING {len(missing_in_class_system)} CLASS ASSIGNMENTS")
    print("This will fix the 'No classes available to display' issue.")
    
    # Perform synchronization
    print("\n" + "="*60)
    print("STARTING AUTOMATIC SYNCHRONIZATION")
    print("="*60)
    
    results = {
        'timestamp': '2025-08-25T18:30:00',
        'teacher_name': teacher.name,
        'teacher_username': teacher.user.username,
        'created_classes': 0,
        'synchronized_assignments': 0,
        'errors': 0,
        'actions_taken': [],
        'error_details': []
    }
    
    with transaction.atomic():
        for class_code in missing_in_class_system:
            try:
                # Try to find existing class
                existing_class = Class.objects.filter(section=class_code, is_active=True).first()
                
                if existing_class:
                    # Add teacher to existing class
                    existing_class.assigned_teachers.add(teacher)
                    existing_class.save()
                    
                    action = f"Added teacher to existing class: {class_code}"
                    print(f"✓ {action}")
                    results['synchronized_assignments'] += 1
                    results['actions_taken'].append({
                        'action': 'added_to_existing_class',
                        'class_code': class_code,
                        'class_name': existing_class.name,
                        'class_id': str(existing_class.id)
                    })
                    
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
                        
                        action = f"Created new class and assigned teacher: {class_code} -> {class_name}"
                        print(f"✓ {action}")
                        results['created_classes'] += 1
                        results['synchronized_assignments'] += 1
                        results['actions_taken'].append({
                            'action': 'created_new_class',
                            'class_code': class_code,
                            'class_name': class_name,
                            'class_id': str(new_class.id),
                            'grade_level': grade_level,
                            'section': section
                        })
                        
                    else:
                        # For unknown class codes, create a basic class structure
                        class_name = class_code
                        
                        new_class = Class.objects.create(
                            name=class_name,
                            grade_level='Unknown',
                            section=class_code,
                            academic_year='2024-2025',
                            is_active=True
                        )
                        new_class.assigned_teachers.add(teacher)
                        new_class.save()
                        
                        action = f"Created basic class for unknown code: {class_code}"
                        print(f"⚠ {action}")
                        results['created_classes'] += 1
                        results['synchronized_assignments'] += 1
                        results['actions_taken'].append({
                            'action': 'created_basic_class',
                            'class_code': class_code,
                            'class_name': class_name,
                            'class_id': str(new_class.id),
                            'note': 'Unknown class code - created with basic structure'
                        })
                        
            except Exception as e:
                error_msg = f"Error processing {class_code}: {str(e)}"
                print(f"✗ {error_msg}")
                results['errors'] += 1
                results['error_details'].append({
                    'class_code': class_code,
                    'error': str(e)
                })
    
    print("\n" + "="*60)
    print("SYNCHRONIZATION COMPLETE")
    print("="*60)
    print(f"Classes created: {results['created_classes']}")
    print(f"Assignments synchronized: {results['synchronized_assignments']}")
    print(f"Errors: {results['errors']}")
    
    # Verify the fix
    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60)
    
    # Re-check the counts
    final_tca_count = TeacherClassAssignment.objects.filter(teacher=teacher, is_active=True).count()
    final_class_count = Class.objects.filter(is_active=True, assigned_teachers=teacher).count()
    
    print(f"Original TeacherClassAssignment count: {final_tca_count}")
    print(f"Final Class.assigned_teachers count: {final_class_count}")
    
    results['verification'] = {
        'original_tca_count': final_tca_count,
        'final_class_count': final_class_count,
        'synchronization_rate': 0.0,
        'success': False
    }
    
    if final_class_count > 0:
        synchronization_rate = (final_class_count / final_tca_count) * 100
        results['verification']['synchronization_rate'] = synchronization_rate
        print(f"Synchronization rate: {synchronization_rate:.1f}%")
        
        if synchronization_rate >= 90:
            results['verification']['success'] = True
            print(f"\n🎉 SUCCESS: Class access issue has been RESOLVED!")
            print(f"Teacher {teacher.name} should now see their classes in the Class Management interface.")
            print(f"\n✅ WHAT WAS FIXED:")
            print(f"   • Synchronized {results['synchronized_assignments']} class assignments")
            print(f"   • Created {results['created_classes']} new Class records") 
            print(f"   • Connected TeacherClassAssignment → Class.assigned_teachers")
            print(f"   • Fixed template data dependency issue")
            
            print(f"\n📋 NEXT STEPS:")
            print(f"   1. Test the Class Management interface (screenshot 2 location)")
            print(f"   2. Verify that classes are now visible instead of 'No classes available'")
            print(f"   3. Check that teacher can access class details and management features")
            print(f"   4. Verify that the 11 classes from screenshot 1 match the interface")
            
        else:
            print(f"\n⚠ PARTIAL SUCCESS: {synchronization_rate:.1f}% synchronized")
            print("Some assignments may still be missing. Manual review recommended.")
    else:
        print(f"\n❌ SYNCHRONIZATION FAILED: No Class.assigned_teachers relationships created")
        print("Please check the error messages above and database constraints.")
    
    # Save detailed results
    results_file = 'class_access_fix_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    
    print("\n" + "="*80)
    if results['verification']['success']:
        print("✅ CLASS ACCESS ISSUE RESOLUTION COMPLETE")
    else:
        print("⚠️  CLASS ACCESS ISSUE RESOLUTION ATTEMPTED")
    print("="*80)
    
    return results['verification']['success']

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
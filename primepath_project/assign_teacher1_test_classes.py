#!/usr/bin/env python
"""
Assign teacher1 to test classes for QC purposes
This script assigns teacher1 to two subprograms across different programs:
- CORE Phonics Level 2 (PRIMARY_2A)
- EDGE Rise Level 1 (MIDDLE_7A)

Run this script from the Django shell:
python manage.py shell < assign_teacher1_test_classes.py
"""

import os
import sys
import django
from datetime import datetime
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from core.models import Teacher
from primepath_routinetest.models import TeacherClassAssignment

def assign_teacher1_test_classes():
    """Assign teacher1 to specific test classes"""
    
    print("\n" + "="*80)
    print("ASSIGNING TEACHER1 TO TEST CLASSES FOR QC")
    print("="*80)
    
    # Get teacher1 user
    try:
        teacher1_user = User.objects.get(username='teacher1')
        print(f"✓ Found user: teacher1 (ID: {teacher1_user.id})")
    except User.DoesNotExist:
        print("✗ ERROR: User 'teacher1' not found!")
        print("Please create teacher1 user first.")
        return False
    
    # Get or create teacher profile
    try:
        teacher1_profile = Teacher.objects.get(user=teacher1_user)
        print(f"✓ Found teacher profile: {teacher1_profile.name} (ID: {teacher1_profile.id})")
    except Teacher.DoesNotExist:
        # Create teacher profile
        teacher1_profile = Teacher.objects.create(
            user=teacher1_user,
            name=teacher1_user.get_full_name() or "Teacher One",
            email=teacher1_user.email or "teacher1@example.com",
            is_head_teacher=False
        )
        print(f"✓ Created teacher profile: {teacher1_profile.name} (ID: {teacher1_profile.id})")
    
    # Define test class assignments
    test_assignments = [
        {
            'class_code': 'PRIMARY_2A',
            'access_level': 'FULL',
            'notes': 'QC Test: CORE Phonics Level 2 - Primary Grade 2A'
        },
        {
            'class_code': 'MIDDLE_7A',
            'access_level': 'FULL',
            'notes': 'QC Test: EDGE Rise Level 1 - Middle School Grade 7A'
        }
    ]
    
    print("\n" + "-"*40)
    print("CREATING CLASS ASSIGNMENTS:")
    print("-"*40)
    
    created_count = 0
    updated_count = 0
    
    for assignment_data in test_assignments:
        # Check if assignment already exists
        existing = TeacherClassAssignment.objects.filter(
            teacher=teacher1_profile,
            class_code=assignment_data['class_code']
        ).first()
        
        if existing:
            # Update existing assignment
            existing.access_level = assignment_data['access_level']
            existing.is_active = True
            existing.notes = assignment_data['notes']
            existing.save()
            
            print(f"↻ Updated: {assignment_data['class_code']} - {assignment_data['access_level']}")
            updated_count += 1
        else:
            # Create new assignment
            assignment = TeacherClassAssignment.objects.create(
                teacher=teacher1_profile,
                class_code=assignment_data['class_code'],
                access_level=assignment_data['access_level'],
                notes=assignment_data['notes'],
                is_active=True
            )
            
            print(f"✓ Created: {assignment_data['class_code']} - {assignment_data['access_level']}")
            print(f"  Display: {assignment.get_class_code_display()}")
            print(f"  Notes: {assignment_data['notes']}")
            created_count += 1
    
    # Display summary
    print("\n" + "="*80)
    print("ASSIGNMENT SUMMARY")
    print("="*80)
    
    # Get all active assignments for teacher1
    all_assignments = TeacherClassAssignment.objects.filter(
        teacher=teacher1_profile,
        is_active=True
    ).order_by('class_code')
    
    print(f"\nTeacher: {teacher1_profile.name}")
    print(f"Username: {teacher1_user.username}")
    print(f"Total Active Class Assignments: {all_assignments.count()}")
    print("\nActive Class Assignments:")
    print("-"*40)
    
    for assignment in all_assignments:
        print(f"  • {assignment.get_class_code_display()}")
        print(f"    Code: {assignment.class_code}")
        print(f"    Access: {assignment.get_access_level_display()}")
        if assignment.notes:
            print(f"    Notes: {assignment.notes}")
        print()
    
    # Log results
    log_data = {
        "action": "assign_teacher1_test_classes",
        "teacher": teacher1_profile.name,
        "user": teacher1_user.username,
        "created": created_count,
        "updated": updated_count,
        "total_active": all_assignments.count(),
        "assignments": [
            {
                "class_code": a.class_code,
                "access_level": a.access_level,
                "display_name": a.get_class_code_display()
            }
            for a in all_assignments
        ],
        "timestamp": datetime.now().isoformat()
    }
    
    print("\n" + "="*80)
    print("LOG DATA (JSON):")
    print("="*80)
    print(json.dumps(log_data, indent=2))
    
    print("\n" + "="*80)
    print("✓ TEACHER1 TEST CLASS ASSIGNMENT COMPLETE")
    print("="*80)
    print("\nTeacher1 can now:")
    print("1. Create exams for PRIMARY_2A and MIDDLE_7A")
    print("2. Edit/delete exams they create")
    print("3. View exams in these classes")
    print("4. Test cross-program functionality")
    print("\n")
    
    return True

if __name__ == "__main__":
    success = assign_teacher1_test_classes()
    if not success:
        sys.exit(1)
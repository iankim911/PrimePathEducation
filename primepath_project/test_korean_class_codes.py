#!/usr/bin/env python
"""
Test script to verify Korean curriculum class codes are being used
"""
import os
import sys
import django

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from primepath_routinetest.models import TeacherClassAssignment, ClassAccessRequest
from primepath_routinetest.class_code_mapping import CLASS_CODE_CURRICULUM_MAPPING
from core.models import Teacher
from django.contrib.auth.models import User

print("=" * 80)
print("KOREAN CURRICULUM CLASS CODES VERIFICATION")
print("=" * 80)

# Check the available class codes
print("\n1. ACTUAL KOREAN CURRICULUM CLASS CODES:")
print("-" * 40)
for code, curriculum in list(CLASS_CODE_CURRICULUM_MAPPING.items())[:10]:
    print(f"   {code:20} -> {curriculum}")
print(f"   ... and {len(CLASS_CODE_CURRICULUM_MAPPING) - 10} more codes")

# Check model choices
print("\n2. MODEL CLASS CODE CHOICES:")
print("-" * 40)
from primepath_routinetest.models.class_access import CLASS_CODE_CHOICES
print(f"   Total choices: {len(CLASS_CODE_CHOICES)}")
for code, display in CLASS_CODE_CHOICES[:5]:
    print(f"   {code:20} -> {display}")
print(f"   ... and {len(CLASS_CODE_CHOICES) - 5} more choices")

# Check if any assignments exist with old fake codes
print("\n3. CHECKING FOR OLD FAKE CLASS CODES IN DATABASE:")
print("-" * 40)
fake_codes = ['PRIMARY_1A', 'PRIMARY_1B', 'MIDDLE_7A', 'HIGH_10A']
for fake_code in fake_codes:
    assignments = TeacherClassAssignment.objects.filter(class_code=fake_code).count()
    requests = ClassAccessRequest.objects.filter(class_code=fake_code).count()
    print(f"   {fake_code}: {assignments} assignments, {requests} requests")

# Check current valid assignments
print("\n4. CURRENT VALID CLASS ASSIGNMENTS:")
print("-" * 40)
valid_assignments = TeacherClassAssignment.objects.filter(
    class_code__in=CLASS_CODE_CURRICULUM_MAPPING.keys()
)[:5]
if valid_assignments:
    for assignment in valid_assignments:
        print(f"   Teacher: {assignment.teacher.name}")
        print(f"   Class: {assignment.class_code} - {CLASS_CODE_CURRICULUM_MAPPING.get(assignment.class_code, 'Unknown')}")
        print(f"   Access: {assignment.get_access_level_display()}")
        print()
else:
    print("   No valid assignments found")

# Test creating a new assignment with Korean class code
print("\n5. TEST CREATING NEW ASSIGNMENT WITH KOREAN CLASS CODE:")
print("-" * 40)
try:
    # Get or create a test teacher
    test_user, _ = User.objects.get_or_create(
        username='test_teacher',
        defaults={'email': 'test@example.com'}
    )
    test_teacher, _ = Teacher.objects.get_or_create(
        user=test_user,
        defaults={'email': 'test@example.com', 'name': 'Test Teacher'}
    )
    
    # Try to create assignment with Korean class code
    test_class_code = 'PS1'  # CORE Phonics Level 1
    assignment, created = TeacherClassAssignment.objects.get_or_create(
        teacher=test_teacher,
        class_code=test_class_code,
        defaults={'access_level': 'VIEW'}
    )
    
    if created:
        print(f"   ✅ Successfully created assignment for class: {test_class_code}")
        print(f"   Display name: {assignment.get_class_code_display()}")
        # Clean up
        assignment.delete()
    else:
        print(f"   Assignment already exists for {test_class_code}")
        
except Exception as e:
    print(f"   ❌ Error creating assignment: {e}")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
#!/usr/bin/env python
"""
Clean up all test/made-up classes from the system.
Keep only the PrimePath curriculum classes.
"""

import os
import sys
import django
from django.db import transaction

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from primepath_routinetest.models.class_model import Class
from primepath_routinetest.class_code_mapping import CLASS_CODE_CURRICULUM_MAPPING

print("=" * 80)
print("CLASS CLEANUP UTILITY")
print("=" * 80)

# Get all valid PrimePath class codes
valid_class_codes = set(CLASS_CODE_CURRICULUM_MAPPING.keys())
print(f"\nValid PrimePath class codes: {len(valid_class_codes)}")
print(f"Examples: {list(valid_class_codes)[:5]}")

# Find all classes in the database
all_classes = Class.objects.all()
print(f"\nTotal classes in database: {all_classes.count()}")

# Identify classes to delete (not in PrimePath curriculum)
classes_to_delete = []
classes_to_keep = []

for cls in all_classes:
    # Check if the section code is a valid PrimePath code
    if cls.section and cls.section in valid_class_codes:
        classes_to_keep.append(cls)
    else:
        classes_to_delete.append(cls)

print(f"\nClasses to DELETE: {len(classes_to_delete)}")
print(f"Classes to KEEP: {len(classes_to_keep)}")

if classes_to_delete:
    print("\n" + "-" * 40)
    print("CLASSES TO BE DELETED:")
    print("-" * 40)
    for cls in classes_to_delete:
        print(f"  ❌ {cls.section or 'NO_CODE'}: {cls.name}")
        # Show related data that would be affected
        enrollment_count = cls.enrollments.count() if hasattr(cls, 'enrollments') else 0
        if enrollment_count:
            print(f"     ⚠️  Has {enrollment_count} student enrollments")
        teacher_count = cls.assigned_teachers.count()
        if teacher_count:
            print(f"     ⚠️  Has {teacher_count} assigned teachers")

if classes_to_keep:
    print("\n" + "-" * 40)
    print("CLASSES TO BE KEPT (PrimePath Curriculum):")
    print("-" * 40)
    for cls in classes_to_keep[:10]:  # Show first 10
        curriculum = CLASS_CODE_CURRICULUM_MAPPING.get(cls.section, 'Unknown')
        print(f"  ✅ {cls.section}: {curriculum}")
    if len(classes_to_keep) > 10:
        print(f"  ... and {len(classes_to_keep) - 10} more")

# Ask for confirmation
print("\n" + "=" * 80)
print("⚠️  WARNING: This will permanently delete the identified classes!")
print("=" * 80)

response = input("\nDo you want to proceed with deletion? (yes/no): ")

if response.lower() == 'yes':
    try:
        with transaction.atomic():
            # Delete the classes
            deleted_count = 0
            for cls in classes_to_delete:
                cls_name = cls.name
                cls_section = cls.section
                cls.delete()
                deleted_count += 1
                print(f"  Deleted: {cls_section or 'NO_CODE'} - {cls_name}")
            
            print(f"\n✅ Successfully deleted {deleted_count} test classes")
            
            # Verify final state
            remaining_classes = Class.objects.all()
            print(f"\nFinal state:")
            print(f"  Total classes remaining: {remaining_classes.count()}")
            
            # Check all remaining are valid
            all_valid = True
            for cls in remaining_classes:
                if cls.section not in valid_class_codes:
                    print(f"  ⚠️  Warning: Non-curriculum class still exists: {cls.section} - {cls.name}")
                    all_valid = False
            
            if all_valid:
                print("  ✅ All remaining classes are valid PrimePath curriculum classes")
                
    except Exception as e:
        print(f"\n❌ Error during deletion: {str(e)}")
        print("No changes were made.")
else:
    print("\n❌ Deletion cancelled. No changes were made.")

print("\n" + "=" * 80)
print("Cleanup complete!")
print("=" * 80)
#!/usr/bin/env python
"""
Reassign teacher class assignments from old CLASS_ codes to PrimePath curriculum codes
"""

import os
import sys
import django
import random
from django.db import transaction

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from primepath_routinetest.models.class_model import Class
from primepath_routinetest.models import TeacherClassAssignment
from core.models import Teacher

print("=" * 80)
print("TEACHER CLASS ASSIGNMENT UPDATE")
print("=" * 80)

# Get all PrimePath classes
primepath_classes = Class.objects.filter(is_active=True).exclude(
    section__startswith='CLASS_'
).order_by('section')

if not primepath_classes.exists():
    print("ERROR: No PrimePath classes found!")
    sys.exit(1)

primepath_codes = list(primepath_classes.values_list('section', flat=True))
print(f"\nAvailable PrimePath classes: {len(primepath_codes)}")
print(f"Examples: {primepath_codes[:5]}")

# Get all assignments with old CLASS_ codes
old_assignments = TeacherClassAssignment.objects.filter(
    class_code__startswith='CLASS_'
)

print(f"\nFound {old_assignments.count()} assignments with old CLASS_ codes")

if old_assignments.exists():
    print("\nReassigning to PrimePath curriculum classes...")
    
    with transaction.atomic():
        # Group assignments by teacher to ensure variety
        teacher_assignments = {}
        for assignment in old_assignments:
            if assignment.teacher_id not in teacher_assignments:
                teacher_assignments[assignment.teacher_id] = []
            teacher_assignments[assignment.teacher_id].append(assignment)
        
        # For each teacher, assign random but unique PrimePath classes
        for teacher_id, assignments in teacher_assignments.items():
            # Get a shuffled list of classes for this teacher
            available_for_teacher = primepath_codes.copy()
            random.shuffle(available_for_teacher)
            
            for i, assignment in enumerate(assignments):
                # Use modulo to cycle through if more assignments than classes
                new_class_code = available_for_teacher[i % len(available_for_teacher)]
                old_code = assignment.class_code
                
                assignment.class_code = new_class_code
                assignment.save()
                
                print(f"  Teacher {assignment.teacher.name}: {old_code} -> {new_class_code}")
    
    print(f"\n✅ Successfully updated {old_assignments.count()} assignments")

# Also update any ExamScheduleMatrix entries
from primepath_routinetest.models import ExamScheduleMatrix

old_matrix_entries = ExamScheduleMatrix.objects.filter(
    class_code__startswith='CLASS_'
)

if old_matrix_entries.exists():
    print(f"\nFound {old_matrix_entries.count()} ExamScheduleMatrix entries with old codes")
    print("Updating matrix entries...")
    
    with transaction.atomic():
        for entry in old_matrix_entries:
            # Randomly assign a PrimePath class
            new_code = random.choice(primepath_codes)
            old_code = entry.class_code
            entry.class_code = new_code
            entry.save()
            print(f"  Matrix entry: {old_code} -> {new_code}")
    
    print(f"✅ Updated {old_matrix_entries.count()} matrix entries")

# Verify the results
print("\n" + "=" * 80)
print("VERIFICATION")
print("=" * 80)

remaining_old = TeacherClassAssignment.objects.filter(
    class_code__startswith='CLASS_'
).count()

if remaining_old == 0:
    print("✅ No more old CLASS_ codes in TeacherClassAssignment!")
else:
    print(f"⚠️  Still {remaining_old} old codes remaining")

# Show sample of new assignments
print("\nSample of updated assignments:")
sample_assignments = TeacherClassAssignment.objects.all()[:10]
for assignment in sample_assignments:
    print(f"  {assignment.teacher.name}: {assignment.class_code} ({assignment.access_level})")

print("\n" + "=" * 80)
print("✅ Teacher class assignments updated to PrimePath curriculum!")
print("=" * 80)
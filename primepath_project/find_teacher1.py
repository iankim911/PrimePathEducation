#!/usr/bin/env python
"""
Find Teacher1 - Debug Script
=============================

This script finds the actual teacher1 record and analyzes their assignments.
The diagnostic script couldn't find teacher1, so let's investigate.
"""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from core.models import Teacher
from primepath_routinetest.models import TeacherClassAssignment

print("=== FINDING TEACHER1 ===")

# Look for all teachers
teachers = Teacher.objects.all()
print(f"Total teachers in system: {teachers.count()}")

print("\nAll teachers:")
for teacher in teachers:
    print(f"  ID: {teacher.id}")
    print(f"  Name: '{teacher.name}'")
    print(f"  Username: '{teacher.user.username}'")
    print(f"  Email: '{teacher.user.email}'")
    
    # Check assignments
    assignments = TeacherClassAssignment.objects.filter(teacher=teacher, is_active=True)
    print(f"  Assignments: {assignments.count()}")
    
    if assignments.exists():
        print("  Classes:")
        for assignment in assignments[:5]:  # Show first 5
            print(f"    - {assignment.class_code} ({assignment.access_level})")
        if assignments.count() > 5:
            print(f"    ... and {assignments.count() - 5} more")
    
    print()

# Try specific searches for teacher1
print("=== SEARCHING FOR TEACHER1 ===")

# Search by name containing 'teacher1'
teachers_by_name = Teacher.objects.filter(name__icontains='teacher1')
print(f"Teachers with 'teacher1' in name: {teachers_by_name.count()}")
for t in teachers_by_name:
    print(f"  - {t.name} (username: {t.user.username})")

# Search by username containing 'teacher1' 
teachers_by_username = Teacher.objects.filter(user__username__icontains='teacher1')
print(f"Teachers with 'teacher1' in username: {teachers_by_username.count()}")
for t in teachers_by_username:
    print(f"  - {t.name} (username: {t.user.username})")

# Find teacher with most assignments (might be teacher1)
print("\n=== TEACHER WITH MOST ASSIGNMENTS ===")
teacher_assignments = []
for teacher in teachers:
    assignment_count = TeacherClassAssignment.objects.filter(teacher=teacher, is_active=True).count()
    teacher_assignments.append((teacher, assignment_count))

# Sort by assignment count
teacher_assignments.sort(key=lambda x: x[1], reverse=True)

print("Teachers by assignment count:")
for teacher, count in teacher_assignments:
    print(f"  {teacher.name} ({teacher.user.username}): {count} assignments")
    
# Show the teacher with 11 assignments (from screenshot)
for teacher, count in teacher_assignments:
    if count == 11:
        print(f"\n*** FOUND TEACHER WITH 11 ASSIGNMENTS ***")
        print(f"Name: '{teacher.name}'")
        print(f"Username: '{teacher.user.username}'")
        print(f"Email: '{teacher.user.email}'")
        print(f"ID: {teacher.id}")
        
        assignments = TeacherClassAssignment.objects.filter(teacher=teacher, is_active=True)
        print(f"\nAll {assignments.count()} assignments:")
        for assignment in assignments:
            print(f"  - {assignment.class_code} ({assignment.access_level}) - assigned {assignment.assigned_date}")
        break
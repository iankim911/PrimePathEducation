#\!/usr/bin/env python
"""
Final verification of the filter fix
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from primepath_routinetest.services.exam_service import ExamService
from primepath_routinetest.models import Exam, TeacherClassAssignment
from core.models import Teacher

print("=" * 60)
print("FILTER FIX VERIFICATION")
print("=" * 60)

# Get teacher1
teacher1_user = User.objects.get(username='teacher1')
teacher1 = Teacher.objects.get(user=teacher1_user)

print("\n1. TEACHER ASSIGNMENTS:")
print("-" * 40)
assignments = TeacherClassAssignment.objects.filter(teacher=teacher1, is_active=True)
for assignment in assignments:
    print(f"  Class: {assignment.get_class_code_display()} - Access: {assignment.access_level}")

# Check service directly
print("\n2. SERVICE FILTER TEST:")
print("-" * 40)
exams = Exam.objects.filter(is_active=True)

# Without filter
result_no_filter = ExamService.organize_exams_hierarchically(
    exams, teacher1_user, filter_assigned_only=False
)

# With filter
result_with_filter = ExamService.organize_exams_hierarchically(
    exams, teacher1_user, filter_assigned_only=True
)

# Count exams and VIEW ONLY
no_filter_total = 0
no_filter_view_only = []
for program in result_no_filter.values():
    for exam_list in program.values():
        for exam in exam_list:
            no_filter_total += 1
            if hasattr(exam, 'user_permission') and exam.user_permission == 'VIEW':
                no_filter_view_only.append(exam.name)

with_filter_total = 0
with_filter_view_only = []
for program in result_with_filter.values():
    for exam_list in program.values():
        for exam in exam_list:
            with_filter_total += 1
            if hasattr(exam, 'user_permission') and exam.user_permission == 'VIEW':
                with_filter_view_only.append(exam.name)

print(f"WITHOUT FILTER: {no_filter_total} exams total")
print(f"  - VIEW ONLY exams: {len(no_filter_view_only)}")
for exam_name in no_filter_view_only[:3]:  # Show first 3
    print(f"    • {exam_name}")

print(f"\nWITH FILTER: {with_filter_total} exams total")
print(f"  - VIEW ONLY exams: {len(with_filter_view_only)}")
for exam_name in with_filter_view_only[:3]:  # Show first 3
    print(f"    • {exam_name}")

print(f"\nFILTERED OUT: {no_filter_total - with_filter_total} exams")

# Test via HTTP
print("\n3. HTTP REQUEST TEST:")
print("-" * 40)
client = Client()
client.login(username='teacher1', password='teacher1')

response = client.get('/routinetest/exams/?assigned_only=true')
content = response.content.decode('utf-8')
view_only_count = content.count('VIEW ONLY')

print(f"URL: /routinetest/exams/?assigned_only=true")
print(f"VIEW ONLY badges found: {view_only_count}")

# Final verdict
print("\n" + "=" * 60)
print("VERDICT:")
print("=" * 60)
if len(with_filter_view_only) == 0 and len(no_filter_view_only) > 0:
    print("✅ SERVICE FILTER WORKS: Hides VIEW ONLY when filter is ON")
else:
    print(f"❌ SERVICE FILTER BROKEN: Still shows {len(with_filter_view_only)} VIEW ONLY exams")

if view_only_count == 0:
    print("✅ HTTP FILTER WORKS: No VIEW ONLY badges with ?assigned_only=true")
else:
    print(f"❌ HTTP FILTER BROKEN: Still shows {view_only_count} VIEW ONLY badges")

print("\nEXPECTED BEHAVIOR:")
print("  • Filter ON: Hide VIEW ONLY exams (teacher not truly assigned)")
print("  • Filter OFF: Show all exams including VIEW ONLY")
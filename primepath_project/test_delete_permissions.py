#!/usr/bin/env python3
"""Test delete permissions for teachers"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from core.models import Teacher
from primepath_routinetest.models import RoutineExam as Exam, TeacherClassAssignment
from primepath_routinetest.services.exam_service import ExamPermissionService

print("\n" + "="*80)
print("DELETE PERMISSION TESTING")
print("="*80 + "\n")

# Get all users and their teacher profiles
users = User.objects.all()
exams = Exam.objects.all()[:3]  # Test with first 3 exams

print(f"Testing with {len(exams)} exams\n")

for user in users:
    print(f"\n{'='*60}")
    print(f"User: {user.username}")
    print(f"  - is_superuser: {user.is_superuser}")
    print(f"  - is_staff: {user.is_staff}")
    
    # Check teacher profile
    teacher = None
    if hasattr(user, 'teacher_profile'):
        teacher = user.teacher_profile
        print(f"  - Teacher profile: {teacher.name}")
        print(f"  - Is head teacher: {teacher.is_head_teacher}")
        
        # Show class assignments
        assignments = TeacherClassAssignment.objects.filter(teacher=teacher, is_active=True)
        if assignments:
            print(f"  - Class assignments:")
            for a in assignments:
                print(f"      {a.get_class_code_display()} ({a.access_level})")
    else:
        print(f"  - No teacher profile")
    
    print(f"\n  Delete permissions for exams:")
    for exam in exams:
        can_delete = ExamPermissionService.can_teacher_delete_exam(user, exam)
        
        # Show why they can/cannot delete
        reasons = []
        if user.is_superuser or user.is_staff:
            reasons.append("ADMIN")
        if teacher and exam.created_by and exam.created_by.id == teacher.id:
            reasons.append("CREATOR")
        if teacher:
            teacher_assignments = ExamPermissionService.get_teacher_assignments(user)
            exam_classes = exam.class_codes if exam.class_codes else []
            for class_code in exam_classes:
                if class_code in teacher_assignments and teacher_assignments[class_code] == 'FULL':
                    reasons.append(f"FULL_ACCESS({class_code})")
                    break
        
        status = "✅ YES" if can_delete else "❌ NO"
        reason = f" ({', '.join(reasons)})" if reasons else ""
        print(f"    - {exam.name[:40]}: {status}{reason}")

print("\n" + "="*80)
print("PERMISSION LOGIC SUMMARY:")
print("="*80)
print("\nTeachers can DELETE an exam if ANY of these conditions are met:")
print("1. They are admin (is_superuser=True or is_staff=True)")
print("2. They created the exam (exam.created_by matches their teacher profile)")
print("3. They have FULL access to at least one of the exam's assigned classes")
print("\nTeachers can EDIT an exam if:")
print("- They are admin OR")
print("- They have FULL or CO_TEACHER access to at least one of the exam's classes")
print("\nTeachers can COPY an exam if:")
print("- They are admin OR")
print("- They have at least one class assignment (any access level)")
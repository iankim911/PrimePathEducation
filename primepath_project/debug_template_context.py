#!/usr/bin/env python
"""
Debug template context issue
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from core.models import Teacher
from primepath_student.models import StudentProfile
from django.db.models import Q, Count

def debug_template_context():
    print("=== DEBUGGING TEMPLATE CONTEXT ISSUE ===\n")
    
    # Get admin teacher
    admin_user = User.objects.get(username='admin')
    teacher = Teacher.objects.get(user=admin_user)
    
    print(f"Admin teacher: {teacher.name}")
    print(f"Is head teacher: {teacher.is_head_teacher}")
    
    # Execute the exact same logic as in the view
    if teacher.is_head_teacher:
        print("Executing head teacher logic...")
        students = StudentProfile.objects.all().select_related('user').annotate(
            class_count=Count('class_assignments', filter=Q(class_assignments__is_active=True))
        ).order_by('user__last_name')
    else:
        print("Should not reach here for admin")
        return
    
    print(f"\nQuerySet: {students}")
    print(f"QuerySet type: {type(students)}")
    print(f"QuerySet count: {students.count()}")
    
    # Force evaluation of queryset
    students_list = list(students)
    print(f"Evaluated list length: {len(students_list)}")
    
    # Check each student
    for i, student in enumerate(students_list):
        print(f"Student {i+1}: {student.user.get_full_name()} ({student.student_id}) - {student.class_count} classes")
        
    # Test the template context dictionary
    context = {
        'students': students,
        'is_head_teacher': teacher.is_head_teacher
    }
    
    print(f"\nContext keys: {list(context.keys())}")
    print(f"Context students type: {type(context['students'])}")
    print(f"Context is_head_teacher: {context['is_head_teacher']}")
    
    # Test template-style access
    print("\n=== TEMPLATE-STYLE ACCESS ===")
    template_students = context['students']
    print(f"template_students.count(): {template_students.count()}")
    print(f"template_students exists check: {bool(template_students)}")
    print(f"template_students.exists(): {template_students.exists()}")
    
    # Test iteration
    print("Iterating through template_students:")
    for student in template_students:
        print(f"  - {student.user.get_full_name() or student.user.username}")

if __name__ == "__main__":
    debug_template_context()
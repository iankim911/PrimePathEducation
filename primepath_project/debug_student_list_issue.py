#!/usr/bin/env python
"""
Debug script to identify why students don't show up in the student list
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from core.models import Teacher
from primepath_student.models import StudentProfile, StudentClassAssignment
from primepath_routinetest.models.class_access import TeacherClassAssignment
from django.db.models import Q, Count

def debug_student_list():
    print("=== DEBUGGING STUDENT LIST ISSUE ===\n")
    
    # Step 1: Check students exist
    print("1. STUDENTS IN DATABASE:")
    students = StudentProfile.objects.all()
    print(f"   Total students: {students.count()}")
    for s in students:
        print(f"   - {s.user.get_full_name() or s.user.username} ({s.student_id})")
    
    # Step 2: Check student class assignments
    print("\n2. STUDENT CLASS ASSIGNMENTS:")
    assignments = StudentClassAssignment.objects.filter(is_active=True)
    print(f"   Active assignments: {assignments.count()}")
    for a in assignments:
        print(f"   - {a.student.user.get_full_name()} -> {a.get_class_code_display()}")
    
    # Step 3: Check teacher1 access
    print("\n3. TEACHER1 ACCESS:")
    try:
        teacher1 = Teacher.objects.get(user__username='teacher1')
        print(f"   Name: {teacher1.name}")
        print(f"   Head Teacher: {teacher1.is_head_teacher}")
        
        teacher1_classes = TeacherClassAssignment.objects.filter(
            teacher=teacher1, is_active=True
        ).values_list('class_code', flat=True)
        print(f"   Classes: {list(teacher1_classes)}")
        
    except Teacher.DoesNotExist:
        print("   ERROR: teacher1 Teacher profile not found")
        return
    
    # Step 4: Simulate the view logic for teacher1
    print("\n4. SIMULATING VIEW LOGIC FOR TEACHER1:")
    
    if teacher1.is_head_teacher:
        print("   Logic: Head teacher - should see ALL students")
        query_students = StudentProfile.objects.all().select_related('user').annotate(
            class_count=Count('class_assignments', filter=Q(class_assignments__is_active=True))
        ).order_by('user__last_name')
    else:
        print("   Logic: Regular teacher - should see students in accessible classes")
        print(f"   Filtering by classes: {list(teacher1_classes)}")
        
        query_students = StudentProfile.objects.filter(
            class_assignments__class_code__in=teacher1_classes,
            class_assignments__is_active=True
        ).distinct().select_related('user').annotate(
            class_count=Count('class_assignments', filter=Q(class_assignments__is_active=True))
        ).order_by('user__last_name')
    
    print(f"   Query result count: {query_students.count()}")
    for s in query_students:
        print(f"   - {s.user.get_full_name()} ({s.student_id}) - {s.class_count} classes")
    
    # Step 5: Check for overlap
    print("\n5. OVERLAP ANALYSIS:")
    student_classes = set(StudentClassAssignment.objects.filter(
        is_active=True
    ).values_list('class_code', flat=True))
    
    print(f"   Students are in classes: {student_classes}")
    print(f"   Teacher1 has access to: {set(teacher1_classes)}")
    overlap = student_classes.intersection(set(teacher1_classes))
    print(f"   Overlap (students teacher1 should see): {overlap}")
    
    # Step 6: Conclusion
    print("\n6. CONCLUSION:")
    if query_students.count() > 0:
        print("   ✅ LOGIC IS CORRECT - Students should appear")
        print("   ❓ Issue might be in template rendering or browser session")
        print("\n   SUGGESTED FIXES:")
        print("   1. Clear browser cache and try again")
        print("   2. Login as 'admin' (head teacher) to see all students")
        print("   3. Make teacher1 a head teacher with the command below:")
        print("      python -c \"from core.models import Teacher; t=Teacher.objects.get(user__username='teacher1'); t.is_head_teacher=True; t.save()\"")
    else:
        print("   ❌ LOGIC ISSUE FOUND")
        if not student_classes:
            print("   - No students are assigned to classes")
        elif not overlap:
            print("   - Students and teacher1 have no class overlap")
        else:
            print("   - Unknown query issue")

if __name__ == "__main__":
    debug_student_list()
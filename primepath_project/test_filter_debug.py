#!/usr/bin/env python
"""
Debug script to test the filter logic directly
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from django.contrib.auth import get_user_model
from primepath_routinetest.models import RoutineExam as Exam, TeacherClassAssignment
from primepath_routinetest.services.exam_service import ExamService

User = get_user_model()

def test_filter():
    print("\n" + "="*80)
    print("FILTER DEBUG TEST")
    print("="*80)
    
    # Get teacher1
    teacher1 = User.objects.filter(username='teacher1').first()
    if not teacher1:
        print("ERROR: teacher1 not found")
        return
    
    print(f"\nTesting with user: {teacher1.username}")
    
    # Get teacher's assignments
    assignments = ExamService.get_teacher_assignments(teacher1)
    print(f"Teacher assignments: {dict(assignments)}")
    
    # Get the Toggle Testing exams
    toggle_exams = Exam.objects.filter(name__icontains='Toggle')
    print(f"\nFound {toggle_exams.count()} Toggle Testing exam(s)")
    
    for exam in toggle_exams:
        print(f"\nExam: {exam.name}")
        print(f"  Created by: {exam.created_by}")
        print(f"  Class codes: {exam.class_codes}")
        
        # Check ownership
        is_owner = False
        if hasattr(teacher1, 'teacher_profile') and exam.created_by:
            is_owner = exam.created_by.id == teacher1.teacher_profile.id
        print(f"  Teacher1 is owner: {is_owner}")
        
        # Check class assignments
        for class_code in exam.class_codes:
            if class_code in assignments:
                print(f"  Teacher has {assignments[class_code]} access to {class_code}")
            else:
                print(f"  Teacher has NO access to {class_code}")
    
    print("\n" + "-"*80)
    print("Testing filter_assigned_only=True (Should EXCLUDE VIEW ONLY)")
    print("-"*80)
    
    # Test with filter ON
    result = ExamService.organize_exams_hierarchically(
        toggle_exams,
        teacher1,
        filter_assigned_only=True
    )
    
    # Count exams in result
    total_exams = 0
    for program in result.values():
        for class_exams in program.values():
            total_exams += len(class_exams)
            for exam in class_exams:
                print(f"  SHOWN: {exam.name} - Badge: {exam.access_badge}")
    
    if total_exams == 0:
        print("  ✅ CORRECT: No Toggle Testing exams shown (VIEW access excluded)")
    else:
        print(f"  ❌ ERROR: {total_exams} exam(s) shown - should be 0!")
    
    print("\n" + "-"*80)
    print("Testing filter_assigned_only=False (Should INCLUDE VIEW ONLY)")
    print("-"*80)
    
    # Test with filter OFF
    result = ExamService.organize_exams_hierarchically(
        toggle_exams,
        teacher1,
        filter_assigned_only=False
    )
    
    # Count exams in result
    total_exams = 0
    for program in result.values():
        for class_exams in program.values():
            total_exams += len(class_exams)
            for exam in class_exams:
                print(f"  SHOWN: {exam.name} - Badge: {exam.access_badge}")
    
    if total_exams > 0:
        print(f"  ✅ CORRECT: {total_exams} exam(s) shown with VIEW ONLY badges")
    else:
        print(f"  ❌ ERROR: No exams shown - should show VIEW ONLY exams")

if __name__ == "__main__":
    test_filter()
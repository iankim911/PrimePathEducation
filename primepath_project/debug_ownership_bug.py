#!/usr/bin/env python
"""
Debug script to identify the ownership permission bug
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from core.models import Teacher
from primepath_routinetest.models import Exam
from primepath_routinetest.services.exam_service import ExamPermissionService

def debug_ownership_bug():
    print("\n" + "="*80)
    print("DEBUGGING OWNERSHIP PERMISSION BUG")
    print("="*80)
    
    # Get teacher1 user
    try:
        user = User.objects.get(username='teacher1')
        print(f"✅ Found user: {user.username}")
        print(f"   - is_superuser: {user.is_superuser}")
        print(f"   - is_staff: {user.is_staff}")
        print(f"   - has teacher_profile: {hasattr(user, 'teacher_profile')}")
        
        if hasattr(user, 'teacher_profile'):
            teacher = user.teacher_profile
            print(f"   - Teacher ID: {teacher.id}")
            print(f"   - Teacher name: {teacher.name}")
        else:
            print("   ❌ NO TEACHER PROFILE FOUND!")
            return
            
    except User.DoesNotExist:
        print("❌ User 'teacher1' not found!")
        return
    
    # Find Test Ownership Exam
    try:
        exam = Exam.objects.filter(name="Test Ownership Exam").first()
        if not exam:
            print("❌ No exam found with name 'Test Ownership Exam'")
            return
        print(f"\n✅ Found exam: {exam.name}")
        print(f"   - Exam ID: {exam.id}")
        print(f"   - Created by: {exam.created_by}")
        print(f"   - Created by ID: {exam.created_by.id if exam.created_by else 'None'}")
        print(f"   - Created by name: {exam.created_by.name if exam.created_by else 'None'}")
        print(f"   - Class codes: {exam.class_codes}")
        
    except Exam.DoesNotExist:
        print("❌ Exam 'Test Ownership Exam' not found!")
        return
    
    # Compare IDs
    print(f"\n🔍 OWNERSHIP COMPARISON:")
    if exam.created_by:
        print(f"   - exam.created_by.id = {exam.created_by.id} (type: {type(exam.created_by.id)})")
        print(f"   - teacher.id = {teacher.id} (type: {type(teacher.id)})")
        print(f"   - IDs match: {exam.created_by.id == teacher.id}")
        print(f"   - String comparison: '{exam.created_by.id}' == '{teacher.id}' = {str(exam.created_by.id) == str(teacher.id)}")
    else:
        print("   ❌ exam.created_by is None!")
    
    # Test permission service
    print(f"\n🧪 TESTING PERMISSION SERVICE:")
    can_delete = ExamPermissionService.can_teacher_delete_exam(user, exam)
    print(f"   - can_teacher_delete_exam result: {can_delete}")
    
    # Test class-based permissions  
    from primepath_routinetest.services.exam_service import ExamService
    assignments = ExamService.get_teacher_assignments(user)
    print(f"\n📚 TEACHER ASSIGNMENTS:")
    print(f"   - Teacher assignments: {assignments}")
    
    if exam.class_codes:
        print(f"   - Exam classes: {exam.class_codes}")
        for class_code in exam.class_codes:
            if class_code in assignments:
                access_level = assignments[class_code]
                print(f"   - Class {class_code}: {access_level} access")
                if access_level == 'FULL':
                    print(f"     ✅ FULL access should allow delete")
                else:
                    print(f"     ❌ {access_level} access not sufficient for delete")
            else:
                print(f"   - Class {class_code}: NO ACCESS")
    
    # Manual ownership check
    print(f"\n🔧 MANUAL OWNERSHIP CHECK:")
    if exam.created_by and hasattr(user, 'teacher_profile'):
        teacher_profile = user.teacher_profile
        is_owner = exam.created_by.id == teacher_profile.id
        print(f"   - Manual ownership check: {is_owner}")
        
        if is_owner:
            print("   ✅ Teacher IS the owner - should have delete permission")
        else:
            print("   ❌ Teacher is NOT the owner")
            print(f"      Owner ID: {exam.created_by.id}")
            print(f"      Teacher ID: {teacher_profile.id}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    debug_ownership_bug()
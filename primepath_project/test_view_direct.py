#!/usr/bin/env python
"""
Test the delete view function directly to isolate the bug
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from primepath_routinetest.models import RoutineExam as Exam
from primepath_routinetest.services.exam_service import ExamPermissionService
from django.test import RequestFactory
import logging

# Set up logging to see the debug messages
logging.basicConfig(level=logging.DEBUG)

def test_view_logic_directly():
    print("\n" + "="*80)
    print("TESTING DELETE VIEW LOGIC DIRECTLY")
    print("="*80)
    
    # Get test data
    user = User.objects.get(username='teacher1')
    exam = Exam.objects.filter(name="Test Ownership Exam").first()
    
    print(f"User: {user.username}")
    print(f"Exam: {exam.name} (ID: {exam.id})")
    
    # Simulate the view logic step by step
    print(f"\n🔍 STEP-BY-STEP VIEW SIMULATION:")
    
    # Step 1: Admin check (from line 823)
    is_admin = user.is_superuser or user.is_staff
    print(f"1. is_admin = {is_admin}")
    
    if not is_admin:
        print("2. Not admin, checking teacher permissions...")
        
        # Step 2: Teacher profile check (from line 827)
        teacher_profile = getattr(user, 'teacher_profile', None)
        print(f"3. teacher_profile = {teacher_profile}")
        
        if not teacher_profile:
            print("4. ❌ No teacher profile - would return error")
            return
        else:
            print(f"4. ✅ Teacher profile found: {teacher_profile.name}")
        
        # Step 3: Permission service check (from line 837)
        print(f"5. Calling ExamPermissionService.can_teacher_delete_exam...")
        can_delete = ExamPermissionService.can_teacher_delete_exam(user, exam)
        print(f"6. can_delete = {can_delete}")
        
        # Step 4: The critical if statement (from line 845)
        print(f"7. Checking 'if not can_delete': {not can_delete}")
        
        if not can_delete:
            print("8. ❌ ENTERING PERMISSION DENIAL BLOCK - THIS IS THE BUG!")
            print("   This should NOT happen since can_delete is True")
        else:
            print("8. ✅ SKIPPING PERMISSION DENIAL BLOCK - Permission granted!")
            print("   Proceeding to actual deletion...")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    test_view_logic_directly()
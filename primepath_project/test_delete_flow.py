#!/usr/bin/env python
"""
Test the exact delete flow to identify where the bug is happening
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
from django.test import RequestFactory, Client
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.urls import reverse

def test_delete_flow():
    print("\n" + "="*80)
    print("TESTING DELETE FLOW STEP BY STEP")
    print("="*80)
    
    # Get test data
    user = User.objects.get(username='teacher1')
    exam = Exam.objects.filter(name="Test Ownership Exam").first()
    
    print(f"User: {user.username}")
    print(f"Exam: {exam.name} (ID: {exam.id})")
    
    # Test 1: Service permission check
    print(f"\n1️⃣ SERVICE PERMISSION CHECK:")
    can_delete_service = ExamPermissionService.can_teacher_delete_exam(user, exam)
    print(f"   ✅ Service result: {can_delete_service}")
    
    # Test 2: Admin check
    print(f"\n2️⃣ ADMIN CHECK:")
    is_admin = user.is_superuser or user.is_staff
    print(f"   Admin status: {is_admin}")
    
    # Test 3: Teacher profile check
    print(f"\n3️⃣ TEACHER PROFILE CHECK:")
    teacher_profile = getattr(user, 'teacher_profile', None)
    print(f"   Has teacher profile: {teacher_profile is not None}")
    if teacher_profile:
        print(f"   Teacher ID: {teacher_profile.id}")
        print(f"   Teacher name: {teacher_profile.name}")
    
    # Test 4: Manual HTTP request simulation
    print(f"\n4️⃣ HTTP REQUEST SIMULATION:")
    
    # Create a test client and login
    client = Client()
    login_success = client.login(username='teacher1', password='password')
    print(f"   Login success: {login_success}")
    
    if login_success:
        # Make a DELETE request to the delete view
        print(f"   Making DELETE request to /RoutineTest/exam/{exam.id}/delete/")
        
        try:
            response = client.delete(f'/RoutineTest/exam/{exam.id}/delete/')
            print(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"   Response data: {response_data}")
            elif response.status_code == 403:
                response_data = response.json()
                print(f"   ❌ PERMISSION DENIED: {response_data}")
            else:
                print(f"   Response content: {response.content[:500]}")
                
        except Exception as e:
            print(f"   ❌ Error making request: {e}")
    else:
        print("   ❌ Login failed!")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    test_delete_flow()
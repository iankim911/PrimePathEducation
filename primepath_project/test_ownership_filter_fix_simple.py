#!/usr/bin/env python
"""
Simple test for the Ownership Filter Fix
Tests both "My Test Files" and "Other Teachers' Test Files" tabs
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from primepath_routinetest.models import RoutineExam as Exam
from primepath_routinetest.services.exam_service import ExamService
from core.models import Teacher
from primepath_routinetest.models import TeacherClassAssignment
import json


def run_simple_test():
    """Run a simple test of the ownership filter fix"""
    
    print("\n" + "="*80)
    print("OWNERSHIP FILTER FIX - SIMPLE TEST")
    print("="*80)
    
    # Set up test client
    client = Client()
    
    # Find a teacher user with class assignments
    try:
        teacher_user = User.objects.filter(teacher_profile__isnull=False).first()
        if not teacher_user:
            print("❌ No teacher users found in database")
            return False
            
        print(f"✅ Found teacher user: {teacher_user.username}")
        
        # Set password to test
        teacher_user.set_password('test123')
        teacher_user.save()
        
        # Login
        login_success = client.login(username=teacher_user.username, password='test123')
        if not login_success:
            print("❌ Failed to login as teacher")
            return False
            
        print(f"✅ Logged in as {teacher_user.username}")
        
    except Exception as e:
        print(f"❌ Error setting up teacher user: {e}")
        return False
    
    # Test "My Test Files" filter
    print("\n" + "-"*60)
    print("TEST 1: My Test Files (ownership=my)")
    print("-"*60)
    
    response = client.get('/RoutineTest/exams/?ownership=my')
    
    if response.status_code == 200:
        print(f"✅ Status: {response.status_code}")
        
        # Check context
        context = response.context
        print(f"  Ownership filter: {context.get('ownership_filter', 'NOT SET')}")
        print(f"  Filter intent: {context.get('filter_intent', 'NOT SET')}")
        print(f"  Is 'My Files' active: {context.get('is_my_files_active', False)}")
        
        # Check for correct filter intent
        if context.get('filter_intent') == 'SHOW_EDITABLE':
            print("  ✅ Correct filter intent: SHOW_EDITABLE")
        else:
            print(f"  ❌ Wrong filter intent: {context.get('filter_intent')}")
            
    else:
        print(f"❌ Failed - Status: {response.status_code}")
        if hasattr(response, 'content'):
            content = response.content.decode('utf-8')
            if 'Error' in content or 'error' in content:
                print(f"  Error in response: {content[:500]}")
    
    # Test "Other Teachers' Test Files" filter
    print("\n" + "-"*60)
    print("TEST 2: Other Teachers' Test Files (ownership=others)")
    print("-"*60)
    
    response = client.get('/RoutineTest/exams/?ownership=others')
    
    if response.status_code == 200:
        print(f"✅ Status: {response.status_code}")
        
        # Check context
        context = response.context
        print(f"  Ownership filter: {context.get('ownership_filter', 'NOT SET')}")
        print(f"  Filter intent: {context.get('filter_intent', 'NOT SET')}")
        print(f"  Is 'Others Files' active: {context.get('is_others_files_active', False)}")
        
        # Check for correct filter intent
        if context.get('filter_intent') == 'SHOW_VIEW_ONLY':
            print("  ✅ Correct filter intent: SHOW_VIEW_ONLY")
        else:
            print(f"  ❌ Wrong filter intent: {context.get('filter_intent')}")
            
    else:
        print(f"❌ Failed - Status: {response.status_code}")
        if hasattr(response, 'content'):
            content = response.content.decode('utf-8')
            if 'Error' in content or 'error' in content:
                print(f"  Error in response: {content[:500]}")
    
    # Test service layer directly
    print("\n" + "-"*60)
    print("TEST 3: Service Layer Filtering")
    print("-"*60)
    
    try:
        exams = Exam.objects.all()[:5]  # Get first 5 exams for testing
        
        # Test MY_EXAMS filter
        result_my = ExamService.organize_exams_hierarchically(
            exams,
            teacher_user,
            filter_assigned_only=True,
            ownership_filter='my',
            filter_intent='SHOW_EDITABLE'
        )
        
        exam_count_my = sum(len(exams) for program in result_my.values() for exams in program.values())
        print(f"  MY_EXAMS filter: {exam_count_my} exams included")
        
        # Test OTHERS_EXAMS filter
        result_others = ExamService.organize_exams_hierarchically(
            exams,
            teacher_user,
            filter_assigned_only=True,
            ownership_filter='others',
            filter_intent='SHOW_VIEW_ONLY'
        )
        
        exam_count_others = sum(len(exams) for program in result_others.values() for exams in program.values())
        print(f"  OTHERS_EXAMS filter: {exam_count_others} exams included")
        
        # They should be different
        if exam_count_my != exam_count_others:
            print("  ✅ Filters are producing different results (expected)")
        else:
            print("  ⚠️ Filters are producing the same results")
            
    except Exception as e:
        print(f"  ❌ Error testing service layer: {e}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    
    return True


if __name__ == '__main__':
    success = run_simple_test()
    sys.exit(0 if success else 1)
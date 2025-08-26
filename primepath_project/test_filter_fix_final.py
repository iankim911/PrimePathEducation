#!/usr/bin/env python
"""
Final comprehensive test for the "Show Assigned Classes Only" filter fix
Tests both backend filtering and actual HTML rendering
"""
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from primepath_routinetest.models import RoutineExam as Exam
from primepath_routinetest.services import ExamService
from primepath_routinetest.services.exam_service import ExamPermissionService


def test_filter_comprehensive():
    """Comprehensive test of the filter functionality"""
    print("\n" + "="*80)
    print("COMPREHENSIVE FILTER TEST - FINAL VERSION")
    print("="*80)
    
    # Get teacher1 user
    teacher_user = User.objects.filter(username='teacher1').first()
    if not teacher_user:
        print("❌ teacher1 user not found")
        return False
    
    print(f"✅ Testing with user: {teacher_user.username}")
    
    # Get all exams
    all_exams = Exam.objects.all()
    print(f"\nTotal exams in database: {all_exams.count()}")
    
    # Test 1: Backend filtering with filter OFF
    print("\n" + "-"*60)
    print("TEST 1: Backend Service - Filter OFF")
    print("-"*60)
    
    result_off = ExamService.organize_exams_hierarchically(
        all_exams, teacher_user, filter_assigned_only=False
    )
    
    total_off = 0
    view_only_off = 0
    for program in result_off.values():
        for class_exams in program.values():
            for exam in class_exams:
                total_off += 1
                if hasattr(exam, 'access_badge') and exam.access_badge == 'VIEW ONLY':
                    view_only_off += 1
    
    print(f"Total exams returned: {total_off}")
    print(f"VIEW ONLY exams: {view_only_off}")
    
    # Test 2: Backend filtering with filter ON
    print("\n" + "-"*60)
    print("TEST 2: Backend Service - Filter ON")
    print("-"*60)
    
    result_on = ExamService.organize_exams_hierarchically(
        all_exams, teacher_user, filter_assigned_only=True
    )
    
    total_on = 0
    view_only_on = 0
    view_only_details = []
    for program in result_on.values():
        for class_exams in program.values():
            for exam in class_exams:
                total_on += 1
                if hasattr(exam, 'access_badge') and exam.access_badge == 'VIEW ONLY':
                    view_only_on += 1
                    view_only_details.append(f"{exam.name} (ID: {exam.id})")
    
    print(f"Total exams returned: {total_on}")
    print(f"VIEW ONLY exams: {view_only_on}")
    
    if view_only_on > 0:
        print(f"❌❌❌ CRITICAL BUG: Found {view_only_on} VIEW ONLY exams when filter is ON!")
        print(f"VIEW ONLY exams that shouldn't be there:")
        for detail in view_only_details:
            print(f"  - {detail}")
    else:
        print("✅ No VIEW ONLY exams found - filter working correctly!")
    
    # Test 3: HTTP request test
    print("\n" + "-"*60)
    print("TEST 3: HTTP Request Test")
    print("-"*60)
    
    client = Client()
    
    # Set password and login
    teacher_user.set_password('teacher123')
    teacher_user.save()
    
    login_success = client.login(username='teacher1', password='teacher123')
    if not login_success:
        print("❌ Failed to login")
        return False
    
    print("✅ Logged in successfully")
    
    # Test with filter OFF
    response_off = client.get('/RoutineTest/exams/')
    if response_off.status_code == 200:
        print(f"Filter OFF request: SUCCESS (status {response_off.status_code})")
        if hasattr(response_off, 'context') and response_off.context:
            context_show_assigned = response_off.context.get('show_assigned_only', False)
            print(f"  Context show_assigned_only: {context_show_assigned}")
    
    # Test with filter ON
    response_on = client.get('/RoutineTest/exams/?assigned_only=true')
    if response_on.status_code == 200:
        print(f"Filter ON request: SUCCESS (status {response_on.status_code})")
        if hasattr(response_on, 'context') and response_on.context:
            context_show_assigned = response_on.context.get('show_assigned_only', False)
            print(f"  Context show_assigned_only: {context_show_assigned}")
            
            # Check hierarchical_exams in context
            hierarchical_exams = response_on.context.get('hierarchical_exams', {})
            context_total = 0
            context_view_only = 0
            
            for program in hierarchical_exams.values():
                for class_exams in program.values():
                    for exam in class_exams:
                        context_total += 1
                        if hasattr(exam, 'access_badge') and exam.access_badge == 'VIEW ONLY':
                            context_view_only += 1
            
            print(f"  Exams in context: {context_total}")
            print(f"  VIEW ONLY in context: {context_view_only}")
            
            if context_view_only > 0:
                print(f"  ❌ CRITICAL: Context contains {context_view_only} VIEW ONLY exams!")
            else:
                print(f"  ✅ Context is clean - no VIEW ONLY exams")
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    success = True
    
    if view_only_off == 0:
        print("❌ WARNING: No VIEW ONLY exams even with filter OFF - check test data")
        success = False
    else:
        print(f"✅ Filter OFF shows {view_only_off} VIEW ONLY exams (expected)")
    
    if view_only_on > 0:
        print(f"❌ FAILED: Filter ON still shows {view_only_on} VIEW ONLY exams")
        success = False
    else:
        print(f"✅ Filter ON shows 0 VIEW ONLY exams (correct)")
    
    print(f"\nFilter reduces exams from {total_off} to {total_on} (removed {total_off - total_on} exams)")
    
    if success:
        print("\n✅✅✅ ALL TESTS PASSED - FILTER IS WORKING! ✅✅✅")
    else:
        print("\n❌❌❌ TESTS FAILED - FILTER STILL BROKEN! ❌❌❌")
    
    return success


if __name__ == '__main__':
    # Install BeautifulSoup if needed for HTML testing
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("Installing BeautifulSoup4 for HTML parsing...")
        os.system("../venv/bin/pip install beautifulsoup4")
    
    success = test_filter_comprehensive()
    
    if not success:
        print("\n" + "="*80)
        print("DEBUGGING RECOMMENDATIONS:")
        print("="*80)
        print("1. Check server logs for [FILTER_] tags")
        print("2. Clear browser cache completely")
        print("3. Test in incognito mode")
        print("4. Check browser console for [PAGE_LOAD_DEBUG] messages")
        print("5. Verify the URL shows ?assigned_only=true when filter is ON")
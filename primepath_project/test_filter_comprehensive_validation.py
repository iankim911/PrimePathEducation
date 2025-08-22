#!/usr/bin/env python
"""
Test script to validate the "Show Assigned Classes Only" filter functionality
This ensures VIEW ONLY exams are properly hidden when the filter is enabled
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from primepath_routinetest.models import Exam
from primepath_routinetest.services import ExamService
from primepath_routinetest.services.exam_service import ExamPermissionService
import json


def test_filter_functionality():
    """Test that the filter properly excludes VIEW ONLY exams"""
    print("\n" + "="*80)
    print("TESTING: Show Assigned Classes Only Filter")
    print("="*80)
    
    # Get a teacher user
    try:
        teacher_user = User.objects.filter(username='teacher1').first()
        if not teacher_user:
            print("❌ Error: teacher1 user not found")
            return False
    except Exception as e:
        print(f"❌ Error getting teacher user: {e}")
        return False
    
    print(f"✅ Testing with user: {teacher_user.username}")
    
    # Get teacher's assignments
    assignments = ExamPermissionService.get_teacher_assignments(teacher_user)
    print(f"\n📋 Teacher's class assignments:")
    for class_code, access_level in assignments.items():
        print(f"   {class_code}: {access_level}")
    
    # Count assignments by access level
    view_only_classes = [c for c, a in assignments.items() if a == 'VIEW']
    editable_classes = [c for c, a in assignments.items() if a in ['FULL', 'CO_TEACHER']]
    
    print(f"\n📊 Assignment Summary:")
    print(f"   VIEW ONLY classes: {len(view_only_classes)}")
    print(f"   Editable classes (FULL/CO_TEACHER): {len(editable_classes)}")
    
    # Get all exams
    all_exams = Exam.objects.all()
    print(f"\n📚 Total exams in database: {all_exams.count()}")
    
    # Test filtering with filter OFF (show all)
    print("\n" + "-"*60)
    print("TEST 1: Filter OFF (Show All Exams)")
    print("-"*60)
    
    exams_unfiltered = ExamService.organize_exams_hierarchically(
        all_exams, teacher_user, filter_assigned_only=False
    )
    
    unfiltered_count = sum(len(exam_list) for program in exams_unfiltered.values() 
                          for exam_list in program.values())
    print(f"Exams shown with filter OFF: {unfiltered_count}")
    
    # Count badges when unfiltered
    unfiltered_badges = {'VIEW ONLY': 0, 'FULL ACCESS': 0, 'EDIT': 0, 'OWNER': 0, 'ADMIN': 0}
    for program in exams_unfiltered.values():
        for class_exams in program.values():
            for exam in class_exams:
                badge = getattr(exam, 'access_badge', 'UNKNOWN')
                if badge in unfiltered_badges:
                    unfiltered_badges[badge] += 1
    
    print("\nBadge distribution (filter OFF):")
    for badge, count in unfiltered_badges.items():
        if count > 0:
            print(f"   {badge}: {count}")
    
    # Test filtering with filter ON (assigned only)
    print("\n" + "-"*60)
    print("TEST 2: Filter ON (Show Assigned Classes Only)")
    print("-"*60)
    
    exams_filtered = ExamService.organize_exams_hierarchically(
        all_exams, teacher_user, filter_assigned_only=True
    )
    
    filtered_count = sum(len(exam_list) for program in exams_filtered.values() 
                        for exam_list in program.values())
    print(f"Exams shown with filter ON: {filtered_count}")
    
    # Count badges when filtered
    filtered_badges = {'VIEW ONLY': 0, 'FULL ACCESS': 0, 'EDIT': 0, 'OWNER': 0, 'ADMIN': 0}
    view_only_exams = []
    for program in exams_filtered.values():
        for class_exams in program.values():
            for exam in class_exams:
                badge = getattr(exam, 'access_badge', 'UNKNOWN')
                if badge in filtered_badges:
                    filtered_badges[badge] += 1
                    if badge == 'VIEW ONLY':
                        view_only_exams.append({
                            'name': exam.name,
                            'id': exam.id,
                            'classes': exam.class_codes if hasattr(exam, 'class_codes') else []
                        })
    
    print("\nBadge distribution (filter ON):")
    for badge, count in filtered_badges.items():
        if count > 0:
            print(f"   {badge}: {count}")
    
    # Check for the bug
    print("\n" + "="*60)
    print("FILTER VALIDATION RESULTS")
    print("="*60)
    
    if filtered_badges['VIEW ONLY'] > 0:
        print(f"❌❌❌ CRITICAL BUG DETECTED ❌❌❌")
        print(f"Found {filtered_badges['VIEW ONLY']} VIEW ONLY exams when filter is ON!")
        print("\nThese VIEW ONLY exams should be HIDDEN:")
        for exam_info in view_only_exams:
            print(f"   - {exam_info['name']}")
            print(f"     ID: {exam_info['id']}")
            print(f"     Classes: {exam_info['classes']}")
        
        print("\n⚠️ EXPECTED: 0 VIEW ONLY exams when filter is ON")
        print("⚠️ ACTUAL: {} VIEW ONLY exams still showing".format(filtered_badges['VIEW ONLY']))
        return False
    else:
        print("✅✅✅ FILTER WORKING CORRECTLY ✅✅✅")
        print("No VIEW ONLY exams shown when filter is ON")
        print(f"Filtered from {unfiltered_count} to {filtered_count} exams")
        print(f"Removed {unfiltered_count - filtered_count} exams (should be VIEW ONLY)")
        return True
    
    print("\n" + "="*60)


def test_via_http_request():
    """Test the filter via actual HTTP requests"""
    print("\n" + "="*80)
    print("TESTING: Filter via HTTP Request")
    print("="*80)
    
    client = Client()
    
    # Login as teacher1
    login_success = client.login(username='teacher1', password='1234')
    if not login_success:
        print("❌ Failed to login as teacher1")
        return False
    
    print("✅ Logged in as teacher1")
    
    # Test with filter OFF
    print("\n📋 Testing with filter OFF...")
    response = client.get('/RoutineTest/exams/')
    if response.status_code == 200:
        # Count exams in response context
        context = response.context
        if context:
            hierarchical_exams = context.get('hierarchical_exams', {})
            count_off = sum(len(exam_list) for program in hierarchical_exams.values() 
                          for exam_list in program.values())
            print(f"   Exams shown: {count_off}")
    
    # Test with filter ON
    print("\n📋 Testing with filter ON...")
    response = client.get('/RoutineTest/exams/?assigned_only=true')
    if response.status_code == 200:
        context = response.context
        if context:
            hierarchical_exams = context.get('hierarchical_exams', {})
            count_on = sum(len(exam_list) for program in hierarchical_exams.values() 
                         for exam_list in program.values())
            print(f"   Exams shown: {count_on}")
            
            # Check for VIEW ONLY badges
            view_only_count = 0
            for program in hierarchical_exams.values():
                for class_exams in program.values():
                    for exam in class_exams:
                        if hasattr(exam, 'access_badge') and exam.access_badge == 'VIEW ONLY':
                            view_only_count += 1
                            print(f"   ❌ Found VIEW ONLY exam: {exam.name}")
            
            if view_only_count > 0:
                print(f"\n❌ BUG: {view_only_count} VIEW ONLY exams still showing with filter ON")
                return False
            else:
                print("\n✅ No VIEW ONLY exams with filter ON - Working correctly!")
                return True
    
    return False


if __name__ == '__main__':
    print("\n" + "🔍"*40)
    print("COMPREHENSIVE FILTER VALIDATION TEST")
    print("🔍"*40)
    
    # Run both tests
    service_test_passed = test_filter_functionality()
    http_test_passed = test_via_http_request()
    
    print("\n" + "="*80)
    print("FINAL TEST RESULTS")
    print("="*80)
    
    if service_test_passed and http_test_passed:
        print("✅✅✅ ALL TESTS PASSED ✅✅✅")
        print("The filter is working correctly!")
    else:
        print("❌❌❌ TESTS FAILED ❌❌❌")
        print("The filter is NOT working correctly")
        print("\nNext steps:")
        print("1. Check server logs for [FILTER_COMPREHENSIVE] messages")
        print("2. Check browser console for [PAGE_LOAD_DEBUG] messages")
        print("3. Verify teacher assignments are correct in the database")
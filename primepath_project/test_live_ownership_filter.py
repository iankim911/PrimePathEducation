#!/usr/bin/env python
"""
Test the live ownership filter behavior by directly calling the view
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import User
from primepath_routinetest.views.exam import exam_list

def test_live_filter():
    print("="*80)
    print("🔍 TESTING LIVE OWNERSHIP FILTER")
    print("="*80)
    
    # Get a user to test with
    client = Client()
    factory = RequestFactory()
    
    # Try to get admin user
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No admin user found")
        return
    
    print(f"👤 Testing with user: {admin_user.username} (superuser: {admin_user.is_superuser})")
    
    # Test 1: "My Test Files" filter
    print(f"\n{'='*60}")
    print("🔍 Testing 'My Test Files' (ownership=my)")
    
    request = factory.get('/RoutineTest/exams/?ownership=my&exam_type=ALL')
    request.user = admin_user
    
    response = exam_list(request)
    print(f"📊 Response status: {response.status_code}")
    
    if hasattr(response, 'context_data'):
        context = response.context_data
        my_exams = context.get('hierarchical_exams', {})
        total_my = sum(len(exam_list) for program in my_exams.values() for exam_list in program.values())
        print(f"📋 'My Test Files' returned: {total_my} exams")
        
        # Show sample exams with badges
        count = 0
        for program, program_data in my_exams.items():
            for class_code, exams in program_data.items():
                for exam in exams:
                    if count < 3:  # Show first 3
                        badge = getattr(exam, 'access_badge', 'No Badge')
                        created_by_name = exam.created_by.name if exam.created_by else 'None'
                        print(f"  📄 {exam.name[:50]}... | Badge: {badge} | Created by: {created_by_name}")
                        count += 1
    
    # Test 2: "Other Teachers' Test Files" filter
    print(f"\n{'='*60}")
    print("🔍 Testing 'Other Teachers' Test Files' (ownership=others)")
    
    request = factory.get('/RoutineTest/exams/?ownership=others&exam_type=ALL')
    request.user = admin_user
    
    response = exam_list(request)
    print(f"📊 Response status: {response.status_code}")
    
    if hasattr(response, 'context_data'):
        context = response.context_data
        others_exams = context.get('hierarchical_exams', {})
        total_others = sum(len(exam_list) for program in others_exams.values() for exam_list in program.values())
        print(f"📋 'Other Teachers' Test Files' returned: {total_others} exams")
        
        # Show sample exams with badges
        count = 0
        for program, program_data in others_exams.items():
            for class_code, exams in program_data.items():
                for exam in exams:
                    if count < 3:  # Show first 3
                        badge = getattr(exam, 'access_badge', 'No Badge')
                        created_by_name = exam.created_by.name if exam.created_by else 'None'
                        print(f"  📄 {exam.name[:50]}... | Badge: {badge} | Created by: {created_by_name}")
                        count += 1
    
    # Analysis
    print(f"\n{'='*80}")
    print("📊 ANALYSIS:")
    print("="*80)
    
    if admin_user.is_superuser:
        print("⚠️  USER IS SUPERUSER - filtering may be bypassed")
        print("   Superusers typically see all exams regardless of ownership")
        print("   For proper testing, need a regular teacher account")
    
    print(f"\n🔍 Expected behavior:")
    print(f"  - 'My Test Files' should show OWNER/FULL ACCESS badges only")
    print(f"  - 'Other Teachers' should show VIEW ONLY badges only")
    print(f"  - No overlap between the two filters")
    
    print(f"\n✅ Fix Status:")
    if total_my == total_others:
        print("❌ ISSUE: Both filters return same number of exams")
        print("   This suggests filtering is not working properly")
    else:
        print("✅ GOOD: Filters return different numbers of exams")
        print("   This suggests filtering is working")

if __name__ == "__main__":
    test_live_filter()
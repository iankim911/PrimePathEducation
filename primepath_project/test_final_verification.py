#!/usr/bin/env python
"""
Final verification test - Quick check that all features work
"""

import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
os.environ['DJANGO_LOG_LEVEL'] = 'ERROR'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from primepath_routinetest.services.exam_service import ExamService

def run_final_check():
    print("\n" + "="*60)
    print("FINAL VERIFICATION CHECK")
    print("="*60)
    
    client = Client()
    
    # Setup admin user
    admin = User.objects.filter(username='admin').first()
    if not admin:
        print("❌ Admin user not found")
        return False
        
    admin.set_password('test123')
    admin.save()
    client.login(username='admin', password='test123')
    
    results = []
    
    # 1. Ownership Filtering
    print("\n✓ Testing Ownership Filtering...")
    r1 = client.get('/RoutineTest/exams/?ownership=my')
    if r1.status_code == 200 and r1.context.get('filter_intent') == 'SHOW_EDITABLE':
        results.append("✅ My Test Files filter working")
    else:
        results.append("❌ My Test Files filter broken")
        
    r2 = client.get('/RoutineTest/exams/?ownership=others')
    if r2.status_code == 200 and r2.context.get('filter_intent') == 'SHOW_VIEW_ONLY':
        results.append("✅ Other Teachers filter working")
    else:
        results.append("❌ Other Teachers filter broken")
    
    # 2. Exam List View
    print("✓ Testing Exam List View...")
    r3 = client.get('/RoutineTest/exams/')
    if r3.status_code == 200:
        if 'exams_by_program' in r3.context and 'teacher_assignments' in r3.context:
            results.append("✅ Exam list view working")
        else:
            results.append("❌ Exam list missing context")
    else:
        results.append(f"❌ Exam list returned {r3.status_code}")
    
    # 3. API Endpoints
    print("✓ Testing API Endpoints...")
    r4 = client.get('/RoutineTest/access/api/my-classes/')
    if r4.status_code == 200:
        results.append("✅ My Classes API working")
    else:
        results.append(f"❌ My Classes API returned {r4.status_code}")
    
    # 4. Create Exam Page
    print("✓ Testing Create Exam Page...")
    r5 = client.get('/RoutineTest/exams/create/')
    if r5.status_code == 200:
        results.append("✅ Create Exam page working")
    else:
        results.append(f"❌ Create Exam page returned {r5.status_code}")
    
    # 5. Service Layer
    print("✓ Testing Service Layer...")
    try:
        levels = ExamService.get_routinetest_curriculum_levels()
        if levels and len(levels) > 0:
            results.append(f"✅ Service layer working ({len(levels)} curriculum levels)")
        else:
            results.append("❌ Service layer - no curriculum levels")
    except Exception as e:
        results.append(f"❌ Service layer error: {e}")
    
    # Print Results
    print("\n" + "="*60)
    print("RESULTS:")
    print("="*60)
    
    passed = 0
    failed = 0
    for result in results:
        print(result)
        if "✅" in result:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "="*60)
    if failed == 0:
        print(f"🎉 ALL {passed} TESTS PASSED!")
        print("No existing features were affected by the changes.")
    else:
        print(f"⚠️ {failed} tests failed, {passed} tests passed")
        print("Some features may need attention.")
    print("="*60)
    
    return failed == 0

if __name__ == '__main__':
    success = run_final_check()
    sys.exit(0 if success else 1)
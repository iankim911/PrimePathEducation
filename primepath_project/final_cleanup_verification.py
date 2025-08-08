#!/usr/bin/env python
"""
Final Cleanup Verification
Quick verification that everything works after cleanup
"""

import os
import sys
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from django.test import Client
from django.urls import reverse


def quick_verify():
    """Quick verification of critical functionality"""
    print("=" * 60)
    print("FINAL CLEANUP VERIFICATION")
    print("=" * 60)
    
    client = Client()
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Critical imports
    print("\n1. Testing critical imports...")
    try:
        from placement_test.models import Exam, StudentSession
        from core.models import School, CurriculumLevel
        from placement_test.views import exam_list, start_test
        from core.views import teacher_dashboard
        print("   ✅ All imports working")
        tests_passed += 1
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        tests_failed += 1
    
    # Test 2: URL resolution
    print("\n2. Testing URL resolution...")
    try:
        urls = [
            reverse('core:index'),
            reverse('core:teacher_dashboard'),
            reverse('placement_test:exam_list'),
            reverse('placement_test:start_test'),
        ]
        print(f"   ✅ {len(urls)} URLs resolved")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ URL error: {e}")
        tests_failed += 1
    
    # Test 3: Database queries
    print("\n3. Testing database queries...")
    try:
        exam_count = Exam.objects.count()
        session_count = StudentSession.objects.count()
        school_count = School.objects.count()
        print(f"   ✅ Database working (Exams: {exam_count}, Sessions: {session_count}, Schools: {school_count})")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        tests_failed += 1
    
    # Test 4: View accessibility
    print("\n4. Testing view accessibility...")
    try:
        response = client.get('/')
        if response.status_code in [200, 301, 302]:
            print(f"   ✅ Home page accessible (HTTP {response.status_code})")
            tests_passed += 1
        else:
            print(f"   ❌ Home page error (HTTP {response.status_code})")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ View error: {e}")
        tests_failed += 1
    
    # Test 5: Modular structure
    print("\n5. Testing modular structure...")
    try:
        # Test Phase 9 - Model modularization
        from placement_test.models.exam import Exam as ExamModel
        from placement_test.models.session import StudentSession as SessionModel
        
        # Test Phase 10 - URL modularization
        from placement_test.student_urls import urlpatterns as student_urls
        from core.dashboard_urls import urlpatterns as dashboard_urls
        
        print("   ✅ Modular structure intact")
        tests_passed += 1
    except ImportError as e:
        print(f"   ❌ Modular structure error: {e}")
        tests_failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    total_tests = tests_passed + tests_failed
    success_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n✅ Passed: {tests_passed}/{total_tests}")
    print(f"❌ Failed: {tests_failed}/{total_tests}")
    print(f"📊 Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("\n🎉 PERFECT! All systems operational!")
        print("✅ Cleanup successful - no issues detected")
        print("✅ Project ready for development")
    elif success_rate >= 80:
        print("\n✅ GOOD! Most systems operational")
        print("Minor issues detected but non-critical")
    else:
        print("\n⚠️  WARNING! Critical issues detected")
        print("Review failed tests immediately")
    
    return success_rate >= 80


if __name__ == "__main__":
    success = quick_verify()
    sys.exit(0 if success else 1)
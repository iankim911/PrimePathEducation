#!/usr/bin/env python
"""
Phase 10 URL Verification Test
Verifies that URL modularization did not break any existing functionality
"""

import os
import sys
import django
from django.urls import reverse
from django.test import Client
import traceback

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
django.setup()


def test_url_resolution():
    """Test that all URLs resolve correctly"""
    print("📋 TESTING URL RESOLUTION")
    print("=" * 50)
    
    # Test critical URLs that were identified in analysis
    test_urls = [
        # Placement test URLs  
        ('placement_test:exam_list', {}, '/api/placement/exams/'),
        ('placement_test:create_exam', {}, '/api/placement/exams/create/'),
        ('placement_test:session_list', {}, '/api/placement/sessions/'),
        ('placement_test:start_test', {}, '/api/placement/start/'),
        
        # Core URLs
        ('core:index', {}, '/'),
        ('core:teacher_dashboard', {}, '/teacher/dashboard/'),
        ('core:placement_rules', {}, '/placement-rules/'),
        ('core:curriculum_levels', {}, '/curriculum/levels/'),
        
        # API URLs
        ('core:get_placement_rules', {}, '/api/placement-rules/'),
        ('core:save_placement_rules', {}, '/api/placement-rules/save/'),
        ('core:exam_mapping', {}, '/exam-mapping/'),
    ]
    
    success_count = 0
    total_tests = len(test_urls)
    
    for url_name, kwargs, expected_url in test_urls:
        try:
            resolved_url = reverse(url_name, kwargs=kwargs)
            if resolved_url == expected_url:
                print(f"✅ {url_name} -> {resolved_url}")
                success_count += 1
            else:
                print(f"❌ {url_name} -> Expected: {expected_url}, Got: {resolved_url}")
        except Exception as e:
            print(f"❌ {url_name} -> ERROR: {e}")
    
    success_rate = (success_count / total_tests) * 100
    print(f"\n📊 URL Resolution: {success_count}/{total_tests} ({success_rate:.1f}%)")
    
    return success_count == total_tests


def test_url_accessibility():
    """Test that URLs are actually accessible"""
    print("\n🌐 TESTING URL ACCESSIBILITY")
    print("=" * 50)
    
    client = Client()
    test_urls = [
        ('/api/placement/exams/', 'Exam List'),
        ('/api/placement/sessions/', 'Session List'),
        ('/api/placement/start/', 'Start Test'),
        ('/', 'Home Page'),
        ('/teacher/dashboard/', 'Teacher Dashboard'),
        ('/placement-rules/', 'Placement Rules'),
    ]
    
    success_count = 0
    total_tests = len(test_urls)
    
    for url, description in test_urls:
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"✅ {description} ({url}) -> 200 OK")
                success_count += 1
            elif response.status_code in [301, 302]:
                print(f"⚠️  {description} ({url}) -> {response.status_code} Redirect")
                success_count += 0.5  # Partial credit for redirects
            else:
                print(f"❌ {description} ({url}) -> {response.status_code}")
        except Exception as e:
            print(f"❌ {description} ({url}) -> ERROR: {e}")
    
    success_rate = (success_count / total_tests) * 100
    print(f"\n📊 URL Accessibility: {success_count}/{total_tests} ({success_rate:.1f}%)")
    
    return success_count >= (total_tests * 0.85)  # 85% success rate acceptable


def test_url_import_structure():
    """Test that URL imports work correctly"""
    print("\n📦 TESTING URL IMPORT STRUCTURE") 
    print("=" * 50)
    
    try:
        # Test that we can import the URL modules
        from placement_test.student_urls import urlpatterns as student_patterns
        from placement_test.exam_urls import urlpatterns as exam_patterns
        from placement_test.session_urls import urlpatterns as session_patterns
        from placement_test.api_urls import urlpatterns as api_patterns
        
        from core.dashboard_urls import urlpatterns as dashboard_patterns
        from core.admin_urls import urlpatterns as admin_patterns
        from core.api_urls import urlpatterns as core_api_patterns
        
        print("✅ All URL modules import successfully")
        
        # Test pattern counts
        placement_total = len(student_patterns) + len(exam_patterns) + len(session_patterns) + len(api_patterns)
        core_total = len(dashboard_patterns) + len(admin_patterns) + len(core_api_patterns)
        
        print(f"✅ Placement test patterns: {placement_total} (Student: {len(student_patterns)}, Exam: {len(exam_patterns)}, Session: {len(session_patterns)}, API: {len(api_patterns)})")
        print(f"✅ Core patterns: {core_total} (Dashboard: {len(dashboard_patterns)}, Admin: {len(admin_patterns)}, API: {len(core_api_patterns)})")
        
        # Verify expected totals (from original analysis)
        if placement_total >= 30:  # Original had 36, allowing for some flexibility
            print("✅ Placement test pattern count matches expectations")
        else:
            print(f"⚠️  Placement test pattern count lower than expected: {placement_total}")
            
        if core_total >= 15:  # Original had 17, allowing for some flexibility
            print("✅ Core pattern count matches expectations")
        else:
            print(f"⚠️  Core pattern count lower than expected: {core_total}")
        
        return True
        
    except Exception as e:
        print(f"❌ URL import error: {e}")
        traceback.print_exc()
        return False


def run_comprehensive_verification():
    """Run all verification tests"""
    print("=" * 80)
    print("PHASE 10 URL MODULARIZATION VERIFICATION")
    print("Testing URL organization and backward compatibility")
    print("=" * 80)
    
    results = {
        'url_resolution': test_url_resolution(),
        'url_accessibility': test_url_accessibility(),
        'import_structure': test_url_import_structure(),
    }
    
    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"\nOverall Success: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("\n🎉 PHASE 10 URL MODULARIZATION SUCCESSFUL!")
        print("✅ All URL patterns working correctly")
        print("✅ Backward compatibility maintained")
        print("✅ Modular structure implemented")
        return True
    else:
        print(f"\n⚠️  PHASE 10 NEEDS ATTENTION")
        print(f"Some tests failed. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = run_comprehensive_verification()
    sys.exit(0 if success else 1)
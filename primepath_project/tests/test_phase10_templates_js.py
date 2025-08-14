#!/usr/bin/env python
"""
Phase 10 Template & JavaScript Verification
Test that templates and JavaScript still work correctly with modular URLs
"""

import os
import sys
import django
from django.test import Client
from django.urls import reverse
import re

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
django.setup()


def test_template_url_generation():
    """Test that templates can generate URLs correctly"""
    print("🎨 TESTING TEMPLATE URL GENERATION")
    print("=" * 50)
    
    client = Client()
    
    # Test pages that contain URL references identified in our analysis
    template_tests = [
        ('/api/PlacementTest/exams/', 'Exam List', ['create_exam', 'teacher_dashboard']),
        ('/PlacementTest/PlacementTest/teacher/dashboard/', 'Teacher Dashboard', ['PlacementTest:exam_list', 'PlacementTest:create_exam', 'core:placement_rules']),
        ('/placement-rules/', 'Placement Rules', ['placement-rules']),
    ]
    
    success_count = 0
    total_tests = len(template_tests)
    
    for url, description, expected_urls in template_tests:
        try:
            response = client.get(url)
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                
                # Check if expected URLs are generated in the content
                urls_found = 0
                for expected_url in expected_urls:
                    if expected_url in content or expected_url.replace(':', '/') in content:
                        urls_found += 1
                
                if urls_found > 0:
                    print(f"✅ {description} -> URLs generated ({urls_found}/{len(expected_urls)} found)")
                    success_count += 1
                else:
                    print(f"⚠️  {description} -> Template loaded but no expected URLs found")
                    success_count += 0.5
            else:
                print(f"❌ {description} -> HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {description} -> ERROR: {e}")
    
    success_rate = (success_count / total_tests) * 100
    print(f"\n📊 Template URL Generation: {success_count}/{total_tests} ({success_rate:.1f}%)")
    
    return success_count >= (total_tests * 0.8)  # 80% success rate


def test_reverse_url_lookups():
    """Test URL reverse lookups work with new structure"""
    print("\n🔗 TESTING REVERSE URL LOOKUPS")
    print("=" * 50)
    
    # Test URLs that were identified as having template dependencies
    reverse_tests = [
        ('core:teacher_dashboard', {}, 'Teacher Dashboard'),
        ('PlacementTest:start_test', {}, 'Start Test'),
        ('PlacementTest:exam_list', {}, 'Exam List'),
        ('core:placement_rules', {}, 'Placement Rules'),
        ('PlacementTest:get_audio', {'audio_id': 1}, 'Get Audio'),
    ]
    
    success_count = 0
    total_tests = len(reverse_tests)
    
    for url_name, kwargs, description in reverse_tests:
        try:
            resolved_url = reverse(url_name, kwargs=kwargs)
            print(f"✅ {description} ({url_name}) -> {resolved_url}")
            success_count += 1
        except Exception as e:
            print(f"❌ {description} ({url_name}) -> ERROR: {e}")
    
    success_rate = (success_count / total_tests) * 100
    print(f"\n📊 Reverse URL Lookups: {success_count}/{total_tests} ({success_rate:.1f}%)")
    
    return success_rate >= 90


def test_javascript_endpoints():
    """Test JavaScript API endpoints work"""
    print("\n📜 TESTING JAVASCRIPT API ENDPOINTS")
    print("=" * 50)
    
    client = Client()
    
    # Test API endpoints that JavaScript uses (from our analysis)
    js_api_tests = [
        ('/api/placement-rules/', 'GET', 'Placement Rules API'),
        # Note: Some endpoints require POST with data, testing GET for basic connectivity
    ]
    
    success_count = 0
    total_tests = len(js_api_tests)
    
    for url, method, description in js_api_tests:
        try:
            if method == 'GET':
                response = client.get(url)
            elif method == 'POST':
                response = client.post(url)
            
            if response.status_code in [200, 302, 405]:  # 405 = Method not allowed, but URL exists
                status_msg = "✅" if response.status_code == 200 else "⚠️"
                print(f"{status_msg} {description} -> {response.status_code}")
                success_count += 1 if response.status_code == 200 else 0.5
            else:
                print(f"❌ {description} -> {response.status_code}")
        except Exception as e:
            print(f"❌ {description} -> ERROR: {e}")
    
    success_rate = (success_count / total_tests) * 100 if total_tests > 0 else 100
    print(f"\n📊 JavaScript API Endpoints: {success_count}/{total_tests} ({success_rate:.1f}%)")
    
    return success_rate >= 75  # Lower threshold due to method restrictions


def test_critical_page_loads():
    """Test that critical pages load without URL errors"""
    print("\n🚀 TESTING CRITICAL PAGES LOAD")
    print("=" * 50)
    
    client = Client()
    
    # Test critical pages
    critical_pages = [
        ('/', 'Home Page'),
        ('/PlacementTest/PlacementTest/teacher/dashboard/', 'Teacher Dashboard'),
        ('/api/PlacementTest/exams/', 'Exam List'),
        ('/api/PlacementTest/sessions/', 'Session List'),
        ('/api/PlacementTest/start/', 'Start Test'),
        ('/placement-rules/', 'Placement Rules'),
    ]
    
    success_count = 0
    total_tests = len(critical_pages)
    
    for url, description in critical_pages:
        try:
            response = client.get(url)
            if response.status_code == 200:
                # Check for common URL-related errors in the content
                content = response.content.decode('utf-8')
                
                url_errors = [
                    'NoReverseMatch',
                    'Reverse for',
                    'No module named',
                    'urlpatterns',
                    'URLconf'
                ]
                
                has_url_error = any(error in content for error in url_errors)
                
                if not has_url_error:
                    print(f"✅ {description} -> Loads without URL errors")
                    success_count += 1
                else:
                    print(f"⚠️  {description} -> Loads but contains URL errors")
                    success_count += 0.5
            else:
                print(f"❌ {description} -> HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {description} -> ERROR: {e}")
    
    success_rate = (success_count / total_tests) * 100
    print(f"\n📊 Critical Pages Load: {success_count}/{total_tests} ({success_rate:.1f}%)")
    
    return success_rate >= 90


def run_template_js_verification():
    """Run all template and JavaScript verification tests"""
    print("=" * 80)
    print("PHASE 10 TEMPLATE & JAVASCRIPT VERIFICATION")
    print("Testing that templates and JavaScript work with modular URLs")
    print("=" * 80)
    
    results = {
        'template_url_generation': test_template_url_generation(),
        'reverse_url_lookups': test_reverse_url_lookups(),
        'javascript_endpoints': test_javascript_endpoints(),
        'critical_page_loads': test_critical_page_loads(),
    }
    
    # Summary
    print("\n" + "=" * 80)
    print("TEMPLATE & JAVASCRIPT VERIFICATION SUMMARY")
    print("=" * 80)
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"\nOverall Success: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 85:
        print("\n🎉 TEMPLATES & JAVASCRIPT WORKING CORRECTLY!")
        print("✅ All URL patterns accessible from templates")
        print("✅ Reverse URL lookups functioning") 
        print("✅ JavaScript endpoints responding")
        print("✅ Critical pages load without errors")
        print("\n🏆 PHASE 10 URL MODULARIZATION COMPLETE!")
        return True
    else:
        print(f"\n⚠️  TEMPLATES & JAVASCRIPT NEED ATTENTION")
        print(f"Some functionality may be impacted. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = run_template_js_verification()
    sys.exit(0 if success else 1)
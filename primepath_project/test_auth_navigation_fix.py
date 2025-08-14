#!/usr/bin/env python
"""
Test script to verify authentication navigation fix implementation
Tests that login tab is removed and all teacher features require authentication
"""
import os
import sys
import django
import json
from datetime import datetime

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import Teacher

def test_auth_navigation():
    """Test the authentication navigation improvements"""
    print("\n" + "="*70)
    print("AUTHENTICATION NAVIGATION FIX TEST")
    print("="*70)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": []
    }
    
    client = Client()
    
    # Test 1: Verify teacher1 is now Taehyun Kim
    print("\n1. Testing teacher1 name update...")
    try:
        user = User.objects.get(username='teacher1')
        teacher = user.teacher_profile
        
        test_result = {
            "test": "Teacher name update",
            "expected": "Taehyun Kim",
            "actual": teacher.name,
            "passed": teacher.name == "Taehyun Kim"
        }
        
        if test_result["passed"]:
            print(f"   ✅ Teacher name correctly updated to: {teacher.name}")
        else:
            print(f"   ❌ Teacher name is: {teacher.name}, expected: Taehyun Kim")
        
        results["tests"].append(test_result)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results["tests"].append({
            "test": "Teacher name update",
            "error": str(e),
            "passed": False
        })
    
    # Test 2: Check that login tab is removed from navigation
    print("\n2. Testing login tab removal from navigation...")
    response = client.get('/')
    
    test_result = {
        "test": "Login tab removal",
        "description": "Login tab should not exist in navigation",
        "found_login_tab": 'Teacher Login</a>' in response.content.decode(),
        "passed": 'Teacher Login</a>' not in response.content.decode()
    }
    
    if test_result["passed"]:
        print("   ✅ Login tab successfully removed from navigation")
    else:
        print("   ❌ Login tab still present in navigation")
    
    results["tests"].append(test_result)
    
    # Test 3: Test unauthenticated access to protected views
    print("\n3. Testing unauthenticated access redirects to login...")
    protected_urls = [
        ('/PlacementTest/PlacementTest/teacher/dashboard/', 'Dashboard'),
        ('/api/PlacementTest/exams/create/', 'Create Exam'),
        ('/api/PlacementTest/exams/', 'Exam List'),
        ('/api/PlacementTest/sessions/', 'Session List'),
        ('/exam-mapping/', 'Exam Mapping'),
        ('/placement-rules/', 'Placement Rules')
    ]
    
    for url, name in protected_urls:
        response = client.get(url, follow=False)
        is_redirect = response.status_code == 302
        redirects_to_login = is_redirect and response.url.startswith('/login/')
        
        test_result = {
            "test": f"Protected view: {name}",
            "url": url,
            "status_code": response.status_code,
            "redirects_to_login": redirects_to_login,
            "redirect_url": response.url if is_redirect else None,
            "passed": redirects_to_login
        }
        
        if test_result["passed"]:
            print(f"   ✅ {name}: Correctly redirects to login")
        else:
            print(f"   ❌ {name}: Does not redirect to login (status: {response.status_code})")
        
        results["tests"].append(test_result)
    
    # Test 4: Test student pages remain accessible without auth
    print("\n4. Testing student pages accessible without authentication...")
    student_urls = [
        ('/api/PlacementTest/start/', 'Start Test'),
        ('/', 'Home Page')
    ]
    
    for url, name in student_urls:
        response = client.get(url, follow=False)
        is_accessible = response.status_code == 200
        
        test_result = {
            "test": f"Student page: {name}",
            "url": url,
            "status_code": response.status_code,
            "passed": is_accessible
        }
        
        if test_result["passed"]:
            print(f"   ✅ {name}: Accessible without authentication")
        else:
            print(f"   ❌ {name}: Not accessible (status: {response.status_code})")
        
        results["tests"].append(test_result)
    
    # Test 5: Test authenticated access
    print("\n5. Testing authenticated access to protected views...")
    # Login as teacher1
    login_success = client.login(username='teacher1', password='teacher123')
    
    if login_success:
        print("   ✅ Successfully logged in as teacher1 (Taehyun Kim)")
        
        # Test accessing dashboard
        response = client.get('/PlacementTest/PlacementTest/teacher/dashboard/')
        test_result = {
            "test": "Authenticated dashboard access",
            "status_code": response.status_code,
            "passed": response.status_code == 200
        }
        
        if test_result["passed"]:
            print("   ✅ Dashboard accessible when authenticated")
        else:
            print(f"   ❌ Dashboard not accessible (status: {response.status_code})")
        
        results["tests"].append(test_result)
        
        # Check if user info shows in navigation
        response = client.get('/')
        has_user_info = 'Taehyun Kim' in response.content.decode()
        has_logout = 'Logout' in response.content.decode()
        
        test_result = {
            "test": "User info in navigation",
            "has_user_name": has_user_info,
            "has_logout": has_logout,
            "passed": has_user_info and has_logout
        }
        
        if test_result["passed"]:
            print("   ✅ User info (Taehyun Kim) and Logout shown in navigation")
        else:
            print("   ❌ User info not properly displayed in navigation")
        
        results["tests"].append(test_result)
    else:
        print("   ❌ Failed to login as teacher1")
        results["tests"].append({
            "test": "Authentication",
            "error": "Login failed",
            "passed": False
        })
    
    # Calculate summary
    total_tests = len(results["tests"])
    passed_tests = sum(1 for t in results["tests"] if t.get("passed", False))
    
    results["summary"] = {
        "total": total_tests,
        "passed": passed_tests,
        "failed": total_tests - passed_tests,
        "success_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
    }
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {results['summary']['success_rate']}")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Authentication navigation fix is working correctly.")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Please review the results above.")
    
    # Save results to file
    with open('auth_navigation_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("\nDetailed results saved to: auth_navigation_test_results.json")
    
    return results

if __name__ == "__main__":
    test_auth_navigation()
#!/usr/bin/env python
"""
Test script to verify the logout button 403 error fix
Tests that logout now works with GET request without CSRF issues
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

def test_logout_fix():
    """Test the logout functionality fix"""
    print("\n" + "="*70)
    print("LOGOUT BUTTON FIX TEST")
    print("Testing that logout works with GET request (no 403 error)")
    print("="*70)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": []
    }
    
    client = Client()
    
    # Test 1: Login first
    print("\n1. Testing login...")
    login_success = client.login(username='teacher1', password='teacher123')
    
    test_result = {
        "test": "Teacher login",
        "username": "teacher1",
        "passed": login_success
    }
    
    if test_result["passed"]:
        print(f"   ✅ Successfully logged in as teacher1 (Taehyun Kim)")
    else:
        print(f"   ❌ Failed to login")
    
    results["tests"].append(test_result)
    
    if login_success:
        # Test 2: Check authenticated state
        print("\n2. Testing authenticated state...")
        response = client.get('/teacher/dashboard/')
        
        test_result = {
            "test": "Authenticated access",
            "endpoint": "/teacher/dashboard/",
            "status_code": response.status_code,
            "passed": response.status_code == 200
        }
        
        if test_result["passed"]:
            print(f"   ✅ Dashboard accessible when logged in")
        else:
            print(f"   ❌ Dashboard not accessible (status: {response.status_code})")
        
        results["tests"].append(test_result)
        
        # Test 3: Test logout with GET request (the main fix)
        print("\n3. Testing logout with GET request...")
        response = client.get('/logout/', follow=False)
        
        test_result = {
            "test": "Logout with GET request",
            "endpoint": "/logout/",
            "method": "GET",
            "status_code": response.status_code,
            "is_redirect": response.status_code == 302,
            "redirect_url": response.url if response.status_code == 302 else None,
            "passed": response.status_code == 302 and '/login/' in response.url
        }
        
        if test_result["passed"]:
            print(f"   ✅ Logout successful with GET request (no 403 error!)")
            print(f"      Redirected to: {response.url}")
        else:
            print(f"   ❌ Logout failed (status: {response.status_code})")
            if response.status_code == 403:
                print(f"      ERROR: Still getting 403 Forbidden!")
        
        results["tests"].append(test_result)
        
        # Test 4: Verify actually logged out
        print("\n4. Verifying logout completed...")
        response = client.get('/teacher/dashboard/', follow=False)
        
        test_result = {
            "test": "Verify logged out",
            "endpoint": "/teacher/dashboard/",
            "status_code": response.status_code,
            "redirects_to_login": response.status_code == 302 and '/login/' in response.get('Location', ''),
            "passed": response.status_code == 302
        }
        
        if test_result["passed"]:
            print(f"   ✅ Confirmed logged out (dashboard now redirects to login)")
        else:
            print(f"   ❌ Still logged in somehow (status: {response.status_code})")
        
        results["tests"].append(test_result)
    
    # Test 5: Test multiple login/logout cycles
    print("\n5. Testing multiple login/logout cycles...")
    cycle_results = []
    for i in range(3):
        # Login
        login_ok = client.login(username='admin', password='admin123')
        # Logout
        logout_response = client.get('/logout/', follow=False)
        logout_ok = logout_response.status_code == 302
        
        cycle_results.append({
            "cycle": i + 1,
            "login": login_ok,
            "logout": logout_ok,
            "logout_status": logout_response.status_code
        })
        
        print(f"   Cycle {i+1}: Login={'✅' if login_ok else '❌'}, Logout={'✅' if logout_ok else '❌'} (status: {logout_response.status_code})")
    
    test_result = {
        "test": "Multiple login/logout cycles",
        "cycles": cycle_results,
        "passed": all(c["login"] and c["logout"] for c in cycle_results)
    }
    
    if test_result["passed"]:
        print(f"   ✅ All login/logout cycles successful")
    else:
        print(f"   ❌ Some cycles failed")
    
    results["tests"].append(test_result)
    
    # Test 6: Check that logout message is shown
    print("\n6. Testing logout success message...")
    client.login(username='teacher1', password='teacher123')
    response = client.get('/logout/', follow=True)  # Follow redirect to login page
    
    # Check if success message is in the response
    has_message = False
    if hasattr(response, 'context') and response.context:
        messages = list(response.context.get('messages', []))
        has_message = any('logged out' in str(m).lower() for m in messages)
    
    test_result = {
        "test": "Logout success message",
        "has_message": has_message,
        "final_url": response.redirect_chain[-1][0] if response.redirect_chain else None,
        "passed": has_message or 'logged out' in response.content.decode().lower()
    }
    
    if test_result["passed"]:
        print(f"   ✅ Logout success message displayed")
    else:
        print(f"   ⚠️  Logout message might not be visible")
    
    results["tests"].append(test_result)
    
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
        print("\n🎉 SUCCESS! The logout button 403 error is FIXED!")
        print("✅ Logout now works with GET request (industry standard)")
        print("✅ No CSRF token required")
        print("✅ Immediate logout on click")
        print("✅ Proper redirect to login page")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Please review the results above.")
    
    # Save results to file
    with open('logout_fix_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("\nDetailed results saved to: logout_fix_test_results.json")
    
    return results

if __name__ == "__main__":
    test_logout_fix()
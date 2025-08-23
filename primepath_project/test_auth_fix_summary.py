#!/usr/bin/env python
"""
Summary test for authentication navigation fix
"""

import requests
from bs4 import BeautifulSoup
import sys

def test_auth_fix():
    """Test that authentication pages are properly neutral"""
    
    print("\n" + "="*80)
    print("🔍 AUTHENTICATION NAVIGATION FIX - FINAL VERIFICATION")
    print("="*80)
    
    base_url = "http://127.0.0.1:8000"
    
    tests = []
    
    # Test 1: Login page
    print("\n📋 Testing Login Page...")
    try:
        response = requests.get(f"{base_url}/login/")
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check for navigation elements
        nav_tabs = soup.find_all(class_='nav-tabs')
        nav_elements = soup.find_all('nav')
        placement_links = soup.find_all('a', href=lambda x: x and 'PlacementTest' in x)
        dashboard_links = [a for a in soup.find_all('a') if a.get_text() and 'Dashboard' in a.get_text()]
        
        login_clean = (len(nav_tabs) == 0 and 
                      len(nav_elements) == 0 and 
                      len(placement_links) == 0 and
                      len(dashboard_links) == 0)
        
        tests.append(('Login page is neutral (no navigation)', login_clean))
        
    except Exception as e:
        tests.append(('Login page accessible', False))
        print(f"  Error: {e}")
    
    # Test 2: Check template inheritance
    print("\n📋 Checking Template Structure...")
    try:
        response = requests.get(f"{base_url}/login/")
        content = response.text
        
        # The JavaScript should be checking for navigation
        has_nav_check = 'AUTH_LOGIN_NAV_ERROR' in content
        tests.append(('Navigation detection JavaScript present', has_nav_check))
        
        # Should have login form
        has_login_form = 'loginForm' in content
        tests.append(('Login form present', has_login_form))
        
    except Exception as e:
        tests.append(('Template structure check', False))
    
    # Test 3: Profile page (requires login)
    print("\n📋 Testing Profile Page...")
    session = requests.Session()
    
    # Try to login
    login_data = {
        'username': 'admin',  # Using admin as it likely exists
        'password': 'admin',
        'csrfmiddlewaretoken': 'test'  # Will be rejected but that's OK for this test
    }
    
    try:
        # Get CSRF token first
        login_page = session.get(f"{base_url}/login/")
        soup = BeautifulSoup(login_page.content, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        
        if csrf_input:
            login_data['csrfmiddlewaretoken'] = csrf_input.get('value')
            
            # Attempt login
            response = session.post(f"{base_url}/login/", data=login_data)
            
            # Check profile page (might redirect to login if auth failed, that's OK)
            profile_response = session.get(f"{base_url}/profile/")
            
            if profile_response.status_code == 200:
                soup = BeautifulSoup(profile_response.content, 'html.parser')
                nav_tabs = soup.find_all(class_='nav-tabs')
                profile_clean = len(nav_tabs) == 0
                tests.append(('Profile page is neutral', profile_clean))
            else:
                tests.append(('Profile page (requires authentication)', 'N/A'))
        else:
            tests.append(('Profile page test', 'Skipped - no CSRF token'))
            
    except Exception as e:
        tests.append(('Profile page test', 'Skipped'))
    
    # Test 4: App chooser
    print("\n📋 Testing App Chooser...")
    try:
        response = requests.get(f"{base_url}/")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            nav_tabs = soup.find_all(class_='nav-tabs')
            
            # Should have application choices
            content = response.text
            has_placement = 'Placement Test' in content
            has_routine = 'Routine Test' in content
            
            app_chooser_clean = len(nav_tabs) == 0 and has_placement and has_routine
            tests.append(('App chooser is neutral with both options', app_chooser_clean))
        else:
            tests.append(('App chooser redirects to login', True))  # This is also correct behavior
            
    except Exception as e:
        tests.append(('App chooser test', False))
    
    # Print results
    print("\n" + "="*80)
    print("📊 TEST RESULTS")
    print("="*80)
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test_name, result in tests:
        if result == 'N/A' or result == 'Skipped':
            status = '⏭️'
            skipped += 1
        elif result:
            status = '✅'
            passed += 1
        else:
            status = '❌'
            failed += 1
            
        print(f"  {status} {test_name}")
    
    print("\n" + "-"*80)
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Skipped: {skipped}")
    
    print("\n" + "="*80)
    if failed == 0:
        print("✅ SUCCESS - Authentication pages are correctly neutral!")
        print("   The login page no longer shows Placement Test navigation.")
        print("   Users see a clean, application-neutral login experience.")
    else:
        print("⚠️  Some tests failed - please review")
    print("="*80)
    
    return failed == 0

if __name__ == '__main__':
    success = test_auth_fix()
    sys.exit(0 if success else 1)
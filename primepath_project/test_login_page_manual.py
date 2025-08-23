#!/usr/bin/env python
"""
Manual test to verify login page has no navigation
Requires server to be running at http://127.0.0.1:8000/
"""

import requests
from bs4 import BeautifulSoup
import json

def test_login_page():
    """Test that the login page has no navigation elements"""
    print("\n" + "="*80)
    print("🧪 LOGIN PAGE NAVIGATION TEST")
    print("="*80)
    
    url = "http://127.0.0.1:8000/login/"
    
    try:
        # Get the login page
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"❌ Failed to get login page: Status {response.status_code}")
            return False
        
        print(f"✅ Login page loaded successfully")
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check for navigation elements
        test_results = {
            'nav_tabs': len(soup.find_all(class_='nav-tabs')),
            'nav_elements': len(soup.find_all('nav')),
            'placement_links': len(soup.find_all('a', href=lambda x: x and 'PlacementTest' in x)),
            'routine_links': len(soup.find_all('a', href=lambda x: x and 'RoutineTest' in x)),
            'dashboard_links': len([a for a in soup.find_all('a') if a.get_text() and 'Dashboard' in a.get_text()]),
            'upload_links': len([a for a in soup.find_all('a') if a.get_text() and 'Upload Exam' in a.get_text()]),
            'manage_links': len([a for a in soup.find_all('a') if a.get_text() and 'Manage Exams' in a.get_text()]),
            'start_test_links': len([a for a in soup.find_all('a') if a.get_text() and 'Start Test' in a.get_text()]),
            'view_results_links': len([a for a in soup.find_all('a') if a.get_text() and 'View Results' in a.get_text()]),
        }
        
        print("\n📊 Navigation Element Check:")
        print("-"*40)
        
        all_good = True
        for element, count in test_results.items():
            status = "✅" if count == 0 else "❌"
            print(f"  {status} {element.replace('_', ' ').title()}: {count}")
            if count > 0:
                all_good = False
        
        # Check for the clean base template indicators
        print("\n📋 Template Check:")
        print("-"*40)
        
        # The clean base template should not have nav-tabs class in actual HTML elements
        # (It might appear in JavaScript checking code, which is fine)
        actual_nav_tabs = soup.find_all(class_='nav-tabs')
        if len(actual_nav_tabs) == 0:
            print("  ✅ No nav-tabs HTML elements found (using clean template)")
        else:
            print("  ❌ nav-tabs HTML elements found (wrong template!)")
            all_good = False
        
        # Check for login form elements (should exist)
        login_form = soup.find('form', id='loginForm')
        if login_form:
            print("  ✅ Login form present")
        else:
            print("  ❌ Login form missing")
            all_good = False
        
        # Check for proper page title
        title = soup.find('title')
        if title and 'Teacher Login' in title.text:
            print("  ✅ Correct page title")
        else:
            print("  ❌ Wrong page title")
        
        # Check JavaScript console logging
        scripts = soup.find_all('script')
        has_nav_check = False
        for script in scripts:
            if script.string and 'AUTH_LOGIN_NAV_ERROR' in script.string:
                has_nav_check = True
                break
        
        if has_nav_check:
            print("  ✅ Navigation check JavaScript present")
        else:
            print("  ⚠️  Navigation check JavaScript might be missing")
        
        print("\n" + "="*80)
        if all_good:
            print("✅ SUCCESS: Login page is correctly neutral (no navigation)")
        else:
            print("❌ FAILURE: Login page still has navigation elements")
        print("="*80)
        
        return all_good
        
    except requests.ConnectionError:
        print("❌ Cannot connect to server at http://127.0.0.1:8000/")
        print("   Make sure the server is running!")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    success = test_login_page()
    exit(0 if success else 1)
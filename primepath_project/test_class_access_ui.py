#!/usr/bin/env python
"""
UI Test Script for Teacher Class Access Management
Tests the frontend visibility and functionality

Run with: python test_class_access_ui.py
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import Teacher

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_dashboard_button():
    """Test that the button appears on the dashboard"""
    print_section("Testing Dashboard Button Visibility")
    
    try:
        client = Client()
        
        # Test without login first
        response = client.get('/RoutineTest/')
        print(f"  Response status (no login): {response.status_code}")
        
        # Create and login a user
        user = User.objects.filter(username='test_teacher').first()
        if not user:
            user = User.objects.create_user('test_teacher', 'test@example.com', 'password123')
            user.is_staff = True
            user.save()
            print("  Created test user")
        
        # Login
        logged_in = client.login(username='test_teacher', password='password123')
        if not logged_in:
            # Try setting password again
            user.set_password('password123')
            user.save()
            logged_in = client.login(username='test_teacher', password='password123')
        
        print(f"  Login successful: {logged_in}")
        
        # Get dashboard
        response = client.get('/RoutineTest/')
        print(f"  Dashboard response status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check for button
            if 'My Classes & Access' in content:
                print("  ✓ 'My Classes & Access' button text found")
            else:
                print("  ✗ 'My Classes & Access' button text NOT found")
            
            # Check for URL
            if 'RoutineTest:my_classes' in content:
                print("  ✓ URL pattern 'RoutineTest:my_classes' found")
            else:
                print("  ✗ URL pattern 'RoutineTest:my_classes' NOT found")
                
            # Check for actual URL path
            if '/RoutineTest/access/my-classes/' in content:
                print("  ✓ Resolved URL path found")
            else:
                print("  ✗ Resolved URL path NOT found")
            
            # Check for icon
            if 'fa-users-cog' in content:
                print("  ✓ Icon class 'fa-users-cog' found")
            else:
                print("  ✗ Icon class NOT found")
                
            # Check for style
            if '#FF9800' in content:
                print("  ✓ Orange color style found")
            else:
                print("  ✗ Orange color style NOT found")
            
            return True
        else:
            print(f"  ✗ Dashboard returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ✗ Error testing dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_access_page():
    """Test that the access page loads correctly"""
    print_section("Testing Access Page Loading")
    
    try:
        client = Client()
        
        # Login
        user = User.objects.filter(username='test_teacher').first()
        if user:
            user.set_password('password123')
            user.save()
            client.login(username='test_teacher', password='password123')
            
            # Try to access the page
            url = reverse('RoutineTest:my_classes')
            print(f"  Accessing URL: {url}")
            
            response = client.get(url)
            print(f"  Response status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                
                # Check for key elements
                checks = [
                    ('My Classes & Access', 'Page title'),
                    ('My Current Classes', 'Teacher view section'),
                    ('Request Access', 'Request section'),
                    ('access-container', 'Split view container'),
                    ('left-panel', 'Left panel'),
                    ('right-panel', 'Right panel')
                ]
                
                for text, description in checks:
                    if text in content:
                        print(f"  ✓ {description} found: '{text}'")
                    else:
                        print(f"  ✗ {description} NOT found: '{text}'")
                
                return True
            elif response.status_code == 302:
                print(f"  ⚠ Redirected to: {response.url}")
                return False
            else:
                print(f"  ✗ Page returned status {response.status_code}")
                return False
        else:
            print("  ✗ Test user not found")
            return False
            
    except Exception as e:
        print(f"  ✗ Error testing access page: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_url_resolution():
    """Test URL resolution directly"""
    print_section("Testing URL Resolution")
    
    try:
        from django.urls import resolve, reverse
        
        # Test reverse resolution
        url = reverse('RoutineTest:my_classes')
        print(f"  URL from reverse: {url}")
        print(f"  Expected: /RoutineTest/access/my-classes/")
        
        # Test forward resolution
        match = resolve('/RoutineTest/access/my-classes/')
        print(f"  View name from resolve: {match.url_name}")
        print(f"  View function: {match.func.__name__}")
        print(f"  Namespace: {match.namespace}")
        
        # Verify correctness
        if url == '/RoutineTest/access/my-classes/':
            print("  ✓ URL path is correct")
        else:
            print(f"  ✗ URL path mismatch: got '{url}'")
            
        if match.url_name == 'my_classes':
            print("  ✓ URL name is correct")
        else:
            print(f"  ✗ URL name mismatch: got '{match.url_name}'")
            
        if match.namespace == 'RoutineTest':
            print("  ✓ Namespace is correct")
        else:
            print(f"  ✗ Namespace mismatch: got '{match.namespace}'")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error in URL resolution: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_javascript_console():
    """Provide JavaScript to test in browser console"""
    print_section("Browser Console Test Commands")
    
    print("""
  To test in browser console, run these commands:
  
  1. Check if button exists:
     document.querySelector('a[href*="my-classes"]')
     
  2. Check button text:
     document.querySelector('a[href*="my-classes"]').textContent
     
  3. Click the button programmatically:
     document.querySelector('a[href*="my-classes"]').click()
     
  4. Check console logs:
     // Should see: [RoutineTest] Quick action: My Classes & Access
     
  5. Direct navigation:
     window.location.href = '/RoutineTest/access/my-classes/'
    """)
    
    return True

def main():
    """Run all UI tests"""
    print("\n" + "="*60)
    print("  TEACHER CLASS ACCESS - UI TEST SUITE")
    print("="*60)
    print(f"  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("URL Resolution", test_url_resolution),
        ("Dashboard Button", test_dashboard_button),
        ("Access Page Loading", test_access_page),
        ("Browser Console Commands", test_javascript_console)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n✗ Unexpected error in {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print_section("UI TEST SUMMARY")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 All UI tests passed!")
        print("\n  The button should now be visible on the RoutineTest dashboard.")
    else:
        print(f"\n  ⚠ {total - passed} test(s) failed.")
        print("\n  Debugging steps:")
        print("    1. Check browser console for errors")
        print("    2. View page source to see if button HTML is present")
        print("    3. Check Django debug toolbar if enabled")
        print("    4. Clear browser cache and try again")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
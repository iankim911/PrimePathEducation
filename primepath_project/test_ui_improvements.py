#!/usr/bin/env python
"""
Test UI Improvements for My Classes & Access Page
Verifies that UI enhancements are working without breaking functionality

Run with: python test_ui_improvements.py
"""

import os
import sys
import django
from datetime import datetime
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import Teacher
from primepath_routinetest.models import TeacherClassAssignment, ClassAccessRequest

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def test_ui_elements_present():
    """Test that new UI elements are present in the rendered HTML"""
    print_section("Testing UI Elements Presence")
    
    client = Client()
    
    # Create and login as teacher
    user = User.objects.filter(username='ui_test_teacher').first()
    if not user:
        user = User.objects.create_user('ui_test_teacher', 'ui_test@example.com', 'password123')
        user.is_staff = True
        user.save()
        
    # Ensure teacher profile exists
    teacher, created = Teacher.objects.get_or_create(
        email=user.email,
        defaults={'name': 'UI Test Teacher', 'user': user}
    )
    
    client.force_login(user)
    response = client.get('/RoutineTest/access/my-classes/')
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check for new UI elements
        ui_checks = {
            'Information Banner': 'access-info-banner' in content,
            'How it works text': 'How it works:' in content,
            'Enhanced Empty State': 'empty-state' in content,
            'Empty State Icon': 'empty-state-icon' in content,
            'Visual Separator CSS': 'access-container::after' in content,
            'Left Panel Background': 'background: #ffffff' in content,
            'Right Panel Background': 'background: #F8FAFB' in content,
            'Enhanced Console Logging': 'CLASS_ACCESS_UI_ENHANCED' in content,
            'UI State Tracking': 'UI Panel Configuration' in content,
            'Request New Access Header': 'Request New Access' in content,
        }
        
        all_passed = True
        for element, present in ui_checks.items():
            status = "✓" if present else "✗"
            print(f"  {status} {element}: {'Present' if present else 'NOT FOUND'}")
            if not present:
                all_passed = False
        
        # Check CSS improvements
        print("\n  CSS Improvements:")
        css_checks = {
            'Increased gap (35px)': 'gap: 35px' in content,
            'Border radius 10px': 'border-radius: 10px' in content,
            'Info banner gradient': 'linear-gradient(135deg, #E8F5E9' in content,
            'Animation keyframes': '@keyframes pulse' in content,
        }
        
        for css_element, present in css_checks.items():
            status = "✓" if present else "✗"
            print(f"    {status} {css_element}: {'Applied' if present else 'Missing'}")
            if not present:
                all_passed = False
        
        return all_passed
    else:
        print(f"  ✗ Failed to load page: Status {response.status_code}")
        return False

def test_functionality_preserved():
    """Test that all original functionality still works"""
    print_section("Testing Functionality Preservation")
    
    client = Client()
    
    # Login as teacher
    user = User.objects.get(username='ui_test_teacher')
    client.force_login(user)
    
    # Test key endpoints
    endpoints = [
        ('/RoutineTest/access/my-classes/', 'My Classes Page'),
        ('/RoutineTest/access/api/my-classes/', 'API - My Classes'),
        ('/RoutineTest/access/api/available-classes/', 'API - Available Classes'),
        ('/RoutineTest/access/api/my-requests/', 'API - My Requests'),
    ]
    
    all_passed = True
    for endpoint, name in endpoints:
        response = client.get(endpoint)
        status = "✓" if response.status_code == 200 else "✗"
        print(f"  {status} {name}: Status {response.status_code}")
        if response.status_code != 200:
            all_passed = False
    
    return all_passed

def test_admin_view_improvements():
    """Test admin view UI improvements"""
    print_section("Testing Admin View Improvements")
    
    client = Client()
    
    # Create or get admin user
    admin = User.objects.filter(username='ui_test_admin').first()
    if not admin:
        admin = User.objects.create_superuser('ui_test_admin', 'admin@example.com', 'admin123')
    
    # Ensure teacher profile for admin
    teacher, created = Teacher.objects.get_or_create(
        email=admin.email,
        defaults={'name': 'Admin User', 'user': admin, 'is_head_teacher': True}
    )
    
    client.force_login(admin)
    response = client.get('/RoutineTest/access/my-classes/?admin_view=true')
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        admin_checks = {
            'Admin Info Banner': 'Admin View:' in content and 'access-info-banner' in content,
            'Admin Dashboard Header': 'Admin Dashboard' in content,
            'Enhanced Headers': '<i class="fas fa-users"></i>' in content,
            'Pending Requests Icon': '<i class="fas fa-clock"></i>' in content,
            'Empty State for Admin': 'All Caught Up!' in content or 'pending_requests' in content,
        }
        
        all_passed = True
        for element, present in admin_checks.items():
            status = "✓" if present else "✗"
            print(f"  {status} {element}: {'Present' if present else 'Missing'}")
            if not present:
                all_passed = False
        
        return all_passed
    else:
        print(f"  ✗ Failed to load admin view: Status {response.status_code}")
        return False

def test_responsive_behavior():
    """Test that responsive behavior is preserved"""
    print_section("Testing Responsive Behavior")
    
    client = Client()
    user = User.objects.get(username='ui_test_teacher')
    client.force_login(user)
    
    response = client.get('/RoutineTest/access/my-classes/')
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        responsive_checks = {
            'Flex layout preserved': 'display: flex' in content,
            'Container fluid': 'container-fluid' in content,
            'Grid layout for stats': 'display: grid' in content,
            'Responsive minmax': 'minmax(' in content,
        }
        
        all_passed = True
        for check, present in responsive_checks.items():
            status = "✓" if present else "✗"
            print(f"  {status} {check}: {'Yes' if present else 'No'}")
            if not present:
                all_passed = False
        
        return all_passed
    else:
        print(f"  ✗ Failed to load page: Status {response.status_code}")
        return False

def test_javascript_functionality():
    """Test that JavaScript functions are intact"""
    print_section("Testing JavaScript Functionality")
    
    client = Client()
    user = User.objects.get(username='ui_test_teacher')
    client.force_login(user)
    
    response = client.get('/RoutineTest/access/my-classes/')
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        js_checks = {
            'switchTab function': 'function switchTab(' in content,
            'requestAccess function': 'function requestAccess(' in content,
            'withdrawRequest function': 'function withdrawRequest(' in content,
            'Form submission handler': 'requestAccessForm' in content,
            'Modal functionality': '$requestAccessModal' in content or 'requestAccessModal' in content,
            'Console logging groups': 'console.group(' in content,
            'UI verification timeout': 'setTimeout(() =>' in content,
        }
        
        all_passed = True
        for function, present in js_checks.items():
            status = "✓" if present else "✗"
            print(f"  {status} {function}: {'Intact' if present else 'Missing'}")
            if not present:
                all_passed = False
        
        return all_passed
    else:
        print(f"  ✗ Failed to load page: Status {response.status_code}")
        return False

def check_no_other_pages_affected():
    """Verify that other RoutineTest pages are not affected"""
    print_section("Verifying Other Pages Not Affected")
    
    client = Client()
    
    # Check other RoutineTest pages
    pages_to_check = [
        '/RoutineTest/',
        '/RoutineTest/create/',
        '/RoutineTest/exams/',
        '/RoutineTest/start/',
    ]
    
    all_passed = True
    for page_url in pages_to_check:
        response = client.get(page_url)
        if response.status_code in [200, 302]:  # 302 for pages requiring auth
            content = response.content.decode('utf-8') if response.status_code == 200 else ''
            
            # These UI elements should NOT appear on other pages
            should_not_have = [
                'access-info-banner',
                'CLASS_ACCESS_UI_ENHANCED',
                'empty-state-icon',
                'background: #F8FAFB'
            ]
            
            page_ok = True
            for element in should_not_have:
                if element in content:
                    page_ok = False
                    print(f"  ✗ {page_url}: Contains class_access UI element '{element}'")
                    break
            
            if page_ok:
                print(f"  ✓ {page_url}: Not affected by UI changes")
            else:
                all_passed = False
        else:
            print(f"  - {page_url}: Skipped (Status {response.status_code})")
    
    return all_passed

def main():
    """Run all UI improvement tests"""
    print("\n" + "="*70)
    print("  MY CLASSES & ACCESS - UI IMPROVEMENTS TEST")
    print("="*70)
    print(f"  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("UI Elements Present", test_ui_elements_present),
        ("Functionality Preserved", test_functionality_preserved),
        ("Admin View Improvements", test_admin_view_improvements),
        ("Responsive Behavior", test_responsive_behavior),
        ("JavaScript Functionality", test_javascript_functionality),
        ("Other Pages Not Affected", check_no_other_pages_affected),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n✗ Error in {test_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Print summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 All UI improvements successfully implemented!")
        print("\n  UI Enhancements Applied:")
        print("    1. Visual separation with colored backgrounds")
        print("    2. Information banner explaining the system")
        print("    3. Enhanced empty states with helpful guidance")
        print("    4. Improved debugging with comprehensive console logs")
        print("    5. No impact on other RoutineTest pages")
        print("\n  Next Steps:")
        print("    1. Clear browser cache")
        print("    2. Test in browser with different user types")
        print("    3. Verify visual appearance matches requirements")
    else:
        print(f"\n  ⚠ {total - passed} test(s) failed.")
        print("\n  Please review the failed tests above.")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
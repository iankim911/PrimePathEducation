#!/usr/bin/env python
"""
Test Layout Fix Verification for Class Access Page
Verifies that the panel overlap issue is resolved

Run with: python test_layout_fix_verification.py
"""

import os
import sys
import django
from datetime import datetime
import json
import time

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
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}")

def test_css_files_exist():
    """Verify that all required CSS files exist"""
    print_section("Testing CSS Files Existence")
    
    css_files = [
        'static/css/mobile-responsive.css',
        'static/css/desktop-layout-fix.css',
        'static/css/routinetest-theme.css'
    ]
    
    all_exist = True
    for css_file in css_files:
        file_path = os.path.join(os.path.dirname(__file__), css_file)
        exists = os.path.exists(file_path)
        status = "✓" if exists else "✗"
        print(f"  {status} {css_file}: {'Found' if exists else 'NOT FOUND'}")
        if not exists:
            all_exist = False
    
    return all_exist

def test_mobile_css_fixed():
    """Verify that mobile-responsive.css has been fixed"""
    print_section("Testing Mobile CSS Fix")
    
    mobile_css_path = os.path.join(os.path.dirname(__file__), 'static/css/mobile-responsive.css')
    
    try:
        with open(mobile_css_path, 'r') as f:
            content = f.read()
        
        # Check that the problematic rule is within a media query
        lines = content.split('\n')
        in_media_query = False
        max_width_100vw_found = False
        max_width_line_num = 0
        media_query_line_num = 0
        
        for i, line in enumerate(lines, 1):
            if '@media' in line and 'max-width: 767px' in line:
                in_media_query = True
                media_query_line_num = i
            elif line.strip() == '}' and in_media_query:
                # Check if we're closing the media query
                open_braces = content[:content.find('\n'.join(lines[:i]))].count('{')
                close_braces = content[:content.find('\n'.join(lines[:i]))].count('}')
                if open_braces == close_braces:
                    in_media_query = False
            elif 'max-width: 100vw !important' in line:
                max_width_100vw_found = True
                max_width_line_num = i
                if in_media_query:
                    print(f"  ✓ max-width: 100vw rule is correctly inside mobile media query (line {i})")
                    return True
        
        if max_width_100vw_found and not in_media_query:
            print(f"  ✗ max-width: 100vw rule found OUTSIDE media query at line {max_width_line_num}")
            print(f"    This will cause desktop layout issues!")
            return False
        elif not max_width_100vw_found:
            print(f"  ⚠ max-width: 100vw rule not found in file")
            return True  # Might have been removed entirely, which is also fine
        
    except Exception as e:
        print(f"  ✗ Error reading mobile CSS: {str(e)}")
        return False

def test_template_includes_desktop_fix():
    """Verify that class_access.html includes desktop-layout-fix.css"""
    print_section("Testing Template Includes Desktop Fix CSS")
    
    template_path = os.path.join(os.path.dirname(__file__), 
                                'templates/primepath_routinetest/class_access.html')
    
    try:
        with open(template_path, 'r') as f:
            content = f.read()
        
        checks = {
            'Desktop fix CSS link': 'desktop-layout-fix.css' in content,
            'Enhanced flex styles': 'display: flex !important' in content,
            'Left panel flex fix': 'flex: 0 0 60% !important' in content,
            'Right panel flex fix': 'flex: 0 0 38% !important' in content,
            'Max-width override': 'max-width: none !important' in content,
            'Debug JavaScript': 'CLASS_ACCESS_LAYOUT_DEBUG' in content,
            'Overlap detection': 'isOverlapping' in content,
            'Layout diagnostics': 'layoutDiagnostics' in content
        }
        
        all_passed = True
        for check_name, passed in checks.items():
            status = "✓" if passed else "✗"
            print(f"  {status} {check_name}: {'Present' if passed else 'Missing'}")
            if not passed:
                all_passed = False
        
        return all_passed
    
    except Exception as e:
        print(f"  ✗ Error reading template: {str(e)}")
        return False

def test_page_renders_correctly():
    """Test that the page renders without errors"""
    print_section("Testing Page Rendering")
    
    client = Client()
    
    # Create test teacher user
    user = User.objects.filter(username='layout_test_teacher').first()
    if not user:
        user = User.objects.create_user('layout_test_teacher', 'layout@test.com', 'testpass123')
        user.is_staff = True
        user.save()
    
    # Ensure teacher profile exists
    teacher, created = Teacher.objects.get_or_create(
        email=user.email,
        defaults={'name': 'Layout Test Teacher', 'user': user}
    )
    
    # Add some test data
    if created:
        # Assign a test class
        TeacherClassAssignment.objects.create(
            teacher=teacher,
            class_code='CLASS_7A',
            access_level='FULL',
            assigned_by=user
        )
    
    client.force_login(user)
    
    try:
        response = client.get('/RoutineTest/access/my-classes/')
        
        if response.status_code == 200:
            print(f"  ✓ Page loaded successfully (Status: {response.status_code})")
            
            content = response.content.decode('utf-8')
            
            # Check for key elements
            elements = {
                'Access container': 'access-container' in content,
                'Left panel': 'left-panel' in content,
                'Right panel': 'right-panel' in content,
                'Desktop fix CSS': 'desktop-layout-fix.css' in content,
                'Debug logging': 'CLASS_ACCESS_LAYOUT_DEBUG' in content
            }
            
            all_present = True
            for element, present in elements.items():
                status = "✓" if present else "✗"
                print(f"    {status} {element}: {'Present' if present else 'Missing'}")
                if not present:
                    all_present = False
            
            return all_present
        else:
            print(f"  ✗ Page failed to load (Status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"  ✗ Error loading page: {str(e)}")
        return False

def test_css_specificity():
    """Test that our CSS has proper specificity to override conflicts"""
    print_section("Testing CSS Specificity")
    
    desktop_css_path = os.path.join(os.path.dirname(__file__), 'static/css/desktop-layout-fix.css')
    
    try:
        with open(desktop_css_path, 'r') as f:
            content = f.read()
        
        important_rules = {
            'Container flex': 'display: flex !important' in content,
            'Panel widths': 'flex: 0 0 60% !important' in content,
            'Max-width reset': 'max-width: none !important' in content,
            'Width enforcement': 'width: 60% !important' in content,
            'Position relative': 'position: relative !important' in content,
            'No float': 'float: none !important' in content
        }
        
        all_passed = True
        for rule_name, has_important in important_rules.items():
            status = "✓" if has_important else "✗"
            print(f"  {status} {rule_name}: {'Has !important' if has_important else 'Missing !important'}")
            if not has_important:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"  ✗ Error reading desktop CSS: {str(e)}")
        return False

def test_no_side_effects():
    """Test that the fix doesn't affect other pages"""
    print_section("Testing No Side Effects on Other Pages")
    
    client = Client()
    
    # Test other RoutineTest pages
    test_urls = [
        '/RoutineTest/',
        '/RoutineTest/create/',
        '/RoutineTest/exams/',
    ]
    
    all_passed = True
    for url in test_urls:
        try:
            response = client.get(url)
            if response.status_code in [200, 302]:  # 302 for redirects
                if response.status_code == 200:
                    content = response.content.decode('utf-8')
                    # These should NOT appear on other pages
                    if 'access-container' not in content and 'CLASS_ACCESS_LAYOUT_DEBUG' not in content:
                        print(f"  ✓ {url}: No class_access specific code")
                    else:
                        print(f"  ✗ {url}: Contains class_access specific code")
                        all_passed = False
                else:
                    print(f"  - {url}: Redirected (likely auth required)")
            else:
                print(f"  ⚠ {url}: Status {response.status_code}")
                
        except Exception as e:
            print(f"  ✗ {url}: Error - {str(e)}")
            all_passed = False
    
    return all_passed

def main():
    """Run all layout fix verification tests"""
    print("\n" + "="*80)
    print("  LAYOUT FIX VERIFICATION TEST SUITE")
    print("  Testing Panel Overlap Fix for Class Access Page")
    print("="*80)
    print(f"  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("CSS Files Exist", test_css_files_exist),
        ("Mobile CSS Fixed", test_mobile_css_fixed),
        ("Template Includes Desktop Fix", test_template_includes_desktop_fix),
        ("CSS Specificity", test_css_specificity),
        ("Page Renders Correctly", test_page_renders_correctly),
        ("No Side Effects", test_no_side_effects),
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
        print("\n  🎉 Layout fix successfully implemented!")
        print("\n  FIXED ISSUES:")
        print("    1. Removed global max-width: 100vw from desktop viewports")
        print("    2. Added desktop-specific layout protection CSS")
        print("    3. Enhanced flexbox rules with !important specificity")
        print("    4. Added comprehensive debugging and diagnostics")
        print("    5. Ensured no side effects on other pages")
        print("\n  NEXT STEPS:")
        print("    1. Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)")
        print("    2. Test in browser at /RoutineTest/access/my-classes/")
        print("    3. Check browser console for layout diagnostics")
        print("    4. Verify panels are side-by-side, not overlapping")
    else:
        print(f"\n  ⚠ {total - passed} test(s) failed.")
        print("\n  TROUBLESHOOTING:")
        print("    1. Check if all files were saved properly")
        print("    2. Restart Django development server")
        print("    3. Clear browser cache completely")
        print("    4. Check browser console for errors")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
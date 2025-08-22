#!/usr/bin/env python
"""
Test script to verify mode toggle removal from Classes & Exams page
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client

def test_mode_toggle_removal():
    print("=== MODE TOGGLE REMOVAL TEST ===")
    
    # Create test client
    c = Client()
    
    # Login as admin
    print("1. Logging in as admin...")
    login_success = c.login(username='admin', password='admin123')
    print(f"   Login successful: {login_success}")
    
    if not login_success:
        print("   ❌ Login failed - cannot test page")
        return False
        
    # Test the classes-exams page
    print("2. Testing Classes & Exams page...")
    response = c.get('/RoutineTest/classes-exams/')
    print(f"   Status code: {response.status_code}")
    print(f"   Page loads successfully: {response.status_code == 200}")
    
    if response.status_code != 200:
        print(f"   ❌ Page failed to load. Error: {response.status_code}")
        if hasattr(response, 'content'):
            print(f"   Error content: {response.content.decode()[:500]}")
        return False
    
    # Check if mode toggle content is NOT in the response
    print("3. Checking for mode toggle elements...")
    content = response.content.decode()
    
    # Check for various mode toggle indicators
    checks = {
        'mode_toggle_enhanced include': 'mode_toggle_enhanced' in content,
        'Mode Toggle text': 'Mode Toggle' in content,
        'Current Mode text': 'Current Mode:' in content,
        'mode-toggle-container class': 'mode-toggle-container' in content,
        'mode-toggle-wrapper class': 'mode-toggle-wrapper' in content,
        'adminAuthModal element': 'adminAuthModal' in content,
        'handleModeToggle function': 'handleModeToggle' in content,
        'Teacher Mode button': 'Teacher Mode' in content and 'btn' in content,
        'Admin Mode button': 'Admin Mode' in content and 'btn' in content
    }
    
    found_elements = []
    for check_name, found in checks.items():
        status = "❌ FOUND" if found else "✅ REMOVED"
        print(f"   {status}: {check_name}")
        if found:
            found_elements.append(check_name)
    
    # Overall result
    all_removed = len(found_elements) == 0
    print(f"\n4. Overall Result:")
    print(f"   All mode toggle elements removed: {'✅ YES' if all_removed else '❌ NO'}")
    
    if not all_removed:
        print(f"   Elements still present: {', '.join(found_elements)}")
    
    # Check that the page still has essential content
    essential_checks = {
        'Classes & Exams Management title': 'Classes & Exams Management' in content,
        'unified-container div': 'unified-container' in content,
        'access-summary-section': 'access-summary-section' in content,
        'matrix-preview': 'matrix-preview' in content
    }
    
    print(f"\n5. Essential functionality check:")
    essential_ok = True
    for check_name, found in essential_checks.items():
        status = "✅ PRESENT" if found else "❌ MISSING"
        print(f"   {status}: {check_name}")
        if not found:
            essential_ok = False
    
    print(f"\n=== TEST SUMMARY ===")
    print(f"✅ Page loads successfully: {response.status_code == 200}")
    print(f"{'✅' if all_removed else '❌'} Mode toggle completely removed: {all_removed}")
    print(f"{'✅' if essential_ok else '❌'} Essential functionality intact: {essential_ok}")
    
    overall_success = response.status_code == 200 and all_removed and essential_ok
    print(f"\n🎯 OVERALL TEST RESULT: {'✅ SUCCESS' if overall_success else '❌ FAILED'}")
    
    return overall_success

if __name__ == "__main__":
    test_mode_toggle_removal()
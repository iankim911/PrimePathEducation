#!/usr/bin/env python
"""
QA Test: Mode Toggle Position Fix
Verifies that the Teacher/Admin mode toggle appears BELOW the navigation bar
NOT in the header area

Created: August 18, 2025
"""

import os
import sys
import django
import json
from datetime import datetime

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from bs4 import BeautifulSoup

User = get_user_model()

def test_mode_toggle_position():
    """Test that mode toggle appears below navigation, not in header"""
    print("\n" + "="*80)
    print("MODE TOGGLE POSITION FIX - QA TEST")
    print("="*80)
    print(f"Test Started: {datetime.now()}")
    print("-"*80)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'tests': [],
        'summary': {
            'total': 0,
            'passed': 0,
            'failed': 0
        }
    }
    
    client = Client()
    
    # Test 1: Check if CSS fix file exists
    print("\n[TEST 1] Checking if position fix CSS exists...")
    css_path = 'static/css/mode-toggle-position-fix.css'
    if os.path.exists(css_path):
        print("✅ PASS: Position fix CSS file exists")
        results['tests'].append({'name': 'CSS Fix File Exists', 'status': 'PASS'})
        results['summary']['passed'] += 1
    else:
        print("❌ FAIL: Position fix CSS file not found")
        results['tests'].append({'name': 'CSS Fix File Exists', 'status': 'FAIL'})
        results['summary']['failed'] += 1
    results['summary']['total'] += 1
    
    # Test 2: Login as admin
    print("\n[TEST 2] Logging in as admin...")
    try:
        admin = User.objects.filter(is_staff=True).first()
        if not admin:
            admin = User.objects.create_superuser('testadmin', 'admin@test.com', 'testpass123')
        client.force_login(admin)
        print("✅ PASS: Logged in as admin")
        results['tests'].append({'name': 'Admin Login', 'status': 'PASS'})
        results['summary']['passed'] += 1
    except Exception as e:
        print(f"❌ FAIL: Could not login - {e}")
        results['tests'].append({'name': 'Admin Login', 'status': 'FAIL', 'error': str(e)})
        results['summary']['failed'] += 1
    results['summary']['total'] += 1
    
    # Test 3: Load the exam list page
    print("\n[TEST 3] Loading exam list page...")
    response = client.get('/RoutineTest/exams/')
    if response.status_code == 200:
        print("✅ PASS: Exam list page loaded successfully")
        results['tests'].append({'name': 'Page Load', 'status': 'PASS'})
        results['summary']['passed'] += 1
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test 4: Check if mode toggle exists
        print("\n[TEST 4] Checking if mode toggle exists...")
        mode_toggle = soup.find('div', class_='mode-toggle-container')
        if mode_toggle:
            print("✅ PASS: Mode toggle container found")
            results['tests'].append({'name': 'Mode Toggle Exists', 'status': 'PASS'})
            results['summary']['passed'] += 1
            
            # Test 5: Check toggle is NOT inside header
            print("\n[TEST 5] Checking toggle is NOT in header...")
            header = soup.find('div', class_='header')
            if header:
                toggle_in_header = header.find('div', class_='mode-toggle-container')
                if not toggle_in_header:
                    print("✅ PASS: Toggle is NOT inside header")
                    results['tests'].append({'name': 'Toggle Not In Header', 'status': 'PASS'})
                    results['summary']['passed'] += 1
                else:
                    print("❌ FAIL: Toggle found inside header!")
                    results['tests'].append({'name': 'Toggle Not In Header', 'status': 'FAIL'})
                    results['summary']['failed'] += 1
            else:
                print("⚠️ WARNING: Header not found")
                results['tests'].append({'name': 'Toggle Not In Header', 'status': 'SKIP'})
            results['summary']['total'] += 1
            
            # Test 6: Check toggle is after navigation
            print("\n[TEST 6] Checking toggle is after navigation...")
            nav = soup.find('nav', class_='nav-tabs')
            if nav and mode_toggle:
                # Check if mode toggle appears after nav in the HTML
                nav_pos = str(soup).find('nav-tabs')
                toggle_pos = str(soup).find('mode-toggle-container')
                if toggle_pos > nav_pos:
                    print("✅ PASS: Toggle appears after navigation in HTML")
                    results['tests'].append({'name': 'Toggle After Nav', 'status': 'PASS'})
                    results['summary']['passed'] += 1
                else:
                    print("❌ FAIL: Toggle appears before navigation!")
                    results['tests'].append({'name': 'Toggle After Nav', 'status': 'FAIL'})
                    results['summary']['failed'] += 1
            else:
                print("⚠️ WARNING: Could not verify position relative to nav")
                results['tests'].append({'name': 'Toggle After Nav', 'status': 'SKIP'})
            results['summary']['total'] += 1
            
            # Test 7: Check CSS fix is included
            print("\n[TEST 7] Checking if CSS fix is included...")
            css_links = soup.find_all('link', rel='stylesheet')
            css_fix_included = any('mode-toggle-position-fix.css' in str(link.get('href', '')) for link in css_links)
            if css_fix_included:
                print("✅ PASS: CSS fix is included in the page")
                results['tests'].append({'name': 'CSS Fix Included', 'status': 'PASS'})
                results['summary']['passed'] += 1
            else:
                print("❌ FAIL: CSS fix not included in the page")
                results['tests'].append({'name': 'CSS Fix Included', 'status': 'FAIL'})
                results['summary']['failed'] += 1
            results['summary']['total'] += 1
            
        else:
            print("❌ FAIL: Mode toggle container not found")
            results['tests'].append({'name': 'Mode Toggle Exists', 'status': 'FAIL'})
            results['summary']['failed'] += 1
        results['summary']['total'] += 1
        
    else:
        print(f"❌ FAIL: Page returned status {response.status_code}")
        results['tests'].append({'name': 'Page Load', 'status': 'FAIL', 'status_code': response.status_code})
        results['summary']['failed'] += 1
    results['summary']['total'] += 1
    
    # Print Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {results['summary']['total']}")
    print(f"Passed: {results['summary']['passed']} ✅")
    print(f"Failed: {results['summary']['failed']} ❌")
    print(f"Success Rate: {(results['summary']['passed']/results['summary']['total']*100):.1f}%")
    
    # Save results
    with open('qa_mode_toggle_position_fix.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: qa_mode_toggle_position_fix.json")
    
    # Overall result
    if results['summary']['failed'] == 0:
        print("\n🎉 ALL TESTS PASSED! Mode toggle position fix is working correctly.")
        return True
    else:
        print(f"\n⚠️ {results['summary']['failed']} test(s) failed. Please review the issues.")
        return False

if __name__ == '__main__':
    success = test_mode_toggle_position()
    sys.exit(0 if success else 1)
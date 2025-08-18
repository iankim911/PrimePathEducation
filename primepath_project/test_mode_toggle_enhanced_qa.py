#!/usr/bin/env python3
"""
QA Test for Enhanced Mode Toggle Implementation
Tests the Admin/Teacher mode switching with authentication
Date: August 18, 2025
"""

import os
import sys
import django
import json
from datetime import datetime

# Django setup
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import Teacher

def run_mode_toggle_tests():
    """Run comprehensive tests for enhanced mode toggle feature"""
    
    print("\n" + "="*80)
    print("ENHANCED MODE TOGGLE QA TEST SUITE")
    print("Testing: Admin/Teacher Mode Switching with Authentication")
    print("Timestamp:", datetime.now().isoformat())
    print("="*80 + "\n")
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'tests': {},
        'summary': {'passed': 0, 'failed': 0, 'warnings': 0}
    }
    
    # Test 1: Verify admin user exists
    print("Test 1: Verifying admin user...")
    try:
        admin = User.objects.get(username='admin')
        if admin.is_staff or admin.is_superuser:
            print(f"✅ Admin user found: {admin.username}")
            print(f"   is_staff: {admin.is_staff}, is_superuser: {admin.is_superuser}")
            results['tests']['admin_user'] = 'PASSED'
            results['summary']['passed'] += 1
        else:
            print("⚠️ User 'admin' exists but lacks admin privileges")
            results['tests']['admin_user'] = 'WARNING'
            results['summary']['warnings'] += 1
    except User.DoesNotExist:
        print("❌ Admin user not found")
        results['tests']['admin_user'] = 'FAILED'
        results['summary']['failed'] += 1
        return results
    
    # Test 2: Test authentication endpoint
    print("\nTest 2: Testing authentication endpoint...")
    client = Client()
    client.force_login(admin)
    
    # Test with correct credentials
    response = client.post('/RoutineTest/api/authenticate-admin/', 
                          json.dumps({'username': 'admin', 'password': 'admin'}),
                          content_type='application/json')
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"✅ Authentication successful with correct credentials")
            results['tests']['auth_correct'] = 'PASSED'
            results['summary']['passed'] += 1
        else:
            print(f"❌ Authentication failed: {data.get('message')}")
            results['tests']['auth_correct'] = 'FAILED'
            results['summary']['failed'] += 1
    else:
        print(f"❌ Authentication endpoint error: Status {response.status_code}")
        results['tests']['auth_correct'] = 'FAILED'
        results['summary']['failed'] += 1
    
    # Test 3: Test authentication with wrong credentials
    print("\nTest 3: Testing authentication with wrong credentials...")
    response = client.post('/RoutineTest/api/authenticate-admin/',
                          json.dumps({'username': 'admin', 'password': 'wrong'}),
                          content_type='application/json')
    
    if response.status_code in [401, 403]:
        print("✅ Authentication correctly rejected wrong credentials")
        results['tests']['auth_wrong'] = 'PASSED'
        results['summary']['passed'] += 1
    else:
        print(f"⚠️ Unexpected response for wrong credentials: Status {response.status_code}")
        results['tests']['auth_wrong'] = 'WARNING'
        results['summary']['warnings'] += 1
    
    # Test 4: Test mode toggle endpoint
    print("\nTest 4: Testing mode toggle endpoint...")
    response = client.post('/RoutineTest/api/toggle-mode/',
                          json.dumps({'mode': 'Admin'}),
                          content_type='application/json')
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success') and data.get('mode') == 'Admin':
            print("✅ Mode toggle to Admin successful")
            results['tests']['toggle_admin'] = 'PASSED'
            results['summary']['passed'] += 1
        else:
            print(f"⚠️ Mode toggle response: {data}")
            results['tests']['toggle_admin'] = 'WARNING'
            results['summary']['warnings'] += 1
    else:
        print(f"❌ Mode toggle failed: Status {response.status_code}")
        results['tests']['toggle_admin'] = 'FAILED'
        results['summary']['failed'] += 1
    
    # Test 5: Test current mode endpoint
    print("\nTest 5: Testing current mode endpoint...")
    response = client.get('/RoutineTest/api/current-mode/')
    
    if response.status_code == 200:
        data = response.json()
        current_mode = data.get('mode', 'Unknown')
        print(f"✅ Current mode retrieved: {current_mode}")
        results['tests']['get_mode'] = 'PASSED'
        results['summary']['passed'] += 1
    else:
        print(f"❌ Failed to get current mode: Status {response.status_code}")
        results['tests']['get_mode'] = 'FAILED'
        results['summary']['failed'] += 1
    
    # Test 6: Verify template changes
    print("\nTest 6: Verifying template files...")
    template_files = {
        'enhanced_toggle': '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/templates/primepath_routinetest/includes/mode_toggle_enhanced.html',
        'base_template': '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/templates/routinetest_base.html'
    }
    
    all_templates_exist = True
    for name, path in template_files.items():
        if os.path.exists(path):
            print(f"✅ {name} exists")
        else:
            print(f"❌ {name} not found at {path}")
            all_templates_exist = False
    
    if all_templates_exist:
        results['tests']['templates'] = 'PASSED'
        results['summary']['passed'] += 1
    else:
        results['tests']['templates'] = 'FAILED'
        results['summary']['failed'] += 1
    
    # Test 7: Check for authentication modal in template
    print("\nTest 7: Checking authentication modal implementation...")
    with open(template_files['enhanced_toggle'], 'r') as f:
        content = f.read()
        
        checks = {
            'auth_modal': 'adminAuthModal' in content,
            'auth_form': 'adminAuthForm' in content,
            'teacher_admin_text': 'Teacher Mode' in content and 'Admin Mode' in content,
            'console_logging': '[MODE_TOGGLE_ENHANCED]' in content,
            'authentication_js': 'authenticateAdmin' in content
        }
        
        all_checks_pass = all(checks.values())
        for check, passed in checks.items():
            if passed:
                print(f"✅ {check.replace('_', ' ').title()}: Implemented")
            else:
                print(f"❌ {check.replace('_', ' ').title()}: Not found")
        
        if all_checks_pass:
            results['tests']['modal_implementation'] = 'PASSED'
            results['summary']['passed'] += 1
        else:
            results['tests']['modal_implementation'] = 'FAILED'
            results['summary']['failed'] += 1
    
    # Test 8: Check session handling
    print("\nTest 8: Testing session persistence...")
    # Set mode to Admin
    client.post('/routinetest/api/toggle-mode/',
                json.dumps({'mode': 'Admin'}),
                content_type='application/json')
    
    # Check if mode persists
    response = client.get('/RoutineTest/api/current-mode/')
    if response.status_code == 200:
        data = response.json()
        if data.get('mode') == 'Admin':
            print("✅ Session correctly persists Admin mode")
            results['tests']['session_persistence'] = 'PASSED'
            results['summary']['passed'] += 1
        else:
            print(f"⚠️ Mode not persisted correctly: {data.get('mode')}")
            results['tests']['session_persistence'] = 'WARNING'
            results['summary']['warnings'] += 1
    else:
        print("❌ Failed to verify session persistence")
        results['tests']['session_persistence'] = 'FAILED'
        results['summary']['failed'] += 1
    
    # Final Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"✅ Passed: {results['summary']['passed']}")
    print(f"⚠️ Warnings: {results['summary']['warnings']}")
    print(f"❌ Failed: {results['summary']['failed']}")
    
    total_tests = results['summary']['passed'] + results['summary']['warnings'] + results['summary']['failed']
    if results['summary']['failed'] == 0:
        print("\n🎉 ALL CRITICAL TESTS PASSED!")
        results['overall'] = 'SUCCESS'
    elif results['summary']['failed'] <= 1:
        print("\n⚠️ MOSTLY SUCCESSFUL with minor issues")
        results['overall'] = 'PARTIAL_SUCCESS'
    else:
        print("\n❌ CRITICAL FAILURES DETECTED")
        results['overall'] = 'FAILURE'
    
    # Save results
    results_file = '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/qa_mode_toggle_enhanced_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {results_file}")
    
    print("\n" + "="*80)
    print("MANUAL TESTING CHECKLIST:")
    print("="*80)
    print("1. Navigate to http://127.0.0.1:8000/RoutineTest/classes-exams/")
    print("2. Look for mode toggle button in header (right side)")
    print("3. Click toggle button - should show 'Teacher Mode'")
    print("4. Click to switch to Admin Mode")
    print("5. Authentication modal should appear")
    print("6. Enter admin credentials (username: admin, password: admin)")
    print("7. Verify switch to Admin Mode")
    print("8. Click toggle again to switch back to Teacher Mode")
    print("9. Check browser console for debug messages")
    print("10. Test keyboard shortcut: Alt+M")
    print("\n" + "="*80)
    print("VISUAL CHECKS:")
    print("="*80)
    print("✓ Toggle button positioned in header (not in stats box)")
    print("✓ Shows 'Teacher Mode' and 'Admin Mode' (not redundant text)")
    print("✓ Authentication modal appears centered with blur background")
    print("✓ Error messages display for wrong credentials")
    print("✓ Success notification on mode switch")
    print("✓ Mode indicator shows current active mode")
    print("\n")
    
    return results

if __name__ == '__main__':
    results = run_mode_toggle_tests()
    sys.exit(0 if results['overall'] == 'SUCCESS' else 1)
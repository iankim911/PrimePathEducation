#!/usr/bin/env python3
"""
QA Test for Column Visibility Implementation
Tests the Review vs Quarterly tab functionality in Classes & Exams page
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

def run_column_visibility_tests():
    """Run comprehensive tests for column visibility feature"""
    
    print("\n" + "="*80)
    print("COLUMN VISIBILITY QA TEST SUITE")
    print("Testing: Review vs Quarterly Tab Column Hiding")
    print("Timestamp:", datetime.now().isoformat())
    print("="*80 + "\n")
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'tests': {},
        'summary': {'passed': 0, 'failed': 0, 'warnings': 0}
    }
    
    # Test 1: Verify user access
    print("Test 1: Verifying admin user access...")
    try:
        admin = User.objects.get(username='admin')
        teacher = Teacher.objects.filter(user=admin).first()
        if teacher:
            print("✅ Admin user and teacher profile found")
            results['tests']['user_access'] = 'PASSED'
            results['summary']['passed'] += 1
        else:
            print("⚠️ Admin user found but no teacher profile")
            results['tests']['user_access'] = 'WARNING'
            results['summary']['warnings'] += 1
    except User.DoesNotExist:
        print("❌ Admin user not found")
        results['tests']['user_access'] = 'FAILED'
        results['summary']['failed'] += 1
    
    # Test 2: Test page accessibility
    print("\nTest 2: Testing Classes & Exams page accessibility...")
    client = Client()
    client.force_login(admin)
    
    response = client.get('/RoutineTest/classes-exams/')
    if response.status_code == 200:
        print(f"✅ Page loaded successfully (Status: {response.status_code})")
        results['tests']['page_load'] = 'PASSED'
        results['summary']['passed'] += 1
    else:
        print(f"❌ Page failed to load (Status: {response.status_code})")
        results['tests']['page_load'] = 'FAILED'
        results['summary']['failed'] += 1
    
    # Test 3: Verify template changes
    print("\nTest 3: Verifying template modifications...")
    template_path = '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/templates/primepath_routinetest/classes_exams_unified.html'
    
    checks = {
        'tab_label_changed': False,
        'column_classes_added': False,
        'visibility_js_added': False,
        'console_logging_added': False
    }
    
    try:
        with open(template_path, 'r') as f:
            content = f.read()
            
            # Check tab label change
            if '<span>Review</span>' in content and '<span>Review/Monthly</span>' not in content:
                checks['tab_label_changed'] = True
                print("✅ Tab label changed from 'Review/Monthly' to 'Review'")
            else:
                print("❌ Tab label not properly changed")
            
            # Check column classes
            if 'monthly-column' in content and 'quarterly-column' in content:
                checks['column_classes_added'] = True
                print("✅ Column identification classes added")
            else:
                print("❌ Column classes not found")
            
            # Check visibility JavaScript
            if 'col.style.display = \'none\'' in content:
                checks['visibility_js_added'] = True
                print("✅ Column visibility JavaScript implemented")
            else:
                print("❌ Column visibility JavaScript not found")
            
            # Check console logging
            if '[COLUMN_VISIBILITY]' in content and '[COLUMN_DETECTION]' in content:
                checks['console_logging_added'] = True
                print("✅ Comprehensive console logging added")
            else:
                print("❌ Console logging not comprehensive")
            
            # Update results
            if all(checks.values()):
                results['tests']['template_changes'] = 'PASSED'
                results['summary']['passed'] += 1
            elif any(checks.values()):
                results['tests']['template_changes'] = 'PARTIAL'
                results['summary']['warnings'] += 1
            else:
                results['tests']['template_changes'] = 'FAILED'
                results['summary']['failed'] += 1
                
    except FileNotFoundError:
        print("❌ Template file not found")
        results['tests']['template_changes'] = 'FAILED'
        results['summary']['failed'] += 1
    
    # Test 4: Verify data structure
    print("\nTest 4: Verifying data structure...")
    if 'timeslots' in response.context:
        timeslots = response.context['timeslots']
        months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
                  'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        quarters = ['Q1', 'Q2', 'Q3', 'Q4']
        
        expected_timeslots = months + quarters
        if timeslots == expected_timeslots:
            print(f"✅ Timeslots structure correct: {len(timeslots)} periods (12 months + 4 quarters)")
            results['tests']['data_structure'] = 'PASSED'
            results['summary']['passed'] += 1
        else:
            print(f"❌ Timeslots mismatch. Expected {len(expected_timeslots)}, got {len(timeslots)}")
            results['tests']['data_structure'] = 'FAILED'
            results['summary']['failed'] += 1
    else:
        print("⚠️ Timeslots not found in context")
        results['tests']['data_structure'] = 'WARNING'
        results['summary']['warnings'] += 1
    
    # Test 5: Performance check
    print("\nTest 5: Performance check...")
    import time
    start = time.time()
    response = client.get('/RoutineTest/classes-exams/')
    load_time = time.time() - start
    
    if load_time < 2.0:
        print(f"✅ Page loads quickly ({load_time:.2f}s)")
        results['tests']['performance'] = 'PASSED'
        results['summary']['passed'] += 1
    elif load_time < 5.0:
        print(f"⚠️ Page loads slowly ({load_time:.2f}s)")
        results['tests']['performance'] = 'WARNING'
        results['summary']['warnings'] += 1
    else:
        print(f"❌ Page loads too slowly ({load_time:.2f}s)")
        results['tests']['performance'] = 'FAILED'
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
    results_file = '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/qa_column_visibility_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {results_file}")
    
    print("\n" + "="*80)
    print("RECOMMENDED MANUAL TESTS:")
    print("="*80)
    print("1. Open http://127.0.0.1:8000/RoutineTest/classes-exams/")
    print("2. Click 'Quarterly' tab - verify only Q1-Q4 columns show")
    print("3. Click 'Review' tab - verify only monthly columns show")
    print("4. Check browser console for debug messages")
    print("5. Test keyboard shortcuts: Alt+1 (Review), Alt+2 (Quarterly)")
    print("\n")
    
    return results

if __name__ == '__main__':
    results = run_column_visibility_tests()
    sys.exit(0 if results['overall'] == 'SUCCESS' else 1)
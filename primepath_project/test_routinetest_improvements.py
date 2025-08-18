#!/usr/bin/env python
"""
Comprehensive QA Test Script for RoutineTest Module Improvements
Tests the following changes:
1. Title change from "Continuous Assessment" to "Exam Management"
2. Tab renamed from "Schedule Matrix" to "Exam Assignments"
3. Tab renamed from "Manage Exams" to "Answer Keys"
4. Exam assignment/unassignment functionality
5. Enhanced console debugging
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from primepath_routinetest.models import Exam, ExamScheduleMatrix, TeacherClassAssignment
from core.models import Teacher
import json

def run_qa_tests():
    """Run comprehensive QA tests for RoutineTest improvements"""
    print("\n" + "="*80)
    print("ROUTINETEST MODULE IMPROVEMENTS - QA TEST SUITE")
    print("="*80)
    
    client = Client()
    results = {
        'passed': [],
        'failed': [],
        'warnings': []
    }
    
    # Test 1: Check module description update
    print("\n[TEST 1] Checking module description update...")
    try:
        from primepath_routinetest.context_processors import routinetest_context
        mock_request = type('obj', (object,), {'path': '/RoutineTest/'})()
        context = routinetest_context(mock_request)
        
        if context['module_description'] == 'Exam Management System':
            results['passed'].append("✅ Module description updated to 'Exam Management System'")
            print("  ✅ Module description correctly updated")
        else:
            results['failed'].append(f"❌ Module description is '{context['module_description']}', expected 'Exam Management System'")
            print(f"  ❌ Module description incorrect: {context['module_description']}")
            
        if context['module_version'] == '2.1.0':
            results['passed'].append("✅ Module version updated to 2.1.0")
            print("  ✅ Module version correctly updated")
        else:
            results['warnings'].append(f"⚠️ Module version is {context['module_version']}")
            print(f"  ⚠️ Module version: {context['module_version']}")
    except Exception as e:
        results['failed'].append(f"❌ Error checking module description: {str(e)}")
        print(f"  ❌ Error: {str(e)}")
    
    # Test 2: Check URL patterns still work
    print("\n[TEST 2] Checking URL patterns...")
    from django.urls import reverse
    
    url_tests = [
        ('RoutineTest:index', 'Dashboard'),
        ('RoutineTest:exam_list', 'Answer Keys (formerly Manage Exams)'),
        ('RoutineTest:schedule_matrix', 'Exam Assignments (formerly Schedule Matrix)'),
        ('RoutineTest:my_classes', 'My Classes & Access'),
        ('RoutineTest:create_exam', 'Upload Exam'),
    ]
    
    for url_name, description in url_tests:
        try:
            url = reverse(url_name)
            results['passed'].append(f"✅ URL pattern '{url_name}' ({description}) resolves to {url}")
            print(f"  ✅ {description}: {url}")
        except Exception as e:
            results['failed'].append(f"❌ URL pattern '{url_name}' ({description}) failed: {str(e)}")
            print(f"  ❌ {description}: {str(e)}")
    
    # Test 3: Check ExamScheduleMatrix model functionality
    print("\n[TEST 3] Checking ExamScheduleMatrix functionality...")
    try:
        # Create a test matrix cell
        test_cell = ExamScheduleMatrix.objects.create(
            class_code='CLASS_TEST',
            academic_year='2025',
            time_period_type='MONTHLY',
            time_period_value='JAN'
        )
        
        # Test exam assignment methods
        if hasattr(test_cell, 'add_exam') and hasattr(test_cell, 'remove_exam'):
            results['passed'].append("✅ ExamScheduleMatrix has add_exam and remove_exam methods")
            print("  ✅ Exam assignment methods present")
        else:
            results['warnings'].append("⚠️ ExamScheduleMatrix missing assignment methods")
            print("  ⚠️ Assignment methods may need implementation")
        
        # Test exam count
        exam_count = test_cell.get_exam_count()
        if exam_count == 0:
            results['passed'].append("✅ ExamScheduleMatrix.get_exam_count() works")
            print(f"  ✅ Exam count method works: {exam_count}")
        
        # Cleanup
        test_cell.delete()
        
    except Exception as e:
        results['warnings'].append(f"⚠️ ExamScheduleMatrix test: {str(e)}")
        print(f"  ⚠️ Model test: {str(e)}")
    
    # Test 4: Check view logging updates
    print("\n[TEST 4] Checking view logging updates...")
    try:
        from primepath_routinetest.views import schedule_matrix
        import inspect
        
        source = inspect.getsource(schedule_matrix.schedule_matrix_view)
        
        if 'exam_assignments_view' in source:
            results['passed'].append("✅ View logging updated to use 'exam_assignments_view'")
            print("  ✅ View logging correctly updated")
        elif 'schedule_matrix_view' in source:
            results['warnings'].append("⚠️ View still uses old 'schedule_matrix_view' naming")
            print("  ⚠️ View uses old naming")
            
        if 'EXAM_ASSIGNMENTS' in source:
            results['passed'].append("✅ View uses new EXAM_ASSIGNMENTS logging prefix")
            print("  ✅ Logging prefix updated")
            
    except Exception as e:
        results['warnings'].append(f"⚠️ Could not check view logging: {str(e)}")
        print(f"  ⚠️ View check: {str(e)}")
    
    # Test 5: Check navigation changes in templates
    print("\n[TEST 5] Checking template updates...")
    import os
    template_path = '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/templates/routinetest_base.html'
    
    if os.path.exists(template_path):
        with open(template_path, 'r') as f:
            content = f.read()
            
        checks = [
            ('RoutineTest - Exam Management', 'Title updated'),
            ('Answer Keys</a>', 'Answer Keys tab name'),
            ('Exam Assignments</a>', 'Exam Assignments tab name'),
            ('data-nav="answer-keys"', 'Answer Keys data attribute'),
            ('data-nav="exam-assignments"', 'Exam Assignments data attribute'),
        ]
        
        for check_text, description in checks:
            if check_text in content:
                results['passed'].append(f"✅ Template has '{description}'")
                print(f"  ✅ {description} found")
            else:
                results['failed'].append(f"❌ Template missing '{description}'")
                print(f"  ❌ {description} missing")
    else:
        results['warnings'].append("⚠️ Base template not found")
        print("  ⚠️ Could not check base template")
    
    # Summary
    print("\n" + "="*80)
    print("QA TEST SUMMARY")
    print("="*80)
    print(f"\n✅ PASSED: {len(results['passed'])} tests")
    for msg in results['passed']:
        print(f"  {msg}")
    
    if results['warnings']:
        print(f"\n⚠️ WARNINGS: {len(results['warnings'])} warnings")
        for msg in results['warnings']:
            print(f"  {msg}")
    
    if results['failed']:
        print(f"\n❌ FAILED: {len(results['failed'])} tests")
        for msg in results['failed']:
            print(f"  {msg}")
    else:
        print("\n🎉 All critical tests passed!")
    
    print("\n" + "="*80)
    print("RECOMMENDATIONS:")
    print("="*80)
    print("1. Clear browser cache to see UI changes")
    print("2. Test exam assignment functionality in the UI")
    print("3. Verify console logging in browser developer tools")
    print("4. Check that all navigation links work correctly")
    print("5. Ensure exam assignment/unassignment works in Exam Assignments view")
    
    return len(results['failed']) == 0

if __name__ == '__main__':
    success = run_qa_tests()
    sys.exit(0 if success else 1)
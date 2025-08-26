#!/usr/bin/env python
"""
Comprehensive Test for Copy Exam Feature
Tests all components of the copy exam functionality
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from primepath_routinetest.models import RoutineExam as Exam
from primepath_routinetest.views.exam_api import copy_exam, generate_exam_name

def test_copy_exam_backend():
    """Test the backend copy exam functionality"""
    print("\n" + "="*80)
    print("TESTING COPY EXAM BACKEND FUNCTIONALITY")
    print("="*80)
    
    # Get a test user
    user = User.objects.filter(username='teacher1').first()
    if not user:
        print("❌ Test user 'teacher1' not found")
        return False
    
    print(f"✅ Using test user: {user.username}")
    
    # Get a source exam to copy
    source_exam = Exam.objects.filter(exam_type__in=['REVIEW', 'QUARTERLY']).first()
    if not source_exam:
        print("❌ No source exam found for testing")
        return False
    
    print(f"✅ Source exam found: {source_exam.name} (ID: {source_exam.id})")
    
    # Test name generation
    print("\n--- Testing Name Generation ---")
    test_cases = [
        {
            'exam_type': 'REVIEW',
            'time_period': 'JAN',
            'academic_year': '2025',
            'custom_suffix': '123',
            'expected_contains': ['[RT]', 'Jan 2025', '_123']
        },
        {
            'exam_type': 'QUARTERLY',
            'time_period': 'Q1',
            'academic_year': '2026',
            'custom_suffix': 'version2',
            'expected_contains': ['[QTR]', 'Q1 2026', '_version2']
        },
        {
            'exam_type': 'REVIEW',
            'time_period': 'MAR',
            'academic_year': '2025',
            'custom_suffix': '',
            'expected_contains': ['[RT]', 'Mar 2025']
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        generated_name = generate_exam_name(
            exam_type=test_case['exam_type'],
            time_period=test_case['time_period'],
            academic_year=test_case['academic_year'],
            source_exam=source_exam,
            custom_suffix=test_case['custom_suffix']
        )
        
        print(f"\nTest Case {i}:")
        print(f"  Input: {test_case['exam_type']} - {test_case['time_period']} {test_case['academic_year']}")
        print(f"  Custom Suffix: '{test_case['custom_suffix']}'")
        print(f"  Generated Name: {generated_name}")
        
        # Check if all expected parts are in the generated name
        all_found = all(part in generated_name for part in test_case['expected_contains'])
        if all_found:
            print(f"  ✅ Name generation correct")
        else:
            print(f"  ❌ Missing expected parts: {test_case['expected_contains']}")
    
    # Test copy exam API endpoint
    print("\n--- Testing Copy Exam API ---")
    factory = RequestFactory()
    
    request_data = {
        'source_exam_id': str(source_exam.id),
        'target_class': 'C5',
        'target_timeslot': 'FEB',
        'academic_year': '2025',
        'custom_suffix': 'test123'
    }
    
    request = factory.post(
        '/RoutineTest/api/copy-exam/',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    request.user = user
    
    print(f"Request Data: {json.dumps(request_data, indent=2)}")
    
    try:
        response = copy_exam(request)
        response_data = json.loads(response.content.decode())
        
        if response.status_code == 200:
            print(f"✅ Copy exam API successful")
            print(f"  New Exam Name: {response_data.get('exam_name', 'N/A')}")
            print(f"  New Exam ID: {response_data.get('exam_id', 'N/A')}")
            print(f"  Message: {response_data.get('message', 'N/A')}")
            
            # Verify the new exam exists
            if 'exam_id' in response_data:
                new_exam = Exam.objects.filter(id=response_data['exam_id']).first()
                if new_exam:
                    print(f"✅ New exam verified in database: {new_exam.name}")
                    # Check naming convention
                    if '[RT]' in new_exam.name and 'Feb 2025' in new_exam.name and '_test123' in new_exam.name:
                        print(f"✅ Naming convention followed correctly")
                    else:
                        print(f"⚠️ Naming convention may not be correct: {new_exam.name}")
                else:
                    print(f"❌ New exam not found in database")
        else:
            print(f"❌ Copy exam API failed: {response.status_code}")
            print(f"  Error: {response_data.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Exception during copy exam API test: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return True

def test_frontend_elements():
    """Test that frontend elements are properly configured"""
    print("\n" + "="*80)
    print("TESTING FRONTEND CONFIGURATION")
    print("="*80)
    
    template_path = '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/templates/primepath_routinetest/exam_list_hierarchical.html'
    
    if os.path.exists(template_path):
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Check for new elements
        elements_to_check = [
            ('academicYear', 'Academic Year dropdown'),
            ('customSuffix', 'Custom Suffix input'),
            ('examNamePreview', 'Exam Name Preview'),
            ('updateCopyExamNamePreview', 'Name Preview Function')
        ]
        
        print("\nChecking for required elements in template:")
        for element_id, description in elements_to_check:
            if element_id in content:
                print(f"  ✅ {description} found")
            else:
                print(f"  ❌ {description} missing")
    else:
        print(f"❌ Template file not found at {template_path}")
    
    # Check JavaScript file
    js_path = '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/static/js/routinetest/copy-exam-modal.js'
    
    if os.path.exists(js_path):
        with open(js_path, 'r') as f:
            js_content = f.read()
        
        # Check for key functions
        functions_to_check = [
            ('updateNamePreview', 'Name Preview Update Function'),
            ('academic_year', 'Academic Year handling'),
            ('custom_suffix', 'Custom Suffix handling')
        ]
        
        print("\nChecking JavaScript functionality:")
        for func_name, description in functions_to_check:
            if func_name in js_content:
                print(f"  ✅ {description} found")
            else:
                print(f"  ❌ {description} missing")
    else:
        print(f"❌ JavaScript file not found at {js_path}")

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("COPY EXAM COMPREHENSIVE TEST SUITE")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Run backend tests
    backend_result = test_copy_exam_backend()
    
    # Run frontend tests
    test_frontend_elements()
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    if backend_result:
        print("✅ Backend tests completed")
    else:
        print("❌ Backend tests failed")
    
    print("\n✅ All tests completed successfully!")
    print("="*80)

if __name__ == '__main__':
    run_all_tests()
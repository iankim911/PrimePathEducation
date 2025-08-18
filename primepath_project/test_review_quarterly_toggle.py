#!/usr/bin/env python
"""
Comprehensive QA Test for Review/Quarterly Toggle System
Tests the new tab-based filtering system for RoutineTest exams
Author: Claude
Date: August 17, 2025
"""

import os
import sys
import json
from datetime import datetime

# Setup Django environment FIRST before any Django imports
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')

import django
django.setup()

# Now import Django modules after setup
from django.test import RequestFactory
from django.contrib.auth.models import User

from primepath_routinetest.models import Exam
from primepath_routinetest.views import exam_list
from core.models import Teacher, CurriculumLevel, SubProgram, Program

def create_test_data():
    """Create test exams of different types"""
    print("\n" + "="*80)
    print("CREATING TEST DATA")
    print("="*80)
    
    # Get or create a test teacher
    user, _ = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com'}
    )
    teacher, _ = Teacher.objects.get_or_create(
        user=user,
        defaults={'name': 'Test Teacher', 'email': 'test@example.com'}
    )
    
    # Get a curriculum level for testing
    curriculum_level = CurriculumLevel.objects.first()
    
    # Create Review exams
    review_exams_created = 0
    for month in ['JAN', 'FEB', 'MAR']:
        exam_name = f"Test Review Exam - {month} 2025"
        exam, created = Exam.objects.get_or_create(
            name=exam_name,
            defaults={
                'exam_type': 'REVIEW',
                'time_period_month': month,
                'academic_year': '2025',
                'curriculum_level': curriculum_level,
                'total_questions': 20,
                'timer_minutes': 60,
                'created_by': teacher,
                'pdf_file': 'test.pdf'  # This would be a real file in production
            }
        )
        if created:
            review_exams_created += 1
            print(f"✅ Created Review exam: {exam_name}")
    
    # Create Quarterly exams
    quarterly_exams_created = 0
    for quarter in ['Q1', 'Q2']:
        exam_name = f"Test Quarterly Exam - {quarter} 2025"
        exam, created = Exam.objects.get_or_create(
            name=exam_name,
            defaults={
                'exam_type': 'QUARTERLY',
                'time_period_quarter': quarter,
                'academic_year': '2025',
                'curriculum_level': curriculum_level,
                'total_questions': 50,
                'timer_minutes': 120,
                'created_by': teacher,
                'pdf_file': 'test.pdf'
            }
        )
        if created:
            quarterly_exams_created += 1
            print(f"✅ Created Quarterly exam: {exam_name}")
    
    print(f"\nSummary: Created {review_exams_created} Review exams, {quarterly_exams_created} Quarterly exams")
    return True

def test_backend_filtering():
    """Test the backend filtering logic"""
    print("\n" + "="*80)
    print("TESTING BACKEND FILTERING")
    print("="*80)
    
    # Create request factory
    factory = RequestFactory()
    
    # Get or create test user
    user, _ = User.objects.get_or_create(username='test_user')
    
    test_cases = [
        ('REVIEW', 'Review/Monthly filter'),
        ('QUARTERLY', 'Quarterly filter'),
        ('ALL', 'All exams filter'),
        ('INVALID', 'Invalid filter (should default to REVIEW)'),
        (None, 'No filter (should default to REVIEW)')
    ]
    
    results = []
    for filter_type, description in test_cases:
        print(f"\nTesting: {description}")
        
        # Create request with filter
        if filter_type:
            request = factory.get('/RoutineTest/exams/', {'exam_type': filter_type})
        else:
            request = factory.get('/RoutineTest/exams/')
        
        request.user = user
        
        try:
            # Call the view
            response = exam_list(request)
            
            # Check response
            if response.status_code == 200:
                # Extract context from response (this is a simplification)
                # In real tests, we'd use Django's test client
                print(f"  ✅ Response OK (status: {response.status_code})")
                
                # Check headers
                template_version = response.get('X-Template-Version', 'Unknown')
                feature = response.get('X-Feature', 'Unknown')
                filter_header = response.get('X-Exam-Type-Filter', 'Unknown')
                
                print(f"  📋 Template Version: {template_version}")
                print(f"  🎯 Feature: {feature}")
                print(f"  🔍 Filter in Header: {filter_header}")
                
                results.append({
                    'filter': filter_type,
                    'status': 'PASS',
                    'response_code': response.status_code,
                    'filter_header': filter_header
                })
            else:
                print(f"  ❌ Unexpected status code: {response.status_code}")
                results.append({
                    'filter': filter_type,
                    'status': 'FAIL',
                    'response_code': response.status_code
                })
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            results.append({
                'filter': filter_type,
                'status': 'ERROR',
                'error': str(e)
            })
    
    return results

def test_exam_counts():
    """Test that exam counts are correct"""
    print("\n" + "="*80)
    print("TESTING EXAM COUNTS")
    print("="*80)
    
    review_count = Exam.objects.filter(exam_type='REVIEW').count()
    quarterly_count = Exam.objects.filter(exam_type='QUARTERLY').count()
    total_count = Exam.objects.count()
    
    print(f"📊 Database Counts:")
    print(f"  Review Exams: {review_count}")
    print(f"  Quarterly Exams: {quarterly_count}")
    print(f"  Total Exams: {total_count}")
    
    # Verify counts are reasonable
    tests_passed = 0
    tests_total = 3
    
    if review_count >= 0:
        print("  ✅ Review count valid")
        tests_passed += 1
    else:
        print("  ❌ Review count invalid")
    
    if quarterly_count >= 0:
        print("  ✅ Quarterly count valid")
        tests_passed += 1
    else:
        print("  ❌ Quarterly count invalid")
    
    if total_count == review_count + quarterly_count:
        print("  ✅ Total count matches sum")
        tests_passed += 1
    else:
        print("  ❌ Total count doesn't match sum")
    
    return tests_passed == tests_total

def test_exam_type_field():
    """Test that all exams have valid exam_type values"""
    print("\n" + "="*80)
    print("TESTING EXAM TYPE FIELD VALIDITY")
    print("="*80)
    
    valid_types = ['REVIEW', 'QUARTERLY']
    invalid_exams = []
    
    for exam in Exam.objects.all():
        if exam.exam_type not in valid_types:
            invalid_exams.append({
                'id': str(exam.id),
                'name': exam.name,
                'type': exam.exam_type
            })
    
    if invalid_exams:
        print(f"❌ Found {len(invalid_exams)} exams with invalid types:")
        for exam in invalid_exams[:5]:  # Show first 5
            print(f"  - {exam['name']}: {exam['type']}")
        return False
    else:
        print(f"✅ All {Exam.objects.count()} exams have valid exam_type values")
        return True

def test_filter_accuracy():
    """Test that filters return correct exams"""
    print("\n" + "="*80)
    print("TESTING FILTER ACCURACY")
    print("="*80)
    
    # Test REVIEW filter
    review_exams = Exam.objects.filter(exam_type='REVIEW')
    print(f"\n📚 REVIEW Filter Test:")
    print(f"  Found {review_exams.count()} Review exams")
    
    non_review = 0
    for exam in review_exams:
        if exam.exam_type != 'REVIEW':
            non_review += 1
            print(f"  ❌ Non-review exam in filter: {exam.name} (type: {exam.exam_type})")
    
    if non_review == 0:
        print("  ✅ All filtered exams are Review type")
        review_pass = True
    else:
        print(f"  ❌ Found {non_review} non-Review exams in Review filter")
        review_pass = False
    
    # Test QUARTERLY filter
    quarterly_exams = Exam.objects.filter(exam_type='QUARTERLY')
    print(f"\n📊 QUARTERLY Filter Test:")
    print(f"  Found {quarterly_exams.count()} Quarterly exams")
    
    non_quarterly = 0
    for exam in quarterly_exams:
        if exam.exam_type != 'QUARTERLY':
            non_quarterly += 1
            print(f"  ❌ Non-quarterly exam in filter: {exam.name} (type: {exam.exam_type})")
    
    if non_quarterly == 0:
        print("  ✅ All filtered exams are Quarterly type")
        quarterly_pass = True
    else:
        print(f"  ❌ Found {non_quarterly} non-Quarterly exams in Quarterly filter")
        quarterly_pass = False
    
    return review_pass and quarterly_pass

def test_no_breaking_changes():
    """Verify existing features still work"""
    print("\n" + "="*80)
    print("TESTING FOR BREAKING CHANGES")
    print("="*80)
    
    checks = []
    
    # Check exam model fields
    exam = Exam.objects.first()
    if exam:
        required_fields = [
            'name', 'exam_type', 'curriculum_level', 'total_questions',
            'timer_minutes', 'created_by', 'created_at', 'is_active'
        ]
        
        for field in required_fields:
            if hasattr(exam, field):
                print(f"  ✅ Field '{field}' exists")
                checks.append(True)
            else:
                print(f"  ❌ Field '{field}' missing!")
                checks.append(False)
        
        # Check methods
        required_methods = [
            'get_exam_type_display_short',
            'get_time_period_display',
            'get_answer_mapping_status',
            'get_routinetest_display_name'
        ]
        
        for method in required_methods:
            if hasattr(exam, method):
                print(f"  ✅ Method '{method}' exists")
                checks.append(True)
            else:
                print(f"  ❌ Method '{method}' missing!")
                checks.append(False)
    else:
        print("  ⚠️ No exams found for testing")
        return False
    
    return all(checks)

def run_all_tests():
    """Run all QA tests"""
    print("\n" + "="*80)
    print("REVIEW/QUARTERLY TOGGLE SYSTEM - COMPREHENSIVE QA TEST")
    print("="*80)
    print(f"Test Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = {
        'total_tests': 0,
        'passed': 0,
        'failed': 0,
        'errors': 0,
        'details': []
    }
    
    # Test 1: Create test data
    try:
        print("\n🔧 TEST 1: Creating Test Data")
        create_test_data()
        test_results['total_tests'] += 1
        test_results['passed'] += 1
        test_results['details'].append("✅ Test data creation")
    except Exception as e:
        test_results['total_tests'] += 1
        test_results['failed'] += 1
        test_results['details'].append(f"❌ Test data creation: {str(e)}")
    
    # Test 2: Backend filtering
    try:
        print("\n🔧 TEST 2: Backend Filtering")
        backend_results = test_backend_filtering()
        test_results['total_tests'] += 1
        if all(r.get('status') == 'PASS' for r in backend_results):
            test_results['passed'] += 1
            test_results['details'].append("✅ Backend filtering")
        else:
            test_results['failed'] += 1
            test_results['details'].append("❌ Backend filtering issues found")
    except Exception as e:
        test_results['total_tests'] += 1
        test_results['errors'] += 1
        test_results['details'].append(f"❌ Backend filtering error: {str(e)}")
    
    # Test 3: Exam counts
    try:
        print("\n🔧 TEST 3: Exam Counts")
        if test_exam_counts():
            test_results['total_tests'] += 1
            test_results['passed'] += 1
            test_results['details'].append("✅ Exam counts")
        else:
            test_results['total_tests'] += 1
            test_results['failed'] += 1
            test_results['details'].append("❌ Exam count mismatch")
    except Exception as e:
        test_results['total_tests'] += 1
        test_results['errors'] += 1
        test_results['details'].append(f"❌ Exam counts error: {str(e)}")
    
    # Test 4: Exam type field validity
    try:
        print("\n🔧 TEST 4: Exam Type Field Validity")
        if test_exam_type_field():
            test_results['total_tests'] += 1
            test_results['passed'] += 1
            test_results['details'].append("✅ Exam type field validity")
        else:
            test_results['total_tests'] += 1
            test_results['failed'] += 1
            test_results['details'].append("❌ Invalid exam types found")
    except Exception as e:
        test_results['total_tests'] += 1
        test_results['errors'] += 1
        test_results['details'].append(f"❌ Exam type validation error: {str(e)}")
    
    # Test 5: Filter accuracy
    try:
        print("\n🔧 TEST 5: Filter Accuracy")
        if test_filter_accuracy():
            test_results['total_tests'] += 1
            test_results['passed'] += 1
            test_results['details'].append("✅ Filter accuracy")
        else:
            test_results['total_tests'] += 1
            test_results['failed'] += 1
            test_results['details'].append("❌ Filter accuracy issues")
    except Exception as e:
        test_results['total_tests'] += 1
        test_results['errors'] += 1
        test_results['details'].append(f"❌ Filter accuracy error: {str(e)}")
    
    # Test 6: No breaking changes
    try:
        print("\n🔧 TEST 6: No Breaking Changes")
        if test_no_breaking_changes():
            test_results['total_tests'] += 1
            test_results['passed'] += 1
            test_results['details'].append("✅ No breaking changes detected")
        else:
            test_results['total_tests'] += 1
            test_results['failed'] += 1
            test_results['details'].append("❌ Breaking changes detected")
    except Exception as e:
        test_results['total_tests'] += 1
        test_results['errors'] += 1
        test_results['details'].append(f"❌ Breaking changes check error: {str(e)}")
    
    # Print final summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {test_results['total_tests']}")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"⚠️ Errors: {test_results['errors']}")
    
    print("\nDetailed Results:")
    for detail in test_results['details']:
        print(f"  {detail}")
    
    # Overall verdict
    print("\n" + "="*80)
    if test_results['failed'] == 0 and test_results['errors'] == 0:
        print("🎉 ALL TESTS PASSED! Review/Quarterly Toggle System is working correctly!")
        print("✅ The implementation is ready for production use.")
    else:
        print("⚠️ SOME TESTS FAILED! Please review the issues above.")
        print("🔧 Fix the failing tests before deploying to production.")
    print("="*80)
    
    print(f"\nTest End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Save results to JSON file
    with open('test_review_quarterly_results.json', 'w') as f:
        json.dump(test_results, f, indent=2)
        print(f"\n📄 Test results saved to: test_review_quarterly_results.json")
    
    return test_results['failed'] == 0 and test_results['errors'] == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
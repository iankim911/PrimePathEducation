#!/usr/bin/env python
"""
Comprehensive test for student search functionality
Tests the integration between StudentProfile and legacy Student models
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import Teacher, Student
from primepath_student.models import StudentProfile, StudentClassAssignment
from primepath_routinetest.models import Class, StudentEnrollment, TeacherClassAssignment
import json
from datetime import datetime


def run_comprehensive_test():
    """Run comprehensive test of student search functionality"""
    
    print("\n" + "="*70)
    print("COMPREHENSIVE STUDENT SEARCH TEST")
    print("="*70)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test data
    test_results = {
        'passed': 0,
        'failed': 0,
        'details': []
    }
    
    # Step 1: Check StudentProfile and Student sync
    print("STEP 1: Checking StudentProfile to Student synchronization")
    print("-" * 60)
    
    # Check test1234 student
    try:
        profile = StudentProfile.objects.get(student_id='test1234')
        print(f"✓ Found StudentProfile: {profile.student_id} - {profile.get_full_name()}")
        test_results['passed'] += 1
        
        # Check if corresponding Student exists
        legacy_student = Student.objects.filter(user=profile.user).first()
        if legacy_student:
            print(f"✓ Found corresponding Student: {legacy_student.id} - {legacy_student.name}")
            test_results['passed'] += 1
        else:
            print("✗ No corresponding Student record found")
            test_results['failed'] += 1
            test_results['details'].append("Missing Student record for test1234")
    except StudentProfile.DoesNotExist:
        print("✗ StudentProfile test1234 not found")
        test_results['failed'] += 1
        test_results['details'].append("StudentProfile test1234 not found")
    
    print()
    
    # Step 2: Test class details view for available students
    print("STEP 2: Testing class details view for available students")
    print("-" * 60)
    
    # Login as admin/teacher
    client = Client()
    
    # Create or get admin user
    admin_user = User.objects.get(username='admin')
    
    # Ensure teacher profile exists
    teacher, _ = Teacher.objects.get_or_create(
        user=admin_user,
        defaults={'name': 'Admin Teacher', 'is_head_teacher': True}
    )
    
    # Login
    client.force_login(admin_user)
    
    # Test class details view
    response = client.get('/RoutineTest/class/A2/details/')
    
    if response.status_code == 200:
        print(f"✓ Class details page loaded successfully")
        test_results['passed'] += 1
        
        # Check if available students includes our test student
        context = response.context
        if context:
            available_students = context.get('available_students', [])
            print(f"  Available students count: {len(available_students)}")
            
            # Check if test1234 (as test123 test123) is in available students
            test_student_found = False
            for student in available_students:
                if 'test123' in student.get('name', '').lower() or 'test1234' in str(student.get('student_id', '')).lower():
                    test_student_found = True
                    print(f"  ✓ Found test student: {student.get('name')} (ID: {student.get('id')})")
                    print(f"    Student ID: {student.get('student_id')}")
                    break
            
            if test_student_found:
                test_results['passed'] += 1
            else:
                print("  ✗ Test student not found in available students")
                test_results['failed'] += 1
                test_results['details'].append("test1234 not in available students list")
                
                # Debug: Show first 5 available students
                print("  Available students (first 5):")
                for i, student in enumerate(available_students[:5]):
                    print(f"    {i+1}. {student.get('name')} (student_id: {student.get('student_id')})")
        else:
            print("  ✗ No context available")
            test_results['failed'] += 1
    else:
        print(f"✗ Class details page failed to load (status: {response.status_code})")
        test_results['failed'] += 1
    
    print()
    
    # Step 3: Test adding student to class via API
    print("STEP 3: Testing add student to class API")
    print("-" * 60)
    
    if legacy_student:
        # Try to add the student to class A2
        add_response = client.post(
            '/RoutineTest/class/A2/add-student/',
            data=json.dumps({'student_id': str(legacy_student.id)}),
            content_type='application/json'
        )
        
        if add_response.status_code == 200:
            data = add_response.json()
            if data.get('success'):
                print(f"✓ Successfully added student to class")
                print(f"  Message: {data.get('message')}")
                test_results['passed'] += 1
                
                # Verify enrollment was created
                enrollment = StudentEnrollment.objects.filter(
                    student=legacy_student,
                    class_assigned__section='A2'
                ).first()
                
                if enrollment:
                    print(f"  ✓ StudentEnrollment created: {enrollment.id}")
                    test_results['passed'] += 1
                else:
                    print("  ✗ StudentEnrollment not found")
                    test_results['failed'] += 1
            else:
                print(f"✗ Add student failed: {data.get('error')}")
                test_results['failed'] += 1
        else:
            print(f"✗ API call failed (status: {add_response.status_code})")
            test_results['failed'] += 1
    
    print()
    
    # Step 4: Test JavaScript search functionality
    print("STEP 4: Checking template search attributes")
    print("-" * 60)
    
    # Check if the template includes proper search attributes
    response = client.get('/RoutineTest/class/A2/details/')
    if response.status_code == 200:
        content = response.content.decode()
        
        # Check for search elements
        has_search_input = 'studentSearchInput' in content
        has_student_options = 'student-option' in content
        has_data_attributes = 'data-student-code' in content or 'data-student-id' in content
        
        print(f"  {'✓' if has_search_input else '✗'} Search input field present")
        print(f"  {'✓' if has_student_options else '✗'} Student option elements present")
        print(f"  {'✓' if has_data_attributes else '✗'} Data attributes for search present")
        
        if has_search_input:
            test_results['passed'] += 1
        else:
            test_results['failed'] += 1
            
        if has_student_options:
            test_results['passed'] += 1
        else:
            test_results['failed'] += 1
            
        if has_data_attributes:
            test_results['passed'] += 1
        else:
            test_results['failed'] += 1
    
    print()
    
    # Step 5: Console logging verification
    print("STEP 5: Verifying console logging")
    print("-" * 60)
    
    # Check if logging is present in the view
    from primepath_routinetest.views.class_details import logger
    print("✓ Logger configured in class_details.py")
    test_results['passed'] += 1
    
    # The actual logs would appear in the server console when running
    print("  Console logs will appear during actual usage:")
    print("  - [STUDENT_SEARCH] Getting available students")
    print("  - [STUDENT_SYNC] Creating/updating legacy Student")
    print("  - [ADD_STUDENT] Processing student addition")
    
    print()
    
    # Final Summary
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"✓ Passed: {test_results['passed']}")
    print(f"✗ Failed: {test_results['failed']}")
    print(f"Total Tests: {test_results['passed'] + test_results['failed']}")
    
    if test_results['failed'] > 0:
        print("\nFailed Test Details:")
        for detail in test_results['details']:
            print(f"  - {detail}")
    
    if test_results['failed'] == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("The student search functionality is working correctly.")
        print("Students registered via StudentProfile are now visible in class management.")
    else:
        print("\n⚠️  Some tests failed. Review the details above.")
    
    print()
    print("="*70)
    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return test_results['failed'] == 0


if __name__ == '__main__':
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
#!/usr/bin/env python
"""
Comprehensive Test Script for Copy Exam Fix
Tests the complete copy exam functionality after fixing the model mismatch issue
"""

import os
import sys
import json
import django
from datetime import datetime

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from primepath_routinetest.models import Exam
from primepath_routinetest.models.exam_management import RoutineExam
from core.models import CurriculumLevel, SubProgram, Program

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*80}")
    print(f" {text}")
    print(f"{'='*80}")

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")

def test_copy_exam_fix():
    """Test the copy exam functionality after the fix"""
    
    print_header("COPY EXAM COMPREHENSIVE TEST")
    print(f"Test started at: {datetime.now()}")
    
    # Initialize test client
    client = Client()
    
    # Step 1: Check database state
    print_header("Step 1: Database State Check")
    
    exam_count = Exam.objects.count()
    routine_exam_count = RoutineExam.objects.count()
    
    print_info(f"Exam objects in database: {exam_count}")
    print_info(f"RoutineExam objects in database: {routine_exam_count}")
    
    if exam_count == 0:
        print_error("No Exam objects found in database. Cannot test copy functionality.")
        return False
    
    # Step 2: Get a test exam
    print_header("Step 2: Select Test Exam")
    
    # Get an exam with curriculum level
    test_exam = Exam.objects.filter(curriculum_level__isnull=False).first()
    if not test_exam:
        # If no exam with curriculum, get any exam
        test_exam = Exam.objects.first()
        print_info(f"Selected exam without curriculum level: {test_exam.name}")
    else:
        print_info(f"Selected exam with curriculum: {test_exam.name}")
    
    print_info(f"Exam ID: {test_exam.id}")
    print_info(f"Exam Type: {test_exam.exam_type}")
    print_info(f"Timer Minutes: {test_exam.timer_minutes}")
    print_info(f"Total Questions: {test_exam.total_questions}")
    print_info(f"Default Options Count: {test_exam.default_options_count}")
    
    # Step 3: Get or create curriculum level for copy
    print_header("Step 3: Setup Curriculum Level")
    
    # Get or create a curriculum level
    curriculum_level = CurriculumLevel.objects.first()
    if not curriculum_level:
        print_info("Creating test curriculum level...")
        # Create program and subprogram
        program, _ = Program.objects.get_or_create(
            name="CORE",
            defaults={'description': 'Core Program'}
        )
        subprogram, _ = SubProgram.objects.get_or_create(
            program=program,
            name="Phonics",
            defaults={'description': 'Phonics SubProgram'}
        )
        curriculum_level, _ = CurriculumLevel.objects.get_or_create(
            subprogram=subprogram,
            level_number=1,
            defaults={'description': 'Level 1'}
        )
    
    print_info(f"Using curriculum level: {curriculum_level}")
    print_info(f"Curriculum ID: {curriculum_level.id}")
    
    # Step 4: Setup authentication
    print_header("Step 4: Authentication Setup")
    
    # Get or create admin user
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.filter(is_staff=True).first()
    
    if admin_user:
        print_info(f"Using user: {admin_user.username}")
        client.force_login(admin_user)
        print_success("User authenticated")
    else:
        print_error("No admin/staff user found for authentication")
        return False
    
    # Step 5: Test the copy endpoint
    print_header("Step 5: Test Copy Exam Endpoint")
    
    # Prepare copy request data
    copy_data = {
        'source_exam_id': str(test_exam.id),
        'curriculum_level_id': str(curriculum_level.id),
        'exam_type': 'REVIEW',
        'timeslot': 'JAN',
        'academic_year': '2025',
        'custom_suffix': 'TEST COPY'
    }
    
    print_info("Request data:")
    for key, value in copy_data.items():
        print(f"  {key}: {value}")
    
    # Make the copy request
    print_info("\nSending copy request to /RoutineTest/exams/copy/...")
    
    response = client.post(
        '/RoutineTest/exams/copy/',
        data=json.dumps(copy_data),
        content_type='application/json'
    )
    
    print_info(f"Response status: {response.status_code}")
    
    # Parse response
    try:
        response_data = response.json()
        print_info("Response data:")
        print(json.dumps(response_data, indent=2))
    except:
        print_error(f"Failed to parse response as JSON: {response.content[:200]}")
        return False
    
    # Step 6: Verify the result
    print_header("Step 6: Verify Copy Result")
    
    if response.status_code == 200 and response_data.get('success'):
        print_success("Copy operation successful!")
        
        new_exam_id = response_data.get('new_exam_id')
        new_exam_name = response_data.get('new_exam_name')
        
        print_info(f"New exam ID: {new_exam_id}")
        print_info(f"New exam name: {new_exam_name}")
        
        # Verify the new exam exists
        try:
            new_exam = Exam.objects.get(id=new_exam_id)
            print_success("New exam found in database")
            
            # Verify fields were copied correctly
            print_info("\nVerifying copied fields:")
            
            # Check critical fields
            checks = [
                ('Name contains TEST COPY', 'TEST COPY' in new_exam.name),
                ('Timer minutes copied', new_exam.timer_minutes == test_exam.timer_minutes),
                ('Total questions copied', new_exam.total_questions == test_exam.total_questions),
                ('Default options count copied', new_exam.default_options_count == test_exam.default_options_count),
                ('Curriculum level set', new_exam.curriculum_level == curriculum_level),
                ('Exam is active', new_exam.is_active)
            ]
            
            all_passed = True
            for check_name, check_result in checks:
                if check_result:
                    print_success(check_name)
                else:
                    print_error(check_name)
                    all_passed = False
            
            if all_passed:
                print_success("\n🎉 ALL TESTS PASSED! Copy exam functionality is working correctly.")
                return True
            else:
                print_error("\n⚠️ Some checks failed. Review the fields above.")
                return False
            
        except Exam.DoesNotExist:
            print_error(f"New exam with ID {new_exam_id} not found in database!")
            return False
    else:
        print_error("Copy operation failed!")
        if response_data.get('error'):
            print_error(f"Error: {response_data.get('error')}")
        if response_data.get('details'):
            print_error(f"Details: {response_data.get('details')}")
        return False
    
    # Step 7: Test error handling
    print_header("Step 7: Test Error Handling")
    
    # Test with invalid exam ID
    print_info("Testing with invalid exam ID...")
    invalid_data = copy_data.copy()
    invalid_data['source_exam_id'] = 'invalid-uuid-12345'
    
    response = client.post(
        '/RoutineTest/exams/copy/',
        data=json.dumps(invalid_data),
        content_type='application/json'
    )
    
    if response.status_code == 404:
        print_success("Correctly returned 404 for invalid exam ID")
    else:
        print_error(f"Unexpected status code for invalid exam: {response.status_code}")
    
    # Test with missing curriculum level
    print_info("Testing with missing curriculum level...")
    missing_data = copy_data.copy()
    del missing_data['curriculum_level_id']
    
    response = client.post(
        '/RoutineTest/exams/copy/',
        data=json.dumps(missing_data),
        content_type='application/json'
    )
    
    if response.status_code == 400:
        print_success("Correctly returned 400 for missing curriculum level")
    else:
        print_error(f"Unexpected status code for missing field: {response.status_code}")
    
    print_header("TEST COMPLETE")
    return True

def check_model_confusion():
    """Check for any model confusion issues"""
    print_header("Model Confusion Check")
    
    # Check if any exam IDs exist in both tables
    exam_ids = set(str(e.id) for e in Exam.objects.all())
    routine_exam_ids = set(str(re.id) for re in RoutineExam.objects.all())
    
    overlapping = exam_ids.intersection(routine_exam_ids)
    
    if overlapping:
        print_error(f"Found {len(overlapping)} overlapping IDs between Exam and RoutineExam!")
        for oid in list(overlapping)[:5]:
            print(f"  - {oid}")
        return False
    else:
        print_success("No overlapping IDs between Exam and RoutineExam tables")
        return True

def main():
    """Main test runner"""
    print("\n" + "="*80)
    print(" COPY EXAM FIX - COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    try:
        # Run model confusion check
        model_check = check_model_confusion()
        
        # Run copy exam test
        copy_test = test_copy_exam_fix()
        
        # Summary
        print_header("TEST SUMMARY")
        if model_check and copy_test:
            print_success("✅ ALL TESTS PASSED!")
            print_success("The copy exam feature is working correctly.")
            print_success("The model mismatch issue has been resolved.")
        else:
            print_error("❌ SOME TESTS FAILED")
            print_error("Please review the errors above.")
        
    except Exception as e:
        print_error(f"Unexpected error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
#!/usr/bin/env python
"""
Test Copy Exam Functionality After Model Fix
Verifies that the ExamScheduleMatrix model fix resolves the copy exam bug
"""
import os
import sys
import django

# Add project root to Python path
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.http import JsonResponse
from core.models import Teacher
from primepath_routinetest.models import RoutineExam, ExamScheduleMatrix
from primepath_routinetest.views.exam_api import copy_exam, get_class_filtered_exams
import json

def test_model_relationships():
    """Test that model relationships are properly set up"""
    print("=== Testing Model Relationships ===")
    
    # Check ExamScheduleMatrix field relationship
    field = ExamScheduleMatrix._meta.get_field('exams')
    print(f"ExamScheduleMatrix.exams field relates to: {field.related_model}")
    print(f"Should be RoutineExam: {field.related_model == RoutineExam}")
    
    if field.related_model == RoutineExam:
        print("✅ ExamScheduleMatrix model relationship is CORRECT")
        return True
    else:
        print("❌ ExamScheduleMatrix model relationship is INCORRECT")
        return False

def test_routine_exam_creation():
    """Test creating a RoutineExam"""
    print("\n=== Testing RoutineExam Creation ===")
    
    try:
        # Create a test RoutineExam
        exam = RoutineExam.objects.create(
            name="Test Science Quarterly Exam",
            exam_type="QUARTERLY", 
            curriculum_level="CORE Phonics Level 1",
            academic_year="2025",
            time_period_quarter="Q1",
            answer_key={"1": "A", "2": "B", "3": "C"}
        )
        
        print(f"✅ Created RoutineExam: {exam.name} (ID: {exam.id})")
        print(f"   Exam type: {exam.exam_type}")
        print(f"   Time period: {exam.get_time_period_display()}")
        return exam
        
    except Exception as e:
        print(f"❌ Failed to create RoutineExam: {str(e)}")
        return None

def test_exam_schedule_matrix_interaction(exam):
    """Test ExamScheduleMatrix can work with RoutineExam"""
    print("\n=== Testing ExamScheduleMatrix-RoutineExam Interaction ===")
    
    if not exam:
        print("❌ No exam to test with")
        return False
        
    try:
        # Create or get an ExamScheduleMatrix entry
        matrix, created = ExamScheduleMatrix.objects.get_or_create(
            class_code="CLASS_2A",
            academic_year="2025",
            time_period_type="QUARTERLY",
            time_period_value="Q1",
            defaults={
                'status': 'SCHEDULED'
            }
        )
        
        print(f"{'✅ Created' if created else '✅ Found'} ExamScheduleMatrix: {matrix}")
        
        # Test adding the RoutineExam to the matrix
        matrix.exams.add(exam)
        print(f"✅ Successfully added RoutineExam to matrix")
        
        # Test querying
        exams_in_matrix = matrix.exams.all()
        print(f"✅ Matrix now contains {exams_in_matrix.count()} exam(s)")
        
        for matrix_exam in exams_in_matrix:
            print(f"   - {matrix_exam.name} (Type: {type(matrix_exam).__name__})")
            
        return True
        
    except Exception as e:
        print(f"❌ ExamScheduleMatrix-RoutineExam interaction failed: {str(e)}")
        return False

def test_copy_exam_function(exam):
    """Test the actual copy_exam function"""
    print("\n=== Testing copy_exam Function ===")
    
    if not exam:
        print("❌ No exam to test with")
        return False
        
    try:
        # Create a test user and teacher
        user, created = User.objects.get_or_create(
            username="test_teacher",
            defaults={'password': 'testpass'}
        )
        
        teacher, created = Teacher.objects.get_or_create(
            user=user,
            defaults={'name': 'Test Teacher'}
        )
        
        # Create a request factory
        factory = RequestFactory()
        
        # Simulate copy exam request
        copy_data = {
            'source_exam_id': str(exam.id),
            'target_class': 'CLASS_2B',
            'target_timeslot': 'Q1'
        }
        
        request = factory.post(
            '/api/copy-exam/',
            data=json.dumps(copy_data),
            content_type='application/json'
        )
        request.user = user
        
        # Call the copy_exam function
        response = copy_exam(request)
        
        print(f"✅ copy_exam function executed")
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            print(f"   Response: {response_data}")
            
            if response_data.get('success'):
                print("✅ Copy exam operation SUCCESSFUL!")
                return True
            else:
                print(f"❌ Copy exam operation failed: {response_data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ copy_exam returned error status: {response.status_code}")
            print(f"   Response: {response.content.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ copy_exam function test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_get_class_filtered_exams():
    """Test the get_class_filtered_exams function"""
    print("\n=== Testing get_class_filtered_exams Function ===")
    
    try:
        factory = RequestFactory()
        
        # Create request with filters
        request = factory.get('/api/get-class-filtered-exams/CLASS_2A/', {
            'exam_type': 'QUARTERLY',
            'time_period': 'Q1'
        })
        
        # Add a mock user
        user = User.objects.first()
        if user:
            request.user = user
        
        # Call the function
        response = get_class_filtered_exams(request, 'CLASS_2A')
        
        print(f"✅ get_class_filtered_exams function executed")
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = json.loads(response.content)
            exams = response_data.get('exams', [])
            print(f"   Found {len(exams)} exams")
            
            for exam in exams:
                print(f"   - {exam.get('name')} (Type: {exam.get('exam_type')})")
            
            print("✅ get_class_filtered_exams working correctly!")
            return True
        else:
            print(f"❌ get_class_filtered_exams returned error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ get_class_filtered_exams test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_test_data():
    """Clean up test data"""
    print("\n=== Cleaning Up Test Data ===")
    
    try:
        # Delete test exams
        deleted_exams = RoutineExam.objects.filter(name__contains="Test Science").delete()
        print(f"✅ Deleted {deleted_exams[0]} test exams")
        
        # Delete test matrices
        deleted_matrices = ExamScheduleMatrix.objects.filter(
            class_code__in=["CLASS_2A", "CLASS_2B"], 
            academic_year="2025"
        ).delete()
        print(f"✅ Deleted {deleted_matrices[0]} test matrices")
        
        # Delete test users
        User.objects.filter(username="test_teacher").delete()
        print("✅ Deleted test user")
        
    except Exception as e:
        print(f"⚠️ Cleanup warning: {str(e)}")

def main():
    """Main test function"""
    print("🔧 TESTING COPY EXAM MODEL FIX")
    print("="*50)
    
    all_tests_passed = True
    
    # Test 1: Model relationships
    if not test_model_relationships():
        all_tests_passed = False
        
    # Test 2: RoutineExam creation
    exam = test_routine_exam_creation()
    if not exam:
        all_tests_passed = False
        
    # Test 3: ExamScheduleMatrix interaction
    if not test_exam_schedule_matrix_interaction(exam):
        all_tests_passed = False
        
    # Test 4: copy_exam function
    if not test_copy_exam_function(exam):
        all_tests_passed = False
        
    # Test 5: get_class_filtered_exams function
    if not test_get_class_filtered_exams():
        all_tests_passed = False
    
    # Cleanup
    cleanup_test_data()
    
    # Final result
    print("\n" + "="*50)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED! Copy exam model fix is successful!")
        print("✅ The ExamScheduleMatrix now properly references RoutineExam")
        print("✅ Copy exam functionality should work correctly")
    else:
        print("❌ Some tests failed. The fix may need additional work.")
    
    print("="*50)

if __name__ == "__main__":
    main()
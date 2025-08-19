#!/usr/bin/env python3
"""
Internal test for the Assigned Exams display fix.
This script directly calls the view function to test the logic without HTTP authentication.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from primepath_routinetest.views.exam_api import get_class_exams
from primepath_routinetest.models import ExamScheduleMatrix, Exam
from primepath_routinetest.models.exam_management import ExamAssignment, Class
import json

def test_get_class_exams_function():
    """Test the get_class_exams function directly"""
    print("=== Testing get_class_exams Function Directly ===")
    
    # Find a matrix entry with exams to test with
    matrix_entry = ExamScheduleMatrix.objects.filter(exams__isnull=False).first()
    
    if not matrix_entry:
        print("No ExamScheduleMatrix entries with exams found")
        return
    
    class_code = matrix_entry.class_code
    timeslot = matrix_entry.time_period_value
    
    print(f"Testing with Class: {class_code}, Timeslot: {timeslot}")
    print(f"Matrix entry has {matrix_entry.exams.count()} exams")
    
    # List the exams in the matrix
    print("Exams in matrix entry:")
    for exam in matrix_entry.exams.all():
        print(f"  - {exam.name} (ID: {exam.id})")
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get(f'/api/RoutineTest/api/class/{class_code}/exams/?timeslot={timeslot}')
    
    # Create a mock user
    user = User.objects.first()
    if not user:
        user = User.objects.create_user('testuser', 'test@test.com', 'password')
    request.user = user
    
    # Call the function
    try:
        response = get_class_exams(request, class_code)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            # Parse the JSON response
            response_data = json.loads(response.content.decode('utf-8'))
            exams = response_data.get('exams', [])
            
            print(f"Function returned {len(exams)} exams")
            
            for exam in exams:
                print(f"  - {exam.get('name')} (Source: {exam.get('source', 'Unknown')})")
                print(f"    ID: {exam.get('id')}")
                print(f"    Type: {exam.get('type')}")
                print(f"    Duration: {exam.get('duration')} min")
                print(f"    Questions: {exam.get('question_count')}")
        else:
            print(f"Error Response: {response.content.decode('utf-8')}")
    
    except Exception as e:
        print(f"Function call failed: {e}")
        import traceback
        traceback.print_exc()

def check_available_test_data():
    """Show what test data is available"""
    print("\n=== Available Test Data ===")
    
    # Show matrix entries with exams
    print("ExamScheduleMatrix entries with exams:")
    matrices_with_exams = ExamScheduleMatrix.objects.filter(exams__isnull=False).distinct()
    
    for matrix in matrices_with_exams[:5]:  # Show first 5
        print(f"  Class: {matrix.class_code}, Timeslot: {matrix.time_period_value}, Exams: {matrix.exams.count()}")
        for exam in matrix.exams.all():
            print(f"    - {exam.name}")
    
    # Show exam assignments
    print(f"\nExamAssignment entries: {ExamAssignment.objects.count()}")
    if ExamAssignment.objects.exists():
        for assignment in ExamAssignment.objects.all()[:3]:
            print(f"  Class: {assignment.class_assigned.name}, Exam: {assignment.exam.name}")

if __name__ == "__main__":
    check_available_test_data()
    test_get_class_exams_function()
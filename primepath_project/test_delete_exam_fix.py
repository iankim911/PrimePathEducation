#!/usr/bin/env python3
"""
Test script for the delete exam fix.
Tests the delete_exam function to ensure it works with copied exams.
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
from primepath_routinetest.views.exam_api import delete_exam
from primepath_routinetest.models import ExamScheduleMatrix, Exam
import json

def test_delete_exam_function():
    """Test the delete_exam function with a copied exam"""
    print("=== Testing delete_exam Function ===")
    
    # Find a matrix entry with exams to test with
    matrix_entry = ExamScheduleMatrix.objects.filter(exams__isnull=False).first()
    
    if not matrix_entry:
        print("No ExamScheduleMatrix entries with exams found")
        return
    
    class_code = matrix_entry.class_code
    timeslot = matrix_entry.time_period_value
    
    # Get the first exam from the matrix
    exam = matrix_entry.exams.first()
    exam_id = str(exam.id)
    
    print(f"Testing delete for:")
    print(f"  Class: {class_code}")
    print(f"  Timeslot: {timeslot}")
    print(f"  Exam: {exam.name} (ID: {exam_id})")
    
    print(f"\nBefore delete: Matrix entry has {matrix_entry.exams.count()} exams")
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.delete(f'/api/RoutineTest/api/exam/{exam_id}/delete/?class_code={class_code}&timeslot={timeslot}')
    
    # Create a mock user
    user = User.objects.first()
    if not user:
        user = User.objects.create_user('testuser', 'test@test.com', 'password')
    request.user = user
    
    # Call the function
    try:
        response = delete_exam(request, exam_id)
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            # Parse the JSON response
            response_data = json.loads(response.content.decode('utf-8'))
            print(f"Success: {response_data.get('success')}")
            print(f"Message: {response_data.get('message')}")
            
            # Check if exam was actually removed from matrix
            matrix_entry.refresh_from_db()
            print(f"After delete: Matrix entry has {matrix_entry.exams.count()} exams")
            
            # Check if the specific exam is no longer in this matrix entry
            still_in_matrix = matrix_entry.exams.filter(id=exam_id).exists()
            print(f"Exam still in matrix entry: {still_in_matrix}")
            
        else:
            print(f"Error Response: {response.content.decode('utf-8')}")
    
    except Exception as e:
        print(f"Function call failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_delete_exam_function()
#!/usr/bin/env python3
"""
Test script for the Assigned Exams display fix.
This script tests the get_class_exams API endpoint to ensure copied exams appear.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

import requests
import json
from primepath_routinetest.models import ExamScheduleMatrix, Exam
from primepath_routinetest.models.exam_management import ExamAssignment, Class
from core.models import Student, Teacher
from django.contrib.auth.models import User

def test_api_endpoint():
    """Test the get_class_exams API endpoint"""
    print("=== Testing get_class_exams API Endpoint ===")
    
    # Test parameters
    class_code = "Test Class"  # Adjust this to an actual class name in your system
    timeslot = "JAN"  # Adjust this to an actual timeslot
    
    # Make API request
    url = f"http://127.0.0.1:8000/api/RoutineTest/api/class/{class_code}/exams/?timeslot={timeslot}"
    
    try:
        response = requests.get(url)
        print(f"API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            exams = data.get('exams', [])
            print(f"Number of exams returned: {len(exams)}")
            
            for i, exam in enumerate(exams, 1):
                print(f"\nExam {i}:")
                print(f"  ID: {exam.get('id')}")
                print(f"  Name: {exam.get('name')}")
                print(f"  Type: {exam.get('type')}")
                print(f"  Duration: {exam.get('duration')} min")
                print(f"  Questions: {exam.get('question_count')}")
                print(f"  Source: {exam.get('source', 'Unknown')}")
                print(f"  Status: {exam.get('status')}")
        else:
            print(f"API Error: {response.text}")
    
    except Exception as e:
        print(f"Request failed: {e}")

def check_database_state():
    """Check current database state for debugging"""
    print("\n=== Database State Check ===")
    
    # Check ExamScheduleMatrix entries
    matrix_count = ExamScheduleMatrix.objects.count()
    print(f"Total ExamScheduleMatrix entries: {matrix_count}")
    
    if matrix_count > 0:
        print("\nSample ExamScheduleMatrix entries:")
        for matrix in ExamScheduleMatrix.objects.all()[:3]:
            print(f"  Class: {matrix.class_code}, Timeslot: {matrix.time_period_value}, Exams: {matrix.exams.count()}")
    
    # Check ExamAssignment entries
    assignment_count = ExamAssignment.objects.count()
    print(f"\nTotal ExamAssignment entries: {assignment_count}")
    
    # Check Class entries
    class_count = Class.objects.count()
    print(f"Total Class entries: {class_count}")
    
    if class_count > 0:
        print("\nAvailable Classes:")
        for cls in Class.objects.all()[:5]:
            print(f"  Name: {cls.name}")

def test_specific_class_timeslot():
    """Test with actual data from the database"""
    print("\n=== Testing with Real Data ===")
    
    # Find a matrix entry to test with
    matrix_entry = ExamScheduleMatrix.objects.filter(exams__isnull=False).first()
    
    if matrix_entry:
        class_code = matrix_entry.class_code
        timeslot = matrix_entry.time_period_value
        
        print(f"Testing with Class: {class_code}, Timeslot: {timeslot}")
        print(f"Matrix entry has {matrix_entry.exams.count()} exams")
        
        # Test the API
        url = f"http://127.0.0.1:8000/api/RoutineTest/api/class/{class_code}/exams/?timeslot={timeslot}"
        
        try:
            response = requests.get(url)
            print(f"API Response Status: {response.status_code}")
            print(f"Raw Response Content: {response.text[:500]}...")  # Show first 500 chars
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    exams = data.get('exams', [])
                    print(f"API returned {len(exams)} exams")
                    
                    for exam in exams:
                        print(f"  - {exam.get('name')} (Source: {exam.get('source', 'Unknown')})")
                except json.JSONDecodeError as json_error:
                    print(f"JSON parsing failed: {json_error}")
                    print("Response content is not valid JSON")
            else:
                print(f"API Error: {response.text}")
        
        except Exception as e:
            print(f"Request failed: {e}")
    else:
        print("No ExamScheduleMatrix entries with exams found")

if __name__ == "__main__":
    check_database_state()
    test_specific_class_timeslot()
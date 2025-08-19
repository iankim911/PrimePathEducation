#!/usr/bin/env python
"""
Test script to verify Copy Exam functionality after fixes
Creates test data and tests the API endpoint
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from primepath_routinetest.models.exam_management import RoutineExam
from primepath_routinetest.models import TeacherClassAssignment
from core.models import Teacher
from django.contrib.auth.models import User

def create_test_data():
    """Create test data for Copy Exam functionality"""
    print("Creating test data for Copy Exam functionality...")
    
    # Create test user and teacher if they don't exist
    user, created = User.objects.get_or_create(
        username='test_teacher',
        defaults={
            'email': 'test@teacher.com',
            'first_name': 'Test',
            'last_name': 'Teacher'
        }
    )
    if created:
        user.set_password('password123')
        user.save()
    
    teacher, created = Teacher.objects.get_or_create(
        user=user,
        defaults={
            'name': 'Test Teacher',
            'email': 'test@teacher.com',
            'phone': '123-456-7890'
        }
    )
    
    # Create test class assignments
    test_classes = [
        ('HIGH_10A', 'High School Grade 10A'),
        ('HIGH_10B', 'High School Grade 10B'),
        ('MIDDLE_8A', 'Middle School Grade 8A')
    ]
    
    for class_code, display_name in test_classes:
        assignment, created = TeacherClassAssignment.objects.get_or_create(
            class_code=class_code,
            teacher=teacher,
            defaults={
                'is_active': True,
                'access_level': 'FULL'
            }
        )
        if created:
            print(f"Created class assignment: {class_code}")
    
    # Create test RoutineExams with proper time periods
    test_exams = [
        {
            'name': 'April Review Test - Core Phonics Level 1',
            'exam_type': 'REVIEW',
            'curriculum_level': 'CORE Phonics Level 1',
            'academic_year': '2025',
            'time_period_month': 'APR',
            'time_period_quarter': None,
            'quarter': None,  # Legacy field
            'answer_key': {'q1': 'A', 'q2': 'B', 'q3': 'C', 'q4': 'D', 'q5': 'A'}
        },
        {
            'name': 'May Review Test - Core Phonics Level 2',
            'exam_type': 'REVIEW',
            'curriculum_level': 'CORE Phonics Level 2',
            'academic_year': '2025',
            'time_period_month': 'MAY',
            'time_period_quarter': None,
            'quarter': None,
            'answer_key': {'q1': 'B', 'q2': 'C', 'q3': 'D', 'q4': 'A', 'q5': 'B'}
        },
        {
            'name': 'Q1 Quarterly Exam - Core Sigma Level 1',
            'exam_type': 'QUARTERLY',
            'curriculum_level': 'CORE Sigma Level 1',
            'academic_year': '2025',
            'time_period_month': None,
            'time_period_quarter': 'Q1',
            'quarter': 'Q1',  # Legacy field for compatibility
            'answer_key': {'q1': 'C', 'q2': 'D', 'q3': 'A', 'q4': 'B', 'q5': 'C'}
        },
        {
            'name': 'Q2 Quarterly Exam - Core Elite Level 1',
            'exam_type': 'QUARTERLY',
            'curriculum_level': 'CORE Elite Level 1',
            'academic_year': '2025',
            'time_period_month': None,
            'time_period_quarter': 'Q2',
            'quarter': 'Q2',
            'answer_key': {'q1': 'D', 'q2': 'A', 'q3': 'B', 'q4': 'C', 'q5': 'D'}
        }
    ]
    
    created_exams = []
    for exam_data in test_exams:
        exam, created = RoutineExam.objects.get_or_create(
            name=exam_data['name'],
            academic_year=exam_data['academic_year'],
            defaults=exam_data
        )
        created_exams.append(exam)
        if created:
            print(f"Created exam: {exam.name}")
        else:
            print(f"Exam already exists: {exam.name}")
    
    return created_exams

def test_api_endpoint():
    """Test the filtered exams API endpoint"""
    print("\nTesting API endpoint...")
    
    from django.test import Client
    from django.contrib.auth import authenticate
    
    client = Client()
    
    # Log in as test user
    user = User.objects.get(username='test_teacher')
    client.force_login(user)
    
    # Test different filter combinations
    test_cases = [
        {
            'class_code': 'HIGH_10A',
            'exam_type': 'REVIEW',
            'time_period': 'APR',
            'expected_count': 1,
            'description': 'April Review exams'
        },
        {
            'class_code': 'HIGH_10A',
            'exam_type': 'REVIEW',
            'time_period': 'MAY',
            'expected_count': 1,
            'description': 'May Review exams'
        },
        {
            'class_code': 'HIGH_10A',
            'exam_type': 'QUARTERLY',
            'time_period': 'Q1',
            'expected_count': 1,
            'description': 'Q1 Quarterly exams'
        },
        {
            'class_code': 'HIGH_10A',
            'exam_type': 'QUARTERLY',
            'time_period': 'Q2',
            'expected_count': 1,
            'description': 'Q2 Quarterly exams'
        },
        {
            'class_code': 'HIGH_10A',
            'exam_type': 'REVIEW',
            'time_period': 'JUN',
            'expected_count': 0,
            'description': 'June Review exams (should be empty)'
        }
    ]
    
    for test_case in test_cases:
        url = f"/RoutineTest/api/class/{test_case['class_code']}/filtered-exams/"
        params = {
            'exam_type': test_case['exam_type'],
            'time_period': test_case['time_period']
        }
        
        response = client.get(url, params)
        
        print(f"\nTesting {test_case['description']}:")
        print(f"  URL: {url}")
        print(f"  Params: {params}")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            actual_count = len(data.get('exams', []))
            print(f"  Expected: {test_case['expected_count']} exams")
            print(f"  Actual: {actual_count} exams")
            
            if actual_count == test_case['expected_count']:
                print(f"  ✅ PASS")
            else:
                print(f"  ❌ FAIL")
                
            if data.get('exams'):
                for exam in data['exams']:
                    print(f"    - {exam['name']} ({exam['exam_type']}, {exam['time_period']})")
            
            if data.get('message'):
                print(f"  Message: {data['message']}")
        else:
            print(f"  ❌ FAIL - HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"  Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"  Error: {response.content.decode()}")

def main():
    """Main test function"""
    print("="*60)
    print("COPY EXAM FUNCTIONALITY TEST")
    print("="*60)
    
    try:
        # Create test data
        created_exams = create_test_data()
        print(f"\nCreated {len(created_exams)} test exams")
        
        # Test API endpoint
        test_api_endpoint()
        
        print("\n" + "="*60)
        print("TEST COMPLETE")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
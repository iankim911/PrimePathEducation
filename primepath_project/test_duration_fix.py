#!/usr/bin/env python3
"""
Test script specifically for duration update fix.
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
from primepath_routinetest.views.exam_api import get_class_exams, update_exam_duration
from primepath_routinetest.models import ExamScheduleMatrix, Exam
import json

def test_duration_update():
    """Test duration update functionality"""
    print("=== Testing Duration Update Fix ===")
    
    # Find any exam to test with
    exam = Exam.objects.first()
    if not exam:
        print("No exams found")
        return
    
    exam_id = str(exam.id)
    original_duration = exam.timer_minutes
    new_duration = original_duration + 20
    
    print(f"Testing with exam: {exam.name}")
    print(f"Original duration: {original_duration} minutes")
    print(f"New duration: {new_duration} minutes")
    
    # Create mock user
    user = User.objects.first()
    if not user:
        user = User.objects.create_user('testuser', 'test@test.com', 'password')
    
    # Test updating duration
    factory = RequestFactory()
    duration_data = {'duration': new_duration}
    request = factory.patch(f'/api/RoutineTest/api/exam/{exam_id}/duration/', 
                           json.dumps(duration_data), content_type='application/json')
    request.user = user
    
    try:
        response = update_exam_duration(request, exam_id)
        result = json.loads(response.content.decode('utf-8'))
        
        print(f"Update response: {result}")
        
        if result.get('success'):
            # Check if the change was actually saved
            exam.refresh_from_db()
            print(f"Duration after update: {exam.timer_minutes} minutes")
            
            if exam.timer_minutes == new_duration:
                print("✅ Duration update successful and persisted!")
            else:
                print(f"❌ Duration not updated correctly (expected {new_duration}, got {exam.timer_minutes})")
        else:
            print(f"❌ Duration update failed: {result}")
    
    except Exception as e:
        print(f"Duration update failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_duration_update()
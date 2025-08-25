#!/usr/bin/env python
"""Test Copy Exam endpoint directly"""
import os
import sys
import django
import json

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from primepath_routinetest.models import Exam
from core.models import CurriculumLevel

def test_copy_exam_endpoint():
    """Test the copy exam endpoint"""
    print("=" * 80)
    print("TESTING COPY EXAM ENDPOINT")
    print("=" * 80)
    
    # Create test client and login
    client = Client()
    
    # Get admin user
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("❌ No admin user found")
        return
    
    # Login
    client.force_login(admin)
    print(f"✅ Logged in as: {admin.username}")
    
    # Get a source exam
    source_exam = Exam.objects.filter(curriculum_level__isnull=False).first()
    if not source_exam:
        print("❌ No exam with curriculum level found")
        return
    
    print(f"✅ Source exam: {source_exam.name} (ID: {source_exam.id})")
    print(f"   Curriculum: {source_exam.curriculum_level}")
    
    # Get a target curriculum level
    target_level = CurriculumLevel.objects.exclude(id=source_exam.curriculum_level_id).first()
    if not target_level:
        print("❌ No other curriculum level found")
        return
    
    print(f"✅ Target curriculum: {target_level}")
    
    # Test data
    test_data = {
        'source_exam_id': str(source_exam.id),
        'curriculum_level_id': target_level.id,
        'custom_suffix': 'TEST',
        'exam_type': 'REVIEW',
        'timeslot': 'SEP',
        'academic_year': '2025'
    }
    
    print("\n📤 Sending POST request to /RoutineTest/exams/copy/")
    print(f"Data: {json.dumps(test_data, indent=2)}")
    
    # Test the endpoint
    response = client.post(
        '/RoutineTest/exams/copy/',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    print(f"\n📥 Response status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ SUCCESS: {json.dumps(result, indent=2)}")
    else:
        print(f"❌ FAILED")
        print(f"Content: {response.content.decode()[:500]}")
        
        # Try to parse as JSON
        try:
            error_data = response.json()
            print(f"Error data: {json.dumps(error_data, indent=2)}")
        except:
            print("Could not parse response as JSON")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_copy_exam_endpoint()
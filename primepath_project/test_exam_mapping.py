#!/usr/bin/env python
"""
Test script to reproduce the exam mapping save error
"""

import os
import sys
import django
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')

# Setup Django path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import ExamLevelMapping
from placement_test.models import Exam
from core.models import CurriculumLevel

def test_exam_mapping_save():
    """Test the exam mapping save functionality"""
    
    print("Setting up test client...")
    client = Client()
    
    # Get some sample data
    print("Getting sample exams and levels...")
    exams = list(Exam.objects.all()[:2])
    levels = list(CurriculumLevel.objects.all()[:2])
    
    if not exams:
        print("No exams found in database. Please create some exams first.")
        return
        
    if not levels:
        print("No curriculum levels found in database. Please create some levels first.")
        return
    
    print(f"Found {len(exams)} exams and {len(levels)} levels")
    print(f"Sample exam: {exams[0].name} (ID: {exams[0].id})")
    print(f"Sample level: {levels[0]} (ID: {levels[0].id})")
    
    # Prepare test mapping data
    test_mappings = [
        {
            'curriculum_level_id': levels[0].id,
            'exam_id': str(exams[0].id),  # Convert UUID to string
            'slot': 1
        }
    ]
    
    if len(exams) > 1 and len(levels) > 1:
        test_mappings.append({
            'curriculum_level_id': levels[1].id,
            'exam_id': str(exams[1].id),  # Convert UUID to string
            'slot': 1
        })
    
    print("Test mapping data:")
    for mapping in test_mappings:
        print(f"  Level {mapping['curriculum_level_id']} -> Exam {mapping['exam_id']} (Slot {mapping['slot']})")
    
    # Test the API endpoint
    url = reverse('core:save_exam_mappings')
    print(f"Testing URL: {url}")
    
    # Get CSRF token first
    response = client.get('/core/')
    csrf_token = client.cookies.get('csrftoken')
    
    if not csrf_token:
        print("Warning: Could not get CSRF token")
    
    # Prepare request data
    request_data = {
        'mappings': test_mappings
    }
    
    print("Sending POST request...")
    response = client.post(
        url,
        data=json.dumps(request_data),
        content_type='application/json',
        HTTP_X_CSRFTOKEN=csrf_token.value if csrf_token else '',
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    
    print(f"Response status: {response.status_code}")
    
    if hasattr(response, 'json'):
        try:
            response_data = response.json()
            print(f"Response data: {response_data}")
        except json.JSONDecodeError:
            print(f"Response content (not JSON): {response.content}")
    else:
        print(f"Response content: {response.content}")
    
    # Check if mappings were created
    print("\nChecking database for created mappings...")
    mappings = ExamLevelMapping.objects.all()
    print(f"Found {mappings.count()} mappings in database:")
    
    for mapping in mappings:
        print(f"  Level {mapping.curriculum_level_id} -> Exam {mapping.exam_id} (Slot {mapping.slot})")
    
    return response.status_code == 200

if __name__ == '__main__':
    print("=== Testing Exam Mapping Save Functionality ===")
    try:
        success = test_exam_mapping_save()
        if success:
            print("\n✅ Test completed successfully!")
        else:
            print("\n❌ Test failed!")
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()
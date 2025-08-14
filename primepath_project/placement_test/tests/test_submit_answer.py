"""Test submit answer endpoint"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from placement_test.models import StudentSession, Question

# Test the submit answer endpoint
client = Client()
session = StudentSession.objects.first()

if session:
    print(f'Testing with session: {session.id}')
    question = session.exam.questions.first()
    
    if question:
        print(f'Testing with question: {question.id}')
        
        # Test 1: POST with form data (traditional)
        print("\nTest 1: Form data POST")
        response = client.post(f'/api/PlacementTest/session/{session.id}/submit/', {
            'question_id': str(question.id),
            'answer': 'A'
        })
        print(f'Status: {response.status_code}')
        if response.status_code != 200:
            print(f'Response: {response.content.decode()[:300]}')
        
        # Test 2: POST with JSON data
        print("\nTest 2: JSON POST")
        response = client.post(
            f'/api/PlacementTest/session/{session.id}/submit/',
            json.dumps({
                'question_id': str(question.id),
                'answer': 'B'
            }),
            content_type='application/json'
        )
        print(f'Status: {response.status_code}')
        if response.status_code != 200:
            print(f'Response: {response.content.decode()[:300]}')
        
        # Test 3: Check what the view expects
        print("\nTest 3: Check view code")
        from placement_test.views import submit_answer
        import inspect
        print("View expects:", inspect.signature(submit_answer))
else:
    print("No session found for testing")
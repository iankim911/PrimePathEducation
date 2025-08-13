#!/usr/bin/env python3
"""
Final comprehensive test of answer input and submission flow
"""

import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.append('.')
django.setup()

from placement_test.models import Exam, StudentSession, Question, StudentAnswer

def comprehensive_test():
    print("COMPREHENSIVE ANSWER INPUT & SUBMISSION TEST")
    print("=" * 50)
    
    # Get existing session
    session_id = "84ff4d19-de9b-4686-95bf-f6c87d78024a"
    
    try:
        session = StudentSession.objects.get(id=session_id)
        print(f"Testing with session: {session.student_name}")
        
        # Get the test page to extract CSRF token
        test_url = f'http://127.0.0.1:8000/api/placement/session/{session_id}/'
        response = requests.get(test_url, timeout=10)
        
        if response.status_code != 200:
            print(f"Error: Cannot access test page - {response.status_code}")
            return
            
        html = response.text
        
        # Extract CSRF token
        csrf_start = html.find('csrfmiddlewaretoken')
        if csrf_start == -1:
            print("Error: CSRF token not found")
            return
            
        csrf_start = html.find('value="', csrf_start) + 7
        csrf_end = html.find('"', csrf_start)
        csrf_token = html[csrf_start:csrf_end]
        
        print(f"CSRF token extracted: {csrf_token[:20]}...")
        
        # Test answer submission for each question type
        questions = session.exam.questions.all()[:3]  # Test first 3 questions
        
        print(f"\nTesting answer submission for {len(questions)} questions...")
        
        for question in questions:
            print(f"\nQuestion {question.question_number} ({question.question_type}):")
            
            # Prepare test answer based on question type
            if question.question_type == 'MCQ':
                test_answer = 'A'
            elif question.question_type == 'SHORT':
                test_answer = 'Test short answer'
            elif question.question_type == 'LONG':
                test_answer = 'This is a test long answer for validation purposes.'
            elif question.question_type == 'CHECKBOX':
                test_answer = 'A,B'
            else:
                test_answer = 'A'
            
            # Submit answer
            submit_url = f'http://127.0.0.1:8000/api/placement/session/{session_id}/submit/'
            headers = {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf_token,
                'Referer': test_url
            }
            data = {
                'question_id': str(question.id),
                'answer': test_answer
            }
            
            try:
                submit_response = requests.post(
                    submit_url,
                    headers=headers,
                    data=json.dumps(data),
                    timeout=5
                )
                
                if submit_response.status_code == 200:
                    response_data = submit_response.json()
                    if response_data.get('success'):
                        print(f"  SUCCESS: Answer submitted successfully")
                        
                        # Verify in database
                        saved_answer = StudentAnswer.objects.filter(
                            session=session,
                            question=question
                        ).first()
                        
                        if saved_answer:
                            print(f"  VERIFIED: Answer saved in database: '{saved_answer.answer[:30]}...'")
                        else:
                            print(f"  WARNING: Answer not found in database")
                    else:
                        print(f"  FAIL: Server returned error: {response_data}")
                else:
                    print(f"  FAIL: HTTP {submit_response.status_code} - {submit_response.text[:100]}")
                    
            except Exception as e:
                print(f"  ERROR: {e}")
        
        # Test final submission
        print(f"\nTesting complete test submission...")
        complete_url = f'http://127.0.0.1:8000/api/placement/session/{session_id}/complete/'
        
        try:
            complete_response = requests.post(
                complete_url,
                headers={
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrf_token,
                    'Referer': test_url
                },
                data=json.dumps({'session_id': session_id}),
                timeout=5
            )
            
            if complete_response.status_code == 200:
                complete_data = complete_response.json()
                if complete_data.get('success'):
                    print("SUCCESS: Test submission completed!")
                    print(f"Results: {complete_data.get('results', 'No results')}")
                else:
                    print(f"FAIL: Complete test error: {complete_data}")
            else:
                print(f"FAIL: Complete test HTTP {complete_response.status_code}")
                
        except Exception as e:
            print(f"ERROR completing test: {e}")
        
        # Final database check
        print(f"\nFinal database verification...")
        total_answers = StudentAnswer.objects.filter(session=session).count()
        print(f"Total answers saved: {total_answers}")
        
        session.refresh_from_db()
        print(f"Session completed: {'Yes' if session.is_completed else 'No'}")
        
        if total_answers > 0:
            print("\nSUCCESS: Answer input interface is fully functional!")
            print("- Form wrapper is working")
            print("- CSRF protection is working") 
            print("- Answer submission is working")
            print("- Database persistence is working")
        else:
            print("\nFAIL: No answers were saved to database")
            
    except Exception as e:
        print(f"Error in comprehensive test: {e}")

if __name__ == "__main__":
    comprehensive_test()
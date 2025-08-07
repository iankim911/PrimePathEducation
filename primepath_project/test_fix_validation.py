#!/usr/bin/env python3
"""
Test script to validate the answer input interface fix
"""

import os
import sys
import django
import requests

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.append('.')
django.setup()

from placement_test.models import Exam, StudentSession, Question

def test_fix_validation():
    print("=" * 60)
    print("TESTING ANSWER INPUT INTERFACE FIX")
    print("=" * 60)
    
    # Create a new test session
    exam = Exam.objects.first()
    if not exam:
        print("❌ No exam found")
        return
        
    session = StudentSession.objects.create(
        student_name="Fix Test Student",
        grade=9,
        academic_rank='TOP_30',
        exam=exam,
        original_curriculum_level=exam.curriculum_level,
        final_curriculum_level=exam.curriculum_level,
    )
    
    print(f"Created test session: {session.id}")
    
    # Test the page
    test_url = f'http://127.0.0.1:8000/api/placement/session/{session.id}/'
    
    try:
        response = requests.get(test_url, timeout=10)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            
            # Check for the fix
            form_checks = {
                'form element present': '<form' in html,
                'form has test-form id': 'id="test-form"' in html,
                'form has POST method': 'method="post"' in html,
                'CSRF token present': 'csrfmiddlewaretoken' in html,
                'inputs inside form': '<form' in html and 'type="radio"' in html.split('<form')[1].split('</form>')[0] if '<form' in html else False,
                'radio buttons work': 'type="radio"' in html,
                'answer options present': 'answer-options' in html,
                'submit button present': 'submit-test-btn' in html
            }
            
            print("\n🔧 FIX VALIDATION RESULTS:")
            print("-" * 40)
            
            all_passed = True
            for check_name, passed in form_checks.items():
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"{status} {check_name}")
                if not passed:
                    all_passed = False
            
            if all_passed:
                print("\n🎉 ALL CHECKS PASSED! Answer input interface is fixed!")
                
                # Test answer submission (basic)
                print("\n🧪 TESTING ANSWER SUBMISSION:")
                print("-" * 40)
                
                # Find a question to test with
                question = exam.questions.first()
                if question:
                    submit_url = f'http://127.0.0.1:8000/api/placement/session/{session.id}/submit/'
                    test_data = {
                        'question_id': str(question.id),
                        'answer': 'A'
                    }
                    
                    # Get CSRF token from the page
                    csrf_start = html.find('csrfmiddlewaretoken')
                    if csrf_start != -1:
                        csrf_start = html.find('value="', csrf_start) + 7
                        csrf_end = html.find('"', csrf_start)
                        csrf_token = html[csrf_start:csrf_end]
                        
                        headers = {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrf_token,
                            'Referer': test_url
                        }
                        
                        import json
                        try:
                            submit_response = requests.post(
                                submit_url, 
                                headers=headers,
                                data=json.dumps(test_data),
                                timeout=5
                            )
                            print(f"✅ Answer submission test: HTTP {submit_response.status_code}")
                            if submit_response.status_code == 200:
                                print("✅ Answer submission endpoint is working!")
                            else:
                                print(f"⚠️  Answer submission returned: {submit_response.text[:200]}")
                        except Exception as e:
                            print(f"⚠️  Answer submission test failed: {e}")
                    else:
                        print("⚠️  Could not extract CSRF token for submission test")
                else:
                    print("⚠️  No questions found for submission test")
            else:
                print("\n❌ SOME CHECKS FAILED - Fix incomplete")
            
            # Save output for inspection
            with open('fix_test_output.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print("\n📄 Output saved to fix_test_output.html")
            
        else:
            print(f"❌ Cannot access test page: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error testing fix: {e}")

if __name__ == "__main__":
    test_fix_validation()
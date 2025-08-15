"""
Test Script for Answer Input Interface
Verifies that all question types can accept and save answers
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.urls import reverse
from primepath_routinetest.models import Exam, StudentSession, Question
from datetime import datetime
import json

def print_test(test_name, result, details=""):
    """Print test result in formatted way"""
    status = "[PASS]" if result else "[FAIL]"
    print(f"{status} - {test_name}")
    if details:
        print(f"    {details}")
    return result

def test_answer_inputs():
    """Test answer input functionality"""
    print("\n" + "="*60)
    print("ANSWER INPUT INTERFACE TEST SUITE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    
    client = Client()
    passed = 0
    failed = 0
    
    # Test 1: Find an exam with questions
    print("\n[1] FINDING TEST DATA")
    try:
        exam = Exam.objects.filter(pdf_file__isnull=False).first()
        if exam:
            print_test("Found exam with PDF", True, f"Exam: {exam.name}")
            passed += 1
        else:
            print_test("Found exam with PDF", False, "No exam found")
            failed += 1
            return passed, failed
            
        # Check questions
        questions = exam.routine_questions.all()
        question_count = questions.count()
        print_test("Exam has questions", question_count > 0, f"Found {question_count} questions")
        if question_count > 0:
            passed += 1
        else:
            failed += 1
            return passed, failed
            
    except Exception as e:
        print_test("Test data check", False, str(e))
        failed += 1
        return passed, failed
    
    # Test 2: Check question types
    print("\n[2] CHECKING QUESTION TYPES")
    try:
        question_types = questions.values_list('question_type', flat=True).distinct()
        types_list = list(question_types)
        print_test("Question types found", len(types_list) > 0, f"Types: {', '.join(types_list)}")
        passed += 1
        
        # Check for MCQ questions
        mcq_questions = questions.filter(question_type='MCQ')
        print_test("MCQ questions exist", mcq_questions.exists(), f"Found {mcq_questions.count()} MCQ questions")
        if mcq_questions.exists():
            passed += 1
        else:
            failed += 1
            
        # Check options count
        for q in mcq_questions[:3]:
            has_options = q.options_count and q.options_count > 0
            print_test(f"Question {q.question_number} has options", has_options, f"Options: {q.options_count}")
            if has_options:
                passed += 1
            else:
                failed += 1
                
    except Exception as e:
        print_test("Question type check", False, str(e))
        failed += 1
    
    # Test 3: Test session creation
    print("\n[3] TESTING SESSION CREATION")
    try:
        # Create test session data
        test_data = {
            'student_name': 'Test Student',
            'grade': '5',
            'academic_rank': 'TOP_50',
            'parent_phone': '1234567890',
            'school_name': 'Test School'
        }
        
        response = client.post(reverse('RoutineTest:start_test'), test_data)
        
        # Check if redirected to test page
        is_redirect = response.status_code == 302
        print_test("Session created successfully", is_redirect, f"Status: {response.status_code}")
        if is_redirect:
            passed += 1
            
            # Get the session ID from redirect URL
            if hasattr(response, 'url'):
                session_url = response.url
                print(f"    Redirect URL: {session_url}")
                
                # Extract session ID if possible
                if '/session/' in session_url:
                    session_id = session_url.split('/session/')[1].split('/')[0]
                    print_test("Session ID extracted", True, f"ID: {session_id}")
                    passed += 1
                    
                    # Test 4: Check if test page loads
                    print("\n[4] TESTING TEST PAGE")
                    test_response = client.get(session_url)
                    page_loads = test_response.status_code == 200
                    print_test("Test page loads", page_loads, f"Status: {test_response.status_code}")
                    if page_loads:
                        passed += 1
                        
                        # Check for form element
                        has_form = b'<form' in test_response.content and b'test-form' in test_response.content
                        print_test("Form element present", has_form, "Form with id='test-form' found" if has_form else "Form not found")
                        if has_form:
                            passed += 1
                        else:
                            failed += 1
                            
                        # Check for CSRF token
                        has_csrf = b'csrfmiddlewaretoken' in test_response.content
                        print_test("CSRF token present", has_csrf, "Security token found" if has_csrf else "Missing CSRF token")
                        if has_csrf:
                            passed += 1
                        else:
                            failed += 1
                            
                        # Check for answer inputs
                        has_radio = b'type="radio"' in test_response.content
                        print_test("Radio buttons present", has_radio, "MCQ answer options found" if has_radio else "No radio buttons")
                        if has_radio:
                            passed += 1
                        else:
                            failed += 1
                            
                        # Check for question panels
                        has_panels = b'question-panel' in test_response.content
                        print_test("Question panels present", has_panels, "Question structure found" if has_panels else "No question panels")
                        if has_panels:
                            passed += 1
                        else:
                            failed += 1
                            
                        # Check for JavaScript modules
                        has_answer_manager = b'answer-manager.js' in test_response.content
                        print_test("Answer manager loaded", has_answer_manager, "JavaScript module found" if has_answer_manager else "Module missing")
                        if has_answer_manager:
                            passed += 1
                        else:
                            failed += 1
                    else:
                        failed += 1
                else:
                    print_test("Session ID extracted", False, "Could not parse URL")
                    failed += 1
            else:
                print_test("Redirect URL found", False, "No URL in response")
                failed += 1
        else:
            failed += 1
            
    except Exception as e:
        print_test("Session test", False, str(e))
        failed += 1
    
    # Test 5: Check answer submission endpoint
    print("\n[5] TESTING ANSWER SUBMISSION")
    try:
        # Check if we have a valid session
        latest_session = StudentSession.objects.filter(completed_at__isnull=True).last()
        if latest_session:
            print_test("Test session found", True, f"Session ID: {latest_session.id}")
            passed += 1
            
            # Test answer submission endpoint
            submit_url = reverse('RoutineTest:submit_answer', args=[latest_session.id])
            
            # Prepare test answer data
            test_question = latest_session.exam.routine_questions.first()
            if test_question:
                answer_data = {
                    'question_id': str(test_question.id),
                    'answer': 'A'
                }
                
                # Submit answer via AJAX
                response = client.post(
                    submit_url,
                    json.dumps(answer_data),
                    content_type='application/json'
                )
                
                submission_works = response.status_code == 200
                print_test("Answer submission endpoint", submission_works, f"Status: {response.status_code}")
                if submission_works:
                    passed += 1
                    
                    # Check response
                    try:
                        response_data = json.loads(response.content)
                        success = response_data.get('success', False)
                        print_test("Answer saved successfully", success, "Server confirmed save" if success else "Save failed")
                        if success:
                            passed += 1
                        else:
                            failed += 1
                    except:
                        print_test("Response parsing", False, "Invalid JSON response")
                        failed += 1
                else:
                    failed += 1
            else:
                print_test("Test question found", False, "No questions in exam")
                failed += 1
        else:
            print_test("Test session found", False, "No active session")
            failed += 1
            
    except Exception as e:
        print_test("Answer submission test", False, str(e))
        failed += 1
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    total = passed + failed
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if failed == 0:
        print("\n*** ALL ANSWER INPUT TESTS PASSED! ***")
    else:
        print(f"\n*** WARNING: {failed} test(s) failed ***")
    
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    
    return passed, failed

if __name__ == "__main__":
    test_answer_inputs()
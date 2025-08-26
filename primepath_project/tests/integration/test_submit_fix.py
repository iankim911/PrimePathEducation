#!/usr/bin/env python
"""
Test that the answer submission fix works
Tests the 500 error fix for student answer submission
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.utils import timezone
from placement_test.models import PlacementExam as Exam, Question, StudentSession, StudentAnswer
from core.models import CurriculumLevel, SubProgram, Program

def test_submit_answer_fix():
    """Test that answer submission works without 500 errors"""
    
    print("=" * 80)
    print("🔧 ANSWER SUBMISSION FIX TEST")
    print("=" * 80)
    
    base_url = "http://127.0.0.1:8000"
    
    # Check server
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code != 200:
            print(f"❌ Server not responding: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Please start the server first")
        return False
    
    print(f"✅ Server running at {base_url}")
    
    all_tests_passed = True
    
    # Create test exam
    print("\n📋 Creating Test Setup")
    print("-" * 40)
    
    # Get or create test curriculum
    program, _ = Program.objects.get_or_create(
        name="CORE",
        defaults={'grade_range_start': 1, 'grade_range_end': 12, 'order': 1}
    )
    
    subprogram, _ = SubProgram.objects.get_or_create(
        name="Submit Test SubProgram",
        program=program,
        defaults={'order': 1}
    )
    
    curriculum_level, _ = CurriculumLevel.objects.get_or_create(
        subprogram=subprogram,
        level_number=1,
        defaults={'description': 'Submit Test Level'}
    )
    
    # Create test exam
    exam = Exam.objects.create(
        name=f"Submit Test - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        curriculum_level=curriculum_level,
        timer_minutes=60,
        total_questions=3,
        is_active=True
    )
    
    print(f"✅ Created test exam: {exam.name}")
    
    # Create questions
    questions = []
    for i in range(1, 4):
        q = Question.objects.create(
            exam=exam,
            question_number=i,
            question_type='MCQ' if i < 3 else 'SHORT',
            correct_answer='',
            points=1,
            options_count=4 if i < 3 else None
        )
        questions.append(q)
        print(f"✅ Created Question {i}")
    
    # Create test session
    session = StudentSession.objects.create(
        exam=exam,
        student_name='Test Student',
        parent_phone='0987654321',
        grade=5,
        academic_rank='TOP_30',
        started_at=timezone.now()
    )
    
    print(f"✅ Created test session: {session.id}")
    
    # Test 1: Submit first answer (should create new StudentAnswer)
    print("\n📋 TEST 1: Submit First Answer (Create)")
    print("-" * 40)
    
    submit_url = f"{base_url}/api/PlacementTest/session/{session.id}/submit/"
    
    # Submit answer for question 1
    answer_data = {
        'question_id': questions[0].id,
        'answer': 'A'
    }
    
    try:
        response = requests.post(
            submit_url,
            json=answer_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ First answer submitted successfully (created new record)")
            response_data = response.json()
            if response_data.get('success'):
                print(f"  ✅ {response_data.get('message', 'Answer saved')}")
            else:
                print(f"  ❌ Response indicates failure: {response_data}")
                all_tests_passed = False
        else:
            print(f"❌ HTTP {response.status_code} error")
            print(f"Response: {response.text}")
            all_tests_passed = False
            
    except Exception as e:
        print(f"❌ Error submitting first answer: {e}")
        all_tests_passed = False
    
    # Test 2: Update same answer (should update existing StudentAnswer)
    print("\n📋 TEST 2: Update Same Answer (Update)")
    print("-" * 40)
    
    answer_data['answer'] = 'B'  # Change answer
    
    try:
        response = requests.post(
            submit_url,
            json=answer_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Answer updated successfully (modified existing record)")
        else:
            print(f"❌ HTTP {response.status_code} error on update")
            all_tests_passed = False
            
    except Exception as e:
        print(f"❌ Error updating answer: {e}")
        all_tests_passed = False
    
    # Test 3: Submit multiple answers in sequence
    print("\n📋 TEST 3: Submit Multiple Answers")
    print("-" * 40)
    
    for i, question in enumerate(questions[1:], start=2):
        answer_data = {
            'question_id': question.id,
            'answer': 'C' if question.question_type == 'MCQ' else 'Test answer'
        }
        
        try:
            response = requests.post(
                submit_url,
                json=answer_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Question {i} answer submitted")
            else:
                print(f"❌ Question {i} failed: HTTP {response.status_code}")
                all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Error submitting question {i}: {e}")
            all_tests_passed = False
    
    # Test 4: Verify answers in database
    print("\n📋 TEST 4: Verify Database Records")
    print("-" * 40)
    
    saved_answers = StudentAnswer.objects.filter(session=session)
    
    if saved_answers.count() == 3:
        print(f"✅ All 3 answers saved in database")
        for answer in saved_answers:
            print(f"  Q{answer.question.question_number}: {answer.answer}")
    else:
        print(f"❌ Expected 3 answers, found {saved_answers.count()}")
        all_tests_passed = False
    
    # Test 5: Test edge cases
    print("\n📋 TEST 5: Edge Cases")
    print("-" * 40)
    
    # Test with empty answer
    answer_data = {
        'question_id': questions[0].id,
        'answer': ''
    }
    
    try:
        response = requests.post(
            submit_url,
            json=answer_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Empty answer handled correctly")
        else:
            print(f"⚠️ Empty answer returned: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error with empty answer: {e}")
        all_tests_passed = False
    
    print("\n" + "=" * 80)
    print("🎯 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    if all_tests_passed:
        print("✅ ALL TESTS PASSED!")
        print("\n📋 Fixed Issues:")
        print("  1. ✅ Can create new StudentAnswer records")
        print("  2. ✅ Can update existing StudentAnswer records")
        print("  3. ✅ Multiple submissions work correctly")
        print("  4. ✅ No more 500 errors on submission")
        print("\n🎉 Answer submission is working correctly!")
        return True
    else:
        print("❌ Some tests failed - submission issues remain")
        return False


if __name__ == '__main__':
    success = test_submit_answer_fix()
    sys.exit(0 if success else 1)
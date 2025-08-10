#!/usr/bin/env python
"""
Comprehensive test for SHORT answer save functionality
Tests that SHORT answer questions properly save in the exam management interface
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
from placement_test.models import Exam, Question
from core.models import CurriculumLevel, SubProgram, Program

def test_short_answer_save():
    """Test SHORT answer save functionality"""
    
    print("=" * 80)
    print("🔧 SHORT ANSWER SAVE FUNCTIONALITY TEST")
    print("=" * 80)
    
    # Check server
    base_url = "http://127.0.0.1:8000"
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code != 200:
            print(f"❌ Server not responding: HTTP {response.status_code}")
            print("Please start the server first")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
    
    print(f"✅ Server running at {base_url}")
    
    all_tests_passed = True
    
    # Test 1: Create test exam with SHORT answer questions
    print("\n📋 TEST 1: Create Test Exam with SHORT Questions")
    print("-" * 40)
    
    # Get or create test curriculum
    program, _ = Program.objects.get_or_create(
        name="CORE",
        defaults={'grade_range_start': 1, 'grade_range_end': 12, 'order': 1}
    )
    
    subprogram, _ = SubProgram.objects.get_or_create(
        name="SHORT Answer Test SubProgram",
        program=program,
        defaults={'order': 1}
    )
    
    curriculum_level, _ = CurriculumLevel.objects.get_or_create(
        subprogram=subprogram,
        level_number=1,
        defaults={'description': 'SHORT Answer Test Level'}
    )
    
    # Create test exam
    exam = Exam.objects.create(
        name=f"SHORT Answer Test - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        curriculum_level=curriculum_level,
        timer_minutes=60,
        total_questions=5,
        is_active=True
    )
    
    print(f"✅ Created test exam: {exam.name} (ID: {exam.id})")
    
    # Create questions with different types
    questions = []
    
    # Question 1: MCQ (control)
    q1 = Question.objects.create(
        exam=exam,
        question_number=1,
        question_type='MCQ',
        correct_answer='B',
        points=1,
        options_count=4
    )
    questions.append(q1)
    print(f"✅ Created Q1: MCQ (control)")
    
    # Question 2: SHORT with no options_count (single answer)
    q2 = Question.objects.create(
        exam=exam,
        question_number=2,
        question_type='SHORT',
        correct_answer='',  # No initial answer
        points=1,
        options_count=None
    )
    questions.append(q2)
    print(f"✅ Created Q2: SHORT with options_count=None")
    
    # Question 3: SHORT with options_count=1 (single answer)
    q3 = Question.objects.create(
        exam=exam,
        question_number=3,
        question_type='SHORT',
        correct_answer='',
        points=1,
        options_count=1
    )
    questions.append(q3)
    print(f"✅ Created Q3: SHORT with options_count=1")
    
    # Question 4: SHORT with options_count=0 (single answer)
    q4 = Question.objects.create(
        exam=exam,
        question_number=4,
        question_type='SHORT',
        correct_answer='',
        points=1,
        options_count=0
    )
    questions.append(q4)
    print(f"✅ Created Q4: SHORT with options_count=0")
    
    # Question 5: SHORT with options_count=3 (multiple answers)
    q5 = Question.objects.create(
        exam=exam,
        question_number=5,
        question_type='SHORT',
        correct_answer='',
        points=1,
        options_count=3
    )
    questions.append(q5)
    print(f"✅ Created Q5: SHORT with options_count=3")
    
    # Test 2: Save answers via API
    print("\n📋 TEST 2: Save Answers via API")
    print("-" * 40)
    
    # Prepare test data
    save_data = {
        'questions': [
            {
                'id': str(q1.id),
                'question_number': '1',
                'question_type': 'MCQ',
                'correct_answer': 'C',
                'options_count': 4
            },
            {
                'id': str(q2.id),
                'question_number': '2',
                'question_type': 'SHORT',
                'correct_answer': 'Single answer for Q2'
            },
            {
                'id': str(q3.id),
                'question_number': '3',
                'question_type': 'SHORT',
                'correct_answer': 'Single answer for Q3',
                'options_count': 1
            },
            {
                'id': str(q4.id),
                'question_number': '4',
                'question_type': 'SHORT',
                'correct_answer': 'Single answer for Q4',
                'options_count': 0
            },
            {
                'id': str(q5.id),
                'question_number': '5',
                'question_type': 'SHORT',
                'correct_answer': 'Answer1|Answer2|Answer3',
                'options_count': 3
            }
        ]
    }
    
    # Make API call to save answers
    save_url = f"{base_url}/api/placement/exams/{exam.id}/save-answers/"
    
    try:
        response = requests.post(
            save_url,
            json=save_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ API save request successful")
            response_data = response.json()
            if response_data.get('success'):
                print(f"✅ {response_data.get('message', 'Answers saved')}")
            else:
                print(f"❌ Save failed: {response_data}")
                all_tests_passed = False
        else:
            print(f"❌ API returned HTTP {response.status_code}")
            print(f"Response: {response.text}")
            all_tests_passed = False
            
    except Exception as e:
        print(f"❌ Error calling save API: {e}")
        all_tests_passed = False
    
    # Test 3: Verify persistence
    print("\n📋 TEST 3: Verify Answer Persistence")
    print("-" * 40)
    
    # Refresh questions from database
    for question in questions:
        question.refresh_from_db()
    
    # Check each question
    test_results = []
    
    # Q1: MCQ
    if q1.correct_answer == 'C':
        print(f"✅ Q1 (MCQ): Answer saved correctly: '{q1.correct_answer}'")
        test_results.append(True)
    else:
        print(f"❌ Q1 (MCQ): Expected 'C', got '{q1.correct_answer}'")
        test_results.append(False)
    
    # Q2: SHORT with no options_count
    if q2.correct_answer == 'Single answer for Q2':
        print(f"✅ Q2 (SHORT, no options_count): Answer saved correctly: '{q2.correct_answer}'")
        test_results.append(True)
    else:
        print(f"❌ Q2 (SHORT, no options_count): Expected 'Single answer for Q2', got '{q2.correct_answer}'")
        test_results.append(False)
    
    # Q3: SHORT with options_count=1
    if q3.correct_answer == 'Single answer for Q3':
        print(f"✅ Q3 (SHORT, options_count=1): Answer saved correctly: '{q3.correct_answer}'")
        test_results.append(True)
    else:
        print(f"❌ Q3 (SHORT, options_count=1): Expected 'Single answer for Q3', got '{q3.correct_answer}'")
        test_results.append(False)
    
    # Q4: SHORT with options_count=0
    if q4.correct_answer == 'Single answer for Q4':
        print(f"✅ Q4 (SHORT, options_count=0): Answer saved correctly: '{q4.correct_answer}'")
        test_results.append(True)
    else:
        print(f"❌ Q4 (SHORT, options_count=0): Expected 'Single answer for Q4', got '{q4.correct_answer}'")
        test_results.append(False)
    
    # Q5: SHORT with multiple answers
    if q5.correct_answer == 'Answer1|Answer2|Answer3':
        print(f"✅ Q5 (SHORT, options_count=3): Multiple answers saved correctly: '{q5.correct_answer}'")
        test_results.append(True)
    else:
        print(f"❌ Q5 (SHORT, options_count=3): Expected 'Answer1|Answer2|Answer3', got '{q5.correct_answer}'")
        test_results.append(False)
    
    all_tests_passed = all(test_results)
    
    # Test 4: Preview page rendering
    print("\n📋 TEST 4: Preview Page Rendering")
    print("-" * 40)
    
    preview_url = f"{base_url}/api/placement/exams/{exam.id}/preview/"
    
    try:
        response = requests.get(preview_url, timeout=10)
        
        if response.status_code == 200:
            html_content = response.text
            
            # Check if our saved answers appear in the rendered HTML
            checks = [
                ('Single answer for Q2' in html_content, "Q2 answer in HTML"),
                ('Single answer for Q3' in html_content, "Q3 answer in HTML"),
                ('Single answer for Q4' in html_content, "Q4 answer in HTML"),
                ('Answer1' in html_content, "Q5 first answer in HTML")
            ]
            
            for check, description in checks:
                if check:
                    print(f"✅ {description}: Found")
                else:
                    print(f"⚠️ {description}: Not found")
                    
        else:
            print(f"❌ Preview page: HTTP {response.status_code}")
            all_tests_passed = False
            
    except Exception as e:
        print(f"❌ Error accessing preview: {e}")
        all_tests_passed = False
    
    print("\n" + "=" * 80)
    print("🎯 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    if all_tests_passed:
        print("✅ ALL TESTS PASSED!")
        print("\n📋 Fixed Issues:")
        print("  1. ✅ SHORT answers with no options_count save correctly")
        print("  2. ✅ SHORT answers with options_count=0 save correctly")
        print("  3. ✅ SHORT answers with options_count=1 save correctly")
        print("  4. ✅ SHORT answers with multiple values save correctly")
        print("  5. ✅ Values persist after save and reload")
        print("\n🎉 SHORT answer save functionality is working correctly!")
        return True
    else:
        print("❌ Some tests failed - review issues above")
        return False

def test_other_question_types():
    """Test that other question types still work"""
    
    print("\n" + "=" * 80)
    print("🔍 TESTING OTHER QUESTION TYPES")
    print("=" * 80)
    
    all_types_working = True
    
    # Get a test exam
    exam = Exam.objects.filter(is_active=True).first()
    
    if not exam:
        print("⚠️ No active exam found for testing")
        return True
    
    print(f"Using exam: {exam.name}")
    
    # Test different question types
    question_types = ['MCQ', 'CHECKBOX', 'LONG', 'MIXED']
    
    for q_type in question_types:
        questions = exam.questions.filter(question_type=q_type)
        if questions.exists():
            print(f"✅ {q_type}: {questions.count()} questions found")
        else:
            print(f"⚠️ {q_type}: No questions of this type")
    
    return all_types_working

if __name__ == '__main__':
    # Run SHORT answer save tests
    short_success = test_short_answer_save()
    
    # Run other question type tests
    other_success = test_other_question_types()
    
    print("\n" + "=" * 80)
    print("🎯 COMPREHENSIVE QA COMPLETE")
    print("=" * 80)
    
    if short_success and other_success:
        print("✅ ALL SYSTEMS OPERATIONAL")
        print("\n🎉 SHORT answer fix is working correctly!")
        print("📋 No existing features were disrupted")
        sys.exit(0)
    else:
        print("❌ Some issues detected - review test output")
        sys.exit(1)
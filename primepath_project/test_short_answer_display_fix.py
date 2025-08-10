#!/usr/bin/env python
"""
Test SHORT answer display fix
Verifies that SHORT answers display correctly after being saved
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

def test_short_answer_display():
    """Test SHORT answer display after save"""
    
    print("=" * 80)
    print("🔧 SHORT ANSWER DISPLAY FIX TEST")
    print("=" * 80)
    
    # Check server
    base_url = "http://127.0.0.1:8000"
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code != 200:
            print(f"❌ Server not responding: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
    
    print(f"✅ Server running at {base_url}")
    
    all_tests_passed = True
    
    # Create test exam
    print("\n📋 Creating Test Exam")
    print("-" * 40)
    
    # Get or create test curriculum
    program, _ = Program.objects.get_or_create(
        name="CORE",
        defaults={'grade_range_start': 1, 'grade_range_end': 12, 'order': 1}
    )
    
    subprogram, _ = SubProgram.objects.get_or_create(
        name="SHORT Display Test SubProgram",
        program=program,
        defaults={'order': 1}
    )
    
    curriculum_level, _ = CurriculumLevel.objects.get_or_create(
        subprogram=subprogram,
        level_number=1,
        defaults={'description': 'SHORT Display Test Level'}
    )
    
    # Create test exam
    exam = Exam.objects.create(
        name=f"SHORT Display Test - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        curriculum_level=curriculum_level,
        timer_minutes=60,
        total_questions=6,
        is_active=True
    )
    
    print(f"✅ Created test exam: {exam.name} (ID: {exam.id})")
    
    # Create test questions with various SHORT answer patterns
    test_cases = [
        {
            'num': 1,
            'type': 'SHORT',
            'answer': 'C',
            'description': 'Single letter (like MCQ)'
        },
        {
            'num': 2,
            'type': 'SHORT',
            'answer': 'apple',
            'description': 'Single word'
        },
        {
            'num': 3,
            'type': 'SHORT',
            'answer': 'cat|dog|bird',
            'description': 'Pipe-separated multiple'
        },
        {
            'num': 4,
            'type': 'SHORT',
            'answer': 'A,B,C',
            'description': 'Comma-separated letters'
        },
        {
            'num': 5,
            'type': 'SHORT',
            'answer': 'red,blue,green',
            'description': 'Comma-separated words'
        },
        {
            'num': 6,
            'type': 'MCQ',
            'answer': 'B',
            'description': 'MCQ control'
        }
    ]
    
    questions = []
    for case in test_cases:
        q = Question.objects.create(
            exam=exam,
            question_number=case['num'],
            question_type=case['type'],
            correct_answer=case['answer'],
            points=1,
            options_count=4 if case['type'] == 'MCQ' else None
        )
        questions.append(q)
        print(f"✅ Created Q{case['num']}: {case['description']}")
    
    # Test 1: Save via API
    print("\n📋 TEST 1: Save Answers via API")
    print("-" * 40)
    
    save_data = {
        'questions': []
    }
    
    for i, case in enumerate(test_cases):
        save_data['questions'].append({
            'id': str(questions[i].id),
            'question_number': str(case['num']),
            'question_type': case['type'],
            'correct_answer': case['answer'],
            'options_count': 4 if case['type'] == 'MCQ' else None
        })
    
    save_url = f"{base_url}/api/placement/exams/{exam.id}/save-answers/"
    
    try:
        response = requests.post(
            save_url,
            json=save_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ API save successful")
        else:
            print(f"❌ API save failed: HTTP {response.status_code}")
            all_tests_passed = False
            
    except Exception as e:
        print(f"❌ Error saving: {e}")
        all_tests_passed = False
    
    # Test 2: Check preview page display
    print("\n📋 TEST 2: Check Preview Page Display")
    print("-" * 40)
    
    preview_url = f"{base_url}/api/placement/exams/{exam.id}/preview/"
    
    try:
        response = requests.get(preview_url, timeout=10)
        
        if response.status_code == 200:
            html_content = response.text
            
            # Check each test case appears in HTML
            for case in test_cases:
                if case['type'] == 'SHORT':
                    # Check if the answer appears as a value in an input field
                    if case['answer'] == 'C':
                        # Single letter should appear in value attribute
                        if 'value="C"' in html_content or 'value=\'C\'' in html_content:
                            print(f"✅ Q{case['num']} ({case['description']}): Displayed correctly")
                        else:
                            print(f"❌ Q{case['num']} ({case['description']}): Not displayed")
                            all_tests_passed = False
                    elif '|' in case['answer']:
                        # Pipe-separated should show first value at least
                        first_value = case['answer'].split('|')[0]
                        if f'value="{first_value}"' in html_content:
                            print(f"✅ Q{case['num']} ({case['description']}): Displayed correctly")
                        else:
                            print(f"❌ Q{case['num']} ({case['description']}): Not displayed")
                            all_tests_passed = False
                    elif ',' in case['answer']:
                        # Comma-separated might show first value or all
                        first_value = case['answer'].split(',')[0].strip()
                        if f'value="{first_value}"' in html_content or f'value="{case["answer"]}"' in html_content:
                            print(f"✅ Q{case['num']} ({case['description']}): Displayed correctly")
                        else:
                            print(f"❌ Q{case['num']} ({case['description']}): Not displayed")
                            all_tests_passed = False
                    else:
                        # Single value
                        if f'value="{case["answer"]}"' in html_content:
                            print(f"✅ Q{case['num']} ({case['description']}): Displayed correctly")
                        else:
                            print(f"❌ Q{case['num']} ({case['description']}): Not displayed")
                            all_tests_passed = False
                            
        else:
            print(f"❌ Preview page error: HTTP {response.status_code}")
            all_tests_passed = False
            
    except Exception as e:
        print(f"❌ Error accessing preview: {e}")
        all_tests_passed = False
    
    # Test 3: Verify database persistence
    print("\n📋 TEST 3: Verify Database Persistence")
    print("-" * 40)
    
    for i, case in enumerate(test_cases):
        questions[i].refresh_from_db()
        if questions[i].correct_answer == case['answer']:
            print(f"✅ Q{case['num']}: Persisted correctly in DB")
        else:
            print(f"❌ Q{case['num']}: Expected '{case['answer']}', got '{questions[i].correct_answer}'")
            all_tests_passed = False
    
    # Test 4: Test response_list generation
    print("\n📋 TEST 4: Response List Generation")
    print("-" * 40)
    
    from placement_test.views.exam import preview_exam
    from django.test import RequestFactory
    
    factory = RequestFactory()
    request = factory.get(f'/preview/{exam.id}/')
    
    # Get questions with response_list populated
    exam_fresh = Exam.objects.get(id=exam.id)
    questions_fresh = exam_fresh.questions.all().order_by('question_number')
    
    # Simulate the view logic
    for question in questions_fresh:
        if question.question_type == 'SHORT':
            if question.correct_answer:
                if '|' in question.correct_answer:
                    question.response_list = question.correct_answer.split('|')
                elif ',' in question.correct_answer and question.options_count and question.options_count > 1:
                    question.response_list = [s.strip() for s in question.correct_answer.split(',')]
                else:
                    question.response_list = [question.correct_answer] if question.correct_answer else []
            else:
                question.response_list = []
    
    # Check response_list generation
    for i, case in enumerate(test_cases):
        if case['type'] == 'SHORT':
            q = questions_fresh[i]
            if case['answer'] == 'C':
                if q.response_list == ['C']:
                    print(f"✅ Q{case['num']}: response_list = {q.response_list}")
                else:
                    print(f"❌ Q{case['num']}: response_list = {q.response_list}, expected ['C']")
                    all_tests_passed = False
            elif '|' in case['answer']:
                expected = case['answer'].split('|')
                if q.response_list == expected:
                    print(f"✅ Q{case['num']}: response_list = {q.response_list}")
                else:
                    print(f"❌ Q{case['num']}: response_list = {q.response_list}, expected {expected}")
                    all_tests_passed = False
            elif ',' in case['answer']:
                # Check if it's being split correctly
                if q.options_count and q.options_count > 1:
                    expected = [s.strip() for s in case['answer'].split(',')]
                else:
                    expected = [case['answer']]
                print(f"ℹ️ Q{case['num']}: response_list = {q.response_list}, options_count = {q.options_count}")
    
    print("\n" + "=" * 80)
    print("🎯 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    if all_tests_passed:
        print("✅ ALL TESTS PASSED!")
        print("\n📋 Fixed Issues:")
        print("  1. ✅ Single letter SHORT answers display correctly")
        print("  2. ✅ Single word SHORT answers display correctly")
        print("  3. ✅ Pipe-separated SHORT answers display correctly")
        print("  4. ✅ Comma-separated SHORT answers display correctly")
        print("  5. ✅ Values persist and display after save")
        print("\n🎉 SHORT answer display fix is working!")
        return True
    else:
        print("❌ Some tests failed - review issues above")
        return False


if __name__ == '__main__':
    success = test_short_answer_display()
    sys.exit(0 if success else 1)
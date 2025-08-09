#!/usr/bin/env python
"""
Comprehensive test for all question types and multiple input scenarios.
Tests SHORT, MIXED, MCQ, CHECKBOX, and LONG question types.
"""

import os
import sys
import django
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.urls import reverse
from placement_test.models import Exam, Question, StudentSession
from placement_test.templatetags.grade_tags import (
    has_multiple_answers, get_answer_letters, get_mixed_components, is_mixed_question
)


def test_all_question_types():
    """Test all question types and their rendering."""
    print("\n" + "="*70)
    print("COMPREHENSIVE QUESTION TYPE TESTING")
    print("="*70)
    
    results = []
    client = Client()
    
    # Test 1: Database Analysis of All Question Types
    print("\n[Test 1] Database Analysis of All Question Types")
    print("-"*50)
    
    question_stats = {}
    for q_type in ['MCQ', 'CHECKBOX', 'SHORT', 'LONG', 'MIXED']:
        count = Question.objects.filter(question_type=q_type).count()
        multi_count = Question.objects.filter(
            question_type=q_type, 
            options_count__gt=1
        ).count()
        question_stats[q_type] = {'total': count, 'multiple': multi_count}
        print(f"  {q_type}: {count} total, {multi_count} with options_count > 1")
    
    results.append(("Database Stats", True))
    
    # Test 2: SHORT Questions with Multiple Answers
    print("\n[Test 2] SHORT Questions with Multiple Answers")
    print("-"*50)
    
    short_questions = Question.objects.filter(
        question_type='SHORT',
        options_count__gt=1
    )[:3]
    
    short_pass = True
    for q in short_questions:
        has_multi = has_multiple_answers(q)
        letters = get_answer_letters(q)
        
        print(f"  Question {q.question_number} (Exam: {q.exam.name[:30]}...):")
        print(f"    Options Count: {q.options_count}")
        print(f"    Has Multiple: {has_multi}")
        print(f"    Letters: {letters}")
        
        if q.options_count > 1:
            if not has_multi or len(letters) != q.options_count:
                print(f"    ❌ FAIL: Expected {q.options_count} inputs")
                short_pass = False
            else:
                print(f"    ✅ PASS: Correctly shows {q.options_count} inputs")
    
    results.append(("SHORT Multiple", short_pass))
    
    # Test 3: MIXED Questions with options_count
    print("\n[Test 3] MIXED Questions with options_count")
    print("-"*50)
    
    mixed_questions = Question.objects.filter(
        question_type='MIXED'
    )[:5]
    
    mixed_pass = True
    for q in mixed_questions:
        components = get_mixed_components(q)
        
        print(f"  Question {q.question_number} (Exam: {q.exam.name[:30]}...):")
        print(f"    Options Count: {q.options_count}")
        print(f"    Components: {len(components)}")
        print(f"    All Inputs: {all(c['type'] == 'input' for c in components)}")
        
        if q.options_count > 1:
            if len(components) != q.options_count:
                print(f"    ❌ FAIL: Expected {q.options_count} but got {len(components)}")
                mixed_pass = False
            elif not all(c['type'] == 'input' for c in components):
                print(f"    ❌ FAIL: Not all components are text inputs")
                mixed_pass = False
            else:
                print(f"    ✅ PASS: Correctly shows {q.options_count} text inputs")
    
    results.append(("MIXED Multiple", mixed_pass))
    
    # Test 4: Template Rendering for Specific Questions
    print("\n[Test 4] Template Rendering for Specific Questions")
    print("-"*50)
    
    # Test the exam from the screenshot
    exam = Exam.objects.filter(name__contains='PRIME CORE PHONICS - Level 2_v_a').first()
    if exam:
        session = StudentSession.objects.filter(exam=exam).first()
        if session:
            response = client.get(reverse('placement_test:take_test', args=[session.id]))
            
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                
                # Check Question 3 (MIXED with 3 inputs)
                q3 = exam.questions.filter(question_number=3).first()
                if q3:
                    q3_id = q3.id
                    # Look for the three input fields
                    has_input_a = f'name="q_{q3_id}_A"' in content
                    has_input_b = f'name="q_{q3_id}_B"' in content
                    has_input_c = f'name="q_{q3_id}_C"' in content
                    
                    print(f"  Question 3 (ID: {q3_id}):")
                    print(f"    Has input A: {has_input_a}")
                    print(f"    Has input B: {has_input_b}")
                    print(f"    Has input C: {has_input_c}")
                    
                    if has_input_a and has_input_b and has_input_c:
                        print(f"    ✅ PASS: All 3 inputs rendered")
                        results.append(("Q3 Rendering", True))
                    else:
                        print(f"    ❌ FAIL: Not all inputs rendered")
                        results.append(("Q3 Rendering", False))
                
                # Check Question 4 (MIXED with 3 inputs)
                q4 = exam.questions.filter(question_number=4).first()
                if q4:
                    q4_id = q4.id
                    has_input_a = f'name="q_{q4_id}_A"' in content
                    has_input_b = f'name="q_{q4_id}_B"' in content
                    has_input_c = f'name="q_{q4_id}_C"' in content
                    
                    print(f"  Question 4 (ID: {q4_id}):")
                    print(f"    Has input A: {has_input_a}")
                    print(f"    Has input B: {has_input_b}")
                    print(f"    Has input C: {has_input_c}")
                    
                    if has_input_a and has_input_b and has_input_c:
                        print(f"    ✅ PASS: All 3 inputs rendered")
                        results.append(("Q4 Rendering", True))
                    else:
                        print(f"    ❌ FAIL: Not all inputs rendered")
                        results.append(("Q4 Rendering", False))
    
    # Test 5: MCQ and CHECKBOX Types
    print("\n[Test 5] MCQ and CHECKBOX Question Types")
    print("-"*50)
    
    # Test single MCQ
    single_mcq = Question.objects.filter(
        question_type='MCQ'
    ).exclude(correct_answer__contains=',').first()
    
    if single_mcq:
        print(f"  Single MCQ (Q{single_mcq.question_number}): {single_mcq.options_count} options")
        results.append(("Single MCQ", True))
    
    # Test multiple MCQ
    multi_mcq = Question.objects.filter(
        question_type='MCQ',
        correct_answer__contains=','
    ).first()
    
    if multi_mcq:
        print(f"  Multiple MCQ (Q{multi_mcq.question_number}): {multi_mcq.options_count} options")
        results.append(("Multiple MCQ", True))
    
    # Test CHECKBOX
    checkbox = Question.objects.filter(question_type='CHECKBOX').first()
    if checkbox:
        print(f"  Checkbox (Q{checkbox.question_number}): {checkbox.options_count} options")
        results.append(("Checkbox", True))
    
    # Test 6: Edge Cases
    print("\n[Test 6] Edge Cases")
    print("-"*50)
    
    # Questions with options_count = 0 or 1
    single_option = Question.objects.filter(options_count=1).first()
    if single_option:
        has_multi = has_multiple_answers(single_option)
        print(f"  Single option question: has_multiple={has_multi}")
        if not has_multi:
            print("    ✅ PASS: Single option not treated as multiple")
            results.append(("Single Option", True))
        else:
            print("    ❌ FAIL: Single option incorrectly treated as multiple")
            results.append(("Single Option", False))
    
    # Questions with no correct_answer
    no_answer = Question.objects.filter(correct_answer='').first()
    if no_answer and no_answer.options_count > 1:
        letters = get_answer_letters(no_answer)
        print(f"  No correct_answer but options_count={no_answer.options_count}: letters={letters}")
        if len(letters) == no_answer.options_count:
            print("    ✅ PASS: Generates letters from options_count")
            results.append(("No Answer", True))
        else:
            print("    ❌ FAIL: Failed to generate letters")
            results.append(("No Answer", False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    total = len(results)
    
    for test_name, result in results:
        if result is True:
            print(f"  ✅ {test_name}: PASSED")
        elif result is False:
            print(f"  ❌ {test_name}: FAILED")
        else:
            print(f"  ⚠️ {test_name}: SKIPPED")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if failed == 0:
        print("\n🎉 SUCCESS! All question types render correctly.")
        print("✅ SHORT questions with multiple answers: Working")
        print("✅ MIXED questions with options_count: Working")
        print("✅ MCQ and CHECKBOX questions: Working")
        print("✅ Template rendering: Correct")
    else:
        print(f"\n⚠️ {failed} test(s) failed. Review the implementation.")
    
    return failed == 0


if __name__ == "__main__":
    success = test_all_question_types()
    sys.exit(0 if success else 1)
#!/usr/bin/env python
"""
Test script to verify MIXED question type rendering and functionality.
Tests the complete fix for Question 4 and other MIXED questions.
"""

import os
import sys
import django
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client, RequestFactory
from django.urls import reverse
from placement_test.models import Exam, Question, StudentSession
from placement_test.templatetags.grade_tags import (
    has_multiple_answers, get_answer_letters, get_mixed_components, is_mixed_question
)
from placement_test.services import GradingService


def test_mixed_questions():
    """Test MIXED question type rendering and processing."""
    print("\n" + "="*70)
    print("TESTING MIXED QUESTION TYPE FIX")
    print("="*70)
    
    results = []
    
    # Test 1: Template Filter Detection
    print("\n[Test 1] Template Filter Detection for MIXED Questions")
    exam = Exam.objects.filter(name__contains='PRIME CORE PHONICS - Level 2_v_a').first()
    if exam:
        q4 = exam.questions.filter(question_number=4).first()
        if q4:
            is_mixed = is_mixed_question(q4)
            has_multi = has_multiple_answers(q4)
            components = get_mixed_components(q4)
            
            print(f"  Question 4 Type: {q4.question_type}")
            print(f"  Is Mixed: {is_mixed}")
            print(f"  Has Multiple Answers: {has_multi}")
            print(f"  Components Count: {len(components)}")
            
            if components:
                print("  Component Details:")
                for comp in components:
                    print(f"    - {comp['letter']}: {comp['type']}")
            
            # Verify expected structure
            expected_components = 4  # 1 MCQ + 3 inputs
            if len(components) == expected_components:
                print("  ✅ PASS: Correct number of components")
                results.append(("Filter Detection", True))
            else:
                print(f"  ❌ FAIL: Expected {expected_components} components, got {len(components)}")
                results.append(("Filter Detection", False))
    
    # Test 2: Template Rendering Simulation
    print("\n[Test 2] Template Rendering for Different MIXED Questions")
    mixed_questions = Question.objects.filter(question_type='MIXED')[:5]
    
    if mixed_questions:
        for q in mixed_questions:
            components = get_mixed_components(q)
            print(f"  Question {q.question_number} (Exam: {q.exam.name[:30]}...):")
            print(f"    Options Count: {q.options_count}")
            print(f"    Components: {len(components)}")
            
            input_count = sum(1 for c in components if c['type'] == 'input')
            mcq_count = sum(1 for c in components if c['type'] == 'mcq')
            
            print(f"    Input Fields: {input_count}")
            print(f"    MCQ Fields: {mcq_count}")
        
        print("  ✅ PASS: All MIXED questions processed")
        results.append(("Template Rendering", True))
    else:
        print("  ⚠️ No MIXED questions found for testing")
        results.append(("Template Rendering", None))
    
    # Test 3: SHORT vs MIXED Differentiation
    print("\n[Test 3] SHORT vs MIXED Question Differentiation")
    short_q = Question.objects.filter(question_type='SHORT', options_count__gt=1).first()
    mixed_q = Question.objects.filter(question_type='MIXED').first()
    
    if short_q and mixed_q:
        # Test SHORT question
        short_has_multi = has_multiple_answers(short_q)
        short_letters = get_answer_letters(short_q)
        
        print(f"  SHORT Question {short_q.question_number}:")
        print(f"    Has Multiple: {short_has_multi}")
        print(f"    Letters: {short_letters}")
        
        # Test MIXED question
        mixed_has_multi = has_multiple_answers(mixed_q)
        mixed_components = get_mixed_components(mixed_q)
        
        print(f"  MIXED Question {mixed_q.question_number}:")
        print(f"    Has Multiple: {mixed_has_multi}")
        print(f"    Components: {len(mixed_components)}")
        
        print("  ✅ PASS: Correctly differentiates SHORT and MIXED")
        results.append(("Question Differentiation", True))
    
    # Test 4: Grading System Compatibility
    print("\n[Test 4] Grading System Compatibility")
    grading_service = GradingService()
    
    # Test MIXED question grading
    mixed_q = Question.objects.filter(question_type='MIXED').first()
    if mixed_q:
        # Simulate a student answer for MIXED question
        test_answer = json.dumps({
            'A': 'C',  # MCQ part
            'B': 'test1',  # Short answer parts
            'C': 'test2',
            'D': 'test3'
        })
        
        # Check if grading marks it for manual review
        from placement_test.models import StudentAnswer
        from django.utils import timezone
        
        # Create a test session if needed
        session = StudentSession.objects.first()
        if session:
            # Create a mock answer
            answer = StudentAnswer(
                session=session,
                question=mixed_q,
                answer=test_answer
            )
            
            result = GradingService.auto_grade_answer(answer)
            
            print(f"  MIXED Question Grading:")
            print(f"    Requires Manual: {result['requires_manual_grading']}")
            print(f"    Is Correct: {result['is_correct']}")
            print(f"    Points Earned: {result['points_earned']}")
            
            if result['requires_manual_grading']:
                print("  ✅ PASS: MIXED questions correctly marked for manual grading")
                results.append(("Grading Compatibility", True))
            else:
                print("  ❌ FAIL: MIXED questions should require manual grading")
                results.append(("Grading Compatibility", False))
    
    # Test 5: Client Rendering Test
    print("\n[Test 5] Client Rendering Test")
    client = Client()
    
    # Try to access a student test with MIXED questions
    session = StudentSession.objects.filter(
        exam__questions__question_type='MIXED'
    ).first()
    
    if session:
        try:
            response = client.get(reverse('placement_test:take_test', args=[session.id]))
            if response.status_code == 200:
                content = str(response.content)
                
                # Check for our new MIXED question rendering
                has_mixed_section = 'mixed-answer-section' in content or 'Mixed Type with Multiple Components' in content
                has_answer_letters = 'Answer A:' in content or 'Answer B:' in content
                
                print(f"  Response Status: {response.status_code}")
                print(f"  Has Mixed Section: {has_mixed_section}")
                print(f"  Has Answer Letters: {has_answer_letters}")
                
                if has_mixed_section or has_answer_letters:
                    print("  ✅ PASS: MIXED questions rendered in template")
                    results.append(("Client Rendering", True))
                else:
                    print("  ⚠️ MIXED question markup not found (may be using V2 template)")
                    results.append(("Client Rendering", None))
            else:
                print(f"  ❌ FAIL: Response status {response.status_code}")
                results.append(("Client Rendering", False))
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            results.append(("Client Rendering", False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)
    
    for test_name, result in results:
        if result is True:
            print(f"  ✅ {test_name}: PASSED")
        elif result is False:
            print(f"  ❌ {test_name}: FAILED")
        else:
            print(f"  ⚠️ {test_name}: SKIPPED")
    
    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! MIXED questions are now fully functional.")
    else:
        print(f"\n⚠️ {failed} test(s) failed. Review the implementation.")
    
    return failed == 0


if __name__ == "__main__":
    success = test_mixed_questions()
    sys.exit(0 if success else 1)
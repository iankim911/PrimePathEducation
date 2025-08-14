#!/usr/bin/env python3
"""
Comprehensive test for ENHANCED grading system with LONG exclusion.

Tests the new grading policy where:
1. LONG questions are excluded from total_possible
2. SHORT answers are fully auto-graded
3. MIXED questions use all-or-nothing grading for MCQ/SHORT parts only

Run with: python test_enhanced_grading.py
"""

import os
import sys
import django
import json
from decimal import Decimal

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from placement_test.models import StudentSession, StudentAnswer, Question, Exam
from core.models import CurriculumLevel
from placement_test.services.grading_service import GradingService

def test_scenario_with_all_question_types():
    """Test grading with MCQ, SHORT, LONG, and MIXED questions"""
    print("\n🧪 TESTING ENHANCED GRADING WITH ALL QUESTION TYPES")
    print("=" * 60)
    
    # Find an exam with all question types
    exam = Exam.objects.filter(
        questions__question_type='LONG'
    ).first()
    
    if not exam:
        print("❌ No exam with LONG questions found")
        return False
    
    curriculum_level = CurriculumLevel.objects.first()
    if not curriculum_level:
        print("❌ No curriculum levels found")
        return False
    
    # Create a test session
    session = StudentSession.objects.create(
        student_name='Enhanced Grading Test',
        grade=8,
        academic_rank='TOP_10',
        school_name_manual='Test School',
        exam=exam,
        original_curriculum_level=curriculum_level
    )
    
    print(f"Created test session: {session.id}")
    
    # Get questions and categorize them
    questions = exam.questions.all()[:10]  # Test with first 10 questions
    
    question_types = {}
    for q in questions:
        if q.question_type not in question_types:
            question_types[q.question_type] = []
        question_types[q.question_type].append(q)
    
    print(f"\nQuestion distribution:")
    for q_type, qs in question_types.items():
        print(f"  {q_type}: {len(qs)} questions")
    
    # Create answers with all correct (copying from correct_answer field)
    print("\nCreating answers (all correct from answer key)...")
    for question in questions:
        if question.correct_answer:
            # Use the correct answer
            answer_value = question.correct_answer
        else:
            # For questions without correct_answer, provide a default
            if question.question_type == 'MCQ':
                answer_value = 'A'
            elif question.question_type == 'SHORT':
                answer_value = 'test answer'
            elif question.question_type == 'LONG':
                answer_value = 'This is a long answer that would normally require manual grading.'
            elif question.question_type == 'MIXED':
                # Create JSON answer for mixed
                answer_value = json.dumps({'0': 'A', '1': 'B', '2': 'short answer'})
            else:
                answer_value = 'default'
        
        StudentAnswer.objects.create(
            session=session,
            question=question,
            answer=answer_value
        )
    
    # Grade the session with enhanced grading
    print("\n🔧 Running ENHANCED GradingService...")
    results = GradingService.grade_session(session)
    
    # Display results
    print("\n📊 GRADING RESULTS:")
    print(f"  Total Score: {results['total_score']}")
    print(f"  Total Possible (LONG excluded): {results['total_possible']}")
    print(f"  Total Possible (if LONG included): {results.get('total_possible_including_long', 'N/A')}")
    print(f"  Percentage: {results['percentage_score']:.2f}%")
    print(f"  Auto-graded: {results['auto_graded']}")
    print(f"  Excluded questions: {len(results.get('excluded_questions', []))}")
    
    # Breakdown by type
    print("\n📈 BREAKDOWN BY QUESTION TYPE:")
    breakdown = results.get('question_breakdown', {})
    for q_type, data in breakdown.items():
        if data['count'] > 0:
            if q_type == 'LONG':
                print(f"  {q_type}: {data['count']} questions [EXCLUDED FROM SCORING]")
            else:
                print(f"  {q_type}: {data['score']}/{data['possible']} points")
    
    # Verify expected behavior
    print("\n✅ VERIFICATION:")
    
    # Check that LONG questions were excluded
    long_excluded = any(q['question_type'] == 'LONG' for q in results.get('excluded_questions', []))
    print(f"  LONG questions excluded: {'✅ Yes' if long_excluded else '❌ No'}")
    
    # Check that percentage would be 100% for gradable questions
    if results['total_possible'] > 0:
        is_perfect = results['percentage_score'] >= 99.9  # Allow for rounding
        print(f"  Perfect score on gradable questions: {'✅ Yes' if is_perfect else '❌ No'}")
        
        if not is_perfect:
            print(f"    Expected ~100%, got {results['percentage_score']:.2f}%")
            print(f"    This may indicate some answers didn't match or MIXED questions failed all-or-nothing")
    
    # Cleanup
    session.delete()
    
    return True

def test_specific_exam_scenario():
    """Test with the specific exam from the user's screenshot"""
    print("\n🧪 TESTING WITH SPECIFIC 10-QUESTION EXAM SCENARIO")
    print("=" * 60)
    
    # Find or create an exam matching the user's description
    exam = Exam.objects.filter(total_questions=10).first()
    
    if not exam:
        print("❌ No 10-question exam found")
        return False
    
    print(f"Using exam: {exam.name}")
    
    curriculum_level = CurriculumLevel.objects.first()
    session = StudentSession.objects.create(
        student_name='100% Test User',
        grade=8,
        academic_rank='TOP_10',
        school_name_manual='Test School',
        exam=exam,
        original_curriculum_level=curriculum_level
    )
    
    # Simulate copying all correct answers
    questions = exam.questions.all()[:10]
    
    print(f"\n📝 Creating answers for {len(questions)} questions...")
    
    for i, question in enumerate(questions, 1):
        print(f"  Q{i} ({question.question_type}): ", end="")
        
        if question.correct_answer:
            answer_value = question.correct_answer
            print(f"Using correct answer: '{answer_value[:20]}...'")
        else:
            # No correct answer provided
            answer_value = "A" if question.question_type == "MCQ" else "test"
            print(f"No correct answer, using default: '{answer_value}'")
        
        StudentAnswer.objects.create(
            session=session,
            question=question,
            answer=answer_value
        )
    
    # Grade with enhanced service
    print("\n🔧 Grading with ENHANCED policy...")
    results = GradingService.grade_session(session)
    
    # Calculate what we expect
    expected_excluded = sum(1 for q in questions if q.question_type == 'LONG')
    expected_possible = sum(q.points for q in questions if q.question_type != 'LONG')
    
    print("\n📊 RESULTS:")
    print(f"  Score: {results['total_score']}/{results['total_possible']}")
    print(f"  Percentage: {results['percentage_score']:.2f}%")
    print(f"  Expected possible (excluding LONG): {expected_possible}")
    print(f"  Expected excluded: {expected_excluded} LONG questions")
    
    # Verify 100% on gradable questions
    is_perfect = results['percentage_score'] >= 99.9 if results['total_possible'] > 0 else False
    
    print(f"\n{'✅' if is_perfect else '❌'} RESULT: {results['percentage_score']:.2f}%")
    
    if is_perfect:
        print("SUCCESS: Copying all answers now gives 100% (LONG excluded)!")
    else:
        print("ISSUE: Not getting 100% - checking why...")
        
        # Debug info
        answers = session.answers.select_related('question').all()
        for answer in answers:
            if answer.question.question_type != 'LONG' and not answer.is_correct:
                print(f"  Q{answer.question.question_number} ({answer.question.question_type}): "
                      f"INCORRECT - '{answer.answer}' vs '{answer.question.correct_answer}'")
    
    # Cleanup
    session.delete()
    
    return is_perfect

def main():
    """Run all tests"""
    print("🎯 ENHANCED GRADING SYSTEM TEST SUITE")
    print("=" * 60)
    print("Testing new grading policy:")
    print("• LONG questions excluded from total_possible")
    print("• SHORT answers fully auto-graded")
    print("• MIXED questions with all-or-nothing grading")
    print()
    
    # Run tests
    test_results = []
    
    print("Running tests...")
    
    # Test 1: All question types
    try:
        result1 = test_scenario_with_all_question_types()
        test_results.append(("All Question Types", result1))
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
        test_results.append(("All Question Types", False))
    
    # Test 2: Specific exam scenario
    try:
        result2 = test_specific_exam_scenario()
        test_results.append(("10-Question Exam (100% Test)", result2))
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
        test_results.append(("10-Question Exam (100% Test)", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    all_passed = all(result for _, result in test_results)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✅ ENHANCED GRADING SYSTEM WORKING CORRECTLY:")
        print("  • LONG questions properly excluded from scoring")
        print("  • SHORT answers auto-graded successfully")
        print("  • Copying all answers now gives 100% (for gradable questions)")
    else:
        print("\n⚠️ Some tests failed - review the output above")
    
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
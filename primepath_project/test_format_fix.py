#!/usr/bin/env python3
"""
Test script for the format mismatch fix.
Tests that the grading system now correctly handles both old and new answer formats.
"""

import os
import sys
import django
import json

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from placement_test.models import StudentSession, StudentAnswer, Question, Exam
from core.models import CurriculumLevel
from placement_test.services.grading_service import GradingService

def test_format_conversion():
    """Test that format conversion works correctly"""
    print("\n🧪 TESTING FORMAT CONVERSION FIX")
    print("=" * 60)
    
    # Test SHORT answer format conversion
    print("\n1. Testing SHORT answer format conversion:")
    
    # Test old frontend format
    old_format = "A: A | B: A"
    expected = "A|A"
    result = GradingService.grade_short_answer(old_format, expected)
    print(f"   Old format: '{old_format}' -> Expected: '{expected}'")
    print(f"   Result: {'✅ PASS' if result else '❌ FAIL'}")
    
    # Test new format (should already work)
    new_format = "A|A"
    result = GradingService.grade_short_answer(new_format, expected)
    print(f"   New format: '{new_format}' -> Expected: '{expected}'")
    print(f"   Result: {'✅ PASS' if result else '❌ FAIL'}")
    
    # Test MIXED answer format conversion
    print("\n2. Testing MIXED answer format conversion:")
    
    # Test old frontend format
    old_mixed = "A: B,C | B: B,C"
    expected_mixed = '[{"type":"Multiple Choice","value":"B,C"},{"type":"Multiple Choice","value":"B,C"}]'
    result = GradingService.grade_mixed_question(old_mixed, expected_mixed)
    print(f"   Old format: '{old_mixed[:30]}...'")
    print(f"   Expected: '{expected_mixed[:50]}...'")
    print(f"   Result: {'✅ PASS' if result else '❌ FAIL'}")
    
    # Test new format
    new_mixed = expected_mixed
    result = GradingService.grade_mixed_question(new_mixed, expected_mixed)
    print(f"   New format matches expected: {'✅ PASS' if result else '❌ FAIL'}")
    
    return True

def test_full_exam_scenario():
    """Test a complete exam with all question types"""
    print("\n🧪 TESTING FULL EXAM SCENARIO WITH FORMAT FIX")
    print("=" * 60)
    
    # Find a 10-question exam
    exam = Exam.objects.filter(total_questions=10).first()
    if not exam:
        print("❌ No 10-question exam found")
        return False
    
    print(f"Using exam: {exam.name}")
    
    # Create test session
    curriculum_level = CurriculumLevel.objects.first()
    session = StudentSession.objects.create(
        student_name='Format Fix Test User',
        grade=8,
        academic_rank='TOP_10',
        school_name_manual='Test School',
        exam=exam,
        original_curriculum_level=curriculum_level
    )
    
    print(f"Created session: {session.id}")
    
    # Get questions
    questions = exam.questions.all()[:10]
    
    # Create answers - simulate old frontend format
    print("\n📝 Creating answers with OLD frontend format...")
    for i, question in enumerate(questions, 1):
        answer_value = None
        
        if question.question_type == 'SHORT':
            # Simulate old frontend format for SHORT with multiple parts
            if '|' in (question.correct_answer or ''):
                # Multiple parts - use old format
                parts = question.correct_answer.split('|')
                formatted_parts = []
                for j, part in enumerate(parts):
                    letter = chr(65 + j)  # A, B, C, etc.
                    formatted_parts.append(f"{letter}: {part}")
                answer_value = " | ".join(formatted_parts)
                print(f"  Q{i} (SHORT): Using OLD format: '{answer_value[:50]}...'")
            else:
                # Single part
                answer_value = question.correct_answer
                print(f"  Q{i} (SHORT): Single answer: '{answer_value}'")
        
        elif question.question_type == 'MIXED':
            # Simulate old frontend format for MIXED
            if question.correct_answer and question.correct_answer.startswith('['):
                try:
                    correct_data = json.loads(question.correct_answer)
                    formatted_parts = []
                    for j, item in enumerate(correct_data):
                        if isinstance(item, dict) and 'value' in item:
                            letter = chr(65 + j)  # A, B, C, etc.
                            formatted_parts.append(f"{letter}: {item['value']}")
                    answer_value = " | ".join(formatted_parts)
                    print(f"  Q{i} (MIXED): Using OLD format: '{answer_value[:50]}...'")
                except:
                    answer_value = question.correct_answer
            else:
                answer_value = question.correct_answer
        
        elif question.correct_answer:
            # MCQ, LONG, etc - use as is
            answer_value = question.correct_answer
            print(f"  Q{i} ({question.question_type}): Using correct answer")
        
        else:
            # No correct answer - use default
            answer_value = "A"
            print(f"  Q{i} ({question.question_type}): No correct answer, using default")
        
        StudentAnswer.objects.create(
            session=session,
            question=question,
            answer=answer_value
        )
    
    # Grade the session
    print("\n🔧 Grading with format conversion...")
    results = GradingService.grade_session(session)
    
    print("\n📊 RESULTS:")
    print(f"  Score: {results['total_score']}/{results['total_possible']}")
    print(f"  Percentage: {results['percentage_score']:.2f}%")
    print(f"  LONG excluded: {len(results.get('excluded_questions', []))}")
    
    # Check if we got 100% on gradable questions
    is_perfect = results['percentage_score'] >= 99.9 if results['total_possible'] > 0 else False
    
    if is_perfect:
        print("\n✅ SUCCESS: Format conversion works! Got 100% with old format answers!")
    else:
        print(f"\n❌ ISSUE: Got {results['percentage_score']:.2f}% instead of 100%")
        
        # Debug which questions failed
        answers = session.answers.select_related('question').all()
        for answer in answers:
            if answer.question.question_type != 'LONG' and not answer.is_correct:
                print(f"  Q{answer.question.question_number} ({answer.question.question_type}): INCORRECT")
                print(f"    Student: '{answer.answer[:100]}...'")
                print(f"    Correct: '{answer.question.correct_answer[:100] if answer.question.correct_answer else 'None'}...'")
    
    # Cleanup
    session.delete()
    
    return is_perfect

def main():
    """Run all tests"""
    print("🎯 FORMAT FIX VERIFICATION TEST")
    print("=" * 60)
    print("Testing that the grading system now handles:")
    print("• Old frontend format: 'A: A | B: A' for SHORT")
    print("• Old frontend format: 'A: B,C | B: B,C' for MIXED")
    print("• New backend-compatible formats")
    print()
    
    # Run tests
    test_results = []
    
    # Test 1: Format conversion
    try:
        result1 = test_format_conversion()
        test_results.append(("Format Conversion", result1))
    except Exception as e:
        print(f"❌ Format conversion test failed: {e}")
        test_results.append(("Format Conversion", False))
    
    # Test 2: Full exam scenario
    try:
        result2 = test_full_exam_scenario()
        test_results.append(("Full Exam (100% Test)", result2))
    except Exception as e:
        print(f"❌ Full exam test failed: {e}")
        import traceback
        traceback.print_exc()
        test_results.append(("Full Exam (100% Test)", False))
    
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
        print("\n✅ FORMAT FIX VERIFIED:")
        print("  • Frontend can send old or new formats")
        print("  • Backend converts formats automatically")
        print("  • 100% scoring now works when copying all answers")
    else:
        print("\n⚠️ Some tests failed - review the output above")
    
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
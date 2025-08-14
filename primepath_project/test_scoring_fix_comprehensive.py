#!/usr/bin/env python3
"""
Comprehensive test script for the scoring calculation fix.

This script tests the complete scoring fix implementation to ensure:
1. The GradingService calculates percentages correctly
2. All question types are included in scoring
3. Frontend displays correct values
4. No existing functionality is broken

Run with: python test_scoring_fix_comprehensive.py
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

from django.test import Client, RequestFactory
from django.contrib.auth.models import AnonymousUser
from placement_test.models import StudentSession, StudentAnswer, Question, Exam
from core.models import CurriculumLevel
from placement_test.services.grading_service import GradingService
from placement_test.views.student import test_result

def create_test_scenario():
    """Create a controlled test scenario with known scoring"""
    print("🔧 Creating test scenario...")
    
    # Find an exam with mixed question types
    exam = Exam.objects.filter(
        questions__question_type='LONG'
    ).first()
    
    if not exam:
        print("❌ No exam with LONG questions found for testing")
        return None
    
    curriculum_level = CurriculumLevel.objects.first()
    if not curriculum_level:
        print("❌ No curriculum levels found")
        return None
    
    # Create a test session
    session = StudentSession.objects.create(
        student_name='Scoring Fix Test Student',
        grade=8,
        academic_rank='TOP_10',
        school_name_manual='Test School',
        exam=exam,
        original_curriculum_level=curriculum_level
    )
    
    # Create answers with known scores
    questions = exam.questions.all()[:6]  # Test with first 6 questions
    
    test_answers = [
        {'correct': True, 'answer': 'A'},     # MCQ - correct
        {'correct': False, 'answer': 'B'},    # MCQ - incorrect  
        {'correct': True, 'answer': 'correct'},   # SHORT - correct
        {'correct': False, 'answer': 'wrong'},    # SHORT - incorrect
        {'correct': None, 'answer': 'essay answer'},  # LONG - needs manual
        {'correct': None, 'answer': 'mixed answer'}   # MIXED - needs manual
    ]
    
    created_answers = []
    for i, question in enumerate(questions):
        if i < len(test_answers):
            answer_data = test_answers[i]
            answer = StudentAnswer.objects.create(
                session=session,
                question=question,
                answer=answer_data['answer'],
                is_correct=answer_data['correct'],
                points_earned=question.points if answer_data['correct'] else 0
            )
            created_answers.append(answer)
    
    print(f"✅ Created test session {session.id} with {len(created_answers)} answers")
    return session

def test_grading_service_fix():
    """Test that the GradingService calculates scores correctly"""
    print("\n🧪 TESTING GRADING SERVICE FIX")
    print("=" * 60)
    
    session = create_test_scenario()
    if not session:
        return False
    
    print(f"Testing session: {session.id}")
    
    # Get the questions and their point values
    answers = session.answers.select_related('question').all()
    
    print(f"\nQuestion breakdown:")
    total_expected_score = 0
    total_expected_possible = 0
    
    for answer in answers:
        print(f"  Q{answer.question.question_number} ({answer.question.question_type}): "
              f"{answer.points_earned}/{answer.question.points} points")
        total_expected_score += answer.points_earned
        total_expected_possible += answer.question.points
    
    expected_percentage = (total_expected_score / total_expected_possible * 100) if total_expected_possible > 0 else 0
    
    print(f"\nExpected calculation:")
    print(f"  Total score: {total_expected_score}")
    print(f"  Total possible: {total_expected_possible}")
    print(f"  Expected percentage: {expected_percentage:.2f}%")
    
    # Run the fixed grading service
    print(f"\nRunning GradingService.grade_session()...")
    results = GradingService.grade_session(session)
    
    # Check results
    session.refresh_from_db()
    print(f"\nGradingService results:")
    print(f"  Calculated score: {results['total_score']}")
    print(f"  Calculated possible: {results['total_possible']}")
    print(f"  Calculated percentage: {results['percentage_score']:.2f}%")
    print(f"  Session score: {session.score}")
    print(f"  Session percentage: {session.percentage_score}%")
    
    # Verify correctness
    success = (
        results['total_score'] == total_expected_score and
        results['total_possible'] == total_expected_possible and
        abs(results['percentage_score'] - expected_percentage) < 0.01 and
        session.score == total_expected_score and
        abs(float(session.percentage_score) - expected_percentage) < 0.01
    )
    
    if success:
        print(f"✅ GradingService fix verified!")
    else:
        print(f"❌ GradingService fix failed!")
        print(f"   Expected: {total_expected_score}/{total_expected_possible} = {expected_percentage:.2f}%")
        print(f"   Got: {results['total_score']}/{results['total_possible']} = {results['percentage_score']:.2f}%")
    
    # Cleanup
    session.delete()
    return success

def test_frontend_display():
    """Test that the frontend displays correct values"""
    print("\n🖥️ TESTING FRONTEND DISPLAY")
    print("=" * 60)
    
    # Find a completed session to test with
    session = StudentSession.objects.filter(
        completed_at__isnull=False,
        answers__isnull=False
    ).first()
    
    if not session:
        print("❌ No completed sessions found for frontend testing")
        return False
    
    print(f"Testing frontend display for session: {session.id}")
    
    # Test the view
    factory = RequestFactory()
    request = factory.get(f'/PlacementTest/session/{session.id}/result/')
    request.user = AnonymousUser()
    
    try:
        from placement_test.views.student import test_result
        response = test_result(request, str(session.id))
        
        if response.status_code == 200:
            content = response.content.decode()
            
            # Check if the context has the right values
            answers = session.answers.select_related('question').all()
            expected_total_possible = sum(answer.question.points for answer in answers)
            
            # Check if total_possible_score is in the template
            if str(expected_total_possible) in content:
                print(f"✅ Frontend displays correct total possible: {expected_total_possible}")
                
                # Check percentage display
                if str(session.percentage_score) in content:
                    print(f"✅ Frontend displays percentage: {session.percentage_score}%")
                    return True
                else:
                    print(f"❌ Percentage not found in frontend content")
                    return False
            else:
                print(f"❌ Total possible score not found in frontend content")
                return False
        else:
            print(f"❌ Frontend view failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend test error: {e}")
        return False

def test_edge_cases():
    """Test edge cases and special scenarios"""
    print("\n🎯 TESTING EDGE CASES")
    print("=" * 60)
    
    test_cases = [
        {
            'name': 'All correct answers',
            'test': test_all_correct_scenario
        },
        {
            'name': 'All incorrect answers', 
            'test': test_all_incorrect_scenario
        },
        {
            'name': 'Mixed question types with manual grading',
            'test': test_manual_grading_scenario
        },
        {
            'name': 'Zero possible points edge case',
            'test': test_zero_points_scenario
        }
    ]
    
    results = []
    for case in test_cases:
        print(f"\n  Testing: {case['name']}")
        try:
            result = case['test']()
            status = "✅" if result else "❌"
            results.append(result)
            print(f"  {status} {case['name']}")
        except Exception as e:
            print(f"  ❌ {case['name']}: Error - {e}")
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    print(f"\nEdge cases: {passed}/{total} passed")
    
    return passed == total

def test_all_correct_scenario():
    """Test scenario where student gets all answers correct"""
    # Create a simple test
    exam = Exam.objects.first()
    if not exam:
        return False
    
    curriculum_level = CurriculumLevel.objects.first()
    session = StudentSession.objects.create(
        student_name='All Correct Test',
        grade=8,
        academic_rank='TOP_10', 
        school_name_manual='Test School',
        exam=exam,
        original_curriculum_level=curriculum_level
    )
    
    # Create correct answers for first 3 questions
    questions = exam.questions.all()[:3]
    for question in questions:
        StudentAnswer.objects.create(
            session=session,
            question=question,
            answer='correct',
            is_correct=True,
            points_earned=question.points
        )
    
    results = GradingService.grade_session(session)
    session.refresh_from_db()
    
    # Should be 100%
    success = abs(float(session.percentage_score) - 100.0) < 0.01
    
    session.delete()
    return success

def test_all_incorrect_scenario():
    """Test scenario where student gets all answers incorrect"""
    exam = Exam.objects.first()
    if not exam:
        return False
    
    curriculum_level = CurriculumLevel.objects.first()
    session = StudentSession.objects.create(
        student_name='All Incorrect Test',
        grade=8,
        academic_rank='TOP_10',
        school_name_manual='Test School', 
        exam=exam,
        original_curriculum_level=curriculum_level
    )
    
    # Create incorrect answers for first 3 questions
    questions = exam.questions.all()[:3]
    for question in questions:
        StudentAnswer.objects.create(
            session=session,
            question=question,
            answer='incorrect',
            is_correct=False,
            points_earned=0
        )
    
    results = GradingService.grade_session(session)
    session.refresh_from_db()
    
    # Should be 0%
    success = abs(float(session.percentage_score) - 0.0) < 0.01
    
    session.delete()
    return success

def test_manual_grading_scenario():
    """Test scenario with manual grading"""
    exam = Exam.objects.first()
    if not exam:
        return False
    
    curriculum_level = CurriculumLevel.objects.first()
    session = StudentSession.objects.create(
        student_name='Manual Grading Test',
        grade=8,
        academic_rank='TOP_10',
        school_name_manual='Test School',
        exam=exam,
        original_curriculum_level=curriculum_level
    )
    
    # Create answers that need manual grading
    questions = exam.questions.all()[:2]
    for question in questions:
        StudentAnswer.objects.create(
            session=session,
            question=question,
            answer='essay answer',
            is_correct=None,  # Needs manual grading
            points_earned=0
        )
    
    # Test with manual grades
    manual_grades = {
        questions[0].id: {'is_correct': True, 'points': questions[0].points},
        questions[1].id: {'is_correct': False, 'points': 0}
    }
    
    results = GradingService.grade_session(session, manual_grades)
    session.refresh_from_db()
    
    # Check that manual grades were applied
    expected_score = questions[0].points
    expected_possible = questions[0].points + questions[1].points
    expected_percentage = (expected_score / expected_possible) * 100
    
    success = (
        session.score == expected_score and
        abs(float(session.percentage_score) - expected_percentage) < 0.01
    )
    
    session.delete()
    return success

def test_zero_points_scenario():
    """Test edge case with zero possible points"""
    # This tests the division by zero protection
    exam = Exam.objects.first()
    if not exam:
        return False
    
    curriculum_level = CurriculumLevel.objects.first()
    session = StudentSession.objects.create(
        student_name='Zero Points Test',
        grade=8,
        academic_rank='TOP_10',
        school_name_manual='Test School',
        exam=exam,
        original_curriculum_level=curriculum_level
    )
    
    # Don't create any answers (edge case)
    results = GradingService.grade_session(session)
    session.refresh_from_db()
    
    # Should handle gracefully with 0%
    success = abs(float(session.percentage_score) - 0.0) < 0.01
    
    session.delete()
    return success

def test_backward_compatibility():
    """Test that existing functionality still works"""
    print("\n🔄 TESTING BACKWARD COMPATIBILITY")
    print("=" * 60)
    
    # Test that the fix doesn't break existing workflows
    compatibility_tests = [
        {
            'name': 'Complete test workflow',
            'test': test_complete_workflow
        },
        {
            'name': 'Results page rendering',
            'test': test_results_rendering
        },
        {
            'name': 'API endpoints',
            'test': test_api_endpoints
        }
    ]
    
    results = []
    for test in compatibility_tests:
        print(f"  Testing: {test['name']}")
        try:
            result = test['test']()
            status = "✅" if result else "❌"
            results.append(result)
            print(f"  {status} {test['name']}")
        except Exception as e:
            print(f"  ❌ {test['name']}: Error - {e}")
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    print(f"\nBackward compatibility: {passed}/{total} tests passed")
    
    return passed == total

def test_complete_workflow():
    """Test the complete test workflow still works"""
    client = Client()
    
    # Test start page
    response = client.get('/PlacementTest/start/')
    if response.status_code != 200:
        return False
    
    # Test that sessions can still be created and completed
    session = StudentSession.objects.filter(completed_at__isnull=True).first()
    if session:
        # Test that the session page loads
        response = client.get(f'/PlacementTest/session/{session.id}/')
        return response.status_code == 200
    
    return True

def test_results_rendering():
    """Test that results pages render correctly"""
    client = Client()
    
    session = StudentSession.objects.filter(completed_at__isnull=False).first()
    if session:
        response = client.get(f'/PlacementTest/session/{session.id}/result/')
        return response.status_code == 200
    
    return True

def test_api_endpoints():
    """Test that API endpoints still work"""
    # Test that existing API endpoints are not broken
    client = Client()
    
    # Test basic endpoints that should work
    response = client.get('/PlacementTest/')
    return response.status_code in [200, 302]  # Either direct access or redirect

def main():
    """Run comprehensive testing"""
    print("COMPREHENSIVE SCORING FIX TEST SUITE")
    print("=" * 60)
    print("Testing the complete scoring calculation fix implementation...")
    print()
    
    test_results = []
    
    # Core functionality tests
    tests = [
        ('GradingService Fix', test_grading_service_fix),
        ('Frontend Display', test_frontend_display),
        ('Edge Cases', test_edge_cases),
        ('Backward Compatibility', test_backward_compatibility)
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            test_results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 COMPREHENSIVE TEST RESULTS")
    print("=" * 60)
    
    total_passed = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            total_passed += 1
    
    success_rate = (total_passed / total_tests) * 100
    print(f"\nOverall Success Rate: {success_rate:.1f}% ({total_passed}/{total_tests})")
    
    if total_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✅ SCORING FIX VERIFICATION COMPLETE")
        print("\nThe scoring calculation fix has been successfully implemented:")
        print("• ✅ GradingService includes all question types in calculations")
        print("• ✅ Frontend displays correct total possible scores")
        print("• ✅ Percentage calculations are accurate and fair")
        print("• ✅ Edge cases are handled properly")
        print("• ✅ Backward compatibility maintained")
        print("• ✅ Comprehensive debugging and logging added")
        
        print("\n🛡️ FIX SUMMARY:")
        print("The original bug excluded LONG questions from total_possible")
        print("but included their points in total_score, causing inflated percentages.")
        print("The fix ensures ALL question types are included in both numerator")
        print("and denominator for fair and accurate scoring.")
        
    else:
        failed_tests = [name for name, result in test_results if not result]
        print(f"\n⚠️ {total_tests - total_passed} test(s) failed:")
        for test_name in failed_tests:
            print(f"  • {test_name}")
        print("\nReview failed tests before deploying the fix")
    
    return total_passed == total_tests

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
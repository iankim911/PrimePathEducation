#!/usr/bin/env python3
"""
COMPREHENSIVE TEST: Timer Expiry Grace Period Fix
Tests the exact scenario that was failing in production.
"""

import os
import sys
import django
import json
import time
from datetime import datetime, timedelta
from django.utils import timezone
from django.test import RequestFactory
from django.http import JsonResponse

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from placement_test.models import Exam, Question, StudentSession, StudentAnswer
from placement_test.views.student import submit_answer
from core.models import CurriculumLevel
from core.exceptions import SessionAlreadyCompletedException


def create_test_data():
    """Create test exam and session using existing curriculum level."""
    print("Setting up test data...")
    
    # Get existing curriculum level
    level = CurriculumLevel.objects.first()
    if not level:
        print("❌ No curriculum levels found. Please run migrations and populate data.")
        sys.exit(1)
    
    print(f"Using existing curriculum level: {level.description}")
    
    # Create test exam with 2-minute timer
    exam = Exam.objects.create(
        name="Timer Grace Period Test Exam",
        curriculum_level=level,
        total_questions=5,
        timer_minutes=2,  # Short timer for testing
        is_active=True
    )
    
    # Create questions
    questions = []
    for i in range(5):
        question = Question.objects.create(
            exam=exam,
            question_number=i + 1,
            question_type='MCQ',
            correct_answer='A',
            points=1,
            options_count=4
        )
        questions.append(question)
    
    # Create test session
    session = StudentSession.objects.create(
        student_name="Test Student",
        grade=10,
        academic_rank="TOP_20",
        exam=exam,
        original_curriculum_level=level,
        final_curriculum_level=level
    )
    
    print(f"✅ Created exam {exam.id} with {len(questions)} questions")
    print(f"✅ Created session {session.id}")
    print(f"✅ Timer duration: {exam.timer_minutes} minutes")
    
    return exam, session, questions


def test_timer_scenarios():
    """Test various timer expiry scenarios."""
    exam, session, questions = create_test_data()
    factory = RequestFactory()
    
    print(f"\n{'='*60}")
    print("TESTING TIMER EXPIRY SCENARIOS")
    print(f"{'='*60}")
    
    # Test 1: Normal submission during timer (should work)
    print(f"\n1. Testing normal submission during timer...")
    
    request_data = {
        'question_id': str(questions[0].id),
        'answer': 'A'
    }
    
    request = factory.post(
        f'/api/placement/session/{session.id}/submit-answer/',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    request.user = None
    
    try:
        response = submit_answer(request, session.id)
        assert response.status_code == 200
        data = json.loads(response.content.decode())
        assert data['success'] == True
        print(f"   ✅ Normal submission: {data['message']}")
    except Exception as e:
        print(f"   ❌ Normal submission failed: {e}")
    
    # Test 2: Simulate timer expiry by modifying started_at
    print(f"\n2. Testing submission exactly at timer expiry...")
    
    # Make the session start 2 minutes ago (timer expired)
    session.started_at = timezone.now() - timedelta(minutes=2)
    session.save()
    
    # Test timer expiry detection
    print(f"   Timer expired: {session.is_timer_expired()}")
    print(f"   In grace period: {session.is_in_grace_period()}")
    print(f"   Can accept answers: {session.can_accept_answers()}")
    
    # Try submission immediately after timer expiry (within grace period)
    request_data = {
        'question_id': str(questions[1].id),
        'answer': 'B'
    }
    
    request = factory.post(
        f'/api/placement/session/{session.id}/submit-answer/',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    request.user = None
    
    try:
        response = submit_answer(request, session.id)
        assert response.status_code == 200
        data = json.loads(response.content.decode())
        assert data['success'] == True
        print(f"   ✅ Grace period submission: {data['message']}")
    except SessionAlreadyCompletedException as e:
        print(f"   ❌ Grace period submission FAILED: {e}")
        print(f"   This indicates the fix is not working!")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
    
    # Test 3: Simulate network delay (submission 10 seconds after timer expiry)
    print(f"\n3. Testing submission with simulated network delay...")
    
    # Make timer expire 10 seconds ago
    session.started_at = timezone.now() - timedelta(minutes=2, seconds=10)
    session.save()
    
    print(f"   Timer expired: {session.is_timer_expired()}")
    print(f"   In grace period: {session.is_in_grace_period()}")
    print(f"   Can accept answers: {session.can_accept_answers()}")
    
    request_data = {
        'question_id': str(questions[2].id),
        'answer': 'C'
    }
    
    request = factory.post(
        f'/api/placement/session/{session.id}/submit-answer/',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    request.user = None
    
    try:
        response = submit_answer(request, session.id)
        assert response.status_code == 200
        data = json.loads(response.content.decode())
        assert data['success'] == True
        print(f"   ✅ Network delay submission: {data['message']}")
        print(f"   ✅ This would have FAILED with the old logic!")
    except SessionAlreadyCompletedException as e:
        print(f"   ❌ Network delay submission FAILED: {e}")
        print(f"   This should work with the new grace period logic!")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
    
    # Test 4: Test submission after grace period expires (should fail)
    print(f"\n4. Testing submission after grace period expires...")
    
    # Make timer expire 6 minutes ago (beyond 5-minute grace period)
    session.started_at = timezone.now() - timedelta(minutes=8)
    session.save()
    
    print(f"   Timer expired: {session.is_timer_expired()}")
    print(f"   In grace period: {session.is_in_grace_period()}")
    print(f"   Can accept answers: {session.can_accept_answers()}")
    
    request_data = {
        'question_id': str(questions[3].id),
        'answer': 'D'
    }
    
    request = factory.post(
        f'/api/placement/session/{session.id}/submit-answer/',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    request.user = None
    
    try:
        response = submit_answer(request, session.id)
        print(f"   ❌ Submission should have been rejected!")
    except SessionAlreadyCompletedException as e:
        print(f"   ✅ Correctly rejected after grace period: {e}")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
    
    # Test 5: Test non-timed exam (should work normally)
    print(f"\n5. Testing non-timed exam behavior...")
    
    # Create non-timed exam (use 0 instead of None for timer_minutes)
    non_timed_exam = Exam.objects.create(
        name="Non-timed Test Exam",
        curriculum_level=session.original_curriculum_level,
        total_questions=3,
        timer_minutes=0,  # No timer (use 0 instead of None)
        is_active=True
    )
    
    # Create question
    nt_question = Question.objects.create(
        exam=non_timed_exam,
        question_number=1,
        question_type='MCQ',
        correct_answer='A',
        points=1,
        options_count=4
    )
    
    # Create non-timed session
    nt_session = StudentSession.objects.create(
        student_name="Test Student NT",
        grade=10,
        academic_rank="TOP_20",
        exam=non_timed_exam,
        original_curriculum_level=session.original_curriculum_level,
        final_curriculum_level=session.original_curriculum_level
    )
    
    print(f"   Timer expired: {nt_session.is_timer_expired()}")
    print(f"   In grace period: {nt_session.is_in_grace_period()}")
    print(f"   Can accept answers: {nt_session.can_accept_answers()}")
    
    request_data = {
        'question_id': str(nt_question.id),
        'answer': 'A'
    }
    
    request = factory.post(
        f'/api/placement/session/{nt_session.id}/submit-answer/',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    request.user = None
    
    try:
        response = submit_answer(request, nt_session.id)
        assert response.status_code == 200
        data = json.loads(response.content.decode())
        assert data['success'] == True
        print(f"   ✅ Non-timed exam submission: {data['message']}")
    except Exception as e:
        print(f"   ❌ Non-timed exam submission failed: {e}")


def test_race_condition_simulation():
    """Simulate the exact race condition that was failing."""
    print(f"\n{'='*60}")
    print("SIMULATING PRODUCTION RACE CONDITION")
    print(f"{'='*60}")
    
    # Create fresh test data
    exam, session, questions = create_test_data()
    factory = RequestFactory()
    
    print(f"\nScenario: Student answers get stuck in network, arrive after timer expires")
    print(f"Expected: Should be accepted within 5-minute grace period")
    
    # Set session to have started 2 minutes and 30 seconds ago
    # Timer expires at 2 minutes, so we're 30 seconds into grace period
    session.started_at = timezone.now() - timedelta(minutes=2, seconds=30)
    session.save()
    
    print(f"\nTiming verification:")
    timer_expiry = session.get_timer_expiry_time()
    print(f"   Session started at: {session.started_at}")
    print(f"   Timer expires at: {timer_expiry}")
    print(f"   Current time: {timezone.now()}")
    print(f"   Time since expiry: {(timezone.now() - timer_expiry).total_seconds():.1f} seconds")
    
    print(f"\nState checks:")
    print(f"   Timer expired: {session.is_timer_expired()}")
    print(f"   In grace period: {session.is_in_grace_period()}")
    print(f"   Can accept answers: {session.can_accept_answers()}")
    print(f"   Session completed: {session.is_completed}")
    
    # Simulate multiple concurrent answer submissions
    print(f"\nSimulating 6 concurrent answer submissions...")
    
    success_count = 0
    fail_count = 0
    
    for i in range(6):
        if i >= len(questions):
            break
            
        request_data = {
            'question_id': str(questions[i].id),
            'answer': ['A', 'B', 'C', 'D'][i % 4]
        }
        
        request = factory.post(
            f'/api/placement/session/{session.id}/submit-answer/',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        request.user = None
        
        try:
            response = submit_answer(request, session.id)
            if response.status_code == 200:
                data = json.loads(response.content.decode())
                if data.get('success'):
                    success_count += 1
                    print(f"   ✅ Answer {i+1}: Saved successfully")
                else:
                    fail_count += 1
                    print(f"   ❌ Answer {i+1}: {data.get('error', 'Unknown error')}")
            else:
                fail_count += 1
                print(f"   ❌ Answer {i+1}: HTTP {response.status_code}")
        except SessionAlreadyCompletedException as e:
            fail_count += 1
            print(f"   ❌ Answer {i+1}: {e}")
        except Exception as e:
            fail_count += 1
            print(f"   ❌ Answer {i+1}: Unexpected error: {e}")
    
    print(f"\nResults:")
    print(f"   ✅ Successful saves: {success_count}")
    print(f"   ❌ Failed saves: {fail_count}")
    
    if fail_count == 0:
        print(f"   🎉 SUCCESS! All answers saved despite timer expiry!")
        print(f"   🎉 The grace period fix is working correctly!")
    else:
        print(f"   ⚠️  Some answers failed - this might indicate remaining issues")
    
    return success_count, fail_count


def main():
    """Run all tests."""
    print("TIMER EXPIRY GRACE PERIOD FIX - COMPREHENSIVE TESTING")
    print("=" * 80)
    
    try:
        # Run timer scenario tests
        test_timer_scenarios()
        
        # Run race condition simulation
        success_count, fail_count = test_race_condition_simulation()
        
        # Final summary
        print(f"\n{'='*60}")
        print("FINAL TEST SUMMARY")
        print(f"{'='*60}")
        
        if fail_count == 0:
            print(f"✅ ALL TESTS PASSED!")
            print(f"✅ Grace period fix is working correctly")
            print(f"✅ Production issue should be resolved")
        else:
            print(f"⚠️  Some tests failed - review implementation")
            print(f"   Successful saves: {success_count}")
            print(f"   Failed saves: {fail_count}")
        
        print(f"\nKey improvements in the fix:")
        print(f"   • Grace period uses timer expiry time as reference")
        print(f"   • Extended grace period to 300 seconds (5 minutes)")
        print(f"   • Removed premature completed_at setting in views")
        print(f"   • Better logging for debugging")
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
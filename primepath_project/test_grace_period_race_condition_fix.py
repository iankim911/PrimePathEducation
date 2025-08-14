#!/usr/bin/env python3
"""
FOCUSED TEST: Race Condition Fix for Timer Expiry Grace Period
Tests the exact production scenario that was failing.
"""

import os
import sys
import django
import json
from datetime import timedelta
from django.utils import timezone
from django.test import RequestFactory

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from placement_test.models import Exam, Question, StudentSession
from placement_test.views.student import submit_answer
from core.models import CurriculumLevel
from core.exceptions import SessionAlreadyCompletedException


def test_production_race_condition():
    """Test the exact race condition scenario that was failing in production."""
    print("=" * 80)
    print("RACE CONDITION FIX TEST - Production Scenario")
    print("=" * 80)
    
    # Use existing curriculum level
    level = CurriculumLevel.objects.first()
    if not level:
        print("❌ No curriculum levels found")
        return False
    
    # Create test exam with 3-minute timer
    exam = Exam.objects.create(
        name="Race Condition Test Exam",
        curriculum_level=level,
        total_questions=6,
        timer_minutes=3,  # 3-minute timer
        is_active=True
    )
    
    # Create questions
    questions = []
    for i in range(6):
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
        student_name="Race Condition Test Student",
        grade=10,
        academic_rank="TOP_20",
        exam=exam,
        original_curriculum_level=level,
        final_curriculum_level=level
    )
    
    print(f"\n📝 Test Setup:")
    print(f"   Exam: {exam.name}")
    print(f"   Timer: {exam.timer_minutes} minutes")
    print(f"   Questions: {len(questions)}")
    print(f"   Session: {session.id}")
    
    # Simulate the exact production scenario:
    # Student answers questions normally, then timer expires while multiple answers
    # are still in transit due to network delays
    
    print(f"\n🎯 Production Scenario Simulation:")
    print(f"   Student answers questions, timer expires, network delays cause")
    print(f"   answer submissions to arrive after timer expiry")
    
    # Set session to have timer expired 15 seconds ago
    # This simulates the network delay scenario
    session.started_at = timezone.now() - timedelta(minutes=3, seconds=15)
    session.save()
    
    # Verify timing
    timer_expiry = session.get_timer_expiry_time()
    current_time = timezone.now()
    time_since_expiry = (current_time - timer_expiry).total_seconds()
    
    print(f"\n⏰ Timing Verification:")
    print(f"   Session started: {session.started_at.strftime('%H:%M:%S')}")
    print(f"   Timer expires:   {timer_expiry.strftime('%H:%M:%S')}")
    print(f"   Current time:    {current_time.strftime('%H:%M:%S')}")
    print(f"   Time since expiry: {time_since_expiry:.1f} seconds")
    
    # Check state
    print(f"\n🔍 Session State Check:")
    print(f"   Timer expired: {session.is_timer_expired()}")
    print(f"   In grace period: {session.is_in_grace_period()}")
    print(f"   Can accept answers: {session.can_accept_answers()}")
    print(f"   Session completed: {session.is_completed}")
    
    # The critical test: Submit 6 answers that arrive after timer expiry
    print(f"\n🚀 Submitting 6 answers after timer expiry (simulating network delays)...")
    
    factory = RequestFactory()
    success_count = 0
    fail_count = 0
    
    for i in range(6):
        request_data = {
            'question_id': str(questions[i].id),
            'answer': ['A', 'B', 'C', 'D', 'A', 'B'][i]
        }
        
        request = factory.post(
            f'/api/PlacementTest/session/{session.id}/submit-answer/',
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
                    print(f"   ❌ Answer {i+1}: {data.get('error')}")
            else:
                fail_count += 1
                print(f"   ❌ Answer {i+1}: HTTP {response.status_code}")
        except SessionAlreadyCompletedException as e:
            fail_count += 1
            print(f"   ❌ Answer {i+1}: Session completed (old bug behavior)")
        except Exception as e:
            fail_count += 1
            print(f"   ❌ Answer {i+1}: Unexpected error: {e}")
    
    # Results
    print(f"\n📊 Results:")
    print(f"   ✅ Successfully saved: {success_count}/6 answers")
    print(f"   ❌ Failed to save: {fail_count}/6 answers")
    
    # Determine if fix worked
    if success_count == 6:
        print(f"\n🎉 SUCCESS! Grace period fix is working correctly!")
        print(f"   All answers saved despite timer expiry + network delays")
        print(f"   This would have been 'Failed to save 6 answer(s)' with the old logic")
        success = True
    elif success_count > 0:
        print(f"\n⚠️  PARTIAL SUCCESS: {success_count} answers saved")
        print(f"   This is better than the old logic (0 saved) but not perfect")
        success = False
    else:
        print(f"\n❌ FAILURE: No answers saved - fix is not working")
        success = False
    
    # Test boundary condition: Submit after grace period expires
    print(f"\n🔒 Testing boundary: Submission after grace period expires...")
    
    # Set timer to have expired 6 minutes ago (beyond 5-minute grace period)
    session.started_at = timezone.now() - timedelta(minutes=9)
    session.save()
    
    print(f"   Time since expiry: {(timezone.now() - session.get_timer_expiry_time()).total_seconds():.0f} seconds")
    print(f"   In grace period: {session.is_in_grace_period()}")
    print(f"   Can accept answers: {session.can_accept_answers()}")
    
    # Try to submit - should fail
    try:
        # Create a new question for this test
        boundary_question = Question.objects.create(
            exam=exam,
            question_number=7,
            question_type='MCQ',
            correct_answer='A',
            points=1,
            options_count=4
        )
        
        request_data = {
            'question_id': str(boundary_question.id),
            'answer': 'A'
        }
        
        request = factory.post(
            f'/api/PlacementTest/session/{session.id}/submit-answer/',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        request.user = None
        
        response = submit_answer(request, session.id)
        print(f"   ❌ Boundary test FAILED: Should have been rejected")
        success = False
    except SessionAlreadyCompletedException:
        print(f"   ✅ Boundary test PASSED: Correctly rejected after grace period")
    except Exception as e:
        print(f"   ❌ Boundary test ERROR: {e}")
    
    # Cleanup
    exam.delete()
    
    return success


def main():
    """Run the race condition test."""
    print("TIMER EXPIRY GRACE PERIOD - RACE CONDITION FIX TEST")
    
    try:
        success = test_production_race_condition()
        
        print(f"\n{'='*60}")
        print("FINAL RESULT")
        print(f"{'='*60}")
        
        if success:
            print("✅ Race condition fix is WORKING!")
            print("✅ Production issue should be resolved")
            print("✅ Students can now save answers during grace period")
        else:
            print("❌ Race condition fix needs more work")
            print("❌ Production issue may still occur")
        
        print(f"\nFix details:")
        print(f"   • Grace period calculated from timer expiry time (not completed_at)")
        print(f"   • Extended grace period to 5 minutes")
        print(f"   • Removed premature completed_at setting in views")
        print(f"   • Enhanced logging for debugging")
        
        return success
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
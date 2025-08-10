#!/usr/bin/env python
"""
Comprehensive test for timer expiry grace period fix
Tests the critical fix for answer submission failures when timer expires
"""

import os
import sys
import django
import json
from django.test import Client
from django.utils import timezone
from unittest.mock import patch
import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from placement_test.models import StudentSession, Exam, Question
from core.models import CurriculumLevel

def test_timer_expiry_grace_period_fix():
    """Test that timer expiry allows grace period saves"""
    print("🔍 TIMER EXPIRY GRACE PERIOD FIX TEST")
    print("=" * 60)
    
    client = Client()
    results = {'passed': 0, 'failed': 0, 'issues': []}
    
    def check(name, condition, message=""):
        if condition:
            print(f"✅ {name}")
            results['passed'] += 1
        else:
            print(f"❌ {name}: {message}")
            results['failed'] += 1
            results['issues'].append(f"{name}: {message}")
    
    # Get test data
    exam = Exam.objects.filter(is_active=True, timer_minutes__isnull=False).first()
    if not exam:
        print("❌ No timed exams found for testing")
        return False
    
    question = exam.questions.first()
    if not question:
        print("❌ No questions found in timed exam")
        return False
    
    print(f"Using exam: {exam.name} (Timer: {exam.timer_minutes} min)")
    print(f"Using question: {question.id}")
    
    # Test 1: Create session and test normal submission (before timer expiry)
    print("\n1. Testing normal submission before timer expiry")
    session = StudentSession.objects.create(
        student_name="Timer Test Student",
        parent_phone="010-1234-5678", 
        school_id=1,
        grade=8,
        academic_rank="TOP_20",
        exam=exam
    )
    # Update started_at to bypass auto_now_add
    past_time = timezone.now() - datetime.timedelta(minutes=exam.timer_minutes - 1)  # 1 minute before expiry
    StudentSession.objects.filter(id=session.id).update(started_at=past_time)
    session.refresh_from_db()
    
    # Test utility methods
    check("Session not completed initially", not session.is_completed)
    check("Session can accept answers initially", session.can_accept_answers())
    check("Session not in grace period initially", not session.is_in_grace_period())
    
    # Submit answer before timer expiry
    response = client.post(
        f'/api/placement/session/{session.id}/submit/',
        data=json.dumps({
            'question_id': str(question.id),
            'answer': 'Test answer before expiry'
        }),
        content_type='application/json'
    )
    check("Answer submission before timer expiry succeeds", response.status_code == 200, f"Status: {response.status_code}")
    
    # Test 2: Test submission exactly at timer expiry
    print("\n2. Testing submission at timer expiry (should trigger completion)")
    
    # Create session that expired exactly now
    expired_session = StudentSession.objects.create(
        student_name="Expired Timer Test",
        parent_phone="010-1234-5679",
        school_id=1, 
        grade=8,
        academic_rank="TOP_20",
        exam=exam
    )
    # Update started_at to bypass auto_now_add
    expired_time = timezone.now() - datetime.timedelta(minutes=exam.timer_minutes + 1)  # 1 minute past expiry
    StudentSession.objects.filter(id=expired_session.id).update(started_at=expired_time)
    expired_session.refresh_from_db()
    
    print(f"Session {expired_session.id} created with expiry time")
    
    # Submit answer - this should mark session complete but allow the save
    response = client.post(
        f'/api/placement/session/{expired_session.id}/submit/',
        data=json.dumps({
            'question_id': str(question.id),
            'answer': 'Test answer at timer expiry'
        }),
        content_type='application/json'
    )
    
    # Refresh from database
    expired_session.refresh_from_db()
    
    check("Timer expired session marked as complete", expired_session.is_completed)
    check("Timer expired session in grace period", expired_session.is_in_grace_period())
    check("Timer expired session can still accept answers", expired_session.can_accept_answers())
    check("Answer submission at timer expiry succeeds", response.status_code == 200, f"Status: {response.status_code}, Content: {response.content.decode()}")
    
    # Test 3: Test multiple submissions during grace period
    print("\n3. Testing multiple submissions during grace period")
    
    question2 = exam.questions.all()[1] if exam.questions.count() > 1 else question
    
    # Submit another answer during grace period
    response = client.post(
        f'/api/placement/session/{expired_session.id}/submit/',
        data=json.dumps({
            'question_id': str(question2.id),
            'answer': 'Second answer during grace period'
        }),
        content_type='application/json'
    )
    
    check("Second submission during grace period succeeds", response.status_code == 200, f"Status: {response.status_code}")
    
    # Test 4: Test submission after grace period expires
    print("\n4. Testing submission after grace period expires")
    
    # Create session completed more than 60 seconds ago
    old_completed_session = StudentSession.objects.create(
        student_name="Old Completed Test",
        parent_phone="010-1234-5680",
        school_id=1,
        grade=8, 
        academic_rank="TOP_20",
        exam=exam
    )
    # Update completed_at to 2 minutes ago
    old_completion_time = timezone.now() - datetime.timedelta(minutes=2)
    StudentSession.objects.filter(id=old_completed_session.id).update(completed_at=old_completion_time)
    old_completed_session.refresh_from_db()
    
    check("Old completed session is completed", old_completed_session.is_completed)
    check("Old completed session NOT in grace period", not old_completed_session.is_in_grace_period())
    check("Old completed session cannot accept answers", not old_completed_session.can_accept_answers())
    
    # Submit answer - this should fail
    response = client.post(
        f'/api/placement/session/{old_completed_session.id}/submit/',
        data=json.dumps({
            'question_id': str(question.id),
            'answer': 'Answer after grace period'
        }),
        content_type='application/json'
    )
    
    check("Submission after grace period fails", response.status_code == 400, f"Status: {response.status_code}")
    
    # Test 5: Test real-world scenario - the exact failing session
    print("\n5. Testing real-world scenario simulation")
    
    # Simulate the exact scenario from the bug report
    failing_session = StudentSession.objects.create(
        student_name="Real World Test",
        parent_phone="010-9999-8888",
        school_id=1,
        grade=8,
        academic_rank="TOP_20", 
        exam=exam
    )
    # Update started_at to just expired
    just_expired_time = timezone.now() - datetime.timedelta(minutes=exam.timer_minutes + 0.5)  # Just expired
    StudentSession.objects.filter(id=failing_session.id).update(started_at=just_expired_time)
    failing_session.refresh_from_db()
    
    # Simulate multiple rapid submissions (like the failing scenario)
    questions_to_test = list(exam.questions.all()[:3])
    success_count = 0
    
    for i, q in enumerate(questions_to_test):
        response = client.post(
            f'/api/placement/session/{failing_session.id}/submit/',
            data=json.dumps({
                'question_id': str(q.id),
                'answer': f'Rapid submission {i+1}'
            }),
            content_type='application/json'
        )
        if response.status_code == 200:
            success_count += 1
    
    check("Multiple rapid submissions during grace period succeed", success_count == len(questions_to_test), f"{success_count}/{len(questions_to_test)} succeeded")
    
    # Test 6: Verify other features not affected
    print("\n6. Testing that other features not affected")
    
    # Test that complete_session still rejects completed sessions
    # First ensure the failing_session is marked complete by triggering timer expiry logic
    failing_session.refresh_from_db()
    
    # Force completion by marking completed_at
    StudentSession.objects.filter(id=failing_session.id).update(completed_at=timezone.now())
    failing_session.refresh_from_db()
    
    try:
        from placement_test.services.session_service import SessionService
        SessionService.complete_session(failing_session)
        check("Complete session rejects completed session", False, "Should have thrown exception")
    except Exception as e:
        check("Complete session rejects completed session", "already been completed" in str(e).lower())
    
    # Summary
    print(f"\n{'='*60}")
    print(f"TIMER EXPIRY GRACE PERIOD FIX TEST SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    total = results['passed'] + results['failed']
    success_rate = (results['passed'] / total * 100) if total > 0 else 0
    print(f"📊 Success Rate: {success_rate:.1f}%")
    
    if results['issues']:
        print(f"\n⚠️ Issues Found:")
        for issue in results['issues']:
            print(f"  - {issue}")
    else:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ Timer expiry grace period fix working correctly")
        print(f"✅ Answer submissions allowed during grace period")
        print(f"✅ Submissions blocked after grace period")
        print(f"✅ Other features not affected")
    
    # Cleanup
    StudentSession.objects.filter(
        student_name__in=[
            "Timer Test Student",
            "Expired Timer Test", 
            "Old Completed Test",
            "Real World Test"
        ]
    ).delete()
    
    return results['failed'] == 0

if __name__ == '__main__':
    success = test_timer_expiry_grace_period_fix()
    sys.exit(0 if success else 1)
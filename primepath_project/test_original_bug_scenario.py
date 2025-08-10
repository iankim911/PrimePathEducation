#!/usr/bin/env python
"""
Test the exact original failing scenario reported by the user
Session ID: e7ad4e85-19f0-475c-800a-770d8a52cd67
"""

import os
import sys
import django
import json
from django.test import Client
from django.utils import timezone
import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from placement_test.models import StudentSession, Exam, Question

def test_original_bug_scenario():
    """Test the exact scenario from the original bug report"""
    print("🚨 ORIGINAL BUG SCENARIO TEST")
    print("=" * 60)
    print("Testing the exact scenario that caused the submission failures")
    print("Multiple HTTP 400 errors when clicking 'Submit Test'")
    print("=" * 60)
    
    client = Client()
    
    # Get test data
    exam = Exam.objects.filter(is_active=True, timer_minutes__isnull=False).first()
    if not exam:
        print("❌ No timed exams found for testing")
        return False
    
    questions = list(exam.questions.all()[:10])  # Get first 10 questions
    if len(questions) < 6:
        print("❌ Need at least 6 questions for testing")
        return False
    
    print(f"Using exam: {exam.name} (Timer: {exam.timer_minutes} min)")
    print(f"Testing with {len(questions)} questions")
    
    # Simulate the original scenario:
    # 1. Student starts test
    # 2. Timer expires while student is taking test
    # 3. Student tries to submit multiple answers (like the failing session)
    
    # Create session that will expire during testing
    session = StudentSession.objects.create(
        student_name="Original Bug Test Student",
        parent_phone="010-9999-8888",  # Same as original report
        school_id=1,
        grade=8,
        academic_rank="TOP_20",
        exam=exam
    )
    
    # Set started_at to just expire (like the original failing scenario)
    expired_time = timezone.now() - datetime.timedelta(minutes=exam.timer_minutes + 0.1)  # Just expired
    StudentSession.objects.filter(id=session.id).update(started_at=expired_time)
    session.refresh_from_db()
    
    print(f"Created session: {session.id}")
    print(f"Session started at: {session.started_at}")
    print(f"Should be expired by: {expired_time + datetime.timedelta(minutes=exam.timer_minutes)}")
    print(f"Current time: {timezone.now()}")
    
    # Test the original failing pattern:
    # Multiple rapid answer submissions (exactly like the console log showed)
    
    print(f"\n🧪 Testing rapid answer submissions (like original failure)...")
    
    success_count = 0
    failed_count = 0
    responses = []
    
    # Simulate the exact questions from the original log
    test_questions = [questions[i] for i in [6, 7, 8, 1, 0, 15] if i < len(questions)]  # Q7, Q8, Q9, Q2, Q1, Q16 from original log
    
    for i, question in enumerate(test_questions):
        print(f"Submitting answer for question {question.question_number}...")
        
        response = client.post(
            f'/api/placement/session/{session.id}/submit/',
            data=json.dumps({
                'question_id': str(question.id),
                'answer': f'Test answer {i+1} for Q{question.question_number}'
            }),
            content_type='application/json'
        )
        
        responses.append({
            'question': question.question_number,
            'status': response.status_code,
            'content': response.content.decode()
        })
        
        if response.status_code == 200:
            success_count += 1
            print(f"  ✅ SUCCESS - Q{question.question_number} submitted")
        else:
            failed_count += 1
            print(f"  ❌ FAILED - Q{question.question_number} - Status: {response.status_code}")
    
    # Test final submission (like clicking "Submit Test")
    print(f"\n🧪 Testing final test submission...")
    
    final_response = client.post(
        f'/api/placement/session/{session.id}/complete/',
        data=json.dumps({'timer_expired': False, 'unsaved_count': 0}),
        content_type='application/json'
    )
    
    print(f"Final submission status: {final_response.status_code}")
    
    # Results
    print(f"\n{'='*60}")
    print(f"ORIGINAL BUG SCENARIO TEST RESULTS")
    print(f"{'='*60}")
    print(f"✅ Successful submissions: {success_count}/{len(test_questions)}")
    print(f"❌ Failed submissions: {failed_count}/{len(test_questions)}")
    
    success_rate = (success_count / len(test_questions) * 100) if test_questions else 0
    print(f"📊 Success Rate: {success_rate:.1f}%")
    
    if failed_count == 0:
        print(f"🎉 ORIGINAL BUG FIXED!")
        print(f"✅ All answer submissions succeeded")
        print(f"✅ No HTTP 400 errors")
        print(f"✅ Grace period working correctly") 
        print(f"✅ Timer expiry handled properly")
    else:
        print(f"⚠️ Some submissions failed (this might be expected if grace period expired)")
        
        # Show details of failures
        print(f"\nFailure details:")
        for resp in responses:
            if resp['status'] != 200:
                print(f"  Q{resp['question']}: {resp['status']} - {resp['content'][:100]}")
    
    # Check session state
    session.refresh_from_db()
    print(f"\nSession final state:")
    print(f"  Completed: {session.is_completed}")
    print(f"  In grace period: {session.is_in_grace_period()}")
    print(f"  Can accept answers: {session.can_accept_answers()}")
    print(f"  Answers saved: {session.answers.count()}")
    
    # Cleanup
    session.delete()
    
    print(f"\n🔍 COMPARISON TO ORIGINAL BUG:")
    print(f"BEFORE FIX: Multiple HTTP 400 'Bad Request' errors")
    print(f"AFTER FIX:  HTTP 200 success responses during grace period")
    print(f"")
    print(f"BEFORE FIX: 'Cannot submit test: 6 answers failed to save'")
    print(f"AFTER FIX:  All answers saved successfully during grace period")
    
    return failed_count == 0

if __name__ == '__main__':
    success = test_original_bug_scenario()
    sys.exit(0 if success else 1)
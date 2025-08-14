#!/usr/bin/env python
"""
Final live verification that the timer expiry fix is working
Tests against the running Django server
"""

import requests
import json
import os
import sys
import django
from django.utils import timezone
import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from placement_test.models import StudentSession, Exam

def test_live_server():
    """Test the fix against the running server"""
    print("🔴 LIVE SERVER VERIFICATION")
    print("=" * 60)
    print("Testing timer expiry grace period fix on running Django server")
    print("Server: http://127.0.0.1:8000")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test server is running
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ Server responding: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Server not responding: {e}")
        return False
    
    # Get test data
    exam = Exam.objects.filter(is_active=True, timer_minutes__isnull=False).first()
    if not exam:
        print("❌ No timed exams found")
        return False
    
    question = exam.questions.first()
    if not question:
        print("❌ No questions found")
        return False
    
    print(f"Using exam: {exam.name} (Timer: {exam.timer_minutes} min)")
    
    # Create expired session
    session = StudentSession.objects.create(
        student_name="Live Server Test",
        parent_phone="010-0000-LIVE",
        school_id=1,
        grade=8,
        academic_rank="TOP_20",
        exam=exam
    )
    
    # Make session expired
    expired_time = timezone.now() - datetime.timedelta(minutes=exam.timer_minutes + 1)
    StudentSession.objects.filter(id=session.id).update(started_at=expired_time)
    session.refresh_from_db()
    
    print(f"Created expired session: {session.id}")
    
    # Test live submission to running server
    print(f"\n🧪 Testing live answer submission...")
    
    url = f"{base_url}/api/PlacementTest/session/{session.id}/submit/"
    data = {
        'question_id': str(question.id),
        'answer': 'Live server test answer'
    }
    headers = {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    try:
        response = requests.post(url, data=json.dumps(data), headers=headers, timeout=10)
        
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text[:200]}")
        
        if response.status_code == 200:
            print("✅ LIVE SERVER TEST PASSED!")
            print("✅ Timer-expired session accepted answer submission")
            print("✅ Grace period working on live server")
            success = True
        else:
            print("❌ LIVE SERVER TEST FAILED!")
            print(f"❌ Status: {response.status_code}")
            print(f"❌ Content: {response.text}")
            success = False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        success = False
    
    # Verify session state
    session.refresh_from_db()
    print(f"\nSession final state:")
    print(f"  ID: {session.id}")
    print(f"  Completed: {session.is_completed}")
    print(f"  In grace period: {session.is_in_grace_period()}")
    print(f"  Can accept answers: {session.can_accept_answers()}")
    print(f"  Saved answers: {session.answers.count()}")
    
    # Cleanup
    session.delete()
    
    print(f"\n{'='*60}")
    if success:
        print("🎉 LIVE SERVER VERIFICATION SUCCESSFUL!")
        print("✅ Fix working correctly on running Django server")
        print("✅ Ready for production deployment")
    else:
        print("❌ LIVE SERVER VERIFICATION FAILED!")
        print("❌ Issue detected on running server")
    print(f"{'='*60}")
    
    return success

if __name__ == '__main__':
    success = test_live_server()
    sys.exit(0 if success else 1)
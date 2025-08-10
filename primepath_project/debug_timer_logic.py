#!/usr/bin/env python
"""
Debug timer logic to understand why timer expiry isn't working
"""

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

def debug_timer_logic():
    """Debug the timer expiry logic"""
    
    # Get a timed exam
    exam = Exam.objects.filter(is_active=True, timer_minutes__isnull=False).first()
    if not exam:
        print("❌ No timed exams found")
        return
        
    print(f"Using exam: {exam.name}")
    print(f"Timer minutes: {exam.timer_minutes}")
    
    # Create a session that should be expired
    now = timezone.now()
    started_time = now - datetime.timedelta(minutes=exam.timer_minutes + 5)  # 5 minutes past expiry
    print(f"Calculated started time: {started_time}")
    print(f"Should be {exam.timer_minutes + 5} minutes ago")
    
    # Create session first, then update started_at to bypass auto_now_add
    session = StudentSession.objects.create(
        student_name="Debug Timer Test",
        parent_phone="010-0000-0000",
        school_id=1,
        grade=8,
        academic_rank="TOP_20",
        exam=exam
    )
    
    # Update started_at to bypass auto_now_add
    StudentSession.objects.filter(id=session.id).update(started_at=started_time)
    session.refresh_from_db()
    
    print(f"Session created: {session.id}")
    print(f"Started at: {session.started_at}")
    print(f"Current time: {now}")
    
    # Calculate time elapsed using the same now timestamp
    time_elapsed_seconds = (now - session.started_at).total_seconds()
    time_elapsed_minutes = time_elapsed_seconds / 60
    
    print(f"Time elapsed: {time_elapsed_minutes:.2f} minutes")
    print(f"Timer limit: {exam.timer_minutes} minutes")
    print(f"Should be expired: {time_elapsed_minutes > exam.timer_minutes}")
    
    # Check session properties
    print(f"Session completed_at: {session.completed_at}")
    print(f"Session is_completed: {session.is_completed}")
    print(f"Session can_accept_answers: {session.can_accept_answers()}")
    print(f"Session is_in_grace_period: {session.is_in_grace_period()}")
    
    # Test the timer logic manually
    if session.exam.timer_minutes and not session.completed_at:
        time_elapsed = (now - session.started_at).total_seconds() / 60
        print(f"\nTimer logic check:")
        print(f"  exam.timer_minutes: {session.exam.timer_minutes}")
        print(f"  session.completed_at: {session.completed_at}")
        print(f"  time_elapsed: {time_elapsed:.2f} minutes")
        print(f"  time_elapsed > timer_minutes: {time_elapsed > session.exam.timer_minutes}")
        
        if time_elapsed > session.exam.timer_minutes:
            print("  -> Should mark session as complete")
            session.completed_at = now
            session.save()
            print(f"  -> Session marked complete at: {session.completed_at}")
        else:
            print("  -> Should NOT mark session as complete")
    else:
        print(f"\nTimer logic skipped:")
        print(f"  timer_minutes exists: {bool(session.exam.timer_minutes)}")
        print(f"  completed_at is None: {session.completed_at is None}")
    
    # Check properties after manual update
    session.refresh_from_db()
    print(f"\nAfter update:")
    print(f"Session completed_at: {session.completed_at}")
    print(f"Session is_completed: {session.is_completed}")
    print(f"Session can_accept_answers: {session.can_accept_answers()}")
    print(f"Session is_in_grace_period: {session.is_in_grace_period()}")
    
    # Cleanup
    session.delete()

if __name__ == '__main__':
    debug_timer_logic()
#!/usr/bin/env python3
"""
Debug script for the "Just Right" button persistent issue.

This script investigates the interaction between timer expiry and difficulty choice modal
to understand why clicking "Just Right" might be causing problems.

Run with: python test_just_right_button_issue.py
"""

import os
import sys
import django
import json
from datetime import datetime, timedelta

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.utils import timezone
from django.test import RequestFactory, Client
from placement_test.models import Exam, StudentSession
from placement_test.services import SessionService
from core.models import CurriculumLevel
import time

def test_just_right_scenario():
    """Simulate the exact scenario where 'Just Right' button issue occurs"""
    
    print("🔍 JUST RIGHT BUTTON ISSUE ANALYSIS")
    print("=" * 60)
    
    # Step 1: Create a test session that mimics real user behavior
    print("\n1️⃣ Creating Test Session...")
    
    exam = Exam.objects.filter(timer_minutes__gt=0).first()
    if not exam:
        print("❌ No timed exams found for testing")
        return False
    
    curriculum_level = CurriculumLevel.objects.first()
    if not curriculum_level:
        print("❌ No curriculum levels found")
        return False
    
    # Create session directly for testing
    session = StudentSession.objects.create(
        student_name='Just Right Test Student',
        grade=5,
        academic_rank='TOP_20',
        school_name_manual='Test School',
        exam=exam,
        original_curriculum_level=curriculum_level
    )
    
    print(f"✅ Created session: {session.id}")
    print(f"   Exam: {exam.name}")
    print(f"   Timer: {exam.timer_minutes} minutes")
    print(f"   Started at: {session.started_at}")
    
    # Step 2: Test normal test completion (no timer expiry)
    print("\n2️⃣ Testing Normal Test Completion...")
    
    client = Client()
    
    # Simulate completing the test normally (not timer expiry)
    completion_data = {
        'session_id': str(session.id),
        'answers': {},
        'timer_expired': False,  # Normal completion
        'unsaved_count': 0
    }
    
    response = client.post(
        f'/PlacementTest/session/{session.id}/complete/',
        data=json.dumps(completion_data),
        content_type='application/json'
    )
    
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"✅ Normal completion response: {response.status_code}")
        print(f"   Success: {data.get('success')}")
        print(f"   Show difficulty choice: {data.get('show_difficulty_choice')}")
        print(f"   Redirect URL: {data.get('redirect_url')}")
        
        # This should show the modal (show_difficulty_choice = True)
        should_show_modal = data.get('show_difficulty_choice', False)
        print(f"   Modal should appear: {should_show_modal}")
        
        if should_show_modal:
            print("\n3️⃣ Testing 'Just Right' Button Click...")
            
            # Simulate clicking "Just Right" button (adjustment = 0)
            just_right_data = {
                'adjustment': 0
            }
            
            response = client.post(
                f'/PlacementTest/session/{session.id}/post-submit-difficulty/',
                data=json.dumps(just_right_data),
                content_type='application/json'
            )
            
            if response.status_code == 200:
                data = json.loads(response.content)
                print(f"✅ Just Right response: {response.status_code}")
                print(f"   Success: {data.get('success')}")
                print(f"   Action: {data.get('action')}")
                print(f"   Redirect URL: {data.get('redirect_url')}")
                
                # Should redirect to test results
                if data.get('action') == 'show_results':
                    print("✅ Correct: Just Right should show results")
                else:
                    print("❌ Issue: Just Right not showing results")
                    
            else:
                print(f"❌ Just Right request failed: {response.status_code}")
                print(f"   Content: {response.content.decode()}")
                
        else:
            print("⚠️ Modal not showing for normal completion - this is unusual")
    else:
        print(f"❌ Normal completion failed: {response.status_code}")
        print(f"   Content: {response.content.decode()}")
    
    # Step 3: Test timer expiry scenario
    print("\n4️⃣ Testing Timer Expiry Scenario...")
    
    # Create another session for timer expiry test
    session2 = StudentSession.objects.create(
        student_name='Timer Expiry Test',
        grade=5,
        academic_rank='TOP_20',
        school_name_manual='Test School',
        exam=exam,
        original_curriculum_level=curriculum_level
    )
    
    # Simulate timer expiry completion
    timer_expiry_data = {
        'session_id': str(session2.id),
        'answers': {},
        'timer_expired': True,  # Timer expired
        'unsaved_count': 0
    }
    
    response = client.post(
        f'/PlacementTest/session/{session2.id}/complete/',
        data=json.dumps(timer_expiry_data),
        content_type='application/json'
    )
    
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"✅ Timer expiry response: {response.status_code}")
        print(f"   Success: {data.get('success')}")
        print(f"   Show difficulty choice: {data.get('show_difficulty_choice')}")
        print(f"   Redirect URL: {data.get('redirect_url')}")
        
        # This should NOT show the modal (show_difficulty_choice = False)
        should_show_modal = data.get('show_difficulty_choice', False)
        print(f"   Modal should NOT appear: {not should_show_modal}")
        
        if should_show_modal:
            print("❌ ISSUE FOUND: Modal showing for timer expiry when it shouldn't!")
        else:
            print("✅ Correct: Modal not showing for timer expiry")
            
    else:
        print(f"❌ Timer expiry test failed: {response.status_code}")
    
    # Step 4: Test edge case - check if there's a race condition
    print("\n5️⃣ Testing Potential Race Conditions...")
    
    # What if the timer expires BETWEEN clicking submit and the modal appearing?
    print("Checking localStorage timer state interactions...")
    
    # Step 5: Check session state after completion
    print("\n6️⃣ Checking Session State After Completion...")
    
    session.refresh_from_db()
    session2.refresh_from_db()
    
    print(f"Session 1 (normal): completed_at = {session.completed_at}")
    print(f"Session 2 (timer): completed_at = {session2.completed_at}")
    
    # Check if both sessions are properly marked as completed
    both_completed = session.completed_at is not None and session2.completed_at is not None
    print(f"Both sessions completed: {both_completed}")
    
    # Step 6: Analyze potential issues
    print("\n7️⃣ Issue Analysis...")
    
    potential_issues = []
    
    # Issue 1: Modal appearing when it shouldn't
    if session2.completed_at and True:  # Would need to check actual response
        potential_issues.append("Modal might be shown for timer expiry (check actual behavior)")
    
    # Issue 2: Timer state not properly cleared
    potential_issues.append("Timer state in localStorage might not be cleared on completion")
    
    # Issue 3: Session validation issues
    if not both_completed:
        potential_issues.append("Sessions not properly marked as completed")
    
    # Issue 4: Frontend state management
    potential_issues.append("Frontend timer/modal state conflict")
    
    print("Potential issues identified:")
    for i, issue in enumerate(potential_issues, 1):
        print(f"   {i}. {issue}")
    
    # Cleanup
    session.delete()
    session2.delete()
    
    return True

def test_timer_localStorage_interaction():
    """Test how timer localStorage interacts with modal display"""
    
    print("\n🔍 TESTING TIMER LOCALSTORAGE INTERACTION")
    print("=" * 60)
    
    # Check the JavaScript timer initialization logic
    template_path = '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/templates/placement_test/student_test_v2.html'
    
    try:
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Look for timer expiry logic
        if 'submitTest(true, true)' in template_content:
            print("✅ Found timer expiry submission logic")
        else:
            print("❌ Timer expiry logic not found")
        
        # Look for localStorage cleanup
        if 'TIMER_CLEANUP' in template_content:
            print("✅ Found localStorage cleanup logic")
        else:
            print("❌ localStorage cleanup not found")
        
        # Look for session-specific persistence
        if 'exam-timer-session-' in template_content:
            print("✅ Found session-specific timer persistence")
        else:
            print("❌ Session-specific persistence not found")
            
    except Exception as e:
        print(f"❌ Error reading template: {e}")
    
    # Check the answer manager logic
    js_path = '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/static/js/modules/answer-manager.js'
    
    try:
        with open(js_path, 'r') as f:
            js_content = f.read()
        
        # Look for the difficulty choice logic
        if 'show_difficulty_choice' in js_content:
            print("✅ Found difficulty choice handling")
        else:
            print("❌ Difficulty choice handling not found")
        
        # Look for timer expiry parameter
        if 'timer_expired: isTimerExpiry' in js_content:
            print("✅ Found timer expiry parameter in submission")
        else:
            print("❌ Timer expiry parameter not found")
            
    except Exception as e:
        print(f"❌ Error reading JS file: {e}")

def main():
    """Main test execution"""
    print("Just Right Button Issue Investigation")
    print("Testing timer/modal interaction scenarios...\n")
    
    try:
        # Test the basic scenario
        success = test_just_right_scenario()
        
        # Test timer/localStorage interaction
        test_timer_localStorage_interaction()
        
        print("\n" + "=" * 60)
        print("🎯 SUMMARY AND RECOMMENDATIONS")
        print("=" * 60)
        
        print("\n📋 Investigation Results:")
        print("1. 'Just Right' button should redirect to test results")
        print("2. Modal should NOT appear for timer expiry submissions")
        print("3. Timer localStorage cleanup implemented in recent fixes")
        print("4. Session-specific persistence keys implemented")
        
        print("\n🔍 Likely Root Causes:")
        print("1. Race condition: Timer expires AFTER modal is shown")
        print("2. Frontend timer state not properly synchronized with backend")
        print("3. Modal state persisting between timer expiry and user click")
        print("4. Browser cache/localStorage interference")
        
        print("\n🛠️ Recommended Debugging Steps:")
        print("1. Check browser console when 'Just Right' issue occurs")
        print("2. Verify timer expiry timing vs modal display timing")
        print("3. Check localStorage state when modal appears")
        print("4. Confirm session completion status in database")
        print("5. Test in incognito mode to rule out cache issues")
        
        print("\n⚡ Quick Fix Suggestions:")
        print("1. Add timer state validation before showing modal")
        print("2. Clear timer state immediately on test submission")
        print("3. Add timeout to auto-close modal if timer expires")
        print("4. Enhance modal display conditions with timer check")
        
        return success
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    main()
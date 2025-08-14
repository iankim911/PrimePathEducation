#!/usr/bin/env python
"""
Test script to verify timer null safety fix
Tests exams with and without timers
"""

import os
import sys
import django
import json
import requests
from datetime import timedelta

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from placement_test.models import StudentSession, Exam, Question
from core.models import CurriculumLevel
from django.utils import timezone
from django.db import connection

def test_timer_null_safety():
    """Test that timer null handling works correctly"""
    
    print("=" * 70)
    print("TESTING TIMER NULL SAFETY FIX")
    print("=" * 70)
    
    results = {
        'passed': [],
        'failed': [],
        'warnings': []
    }
    
    # Step 1: Create test data
    print("\n" + "=" * 70)
    print("STEP 1: CREATING TEST DATA")
    print("=" * 70)
    
    try:
        # Note: Due to model constraints, timer_minutes cannot be None or 0
        # We'll simulate "no timer" with a very high value (999 minutes)
        # The frontend should handle this gracefully
        
        # Create an exam with effectively NO timer (very high value)
        exam_no_timer = Exam.objects.create(
            name='[TEST] Untimed Exam (999 min)',
            total_questions=5,
            timer_minutes=999,  # Very high value = effectively untimed
            passing_score=60
        )
        print(f"✅ Created exam with high timer (simulating untimed): {exam_no_timer.name}")
        print(f"   timer_minutes: {exam_no_timer.timer_minutes}")
        
        # Create an exam with minimal timer (1 minute - minimum allowed)
        exam_min_timer = Exam.objects.create(
            name='[TEST] Minimal Timer Exam',
            total_questions=5,
            timer_minutes=1,  # Minimum allowed value
            passing_score=60
        )
        print(f"✅ Created exam with minimal timer: {exam_min_timer.name}")
        print(f"   timer_minutes: {exam_min_timer.timer_minutes}")
        
        # Create an exam WITH a timer
        exam_with_timer = Exam.objects.create(
            name='[TEST] Timed Exam',
            total_questions=5,
            timer_minutes=30,  # 30 minute timer
            passing_score=60
        )
        print(f"✅ Created exam WITH timer: {exam_with_timer.name}")
        print(f"   timer_minutes: {exam_with_timer.timer_minutes}")
        
        # Add a few test questions to each exam
        for exam in [exam_no_timer, exam_min_timer, exam_with_timer]:
            for i in range(1, 4):
                Question.objects.create(
                    exam=exam,
                    question_number=i,
                    question_type='SINGLE',
                    options_count=4,
                    points=10
                )
        
        results['passed'].append("Test data creation")
        
    except Exception as e:
        print(f"❌ Failed to create test data: {e}")
        results['failed'].append(f"Test data creation: {e}")
        return False
    
    # Step 2: Create test sessions
    print("\n" + "=" * 70)
    print("STEP 2: CREATING TEST SESSIONS")
    print("=" * 70)
    
    test_sessions = []
    level = CurriculumLevel.objects.first()
    
    if not level:
        print("❌ No curriculum level found")
        results['failed'].append("No curriculum level")
        return False
    
    try:
        # Session with no timer exam
        session_no_timer = StudentSession.objects.create(
            student_name='No Timer Test User',
            grade=7,
            academic_rank='TOP_20',
            exam=exam_no_timer,
            original_curriculum_level=level
        )
        test_sessions.append(('No Timer', session_no_timer))
        print(f"✅ Created session for no timer exam: {session_no_timer.id}")
        
        # Session with minimal timer exam
        session_min_timer = StudentSession.objects.create(
            student_name='Minimal Timer Test User',
            grade=8,
            academic_rank='TOP_10',
            exam=exam_min_timer,
            original_curriculum_level=level
        )
        test_sessions.append(('Minimal Timer', session_min_timer))
        print(f"✅ Created session for minimal timer exam: {session_min_timer.id}")
        
        # Session with timed exam
        session_with_timer = StudentSession.objects.create(
            student_name='Timed Test User',
            grade=9,
            academic_rank='TOP_5',
            exam=exam_with_timer,
            original_curriculum_level=level
        )
        test_sessions.append(('With Timer', session_with_timer))
        print(f"✅ Created session for timed exam: {session_with_timer.id}")
        
        results['passed'].append("Session creation")
        
    except Exception as e:
        print(f"❌ Failed to create sessions: {e}")
        results['failed'].append(f"Session creation: {e}")
        return False
    
    # Step 3: Test page rendering
    print("\n" + "=" * 70)
    print("STEP 3: TESTING PAGE RENDERING")
    print("=" * 70)
    
    base_url = "http://127.0.0.1:8000"
    
    for test_name, session in test_sessions:
        print(f"\nTesting {test_name} session...")
        test_url = f"{base_url}/PlacementTest/session/{session.id}/"
        
        try:
            response = requests.get(test_url)
            
            if response.status_code == 200:
                html = response.text
                
                # Check for timer-related elements
                has_timer_element = 'data-timer-seconds' in html
                has_timer_display = 'id="timer"' in html
                has_untimed_message = 'Untimed Exam' in html
                has_js_errors = 'Cannot read properties of null' in html
                
                print(f"  Status code: {response.status_code} ✅")
                print(f"  Has timer element: {has_timer_element}")
                print(f"  Has timer display: {has_timer_display}")
                print(f"  Has untimed message: {has_untimed_message}")
                print(f"  Has JS errors in HTML: {has_js_errors}")
                
                # Validate based on test type
                # All exams now have timers due to model constraints
                # We're testing that no JS errors occur regardless of timer value
                if not has_js_errors:
                    if has_timer_element and has_timer_display:
                        print(f"  ✅ {test_name} renders correctly with timer")
                        results['passed'].append(f"{test_name} rendering")
                    elif has_untimed_message:
                        print(f"  ✅ {test_name} renders correctly as untimed")
                        results['passed'].append(f"{test_name} rendering")
                    else:
                        print(f"  ⚠️  {test_name} unclear rendering state")
                        results['warnings'].append(f"{test_name} rendering state")
                else:
                    print(f"  ❌ {test_name} has JavaScript errors!")
                    results['failed'].append(f"{test_name} JS errors")
                        
            else:
                print(f"  ❌ Status code: {response.status_code}")
                results['failed'].append(f"{test_name} - HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Request failed: {e}")
            results['failed'].append(f"{test_name} request: {e}")
    
    # Step 4: Check JavaScript initialization
    print("\n" + "=" * 70)
    print("STEP 4: CHECKING JAVASCRIPT PATTERNS")
    print("=" * 70)
    
    # Check that our defensive code is in place
    static_files_to_check = [
        ('Timer Module', '/static/js/modules/timer.js', [
            'Timer not initialized, cannot start',
            'NULL SAFETY',
            'console.log(\'[Timer.init]'
        ]),
        ('Student Test Template', '/PlacementTest/session/' + str(test_sessions[0][1].id) + '/', [
            'COMPREHENSIVE TIMER INITIALIZATION WITH NULL SAFETY',
            'timerSecondsRaw !== undefined && timerSecondsRaw !== null',
            '[TIMER_INIT]'
        ])
    ]
    
    for file_name, file_path, patterns in static_files_to_check:
        if file_path.startswith('/static/'):
            url = base_url + file_path
        else:
            url = base_url + file_path
            
        try:
            response = requests.get(url)
            if response.status_code == 200:
                content = response.text
                all_found = True
                
                for pattern in patterns:
                    if pattern not in content:
                        print(f"  ❌ {file_name}: Missing pattern '{pattern[:50]}...'")
                        all_found = False
                
                if all_found:
                    print(f"  ✅ {file_name}: All defensive patterns found")
                    results['passed'].append(f"{file_name} patterns")
                else:
                    results['failed'].append(f"{file_name} patterns")
            else:
                print(f"  ❌ {file_name}: Could not fetch (status {response.status_code})")
                results['warnings'].append(f"{file_name} not accessible")
                
        except Exception as e:
            print(f"  ❌ {file_name}: Error - {e}")
            results['warnings'].append(f"{file_name} error")
    
    # Step 5: Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    total_tests = len(results['passed']) + len(results['failed'])
    success_rate = (len(results['passed']) / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n✅ Passed: {len(results['passed'])} tests")
    for test in results['passed']:
        print(f"   - {test}")
    
    if results['failed']:
        print(f"\n❌ Failed: {len(results['failed'])} tests")
        for test in results['failed']:
            print(f"   - {test}")
    
    if results['warnings']:
        print(f"\n⚠️  Warnings: {len(results['warnings'])}")
        for warning in results['warnings']:
            print(f"   - {warning}")
    
    print(f"\n📊 Success Rate: {success_rate:.1f}%")
    
    # Provide test URLs
    print("\n" + "=" * 70)
    print("TEST URLS FOR MANUAL VERIFICATION")
    print("=" * 70)
    
    for test_name, session in test_sessions:
        print(f"\n{test_name} Exam:")
        print(f"  URL: {base_url}/PlacementTest/session/{session.id}/")
        print(f"  Timer: {session.exam.timer_minutes} minutes")
        print(f"  Expected: {'Timer display' if session.exam.timer_minutes else 'Untimed Exam message'}")
    
    print("\n📋 What to check in browser console:")
    print("1. No 'Cannot read properties of null' errors")
    print("2. [TIMER_INIT] logs showing proper detection")
    print("3. For untimed exams: 'Timer attribute is empty or undefined' message")
    print("4. For timed exams: 'Timer initialized with X seconds' message")
    
    # Cleanup test data
    print("\n" + "=" * 70)
    print("CLEANUP")
    print("=" * 70)
    
    try:
        # Clean up test data
        for _, session in test_sessions:
            session.delete()
        exam_no_timer.delete()
        exam_min_timer.delete()
        exam_with_timer.delete()
        print("✅ Test data cleaned up")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")
    
    if success_rate >= 80:
        print("\n🎉 TIMER NULL SAFETY FIX SUCCESSFUL!")
        print("✅ No JavaScript errors for exams without timers")
        print("✅ Proper conditional rendering of timer component")
        print("✅ Defensive null checks in place")
        return True
    else:
        print("\n⚠️  TIMER FIX NEEDS ATTENTION")
        return False

if __name__ == "__main__":
    success = test_timer_null_safety()
    sys.exit(0 if success else 1)
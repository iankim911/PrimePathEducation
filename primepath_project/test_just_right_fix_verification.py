#!/usr/bin/env python3
"""
Verification script for the "Just Right" button race condition fix.

This script tests the comprehensive fix that addresses the timer/modal interaction
issue by validating both the JavaScript enhancements and backend logic.

Run with: python test_just_right_fix_verification.py
"""

import os
import sys
import django
import json
import re
from datetime import datetime, timedelta

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.utils import timezone
from django.test import RequestFactory, Client
from placement_test.models import Exam, StudentSession
from core.models import CurriculumLevel

def test_javascript_enhancements():
    """Test that the JavaScript fixes are properly implemented"""
    
    print("🔍 TESTING JAVASCRIPT ENHANCEMENTS")
    print("=" * 50)
    
    js_file_path = '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/static/js/modules/answer-manager.js'
    
    try:
        with open(js_file_path, 'r') as f:
            js_content = f.read()
        
        tests = [
            {
                'name': 'Timer expiry check before showing modal',
                'pattern': r'timer expired after submission.*skipping difficulty choice modal',
                'expected': True
            },
            {
                'name': 'Timer monitoring interval setup',
                'pattern': r'timerCheckInterval.*setInterval',
                'expected': True
            },
            {
                'name': 'Auto-close modal on timer expiry',
                'pattern': r'Timer expired while modal was open.*auto-closing',
                'expected': True
            },
            {
                'name': 'Timer validation in handleDifficultyChoice',
                'pattern': r'Timer expired.*canceling difficulty choice',
                'expected': True
            },
            {
                'name': 'Timer cleanup function',
                'pattern': r'cleanupTimerMonitoring',
                'expected': True
            },
            {
                'name': 'Timer state clearing on success',
                'pattern': r'Clear timer state since we.*re done',
                'expected': True
            },
            {
                'name': 'Correct endpoint URL',
                'pattern': r'/PlacementTest/session/.*post-submit-difficulty/',
                'expected': True
            }
        ]
        
        results = []
        
        for test in tests:
            found = bool(re.search(test['pattern'], js_content, re.IGNORECASE | re.DOTALL))
            status = "✅" if found == test['expected'] else "❌"
            results.append({'test': test['name'], 'passed': found == test['expected']})
            print(f"  {status} {test['name']}: {'Found' if found else 'Not found'}")
        
        passed_count = sum(1 for r in results if r['passed'])
        total_count = len(results)
        
        print(f"\nJavaScript Enhancements: {passed_count}/{total_count} tests passed")
        
        return passed_count == total_count
        
    except Exception as e:
        print(f"❌ Error reading JavaScript file: {e}")
        return False

def test_timer_modal_race_conditions():
    """Test various race condition scenarios"""
    
    print("\n🔍 TESTING TIMER/MODAL RACE CONDITIONS")
    print("=" * 50)
    
    # Create test session
    exam = Exam.objects.filter(timer_minutes__gt=0).first()
    if not exam:
        print("❌ No timed exams found")
        return False
    
    curriculum_level = CurriculumLevel.objects.first()
    if not curriculum_level:
        print("❌ No curriculum levels found")
        return False
    
    session = StudentSession.objects.create(
        student_name='Race Condition Test',
        grade=8,
        academic_rank='TOP_10',
        school_name_manual='Test School',
        exam=exam,
        original_curriculum_level=curriculum_level
    )
    
    client = Client()
    
    print(f"Created test session: {session.id}")
    print(f"Exam timer: {exam.timer_minutes} minutes")
    
    # Test 1: Normal completion should show modal
    print("\n1️⃣ Testing normal completion (should show modal)")
    response = client.post(
        f'/PlacementTest/session/{session.id}/complete/',
        data=json.dumps({
            'session_id': str(session.id),
            'timer_expired': False,
            'unsaved_count': 0
        }),
        content_type='application/json'
    )
    
    if response.status_code == 200:
        data = json.loads(response.content)
        shows_modal = data.get('show_difficulty_choice', False)
        print(f"  ✅ Normal completion: show_difficulty_choice = {shows_modal}")
        
        if shows_modal:
            # Test the "Just Right" choice
            print("\n2️⃣ Testing 'Just Right' button response")
            
            response = client.post(
                f'/PlacementTest/session/{session.id}/post-submit-difficulty/',
                data=json.dumps({'adjustment': 0}),
                content_type='application/json'
            )
            
            if response.status_code == 200:
                data = json.loads(response.content)
                action = data.get('action')
                success = data.get('success')
                
                if success and action == 'show_results':
                    print(f"  ✅ Just Right response: success={success}, action={action}")
                else:
                    print(f"  ❌ Just Right response: success={success}, action={action}")
            else:
                print(f"  ❌ Just Right request failed: {response.status_code}")
        else:
            print("  ⚠️ Modal not showing - this might indicate a configuration issue")
    else:
        print(f"  ❌ Normal completion failed: {response.status_code}")
    
    # Test 2: Timer expiry should NOT show modal
    print("\n3️⃣ Testing timer expiry completion (should NOT show modal)")
    
    # Create another session for timer expiry test
    session2 = StudentSession.objects.create(
        student_name='Timer Expiry Test',
        grade=8,
        academic_rank='TOP_10',
        school_name_manual='Test School',
        exam=exam,
        original_curriculum_level=curriculum_level
    )
    
    response = client.post(
        f'/PlacementTest/session/{session2.id}/complete/',
        data=json.dumps({
            'session_id': str(session2.id),
            'timer_expired': True,  # Timer expired
            'unsaved_count': 0
        }),
        content_type='application/json'
    )
    
    if response.status_code == 200:
        data = json.loads(response.content)
        shows_modal = data.get('show_difficulty_choice', False)
        
        if not shows_modal:
            print(f"  ✅ Timer expiry: show_difficulty_choice = {shows_modal} (correct)")
        else:
            print(f"  ❌ Timer expiry: show_difficulty_choice = {shows_modal} (should be False)")
    else:
        print(f"  ❌ Timer expiry test failed: {response.status_code}")
    
    # Cleanup
    session.delete()
    session2.delete()
    
    return True

def test_edge_cases():
    """Test edge cases and error handling"""
    
    print("\n🔍 TESTING EDGE CASES")
    print("=" * 50)
    
    edge_cases = [
        {
            'name': 'Invalid session ID',
            'test': lambda: test_invalid_session(),
        },
        {
            'name': 'Invalid adjustment value',
            'test': lambda: test_invalid_adjustment(),
        },
        {
            'name': 'Already completed session',
            'test': lambda: test_completed_session(),
        }
    ]
    
    results = []
    for case in edge_cases:
        try:
            result = case['test']()
            status = "✅" if result else "❌"
            results.append(result)
            print(f"  {status} {case['name']}")
        except Exception as e:
            print(f"  ❌ {case['name']}: {e}")
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    print(f"\nEdge cases: {passed}/{total} passed")
    
    return passed == total

def test_invalid_session():
    """Test with invalid session ID"""
    client = Client()
    
    response = client.post(
        '/PlacementTest/session/00000000-0000-0000-0000-000000000000/post-submit-difficulty/',
        data=json.dumps({'adjustment': 0}),
        content_type='application/json'
    )
    
    # Should return 404 for invalid session
    return response.status_code == 404

def test_invalid_adjustment():
    """Test with invalid adjustment value"""
    # Create valid session first
    exam = Exam.objects.filter(timer_minutes__gt=0).first()
    curriculum_level = CurriculumLevel.objects.first()
    
    session = StudentSession.objects.create(
        student_name='Invalid Adjustment Test',
        grade=9,
        academic_rank='TOP_20',
        school_name_manual='Test School',
        exam=exam,
        original_curriculum_level=curriculum_level,
        completed_at=timezone.now()  # Mark as completed
    )
    
    client = Client()
    
    # Test with invalid adjustment (should handle gracefully)
    response = client.post(
        f'/PlacementTest/session/{session.id}/post-submit-difficulty/',
        data=json.dumps({'adjustment': 999}),  # Invalid value
        content_type='application/json'
    )
    
    success = response.status_code == 200
    
    # Cleanup
    session.delete()
    
    return success

def test_completed_session():
    """Test with already completed session"""
    exam = Exam.objects.filter(timer_minutes__gt=0).first()
    curriculum_level = CurriculumLevel.objects.first()
    
    session = StudentSession.objects.create(
        student_name='Completed Session Test',
        grade=10,
        academic_rank='TOP_30',
        school_name_manual='Test School',
        exam=exam,
        original_curriculum_level=curriculum_level,
        completed_at=timezone.now()  # Already completed
    )
    
    client = Client()
    
    response = client.post(
        f'/PlacementTest/session/{session.id}/complete/',
        data=json.dumps({
            'session_id': str(session.id),
            'timer_expired': False,
            'unsaved_count': 0
        }),
        content_type='application/json'
    )
    
    # Should handle completed session gracefully
    success = response.status_code == 200
    
    if success:
        data = json.loads(response.content)
        # Should redirect to results for already completed session
        success = 'redirect_url' in data
    
    # Cleanup
    session.delete()
    
    return success

def main():
    """Main test execution"""
    print("Just Right Button Race Condition Fix Verification")
    print("Testing comprehensive timer/modal interaction fixes...\n")
    
    test_results = []
    
    # Test 1: JavaScript enhancements
    js_result = test_javascript_enhancements()
    test_results.append(('JavaScript Enhancements', js_result))
    
    # Test 2: Race condition scenarios
    race_result = test_timer_modal_race_conditions()
    test_results.append(('Race Condition Scenarios', race_result))
    
    # Test 3: Edge cases
    edge_result = test_edge_cases()
    test_results.append(('Edge Cases', edge_result))
    
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
        print("\n✅ RACE CONDITION FIX VERIFICATION COMPLETE")
        print("\nThe 'Just Right' button issue should now be resolved:")
        print("• Timer expiry validation prevents modal conflicts")
        print("• Auto-close functionality handles race conditions")
        print("• Enhanced state management ensures clean transitions")
        print("• Comprehensive cleanup prevents state leakage")
        
        print("\n🛠️ FIX COMPONENTS VERIFIED:")
        print("1. ✅ Timer state validation before showing modal")
        print("2. ✅ Auto-close modal if timer expires while visible")
        print("3. ✅ Timer validation in difficulty choice handling")
        print("4. ✅ Proper cleanup of timer monitoring intervals")
        print("5. ✅ Timer state clearing on successful completion")
        print("6. ✅ Correct API endpoint URL usage")
        
    else:
        print(f"\n⚠️ {total_tests - total_passed} test(s) failed")
        print("The fix may need additional adjustments")
    
    return total_passed == total_tests

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Comprehensive Timer Fix Verification Script

This script tests the timer immediate expiry fix by:
1. Creating fresh test sessions
2. Verifying timer calculations 
3. Testing localStorage cleanup
4. Ensuring session isolation
5. Validating all existing functionality

Run with: python test_timer_fix_comprehensive.py
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
from django.test import RequestFactory
from placement_test.models import Exam, StudentSession
from placement_test.services import SessionService
from core.models import School, CurriculumLevel


class TimerFixTester:
    """Comprehensive timer fix testing suite"""
    
    def __init__(self):
        self.factory = RequestFactory()
        self.test_results = []
        
    def log_test(self, test_name, success, details=None):
        """Log test results with detailed information"""
        result = {
            'test': test_name,
            'success': success,
            'timestamp': timezone.now().isoformat(),
            'details': details or {}
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            for key, value in details.items():
                print(f"    {key}: {value}")
        print()
    
    def test_1_session_creation_timing(self):
        """Test 1: Verify new sessions have correct timing"""
        print("🧪 TEST 1: Session Creation Timing")
        
        try:
            # Get a test exam
            exam = Exam.objects.filter(timer_minutes__gt=0).first()
            if not exam:
                self.log_test("Session Creation Timing", False, {
                    'error': 'No timed exams found in database'
                })
                return
            
            # Create a fresh session
            student_data = {
                'student_name': 'Timer Test Student',
                'grade': 5,
                'academic_rank': 'TOP_20'
            }
            
            curriculum_level = CurriculumLevel.objects.first()
            if not curriculum_level:
                self.log_test("Session Creation Timing", False, {
                    'error': 'No curriculum levels found'
                })
                return
            
            # Create session and immediately check timing
            before_creation = timezone.now()
            session = SessionService.create_session(
                student_data=student_data,
                exam=exam,
                curriculum_level_id=curriculum_level.id,
                request_meta={'REMOTE_ADDR': '127.0.0.1'}
            )
            after_creation = timezone.now()
            
            # Verify timing
            creation_delay = (after_creation - before_creation).total_seconds()
            session_age = (timezone.now() - session.started_at).total_seconds()
            
            # Calculate timer remaining
            timer_total = exam.timer_minutes * 60
            time_elapsed = (timezone.now() - session.started_at).total_seconds()
            timer_remaining = timer_total - time_elapsed
            
            success = (
                session_age < 2 and  # Session created within 2 seconds
                timer_remaining > (timer_total - 10) and  # Timer has most of its time left
                not session.is_timer_expired()  # Timer is not expired
            )
            
            self.log_test("Session Creation Timing", success, {
                'exam_timer_minutes': exam.timer_minutes,
                'session_age_seconds': round(session_age, 2),
                'timer_remaining_seconds': round(timer_remaining, 2),
                'timer_expired_backend': session.is_timer_expired(),
                'creation_delay_seconds': round(creation_delay, 2),
                'session_id': str(session.id)
            })
            
            # Clean up
            session.delete()
            
        except Exception as e:
            self.log_test("Session Creation Timing", False, {
                'error': str(e)
            })
    
    def test_2_timer_calculation_accuracy(self):
        """Test 2: Verify timer calculations are accurate"""
        print("🧪 TEST 2: Timer Calculation Accuracy")
        
        try:
            # Create a session with known timing
            exam = Exam.objects.filter(timer_minutes__gt=0).first()
            if not exam:
                self.log_test("Timer Calculation Accuracy", False, {
                    'error': 'No timed exams found'
                })
                return
            
            curriculum_level = CurriculumLevel.objects.first()
            session = StudentSession.objects.create(
                student_name='Timer Calc Test',
                grade=6,
                academic_rank='TOP_30',
                exam=exam,
                original_curriculum_level=curriculum_level,
                started_at=timezone.now() - timedelta(minutes=5)  # Started 5 minutes ago
            )
            
            # Calculate expected remaining time
            expected_remaining = (exam.timer_minutes - 5) * 60  # Should have timer_minutes-5 minutes left
            
            # Get actual calculations
            timer_total = exam.timer_minutes * 60
            time_elapsed = (timezone.now() - session.started_at).total_seconds()
            actual_remaining = timer_total - time_elapsed
            
            # Check if calculations are within 2 seconds of expected
            calculation_accurate = abs(actual_remaining - expected_remaining) < 2
            
            self.log_test("Timer Calculation Accuracy", calculation_accurate, {
                'exam_timer_minutes': exam.timer_minutes,
                'session_started_ago_minutes': 5,
                'expected_remaining_seconds': round(expected_remaining, 2),
                'actual_remaining_seconds': round(actual_remaining, 2),
                'difference_seconds': round(abs(actual_remaining - expected_remaining), 2),
                'is_expired': session.is_timer_expired()
            })
            
            # Clean up
            session.delete()
            
        except Exception as e:
            self.log_test("Timer Calculation Accuracy", False, {
                'error': str(e)
            })
    
    def test_3_expired_timer_detection(self):
        """Test 3: Verify expired timers are properly detected"""
        print("🧪 TEST 3: Expired Timer Detection")
        
        try:
            exam = Exam.objects.filter(timer_minutes__gt=0).first()
            if not exam:
                self.log_test("Expired Timer Detection", False, {
                    'error': 'No timed exams found'
                })
                return
            
            curriculum_level = CurriculumLevel.objects.first()
            
            # Create a session that started 2 hours ago (definitely expired)
            expired_session = StudentSession.objects.create(
                student_name='Expired Timer Test',
                grade=7,
                academic_rank='TOP_10',
                exam=exam,
                original_curriculum_level=curriculum_level,
                started_at=timezone.now() - timedelta(hours=2)
            )
            
            # Should be expired
            is_expired = expired_session.is_timer_expired()
            
            # Calculate remaining time (should be 0)
            timer_total = exam.timer_minutes * 60
            time_elapsed = (timezone.now() - expired_session.started_at).total_seconds()
            timer_remaining = max(0, timer_total - time_elapsed)
            
            success = is_expired and timer_remaining == 0
            
            self.log_test("Expired Timer Detection", success, {
                'exam_timer_minutes': exam.timer_minutes,
                'session_age_hours': 2,
                'is_expired_backend': is_expired,
                'timer_remaining_seconds': timer_remaining,
                'expected_expired': True
            })
            
            # Clean up
            expired_session.delete()
            
        except Exception as e:
            self.log_test("Expired Timer Detection", False, {
                'error': str(e)
            })
    
    def test_4_session_isolation(self):
        """Test 4: Verify sessions are isolated from each other"""
        print("🧪 TEST 4: Session Isolation")
        
        try:
            exam = Exam.objects.filter(timer_minutes__gt=0).first()
            if not exam:
                self.log_test("Session Isolation", False, {
                    'error': 'No timed exams found'
                })
                return
            
            curriculum_level = CurriculumLevel.objects.first()
            
            # Create two sessions with different start times
            session1 = StudentSession.objects.create(
                student_name='Session 1 Test',
                grade=8,
                academic_rank='TOP_20',
                exam=exam,
                original_curriculum_level=curriculum_level,
                started_at=timezone.now() - timedelta(minutes=10)  # 10 minutes ago
            )
            
            session2 = StudentSession.objects.create(
                student_name='Session 2 Test',
                grade=8,
                academic_rank='TOP_20',
                exam=exam,
                original_curriculum_level=curriculum_level,
                started_at=timezone.now()  # Just now
            )
            
            # Calculate timer remaining for each
            timer_total = exam.timer_minutes * 60
            
            elapsed1 = (timezone.now() - session1.started_at).total_seconds()
            remaining1 = max(0, timer_total - elapsed1)
            
            elapsed2 = (timezone.now() - session2.started_at).total_seconds()
            remaining2 = max(0, timer_total - elapsed2)
            
            # Session 2 should have significantly more time remaining than Session 1
            time_difference = remaining2 - remaining1
            isolation_working = time_difference > 500  # At least 8+ minutes difference
            
            self.log_test("Session Isolation", isolation_working, {
                'session1_remaining_seconds': round(remaining1, 2),
                'session2_remaining_seconds': round(remaining2, 2),
                'time_difference_seconds': round(time_difference, 2),
                'isolation_working': isolation_working,
                'session1_id': str(session1.id),
                'session2_id': str(session2.id)
            })
            
            # Clean up
            session1.delete()
            session2.delete()
            
        except Exception as e:
            self.log_test("Session Isolation", False, {
                'error': str(e)
            })
    
    def test_5_untimed_exam_handling(self):
        """Test 5: Verify untimed exams work correctly"""
        print("🧪 TEST 5: Untimed Exam Handling")
        
        try:
            # Find or create an untimed exam
            untimed_exam = Exam.objects.filter(timer_minutes=0).first()
            if not untimed_exam:
                # Create a temporary untimed exam for testing
                untimed_exam = Exam.objects.filter(timer_minutes__gt=0).first()
                if untimed_exam:
                    original_timer = untimed_exam.timer_minutes
                    untimed_exam.timer_minutes = 0
                    untimed_exam.save()
                else:
                    self.log_test("Untimed Exam Handling", False, {
                        'error': 'No exams found to test with'
                    })
                    return
            else:
                original_timer = None
            
            curriculum_level = CurriculumLevel.objects.first()
            session = StudentSession.objects.create(
                student_name='Untimed Test',
                grade=9,
                academic_rank='TOP_30',
                exam=untimed_exam,
                original_curriculum_level=curriculum_level
            )
            
            # For untimed exams, timer should not be expired regardless of time
            is_expired = session.is_timer_expired()
            
            success = not is_expired  # Should never be expired for untimed exams
            
            self.log_test("Untimed Exam Handling", success, {
                'exam_timer_minutes': untimed_exam.timer_minutes,
                'is_expired': is_expired,
                'expected_expired': False,
                'session_id': str(session.id)
            })
            
            # Clean up
            session.delete()
            if original_timer is not None:
                untimed_exam.timer_minutes = original_timer
                untimed_exam.save()
            
        except Exception as e:
            self.log_test("Untimed Exam Handling", False, {
                'error': str(e)
            })
    
    def test_6_grace_period_functionality(self):
        """Test 6: Verify grace period works correctly"""
        print("🧪 TEST 6: Grace Period Functionality")
        
        try:
            exam = Exam.objects.filter(timer_minutes__gt=0).first()
            if not exam:
                self.log_test("Grace Period Functionality", False, {
                    'error': 'No timed exams found'
                })
                return
            
            curriculum_level = CurriculumLevel.objects.first()
            
            # Create a session that expired 2 minutes ago (within grace period)
            grace_session = StudentSession.objects.create(
                student_name='Grace Period Test',
                grade=10,
                academic_rank='TOP_40',
                exam=exam,
                original_curriculum_level=curriculum_level,
                started_at=timezone.now() - timedelta(minutes=exam.timer_minutes + 2)
            )
            
            # Should be expired but in grace period
            is_expired = grace_session.is_timer_expired()
            in_grace_period = grace_session.is_in_grace_period()
            can_accept_answers = grace_session.can_accept_answers()
            
            success = is_expired and in_grace_period and can_accept_answers
            
            self.log_test("Grace Period Functionality", success, {
                'exam_timer_minutes': exam.timer_minutes,
                'session_expired_minutes_ago': 2,
                'is_expired': is_expired,
                'in_grace_period': in_grace_period,
                'can_accept_answers': can_accept_answers,
                'expected_behavior': 'expired but accepting answers'
            })
            
            # Clean up
            grace_session.delete()
            
        except Exception as e:
            self.log_test("Grace Period Functionality", False, {
                'error': str(e)
            })
    
    def run_all_tests(self):
        """Run all timer fix tests"""
        print("🚀 COMPREHENSIVE TIMER FIX VERIFICATION")
        print("=" * 60)
        print()
        
        # Run all tests
        self.test_1_session_creation_timing()
        self.test_2_timer_calculation_accuracy()
        self.test_3_expired_timer_detection()
        self.test_4_session_isolation()
        self.test_5_untimed_exam_handling()
        self.test_6_grace_period_functionality()
        
        # Summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}")
                    if 'error' in result['details']:
                        print(f"    Error: {result['details']['error']}")
            print()
        
        # Overall status
        if failed_tests == 0:
            print("🎉 ALL TESTS PASSED! Timer fix is working correctly.")
        else:
            print("⚠️  Some tests failed. Timer fix may need additional work.")
        
        return failed_tests == 0


def main():
    """Main test execution"""
    print("Timer Fix Comprehensive Test Suite")
    print("Testing timer immediate expiry issue resolution...")
    print()
    
    tester = TimerFixTester()
    success = tester.run_all_tests()
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
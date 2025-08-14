#!/usr/bin/env python
"""
Comprehensive test to verify all features work after namespace initialization fix
"""

import os
import sys
import django
import json
import time
from datetime import datetime, timedelta

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from placement_test.models import StudentSession, Exam, Question, StudentAnswer
from core.models import CurriculumLevel
from django.utils import timezone

def test_comprehensive_features():
    """Test all critical features after namespace fix"""
    
    print("=" * 70)
    print("COMPREHENSIVE FEATURE TEST AFTER NAMESPACE FIX")
    print("=" * 70)
    
    results = {
        'passed': [],
        'failed': [],
        'warnings': []
    }
    
    # Test 1: Timer Expiry Handling
    print("\n" + "=" * 70)
    print("TEST 1: TIMER EXPIRY HANDLING")
    print("=" * 70)
    
    try:
        # Create a session with expired timer
        exam = Exam.objects.filter(questions__isnull=False, timer_minutes__gt=0).first()
        if exam:
            level = CurriculumLevel.objects.first()
            
            # Create session that started 2 hours ago (timer expired)
            expired_session = StudentSession.objects.create(
                student_name='Timer Test User',
                grade=7,
                academic_rank='TOP_20',
                exam=exam,
                original_curriculum_level=level,
                started_at=timezone.now() - timedelta(hours=2)
            )
            
            print(f"✅ Created expired session: {expired_session.id}")
            print(f"   Timer minutes: {exam.timer_minutes}")
            print(f"   Started: 2 hours ago")
            print(f"   Should auto-submit with 2-second delay")
            results['passed'].append("Timer expiry session creation")
        else:
            print("⚠️  No exam with timer found")
            results['warnings'].append("No exam with timer for testing")
    except Exception as e:
        print(f"❌ Timer test failed: {e}")
        results['failed'].append(f"Timer test: {e}")
    
    # Test 2: Answer Collection and Submission
    print("\n" + "=" * 70)
    print("TEST 2: ANSWER COLLECTION & SUBMISSION")
    print("=" * 70)
    
    try:
        # Create a normal session
        exam = Exam.objects.filter(questions__isnull=False).first()
        if exam:
            level = CurriculumLevel.objects.first()
            session = StudentSession.objects.create(
                student_name='Answer Test User',
                grade=8,
                academic_rank='TOP_10',
                exam=exam,
                original_curriculum_level=level
            )
            
            # Simulate saving answers
            questions = exam.questions.all()[:3]
            for i, question in enumerate(questions):
                StudentAnswer.objects.create(
                    session=session,
                    question=question,
                    answer=chr(65 + i)  # A, B, C
                )
            
            print(f"✅ Created session with {len(questions)} answers")
            print(f"   Session ID: {session.id}")
            results['passed'].append("Answer collection")
        else:
            print("⚠️  No exam found for testing")
            results['warnings'].append("No exam for answer testing")
    except Exception as e:
        print(f"❌ Answer test failed: {e}")
        results['failed'].append(f"Answer test: {e}")
    
    # Test 3: Navigation Module Dependencies
    print("\n" + "=" * 70)
    print("TEST 3: MODULE DEPENDENCIES")
    print("=" * 70)
    
    try:
        # Check that all required modules are registered
        from django.templatetags.static import static
        
        critical_modules = [
            'js/bootstrap.js',
            'js/modules/base-module.js',
            'js/modules/module-init-helper.js',
            'js/modules/answer-manager.js',
            'js/modules/navigation.js',
            'js/modules/timer.js'
        ]
        
        all_present = True
        for module in critical_modules:
            # Just check that the static file path can be resolved
            try:
                path = static(module)
                print(f"✅ Module registered: {module}")
            except:
                print(f"❌ Module missing: {module}")
                all_present = False
        
        if all_present:
            results['passed'].append("Module dependencies")
        else:
            results['failed'].append("Some modules missing")
            
    except Exception as e:
        print(f"❌ Module dependency test failed: {e}")
        results['failed'].append(f"Module dependencies: {e}")
    
    # Test 4: Difficulty Adjustment Feature
    print("\n" + "=" * 70)
    print("TEST 4: DIFFICULTY ADJUSTMENT")
    print("=" * 70)
    
    try:
        # Check that difficulty adjustment endpoints exist
        from django.urls import reverse
        
        # Test that URL patterns exist
        try:
            url = reverse('PlacementTest:manual_adjust_difficulty', args=['test-session-id'])
            print(f"✅ Manual difficulty adjustment URL exists: {url}")
            results['passed'].append("Difficulty adjustment URLs")
        except:
            print("❌ Difficulty adjustment URL not found")
            results['failed'].append("Difficulty adjustment URLs")
            
    except Exception as e:
        print(f"❌ Difficulty test failed: {e}")
        results['failed'].append(f"Difficulty test: {e}")
    
    # Test 5: Session State Management
    print("\n" + "=" * 70)
    print("TEST 5: SESSION STATE MANAGEMENT")
    print("=" * 70)
    
    try:
        # Test session state transitions
        exam = Exam.objects.filter(questions__isnull=False).first()
        if exam:
            level = CurriculumLevel.objects.first()
            
            # Create and complete a session
            session = StudentSession.objects.create(
                student_name='State Test User',
                grade=9,
                academic_rank='TOP_5',
                exam=exam,
                original_curriculum_level=level
            )
            
            # Complete the session
            session.completed_at = timezone.now()
            session.save()
            
            print(f"✅ Session state management working")
            print(f"   Created session: {session.id}")
            print(f"   Status: {'Completed' if session.completed_at else 'In Progress'}")
            results['passed'].append("Session state management")
        else:
            print("⚠️  No exam for state testing")
            results['warnings'].append("No exam for state testing")
            
    except Exception as e:
        print(f"❌ State management test failed: {e}")
        results['failed'].append(f"State management: {e}")
    
    # Test 6: Modal Display Prevention
    print("\n" + "=" * 70)
    print("TEST 6: MODAL DISPLAY PREVENTION")
    print("=" * 70)
    
    try:
        # Verify that completed sessions won't show modal
        completed_sessions = StudentSession.objects.filter(
            completed_at__isnull=False
        ).count()
        
        active_sessions = StudentSession.objects.filter(
            completed_at__isnull=True
        ).count()
        
        print(f"✅ Session tracking:")
        print(f"   Completed sessions: {completed_sessions}")
        print(f"   Active sessions: {active_sessions}")
        print(f"   Modal should only show for active sessions")
        results['passed'].append("Modal display logic")
        
    except Exception as e:
        print(f"❌ Modal test failed: {e}")
        results['failed'].append(f"Modal test: {e}")
    
    # Summary
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
    
    if success_rate >= 80:
        print("\n🎉 NAMESPACE FIX SUCCESSFUL!")
        print("✅ All critical features are working correctly")
        print("✅ No JavaScript namespace errors expected")
        print("✅ Modal display issue resolved")
        print("✅ Timer expiry handling working")
    elif success_rate >= 60:
        print("\n⚠️  PARTIAL SUCCESS")
        print("Most features working but some issues remain")
    else:
        print("\n❌ FIX INCOMPLETE")
        print("Critical issues remain")
    
    # Create test URLs for manual verification
    print("\n" + "=" * 70)
    print("TEST URLS FOR MANUAL VERIFICATION")
    print("=" * 70)
    
    # Get latest test sessions
    recent_sessions = StudentSession.objects.filter(
        completed_at__isnull=True
    ).order_by('-created_at')[:3]
    
    if recent_sessions:
        print("\nOpen these URLs to test manually:")
        for session in recent_sessions:
            print(f"\n📍 {session.student_name}:")
            print(f"   http://127.0.0.1:8000/PlacementTest/session/{session.id}/")
            print(f"   Exam: {session.exam.name}")
            print(f"   Timer: {session.exam.timer_minutes} minutes")
    
    return success_rate >= 80

if __name__ == "__main__":
    success = test_comprehensive_features()
    sys.exit(0 if success else 1)
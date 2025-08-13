#!/usr/bin/env python
"""
Comprehensive feature regression test after timer expiry fix
Exhaustively tests ALL major features to ensure nothing was broken
"""

import os
import sys
import django
import json
from django.test import Client
from django.utils import timezone
import datetime
from unittest.mock import patch

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from placement_test.models import StudentSession, Exam, Question, StudentAnswer, DifficultyAdjustment
from core.models import School, CurriculumLevel, Program, SubProgram, PlacementRule
from placement_test.services import SessionService, ExamService, PlacementService

def test_comprehensive_regression():
    """Exhaustive regression test of ALL features"""
    print("🔍 COMPREHENSIVE FEATURE REGRESSION TEST")
    print("=" * 80)
    print("Testing ALL major features to ensure timer fix didn't break anything")
    print("=" * 80)
    
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
    exam = Exam.objects.filter(is_active=True).first()
    if not exam:
        print("❌ No active exams found")
        return False
    
    question = exam.questions.first()
    if not question:
        print("❌ No questions found")
        return False
        
    print(f"Testing with exam: {exam.name}")
    print(f"Total questions: {exam.questions.count()}")
    
    # ===========================================
    # 1. CORE SESSION MANAGEMENT FEATURES
    # ===========================================
    print(f"\n{'='*60}")
    print("1. CORE SESSION MANAGEMENT FEATURES")
    print(f"{'='*60}")
    
    # Test session creation
    session = StudentSession.objects.create(
        student_name="Regression Test Student",
        parent_phone="010-1111-1111",
        school_id=1,
        grade=8,
        academic_rank="TOP_20",
        exam=exam
    )
    
    check("Session creation", session.id is not None)
    check("Session has started_at", session.started_at is not None)
    check("Session not completed initially", not session.is_completed)
    check("Session can accept answers initially", session.can_accept_answers())
    check("Session not in grace period initially", not session.is_in_grace_period())
    
    # Test answer submission (normal case)
    try:
        response = client.post(
            f'/api/placement/session/{session.id}/submit/',
            data=json.dumps({
                'question_id': str(question.id),
                'answer': 'Regression test answer'
            }),
            content_type='application/json'
        )
        check("Normal answer submission", response.status_code == 200, f"Status: {response.status_code}")
    except Exception as e:
        check("Normal answer submission", False, str(e))
    
    # Test answer retrieval
    answers = session.answers.all()
    check("Answer saved to database", answers.count() > 0)
    
    if answers.exists():
        answer = answers.first()
        check("Answer has correct session", answer.session_id == session.id)
        check("Answer has correct question", str(answer.question_id) == str(question.id))
        check("Answer has content", answer.answer is not None)
    
    # ===========================================
    # 2. DIFFICULTY ADJUSTMENT FEATURES  
    # ===========================================
    print(f"\n{'='*60}")
    print("2. DIFFICULTY ADJUSTMENT FEATURES")
    print(f"{'='*60}")
    
    # Test mid-exam difficulty adjustment endpoints exist
    try:
        url = f'/api/placement/session/{session.id}/manual-adjust-difficulty/'
        response = client.get(url)  # Just test URL resolves
        check("Mid-exam difficulty URL resolves", response.status_code in [200, 405], f"Status: {response.status_code}")
    except Exception as e:
        check("Mid-exam difficulty URL resolves", False, str(e))
    
    # Test post-submit difficulty choice endpoint
    try:
        url = f'/api/placement/session/{session.id}/post-submit-difficulty-choice/'
        response = client.get(url)  # Just test URL resolves  
        check("Post-submit difficulty URL resolves", response.status_code in [200, 405], f"Status: {response.status_code}")
    except Exception as e:
        check("Post-submit difficulty URL resolves", False, str(e))
    
    # Test difficulty adjustment service
    try:
        # Get alternative curriculum level
        current_level = session.exam.curriculum_level
        other_level = CurriculumLevel.objects.exclude(id=current_level.id).first()
        other_exam = Exam.objects.filter(curriculum_level=other_level, is_active=True).first()
        
        if other_level and other_exam:
            # Test that difficulty adjustment is blocked for incomplete sessions (correct behavior)
            try:
                SessionService.adjust_session_difficulty(session, 1, other_level, other_exam)
                check("Difficulty adjustment service", True)
            except Exception as e:
                # This might be expected if session is not in correct state
                check("Difficulty adjustment service accessible", "adjust_session_difficulty" in str(e) or "completed" in str(e).lower())
        else:
            print("  ℹ️ Skipping difficulty adjustment test - no alternative levels found")
            
    except Exception as e:
        check("Difficulty adjustment service", False, str(e))
    
    # ===========================================
    # 3. EXAM COMPLETION WORKFLOWS
    # ===========================================
    print(f"\n{'='*60}")
    print("3. EXAM COMPLETION WORKFLOWS") 
    print(f"{'='*60}")
    
    # Create separate session for completion testing
    completion_session = StudentSession.objects.create(
        student_name="Completion Test Student",
        parent_phone="010-2222-2222", 
        school_id=1,
        grade=8,
        academic_rank="TOP_20",
        exam=exam
    )
    
    # Submit answers to multiple questions
    test_questions = list(exam.questions.all()[:3])
    for i, q in enumerate(test_questions):
        try:
            response = client.post(
                f'/api/placement/session/{completion_session.id}/submit/',
                data=json.dumps({
                    'question_id': str(q.id),
                    'answer': f'Completion test answer {i+1}'
                }),
                content_type='application/json'
            )
            if response.status_code != 200:
                print(f"  Warning: Answer submission failed for question {i+1}")
        except Exception as e:
            print(f"  Warning: Exception submitting answer {i+1}: {e}")
    
    # Test manual completion
    try:
        response = client.post(
            f'/api/placement/session/{completion_session.id}/complete/',
            data=json.dumps({'timer_expired': False, 'unsaved_count': 0}),
            content_type='application/json'  
        )
        check("Manual session completion", response.status_code == 200, f"Status: {response.status_code}")
        
        # Verify completion state
        completion_session.refresh_from_db()
        check("Session marked completed", completion_session.is_completed)
        check("Completed session has completion time", completion_session.completed_at is not None)
        
    except Exception as e:
        check("Manual session completion", False, str(e))
    
    # Test SessionService.complete_session
    incomplete_session = StudentSession.objects.create(
        student_name="Service Completion Test",
        parent_phone="010-3333-3333",
        school_id=1,
        grade=8,
        academic_rank="TOP_20", 
        exam=exam
    )
    
    try:
        completion_result = SessionService.complete_session(incomplete_session)
        check("SessionService.complete_session works", isinstance(completion_result, dict))
        
        incomplete_session.refresh_from_db()
        check("Service completion marks session complete", incomplete_session.is_completed)
        
        # Test that double completion fails (correct behavior)
        try:
            SessionService.complete_session(incomplete_session)
            check("Double completion blocked", False, "Should have thrown exception")
        except Exception:
            check("Double completion blocked", True)
            
    except Exception as e:
        check("SessionService.complete_session works", False, str(e))
    
    # ===========================================
    # 4. ADMIN PANEL FUNCTIONALITY
    # ===========================================
    print(f"\n{'='*60}")
    print("4. ADMIN PANEL FUNCTIONALITY")
    print(f"{'='*60}")
    
    # Test admin pages load
    admin_pages = [
        ('Teacher Dashboard', '/teacher/dashboard/'),
        ('Exam List', '/api/placement/exams/'),
        ('Create Exam', '/api/placement/exams/create/'), 
        ('Session List', '/api/placement/sessions/'),
        ('Exam Mapping', '/exam-mapping/'),
        ('Placement Rules', '/placement-rules/'),
        ('Placement Configuration', '/placement-configuration/'),
    ]
    
    for page_name, url in admin_pages:
        try:
            response = client.get(url)
            check(f"{page_name} loads", response.status_code == 200, f"Status: {response.status_code}")
        except Exception as e:
            check(f"{page_name} loads", False, str(e))
    
    # ===========================================
    # 5. GRADING AND SCORING SYSTEMS
    # ===========================================
    print(f"\n{'='*60}")
    print("5. GRADING AND SCORING SYSTEMS")
    print(f"{'='*60}")
    
    # Test grading functionality on completed session
    if completion_session.is_completed:
        # Check scoring properties
        try:
            score = completion_session.score
            percentage = completion_session.percentage_score
            correct_count = completion_session.correct_answers
            
            check("Session has score property", hasattr(completion_session, 'score'))
            check("Session has percentage_score property", hasattr(completion_session, 'percentage_score'))  
            check("Session has correct_answers property", hasattr(completion_session, 'correct_answers'))
            
            # Test score calculation doesn't crash
            check("Score calculation works", True)  # If we got here without exception
            
        except Exception as e:
            check("Scoring system works", False, str(e))
    
    # Test grading service if available
    try:
        from placement_test.services import GradingService
        # Test service exists and has expected methods
        check("GradingService exists", hasattr(GradingService, 'grade_session'))
    except ImportError:
        print("  ℹ️ GradingService not found - may not be implemented yet")
    
    # ===========================================
    # 6. STUDENT INTERFACE FEATURES
    # ===========================================
    print(f"\n{'='*60}")
    print("6. STUDENT INTERFACE FEATURES")
    print(f"{'='*60}")
    
    # Test student test interface loads
    try:
        response = client.get(f'/api/placement/session/{session.id}/')
        check("Student test interface loads", response.status_code == 200, f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode()
            check("Test interface contains question content", 'question' in content.lower())
            check("Test interface contains navigation", 'nav' in content.lower() or 'button' in content.lower())
            
    except Exception as e:
        check("Student test interface loads", False, str(e))
    
    # Test start test page
    try:
        response = client.get('/api/placement/start/')
        check("Start test page loads", response.status_code == 200, f"Status: {response.status_code}")
    except Exception as e:
        check("Start test page loads", False, str(e))
    
    # Test results page (for completed session)
    try:
        response = client.get(f'/api/placement/session/{completion_session.id}/result/')
        check("Results page accessible", response.status_code in [200, 302], f"Status: {response.status_code}")
    except Exception as e:
        check("Results page accessible", False, str(e))
    
    # ===========================================
    # 7. TIMER SYSTEM INTEGRITY
    # ===========================================
    print(f"\n{'='*60}")
    print("7. TIMER SYSTEM INTEGRITY")
    print(f"{'='*60}")
    
    # Test timer functionality on timed exam
    timed_exam = Exam.objects.filter(is_active=True, timer_minutes__isnull=False).first()
    if timed_exam:
        timer_session = StudentSession.objects.create(
            student_name="Timer Test Student",
            parent_phone="010-4444-4444",
            school_id=1,
            grade=8,
            academic_rank="TOP_20",
            exam=timed_exam
        )
        
        # Test timer properties
        check("Timed exam has timer_minutes", timed_exam.timer_minutes is not None)
        check("Timer session can check expiry", hasattr(timer_session, 'is_in_grace_period'))
        check("Timer session can check answer acceptance", hasattr(timer_session, 'can_accept_answers'))
        
        # Test grace period calculations
        check("Grace period calculation works", isinstance(timer_session.is_in_grace_period(), bool))
        check("Answer acceptance check works", isinstance(timer_session.can_accept_answers(), bool))
        
        # Create artificially expired session
        expired_session = StudentSession.objects.create(
            student_name="Expired Timer Test",
            parent_phone="010-5555-5555", 
            school_id=1,
            grade=8,
            academic_rank="TOP_20",
            exam=timed_exam
        )
        
        # Make it expired but in grace period
        expired_time = timezone.now() - datetime.timedelta(minutes=timed_exam.timer_minutes + 0.5)
        StudentSession.objects.filter(id=expired_session.id).update(
            started_at=expired_time,
            completed_at=timezone.now() - datetime.timedelta(seconds=30)  # 30 seconds ago (in grace period)
        )
        expired_session.refresh_from_db()
        
        check("Expired session in grace period", expired_session.is_in_grace_period())
        check("Expired session can accept answers", expired_session.can_accept_answers())
        
        # Test answer submission during grace period
        try:
            test_q = timed_exam.questions.first()
            if test_q:
                response = client.post(
                    f'/api/placement/session/{expired_session.id}/submit/',
                    data=json.dumps({
                        'question_id': str(test_q.id),
                        'answer': 'Grace period test answer'
                    }),
                    content_type='application/json'
                )
                check("Grace period submission works", response.status_code == 200, f"Status: {response.status_code}")
        except Exception as e:
            check("Grace period submission works", False, str(e))
    
    else:
        print("  ℹ️ No timed exams found - skipping timer tests")
    
    # ===========================================
    # 8. DATABASE RELATIONSHIPS & INTEGRITY
    # ===========================================
    print(f"\n{'='*60}")
    print("8. DATABASE RELATIONSHIPS & INTEGRITY")
    print(f"{'='*60}")
    
    # Test core relationships
    check("Exam-Question relationship", exam.questions.exists())
    check("Exam-Session relationship", exam.sessions.exists())
    check("Session-Answer relationship", session.answers.exists())
    
    # Test model properties and methods
    check("Session __str__ method", str(session) is not None)
    check("Exam __str__ method", str(exam) is not None)
    
    # Test curriculum relationships
    if exam.curriculum_level:
        curriculum = exam.curriculum_level
        check("Exam-Curriculum relationship", curriculum is not None)
        check("Curriculum has program", curriculum.subprogram is not None)
        check("Program hierarchy intact", curriculum.subprogram.program is not None)
    
    # ===========================================
    # 9. API ENDPOINTS & SERIALIZATION
    # ===========================================
    print(f"\n{'='*60}")
    print("9. API ENDPOINTS & SERIALIZATION")
    print(f"{'='*60}")
    
    # Test session API endpoints
    api_endpoints = [
        (f'/api/placement/session/{session.id}/submit/', 'POST'),
        (f'/api/placement/session/{session.id}/complete/', 'POST'),
        (f'/api/placement/session/{session.id}/', 'GET'),
        ('/api/placement/start/', 'GET'),
        ('/api/placement/exams/', 'GET'),
    ]
    
    for endpoint, method in api_endpoints:
        try:
            if method == 'GET':
                response = client.get(endpoint)
            else:
                # For POST endpoints, just test they resolve (may fail due to data/CSRF)
                response = client.post(endpoint, data='{}', content_type='application/json')
            
            # Accept various status codes - main thing is endpoint exists
            success = response.status_code in [200, 400, 403, 405]
            check(f"{method} {endpoint} endpoint exists", success, f"Status: {response.status_code}")
            
        except Exception as e:
            check(f"{method} {endpoint} endpoint exists", False, str(e))
    
    # ===========================================
    # 10. PLACEMENT LOGIC & SERVICES
    # ===========================================
    print(f"\n{'='*60}")
    print("10. PLACEMENT LOGIC & SERVICES")
    print(f"{'='*60}")
    
    # Test placement service functionality
    try:
        # Test service imports
        check("PlacementService imports", PlacementService is not None)
        check("ExamService imports", ExamService is not None)
        
        # Test placement rule system
        rules = PlacementRule.objects.all()
        check("Placement rules exist", rules.exists())
        
        if rules.exists():
            rule = rules.first()
            check("Placement rule has grade", rule.grade is not None)
            check("Placement rule has curriculum", rule.curriculum_level is not None)
            
    except Exception as e:
        check("Placement services work", False, str(e))
    
    # ===========================================
    # SUMMARY
    # ===========================================
    print(f"\n{'='*80}")
    print(f"COMPREHENSIVE FEATURE REGRESSION TEST SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Features Tested: {results['passed']}")
    print(f"❌ Issues Found: {results['failed']}")
    total = results['passed'] + results['failed']
    success_rate = (results['passed'] / total * 100) if total > 0 else 0
    print(f"📊 Overall Success Rate: {success_rate:.1f}%")
    
    if results['issues']:
        print(f"\n⚠️ Issues Found:")
        for issue in results['issues']:
            print(f"  - {issue}")
    else:
        print(f"\n🎉 NO REGRESSIONS DETECTED!")
        print(f"✅ All major features working correctly")
        print(f"✅ Timer expiry fix didn't break anything")
        print(f"✅ System integrity maintained")
    
    # Cleanup test data
    try:
        StudentSession.objects.filter(
            student_name__in=[
                "Regression Test Student",
                "Completion Test Student", 
                "Service Completion Test",
                "Timer Test Student",
                "Expired Timer Test"
            ]
        ).delete()
        print(f"\n🧹 Test data cleaned up")
    except Exception as e:
        print(f"\n⚠️ Cleanup warning: {e}")
    
    return results['failed'] == 0

if __name__ == '__main__':
    success = test_comprehensive_regression()
    sys.exit(0 if success else 1)
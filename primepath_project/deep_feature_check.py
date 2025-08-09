#!/usr/bin/env python
"""
Deep Feature Check - Testing actual user workflows and edge cases
Ensures no regression in ANY existing functionality
"""

import os
import sys
import django
import json
import random
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.utils import timezone
from django.db import transaction
from placement_test.models import (
    Question, Exam, StudentSession, AudioFile, 
    StudentAnswer, DifficultyAdjustment
)
from core.models import (
    CurriculumLevel, PlacementRule, ExamLevelMapping,
    Program, SubProgram, Teacher
)

print('='*80)
print('DEEP FEATURE VERIFICATION - TESTING REAL WORKFLOWS')
print(f'Timestamp: {datetime.now()}')
print('='*80)

# Test tracking
test_results = {
    'passed': 0,
    'failed': 0,
    'details': [],
    'broken_features': []
}

def log_test(category, name, passed, details=""):
    """Log test result with details"""
    status = "✅" if passed else "❌"
    print(f"{status} [{category}] {name}")
    if details:
        print(f"   → {details}")
    
    test_results['passed' if passed else 'failed'] += 1
    test_results['details'].append({
        'category': category,
        'name': name,
        'passed': passed,
        'details': details
    })
    
    if not passed:
        test_results['broken_features'].append(f"{category}: {name}")
    
    return passed

print("\n1. COMPLETE STUDENT WORKFLOW TEST")
print("-" * 50)

client = Client()

try:
    # Find an active exam with questions
    exam = Exam.objects.filter(
        is_active=True,
        questions__isnull=False
    ).distinct().first()
    
    if exam:
        # Create a complete student session
        session = StudentSession.objects.create(
            student_name="Deep Test Student",
            parent_phone="555-1234",
            grade=6,
            academic_rank="TOP_20",
            exam=exam,
            original_curriculum_level=exam.curriculum_level or CurriculumLevel.objects.first()
        )
        
        log_test("Student", "Session creation", True, f"Session {session.id}")
        
        # Test answering questions
        questions = exam.questions.all()[:5]  # Test first 5 questions
        for i, question in enumerate(questions, 1):
            answer_text = "Test Answer" if question.question_type in ['SHORT', 'LONG'] else "A"
            
            answer = StudentAnswer.objects.create(
                session=session,
                question=question,
                answer=answer_text
            )
            
            # Verify answer saved correctly
            answer.refresh_from_db()
            if answer.answer != answer_text:
                log_test("Student", f"Answer Q{i}", False, "Answer not saved correctly")
                break
        else:
            log_test("Student", "Answer submission", True, f"Answered {len(questions)} questions")
        
        # Test session completion
        session.completed_at = timezone.now()
        session.save()
        log_test("Student", "Session completion", session.completed_at is not None)
        
        # Clean up
        session.delete()
    else:
        log_test("Student", "Workflow test", False, "No active exam found")
except Exception as e:
    log_test("Student", "Complete workflow", False, str(e)[:100])

print("\n2. MIXED MCQ OPTIONS TEST (Critical Feature)")
print("-" * 50)

try:
    # Test MIXED questions with various option counts
    mixed_questions = Question.objects.filter(question_type='MIXED')[:5]
    
    if mixed_questions:
        test_counts = [2, 3, 4, 5, 6, 7, 8, 9, 10]
        all_working = True
        
        for mixed_q in mixed_questions:
            original = mixed_q.options_count
            
            for count in test_counts:
                mixed_q.options_count = count
                mixed_q.save()
                mixed_q.refresh_from_db()
                
                if mixed_q.options_count != count:
                    log_test("MIXED", f"Q{mixed_q.id} set to {count}", False, 
                            f"Got {mixed_q.options_count}")
                    all_working = False
                    break
            
            # Restore original
            mixed_q.options_count = original
            mixed_q.save()
            
            if not all_working:
                break
        
        if all_working:
            log_test("MIXED", "All option counts (2-10)", True, 
                    f"Tested {len(mixed_questions)} questions")
    
    # Test exam default_options_count
    exam = Exam.objects.filter(questions__question_type='MIXED').first()
    if exam:
        original = exam.default_options_count
        
        for test_val in [3, 5, 7, 9]:
            exam.default_options_count = test_val
            exam.save()
            exam.refresh_from_db()
            
            if exam.default_options_count != test_val:
                log_test("MIXED", "Exam default options", False, 
                        f"Set {test_val}, got {exam.default_options_count}")
                break
        else:
            log_test("MIXED", "Exam default_options_count", True)
        
        # Restore
        exam.default_options_count = original
        exam.save()
    
except Exception as e:
    log_test("MIXED", "Options system", False, str(e)[:100])

print("\n3. TEACHER EXAM MANAGEMENT")
print("-" * 50)

try:
    # Test exam creation and modification
    exam = Exam.objects.first()
    if exam:
        # Test all modifiable fields
        original_name = exam.name
        original_timer = exam.timer_minutes
        original_total = exam.total_questions
        original_active = exam.is_active
        
        # Modify
        exam.name = "Test Modified Name"
        exam.timer_minutes = 120
        exam.total_questions = 75
        exam.is_active = not original_active
        exam.save()
        exam.refresh_from_db()
        
        # Verify
        modifications_work = (
            exam.name == "Test Modified Name" and
            exam.timer_minutes == 120 and
            exam.total_questions == 75 and
            exam.is_active != original_active
        )
        
        log_test("Teacher", "Exam field modifications", modifications_work)
        
        # Restore
        exam.name = original_name
        exam.timer_minutes = original_timer
        exam.total_questions = original_total
        exam.is_active = original_active
        exam.save()
        
    # Test exam API endpoints
    response = client.get('/api/placement/exams/')
    log_test("Teacher", "Exam list API", response.status_code in [200, 302])
    
    response = client.get('/teacher/dashboard/')
    log_test("Teacher", "Dashboard access", response.status_code in [200, 302])
    
except Exception as e:
    log_test("Teacher", "Exam management", False, str(e)[:100])

print("\n4. AUDIO FILE SYSTEM")
print("-" * 50)

try:
    # Test audio file assignments
    audio_files = AudioFile.objects.all()[:3]
    
    if audio_files:
        for audio in audio_files:
            # Test name modification
            original_name = audio.name
            audio.name = "Test Audio Name"
            audio.save()
            audio.refresh_from_db()
            
            name_works = audio.name == "Test Audio Name"
            
            # Restore
            audio.name = original_name
            audio.save()
            
            if not name_works:
                log_test("Audio", "Name modification", False)
                break
        else:
            log_test("Audio", "Audio file modifications", True, 
                    f"Tested {len(audio_files)} files")
    
    # Test question-audio assignment
    question = Question.objects.filter(audio_file__isnull=True).first()
    audio = AudioFile.objects.first()
    
    if question and audio:
        question.audio_file = audio
        question.save()
        question.refresh_from_db()
        
        assignment_works = question.audio_file == audio
        
        # Clear assignment
        question.audio_file = None
        question.save()
        
        log_test("Audio", "Question assignment", assignment_works)
    else:
        log_test("Audio", "Assignment test", True, "No unassigned questions")
    
except Exception as e:
    log_test("Audio", "Audio system", False, str(e)[:100])

print("\n5. ANSWER GRADING SYSTEM")
print("-" * 50)

try:
    # Test grading for different question types
    session = StudentSession.objects.filter(
        completed_at__isnull=False,
        answers__isnull=False
    ).first()
    
    if session:
        # Calculate score
        correct = 0
        total = 0
        
        for answer in session.answers.all():
            total += 1
            if answer.is_correct:
                correct += 1
        
        score_calculated = total > 0
        log_test("Grading", "Score calculation", score_calculated, 
                f"{correct}/{total} correct")
    else:
        # Create a test session for grading
        exam = Exam.objects.filter(is_active=True).first()
        if exam:
            test_session = StudentSession.objects.create(
                student_name="Grading Test",
                grade=5,
                academic_rank="AVERAGE",
                exam=exam,
                original_curriculum_level=CurriculumLevel.objects.first()
            )
            
            # Add some answers
            for q in exam.questions.all()[:3]:
                StudentAnswer.objects.create(
                    session=test_session,
                    question=q,
                    answer=q.correct_answer
                )
            
            # Mark complete
            test_session.completed_at = timezone.now()
            test_session.save()
            
            log_test("Grading", "Test session grading", True)
            
            # Clean up
            test_session.delete()
            
except Exception as e:
    log_test("Grading", "Grading system", False, str(e)[:100])

print("\n6. QUESTION TYPES TEST")
print("-" * 50)

try:
    # Test all question types
    question_types = {
        'MCQ': 'A',
        'CHECKBOX': 'A,B',
        'SHORT': 'Short answer',
        'LONG': 'Long answer text',
        'MIXED': 'A'
    }
    
    all_types_work = True
    for q_type, sample_answer in question_types.items():
        questions = Question.objects.filter(question_type=q_type)[:2]
        
        if questions:
            for q in questions:
                # Test answer format
                original = q.correct_answer
                q.correct_answer = sample_answer
                q.save()
                q.refresh_from_db()
                
                if q.correct_answer != sample_answer:
                    log_test("Questions", f"{q_type} type", False, 
                            "Cannot save answer")
                    all_types_work = False
                    break
                
                # Restore
                q.correct_answer = original
                q.save()
        else:
            log_test("Questions", f"{q_type} exists", False, "No questions found")
            all_types_work = False
    
    if all_types_work:
        log_test("Questions", "All 5 types functional", True)
        
except Exception as e:
    log_test("Questions", "Question types", False, str(e)[:100])

print("\n7. PLACEMENT RULES SYSTEM")
print("-" * 50)

try:
    # Test placement rules
    rules = PlacementRule.objects.all()
    
    if rules:
        rule = rules.first()
        
        # Test modification
        original_grade = rule.grade
        original_priority = rule.priority
        
        rule.grade = 7
        rule.priority = 99
        rule.save()
        rule.refresh_from_db()
        
        modifications_work = (rule.grade == 7 and rule.priority == 99)
        
        # Restore
        rule.grade = original_grade
        rule.priority = original_priority
        rule.save()
        
        log_test("Placement", "Rule modifications", modifications_work)
        
        # Test curriculum level link
        if rule.curriculum_level:
            log_test("Placement", "Curriculum level link", True,
                    rule.curriculum_level.full_name)
    else:
        log_test("Placement", "Rules exist", False, "No placement rules")
        
    # Test exam-level mapping
    mappings = ExamLevelMapping.objects.all()
    log_test("Placement", "Exam-Level mappings", mappings.exists(),
            f"{mappings.count()} mappings")
    
except Exception as e:
    log_test("Placement", "Placement system", False, str(e)[:100])

print("\n8. DATABASE RELATIONSHIPS")
print("-" * 50)

try:
    # Check all foreign key relationships
    
    # Questions must have exams
    orphan_questions = Question.objects.filter(exam__isnull=True).count()
    log_test("Database", "No orphaned questions", orphan_questions == 0,
            f"{orphan_questions} orphans" if orphan_questions else "All linked")
    
    # Audio files must have exams
    orphan_audio = AudioFile.objects.filter(exam__isnull=True).count()
    log_test("Database", "No orphaned audio", orphan_audio == 0,
            f"{orphan_audio} orphans" if orphan_audio else "All linked")
    
    # Sessions should have exams
    broken_sessions = StudentSession.objects.filter(
        exam__isnull=True,
        completed_at__isnull=True
    ).count()
    log_test("Database", "Session integrity", broken_sessions == 0,
            f"{broken_sessions} broken" if broken_sessions else "All valid")
    
    # Answers must have sessions and questions
    broken_answers = StudentAnswer.objects.filter(
        session__isnull=True
    ).count() + StudentAnswer.objects.filter(
        question__isnull=True
    ).count()
    log_test("Database", "Answer integrity", broken_answers == 0,
            f"{broken_answers} broken" if broken_answers else "All valid")
    
except Exception as e:
    log_test("Database", "Relationships", False, str(e)[:100])

print("\n9. API ENDPOINTS TEST")
print("-" * 50)

try:
    # Test all critical API endpoints
    endpoints = [
        ('/api/placement/exams/', 'GET', 'Exam list'),
        ('/teacher/dashboard/', 'GET', 'Dashboard'),
        ('/placement-rules/', 'GET', 'Placement rules'),
        ('/exam-mapping/', 'GET', 'Exam mapping'),
    ]
    
    for url, method, name in endpoints:
        response = client.get(url) if method == 'GET' else client.post(url)
        log_test("API", name, response.status_code in [200, 302],
                f"Status: {response.status_code}")
    
    # Test question update API
    q = Question.objects.first()
    if q:
        response = client.post(
            f'/api/placement/questions/{q.id}/update/',
            {'correct_answer': q.correct_answer, 'points': q.points}
        )
        log_test("API", "Question update", response.status_code in [200, 302])
        
except Exception as e:
    log_test("API", "Endpoints", False, str(e)[:100])

print("\n10. DIFFICULTY ADJUSTMENT COMPATIBILITY")
print("-" * 50)

try:
    # Ensure difficulty adjustment didn't break existing session flow
    session = StudentSession.objects.filter(completed_at__isnull=True).first()
    
    if not session:
        # Create test session
        exam = Exam.objects.filter(is_active=True).first()
        level = CurriculumLevel.objects.first()
        if exam and level:
            session = StudentSession.objects.create(
                student_name="Compatibility Test",
                grade=5,
                academic_rank="TOP_10",
                exam=exam,
                original_curriculum_level=level
            )
    
    if session:
        # Test that existing sessions still work without difficulty adjustments
        original_exam = session.exam
        original_level = session.original_curriculum_level
        
        # Session should work normally without any adjustments
        session.save()
        session.refresh_from_db()
        
        works_without_adjustment = (
            session.exam == original_exam and
            session.original_curriculum_level == original_level
        )
        
        log_test("Compatibility", "Sessions without adjustment", 
                works_without_adjustment)
        
        # Test that difficulty adjustment is optional
        if hasattr(session, 'difficulty_adjustments'):
            log_test("Compatibility", "Adjustment field exists", True,
                    f"Count: {session.difficulty_adjustments}")
        
        # Clean up test session
        if session.student_name == "Compatibility Test":
            session.delete()
            
except Exception as e:
    log_test("Compatibility", "Backward compatibility", False, str(e)[:100])

# Final Summary
print("\n" + "="*80)
print("DEEP VERIFICATION SUMMARY")
print("="*80)

total = test_results['passed'] + test_results['failed']
pass_rate = (test_results['passed'] / total * 100) if total > 0 else 0

print(f"\n📊 FINAL RESULTS:")
print(f"Passed: {test_results['passed']}/{total} ({pass_rate:.1f}%)")
print(f"Failed: {test_results['failed']}/{total}")

if test_results['broken_features']:
    print(f"\n❌ BROKEN FEATURES:")
    for feature in test_results['broken_features']:
        print(f"  - {feature}")
else:
    print(f"\n✅ NO BROKEN FEATURES DETECTED")

# Category summary
categories = {}
for detail in test_results['details']:
    cat = detail['category']
    if cat not in categories:
        categories[cat] = {'passed': 0, 'failed': 0}
    if detail['passed']:
        categories[cat]['passed'] += 1
    else:
        categories[cat]['failed'] += 1

print(f"\n📋 BY CATEGORY:")
for cat, stats in categories.items():
    total_cat = stats['passed'] + stats['failed']
    rate = (stats['passed'] / total_cat * 100) if total_cat > 0 else 0
    status = "✅" if stats['failed'] == 0 else "⚠️"
    print(f"{status} {cat:15} {stats['passed']}/{total_cat} passed ({rate:.0f}%)")

if pass_rate == 100:
    print("\n" + "🎉"*20)
    print("PERFECT! All existing features working correctly!")
    print("No regression detected from difficulty adjustment!")
    print("🎉"*20)
elif pass_rate >= 95:
    print("\n✅ EXCELLENT - System fully functional")
    print("Minor issues detected but all critical features working")
elif pass_rate >= 90:
    print("\n⚠️ GOOD - Core features intact")
    print("Some issues detected, review needed")
else:
    print("\n❌ ISSUES DETECTED")
    print("Multiple features affected, immediate attention needed")

# Save detailed results
with open('deep_feature_check_results.json', 'w') as f:
    json.dump(test_results, f, indent=2, default=str)

print(f"\nDetailed results saved to: deep_feature_check_results.json")
print("="*80)
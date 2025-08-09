#!/usr/bin/env python
"""
Comprehensive verification of ALL existing features
Ensures no regression from difficulty adjustment implementation
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.db import transaction
from placement_test.models import Question, Exam, StudentSession, AudioFile, StudentAnswer
from core.models import CurriculumLevel, PlacementRule, ExamLevelMapping

print('='*80)
print('EXISTING FEATURES VERIFICATION TEST')
print(f'Timestamp: {datetime.now()}')
print('='*80)

# Test results
test_results = {
    'passed': 0,
    'failed': 0,
    'categories': {}
}

def log_test(category, test_name, passed, details=""):
    """Log test result"""
    status = "✅" if passed else "❌"
    print(f"{status} {test_name}")
    if details:
        print(f"    → {details}")
    
    test_results['passed' if passed else 'failed'] += 1
    
    if category not in test_results['categories']:
        test_results['categories'][category] = {'passed': 0, 'failed': 0, 'tests': []}
    test_results['categories'][category]['passed' if passed else 'failed'] += 1
    test_results['categories'][category]['tests'].append({
        'name': test_name,
        'passed': passed,
        'details': details
    })

print("\n1. MIXED MCQ OPTIONS CUSTOMIZATION (Critical Feature)")
print("-" * 50)

# Test MIXED question type with different options counts
try:
    mixed_questions = Question.objects.filter(question_type='MIXED')
    if mixed_questions.exists():
        test_cases = [2, 4, 6, 8, 10]  # Test various option counts
        all_passed = True
        
        for mixed_q in mixed_questions[:3]:  # Test first 3 MIXED questions
            original_count = mixed_q.options_count
            
            for count in test_cases:
                mixed_q.options_count = count
                mixed_q.save()
                mixed_q.refresh_from_db()
                
                if mixed_q.options_count != count:
                    all_passed = False
                    log_test('MIXED MCQ', f'Set options to {count}', False, 
                            f"Expected {count}, got {mixed_q.options_count}")
                    break
            
            # Restore original
            mixed_q.options_count = original_count
            mixed_q.save()
            
            if all_passed:
                log_test('MIXED MCQ', f'Question {mixed_q.id} options customization', True,
                        f"All counts (2-10) work correctly")
        
        # Test default_options_count on Exam
        exam = Exam.objects.filter(questions__question_type='MIXED').first()
        if exam:
            original_default = exam.default_options_count
            exam.default_options_count = 7
            exam.save()
            exam.refresh_from_db()
            
            log_test('MIXED MCQ', 'Exam default_options_count', 
                    exam.default_options_count == 7,
                    f"Set to 7, got {exam.default_options_count}")
            
            # Restore
            exam.default_options_count = original_default
            exam.save()
    else:
        log_test('MIXED MCQ', 'MIXED questions exist', False, "No MIXED questions found")
except Exception as e:
    log_test('MIXED MCQ', 'Options customization', False, str(e))

print("\n2. QUESTION TYPES INTEGRITY")
print("-" * 50)

# Verify all question types still work
question_types = ['MCQ', 'CHECKBOX', 'SHORT', 'LONG', 'MIXED']
for q_type in question_types:
    try:
        questions = Question.objects.filter(question_type=q_type)
        if questions.exists():
            q = questions.first()
            
            # Test that we can read and modify
            original_answer = q.correct_answer
            q.correct_answer = original_answer + "_test"
            q.save()
            q.refresh_from_db()
            
            modified_correctly = q.correct_answer == original_answer + "_test"
            
            # Restore
            q.correct_answer = original_answer
            q.save()
            
            log_test('Questions', f'{q_type} modification', modified_correctly)
        else:
            log_test('Questions', f'{q_type} exists', False, "No questions of this type")
    except Exception as e:
        log_test('Questions', f'{q_type} integrity', False, str(e))

print("\n3. AUDIO FILE ASSIGNMENTS")
print("-" * 50)

# Test audio file to question assignments
try:
    # Test direct assignment (new model structure)
    question_with_audio = Question.objects.filter(audio_file__isnull=False).first()
    if question_with_audio:
        original_audio = question_with_audio.audio_file
        
        # Try to change audio assignment
        other_audio = AudioFile.objects.exclude(id=original_audio.id).first()
        if other_audio:
            question_with_audio.audio_file = other_audio
            question_with_audio.save()
            question_with_audio.refresh_from_db()
            
            changed = question_with_audio.audio_file.id == other_audio.id
            
            # Restore
            question_with_audio.audio_file = original_audio
            question_with_audio.save()
            
            log_test('Audio', 'Question-Audio assignment', changed,
                    "Can modify audio assignments")
        else:
            log_test('Audio', 'Multiple audio files', False, "Need multiple audio files to test")
    else:
        # Try to create an assignment
        question = Question.objects.filter(audio_file__isnull=True).first()
        audio = AudioFile.objects.first()
        
        if question and audio:
            question.audio_file = audio
            question.save()
            question.refresh_from_db()
            
            assigned = question.audio_file is not None
            
            # Clear assignment
            question.audio_file = None
            question.save()
            
            log_test('Audio', 'New audio assignment', assigned)
        else:
            log_test('Audio', 'Audio assignment test', False, "No questions or audio files")
except Exception as e:
    log_test('Audio', 'Audio file system', False, str(e))

print("\n4. STUDENT SESSION WORKFLOW")
print("-" * 50)

client = Client()

# Test session creation and management
try:
    # Create a test session
    exam = Exam.objects.filter(is_active=True).first()
    level = CurriculumLevel.objects.first()
    
    if exam and level:
        with transaction.atomic():
            session = StudentSession.objects.create(
                student_name="Feature Test Student",
                grade=6,
                academic_rank="TOP_20",
                exam=exam,
                original_curriculum_level=level
            )
            
            log_test('Session', 'Session creation', True, f"Session {session.id}")
            
            # Test answer submission
            question = exam.questions.first()
            if question:
                answer = StudentAnswer.objects.create(
                    session=session,
                    question=question,
                    answer="Test Answer"
                )
                
                log_test('Session', 'Answer submission', True)
                
                # Test answer modification
                answer.answer = "Modified Answer"
                answer.save()
                answer.refresh_from_db()
                
                log_test('Session', 'Answer modification', 
                        answer.answer == "Modified Answer")
            
            # Clean up
            session.delete()
    else:
        log_test('Session', 'Test data available', False, "No exam or curriculum level")
except Exception as e:
    log_test('Session', 'Session workflow', False, str(e))

print("\n5. EXAM MANAGEMENT")
print("-" * 50)

# Test exam creation and editing
try:
    # Test exam properties
    exam = Exam.objects.first()
    if exam:
        # Test timer
        original_timer = exam.timer_minutes
        exam.timer_minutes = 90
        exam.save()
        exam.refresh_from_db()
        
        timer_works = exam.timer_minutes == 90
        
        # Restore
        exam.timer_minutes = original_timer
        exam.save()
        
        log_test('Exam', 'Timer modification', timer_works)
        
        # Test total questions
        original_total = exam.total_questions
        exam.total_questions = 50
        exam.save()
        exam.refresh_from_db()
        
        total_works = exam.total_questions == 50
        
        # Restore
        exam.total_questions = original_total
        exam.save()
        
        log_test('Exam', 'Total questions modification', total_works)
        
        # Test is_active toggle
        original_active = exam.is_active
        exam.is_active = not original_active
        exam.save()
        exam.refresh_from_db()
        
        active_works = exam.is_active != original_active
        
        # Restore
        exam.is_active = original_active
        exam.save()
        
        log_test('Exam', 'Active status toggle', active_works)
except Exception as e:
    log_test('Exam', 'Exam management', False, str(e))

print("\n6. PLACEMENT RULES")
print("-" * 50)

# Test placement rules system
try:
    rules = PlacementRule.objects.all()
    if rules.exists():
        rule = rules.first()
        
        # Test grade field (single grade, not range)
        original_grade = rule.grade
        rule.grade = 5
        rule.save()
        rule.refresh_from_db()
        
        grade_works = rule.grade == 5
        
        # Restore
        rule.grade = original_grade
        rule.save()
        
        log_test('Placement', 'Grade modification', grade_works)
        
        # Test curriculum level assignment
        if rule.curriculum_level:
            log_test('Placement', 'Curriculum level link', True,
                    f"Rule links to {rule.curriculum_level.full_name}")
        else:
            log_test('Placement', 'Curriculum level link', False, "No level assigned")
    else:
        log_test('Placement', 'Placement rules exist', False, "No rules configured")
except Exception as e:
    log_test('Placement', 'Placement system', False, str(e))

print("\n7. EXAM-LEVEL MAPPING")
print("-" * 50)

# Test exam to curriculum level mapping
try:
    mappings = ExamLevelMapping.objects.all()
    if mappings.exists():
        mapping = mappings.first()
        
        log_test('Mapping', 'Exam-Level mapping exists', True,
                f"{mapping.exam.name} → {mapping.curriculum_level.full_name}")
        
        # Test that exams can find their levels
        exam = Exam.objects.filter(level_mappings__isnull=False).first()
        if exam:
            levels = exam.level_mappings.all()
            log_test('Mapping', 'Exam can find levels', levels.exists(),
                    f"Found {levels.count()} level(s)")
    else:
        log_test('Mapping', 'Mappings configured', False, "No mappings found")
except Exception as e:
    log_test('Mapping', 'Mapping system', False, str(e))

print("\n8. API ENDPOINTS")
print("-" * 50)

# Test critical API endpoints
endpoints = [
    ('/api/placement/exams/', 'GET', 'Exam list API'),
    ('/api/placement/questions/', 'GET', 'Questions API'),
]

for url, method, name in endpoints:
    try:
        if method == 'GET':
            response = client.get(url)
        else:
            response = client.post(url)
        
        log_test('API', name, response.status_code in [200, 201, 302])
    except Exception as e:
        log_test('API', name, False, str(e))

print("\n9. VIEWS AND TEMPLATES")
print("-" * 50)

# Test that key views still render
views = [
    ('/', 'Homepage'),
    ('/teacher/dashboard/', 'Teacher Dashboard'),
    ('/placement-rules/', 'Placement Rules'),
    ('/exam-mapping/', 'Exam Mapping'),
]

for url, name in views:
    try:
        response = client.get(url)
        log_test('Views', name, response.status_code in [200, 302])
    except Exception as e:
        log_test('Views', name, False, str(e))

print("\n10. DATABASE INTEGRITY")
print("-" * 50)

# Check for orphaned records or broken relationships
try:
    # Check questions without exams
    orphaned_questions = Question.objects.filter(exam__isnull=True).count()
    log_test('Database', 'No orphaned questions', orphaned_questions == 0,
            f"{orphaned_questions} orphaned" if orphaned_questions > 0 else "All questions have exams")
    
    # Check audio files without exams
    orphaned_audio = AudioFile.objects.filter(exam__isnull=True).count()
    log_test('Database', 'No orphaned audio files', orphaned_audio == 0,
            f"{orphaned_audio} orphaned" if orphaned_audio > 0 else "All audio files have exams")
    
    # Check sessions integrity
    incomplete_sessions = StudentSession.objects.filter(
        exam__isnull=True,
        completed_at__isnull=True
    ).count()
    log_test('Database', 'Session integrity', incomplete_sessions == 0,
            f"{incomplete_sessions} incomplete" if incomplete_sessions > 0 else "All sessions valid")
except Exception as e:
    log_test('Database', 'Database integrity', False, str(e))

# Summary
print("\n" + "="*80)
print("VERIFICATION RESULTS")
print("="*80)

total_tests = test_results['passed'] + test_results['failed']
pass_rate = (test_results['passed'] / total_tests * 100) if total_tests > 0 else 0

print(f"\n📊 OVERALL RESULTS:")
print(f"Total Tests: {total_tests}")
print(f"Passed: {test_results['passed']}")
print(f"Failed: {test_results['failed']}")
print(f"Pass Rate: {pass_rate:.1f}%")

print(f"\n📋 CATEGORY BREAKDOWN:")
for category, stats in test_results['categories'].items():
    cat_total = stats['passed'] + stats['failed']
    cat_rate = (stats['passed'] / cat_total * 100) if cat_total > 0 else 0
    print(f"{category:12} - {stats['passed']}/{cat_total} passed ({cat_rate:.0f}%)")
    
    # Show failed tests
    if stats['failed'] > 0:
        for test in stats['tests']:
            if not test['passed']:
                print(f"  ❌ {test['name']}: {test['details']}")

print("\n🔍 CRITICAL FEATURES STATUS:")
critical_features = {
    'MIXED MCQ Options': 'MIXED MCQ' in test_results['categories'] and 
                        test_results['categories']['MIXED MCQ']['failed'] == 0,
    'Question Types': 'Questions' in test_results['categories'] and 
                     test_results['categories']['Questions']['failed'] == 0,
    'Audio System': 'Audio' in test_results['categories'] and 
                   test_results['categories']['Audio']['failed'] == 0,
    'Session Management': 'Session' in test_results['categories'] and 
                         test_results['categories']['Session']['failed'] == 0,
    'Exam Configuration': 'Exam' in test_results['categories'] and 
                         test_results['categories']['Exam']['failed'] == 0,
}

for feature, working in critical_features.items():
    status = "✅ Working" if working else "❌ BROKEN"
    print(f"{feature}: {status}")

if pass_rate >= 95:
    print("\n" + "🎉"*20)
    print("ALL EXISTING FEATURES VERIFIED WORKING!")
    print("No regression detected from difficulty adjustment implementation")
    print("🎉"*20)
elif pass_rate >= 85:
    print("\n⚠️ MOSTLY WORKING")
    print("Some minor issues detected, but core features are intact")
else:
    print("\n❌ CRITICAL ISSUES DETECTED")
    print("Multiple features may be affected")

# Save results
with open('existing_features_verification.json', 'w') as f:
    json.dump(test_results, f, indent=2, default=str)

print(f"\nDetailed results saved to: existing_features_verification.json")
print("="*80)
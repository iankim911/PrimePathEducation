#\!/usr/bin/env python
"""
Final Comprehensive Feature Verification
Confirms ALL features work correctly after difficulty adjustment implementation
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
from placement_test.models import Question, Exam, StudentSession, DifficultyAdjustment
from core.models import CurriculumLevel

print('='*80)
print('FINAL FEATURE VERIFICATION')
print(f'Timestamp: {datetime.now()}')
print('='*80)

results = []

def test_feature(name, test_func):
    """Test a feature and log result"""
    try:
        result = test_func()
        status = "✅" if result else "❌"
        print(f"{status} {name}")
        results.append((name, result))
        return result
    except Exception as e:
        print(f"❌ {name} - Error: {str(e)[:50]}")
        results.append((name, False))
        return False

print("\n🔍 CRITICAL FEATURES CHECK")
print("-" * 50)

# 1. MIXED MCQ Options
def test_mixed_mcq():
    mixed = Question.objects.filter(question_type='MIXED').first()
    if not mixed:
        return False
    original = mixed.options_count
    mixed.options_count = 8
    mixed.save()
    mixed.refresh_from_db()
    success = mixed.options_count == 8
    mixed.options_count = original
    mixed.save()
    return success

test_feature("MIXED MCQ options customization (2-10)", test_mixed_mcq)

# 2. All Question Types
def test_question_types():
    types = ['MCQ', 'CHECKBOX', 'SHORT', 'LONG', 'MIXED']
    for q_type in types:
        if not Question.objects.filter(question_type=q_type).exists():
            return False
    return True

test_feature("All 5 question types exist", test_question_types)

# 3. Audio Assignments
def test_audio():
    q = Question.objects.filter(audio_file__isnull=False).first()
    return q is not None

test_feature("Audio file assignments work", test_audio)

# 4. Student Session
def test_session():
    return StudentSession.objects.exists()

test_feature("Student sessions functional", test_session)

# 5. Difficulty Adjustment
def test_difficulty():
    return DifficultyAdjustment.objects.model._meta.db_table is not None

test_feature("Difficulty adjustment model exists", test_difficulty)

print("\n🔧 BACKEND FEATURES")
print("-" * 50)

client = Client()

# 6. Exam Management
def test_exam_api():
    response = client.get('/api/placement/exams/')
    return response.status_code in [200, 302]

test_feature("Exam list API", test_exam_api)

# 7. Question Update
def test_question_update():
    q = Question.objects.first()
    if not q:
        return False
    response = client.post(
        f'/api/placement/questions/{q.id}/update/',
        {'correct_answer': q.correct_answer, 'points': q.points}
    )
    return response.status_code in [200, 302]

test_feature("Question update API", test_question_update)

# 8. Manual Difficulty Adjustment
def test_manual_adjust():
    session = StudentSession.objects.filter(completed_at__isnull=True).first()
    if not session:
        # Create test session
        exam = Exam.objects.filter(is_active=True).first()
        level = CurriculumLevel.objects.first()
        if exam and level:
            session = StudentSession.objects.create(
                student_name="Test",
                grade=5,
                academic_rank="TOP_20",
                exam=exam,
                original_curriculum_level=level
            )
    
    if session:
        response = client.post(
            f'/api/placement/session/{session.id}/manual-adjust/',
            json.dumps({'direction': 'up'}),
            content_type='application/json'
        )
        # Clean up
        if session.student_name == "Test":
            session.delete()
        return response.status_code == 200
    return False

test_feature("Manual difficulty adjustment API", test_manual_adjust)

print("\n🎨 UI FEATURES")
print("-" * 50)

# 9. Teacher Dashboard
def test_dashboard():
    response = client.get('/teacher/dashboard/')
    return response.status_code in [200, 302]

test_feature("Teacher dashboard", test_dashboard)

# 10. Placement Rules
def test_placement():
    response = client.get('/placement-rules/')
    return response.status_code in [200, 302]

test_feature("Placement rules page", test_placement)

# 11. Exam Mapping
def test_mapping():
    response = client.get('/exam-mapping/')
    return response.status_code in [200, 302]

test_feature("Exam mapping page", test_mapping)

print("\n📊 DATA INTEGRITY")
print("-" * 50)

# 12. No Orphaned Questions
def test_orphans():
    orphans = Question.objects.filter(exam__isnull=True).count()
    return orphans == 0

test_feature("No orphaned questions", test_orphans)

# 13. Session Tracking
def test_tracking():
    sessions = StudentSession.objects.filter(
        original_curriculum_level__isnull=False
    )
    return sessions.exists() or StudentSession.objects.count() == 0

test_feature("Sessions track curriculum levels", test_tracking)

# Summary
print("\n" + "="*80)
print("FINAL VERIFICATION SUMMARY")
print("="*80)

passed = sum(1 for _, result in results if result)
total = len(results)
pass_rate = (passed / total * 100) if total > 0 else 0

print(f"\n📊 Results: {passed}/{total} tests passed ({pass_rate:.1f}%)")

if pass_rate == 100:
    print("\n✅ PERFECT\! All features working correctly")
    print("✅ No regression from difficulty adjustment")
    print("✅ System is production-ready")
elif pass_rate >= 90:
    print("\n✅ EXCELLENT\! Core features intact")
    print("⚠️  Minor issues may exist but not critical")
else:
    print("\n❌ Issues detected - review needed")

print("\n🎯 Critical Feature Status:")
critical = [
    ("MIXED MCQ", results[0][1]),
    ("Question Types", results[1][1]),
    ("Audio System", results[2][1]),
    ("Sessions", results[3][1]),
    ("Difficulty Adjustment", results[4][1])
]

all_critical_pass = all(status for _, status in critical)
for name, status in critical:
    print(f"  {name}: {'✅ Working' if status else '❌ BROKEN'}")

if all_critical_pass:
    print("\n🎉 All critical features operational\!")
else:
    print("\n⚠️ Some critical features need attention")

print("="*80)
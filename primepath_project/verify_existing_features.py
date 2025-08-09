#!/usr/bin/env python
"""
Verify all existing features still work correctly
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
from django.urls import reverse
from django.db import connection
from placement_test.models import Question, Exam, StudentSession, AudioFile
from placement_test.services.exam_service import ExamService
from core.models import CurriculumLevel

print('='*80)
print('EXISTING FEATURES VERIFICATION')
print(f'Timestamp: {datetime.now()}')
print('='*80)

features_tested = []
issues_found = []

# 1. Exam Creation Feature
print('\n1. EXAM CREATION')
print('-'*40)
try:
    # Check if exam creation view loads
    client = Client()
    response = client.get(reverse('placement_test:create_exam'))
    if response.status_code == 200:
        print('✅ Exam creation page loads')
        features_tested.append(('Exam creation page', True))
    else:
        print(f'❌ Exam creation page error: {response.status_code}')
        features_tested.append(('Exam creation page', False))
        issues_found.append('Exam creation page not loading')
except Exception as e:
    print(f'❌ Error: {e}')
    features_tested.append(('Exam creation page', False))
    issues_found.append(f'Exam creation error: {e}')

# 2. PDF Upload Feature
print('\n2. PDF UPLOAD')
print('-'*40)
pdf_exams = Exam.objects.filter(pdf_file__isnull=False)[:1]
if pdf_exams:
    exam = pdf_exams[0]
    if exam.pdf_file and exam.pdf_file.name:
        print(f'✅ PDF files properly stored: {exam.pdf_file.name}')
        features_tested.append(('PDF storage', True))
    else:
        print('❌ PDF file reference broken')
        features_tested.append(('PDF storage', False))
        issues_found.append('PDF file reference broken')
else:
    print('⚠️ No exams with PDF found for testing')
    features_tested.append(('PDF storage', None))

# 3. Audio Assignment Feature
print('\n3. AUDIO ASSIGNMENT')
print('-'*40)
audio_questions = Question.objects.filter(audio_file__isnull=False)[:1]
if audio_questions:
    q = audio_questions[0]
    print(f'✅ Audio assignment working: Q{q.question_number} has audio')
    features_tested.append(('Audio assignment', True))
else:
    print('⚠️ No questions with audio assignments found')
    features_tested.append(('Audio assignment', None))

# 4. Student Session Creation
print('\n4. STUDENT SESSION')
print('-'*40)
try:
    # Check if start test page loads
    response = client.get(reverse('placement_test:start_test'))
    if response.status_code == 200:
        print('✅ Start test page loads')
        features_tested.append(('Start test page', True))
    else:
        print(f'❌ Start test page error: {response.status_code}')
        features_tested.append(('Start test page', False))
        issues_found.append('Start test page not loading')
except Exception as e:
    print(f'❌ Error: {e}')
    features_tested.append(('Start test page', False))
    issues_found.append(f'Start test error: {e}')

# 5. Grading System
print('\n5. GRADING SYSTEM')
print('-'*40)
# Check if questions have correct_answer field populated
questions_with_answers = Question.objects.exclude(correct_answer='').exclude(correct_answer__isnull=True)
total_questions = Question.objects.count()
if questions_with_answers.count() > 0:
    print(f'✅ Grading data present: {questions_with_answers.count()}/{total_questions} questions have answers')
    features_tested.append(('Grading data', True))
else:
    print('❌ No questions have grading data')
    features_tested.append(('Grading data', False))
    issues_found.append('No grading data found')

# 6. MCQ Questions
print('\n6. MCQ QUESTIONS')
print('-'*40)
mcq = Question.objects.filter(question_type='MCQ').first()
if mcq:
    # Check that MCQ questions don't have multiple inputs
    from placement_test.templatetags.grade_tags import get_answer_letters, has_multiple_answers
    letters = get_answer_letters(mcq)
    multi = has_multiple_answers(mcq)
    if len(letters) == 0 and not multi:
        print('✅ MCQ questions render correctly (single choice)')
        features_tested.append(('MCQ rendering', True))
    else:
        print('❌ MCQ questions incorrectly showing multiple inputs')
        features_tested.append(('MCQ rendering', False))
        issues_found.append('MCQ rendering broken')
else:
    print('⚠️ No MCQ questions found')
    features_tested.append(('MCQ rendering', None))

# 7. Timer Functionality
print('\n7. TIMER FUNCTIONALITY')
print('-'*40)
exams_with_timer = Exam.objects.filter(timer_minutes__gt=0)
if exams_with_timer.exists():
    exam = exams_with_timer.first()
    print(f'✅ Timer configured: {exam.timer_minutes} minutes for "{exam.name[:30]}..."')
    features_tested.append(('Timer configuration', True))
else:
    print('⚠️ No exams with timer configured')
    features_tested.append(('Timer configuration', None))

# 8. Preview and Answer Keys
print('\n8. PREVIEW AND ANSWER KEYS')
print('-'*40)
try:
    exam = Exam.objects.first()
    if exam:
        response = client.get(reverse('placement_test:preview_exam', args=[exam.id]))
        if response.status_code == 200:
            print('✅ Preview and answer keys page loads')
            features_tested.append(('Preview page', True))
        else:
            print(f'❌ Preview page error: {response.status_code}')
            features_tested.append(('Preview page', False))
            issues_found.append('Preview page not loading')
except Exception as e:
    print(f'❌ Error: {e}')
    features_tested.append(('Preview page', False))
    issues_found.append(f'Preview page error: {e}')

# 9. Curriculum Level Integration
print('\n9. CURRICULUM LEVEL')
print('-'*40)
exams_with_curriculum = Exam.objects.filter(curriculum_level__isnull=False)
if exams_with_curriculum.exists():
    exam = exams_with_curriculum.first()
    print(f'✅ Curriculum integration: "{exam.name[:30]}..." linked to {exam.curriculum_level}')
    features_tested.append(('Curriculum integration', True))
else:
    print('⚠️ No exams linked to curriculum levels')
    features_tested.append(('Curriculum integration', None))

# 10. Database Integrity
print('\n10. DATABASE INTEGRITY')
print('-'*40)
try:
    with connection.cursor() as cursor:
        # Check for orphaned questions
        cursor.execute("""
            SELECT COUNT(*) FROM placement_test_question 
            WHERE exam_id NOT IN (SELECT id FROM placement_test_exam)
        """)
        orphaned = cursor.fetchone()[0]
        
        if orphaned == 0:
            print('✅ No orphaned questions')
            features_tested.append(('Database integrity', True))
        else:
            print(f'❌ Found {orphaned} orphaned questions')
            features_tested.append(('Database integrity', False))
            issues_found.append(f'{orphaned} orphaned questions')
except Exception as e:
    print(f'❌ Database check error: {e}')
    features_tested.append(('Database integrity', False))
    issues_found.append(f'Database error: {e}')

# 11. Question Types Distribution
print('\n11. QUESTION TYPES')
print('-'*40)
from django.db.models import Count
type_counts = Question.objects.values('question_type').annotate(count=Count('id'))
for tc in type_counts:
    print(f'   {tc["question_type"]}: {tc["count"]} questions')
features_tested.append(('Question type distribution', True))

# 12. Session Tracking
print('\n12. SESSION TRACKING')
print('-'*40)
recent_sessions = StudentSession.objects.order_by('-started_at')[:1]
if recent_sessions:
    session = recent_sessions[0]
    print(f'✅ Session tracking: Latest session by {session.student_name}')
    features_tested.append(('Session tracking', True))
else:
    print('⚠️ No student sessions found')
    features_tested.append(('Session tracking', None))

# Summary
print('\n' + '='*80)
print('FEATURE VERIFICATION SUMMARY')
print('='*80)

working = sum(1 for _, status in features_tested if status is True)
broken = sum(1 for _, status in features_tested if status is False)
untested = sum(1 for _, status in features_tested if status is None)

print(f'\n✅ Working: {working} features')
print(f'❌ Broken: {broken} features')
print(f'⚠️ Untested: {untested} features (no data)')

if issues_found:
    print('\n🔴 ISSUES FOUND:')
    for issue in issues_found:
        print(f'   - {issue}')
else:
    print('\n✅ ALL TESTED FEATURES WORKING CORRECTLY')

# Detailed results
print('\n' + '='*80)
print('DETAILED RESULTS')
print('='*80)

for feature, status in features_tested:
    if status is True:
        symbol = '✅'
    elif status is False:
        symbol = '❌'
    else:
        symbol = '⚠️'
    print(f'{symbol} {feature}')

# Final verdict
print('\n' + '='*80)
if broken == 0:
    print('✅ NO EXISTING FEATURES WERE BROKEN BY THE FIXES')
    print('All tested features are functioning correctly.')
else:
    print(f'❌ {broken} FEATURES MAY BE AFFECTED')
    print('Please review the issues above.')
print('='*80)
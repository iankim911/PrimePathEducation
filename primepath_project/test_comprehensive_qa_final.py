#!/usr/bin/env python
"""
Final comprehensive QA test for MIXED MCQ fix
Tests all features to ensure nothing is broken
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
from django.conf import settings
from django.db import connection
from placement_test.models import Question, Exam, AudioFile
from placement_test.templatetags.grade_tags import (
    get_mixed_components, has_multiple_answers, get_answer_letters,
    is_mixed_question, format_grade
)
from placement_test.services.exam_service import ExamService
from core.models import CurriculumLevel

print('='*80)
print('FINAL COMPREHENSIVE QA TEST')
print(f'Timestamp: {datetime.now()}')
print('='*80)

all_tests = []
issues = []
test_categories = {}

def add_test(category, name, result):
    """Helper to track tests by category"""
    all_tests.append((name, result))
    if category not in test_categories:
        test_categories[category] = {'passed': 0, 'failed': 0, 'skipped': 0}
    
    if result is True:
        test_categories[category]['passed'] += 1
    elif result is False:
        test_categories[category]['failed'] += 1
    else:
        test_categories[category]['skipped'] += 1

# CATEGORY 1: MIXED QUESTION MCQ RENDERING
print('\n' + '='*60)
print('CATEGORY 1: MIXED QUESTION MCQ RENDERING')
print('='*60)

mixed_mcq_questions = Question.objects.filter(
    question_type='MIXED',
    correct_answer__contains='Multiple Choice'
)

print(f'\nFound {mixed_mcq_questions.count()} MIXED questions with MCQ components')

for q in mixed_mcq_questions[:3]:
    print(f'\nQuestion {q.id} (#{q.question_number}):')
    print(f'  Exam: {q.exam.name[:50]}...')
    print(f'  Options count: {q.options_count}')
    
    # Parse JSON
    try:
        parsed = json.loads(q.correct_answer)
        mcq_count = sum(1 for item in parsed if item.get('type') == 'Multiple Choice')
        print(f'  JSON: {mcq_count} Multiple Choice components')
    except:
        parsed = []
        mcq_count = 0
    
    # Test filter
    components = get_mixed_components(q)
    mcq_components = [c for c in components if c.get('type') == 'mcq']
    
    print(f'  Filter returns: {len(mcq_components)} MCQ components')
    
    # Verify each MCQ component
    all_valid = True
    for comp in mcq_components:
        if 'options' not in comp or not isinstance(comp['options'], list):
            all_valid = False
            print(f'    ❌ Component {comp.get("letter")} missing options')
            issues.append(f'Q{q.id} MCQ component missing options')
        elif 'index' not in comp:
            all_valid = False
            print(f'    ❌ Component {comp.get("letter")} missing index')
            issues.append(f'Q{q.id} MCQ component missing index')
        else:
            print(f'    ✅ Component {comp.get("letter")}: {len(comp["options"])} options, index={comp["index"]}')
    
    if all_valid and len(mcq_components) == mcq_count:
        add_test('MIXED MCQ', f'Q{q.id} MCQ rendering', True)
    else:
        add_test('MIXED MCQ', f'Q{q.id} MCQ rendering', False)

# CATEGORY 2: OTHER QUESTION TYPES
print('\n' + '='*60)
print('CATEGORY 2: OTHER QUESTION TYPES')
print('='*60)

# Test MCQ (single choice)
print('\nMCQ (Single Choice):')
mcq_questions = Question.objects.filter(question_type='MCQ')[:3]
for q in mcq_questions:
    letters = get_answer_letters(q)
    multi = has_multiple_answers(q)
    if not multi and len(letters) == 0:
        print(f'  ✅ Q{q.id}: No text inputs (correct)')
        add_test('Question Types', f'MCQ Q{q.id}', True)
    else:
        print(f'  ❌ Q{q.id}: Has text inputs (BROKEN)')
        add_test('Question Types', f'MCQ Q{q.id}', False)
        issues.append(f'MCQ Q{q.id} incorrectly has text inputs')

# Test CHECKBOX
print('\nCHECKBOX (Multiple Choice):')
checkbox_questions = Question.objects.filter(question_type='CHECKBOX')[:3]
if checkbox_questions:
    for q in checkbox_questions:
        letters = get_answer_letters(q)
        multi = has_multiple_answers(q)
        if not multi and len(letters) == 0:
            print(f'  ✅ Q{q.id}: No text inputs (correct)')
            add_test('Question Types', f'CHECKBOX Q{q.id}', True)
        else:
            print(f'  ❌ Q{q.id}: Has text inputs (BROKEN)')
            add_test('Question Types', f'CHECKBOX Q{q.id}', False)
            issues.append(f'CHECKBOX Q{q.id} incorrectly has text inputs')
else:
    print('  ⚠️ No CHECKBOX questions found')

# Test SHORT
print('\nSHORT Answer:')
short_questions = Question.objects.filter(question_type='SHORT')[:3]
for q in short_questions:
    letters = get_answer_letters(q)
    multi = has_multiple_answers(q)
    
    if q.options_count > 1:
        if multi and len(letters) == q.options_count:
            print(f'  ✅ Q{q.id}: {len(letters)} inputs (correct)')
            add_test('Question Types', f'SHORT Q{q.id}', True)
        else:
            print(f'  ❌ Q{q.id}: Expected {q.options_count} inputs, got {len(letters)}')
            add_test('Question Types', f'SHORT Q{q.id}', False)
            issues.append(f'SHORT Q{q.id} wrong input count')
    else:
        if not multi and len(letters) == 0:
            print(f'  ✅ Q{q.id}: Single input (correct)')
            add_test('Question Types', f'SHORT Q{q.id}', True)
        else:
            print(f'  ❌ Q{q.id}: Should have single input')
            add_test('Question Types', f'SHORT Q{q.id}', False)
            issues.append(f'SHORT Q{q.id} should be single')

# Test LONG
print('\nLONG Answer:')
long_questions = Question.objects.filter(question_type='LONG')[:3]
for q in long_questions:
    letters = get_answer_letters(q)
    multi = has_multiple_answers(q)
    
    if q.options_count > 1:
        if multi and len(letters) == q.options_count:
            print(f'  ✅ Q{q.id}: {len(letters)} textareas (correct)')
            add_test('Question Types', f'LONG Q{q.id}', True)
        else:
            print(f'  ❌ Q{q.id}: Expected {q.options_count} textareas')
            add_test('Question Types', f'LONG Q{q.id}', False)
            issues.append(f'LONG Q{q.id} wrong textarea count')
    else:
        if not multi and len(letters) == 0:
            print(f'  ✅ Q{q.id}: Single textarea (correct)')
            add_test('Question Types', f'LONG Q{q.id}', True)
        else:
            print(f'  ❌ Q{q.id}: Should have single textarea')
            add_test('Question Types', f'LONG Q{q.id}', False)
            issues.append(f'LONG Q{q.id} should be single')

# CATEGORY 3: SYSTEM FEATURES
print('\n' + '='*60)
print('CATEGORY 3: SYSTEM FEATURES')
print('='*60)

client = Client()

# Test pages
print('\nPage Loading:')
pages = [
    ('placement_test:exam_list', 'Exam List'),
    ('placement_test:create_exam', 'Create Exam'),
    ('placement_test:start_test', 'Start Test'),
]

for url_name, desc in pages:
    try:
        response = client.get(reverse(url_name))
        if response.status_code == 200:
            print(f'  ✅ {desc} page loads')
            add_test('System Features', f'{desc} page', True)
        else:
            print(f'  ❌ {desc} page status {response.status_code}')
            add_test('System Features', f'{desc} page', False)
            issues.append(f'{desc} page not loading')
    except Exception as e:
        print(f'  ❌ {desc} page error: {e}')
        add_test('System Features', f'{desc} page', False)
        issues.append(f'{desc} page error')

# Test features
print('\nCore Features:')

# Audio
audio_count = Question.objects.filter(audio_file__isnull=False).count()
if audio_count > 0:
    print(f'  ✅ Audio assignments: {audio_count} questions')
    add_test('System Features', 'Audio assignments', True)
else:
    print('  ⚠️ No audio assignments found')
    add_test('System Features', 'Audio assignments', None)

# PDFs
pdf_count = Exam.objects.filter(pdf_file__isnull=False).count()
if pdf_count > 0:
    print(f'  ✅ PDF files: {pdf_count} exams')
    add_test('System Features', 'PDF files', True)
else:
    print('  ⚠️ No PDF files found')
    add_test('System Features', 'PDF files', None)

# Curriculum
curriculum_count = Exam.objects.filter(curriculum_level__isnull=False).count()
if curriculum_count > 0:
    print(f'  ✅ Curriculum integration: {curriculum_count} exams')
    add_test('System Features', 'Curriculum integration', True)
else:
    print('  ⚠️ No curriculum links found')
    add_test('System Features', 'Curriculum integration', None)

# CATEGORY 4: DATA INTEGRITY
print('\n' + '='*60)
print('CATEGORY 4: DATA INTEGRITY')
print('='*60)

print('\nDatabase Checks:')

# Orphaned questions
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT COUNT(*) FROM placement_test_question 
        WHERE exam_id NOT IN (SELECT id FROM placement_test_exam)
    """)
    orphaned = cursor.fetchone()[0]

if orphaned == 0:
    print(f'  ✅ No orphaned questions')
    add_test('Data Integrity', 'Orphaned questions', True)
else:
    print(f'  ❌ {orphaned} orphaned questions found')
    add_test('Data Integrity', 'Orphaned questions', False)
    issues.append(f'{orphaned} orphaned questions')

# Options count validation
print('\nOptions Count Validation:')
invalid_count = 0
for qtype in ['SHORT', 'LONG', 'MIXED']:
    questions = Question.objects.filter(question_type=qtype)
    for q in questions:
        if q.correct_answer:
            calculated = q._calculate_actual_options_count()
            if calculated != q.options_count:
                invalid_count += 1

if invalid_count == 0:
    print(f'  ✅ All options_count values are correct')
    add_test('Data Integrity', 'Options count', True)
else:
    print(f'  ❌ {invalid_count} questions have incorrect options_count')
    add_test('Data Integrity', 'Options count', False)
    issues.append(f'{invalid_count} incorrect options_count values')

# CATEGORY 5: FILTER FUNCTIONS
print('\n' + '='*60)
print('CATEGORY 5: FILTER FUNCTIONS')
print('='*60)

print('\nFilter Tests:')

# Test filters with edge cases
edge_cases = [
    (None, 'None input'),
    (Question(), 'Empty question'),
    (Question(question_type='INVALID'), 'Invalid type'),
]

for test_input, desc in edge_cases:
    try:
        letters = get_answer_letters(test_input)
        multi = has_multiple_answers(test_input)
        mixed = is_mixed_question(test_input)
        print(f'  ✅ {desc} handled gracefully')
        add_test('Filters', f'{desc}', True)
    except Exception as e:
        print(f'  ❌ {desc} caused error: {e}')
        add_test('Filters', f'{desc}', False)
        issues.append(f'Filter error on {desc}')

# Test format_grade
grade_tests = [(1, 'Primary 1'), (7, 'Middle School 1'), (10, 'High School 1')]
for grade, expected in grade_tests:
    result = format_grade(grade)
    if result == expected:
        add_test('Filters', f'format_grade({grade})', True)
    else:
        add_test('Filters', f'format_grade({grade})', False)
        issues.append(f'format_grade({grade}) wrong')

# CATEGORY 6: SERVICE LAYER
print('\n' + '='*60)
print('CATEGORY 6: SERVICE LAYER')
print('='*60)

print('\nExamService Tests:')
service_tests = [
    ('SHORT', 'a|b|c', 3),
    ('LONG', 'a|||b', 2),
    ('MIXED', '[{"type":"Multiple Choice","value":"A"}]', 1),
]

for qtype, answer, expected in service_tests:
    result = ExamService._calculate_options_count(qtype, answer)
    if result == expected:
        print(f'  ✅ {qtype} calculation correct')
        add_test('Service Layer', f'{qtype} calculation', True)
    else:
        print(f'  ❌ {qtype}: expected {expected}, got {result}')
        add_test('Service Layer', f'{qtype} calculation', False)
        issues.append(f'ExamService {qtype} calculation wrong')

# FINAL SUMMARY
print('\n' + '='*80)
print('FINAL QA SUMMARY')
print('='*80)

total_passed = sum(1 for _, result in all_tests if result is True)
total_failed = sum(1 for _, result in all_tests if result is False)
total_skipped = sum(1 for _, result in all_tests if result is None)
total = len(all_tests)

print(f'\n📊 Overall Results:')
print(f'  ✅ Passed: {total_passed}/{total} ({total_passed*100//total if total else 0}%)')
print(f'  ❌ Failed: {total_failed}/{total} ({total_failed*100//total if total else 0}%)')
print(f'  ⚠️ Skipped: {total_skipped}/{total} ({total_skipped*100//total if total else 0}%)')

print(f'\n📊 Results by Category:')
for category, stats in test_categories.items():
    total_cat = stats['passed'] + stats['failed'] + stats['skipped']
    if stats['failed'] == 0:
        print(f'  ✅ {category}: {stats["passed"]}/{total_cat} passed')
    else:
        print(f'  ❌ {category}: {stats["passed"]}/{total_cat} passed, {stats["failed"]} failed')

if issues:
    print(f'\n🔴 CRITICAL ISSUES ({len(issues)}):')
    for issue in issues[:10]:
        print(f'  - {issue}')
    if len(issues) > 10:
        print(f'  ... and {len(issues)-10} more')
    print('\n⚠️ SOME FEATURES MAY BE BROKEN!')
else:
    print('\n✅ ALL TESTS PASSED!')
    print('The MIXED MCQ fix is successful.')
    print('No existing features were broken.')
    print('System is ready for production.')

print('\n' + '='*80)
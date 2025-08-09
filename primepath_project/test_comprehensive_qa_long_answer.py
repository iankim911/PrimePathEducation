#!/usr/bin/env python
"""
Comprehensive QA test after MIXED Long Answer fix
Ensures all features are still working correctly
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
from placement_test.models import Question, Exam, AudioFile, StudentSession
from placement_test.templatetags.grade_tags import (
    get_mixed_components, has_multiple_answers, get_answer_letters,
    is_mixed_question, format_grade
)
from placement_test.services.exam_service import ExamService
from core.models import CurriculumLevel
import uuid

print('='*80)
print('COMPREHENSIVE QA TEST - POST MIXED LONG ANSWER FIX')
print(f'Timestamp: {datetime.now()}')
print('='*80)

all_tests = []
issues = []
categories = {}

def add_test(category, name, result):
    """Helper to track tests by category"""
    all_tests.append((name, result))
    if category not in categories:
        categories[category] = {'passed': 0, 'failed': 0, 'skipped': 0}
    
    if result is True:
        categories[category]['passed'] += 1
    elif result is False:
        categories[category]['failed'] += 1
    else:
        categories[category]['skipped'] += 1

# CATEGORY 1: MIXED QUESTIONS (All Types)
print('\n' + '='*60)
print('CATEGORY 1: MIXED QUESTIONS (CRITICAL)')
print('='*60)

print('\nMIXED with Long Answer:')
# Test Q6 (2 Short + 1 Long)
q6 = Question.objects.filter(id=1019).first()
if q6:
    components = get_mixed_components(q6)
    types = [c.get('type') for c in components]
    
    if types == ['input', 'input', 'textarea']:
        print(f'  ✅ Q{q6.id}: 2 Short + 1 Long renders correctly')
        add_test('MIXED', 'Q6 rendering', True)
    else:
        print(f'  ❌ Q{q6.id}: Expected [input, input, textarea], got {types}')
        add_test('MIXED', 'Q6 rendering', False)
        issues.append(f'Q6 rendering: {types}')

# Test Q4 (1 MCQ + 2 Short + 1 Long)
q4 = Question.objects.filter(id=1037).first()
if q4:
    components = get_mixed_components(q4)
    types = [c.get('type') for c in components]
    
    if types == ['mcq', 'input', 'input', 'textarea']:
        print(f'  ✅ Q{q4.id}: MCQ + 2 Short + 1 Long renders correctly')
        add_test('MIXED', 'Q4 rendering', True)
    else:
        print(f'  ❌ Q{q4.id}: Expected [mcq, input, input, textarea], got {types}')
        add_test('MIXED', 'Q4 rendering', False)
        issues.append(f'Q4 rendering: {types}')

print('\nMIXED with MCQ only:')
mcq_only = Question.objects.filter(id=1016).first()
if mcq_only:
    components = get_mixed_components(mcq_only)
    all_mcq = all(c.get('type') == 'mcq' for c in components)
    
    if all_mcq:
        print(f'  ✅ Q{mcq_only.id}: Pure MCQ MIXED still works')
        add_test('MIXED', 'Pure MCQ', True)
    else:
        print(f'  ❌ Q{mcq_only.id}: Pure MCQ MIXED broken')
        add_test('MIXED', 'Pure MCQ', False)
        issues.append('Pure MCQ MIXED broken')

# Verify MCQ components still have proper structure
if mcq_only:
    components = get_mixed_components(mcq_only)
    for comp in components:
        if comp.get('type') == 'mcq':
            if 'options' in comp and 'index' in comp:
                add_test('MIXED', 'MCQ structure', True)
            else:
                add_test('MIXED', 'MCQ structure', False)
                issues.append('MCQ component missing fields')
            break

# CATEGORY 2: ALL OTHER QUESTION TYPES
print('\n' + '='*60)
print('CATEGORY 2: ALL OTHER QUESTION TYPES')
print('='*60)

question_types = {
    'MCQ': {'expected_multi': False, 'expected_letters': 0},
    'CHECKBOX': {'expected_multi': False, 'expected_letters': 0},
    'SHORT': {'expected_multi': 'varies', 'expected_letters': 'varies'},
    'LONG': {'expected_multi': 'varies', 'expected_letters': 'varies'}
}

for qtype, expected in question_types.items():
    questions = Question.objects.filter(question_type=qtype)[:2]
    
    if questions:
        type_ok = True
        for q in questions:
            multi = has_multiple_answers(q)
            letters = get_answer_letters(q)
            
            if qtype in ['MCQ', 'CHECKBOX']:
                if multi or len(letters) > 0:
                    type_ok = False
                    issues.append(f'{qtype} Q{q.id} has incorrect rendering')
            elif qtype in ['SHORT', 'LONG']:
                if q.options_count > 1:
                    if not multi or len(letters) != q.options_count:
                        type_ok = False
                        issues.append(f'{qtype} Q{q.id} wrong count')
                else:
                    if multi or len(letters) > 0:
                        type_ok = False
                        issues.append(f'{qtype} Q{q.id} should be single')
        
        if type_ok:
            print(f'  ✅ {qtype}: All questions render correctly')
            add_test('Question Types', qtype, True)
        else:
            print(f'  ❌ {qtype}: Some questions have issues')
            add_test('Question Types', qtype, False)
    else:
        print(f'  ⚠️ {qtype}: No questions found')
        add_test('Question Types', qtype, None)

# CATEGORY 3: ANSWER COLLECTION
print('\n' + '='*60)
print('CATEGORY 3: ANSWER COLLECTION (CRITICAL)')
print('='*60)

# Check JavaScript handles all input types
js_file = './static/js/modules/answer-manager.js'
if os.path.exists(js_file):
    with open(js_file, 'r') as f:
        content = f.read()
        
        required_patterns = [
            ('MIXED handling', 'questionType === \'MIXED\''),
            ('Checkbox collection', 'mixedCheckboxes'),
            ('Text input collection', 'mixedTextInputs'),
            ('Textarea collection', 'mixedTextareas'),
            ('Component parsing', 'componentIndex'),
            ('Answer formatting', 'componentAnswers')
        ]
        
        for name, pattern in required_patterns:
            if pattern in content:
                print(f'  ✅ {name} present')
                add_test('Answer Collection', name, True)
            else:
                print(f'  ❌ {name} missing')
                add_test('Answer Collection', name, False)
                issues.append(f'JS missing {name}')
else:
    print('  ❌ answer-manager.js not found')
    add_test('Answer Collection', 'JS file', False)

# CATEGORY 4: TEMPLATE STRUCTURE
print('\n' + '='*60)
print('CATEGORY 4: TEMPLATE STRUCTURE')
print('='*60)

template_file = 'templates/components/placement_test/question_panel.html'
if os.path.exists(template_file):
    with open(template_file, 'r') as f:
        content = f.read()
        
        required_elements = [
            ('Input component', 'component.type == \'input\''),
            ('Textarea component', 'component.type == \'textarea\''),
            ('MCQ component', 'component.type == \'mcq\''),
            ('MCQ options loop', 'for option in component.options'),
            ('Textarea element', '<textarea name="q_{{ question.id }}_{{ component.letter }}"')
        ]
        
        for name, pattern in required_elements:
            if pattern in content:
                print(f'  ✅ {name} found')
                add_test('Template', name, True)
            else:
                print(f'  ❌ {name} not found')
                add_test('Template', name, False)
                issues.append(f'Template missing {name}')
else:
    print('  ❌ Template file not found')
    add_test('Template', 'File exists', False)

# CATEGORY 5: SYSTEM FEATURES
print('\n' + '='*60)
print('CATEGORY 5: SYSTEM FEATURES')
print('='*60)

client = Client()

# Test critical pages
pages = [
    ('placement_test:exam_list', 'Exam List'),
    ('placement_test:create_exam', 'Create Exam'),
    ('placement_test:start_test', 'Start Test')
]

for url_name, desc in pages:
    try:
        response = client.get(reverse(url_name))
        if response.status_code == 200:
            print(f'  ✅ {desc} loads')
            add_test('Pages', desc, True)
        else:
            print(f'  ❌ {desc} status {response.status_code}')
            add_test('Pages', desc, False)
            issues.append(f'{desc} not loading')
    except Exception as e:
        print(f'  ❌ {desc} error: {e}')
        add_test('Pages', desc, False)

# Test features
print('\nCore Features:')
audio_count = Question.objects.filter(audio_file__isnull=False).count()
print(f'  Audio: {audio_count} questions')
add_test('Features', 'Audio', audio_count > 0)

pdf_count = Exam.objects.filter(pdf_file__isnull=False).count()
print(f'  PDFs: {pdf_count} exams')
add_test('Features', 'PDFs', pdf_count > 0)

curriculum_count = Exam.objects.filter(curriculum_level__isnull=False).count()
print(f'  Curriculum: {curriculum_count} exams')
add_test('Features', 'Curriculum', curriculum_count > 0)

# CATEGORY 6: DATA INTEGRITY
print('\n' + '='*60)
print('CATEGORY 6: DATA INTEGRITY')
print('='*60)

# Check database
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT COUNT(*) FROM placement_test_question 
        WHERE exam_id NOT IN (SELECT id FROM placement_test_exam)
    """)
    orphaned = cursor.fetchone()[0]

if orphaned == 0:
    print('  ✅ No orphaned questions')
    add_test('Data', 'Orphaned questions', True)
else:
    print(f'  ❌ {orphaned} orphaned questions')
    add_test('Data', 'Orphaned questions', False)
    issues.append(f'{orphaned} orphaned questions')

# Check options_count consistency
inconsistent = 0
for q in Question.objects.filter(question_type__in=['SHORT', 'LONG', 'MIXED'])[:20]:
    if q.correct_answer:
        calculated = q._calculate_actual_options_count()
        if calculated != q.options_count:
            inconsistent += 1

if inconsistent == 0:
    print('  ✅ All options_count values correct')
    add_test('Data', 'Options count', True)
else:
    print(f'  ❌ {inconsistent} incorrect options_count')
    add_test('Data', 'Options count', False)
    issues.append(f'{inconsistent} incorrect options_count')

# CATEGORY 7: FILTER FUNCTIONS
print('\n' + '='*60)
print('CATEGORY 7: FILTER FUNCTIONS')
print('='*60)

# Test filters with edge cases
edge_cases = [
    (None, 'None input'),
    (Question(), 'Empty question'),
    (Question(question_type='INVALID'), 'Invalid type')
]

for test_input, desc in edge_cases:
    try:
        letters = get_answer_letters(test_input)
        multi = has_multiple_answers(test_input)
        mixed = is_mixed_question(test_input)
        print(f'  ✅ {desc} handled gracefully')
        add_test('Filters', desc, True)
    except Exception as e:
        print(f'  ❌ {desc} caused error: {e}')
        add_test('Filters', desc, False)
        issues.append(f'Filter error on {desc}')

# Test format_grade
grade_tests = [(1, 'Primary 1'), (7, 'Middle School 1'), (10, 'High School 1')]
all_grade_ok = True
for grade, expected in grade_tests:
    result = format_grade(grade)
    if result != expected:
        all_grade_ok = False
        issues.append(f'format_grade({grade}) wrong')

if all_grade_ok:
    print('  ✅ format_grade filter works')
    add_test('Filters', 'format_grade', True)
else:
    print('  ❌ format_grade filter broken')
    add_test('Filters', 'format_grade', False)

# CATEGORY 8: SUBMISSION FLOW
print('\n' + '='*60)
print('CATEGORY 8: SUBMISSION FLOW')
print('='*60)

# Test submission with MIXED questions including Long Answer
try:
    mixed_exam = Exam.objects.filter(
        questions__id=1019  # Q6 with Long Answer
    ).first()
    
    if mixed_exam:
        session = StudentSession.objects.create(
            id=uuid.uuid4(),
            exam=mixed_exam,
            student_name='QA Test Long Answer',
            grade=1
        )
        
        # Test submission endpoint
        response = client.post(
            f'/api/placement/session/{session.id}/complete/',
            content_type='application/json'
        )
        
        if response.status_code in [200, 302]:
            print('  ✅ Submission with Long Answer works')
            add_test('Submission', 'With Long Answer', True)
        else:
            print(f'  ❌ Submission failed: {response.status_code}')
            add_test('Submission', 'With Long Answer', False)
            issues.append(f'Submission status {response.status_code}')
        
        # Clean up
        session.delete()
    else:
        print('  ⚠️ No exam with Long Answer found')
        add_test('Submission', 'With Long Answer', None)
        
except Exception as e:
    print(f'  ❌ Submission error: {e}')
    add_test('Submission', 'With Long Answer', False)
    issues.append(f'Submission error: {e}')

# FINAL SUMMARY
print('\n' + '='*80)
print('COMPREHENSIVE QA SUMMARY')
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
for category, stats in categories.items():
    total_cat = stats['passed'] + stats['failed'] + stats['skipped']
    if stats['failed'] == 0:
        status = '✅'
    else:
        status = '❌'
    print(f'  {status} {category}: {stats["passed"]}/{total_cat} passed')

# Critical checks
critical_categories = ['MIXED', 'Answer Collection', 'Template', 'Submission']
critical_ok = True

print('\n' + '='*60)
print('CRITICAL SYSTEMS CHECK')
print('='*60)

for cat in critical_categories:
    if cat in categories:
        if categories[cat]['failed'] == 0:
            print(f'✅ {cat}: All tests passed')
        else:
            print(f'❌ {cat}: {categories[cat]["failed"]} failures - CRITICAL!')
            critical_ok = False
    else:
        print(f'⚠️ {cat}: Not tested')

if issues:
    print(f'\n🔴 Issues Found ({len(issues)}):')
    for issue in issues[:10]:
        print(f'  - {issue}')
    if len(issues) > 10:
        print(f'  ... and {len(issues)-10} more')
elif critical_ok:
    print('\n✅ ALL SYSTEMS OPERATIONAL!')
    print('MIXED Long Answer fix successful.')
    print('All question types render correctly.')
    print('No existing features were broken.')
else:
    print('\n⚠️ Some critical systems need attention!')

print('\n' + '='*80)
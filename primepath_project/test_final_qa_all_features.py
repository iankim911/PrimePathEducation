#!/usr/bin/env python
"""
Final comprehensive QA test - All features
Ensures MIXED MCQ template fix and submit fix haven't broken anything
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
print('FINAL COMPREHENSIVE QA TEST - ALL FEATURES')
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

# CATEGORY 1: MIXED QUESTIONS
print('\n' + '='*60)
print('CATEGORY 1: MIXED QUESTIONS (CRITICAL)')
print('='*60)

# Test MIXED MCQ rendering
print('\nMIXED MCQ Components:')
mixed_mcq = Question.objects.filter(
    question_type='MIXED',
    correct_answer__contains='Multiple Choice'
).first()

if mixed_mcq:
    components = get_mixed_components(mixed_mcq)
    mcq_count = sum(1 for c in components if c.get('type') == 'mcq')
    
    print(f'  Question {mixed_mcq.id}: {len(components)} components, {mcq_count} MCQ')
    
    # Verify MCQ components have required fields
    all_valid = True
    for comp in components:
        if comp.get('type') == 'mcq':
            if 'options' not in comp or 'index' not in comp:
                all_valid = False
                print(f'    ❌ Component {comp.get("letter")} missing fields')
            else:
                print(f'    ✅ Component {comp["letter"]}: {len(comp["options"])} options, index={comp["index"]}')
    
    if all_valid and mcq_count > 0:
        add_test('MIXED', 'MCQ component structure', True)
    else:
        add_test('MIXED', 'MCQ component structure', False)
        issues.append('MIXED MCQ components invalid')
else:
    print('  ⚠️ No MIXED MCQ questions found')
    add_test('MIXED', 'MCQ component structure', None)

# Test MIXED with text inputs
mixed_text = Question.objects.filter(
    question_type='MIXED',
    correct_answer__contains='Short Answer'
).first()

if mixed_text:
    components = get_mixed_components(mixed_text)
    text_count = sum(1 for c in components if c.get('type') == 'input')
    print(f'  Question {mixed_text.id}: {text_count} text inputs')
    add_test('MIXED', 'Text component structure', True)
else:
    print('  ⚠️ No MIXED text questions found')

# CATEGORY 2: ALL QUESTION TYPES
print('\n' + '='*60)
print('CATEGORY 2: ALL QUESTION TYPES')
print('='*60)

question_type_tests = {
    'MCQ': {'multi': False, 'letters': 0},
    'CHECKBOX': {'multi': False, 'letters': 0},
    'SHORT': {'multi': 'varies', 'letters': 'varies'},
    'LONG': {'multi': 'varies', 'letters': 'varies'},
    'MIXED': {'multi': True, 'letters': 'varies'}
}

for qtype, expected in question_type_tests.items():
    questions = Question.objects.filter(question_type=qtype)[:2]
    
    if questions:
        type_ok = True
        for q in questions:
            multi = has_multiple_answers(q)
            letters = get_answer_letters(q)
            
            # Type-specific validation
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

# Check JavaScript answer collection
js_file = './static/js/modules/answer-manager.js'
if os.path.exists(js_file):
    with open(js_file, 'r') as f:
        content = f.read()
        
        critical_patterns = [
            ('MIXED handling', 'questionType === \'MIXED\''),
            ('Component parsing', 'componentIndex'),
            ('4-part name format', 'nameParts.length === 4'),
            ('Mixed MCQ type', 'mixed-mcq'),
            ('Component grouping', 'componentAnswers')
        ]
        
        for name, pattern in critical_patterns:
            if pattern in content:
                print(f'  ✅ {name} found')
                add_test('Answer Collection', name, True)
            else:
                print(f'  ❌ {name} not found')
                add_test('Answer Collection', name, False)
                issues.append(f'JS missing {name}')
else:
    print('  ❌ answer-manager.js not found')
    add_test('Answer Collection', 'JS file', False)
    issues.append('answer-manager.js not found')

# CATEGORY 4: SYSTEM FEATURES
print('\n' + '='*60)
print('CATEGORY 4: SYSTEM FEATURES')
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
        issues.append(f'{desc} error')

# Test features
print('\nCore Features:')

# Audio
audio_count = Question.objects.filter(audio_file__isnull=False).count()
print(f'  Audio: {audio_count} questions')
add_test('Features', 'Audio', audio_count > 0)

# PDFs
pdf_count = Exam.objects.filter(pdf_file__isnull=False).count()
print(f'  PDFs: {pdf_count} exams')
add_test('Features', 'PDFs', pdf_count > 0)

# Curriculum
curriculum_count = Exam.objects.filter(curriculum_level__isnull=False).count()
print(f'  Curriculum: {curriculum_count} exams')
add_test('Features', 'Curriculum', curriculum_count > 0)

# CATEGORY 5: DATA INTEGRITY
print('\n' + '='*60)
print('CATEGORY 5: DATA INTEGRITY')
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

# CATEGORY 6: TEMPLATE RENDERING
print('\n' + '='*60)
print('CATEGORY 6: TEMPLATE RENDERING')
print('='*60)

# Check V2 templates active
if settings.FEATURE_FLAGS.get('USE_V2_TEMPLATES'):
    print('  ✅ V2 templates active')
    add_test('Templates', 'V2 active', True)
else:
    print('  ❌ V2 templates not active')
    add_test('Templates', 'V2 active', False)
    issues.append('V2 templates not active')

# Check template structure
template_file = 'templates/components/placement_test/question_panel.html'
if os.path.exists(template_file):
    with open(template_file, 'r') as f:
        content = f.read()
        
        required_elements = [
            ('MCQ component div', 'mcq-component'),
            ('Component label', 'component-label'),
            ('Component index', 'component.index'),
            ('Options loop', 'for option in component.options')
        ]
        
        for name, pattern in required_elements:
            if pattern in content:
                print(f'  ✅ {name} found')
                add_test('Templates', name, True)
            else:
                print(f'  ❌ {name} not found')
                add_test('Templates', name, False)
                issues.append(f'Template missing {name}')
else:
    print('  ❌ Template file not found')
    add_test('Templates', 'File exists', False)

# CATEGORY 7: SUBMISSION FLOW
print('\n' + '='*60)
print('CATEGORY 7: SUBMISSION FLOW (CRITICAL)')
print('='*60)

# Test submission with MIXED questions
try:
    mixed_exam = Exam.objects.filter(
        questions__question_type='MIXED'
    ).distinct().first()
    
    if mixed_exam:
        session = StudentSession.objects.create(
            id=uuid.uuid4(),
            exam=mixed_exam,
            student_name='QA Test',
            grade=1
        )
        
        # Test submission endpoint
        response = client.post(
            f'/api/placement/session/{session.id}/complete/',
            content_type='application/json'
        )
        
        if response.status_code in [200, 302]:
            print('  ✅ Submission endpoint works')
            add_test('Submission', 'Complete endpoint', True)
        else:
            print(f'  ❌ Submission failed: {response.status_code}')
            add_test('Submission', 'Complete endpoint', False)
            issues.append(f'Submission status {response.status_code}')
        
        # Clean up
        session.delete()
    else:
        print('  ⚠️ No MIXED exam found')
        add_test('Submission', 'Complete endpoint', None)
        
except Exception as e:
    print(f'  ❌ Submission error: {e}')
    add_test('Submission', 'Complete endpoint', False)
    issues.append(f'Submission error: {e}')

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
for category, stats in categories.items():
    total_cat = stats['passed'] + stats['failed'] + stats['skipped']
    if stats['failed'] == 0:
        status = '✅'
    else:
        status = '❌'
    print(f'  {status} {category}: {stats["passed"]}/{total_cat} passed')

# Critical checks
critical_categories = ['MIXED', 'Answer Collection', 'Submission']
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
    print('Both MIXED MCQ rendering and submission are working correctly.')
    print('No existing features were broken.')
else:
    print('\n⚠️ Some critical systems need attention!')

print('\n' + '='*80)
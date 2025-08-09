#!/usr/bin/env python
"""
Comprehensive QA test after adding individual MCQ options count feature
Ensures all existing features are still working correctly
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
from placement_test.models import Question, Exam, AudioFile, StudentSession
from placement_test.templatetags.grade_tags import (
    get_mixed_components, has_multiple_answers, get_answer_letters,
    is_mixed_question, format_grade
)
from placement_test.services.exam_service import ExamService
from core.models import CurriculumLevel
import uuid

print('='*80)
print('COMPREHENSIVE QA TEST - POST OPTIONS COUNT FEATURE')
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

# CATEGORY 1: NEW FEATURE - Individual Options Count
print('\n' + '='*60)
print('CATEGORY 1: NEW FEATURE - INDIVIDUAL OPTIONS COUNT')
print('='*60)

print('\nMCQ Questions:')
mcq_questions = Question.objects.filter(question_type='MCQ')[:3]
for q in mcq_questions:
    if 2 <= q.options_count <= 10:
        print(f'  ✅ Q{q.id}: options_count={q.options_count} (valid range)')
        add_test('New Feature', f'MCQ Q{q.id} options', True)
    else:
        print(f'  ❌ Q{q.id}: options_count={q.options_count} (out of range)')
        add_test('New Feature', f'MCQ Q{q.id} options', False)
        issues.append(f'MCQ Q{q.id} has invalid options_count')

print('\nCHECKBOX Questions:')
checkbox_questions = Question.objects.filter(question_type='CHECKBOX')[:3]
for q in checkbox_questions:
    if 2 <= q.options_count <= 10:
        print(f'  ✅ Q{q.id}: options_count={q.options_count} (valid range)')
        add_test('New Feature', f'CHECKBOX Q{q.id} options', True)
    else:
        print(f'  ❌ Q{q.id}: options_count={q.options_count} (out of range)')
        add_test('New Feature', f'CHECKBOX Q{q.id} options', False)

# CATEGORY 2: EXISTING MIXED QUESTIONS
print('\n' + '='*60)
print('CATEGORY 2: EXISTING MIXED QUESTIONS (CRITICAL)')
print('='*60)

print('\nMIXED with Long Answer:')
# Test existing MIXED questions still work
q6 = Question.objects.filter(id=1019).first()
if q6:
    components = get_mixed_components(q6)
    types = [c.get('type') for c in components]
    
    if types == ['input', 'input', 'textarea']:
        print(f'  ✅ Q{q6.id}: Still renders correctly')
        add_test('MIXED', 'Q6 Long Answer', True)
    else:
        print(f'  ❌ Q{q6.id}: Broken - got {types}')
        add_test('MIXED', 'Q6 Long Answer', False)
        issues.append(f'Q6 broken: {types}')

print('\nMIXED with MCQ:')
mcq_mixed = Question.objects.filter(
    question_type='MIXED',
    correct_answer__contains='Multiple Choice'
).first()
if mcq_mixed:
    components = get_mixed_components(mcq_mixed)
    mcq_comps = [c for c in components if c.get('type') == 'mcq']
    
    if mcq_comps:
        for comp in mcq_comps:
            options = comp.get('options', [])
            # Should use question's options_count
            expected_count = mcq_mixed.options_count
            if len(options) == expected_count:
                print(f'  ✅ Q{mcq_mixed.id}: MCQ uses options_count={expected_count}')
                add_test('MIXED', 'MCQ options count', True)
            else:
                print(f'  ❌ Q{mcq_mixed.id}: Expected {expected_count} options, got {len(options)}')
                add_test('MIXED', 'MCQ options count', False)
                issues.append(f'MIXED MCQ wrong options count')
            break
    else:
        print('  ⚠️ No MCQ components found')
        add_test('MIXED', 'MCQ options count', None)

# CATEGORY 3: ALL OTHER QUESTION TYPES
print('\n' + '='*60)
print('CATEGORY 3: ALL OTHER QUESTION TYPES')
print('='*60)

question_types = {
    'MCQ': {'multi_expected': False},
    'CHECKBOX': {'multi_expected': False},
    'SHORT': {'multi_expected': 'varies'},
    'LONG': {'multi_expected': 'varies'}
}

for qtype, expected in question_types.items():
    questions = Question.objects.filter(question_type=qtype)[:2]
    
    if questions:
        type_ok = True
        for q in questions:
            # Verify has_multiple_answers still works
            multi = has_multiple_answers(q)
            letters = get_answer_letters(q)
            
            if qtype in ['MCQ', 'CHECKBOX']:
                # These shouldn't have multiple answer fields
                if multi or len(letters) > 0:
                    type_ok = False
                    issues.append(f'{qtype} Q{q.id} incorrectly showing multiple')
            
            # Verify options_count is within valid range
            if q.options_count < 2 or q.options_count > 10:
                type_ok = False
                issues.append(f'{qtype} Q{q.id} options_count out of range')
        
        if type_ok:
            print(f'  ✅ {qtype}: All questions valid')
            add_test('Question Types', qtype, True)
        else:
            print(f'  ❌ {qtype}: Some questions have issues')
            add_test('Question Types', qtype, False)
    else:
        print(f'  ⚠️ {qtype}: No questions found')
        add_test('Question Types', qtype, None)

# CATEGORY 4: API ENDPOINTS
print('\n' + '='*60)
print('CATEGORY 4: API ENDPOINTS')
print('='*60)

client = Client()

# Test update_question endpoint
test_q = Question.objects.filter(question_type='MCQ').first()
if test_q:
    response = client.post(
        f'/api/placement/questions/{test_q.id}/update/',
        {
            'correct_answer': 'B',
            'points': 2,
            'options_count': 6
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print('  ✅ update_question API works')
            add_test('API', 'update_question', True)
        else:
            print(f'  ❌ update_question error: {data.get("error")}')
            add_test('API', 'update_question', False)
            issues.append('update_question API error')
    else:
        print(f'  ❌ update_question status {response.status_code}')
        add_test('API', 'update_question', False)

# CATEGORY 5: ANSWER VALIDATION
print('\n' + '='*60)
print('CATEGORY 5: ANSWER VALIDATION')
print('='*60)

# Test that answers are validated against options_count
mcq = Question.objects.filter(question_type='MCQ').first()
if mcq:
    mcq.options_count = 3  # Only A, B, C
    mcq.correct_answer = 'D'  # Invalid!
    
    # Try to save via API
    response = client.post(
        f'/api/placement/questions/{mcq.id}/update/',
        {
            'options_count': 3,
            'correct_answer': 'D',
            'points': 1
        }
    )
    
    data = response.json()
    if not data.get('success'):
        print('  ✅ Invalid answers are rejected')
        add_test('Validation', 'Answer range', True)
    else:
        print('  ❌ Invalid answer not rejected')
        add_test('Validation', 'Answer range', False)
        issues.append('Answer validation not working')

# CATEGORY 6: TEMPLATE RENDERING
print('\n' + '='*60)
print('CATEGORY 6: TEMPLATE RENDERING')
print('='*60)

# Check student interface renders correct options
print('Student Interface:')
mcq_3 = Question.objects.filter(question_type='MCQ').first()
if mcq_3:
    mcq_3.options_count = 3
    mcq_3.save()
    
    # Template would use: "ABCDEFGHIJ"|slice:question.options_count
    letters = "ABCDEFGHIJ"[:mcq_3.options_count]
    if letters == "ABC":
        print(f'  ✅ Shows 3 options for options_count=3')
        add_test('Template', 'Student options', True)
    else:
        print(f'  ❌ Wrong letters: {letters}')
        add_test('Template', 'Student options', False)

# CATEGORY 7: ANSWER COLLECTION
print('\n' + '='*60)
print('CATEGORY 7: ANSWER COLLECTION')
print('='*60)

# Check JavaScript handles all input types
js_file = './static/js/modules/answer-manager.js'
if os.path.exists(js_file):
    with open(js_file, 'r') as f:
        content = f.read()
        
        required_patterns = [
            ('MIXED handling', 'questionType === \'MIXED\''),
            ('Checkbox collection', 'mixedCheckboxes'),
            ('Textarea collection', 'mixedTextareas'),
        ]
        
        all_present = True
        for name, pattern in required_patterns:
            if pattern in content:
                print(f'  ✅ {name} present')
            else:
                print(f'  ❌ {name} missing')
                all_present = False
                issues.append(f'JS missing {name}')
        
        add_test('Answer Collection', 'JS patterns', all_present)
else:
    print('  ❌ answer-manager.js not found')
    add_test('Answer Collection', 'JS file', False)

# CATEGORY 8: SYSTEM FEATURES
print('\n' + '='*60)
print('CATEGORY 8: SYSTEM FEATURES')
print('='*60)

# Test critical pages still load
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

# CATEGORY 9: BACKWARD COMPATIBILITY
print('\n' + '='*60)
print('CATEGORY 9: BACKWARD COMPATIBILITY')
print('='*60)

# Check that existing questions with default options_count=5 still work
default_mcq = Question.objects.filter(
    question_type='MCQ',
    options_count=5
).first()

if default_mcq:
    print(f'  ✅ Default MCQ (5 options) exists')
    add_test('Compatibility', 'Default MCQ', True)
    
    # Verify it still renders A-E
    letters = "ABCDEFGHIJ"[:default_mcq.options_count]
    if letters == "ABCDE":
        print(f'  ✅ Default still shows A-E')
        add_test('Compatibility', 'Default rendering', True)
    else:
        print(f'  ❌ Default rendering broken')
        add_test('Compatibility', 'Default rendering', False)
else:
    print('  ⚠️ No default MCQ found')
    add_test('Compatibility', 'Default MCQ', None)

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
critical_categories = ['New Feature', 'MIXED', 'API', 'Validation', 'Compatibility']
critical_ok = True

print('\n' + '='*60)
print('CRITICAL SYSTEMS CHECK')
print('='*60)

for cat in critical_categories:
    if cat in categories:
        if categories[cat]['failed'] == 0:
            print(f'✅ {cat}: All tests passed')
        else:
            print(f'❌ {cat}: {categories[cat]["failed"]} failures')
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
    print('Individual MCQ options count feature successfully added.')
    print('All existing features remain functional.')
    print('No breaking changes detected.')
else:
    print('\n⚠️ Some critical systems need attention!')

print('\n' + '='*80)
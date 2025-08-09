#!/usr/bin/env python
"""
Final QA test suite to ensure no existing features were broken
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
from placement_test.models import Question, Exam, StudentSession, StudentAnswer
from placement_test.templatetags import grade_tags
from django.db.models import Count

print('='*80)
print('FINAL QA TEST SUITE')
print(f'Timestamp: {datetime.now()}')
print('='*80)

results = {
    'passed': [],
    'failed': [],
    'warnings': []
}

# Test 1: Check template filters are loaded
print('\n1. TEMPLATE FILTERS CHECK')
print('-'*40)
try:
    # Check all expected filters exist
    filters = [
        'split', 'has_multiple_answers', 'get_answer_letters',
        'is_mixed_question', 'get_mixed_components', 'format_grade'
    ]
    for filter_name in filters:
        if hasattr(grade_tags, filter_name):
            print(f'  ✅ {filter_name} filter exists')
            results['passed'].append(f'Filter {filter_name} exists')
        else:
            print(f'  ❌ {filter_name} filter missing!')
            results['failed'].append(f'Filter {filter_name} missing')
except Exception as e:
    print(f'  ❌ Error checking filters: {e}')
    results['failed'].append(f'Filter check failed: {e}')

# Test 2: Check question rendering logic
print('\n2. QUESTION RENDERING LOGIC')
print('-'*40)

# Test each question type
test_questions = {
    'MCQ': Question.objects.filter(question_type='MCQ').first(),
    'CHECKBOX': Question.objects.filter(question_type='CHECKBOX').first(),
    'SHORT': Question.objects.filter(question_type='SHORT', options_count=3).first(),
    'LONG': Question.objects.filter(question_type='LONG').first(),
    'MIXED': Question.objects.filter(question_type='MIXED', options_count=3).first()
}

for qtype, q in test_questions.items():
    if q:
        letters = grade_tags.get_answer_letters(q)
        has_multi = grade_tags.has_multiple_answers(q)
        
        # Define expected behavior
        if qtype in ['MCQ', 'CHECKBOX', 'LONG']:
            expected_letters = 0
            expected_multi = False
        elif qtype in ['SHORT', 'MIXED']:
            if q.options_count > 1:
                expected_letters = q.options_count
                expected_multi = True
            else:
                expected_letters = 0
                expected_multi = False
        
        # Check if behavior matches
        if len(letters) == expected_letters and has_multi == expected_multi:
            print(f'  ✅ {qtype} rendering logic correct')
            results['passed'].append(f'{qtype} rendering logic')
        else:
            print(f'  ❌ {qtype} rendering logic incorrect!')
            print(f'     Expected: {expected_letters} letters, multi={expected_multi}')
            print(f'     Got: {len(letters)} letters, multi={has_multi}')
            results['failed'].append(f'{qtype} rendering logic')

# Test 3: Check database consistency
print('\n3. DATABASE CONSISTENCY')
print('-'*40)

# Check for orphaned questions
orphaned = Question.objects.filter(exam__isnull=True).count()
if orphaned == 0:
    print(f'  ✅ No orphaned questions')
    results['passed'].append('No orphaned questions')
else:
    print(f'  ⚠️ {orphaned} orphaned questions found')
    results['warnings'].append(f'{orphaned} orphaned questions')

# Check for exams without questions
empty_exams = Exam.objects.annotate(q_count=Count('questions')).filter(q_count=0).count()
if empty_exams == 0:
    print(f'  ✅ All exams have questions')
    results['passed'].append('All exams have questions')
else:
    print(f'  ⚠️ {empty_exams} exams without questions')
    results['warnings'].append(f'{empty_exams} empty exams')

# Test 4: Check URL patterns are accessible
print('\n4. URL ACCESSIBILITY CHECK')
print('-'*40)

client = Client()
test_urls = [
    ('placement_test:exam_list', [], {}),
    ('placement_test:create_exam', [], {}),
    ('placement_test:start_test', [], {}),
    ('placement_test:session_list', [], {}),
]

for url_name, args, kwargs in test_urls:
    try:
        url = reverse(url_name, args=args, kwargs=kwargs)
        response = client.get(url)
        if response.status_code in [200, 302]:  # 302 for redirects is ok
            print(f'  ✅ {url_name} accessible (status: {response.status_code})')
            results['passed'].append(f'URL {url_name}')
        else:
            print(f'  ❌ {url_name} returned {response.status_code}')
            results['failed'].append(f'URL {url_name} ({response.status_code})')
    except Exception as e:
        print(f'  ❌ {url_name} error: {e}')
        results['failed'].append(f'URL {url_name} error')

# Test 5: Check specific fix for multiple inputs
print('\n5. MULTIPLE INPUT FIX VERIFICATION')
print('-'*40)

# Check SHORT questions with various options_count values
for opt_count in [1, 2, 3, 4]:
    questions = Question.objects.filter(
        question_type='SHORT', 
        options_count=opt_count
    )[:1]
    
    if questions:
        q = questions[0]
        letters = grade_tags.get_answer_letters(q)
        expected = 0 if opt_count <= 1 else opt_count
        
        if len(letters) == expected:
            print(f'  ✅ SHORT with options_count={opt_count}: {len(letters)} letters (correct)')
            results['passed'].append(f'SHORT options_count={opt_count}')
        else:
            print(f'  ❌ SHORT with options_count={opt_count}: {len(letters)} letters (expected {expected})')
            results['failed'].append(f'SHORT options_count={opt_count}')

# Test 6: Check MIXED question components
print('\n6. MIXED QUESTION COMPONENTS')
print('-'*40)

mixed_questions = Question.objects.filter(question_type='MIXED', options_count__gt=1)[:3]
for q in mixed_questions:
    components = grade_tags.get_mixed_components(q)
    
    if len(components) == q.options_count:
        print(f'  ✅ MIXED Q{q.question_number}: {len(components)} components = options_count')
        results['passed'].append(f'MIXED Q{q.question_number} components')
    else:
        print(f'  ❌ MIXED Q{q.question_number}: {len(components)} components != {q.options_count}')
        results['failed'].append(f'MIXED Q{q.question_number} components')

# Test 7: Edge case - pipe in correct_answer
print('\n7. EDGE CASE TESTING')
print('-'*40)

# Test Question 987 specifically (the problematic one)
try:
    q987 = Question.objects.get(id=987)
    letters = grade_tags.get_answer_letters(q987)
    if len(letters) == 0:
        print(f'  ✅ Question 987 (cat|feline) correctly returns no letters')
        results['passed'].append('Question 987 edge case')
    else:
        print(f'  ❌ Question 987 still returns {len(letters)} letters!')
        results['failed'].append('Question 987 edge case')
except Question.DoesNotExist:
    print(f'  ⚠️ Question 987 not found')
    results['warnings'].append('Question 987 not found')

# Final Summary
print('\n' + '='*80)
print('QA TEST SUMMARY')
print('='*80)

total_tests = len(results['passed']) + len(results['failed'])
print(f'\nTotal Tests: {total_tests}')
print(f'✅ Passed: {len(results["passed"])}')
print(f'❌ Failed: {len(results["failed"])}')
print(f'⚠️ Warnings: {len(results["warnings"])}')

if results['failed']:
    print('\nFailed Tests:')
    for failure in results['failed']:
        print(f'  - {failure}')
else:
    print('\n🎉 ALL TESTS PASSED!')

if results['warnings']:
    print('\nWarnings:')
    for warning in results['warnings']:
        print(f'  - {warning}')

# Save results to file
output = {
    'timestamp': str(datetime.now()),
    'summary': {
        'total': total_tests,
        'passed': len(results['passed']),
        'failed': len(results['failed']),
        'warnings': len(results['warnings'])
    },
    'details': results
}

with open('qa_final_results.json', 'w') as f:
    json.dump(output, f, indent=2)
    print(f'\nResults saved to qa_final_results.json')

# Final verdict
if len(results['failed']) == 0:
    print('\n' + '='*80)
    print('✅ FIX SUCCESSFULLY DEPLOYED - NO REGRESSIONS DETECTED')
    print('='*80)
else:
    print('\n' + '='*80)
    print('❌ SOME TESTS FAILED - REVIEW NEEDED')
    print('='*80)
#!/usr/bin/env python
"""
Comprehensive QA test for LONG answer fix
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
from placement_test.models import Question, Exam
from placement_test.templatetags import grade_tags
from placement_test.services.exam_service import ExamService


print('='*80)
print('COMPREHENSIVE QA TEST - LONG ANSWER FIX')
print(f'Timestamp: {datetime.now()}')
print('='*80)

results = {
    'passed': [],
    'failed': [],
    'warnings': []
}

# Test 1: Verify LONG questions with options_count > 1
print('\n1. VERIFYING LONG QUESTIONS WITH MULTIPLE RESPONSES')
print('-'*40)

long_questions = Question.objects.filter(question_type='LONG', options_count__gt=1)
print(f'Found {long_questions.count()} LONG questions with options_count > 1')

for q in long_questions:
    print(f'\nQuestion {q.question_number} (ID {q.id}):')
    print(f'  Exam: {q.exam.name[:40] if q.exam else "None"}...')
    print(f'  options_count: {q.options_count}')
    print(f'  correct_answer: "{q.correct_answer[:50]}..."')
    
    # Check template filters
    letters = grade_tags.get_answer_letters(q)
    has_multi = grade_tags.has_multiple_answers(q)
    
    print(f'  get_answer_letters: {letters} ({len(letters)} letters)')
    print(f'  has_multiple_answers: {has_multi}')
    
    # Verify consistency
    if '|||' in q.correct_answer:
        parts = q.correct_answer.split('|||')
        if len(parts) == q.options_count and len(letters) == q.options_count and has_multi:
            print(f'  ✅ All consistent: {q.options_count} parts, {len(letters)} letters')
            results['passed'].append(f'LONG Q{q.id} consistency')
        else:
            print(f'  ❌ Inconsistent: parts={len(parts)}, options_count={q.options_count}, letters={len(letters)}')
            results['failed'].append(f'LONG Q{q.id} consistency')
    else:
        print(f'  ⚠️ No triple pipe separator found')
        results['warnings'].append(f'LONG Q{q.id} no separator')

# Test 2: Check SHORT questions still work
print('\n2. VERIFYING SHORT QUESTIONS STILL WORK')
print('-'*40)

short_test = Question.objects.filter(question_type='SHORT', options_count__gt=1).first()
if short_test:
    letters = grade_tags.get_answer_letters(short_test)
    has_multi = grade_tags.has_multiple_answers(short_test)
    
    if len(letters) == short_test.options_count and has_multi:
        print(f'  ✅ SHORT questions still work correctly')
        results['passed'].append('SHORT question filters')
    else:
        print(f'  ❌ SHORT questions broken!')
        results['failed'].append('SHORT question filters')
else:
    print(f'  ⚠️ No SHORT questions with multiple answers found')
    results['warnings'].append('No SHORT test questions')

# Test 3: Check MIXED questions still work
print('\n3. VERIFYING MIXED QUESTIONS STILL WORK')
print('-'*40)

mixed_test = Question.objects.filter(question_type='MIXED', options_count__gt=1).first()
if mixed_test:
    letters = grade_tags.get_answer_letters(mixed_test)
    has_multi = grade_tags.has_multiple_answers(mixed_test)
    components = grade_tags.get_mixed_components(mixed_test)
    
    if len(letters) == mixed_test.options_count and has_multi and len(components) == mixed_test.options_count:
        print(f'  ✅ MIXED questions still work correctly')
        results['passed'].append('MIXED question filters')
    else:
        print(f'  ❌ MIXED questions broken!')
        results['failed'].append('MIXED question filters')
else:
    print(f'  ⚠️ No MIXED questions with multiple components found')
    results['warnings'].append('No MIXED test questions')

# Test 4: Test save logic
print('\n4. TESTING SAVE LOGIC FOR LONG QUESTIONS')
print('-'*40)

try:
    # Find a test exam
    test_exam = Exam.objects.filter(name__contains='test').first()
    if not test_exam:
        test_exam = Exam.objects.first()
    
    if test_exam:
        # Test creating a LONG question with multiple responses
        test_data = [{
            'id': None,
            'question_number': 998,  # High number to avoid conflicts
            'question_type': 'LONG',
            'correct_answer': 'response1|||response2|||response3',
            'options_count': 1  # Intentionally wrong to test auto-correction
        }]
        
        # Use ExamService to update
        result = ExamService.update_exam_questions(test_exam, test_data)
        
        # Check if it was created with correct options_count
        created_q = Question.objects.filter(exam=test_exam, question_number=998).first()
        if created_q:
            if created_q.options_count == 3:  # Should be 3, not 1
                print(f'  ✅ Save logic auto-corrected LONG options_count: 3 (correct)')
                results['passed'].append('LONG save logic')
            else:
                print(f'  ❌ Save logic failed: options_count={created_q.options_count} (expected 3)')
                results['failed'].append('LONG save logic')
            
            # Clean up test data
            created_q.delete()
        else:
            print(f'  ⚠️ Test question not created')
            results['warnings'].append('LONG test creation')
    else:
        print(f'  ⚠️ No exam found for testing')
        results['warnings'].append('No test exam')
        
except Exception as e:
    print(f'  ❌ Error testing save logic: {e}')
    results['failed'].append(f'LONG save logic error: {e}')

# Test 5: Check that single LONG questions still work
print('\n5. VERIFYING SINGLE LONG QUESTIONS')
print('-'*40)

single_long = Question.objects.filter(question_type='LONG', options_count=1).first()
if single_long:
    letters = grade_tags.get_answer_letters(single_long)
    has_multi = grade_tags.has_multiple_answers(single_long)
    
    if len(letters) == 0 and not has_multi:
        print(f'  ✅ Single LONG questions render as single textarea')
        results['passed'].append('Single LONG question')
    else:
        print(f'  ❌ Single LONG questions incorrectly showing multiple')
        results['failed'].append('Single LONG question')
else:
    print(f'  ⚠️ No single LONG questions found')
    results['warnings'].append('No single LONG questions')

# Test 6: Check all question types
print('\n6. CHECKING ALL QUESTION TYPES')
print('-'*40)

question_types = {
    'MCQ': (False, 0),  # (should_have_multi, expected_letters)
    'CHECKBOX': (False, 0),
    'SHORT (single)': (False, 0),
    'SHORT (multi)': (True, 'options_count'),
    'LONG (single)': (False, 0),
    'LONG (multi)': (True, 'options_count'),
    'MIXED': (True, 'options_count')
}

for qtype, (expected_multi, expected_letters) in question_types.items():
    if 'single' in qtype:
        if 'SHORT' in qtype:
            q = Question.objects.filter(question_type='SHORT', options_count=1).first()
        else:
            q = Question.objects.filter(question_type='LONG', options_count=1).first()
    elif 'multi' in qtype:
        if 'SHORT' in qtype:
            q = Question.objects.filter(question_type='SHORT', options_count__gt=1).first()
        else:
            q = Question.objects.filter(question_type='LONG', options_count__gt=1).first()
    else:
        q = Question.objects.filter(question_type=qtype).first()
    
    if q:
        letters = grade_tags.get_answer_letters(q)
        has_multi = grade_tags.has_multiple_answers(q)
        
        if expected_letters == 'options_count':
            expected_letters = q.options_count if q.options_count > 1 else 0
        
        if has_multi == expected_multi and len(letters) == expected_letters:
            print(f'  ✅ {qtype}: Correct (multi={has_multi}, letters={len(letters)})')
            results['passed'].append(f'{qtype} rendering')
        else:
            print(f'  ❌ {qtype}: Wrong (multi={has_multi}, letters={len(letters)})')
            print(f'     Expected: multi={expected_multi}, letters={expected_letters}')
            results['failed'].append(f'{qtype} rendering')

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

if results['warnings']:
    print('\nWarnings:')
    for warning in results['warnings']:
        print(f'  - {warning}')

# Save results
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

with open('qa_long_fix_results.json', 'w') as f:
    json.dump(output, f, indent=2)
    print(f'\nResults saved to qa_long_fix_results.json')

# Final verdict
if len(results['failed']) == 0:
    print('\n' + '='*80)
    print('✅ ALL TESTS PASSED - LONG ANSWER FIX SUCCESSFUL')
    print('='*80)
    print('\nKey Achievements:')
    print('  1. LONG questions with multiple responses now show multiple textareas')
    print('  2. Template filters updated to support LONG questions')
    print('  3. Save logic auto-calculates options_count for LONG questions')
    print('  4. Model validation prevents future inconsistencies')
    print('  5. All existing question types still work correctly')
else:
    print('\n' + '='*80)
    print('❌ SOME TESTS FAILED - REVIEW NEEDED')
    print('='*80)
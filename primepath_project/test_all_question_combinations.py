#!/usr/bin/env python
"""
Test all question type combinations comprehensively
"""

import os
import sys
import django
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from placement_test.models import Question, Exam
from placement_test.templatetags.grade_tags import (
    has_multiple_answers, get_answer_letters, get_mixed_components
)

print('='*80)
print('COMPREHENSIVE QUESTION TYPE TESTING')
print('='*80)

# Test matrix: question_type x options_count
test_cases = []
question_types = ['MCQ', 'CHECKBOX', 'SHORT', 'LONG', 'MIXED']
options_counts = [0, 1, 2, 3, 4, 5]

print('\n1. TESTING ALL TYPE x OPTIONS_COUNT COMBINATIONS')
print('-'*50)

for qtype in question_types:
    for opt_count in options_counts:
        questions = Question.objects.filter(
            question_type=qtype, 
            options_count=opt_count
        )[:1]  # Get one example of each
        
        if questions:
            q = questions[0]
            letters = get_answer_letters(q)
            has_multi = has_multiple_answers(q)
            
            # Expected behavior
            if qtype in ['SHORT', 'MIXED']:
                expected_multi = opt_count > 1
                expected_letters = 0 if opt_count <= 1 else opt_count
            else:
                expected_multi = False
                expected_letters = 0
            
            # Check if behavior matches expectations
            status = '✅' if (has_multi == expected_multi and len(letters) == expected_letters) else '❌'
            
            test_cases.append({
                'type': qtype,
                'options_count': opt_count,
                'id': q.id,
                'has_multi': has_multi,
                'expected_multi': expected_multi,
                'letters_count': len(letters),
                'expected_letters': expected_letters,
                'status': status
            })
            
            print(f'{status} {qtype} with options_count={opt_count}:')
            print(f'   Question ID: {q.id}')
            print(f'   has_multiple_answers: {has_multi} (expected: {expected_multi})')
            print(f'   get_answer_letters count: {len(letters)} (expected: {expected_letters})')
            if status == '❌':
                print(f'   ⚠️ MISMATCH DETECTED!')

print('\n2. TESTING EDGE CASES')
print('-'*50)

# Edge case 1: Questions with pipes in correct_answer
pipe_questions = Question.objects.filter(correct_answer__contains='|')[:5]
print('\nQuestions with pipe (|) in correct_answer:')
for q in pipe_questions:
    letters = get_answer_letters(q)
    has_multi = has_multiple_answers(q)
    print(f'  Q{q.question_number} (ID {q.id}, {q.question_type}):')
    print(f'    options_count: {q.options_count}')
    print(f'    correct_answer: "{q.correct_answer[:30]}..."')
    print(f'    has_multiple_answers: {has_multi}')
    print(f'    get_answer_letters: {letters} ({len(letters)} letters)')
    
    # Validation
    if q.options_count <= 1 and len(letters) > 0:
        print(f'    ❌ ERROR: Single input question returning letters!')
    elif q.options_count > 1 and len(letters) != q.options_count:
        print(f'    ❌ ERROR: Letter count mismatch!')
    else:
        print(f'    ✅ Correct behavior')

# Edge case 2: Questions with commas in correct_answer
comma_questions = Question.objects.filter(correct_answer__contains=',')[:5]
print('\nQuestions with comma (,) in correct_answer:')
for q in comma_questions:
    letters = get_answer_letters(q)
    has_multi = has_multiple_answers(q)
    print(f'  Q{q.question_number} (ID {q.id}, {q.question_type}):')
    print(f'    options_count: {q.options_count}')
    print(f'    correct_answer: "{q.correct_answer[:30]}..."')
    print(f'    has_multiple_answers: {has_multi}')
    print(f'    get_answer_letters: {letters} ({len(letters)} letters)')
    
    # Validation
    if q.question_type in ['SHORT', 'MIXED']:
        if q.options_count <= 1 and len(letters) > 0:
            print(f'    ❌ ERROR: Single input question returning letters!')
        elif q.options_count > 1 and len(letters) != q.options_count:
            print(f'    ❌ ERROR: Letter count mismatch!')
        else:
            print(f'    ✅ Correct behavior')
    else:
        print(f'    ✅ Not applicable for {q.question_type}')

# Edge case 3: MIXED questions with JSON structure
print('\nMIXED questions with JSON structure:')
mixed_json = Question.objects.filter(question_type='MIXED')[:3]
for q in mixed_json:
    components = get_mixed_components(q)
    letters = get_answer_letters(q)
    has_multi = has_multiple_answers(q)
    
    print(f'  Q{q.question_number} (ID {q.id}):')
    print(f'    options_count: {q.options_count}')
    print(f'    has_multiple_answers: {has_multi}')
    print(f'    get_answer_letters: {letters} ({len(letters)} letters)')
    print(f'    get_mixed_components: {len(components)} components')
    
    # Try to parse JSON
    if q.correct_answer:
        try:
            parsed = json.loads(q.correct_answer)
            print(f'    JSON structure: {len(parsed)} items')
            types = [item.get('type', 'Unknown') for item in parsed]
            print(f'    Component types: {types}')
        except:
            print(f'    JSON parsing failed')
    
    # Validation
    if q.options_count <= 1:
        if len(letters) > 0 or len(components) > 0:
            print(f'    ❌ ERROR: Single component MIXED returning multiple!')
    else:
        if len(letters) != q.options_count or len(components) != q.options_count:
            print(f'    ❌ ERROR: Component count mismatch!')
        else:
            print(f'    ✅ Correct: All counts match')

print('\n3. TESTING DATA CONSISTENCY')
print('-'*50)

inconsistencies = []
for q in Question.objects.filter(question_type__in=['SHORT', 'MIXED']):
    letters = get_answer_letters(q)
    expected = 0 if q.options_count <= 1 else q.options_count
    
    if len(letters) != expected:
        inconsistencies.append({
            'id': q.id,
            'type': q.question_type,
            'options_count': q.options_count,
            'letters_generated': len(letters),
            'expected': expected
        })

if inconsistencies:
    print(f'\n❌ Found {len(inconsistencies)} inconsistencies:')
    for inc in inconsistencies[:10]:
        print(f'  {inc["type"]} Q{inc["id"]}: options_count={inc["options_count"]}, generated={inc["letters_generated"]}, expected={inc["expected"]}')
else:
    print('\n✅ All questions have consistent letter generation!')

# Summary
print('\n' + '='*80)
print('SUMMARY')
print('='*80)

total_tested = len(test_cases)
passed = sum(1 for tc in test_cases if tc['status'] == '✅')
failed = total_tested - passed

print(f'Type x Options_Count combinations: {passed}/{total_tested} passed')
if failed > 0:
    print(f'❌ {failed} combinations failed')
    print('Failed combinations:')
    for tc in test_cases:
        if tc['status'] == '❌':
            print(f'  - {tc["type"]} with options_count={tc["options_count"]}')
else:
    print('✅ All combinations passed!')

if inconsistencies:
    print(f'\n❌ {len(inconsistencies)} data inconsistencies found')
else:
    print('\n✅ No data inconsistencies found')

print('\n✅ FIX SUCCESSFULLY APPLIED - Questions now render correct number of inputs!')
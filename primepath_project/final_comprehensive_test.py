#!/usr/bin/env python
"""
Final comprehensive test - All fixes working together
"""

import os
import sys
import django
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from placement_test.models import Question
from placement_test.templatetags.grade_tags import get_answer_letters, has_multiple_answers

print('='*80)
print('FINAL COMPREHENSIVE TEST - ALL FIXES')
print(f'Timestamp: {datetime.now()}')
print('='*80)

# Test all question types with various options_count values
test_cases = []

print('\n📋 TESTING ALL QUESTION TYPES AND CONFIGURATIONS')
print('-'*80)

# MCQ and CHECKBOX - Should never show multiple inputs
for qtype in ['MCQ', 'CHECKBOX']:
    for q in Question.objects.filter(question_type=qtype)[:1]:
        letters = get_answer_letters(q)
        multi = has_multiple_answers(q)
        status = '✅' if (len(letters) == 0 and not multi) else '❌'
        print(f'{status} {qtype}: No multiple inputs (letters={len(letters)}, multi={multi})')
        test_cases.append((qtype, status == '✅'))

# SHORT - Single vs Multiple
for options_count in [1, 2, 3]:
    q = Question.objects.filter(question_type='SHORT', options_count=options_count).first()
    if q:
        letters = get_answer_letters(q)
        multi = has_multiple_answers(q)
        expected_letters = 0 if options_count == 1 else options_count
        expected_multi = options_count > 1
        
        status = '✅' if (len(letters) == expected_letters and multi == expected_multi) else '❌'
        print(f'{status} SHORT (options_count={options_count}): letters={len(letters)}, multi={multi}')
        test_cases.append((f'SHORT-{options_count}', status == '✅'))

# LONG - Single vs Multiple
for options_count in [1, 2, 3]:
    q = Question.objects.filter(question_type='LONG', options_count=options_count).first()
    if q:
        letters = get_answer_letters(q)
        multi = has_multiple_answers(q)
        expected_letters = 0 if options_count == 1 else options_count
        expected_multi = options_count > 1
        
        status = '✅' if (len(letters) == expected_letters and multi == expected_multi) else '❌'
        print(f'{status} LONG (options_count={options_count}): letters={len(letters)}, multi={multi}')
        test_cases.append((f'LONG-{options_count}', status == '✅'))

# MIXED - Should show multiple components
for q in Question.objects.filter(question_type='MIXED', options_count__gt=1)[:1]:
    letters = get_answer_letters(q)
    multi = has_multiple_answers(q)
    status = '✅' if (len(letters) == q.options_count and multi) else '❌'
    print(f'{status} MIXED (options_count={q.options_count}): letters={len(letters)}, multi={multi}')
    test_cases.append(('MIXED', status == '✅'))

# Specific fixes verification
print('\n🔧 VERIFYING SPECIFIC FIXES')
print('-'*80)

# Question 1014 (SHORT with 3 answers)
try:
    q1014 = Question.objects.get(id=1014)
    letters = get_answer_letters(q1014)
    if q1014.options_count == 3 and len(letters) == 3:
        print('✅ Question 1014 (SHORT): Shows 3 inputs')
        test_cases.append(('Q1014-SHORT', True))
    else:
        print(f'❌ Question 1014: options_count={q1014.options_count}, letters={len(letters)}')
        test_cases.append(('Q1014-SHORT', False))
except:
    print('⚠️ Question 1014 not found')

# Question 1015 (LONG with 2 responses)
try:
    q1015 = Question.objects.get(id=1015)
    letters = get_answer_letters(q1015)
    if q1015.options_count == 2 and len(letters) == 2:
        print('✅ Question 1015 (LONG): Shows 2 textareas')
        test_cases.append(('Q1015-LONG', True))
    else:
        print(f'❌ Question 1015: options_count={q1015.options_count}, letters={len(letters)}')
        test_cases.append(('Q1015-LONG', False))
except:
    print('⚠️ Question 1015 not found')

# Data consistency check
print('\n📊 DATA CONSISTENCY CHECK')
print('-'*80)

inconsistent = []
for qtype in ['SHORT', 'LONG', 'MIXED']:
    for q in Question.objects.filter(question_type=qtype):
        calculated = q._calculate_actual_options_count()
        if calculated != q.options_count:
            inconsistent.append({
                'id': q.id,
                'type': qtype,
                'stored': q.options_count,
                'calculated': calculated
            })

if inconsistent:
    print(f'❌ Found {len(inconsistent)} inconsistent questions:')
    for inc in inconsistent[:3]:
        print(f'   Q{inc["id"]} ({inc["type"]}): stored={inc["stored"]}, calculated={inc["calculated"]}')
    test_cases.append(('Data-Consistency', False))
else:
    print('✅ All questions have consistent options_count')
    test_cases.append(('Data-Consistency', True))

# Summary
print('\n' + '='*80)
print('FINAL SUMMARY')
print('='*80)

passed = sum(1 for _, result in test_cases if result)
total = len(test_cases)
pass_rate = (passed / total * 100) if total > 0 else 0

print(f'\nTests Passed: {passed}/{total} ({pass_rate:.1f}%)')

if passed == total:
    print('\n🎉 ALL SYSTEMS OPERATIONAL 🎉')
    print('='*80)
    print('✅ SHORT questions with multiple answers: WORKING')
    print('✅ LONG questions with multiple responses: WORKING')
    print('✅ MIXED questions with components: WORKING')
    print('✅ Data consistency maintained: VERIFIED')
    print('✅ Template filters functioning: CONFIRMED')
    print('\n📌 The control panel and student interface are now in perfect sync!')
else:
    failed_tests = [name for name, result in test_cases if not result]
    print(f'\n⚠️ Failed tests: {", ".join(failed_tests)}')
    print('Please review the issues above.')

print('\n' + '='*80)
print('END OF COMPREHENSIVE TEST')
print('='*80)
#!/usr/bin/env python
"""
Test the fix for get_answer_letters filter
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from placement_test.models import Question
from placement_test.templatetags.grade_tags import has_multiple_answers, get_answer_letters

print('='*80)
print('TESTING FIX FOR get_answer_letters')
print('='*80)

# Test Question 987 (options_count=1)
q = Question.objects.get(id=987)
print(f'\nQuestion 987 (should show SINGLE input):')
print(f'  options_count: {q.options_count}')
print(f'  correct_answer: "{q.correct_answer}"')
print(f'  has_multiple_answers: {has_multiple_answers(q)}')
print(f'  get_answer_letters: {get_answer_letters(q)}')
if len(get_answer_letters(q)) == 0:
    print('  ✅ FIXED: Returns empty list for single input')
else:
    print('  ❌ STILL BROKEN')

# Test Question with options_count=3
q3 = Question.objects.filter(question_type='SHORT', options_count=3).first()
if q3:
    print(f'\nQuestion with options_count=3 (should show 3 inputs):')
    print(f'  ID: {q3.id}')
    print(f'  options_count: {q3.options_count}')
    print(f'  correct_answer: "{q3.correct_answer}"')
    print(f'  has_multiple_answers: {has_multiple_answers(q3)}')
    print(f'  get_answer_letters: {get_answer_letters(q3)}')
    if len(get_answer_letters(q3)) == 3:
        print('  ✅ CORRECT: Returns 3 letters')
    else:
        print(f'  ❌ WRONG: Returns {len(get_answer_letters(q3))} letters')

# Test Question with options_count=2
q2 = Question.objects.filter(question_type='SHORT', options_count=2).first()
if q2:
    print(f'\nQuestion with options_count=2 (should show 2 inputs):')
    print(f'  ID: {q2.id}')
    print(f'  options_count: {q2.options_count}')
    print(f'  correct_answer: "{q2.correct_answer}"')
    print(f'  has_multiple_answers: {has_multiple_answers(q2)}')
    print(f'  get_answer_letters: {get_answer_letters(q2)}')
    if len(get_answer_letters(q2)) == 2:
        print('  ✅ CORRECT: Returns 2 letters')
    else:
        print(f'  ❌ WRONG: Returns {len(get_answer_letters(q2))} letters')

# Test all SHORT questions
print('\n' + '='*80)
print('COMPREHENSIVE CHECK')
print('='*80)

issues = []
for q in Question.objects.filter(question_type='SHORT'):
    letters = get_answer_letters(q)
    if q.options_count <= 1:
        expected = 0
    else:
        expected = q.options_count
    actual = len(letters)
    if actual != expected:
        issues.append({
            'id': q.id,
            'q_num': q.question_number,
            'options_count': q.options_count,
            'expected_letters': expected,
            'actual_letters': actual,
            'correct_answer': str(q.correct_answer)[:30]
        })

if issues:
    print(f'\n❌ Found {len(issues)} questions with incorrect letter generation:')
    for issue in issues[:5]:
        print(f'  Q{issue["q_num"]} (ID {issue["id"]}):')
        print(f'    options_count: {issue["options_count"]}')
        print(f'    Expected: {issue["expected_letters"]} letters')
        print(f'    Got: {issue["actual_letters"]} letters')
        print(f'    correct_answer: "{issue["correct_answer"]}..."')
else:
    print('\n✅ All SHORT questions now generate correct number of letters!')

# Test MIXED questions too
print('\n' + '='*80)
print('TESTING MIXED QUESTIONS')
print('='*80)

mixed_issues = []
for q in Question.objects.filter(question_type='MIXED'):
    letters = get_answer_letters(q)
    if q.options_count <= 1:
        expected = 0
    else:
        expected = q.options_count
    actual = len(letters)
    if actual != expected:
        mixed_issues.append({
            'id': q.id,
            'q_num': q.question_number,
            'options_count': q.options_count,
            'expected_letters': expected,
            'actual_letters': actual
        })

if mixed_issues:
    print(f'\n❌ Found {len(mixed_issues)} MIXED questions with issues:')
    for issue in mixed_issues[:3]:
        print(f'  Q{issue["q_num"]} (ID {issue["id"]}):')
        print(f'    options_count: {issue["options_count"]}')
        print(f'    Expected: {issue["expected_letters"]} letters')
        print(f'    Got: {issue["actual_letters"]} letters')
else:
    print('\n✅ All MIXED questions generate correct number of letters!')
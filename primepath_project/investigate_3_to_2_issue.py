#!/usr/bin/env python
"""
Deep investigation: Why does options_count=3 only show 2 inputs?
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from placement_test.models import Question, Exam
from placement_test.templatetags.grade_tags import get_answer_letters, has_multiple_answers

print('='*80)
print('DEEP INVESTIGATION: WHERE DOES 3 BECOME 2?')
print('='*80)

# Find SHORT questions with options_count=3
short_3_questions = Question.objects.filter(
    question_type='SHORT',
    options_count=3
)

print(f'\nFound {short_3_questions.count()} SHORT questions with options_count=3')

for short_3 in short_3_questions[:5]:  # Check first 5
    print(f'\n{"="*40}')
    print(f'Question ID: {short_3.id}')
    print(f'  Exam: {short_3.exam.name[:30] if short_3.exam else "None"}...')
    print(f'  Question Number: {short_3.question_number}')
    print(f'  Type: {short_3.question_type}')
    print(f'  Options Count: {short_3.options_count}')
    print(f'  Correct Answer RAW: "{short_3.correct_answer}"')
    
    # Test our filters
    print(f'\nFilter Results:')
    has_multi = has_multiple_answers(short_3)
    letters = get_answer_letters(short_3)
    print(f'  has_multiple_answers: {has_multi}')
    print(f'  get_answer_letters: {letters}')
    print(f'  Letter count: {len(letters)}')
    
    if len(letters) != short_3.options_count:
        print(f'\n❌ PROBLEM FOUND!')
        print(f'   Expected: {short_3.options_count} letters')
        print(f'   Got: {len(letters)} letters')
        print(f'   Missing: {short_3.options_count - len(letters)} input(s)')
    else:
        print(f'✅ Correct: {len(letters)} letters match options_count')

# Now let's trace through the actual filter code logic
print('\n' + '='*80)
print('TRACING get_answer_letters LOGIC')
print('='*80)

# Import the actual function to inspect
from placement_test.templatetags import grade_tags
import inspect

# Get the source code
source = inspect.getsource(grade_tags.get_answer_letters)
print('\nCurrent get_answer_letters implementation:')
print(source[:500] + '...')  # First 500 chars

# Test specific scenarios
print('\n' + '='*80)
print('TESTING SPECIFIC SCENARIOS')
print('='*80)

# Scenario 1: SHORT with options_count=3 and empty correct_answer
test_cases = [
    {'options_count': 3, 'correct_answer': '', 'expected': ['A', 'B', 'C']},
    {'options_count': 3, 'correct_answer': 'A,B,C', 'expected': ['A', 'B', 'C']},
    {'options_count': 3, 'correct_answer': 'B,C', 'expected': ['A', 'B', 'C']},  # Should use options_count!
    {'options_count': 2, 'correct_answer': 'B,C', 'expected': ['A', 'B']},
]

for i, case in enumerate(test_cases, 1):
    print(f'\nTest Case {i}:')
    print(f'  options_count: {case["options_count"]}')
    print(f'  correct_answer: "{case["correct_answer"]}"')
    print(f'  Expected: {case["expected"]}')
    
    # Create a mock question
    q = Question()
    q.question_type = 'SHORT'
    q.options_count = case['options_count']
    q.correct_answer = case['correct_answer']
    
    result = get_answer_letters(q)
    print(f'  Got: {result}')
    
    if result == case['expected']:
        print('  ✅ PASS')
    else:
        print('  ❌ FAIL - This is the bug!')

# Check the actual database for problematic patterns
print('\n' + '='*80)
print('DATABASE PATTERNS ANALYSIS')
print('='*80)

# Pattern 1: SHORT with options_count > len(correct_answer parts)
problematic = Question.objects.filter(
    question_type='SHORT',
    options_count__gt=1
)

issues = []
for q in problematic[:20]:
    letters = get_answer_letters(q)
    if len(letters) != q.options_count:
        issues.append({
            'id': q.id,
            'options_count': q.options_count,
            'correct_answer': q.correct_answer[:30] if q.correct_answer else '',
            'letters_generated': letters
        })

if issues:
    print(f'\n⚠️ Found {len(issues)} questions with mismatched letter generation:')
    for issue in issues[:5]:
        print(f'  Q{issue["id"]}: options_count={issue["options_count"]}, letters={issue["letters_generated"]}')
        print(f'    correct_answer: "{issue["correct_answer"]}"')
else:
    print('\n✅ No mismatches found in database')
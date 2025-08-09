#!/usr/bin/env python
"""
Find questions where options_count doesn't match rendered inputs
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
print('FINDING PROBLEMATIC QUESTIONS')
print('='*80)

# Check ALL question types with options_count > 1
all_multi = Question.objects.filter(options_count__gt=1).order_by('question_type', 'options_count')

problems = []
stats = {'SHORT': 0, 'MIXED': 0, 'MCQ': 0, 'CHECKBOX': 0, 'LONG': 0}

for q in all_multi:
    stats[q.question_type] = stats.get(q.question_type, 0) + 1
    
    # For SHORT and MIXED, check letter generation
    if q.question_type in ['SHORT', 'MIXED']:
        letters = get_answer_letters(q)
        
        if len(letters) != q.options_count:
            problems.append({
                'id': q.id,
                'type': q.question_type,
                'exam': q.exam.name[:30] if q.exam else 'None',
                'q_num': q.question_number,
                'options_count': q.options_count,
                'correct_answer': str(q.correct_answer)[:50],
                'letters_generated': letters
            })

print(f'\nStatistics (questions with options_count > 1):')
for qtype, count in stats.items():
    print(f'  {qtype}: {count} questions')

if problems:
    print(f'\n❌ Found {len(problems)} problematic questions:')
    
    # Group by type
    short_problems = [p for p in problems if p['type'] == 'SHORT']
    mixed_problems = [p for p in problems if p['type'] == 'MIXED']
    
    if short_problems:
        print(f'\nSHORT Questions with issues ({len(short_problems)}):')
        for p in short_problems[:5]:  # Show first 5
            print(f'  Q{p["q_num"]} (ID {p["id"]}):')
            print(f'    Exam: {p["exam"]}...')
            print(f'    Expected: {p["options_count"]} inputs')
            print(f'    Got: {len(p["letters_generated"])} letters {p["letters_generated"]}')
            print(f'    Correct Answer: "{p["correct_answer"]}"')
    
    if mixed_problems:
        print(f'\nMIXED Questions with issues ({len(mixed_problems)}):')
        for p in mixed_problems[:5]:  # Show first 5
            print(f'  Q{p["q_num"]} (ID {p["id"]}):')
            print(f'    Exam: {p["exam"]}...')
            print(f'    Expected: {p["options_count"]} inputs')
            print(f'    Got: {len(p["letters_generated"])} letters {p["letters_generated"]}')
            print(f'    Correct Answer: "{p["correct_answer"]}"')
else:
    print('\n✅ All questions generate correct number of letters')

# Now let's check if the issue might be with options_count=1 being treated as multiple
print('\n' + '='*80)
print('CHECKING OPTIONS_COUNT=1 QUESTIONS')
print('='*80)

single_option = Question.objects.filter(options_count=1)
print(f'\nFound {single_option.count()} questions with options_count=1')

for q in single_option[:5]:
    has_multi = has_multiple_answers(q)
    letters = get_answer_letters(q)
    
    if has_multi or len(letters) > 0:
        print(f'  ⚠️ Q{q.question_number} (ID {q.id}, {q.question_type}):')
        print(f'    has_multiple_answers: {has_multi}')
        print(f'    get_answer_letters: {letters}')
        print(f'    This should NOT show multiple inputs!')

# Check for data where correct_answer suggests different count than options_count
print('\n' + '='*80)
print('CHECKING DATA CONSISTENCY')
print('='*80)

# Questions where correct_answer has more parts than options_count
for q in Question.objects.filter(question_type='SHORT', options_count__gt=0):
    if q.correct_answer:
        # Count parts in correct_answer
        parts = 0
        answer = str(q.correct_answer)
        
        if ',' in answer:
            parts = len(answer.split(','))
        elif '|' in answer and not any(c.isalpha() for c in answer.split('|')[0]):
            # Pipe separated and not letters (like "111|222")
            parts = len(answer.split('|'))
        else:
            parts = 1
        
        if parts > q.options_count:
            print(f'  Data inconsistency in Q{q.question_number} (ID {q.id}):')
            print(f'    options_count: {q.options_count}')
            print(f'    correct_answer parts: {parts}')
            print(f'    correct_answer: "{q.correct_answer[:50]}"')
#!/usr/bin/env python
"""
Fix options_count for LONG questions with multiple responses
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import transaction
from placement_test.models import Question


def fix_long_questions():
    print('='*80)
    print('FIXING LONG QUESTIONS OPTIONS_COUNT')
    print('='*80)
    
    # Find all LONG questions
    long_questions = Question.objects.filter(question_type='LONG')
    print(f'\nFound {long_questions.count()} LONG questions')
    
    fixed_count = 0
    
    with transaction.atomic():
        for q in long_questions:
            old_count = q.options_count
            
            # Calculate correct count based on triple pipe separator
            if q.correct_answer and '|||' in q.correct_answer:
                parts = [p.strip() for p in q.correct_answer.split('|||') if p.strip()]
                new_count = max(len(parts), 1)
            else:
                new_count = 1
            
            if old_count != new_count:
                print(f'\nQuestion {q.question_number} (ID {q.id}):')
                print(f'  Exam: {q.exam.name[:40] if q.exam else "None"}...')
                print(f'  Old options_count: {old_count}')
                print(f'  New options_count: {new_count}')
                print(f'  Correct answer: "{q.correct_answer[:50]}..."')
                
                q.options_count = new_count
                q.save(update_fields=['options_count'])
                fixed_count += 1
    
    if fixed_count > 0:
        print(f'\n✅ Fixed {fixed_count} LONG questions')
    else:
        print('\n✅ All LONG questions already have correct options_count')
    
    # Verify the fix
    print('\n' + '='*80)
    print('VERIFICATION')
    print('='*80)
    
    for q in Question.objects.filter(question_type='LONG', options_count__gt=1):
        print(f'\nQuestion {q.question_number} (ID {q.id}):')
        print(f'  options_count: {q.options_count}')
        
        if '|||' in q.correct_answer:
            parts = q.correct_answer.split('|||')
            print(f'  Answer parts: {len(parts)}')
            
            if len(parts) == q.options_count:
                print(f'  ✅ Correct: options_count matches answer parts')
            else:
                print(f'  ❌ Mismatch: {q.options_count} != {len(parts)}')


if __name__ == '__main__':
    fix_long_questions()
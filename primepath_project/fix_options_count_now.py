#!/usr/bin/env python
"""
Fix options_count inconsistencies immediately
Ensures options_count matches the actual number of answers in correct_answer field
"""

import os
import sys
import django
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import transaction
from placement_test.models import Question


def get_actual_answer_count(question):
    """
    Determine the actual number of answer options based on the correct_answer field
    """
    if not question.correct_answer:
        return 1  # Default to 1 for empty answers
    
    answer = str(question.correct_answer).strip()
    
    # For MIXED questions with JSON structure
    if question.question_type == 'MIXED':
        try:
            parsed = json.loads(answer)
            if isinstance(parsed, list):
                # Count the number of components
                return max(len(parsed), 1)
        except:
            pass
    
    # For SHORT questions or non-JSON MIXED
    if question.question_type == 'SHORT':
        # Check for multiple parts
        if '|' in answer:
            # Split by pipe and count non-empty parts
            parts = [p.strip() for p in answer.split('|') if p.strip()]
            return max(len(parts), 1)
        elif ',' in answer:
            # Check if it's letter format (A,B,C) or actual answers
            parts = [p.strip() for p in answer.split(',') if p.strip()]
            # If all parts are single letters, it's likely MCQ format
            if all(len(p) == 1 and p.isalpha() for p in parts):
                return len(parts)
            # Otherwise, treat as separate answers
            return max(len(parts), 1)
    
    # Default: if there's an answer, at least 1 option
    return max(question.options_count, 1)


def main(dry_run=False):
    print('='*80)
    print('FIXING OPTIONS_COUNT INCONSISTENCIES')
    print('='*80)
    
    if dry_run:
        print('\nDRY RUN MODE - No changes will be made')
    
    fixed_count = 0
    issues_found = []
    
    # Check all SHORT and MIXED questions
    questions = Question.objects.filter(question_type__in=['SHORT', 'MIXED'])
    
    print(f'\nChecking {questions.count()} SHORT and MIXED questions...\n')
    
    with transaction.atomic():
        for question in questions:
            actual_count = get_actual_answer_count(question)
            
            if actual_count != question.options_count:
                issues_found.append({
                    'id': question.id,
                    'exam': question.exam.name[:40] if question.exam else 'None',
                    'q_num': question.question_number,
                    'type': question.question_type,
                    'old_options_count': question.options_count,
                    'new_options_count': actual_count,
                    'correct_answer': str(question.correct_answer)[:50]
                })
                
                if not dry_run:
                    question.options_count = actual_count
                    question.save(update_fields=['options_count'])
                    fixed_count += 1
    
    # Report results
    if issues_found:
        print(f'Found {len(issues_found)} questions with inconsistent options_count:\n')
        
        for issue in issues_found[:10]:  # Show first 10
            print(f'  Question {issue["q_num"]} (ID {issue["id"]}, {issue["type"]}):')
            print(f'    Exam: {issue["exam"]}...')
            print(f'    Old options_count: {issue["old_options_count"]}')
            print(f'    New options_count: {issue["new_options_count"]}')
            print(f'    Correct answer: "{issue["correct_answer"]}..."')
            print()
        
        if len(issues_found) > 10:
            print(f'  ... and {len(issues_found) - 10} more\n')
        
        if not dry_run:
            print(f'✅ Fixed {fixed_count} questions')
        else:
            print(f'⚠️ Would fix {len(issues_found)} questions (run without --dry-run to apply)')
    else:
        print('✅ No inconsistencies found - all questions have correct options_count')
    
    return issues_found, fixed_count


if __name__ == '__main__':
    import sys
    
    dry_run = '--dry-run' in sys.argv
    issues, fixed = main(dry_run)
    
    if dry_run and issues:
        print('\nTo apply these fixes, run:')
        print('  python fix_options_count_now.py')
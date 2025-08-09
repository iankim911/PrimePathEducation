#!/usr/bin/env python
"""
Test MIXED MCQ components and individual options count
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

from placement_test.models import Question
from placement_test.templatetags.grade_tags import get_mixed_components

print('='*80)
print('MIXED MCQ OPTIONS COUNT INVESTIGATION')
print(f'Timestamp: {datetime.now()}')
print('='*80)

# Find MIXED questions with MCQ components
mixed_questions = Question.objects.filter(
    question_type='MIXED',
    correct_answer__contains='Multiple Choice'
)

print(f'\nFound {mixed_questions.count()} MIXED questions with MCQ components')

for i, q in enumerate(mixed_questions[:3], 1):
    print(f'\n{"-"*50}')
    print(f'MIXED Question {i}: ID={q.id}, #={q.question_number}')
    print(f'Options Count: {q.options_count}')
    
    # Parse the JSON structure
    try:
        parsed = json.loads(q.correct_answer)
        print(f'JSON Components ({len(parsed)}):')
        for j, comp in enumerate(parsed):
            comp_type = comp.get('type', 'Unknown')
            comp_value = comp.get('value', '')
            print(f'  {j+1}. {comp_type}: "{comp_value}"')
    except Exception as e:
        print(f'  JSON Parse Error: {e}')
        continue
    
    # Test the template filter
    components = get_mixed_components(q)
    print(f'\nTemplate Filter Output ({len(components)}):')
    for j, comp in enumerate(components):
        comp_type = comp.get('type', 'unknown')
        comp_letter = comp.get('letter', '?')
        comp_options = comp.get('options', [])
        
        print(f'  {j+1}. Type: {comp_type}, Letter: {comp_letter}')
        
        if comp_type == 'mcq':
            print(f'      Options ({len(comp_options)}): {comp_options}')
            print(f'      Expected from options_count ({q.options_count}): {list("ABCDEFGHIJ"[:q.options_count])}')
            
            # Check if they match
            expected = list("ABCDEFGHIJ"[:q.options_count])
            if comp_options == expected:
                print(f'      ✅ CORRECT: MCQ uses question options_count')
            else:
                print(f'      ❌ WRONG: MCQ should use {expected}, got {comp_options}')

# Test the UI rendering
print(f'\n{"-"*50}')
print('UI RENDERING TEST')
print(f'{"-"*50}')

test_q = mixed_questions.first()
if test_q:
    print(f'\nTesting Q{test_q.id} with options_count={test_q.options_count}')
    
    # Change options_count to see if MCQ components update
    original_count = test_q.options_count
    test_counts = [3, 7, 10]
    
    for count in test_counts:
        test_q.options_count = count
        test_q.save()
        
        components = get_mixed_components(test_q)
        mcq_comps = [c for c in components if c.get('type') == 'mcq']
        
        print(f'\n  With options_count={count}:')
        for comp in mcq_comps:
            options = comp.get('options', [])
            expected = list("ABCDEFGHIJ"[:count])
            print(f'    MCQ options: {options}')
            print(f'    Expected:    {expected}')
            if options == expected:
                print(f'    ✅ CORRECT')
            else:
                print(f'    ❌ WRONG - MCQ not using options_count')
        
        if not mcq_comps:
            print(f'    ⚠️ No MCQ components found')
    
    # Restore original
    test_q.options_count = original_count
    test_q.save()

# Test in student interface context
print(f'\n{"-"*50}')
print('STUDENT INTERFACE SIMULATION')
print(f'{"-"*50}')

if test_q:
    print(f'\nSimulating student interface for Q{test_q.id}:')
    print(f'Question options_count: {test_q.options_count}')
    
    components = get_mixed_components(test_q)
    
    for i, comp in enumerate(components):
        if comp.get('type') == 'mcq':
            options = comp.get('options', [])
            letter = comp.get('letter', 'X')
            index = comp.get('index', i)
            
            print(f'\n  Multiple Choice {letter}:')
            for option in options:
                checkbox_name = f'q_{test_q.id}_{index}_{option}'
                print(f'    ☐ {option} (name="{checkbox_name}")')
            
            print(f'    Student sees {len(options)} options')
            print(f'    Should see {test_q.options_count} options based on question.options_count')

print('\n' + '='*80)
print('INVESTIGATION COMPLETE')
print('='*80)
#!/usr/bin/env python
"""
Detailed test of each question type to ensure correct rendering
"""

import os
import sys
import django
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from placement_test.models import Question
from placement_test.templatetags.grade_tags import (
    get_answer_letters, has_multiple_answers, get_mixed_components
)

print('='*80)
print('DETAILED QUESTION TYPE RENDERING TEST')
print('='*80)

def test_question_type(question_type, expected_behavior):
    """Test a specific question type"""
    questions = Question.objects.filter(question_type=question_type)
    
    if not questions.exists():
        return f"⚠️ No {question_type} questions found", None
    
    results = []
    for q in questions[:3]:  # Test first 3 of each type
        letters = get_answer_letters(q)
        multi = has_multiple_answers(q)
        
        # Build result string
        result = {
            'id': q.id,
            'number': q.question_number,
            'options_count': q.options_count,
            'has_multiple': multi,
            'letter_count': len(letters),
            'correct_answer_preview': q.correct_answer[:50] if q.correct_answer else 'None'
        }
        
        # Check if behavior matches expected
        if question_type == 'MCQ':
            # MCQ should never have multiple answers
            if not multi and len(letters) == 0:
                result['status'] = '✅'
            else:
                result['status'] = '❌'
                
        elif question_type == 'CHECKBOX':
            # CHECKBOX should never have text inputs
            if not multi and len(letters) == 0:
                result['status'] = '✅'
            else:
                result['status'] = '❌'
                
        elif question_type in ['SHORT', 'LONG']:
            # These can have multiple based on options_count
            if q.options_count > 1:
                if multi and len(letters) == q.options_count:
                    result['status'] = '✅'
                else:
                    result['status'] = '❌'
            else:
                if not multi and len(letters) == 0:
                    result['status'] = '✅'
                else:
                    result['status'] = '❌'
                    
        elif question_type == 'MIXED':
            # MIXED uses different logic
            components = get_mixed_components(q)
            if len(components) == q.options_count:
                result['status'] = '✅'
                result['components'] = len(components)
            else:
                result['status'] = '❌'
                result['components'] = len(components)
        else:
            result['status'] = '?'
            
        results.append(result)
    
    return results

# Test each question type
question_types = {
    'MCQ': 'Single choice, no text inputs',
    'CHECKBOX': 'Multiple choice checkboxes, no text inputs',
    'SHORT': 'Text input(s) based on options_count',
    'LONG': 'Textarea(s) based on options_count',
    'MIXED': 'Combination of MCQ and text inputs',
    'multiple_choice': 'Legacy type - should work like MCQ'
}

all_pass = True

for qtype, description in question_types.items():
    print(f'\n{qtype} - {description}')
    print('-'*60)
    
    results = test_question_type(qtype, description)
    
    if isinstance(results, tuple):
        print(results[0])
        continue
    
    for r in results:
        status = r['status']
        print(f'{status} Q{r["id"]} (#{r["number"]}):')
        print(f'   options_count: {r["options_count"]}')
        print(f'   has_multiple: {r["has_multiple"]}')
        print(f'   letter_count: {r["letter_count"]}')
        
        if qtype == 'MIXED' and 'components' in r:
            print(f'   components: {r["components"]}')
            
        if r['status'] == '❌':
            all_pass = False
            print(f'   ⚠️ ISSUE: Rendering not matching expected behavior')
            print(f'   Answer: {r["correct_answer_preview"]}...')

# Special test for MIXED with MCQ components
print('\n\nSPECIAL: MIXED with MCQ Components')
print('-'*60)

mixed_mcq = Question.objects.filter(
    question_type='MIXED',
    correct_answer__contains='Multiple Choice'
).first()

if mixed_mcq:
    components = get_mixed_components(mixed_mcq)
    print(f'Question {mixed_mcq.id}:')
    print(f'  options_count: {mixed_mcq.options_count}')
    print(f'  Components: {len(components)}')
    
    mcq_count = 0
    input_count = 0
    
    for i, comp in enumerate(components):
        comp_type = comp.get('type')
        if comp_type == 'mcq':
            mcq_count += 1
            print(f'  Component {i+1}: MCQ with options {comp.get("options", [])}')
            if 'selected' in comp:
                print(f'    Pre-selected: {comp["selected"]}')
        elif comp_type == 'input':
            input_count += 1
            print(f'  Component {i+1}: Text input')
    
    print(f'\n  Summary: {mcq_count} MCQ checkbox groups, {input_count} text inputs')
    
    # Parse JSON to verify
    try:
        parsed = json.loads(mixed_mcq.correct_answer)
        expected_mcq = sum(1 for item in parsed if item.get('type') == 'Multiple Choice')
        
        if expected_mcq == mcq_count:
            print(f'  ✅ MCQ components correctly identified')
        else:
            print(f'  ❌ Expected {expected_mcq} MCQ, got {mcq_count}')
            all_pass = False
    except:
        print('  ⚠️ Could not parse JSON for verification')

# Summary
print('\n' + '='*80)
print('SUMMARY')
print('='*80)

if all_pass:
    print('\n✅ ALL QUESTION TYPES RENDER CORRECTLY')
    print('Each question type follows its expected rendering behavior:')
    print('  - MCQ: Single choice radio buttons')
    print('  - CHECKBOX: Multiple choice checkboxes')
    print('  - SHORT: Text input(s) based on options_count')
    print('  - LONG: Textarea(s) based on options_count')
    print('  - MIXED: Proper mix of MCQ checkboxes and text inputs')
else:
    print('\n❌ SOME QUESTION TYPES HAVE RENDERING ISSUES')
    print('Review the details above for specific problems.')

print('\n' + '='*80)
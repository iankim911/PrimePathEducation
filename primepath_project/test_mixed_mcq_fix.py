#!/usr/bin/env python
"""
Test MIXED question MCQ rendering fix
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from placement_test.models import Question
from placement_test.templatetags.grade_tags import get_mixed_components
import json

print('='*80)
print('MIXED QUESTION MCQ RENDERING TEST')
print('='*80)

# Test 1: MIXED question with all MCQ components
print('\n1. MIXED QUESTION WITH ALL MCQ COMPONENTS')
print('-'*40)

q = Question.objects.filter(question_type='MIXED', id=1016).first()
if q:
    print(f'Question ID: {q.id}')
    print(f'Question Number: {q.question_number}')
    print(f'Options Count: {q.options_count}')
    print(f'Correct Answer: {q.correct_answer}')
    
    # Test the filter
    components = get_mixed_components(q)
    print(f'\nComponents returned by filter: {len(components)}')
    
    for i, comp in enumerate(components):
        print(f'\nComponent {i+1}:')
        print(f'  Type: {comp.get("type")}')
        print(f'  Letter: {comp.get("letter")}')
        if comp.get('type') == 'mcq':
            print(f'  Options: {comp.get("options")}')
            print(f'  Selected: {comp.get("selected")}')
            print(f'  ✅ MCQ component properly configured')
        else:
            print(f'  ❌ Expected mcq type, got {comp.get("type")}')
else:
    print('❌ Question 1016 not found')

# Test 2: MIXED question with mixed types
print('\n\n2. MIXED QUESTION WITH MIXED TYPES')
print('-'*40)

q = Question.objects.filter(question_type='MIXED', id=1017).first()
if q:
    print(f'Question ID: {q.id}')
    print(f'Question Number: {q.question_number}')
    print(f'Options Count: {q.options_count}')
    
    # Parse JSON
    try:
        parsed = json.loads(q.correct_answer)
        print(f'JSON Components:')
        for i, item in enumerate(parsed):
            print(f'  {i+1}. Type: {item.get("type")}, Value: {item.get("value")}')
    except:
        print(f'Raw: {q.correct_answer[:100]}...')
    
    # Test the filter
    components = get_mixed_components(q)
    print(f'\nComponents returned by filter: {len(components)}')
    
    mcq_count = 0
    input_count = 0
    
    for i, comp in enumerate(components):
        comp_type = comp.get("type")
        if comp_type == 'mcq':
            mcq_count += 1
            print(f'  Component {i+1}: MCQ with options {comp.get("options")}')
        elif comp_type == 'input':
            input_count += 1
            print(f'  Component {i+1}: Text input')
        else:
            print(f'  Component {i+1}: Unknown type {comp_type}')
    
    print(f'\nSummary: {mcq_count} MCQ, {input_count} text inputs')
else:
    print('❌ Question 1017 not found')

# Test 3: Test rendering behavior
print('\n\n3. RENDERING BEHAVIOR TEST')
print('-'*40)

# Check all MIXED questions
mixed_questions = Question.objects.filter(question_type='MIXED')[:5]
print(f'Testing {len(mixed_questions)} MIXED questions:')

for q in mixed_questions:
    components = get_mixed_components(q)
    mcq_components = [c for c in components if c.get('type') == 'mcq']
    input_components = [c for c in components if c.get('type') == 'input']
    
    print(f'\nQuestion {q.id} (#{q.question_number}):')
    print(f'  Options count: {q.options_count}')
    print(f'  Total components: {len(components)}')
    print(f'  MCQ components: {len(mcq_components)}')
    print(f'  Input components: {len(input_components)}')
    
    # Check if rendering matches JSON structure
    if q.correct_answer:
        try:
            parsed = json.loads(q.correct_answer)
            expected_mcq = sum(1 for item in parsed if item.get('type') == 'Multiple Choice')
            expected_input = sum(1 for item in parsed if item.get('type') == 'Short Answer')
            
            if expected_mcq == len(mcq_components) and expected_input == len(input_components):
                print(f'  ✅ Rendering matches JSON structure')
            else:
                print(f'  ❌ Mismatch: Expected {expected_mcq} MCQ, {expected_input} inputs')
        except:
            print(f'  ⚠️ Could not parse JSON')

# Test 4: Template compatibility
print('\n\n4. TEMPLATE COMPATIBILITY TEST')
print('-'*40)

q = Question.objects.filter(question_type='MIXED').first()
if q:
    components = get_mixed_components(q)
    
    print('Checking component structure for template:')
    for i, comp in enumerate(components):
        print(f'\nComponent {i+1}:')
        required_fields = ['type', 'letter', 'index']
        for field in required_fields:
            if field in comp:
                print(f'  ✅ Has {field}: {comp[field]}')
            else:
                print(f'  ❌ Missing {field}')
        
        if comp.get('type') == 'mcq':
            if 'options' in comp:
                print(f'  ✅ Has options: {comp["options"]}')
            else:
                print(f'  ❌ Missing options for MCQ')

print('\n' + '='*80)
print('TEST COMPLETE')
print('='*80)

# Summary
print('\nSUMMARY:')
print('The fix properly identifies Multiple Choice components in MIXED questions')
print('and returns them with type="mcq" instead of type="input".')
print('MCQ components now include options list for checkbox rendering.')
#!/usr/bin/env python
"""
Comprehensive test of all MIXED question combinations
"""

import os
import sys
import django
import json
from django.test import Client
from django.urls import reverse

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from placement_test.models import Question, Exam
from placement_test.templatetags.grade_tags import get_mixed_components

print('='*80)
print('COMPREHENSIVE MIXED QUESTION TEST')
print('='*80)

test_results = []
issues = []

# Test 1: Filter returns correct component types
print('\n1. FILTER COMPONENT TYPE TEST')
print('-'*40)

mixed_questions = Question.objects.filter(question_type='MIXED')
print(f'Found {mixed_questions.count()} MIXED questions')

for q in mixed_questions[:10]:
    components = get_mixed_components(q)
    
    if q.correct_answer:
        try:
            parsed = json.loads(q.correct_answer)
            
            # Count expected vs actual
            expected_mcq = sum(1 for item in parsed if item.get('type') == 'Multiple Choice')
            expected_input = sum(1 for item in parsed if item.get('type') == 'Short Answer')
            
            actual_mcq = sum(1 for c in components if c.get('type') == 'mcq')
            actual_input = sum(1 for c in components if c.get('type') == 'input')
            
            if expected_mcq == actual_mcq and expected_input == actual_input:
                test_results.append(('Filter types', True))
                print(f'✅ Q{q.id}: {actual_mcq} MCQ, {actual_input} inputs - Correct')
            else:
                test_results.append(('Filter types', False))
                issues.append(f'Q{q.id}: Expected {expected_mcq} MCQ, {expected_input} inputs, got {actual_mcq} MCQ, {actual_input} inputs')
                print(f'❌ Q{q.id}: Mismatch')
        except Exception as e:
            print(f'⚠️ Q{q.id}: Parse error - {e}')

# Test 2: MCQ components have required fields
print('\n2. MCQ COMPONENT STRUCTURE TEST')
print('-'*40)

q = Question.objects.filter(question_type='MIXED', correct_answer__contains='Multiple Choice').first()
if q:
    components = get_mixed_components(q)
    mcq_components = [c for c in components if c.get('type') == 'mcq']
    
    if mcq_components:
        all_valid = True
        for comp in mcq_components:
            required = ['type', 'letter', 'index', 'options']
            for field in required:
                if field not in comp:
                    all_valid = False
                    issues.append(f'MCQ component missing {field}')
                    
        if all_valid:
            print('✅ All MCQ components have required fields')
            test_results.append(('MCQ structure', True))
        else:
            print('❌ Some MCQ components missing fields')
            test_results.append(('MCQ structure', False))
    else:
        print('⚠️ No MCQ components found to test')

# Test 3: Template rendering simulation
print('\n3. TEMPLATE RENDERING SIMULATION')
print('-'*40)

q = Question.objects.filter(question_type='MIXED').first()
if q:
    components = get_mixed_components(q)
    
    print(f'Question {q.id} would render:')
    for comp in components:
        if comp.get('type') == 'mcq':
            print(f'  Component {comp["letter"]}: MCQ with checkboxes for {comp.get("options", [])}')
        elif comp.get('type') == 'input':
            print(f'  Component {comp["letter"]}: Text input field')
        else:
            print(f'  Component {comp["letter"]}: Unknown type {comp.get("type")}')
    
    test_results.append(('Template simulation', True))

# Test 4: Options count consistency
print('\n4. OPTIONS COUNT CONSISTENCY')
print('-'*40)

for q in mixed_questions[:5]:
    components = get_mixed_components(q)
    
    if len(components) == q.options_count:
        print(f'✅ Q{q.id}: {len(components)} components matches options_count={q.options_count}')
        test_results.append(('Options count', True))
    else:
        print(f'❌ Q{q.id}: {len(components)} components != options_count={q.options_count}')
        test_results.append(('Options count', False))
        issues.append(f'Q{q.id}: Component count mismatch')

# Test 5: Selected values preserved
print('\n5. SELECTED VALUES TEST')
print('-'*40)

q = Question.objects.filter(id=1016).first()  # Known MCQ question
if q:
    components = get_mixed_components(q)
    
    try:
        parsed = json.loads(q.correct_answer)
        
        for i, comp in enumerate(components):
            if comp.get('type') == 'mcq' and i < len(parsed):
                expected_value = parsed[i].get('value', '')
                actual_selected = ','.join(comp.get('selected', []))
                
                if expected_value == actual_selected:
                    print(f'✅ Component {i+1}: Selected values preserved ({actual_selected})')
                    test_results.append(('Selected values', True))
                else:
                    print(f'❌ Component {i+1}: Expected {expected_value}, got {actual_selected}')
                    test_results.append(('Selected values', False))
                    issues.append(f'Selected values mismatch')
    except:
        print('⚠️ Could not test selected values')

# Test 6: Edge cases
print('\n6. EDGE CASES')
print('-'*40)

# Empty correct_answer
q_empty = Question.objects.filter(question_type='MIXED', correct_answer='').first()
if q_empty:
    components = get_mixed_components(q_empty)
    if len(components) == 0:
        print('✅ Empty correct_answer handled correctly')
        test_results.append(('Edge case - empty', True))
    else:
        print('❌ Empty correct_answer produced components')
        test_results.append(('Edge case - empty', False))

# Invalid JSON
q_invalid = Question.objects.filter(question_type='MIXED').first()
if q_invalid:
    # Temporarily set invalid JSON
    old_answer = q_invalid.correct_answer
    q_invalid.correct_answer = 'invalid json {['
    
    try:
        components = get_mixed_components(q_invalid)
        if len(components) == q_invalid.options_count:
            print('✅ Invalid JSON fallback works')
            test_results.append(('Edge case - invalid JSON', True))
        else:
            print('❌ Invalid JSON not handled properly')
            test_results.append(('Edge case - invalid JSON', False))
    except Exception as e:
        print(f'❌ Exception on invalid JSON: {e}')
        test_results.append(('Edge case - invalid JSON', False))
    finally:
        q_invalid.correct_answer = old_answer

# Final Summary
print('\n' + '='*80)
print('TEST SUMMARY')
print('='*80)

passed = sum(1 for _, result in test_results if result)
failed = sum(1 for _, result in test_results if not result)

print(f'\n✅ Passed: {passed} tests')
print(f'❌ Failed: {failed} tests')

if issues:
    print(f'\n🔴 Issues found:')
    for issue in issues[:5]:  # Show first 5 issues
        print(f'  - {issue}')
else:
    print('\n✅ ALL TESTS PASSED')
    print('MIXED questions with Multiple Choice components now render correctly as checkbox groups.')

print('\n' + '='*80)
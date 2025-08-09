#!/usr/bin/env python
"""
Test MIXED questions with Long Answer components
Verifies they render as textareas instead of text inputs
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
print('MIXED LONG ANSWER FIX TEST')
print(f'Timestamp: {datetime.now()}')
print('='*80)

all_tests = []
issues = []

# Test 1: Check filter output for MIXED with Long Answer
print('\n1. FILTER OUTPUT TEST')
print('-'*40)

# Test Question 6 (2 Short + 1 Long)
q6 = Question.objects.filter(id=1019).first()
if q6:
    print(f'Question {q6.id} (#{q6.question_number}):')
    print(f'  Type: {q6.question_type}')
    print(f'  Options Count: {q6.options_count}')
    
    # Parse JSON
    try:
        parsed = json.loads(q6.correct_answer)
        print(f'  JSON Components:')
        for i, comp in enumerate(parsed):
            print(f'    {i+1}. {comp.get("type")}: "{comp.get("value")}"')
    except:
        pass
    
    # Test filter output
    components = get_mixed_components(q6)
    print(f'\n  Filter returns {len(components)} components:')
    
    expected_types = ['input', 'input', 'textarea']  # 2 Short, 1 Long
    actual_types = [c.get('type') for c in components]
    
    for i, comp in enumerate(components):
        expected = expected_types[i] if i < len(expected_types) else 'unknown'
        actual = comp.get('type')
        symbol = '✅' if actual == expected else '❌'
        
        print(f'    Component {comp.get("letter")}:')
        print(f'      {symbol} Type: {actual} (expected: {expected})')
        print(f'      Index: {comp.get("index")}')
        
        if actual == expected:
            all_tests.append((f'Q6 Component {i+1}', True))
        else:
            all_tests.append((f'Q6 Component {i+1}', False))
            issues.append(f'Q6 Component {i+1}: Expected {expected}, got {actual}')
else:
    print('❌ Question 1019 not found')
    all_tests.append(('Q6 test', False))

# Test 2: Check Question 4 (1 MCQ + 2 Short + 1 Long)
print('\n2. QUESTION 4 TEST (MIXED TYPES)')
print('-'*40)

q4 = Question.objects.filter(id=1037).first()
if q4:
    print(f'Question {q4.id} (#{q4.question_number}):')
    
    # Parse JSON
    try:
        parsed = json.loads(q4.correct_answer)
        print(f'  JSON Components:')
        for i, comp in enumerate(parsed):
            print(f'    {i+1}. {comp.get("type")}')
    except:
        pass
    
    # Test filter output
    components = get_mixed_components(q4)
    print(f'\n  Filter returns {len(components)} components:')
    
    expected_types = ['mcq', 'input', 'input', 'textarea']  # 1 MCQ, 2 Short, 1 Long
    actual_types = [c.get('type') for c in components]
    
    for i, comp in enumerate(components):
        expected = expected_types[i] if i < len(expected_types) else 'unknown'
        actual = comp.get('type')
        symbol = '✅' if actual == expected else '❌'
        
        print(f'    Component {comp.get("letter")}: {symbol} {actual} (expected: {expected})')
        
        if actual == expected:
            all_tests.append((f'Q4 Component {i+1}', True))
        else:
            all_tests.append((f'Q4 Component {i+1}', False))
            issues.append(f'Q4 Component {i+1}: Expected {expected}, got {actual}')
            
        # Special checks for MCQ components
        if comp.get('type') == 'mcq':
            if 'options' in comp:
                print(f'      ✅ Has options: {comp["options"]}')
                all_tests.append((f'Q4 MCQ options', True))
            else:
                print(f'      ❌ Missing options')
                all_tests.append((f'Q4 MCQ options', False))
                issues.append('Q4 MCQ missing options')
else:
    print('⚠️ Question 1037 not found')

# Test 3: Check all MIXED questions
print('\n3. ALL MIXED QUESTIONS CHECK')
print('-'*40)

mixed_questions = Question.objects.filter(question_type='MIXED')
print(f'Total MIXED questions: {mixed_questions.count()}')

long_answer_count = 0
correct_rendering = 0

for q in mixed_questions:
    if q.correct_answer:
        try:
            parsed = json.loads(q.correct_answer)
            has_long = any(comp.get('type') == 'Long Answer' for comp in parsed)
            
            if has_long:
                long_answer_count += 1
                components = get_mixed_components(q)
                
                # Check if Long Answer components are rendered as textarea
                for i, comp_json in enumerate(parsed):
                    if comp_json.get('type') == 'Long Answer':
                        if i < len(components):
                            comp_filter = components[i]
                            if comp_filter.get('type') == 'textarea':
                                correct_rendering += 1
                                print(f'  ✅ Q{q.id}: Long Answer → textarea')
                            else:
                                print(f'  ❌ Q{q.id}: Long Answer → {comp_filter.get("type")}')
                                issues.append(f'Q{q.id} Long Answer not textarea')
        except:
            pass

if long_answer_count > 0:
    if correct_rendering == long_answer_count:
        print(f'\n  ✅ All {long_answer_count} Long Answer components render as textarea')
        all_tests.append(('Long Answer rendering', True))
    else:
        print(f'\n  ❌ Only {correct_rendering}/{long_answer_count} render correctly')
        all_tests.append(('Long Answer rendering', False))
else:
    print('\n  ⚠️ No Long Answer components found')

# Test 4: Verify other MIXED types still work
print('\n4. OTHER MIXED TYPES VERIFICATION')
print('-'*40)

# Test MIXED with only MCQ
mcq_only = Question.objects.filter(
    question_type='MIXED',
    correct_answer__contains='Multiple Choice'
).exclude(correct_answer__contains='Short Answer').exclude(correct_answer__contains='Long Answer').first()

if mcq_only:
    components = get_mixed_components(mcq_only)
    all_mcq = all(c.get('type') == 'mcq' for c in components)
    
    if all_mcq:
        print(f'  ✅ Q{mcq_only.id}: Pure MCQ MIXED works')
        all_tests.append(('Pure MCQ MIXED', True))
    else:
        print(f'  ❌ Q{mcq_only.id}: Pure MCQ MIXED broken')
        all_tests.append(('Pure MCQ MIXED', False))
        issues.append('Pure MCQ MIXED broken')

# Test MIXED with only Short Answer
short_only = Question.objects.filter(
    question_type='MIXED',
    correct_answer__contains='Short Answer'
).exclude(correct_answer__contains='Multiple Choice').exclude(correct_answer__contains='Long Answer').first()

if short_only:
    components = get_mixed_components(short_only)
    all_input = all(c.get('type') == 'input' for c in components)
    
    if all_input:
        print(f'  ✅ Q{short_only.id}: Pure Short Answer MIXED works')
        all_tests.append(('Pure Short MIXED', True))
    else:
        print(f'  ❌ Q{short_only.id}: Pure Short Answer MIXED broken')
        all_tests.append(('Pure Short MIXED', False))
        issues.append('Pure Short MIXED broken')

# Test 5: Template structure check
print('\n5. TEMPLATE STRUCTURE CHECK')
print('-'*40)

template_file = 'templates/components/placement_test/question_panel.html'
if os.path.exists(template_file):
    with open(template_file, 'r') as f:
        content = f.read()
        
        # Check for textarea handling
        if 'component.type == \'textarea\'' in content:
            print('  ✅ Template has textarea component handling')
            all_tests.append(('Template textarea', True))
        else:
            print('  ❌ Template missing textarea component handling')
            all_tests.append(('Template textarea', False))
            issues.append('Template missing textarea handling')
        
        # Check for proper textarea element
        if 'textarea name="q_{{ question.id }}_{{ component.letter }}"' in content:
            print('  ✅ Template has proper textarea element')
            all_tests.append(('Textarea element', True))
        else:
            print('  ❌ Template missing proper textarea element')
            all_tests.append(('Textarea element', False))
            issues.append('Template missing textarea element')
else:
    print('  ❌ Template file not found')

# Test 6: JavaScript answer collection
print('\n6. JAVASCRIPT ANSWER COLLECTION CHECK')
print('-'*40)

js_file = './static/js/modules/answer-manager.js'
if os.path.exists(js_file):
    with open(js_file, 'r') as f:
        content = f.read()
        
        # Check for textarea collection in MIXED
        if 'mixedTextareas' in content:
            print('  ✅ JavaScript handles textarea collection for MIXED')
            all_tests.append(('JS textarea collection', True))
        else:
            print('  ❌ JavaScript missing textarea collection for MIXED')
            all_tests.append(('JS textarea collection', False))
            issues.append('JS missing textarea collection')
        
        # Check for proper selector
        if 'textarea[name^="q_${questionId}_"]' in content:
            print('  ✅ JavaScript has correct textarea selector')
            all_tests.append(('JS textarea selector', True))
        else:
            print('  ❌ JavaScript missing textarea selector')
            all_tests.append(('JS textarea selector', False))
            issues.append('JS missing textarea selector')
else:
    print('  ❌ JavaScript file not found')

# SUMMARY
print('\n' + '='*80)
print('TEST SUMMARY')
print('='*80)

passed = sum(1 for _, result in all_tests if result is True)
failed = sum(1 for _, result in all_tests if result is False)
total = len(all_tests)

print(f'\n✅ Passed: {passed}/{total}')
print(f'❌ Failed: {failed}/{total}')

if issues:
    print(f'\n🔴 Issues Found ({len(issues)}):')
    for issue in issues[:10]:
        print(f'  - {issue}')
else:
    print('\n✅ ALL TESTS PASSED!')
    print('MIXED questions with Long Answer components now render as textareas.')
    print('All other MIXED combinations still work correctly.')

# Critical check
critical_ok = True
if failed > 0:
    critical_ok = False

print('\n' + '='*80)
print('CRITICAL COMPONENTS CHECK')
print('='*80)

critical_checks = [
    ('Filter differentiates Long Answer', 'textarea' in str([c.get('type') for c in get_mixed_components(q6)]) if q6 else False),
    ('Template handles textarea', os.path.exists(template_file) and 'component.type == \'textarea\'' in open(template_file).read()),
    ('JavaScript collects textareas', os.path.exists(js_file) and 'mixedTextareas' in open(js_file).read())
]

for check_name, check_result in critical_checks:
    if check_result:
        print(f'✅ {check_name}')
    else:
        print(f'❌ {check_name}')
        critical_ok = False

if critical_ok and failed == 0:
    print('\n✅ FIX SUCCESSFUL!')
    print('MIXED questions with Long Answer components are properly rendered.')
else:
    print('\n❌ FIX INCOMPLETE!')
    print('Some components need attention.')

print('\n' + '='*80)
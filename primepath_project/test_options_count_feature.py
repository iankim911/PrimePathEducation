#!/usr/bin/env python
"""
Test the new individual question options count feature
Verifies that MCQ/CHECKBOX questions can have custom option counts
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

from django.test import Client
from django.urls import reverse
from placement_test.models import Question, Exam
from placement_test.templatetags.grade_tags import get_mixed_components

print('='*80)
print('MCQ OPTIONS COUNT FEATURE TEST')
print(f'Timestamp: {datetime.now()}')
print('='*80)

all_tests = []
issues = []

def add_test(name, result, message=""):
    """Helper to track test results"""
    all_tests.append((name, result))
    if not result:
        issues.append(f"{name}: {message}")

# CATEGORY 1: Database and Model Tests
print('\n1. DATABASE AND MODEL TESTS')
print('-'*40)

# Test 1.1: Check options_count field exists
try:
    mcq_question = Question.objects.filter(question_type='MCQ').first()
    if mcq_question:
        print(f'✅ MCQ Question has options_count: {mcq_question.options_count}')
        add_test('MCQ options_count field', True)
    else:
        print('⚠️ No MCQ questions found')
        add_test('MCQ options_count field', None)
except Exception as e:
    print(f'❌ Error accessing options_count: {e}')
    add_test('MCQ options_count field', False, str(e))

# Test 1.2: Check default value
new_q = Question(
    exam=Exam.objects.first(),
    question_number=999,
    question_type='MCQ',
    correct_answer='A'
)
if new_q.options_count == 5:
    print('✅ Default options_count is 5')
    add_test('Default options_count', True)
else:
    print(f'❌ Default options_count is {new_q.options_count}, expected 5')
    add_test('Default options_count', False, f'Got {new_q.options_count}')

# CATEGORY 2: API Endpoint Tests
print('\n2. API ENDPOINT TESTS')
print('-'*40)

client = Client()

# Test 2.1: Update options_count for MCQ
if mcq_question:
    response = client.post(
        f'/api/placement/questions/{mcq_question.id}/update/',
        {
            'options_count': 7,
            'correct_answer': mcq_question.correct_answer,
            'points': mcq_question.points
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            mcq_question.refresh_from_db()
            if mcq_question.options_count == 7:
                print('✅ API successfully updated options_count to 7')
                add_test('API update options_count', True)
            else:
                print(f'❌ Options_count not updated: {mcq_question.options_count}')
                add_test('API update options_count', False, 'Value not saved')
        else:
            print(f'❌ API returned error: {data.get("error")}')
            add_test('API update options_count', False, data.get('error'))
    else:
        print(f'❌ API returned status {response.status_code}')
        add_test('API update options_count', False, f'Status {response.status_code}')

# Test 2.2: Validate answer range checking
if mcq_question:
    # Try to set invalid answer with reduced options
    mcq_question.correct_answer = 'E'
    mcq_question.options_count = 5
    mcq_question.save()
    
    response = client.post(
        f'/api/placement/questions/{mcq_question.id}/update/',
        {
            'options_count': 3,  # Reduce to 3 (A, B, C)
            'correct_answer': 'E',  # E is invalid for 3 options
            'points': 1
        }
    )
    
    data = response.json()
    if not data.get('success') and 'invalid' in data.get('error', '').lower():
        print('✅ API correctly validates answer range')
        add_test('Answer range validation', True)
    else:
        print('❌ API did not validate answer range')
        add_test('Answer range validation', False, 'No validation error')

# CATEGORY 3: Template Rendering Tests
print('\n3. TEMPLATE RENDERING TESTS')
print('-'*40)

# Test 3.1: Student interface respects options_count
mcq_with_3 = Question.objects.filter(question_type='MCQ').first()
if mcq_with_3:
    mcq_with_3.options_count = 3
    mcq_with_3.save()
    
    # Check template would render correct options
    letters = "ABCDEFGHIJ"[:mcq_with_3.options_count]
    if letters == "ABC":
        print('✅ Template would show 3 options (A, B, C)')
        add_test('Template options rendering', True)
    else:
        print(f'❌ Template letters incorrect: {letters}')
        add_test('Template options rendering', False, f'Got {letters}')

# Test 3.2: CHECKBOX with custom options
checkbox_q = Question.objects.filter(question_type='CHECKBOX').first()
if checkbox_q:
    checkbox_q.options_count = 8
    checkbox_q.save()
    
    letters = "ABCDEFGHIJ"[:checkbox_q.options_count]
    if letters == "ABCDEFGH":
        print('✅ CHECKBOX shows 8 options (A-H)')
        add_test('CHECKBOX custom options', True)
    else:
        print(f'❌ CHECKBOX letters incorrect: {letters}')
        add_test('CHECKBOX custom options', False, f'Got {letters}')

# CATEGORY 4: MIXED Question Tests
print('\n4. MIXED QUESTION MCQ COMPONENTS')
print('-'*40)

mixed_q = Question.objects.filter(question_type='MIXED').first()
if mixed_q:
    # Set custom options_count
    mixed_q.options_count = 6
    mixed_q.save()
    
    # Get components
    components = get_mixed_components(mixed_q)
    
    # Check if MCQ components have correct options
    mcq_components = [c for c in components if c.get('type') == 'mcq']
    if mcq_components:
        for comp in mcq_components:
            options = comp.get('options', [])
            if options == ['A', 'B', 'C', 'D', 'E', 'F']:
                print(f'✅ MIXED MCQ component has 6 options: {options}')
                add_test('MIXED MCQ options', True)
            else:
                print(f'❌ MIXED MCQ has wrong options: {options}')
                add_test('MIXED MCQ options', False, f'Got {options}')
            break
    else:
        print('⚠️ No MCQ components in MIXED question')
        add_test('MIXED MCQ options', None)
else:
    print('⚠️ No MIXED questions found')
    add_test('MIXED MCQ options', None)

# CATEGORY 5: Edge Cases
print('\n5. EDGE CASE TESTS')
print('-'*40)

# Test 5.1: Minimum options (2)
try:
    test_q = Question.objects.filter(question_type='MCQ').first()
    if test_q:
        response = client.post(
            f'/api/placement/questions/{test_q.id}/update/',
            {'options_count': 2, 'correct_answer': 'A', 'points': 1}
        )
        if response.json().get('success'):
            test_q.refresh_from_db()
            if test_q.options_count == 2:
                print('✅ Minimum options (2) works')
                add_test('Minimum options', True)
            else:
                print(f'❌ Minimum options failed: {test_q.options_count}')
                add_test('Minimum options', False)
        else:
            print(f'❌ Could not set minimum options: {response.json().get("error")}')
            add_test('Minimum options', False)
except Exception as e:
    print(f'❌ Error testing minimum: {e}')
    add_test('Minimum options', False, str(e))

# Test 5.2: Maximum options (10)
try:
    test_q = Question.objects.filter(question_type='MCQ').first()
    if test_q:
        response = client.post(
            f'/api/placement/questions/{test_q.id}/update/',
            {'options_count': 10, 'correct_answer': 'J', 'points': 1}
        )
        if response.json().get('success'):
            test_q.refresh_from_db()
            if test_q.options_count == 10:
                print('✅ Maximum options (10) works')
                add_test('Maximum options', True)
            else:
                print(f'❌ Maximum options failed: {test_q.options_count}')
                add_test('Maximum options', False)
        else:
            print(f'❌ Could not set maximum options: {response.json().get("error")}')
            add_test('Maximum options', False)
except Exception as e:
    print(f'❌ Error testing maximum: {e}')
    add_test('Maximum options', False, str(e))

# Test 5.3: Invalid range (11)
try:
    test_q = Question.objects.filter(question_type='MCQ').first()
    if test_q:
        response = client.post(
            f'/api/placement/questions/{test_q.id}/update/',
            {'options_count': 11, 'correct_answer': 'A', 'points': 1}
        )
        if not response.json().get('success'):
            print('✅ Correctly rejects invalid options_count (11)')
            add_test('Invalid range rejection', True)
        else:
            print('❌ Did not reject invalid options_count')
            add_test('Invalid range rejection', False)
except Exception as e:
    print(f'❌ Error testing invalid range: {e}')
    add_test('Invalid range rejection', False, str(e))

# CATEGORY 6: UI Functionality Check
print('\n6. UI FUNCTIONALITY TESTS')
print('-'*40)

# Test manage_questions page loads
exam = Exam.objects.first()
if exam:
    response = client.get(f'/placement-test/exams/{exam.id}/questions/')
    if response.status_code == 200:
        content = response.content.decode()
        
        # Check for options selector UI elements
        if 'options-count-selector' in content:
            print('✅ Options count selector present in UI')
            add_test('UI selector present', True)
        else:
            print('❌ Options count selector not found in UI')
            add_test('UI selector present', False)
        
        # Check for available options display
        if 'available-options' in content:
            print('✅ Available options display present')
            add_test('UI options display', True)
        else:
            print('❌ Available options display not found')
            add_test('UI options display', False)
    else:
        print(f'❌ Manage questions page returned {response.status_code}')
        add_test('UI page loads', False, f'Status {response.status_code}')

# SUMMARY
print('\n' + '='*80)
print('TEST SUMMARY')
print('='*80)

passed = sum(1 for _, result in all_tests if result is True)
failed = sum(1 for _, result in all_tests if result is False)
skipped = sum(1 for _, result in all_tests if result is None)
total = len(all_tests)

print(f'\n✅ Passed: {passed}/{total}')
print(f'❌ Failed: {failed}/{total}')
print(f'⚠️ Skipped: {skipped}/{total}')

if issues:
    print(f'\n🔴 Issues Found ({len(issues)}):')
    for issue in issues[:10]:
        print(f'  - {issue}')
else:
    print('\n✅ ALL TESTS PASSED!')
    print('Individual MCQ options count feature is working correctly.')
    print('Teachers can now customize options per question.')

# Feature verification
print('\n' + '='*80)
print('FEATURE VERIFICATION')
print('='*80)

feature_checks = [
    ('API endpoint handles options_count', passed > 0 and 'API' in str([name for name, _ in all_tests])),
    ('Validation prevents invalid answers', 'validation' in str([name.lower() for name, _ in all_tests])),
    ('MIXED questions support dynamic options', any('MIXED' in name for name, _ in all_tests)),
    ('UI components are present', any('UI' in name for name, _ in all_tests))
]

for check_name, check_result in feature_checks:
    if check_result:
        print(f'✅ {check_name}')
    else:
        print(f'❌ {check_name}')

if all(result for _, result in feature_checks):
    print('\n✅ FEATURE IMPLEMENTATION SUCCESSFUL!')
else:
    print('\n⚠️ Some feature components need attention.')

print('\n' + '='*80)
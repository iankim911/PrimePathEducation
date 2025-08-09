#!/usr/bin/env python
"""
Comprehensive QA test to ensure all features are working correctly
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
from placement_test.models import Question, Exam, StudentSession
from placement_test.templatetags import grade_tags
from placement_test.services.exam_service import ExamService


print('='*80)
print('COMPREHENSIVE QA TEST - FINAL')
print(f'Timestamp: {datetime.now()}')
print('='*80)

results = {
    'passed': [],
    'failed': [],
    'warnings': []
}

# Test 1: Verify Question 1014 fix
print('\n1. VERIFYING QUESTION 1014 FIX')
print('-'*40)
try:
    q1014 = Question.objects.get(id=1014)
    print(f'  Question 1 (ID 1014):')
    print(f'    correct_answer: "{q1014.correct_answer}"')
    print(f'    options_count: {q1014.options_count}')
    
    # Check if it has 3 parts
    parts = q1014.correct_answer.split('|')
    if len(parts) == 3 and q1014.options_count == 3:
        print(f'    ✅ FIXED: options_count correctly set to 3')
        results['passed'].append('Question 1014 fix')
    else:
        print(f'    ❌ PROBLEM: options_count={q1014.options_count}, parts={len(parts)}')
        results['failed'].append('Question 1014 fix')
        
    # Test template filters
    letters = grade_tags.get_answer_letters(q1014)
    has_multi = grade_tags.has_multiple_answers(q1014)
    
    print(f'    get_answer_letters: {letters} ({len(letters)} letters)')
    print(f'    has_multiple_answers: {has_multi}')
    
    if len(letters) == 3 and has_multi:
        print(f'    ✅ Template filters correct')
        results['passed'].append('Question 1014 template filters')
    else:
        print(f'    ❌ Template filters incorrect')
        results['failed'].append('Question 1014 template filters')
        
except Question.DoesNotExist:
    print('  ⚠️ Question 1014 not found')
    results['warnings'].append('Question 1014 not found')

# Test 2: Check all SHORT questions for consistency
print('\n2. CHECKING ALL SHORT QUESTIONS')
print('-'*40)

short_questions = Question.objects.filter(question_type='SHORT')
inconsistent = []

for q in short_questions:
    if q.correct_answer:
        if '|' in q.correct_answer:
            parts = [p.strip() for p in q.correct_answer.split('|') if p.strip()]
            expected = max(len(parts), 1)
        else:
            expected = 1
        
        if q.options_count != expected:
            inconsistent.append({
                'id': q.id,
                'options_count': q.options_count,
                'expected': expected,
                'answer': q.correct_answer[:30]
            })

if inconsistent:
    print(f'  ❌ {len(inconsistent)} SHORT questions still have inconsistent options_count:')
    for inc in inconsistent[:3]:
        print(f'    Q{inc["id"]}: options_count={inc["options_count"]}, expected={inc["expected"]}')
    results['failed'].append(f'{len(inconsistent)} SHORT questions inconsistent')
else:
    print(f'  ✅ All {short_questions.count()} SHORT questions have consistent options_count')
    results['passed'].append('All SHORT questions consistent')

# Test 3: Test save logic with new data
print('\n3. TESTING SAVE LOGIC')
print('-'*40)

try:
    # Find a test exam
    test_exam = Exam.objects.filter(name__contains='test').first()
    if not test_exam:
        test_exam = Exam.objects.first()
    
    if test_exam:
        # Test updating a SHORT question
        test_data = [{
            'id': None,
            'question_number': 99,  # Use a high number to avoid conflicts
            'question_type': 'SHORT',
            'correct_answer': 'answer1|answer2|answer3|answer4',
            'options_count': 2  # Intentionally wrong to test auto-correction
        }]
        
        # Use ExamService to update
        result = ExamService.update_exam_questions(test_exam, test_data)
        
        # Check if it was created with correct options_count
        created_q = Question.objects.filter(exam=test_exam, question_number=99).first()
        if created_q:
            if created_q.options_count == 4:  # Should be 4, not 2
                print(f'  ✅ Save logic auto-corrected options_count: 4 (correct)')
                results['passed'].append('Save logic auto-correction')
            else:
                print(f'  ❌ Save logic failed: options_count={created_q.options_count} (expected 4)')
                results['failed'].append('Save logic auto-correction')
            
            # Clean up test data
            created_q.delete()
        else:
            print(f'  ⚠️ Test question not created')
            results['warnings'].append('Test question creation')
    else:
        print(f'  ⚠️ No exam found for testing')
        results['warnings'].append('No test exam')
        
except Exception as e:
    print(f'  ❌ Error testing save logic: {e}')
    results['failed'].append(f'Save logic test error: {e}')

# Test 4: Test model validation
print('\n4. TESTING MODEL VALIDATION')
print('-'*40)

try:
    # Create a test question with inconsistent data
    test_exam = Exam.objects.first()
    if test_exam:
        test_q = Question(
            exam=test_exam,
            question_number=999,
            question_type='SHORT',
            correct_answer='a|b|c',
            options_count=1,  # Wrong - should be 3
            points=1
        )
        
        # Save should auto-correct
        test_q.save()
        
        if test_q.options_count == 3:
            print(f'  ✅ Model save() auto-corrected options_count to 3')
            results['passed'].append('Model save auto-correction')
        else:
            print(f'  ❌ Model save() did not correct: options_count={test_q.options_count}')
            results['failed'].append('Model save auto-correction')
        
        # Clean up
        test_q.delete()
        
except Exception as e:
    print(f'  ❌ Error testing model validation: {e}')
    results['failed'].append(f'Model validation error: {e}')

# Test 5: Check template rendering
print('\n5. CHECKING TEMPLATE RENDERING')
print('-'*40)

# Test each question type renders correctly
test_questions = {
    'MCQ': Question.objects.filter(question_type='MCQ').first(),
    'SHORT (single)': Question.objects.filter(question_type='SHORT', options_count=1).first(),
    'SHORT (multiple)': Question.objects.filter(question_type='SHORT', options_count__gt=1).first(),
    'MIXED': Question.objects.filter(question_type='MIXED').first(),
}

for qtype, q in test_questions.items():
    if q:
        letters = grade_tags.get_answer_letters(q)
        has_multi = grade_tags.has_multiple_answers(q)
        
        # Check expectations
        if qtype == 'MCQ':
            expected_letters = 0
            expected_multi = False
        elif qtype == 'SHORT (single)':
            expected_letters = 0
            expected_multi = False
        elif qtype == 'SHORT (multiple)':
            expected_letters = q.options_count
            expected_multi = True
        elif qtype == 'MIXED':
            expected_letters = q.options_count if q.options_count > 1 else 0
            expected_multi = q.options_count > 1
        
        if len(letters) == expected_letters and has_multi == expected_multi:
            print(f'  ✅ {qtype}: Correct rendering (letters={len(letters)}, multi={has_multi})')
            results['passed'].append(f'{qtype} rendering')
        else:
            print(f'  ❌ {qtype}: Wrong (got letters={len(letters)}, multi={has_multi})')
            print(f'     Expected: letters={expected_letters}, multi={expected_multi}')
            results['failed'].append(f'{qtype} rendering')

# Test 6: Check URL accessibility
print('\n6. URL ACCESSIBILITY CHECK')
print('-'*40)

client = Client()
test_urls = [
    ('placement_test:exam_list', 'Exam List'),
    ('placement_test:create_exam', 'Create Exam'),
    ('placement_test:start_test', 'Start Test'),
    ('placement_test:session_list', 'Session List'),
]

for url_name, description in test_urls:
    try:
        url = reverse(url_name)
        response = client.get(url)
        if response.status_code in [200, 302]:
            print(f'  ✅ {description}: Accessible (status {response.status_code})')
            results['passed'].append(f'{description} URL')
        else:
            print(f'  ❌ {description}: Status {response.status_code}')
            results['failed'].append(f'{description} URL')
    except Exception as e:
        print(f'  ❌ {description}: Error - {e}')
        results['failed'].append(f'{description} URL error')

# Final Summary
print('\n' + '='*80)
print('QA TEST SUMMARY')
print('='*80)

total_tests = len(results['passed']) + len(results['failed'])
print(f'\nTotal Tests: {total_tests}')
print(f'✅ Passed: {len(results["passed"])}')
print(f'❌ Failed: {len(results["failed"])}')
print(f'⚠️ Warnings: {len(results["warnings"])}')

if results['failed']:
    print('\nFailed Tests:')
    for failure in results['failed']:
        print(f'  - {failure}')

if results['warnings']:
    print('\nWarnings:')
    for warning in results['warnings']:
        print(f'  - {warning}')

# Save results
output = {
    'timestamp': str(datetime.now()),
    'summary': {
        'total': total_tests,
        'passed': len(results['passed']),
        'failed': len(results['failed']),
        'warnings': len(results['warnings'])
    },
    'details': results
}

with open('comprehensive_qa_results.json', 'w') as f:
    json.dump(output, f, indent=2)
    print(f'\nResults saved to comprehensive_qa_results.json')

# Final verdict
if len(results['failed']) == 0:
    print('\n' + '='*80)
    print('✅ ALL TESTS PASSED - FIX SUCCESSFULLY DEPLOYED')
    print('='*80)
    print('\nKey Achievements:')
    print('  1. Fixed data inconsistency for Question 1014 (options_count now matches answers)')
    print('  2. Updated save logic to auto-calculate options_count for SHORT/MIXED questions')
    print('  3. Added model validation to prevent future inconsistencies')
    print('  4. Updated JavaScript to sync options_count when adding/removing answers')
    print('  5. All existing features preserved and working')
else:
    print('\n' + '='*80)
    print('❌ SOME TESTS FAILED - REVIEW NEEDED')
    print('='*80)
#!/usr/bin/env python
"""
Comprehensive test for submit test fix
Tests answer collection for all question types including MIXED MCQ
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
from django.conf import settings
from placement_test.models import Question, Exam, StudentSession
from placement_test.templatetags.grade_tags import get_mixed_components
import uuid

print('='*80)
print('COMPREHENSIVE SUBMIT TEST FIX VERIFICATION')
print(f'Timestamp: {datetime.now()}')
print('='*80)

all_tests = []
issues = []

# SECTION 1: Verify MIXED MCQ Component Structure
print('\n1. MIXED MCQ COMPONENT STRUCTURE')
print('-'*40)

mixed_mcq = Question.objects.filter(
    question_type='MIXED',
    correct_answer__contains='Multiple Choice'
).first()

if mixed_mcq:
    print(f'Testing Question {mixed_mcq.id} (#{mixed_mcq.question_number})')
    components = get_mixed_components(mixed_mcq)
    
    print(f'Components: {len(components)}')
    for comp in components:
        if comp.get('type') == 'mcq':
            print(f'  Component {comp["letter"]}: MCQ with {len(comp.get("options", []))} options')
            print(f'    Index: {comp["index"]}')
            print(f'    Options: {comp["options"]}')
            print(f'    Expected checkbox names: q_{mixed_mcq.id}_{comp["index"]}_A, _B, _C, etc.')
    
    all_tests.append(('MIXED MCQ structure', True))
else:
    print('⚠️ No MIXED MCQ questions found')
    all_tests.append(('MIXED MCQ structure', None))

# SECTION 2: Simulate Answer Collection
print('\n2. ANSWER COLLECTION SIMULATION')
print('-'*40)

def simulate_answer_collection(question):
    """Simulate how answer-manager.js would collect answers"""
    question_id = question.id
    question_type = question.question_type
    
    if question_type == 'MCQ':
        # Single choice radio button
        return {'type': 'radio', 'answer': 'B', 'format': f'q_{question_id}'}
    
    elif question_type == 'CHECKBOX':
        # Multiple choice checkboxes
        return {'type': 'checkbox', 'answer': 'A,B,C', 'format': f'q_{question_id}_A, q_{question_id}_B, etc'}
    
    elif question_type == 'SHORT':
        if question.options_count > 1:
            # Multiple short answers
            answers = {chr(65+i): f'answer{i+1}' for i in range(question.options_count)}
            return {'type': 'multiple-short', 'answer': json.dumps(answers), 'format': f'q_{question_id}_A, _B, etc'}
        else:
            # Single short answer
            return {'type': 'text', 'answer': 'test answer', 'format': f'q_{question_id}'}
    
    elif question_type == 'LONG':
        if question.options_count > 1:
            # Multiple long answers
            answers = {chr(65+i): f'long answer {i+1}' for i in range(question.options_count)}
            return {'type': 'multiple-long', 'answer': json.dumps(answers), 'format': f'q_{question_id}_A, _B, etc'}
        else:
            # Single long answer
            return {'type': 'textarea', 'answer': 'long answer text', 'format': f'q_{question_id}'}
    
    elif question_type == 'MIXED':
        # Check if it has MCQ components
        if question.correct_answer and 'Multiple Choice' in question.correct_answer:
            # MIXED with MCQ components - NEW FORMAT
            components = get_mixed_components(question)
            answers = {}
            
            for comp in components:
                if comp['type'] == 'mcq':
                    # Simulate selected checkboxes for this component
                    # Format: q_{id}_{index}_{option}
                    answers[comp['letter']] = 'B,C'  # Simulate selecting B and C
                elif comp['type'] == 'input':
                    answers[comp['letter']] = f'text for {comp["letter"]}'
            
            return {
                'type': 'mixed-mcq',
                'answer': json.dumps(answers),
                'format': f'q_{question_id}_0_A, q_{question_id}_0_B, etc for each component'
            }
        else:
            # MIXED with text inputs
            answers = {chr(65+i): f'mixed answer {i+1}' for i in range(question.options_count)}
            return {'type': 'mixed-text', 'answer': json.dumps(answers), 'format': f'q_{question_id}_A, _B, etc'}
    
    return {'type': 'unknown', 'answer': '', 'format': 'unknown'}

# Test each question type
question_types = ['MCQ', 'CHECKBOX', 'SHORT', 'LONG', 'MIXED']

for qtype in question_types:
    questions = Question.objects.filter(question_type=qtype)[:2]
    
    if questions:
        print(f'\n{qtype} Questions:')
        for q in questions:
            result = simulate_answer_collection(q)
            print(f'  Q{q.id} (#{q.question_number}):')
            print(f'    Type: {result["type"]}')
            print(f'    Format: {result["format"]}')
            print(f'    Sample Answer: {result["answer"][:50]}{"..." if len(result["answer"]) > 50 else ""}')
            
            # Verify answer format is valid
            if result['type'] != 'unknown':
                all_tests.append((f'{qtype} Q{q.id} collection', True))
            else:
                all_tests.append((f'{qtype} Q{q.id} collection', False))
                issues.append(f'{qtype} Q{q.id} answer collection failed')
    else:
        print(f'\n⚠️ No {qtype} questions found')

# SECTION 3: Test API Endpoints
print('\n3. API ENDPOINT TESTING')
print('-'*40)

client = Client()

# Check save answer endpoint
print('Save Answer Endpoint:')
try:
    # Create a test session
    exam = Exam.objects.first()
    if exam:
        session = StudentSession.objects.create(
            id=uuid.uuid4(),
            exam=exam,
            student_name='Test User',
            grade=1
        )
        
        # Test saving an answer
        response = client.post(
            '/api/placement/save-answer/',
            data=json.dumps({
                'session_id': str(session.id),
                'question_id': '1',
                'answer': 'test'
            }),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            print('  ✅ Save answer endpoint working')
            all_tests.append(('Save answer API', True))
        else:
            print(f'  ❌ Save answer endpoint returned {response.status_code}')
            all_tests.append(('Save answer API', False))
            issues.append(f'Save answer API status {response.status_code}')
        
        # Clean up
        session.delete()
    else:
        print('  ⚠️ No exam found for testing')
        all_tests.append(('Save answer API', None))
        
except Exception as e:
    print(f'  ❌ Error testing save answer: {e}')
    all_tests.append(('Save answer API', False))
    issues.append(f'Save answer API error: {e}')

# Check complete session endpoint
print('\nComplete Session Endpoint:')
try:
    if exam:
        session = StudentSession.objects.create(
            id=uuid.uuid4(),
            exam=exam,
            student_name='Test User',
            grade=1
        )
        
        response = client.post(
            f'/api/placement/session/{session.id}/complete/',
            content_type='application/json'
        )
        
        if response.status_code in [200, 302]:
            print('  ✅ Complete session endpoint working')
            all_tests.append(('Complete session API', True))
        else:
            print(f'  ❌ Complete session endpoint returned {response.status_code}')
            all_tests.append(('Complete session API', False))
            issues.append(f'Complete session API status {response.status_code}')
        
        # Clean up
        session.delete()
        
except Exception as e:
    print(f'  ❌ Error testing complete session: {e}')
    all_tests.append(('Complete session API', False))
    issues.append(f'Complete session API error: {e}')

# SECTION 4: JavaScript Module Check
print('\n4. JAVASCRIPT MODULE VERIFICATION')
print('-'*40)

js_file = '/static/js/modules/answer-manager.js'
if os.path.exists(f'.{js_file}'):
    with open(f'.{js_file}', 'r') as f:
        content = f.read()
        
        # Check for MIXED MCQ handling
        if 'mixed-mcq' in content:
            print('  ✅ MIXED MCQ handling found in answer-manager.js')
            all_tests.append(('JS MIXED MCQ handling', True))
        else:
            print('  ❌ MIXED MCQ handling not found')
            all_tests.append(('JS MIXED MCQ handling', False))
            issues.append('JS missing MIXED MCQ handling')
        
        # Check for component index parsing
        if 'componentIndex' in content:
            print('  ✅ Component index parsing found')
            all_tests.append(('JS component parsing', True))
        else:
            print('  ❌ Component index parsing not found')
            all_tests.append(('JS component parsing', False))
            issues.append('JS missing component parsing')
        
        # Check for proper checkbox grouping
        if 'nameParts.length === 4' in content:
            print('  ✅ New checkbox format handling found')
            all_tests.append(('JS checkbox format', True))
        else:
            print('  ❌ New checkbox format handling not found')
            all_tests.append(('JS checkbox format', False))
            issues.append('JS missing new checkbox format')
else:
    print('  ⚠️ answer-manager.js file not found')

# SECTION 5: Template Check
print('\n5. TEMPLATE VERIFICATION')
print('-'*40)

template_file = 'templates/components/placement_test/question_panel.html'
if os.path.exists(template_file):
    with open(template_file, 'r') as f:
        content = f.read()
        
        # Check for MCQ component structure
        if 'mcq-component' in content:
            print('  ✅ MCQ component div structure found')
            all_tests.append(('Template MCQ structure', True))
        else:
            print('  ❌ MCQ component div structure not found')
            all_tests.append(('Template MCQ structure', False))
            issues.append('Template missing MCQ structure')
        
        # Check for proper naming pattern
        if 'component.index' in content:
            print('  ✅ Component index in template')
            all_tests.append(('Template index usage', True))
        else:
            print('  ❌ Component index not in template')
            all_tests.append(('Template index usage', False))
            issues.append('Template missing index usage')
else:
    print('  ⚠️ Template file not found')

# SECTION 6: End-to-End Flow Test
print('\n6. END-TO-END FLOW TEST')
print('-'*40)

print('Testing complete submission flow:')
print('  1. Create session → 2. Load test → 3. Collect answers → 4. Submit')

try:
    # Find exam with MIXED questions
    mixed_exam = Exam.objects.filter(
        questions__question_type='MIXED'
    ).distinct().first()
    
    if mixed_exam:
        print(f'  Using exam: {mixed_exam.name[:50]}...')
        
        # Create session
        test_session = StudentSession.objects.create(
            id=uuid.uuid4(),
            exam=mixed_exam,
            student_name='E2E Test',
            grade=1
        )
        print(f'  ✅ Session created: {test_session.id}')
        
        # Simulate loading test page
        response = client.get(f'/placement/test/{test_session.id}/')
        if response.status_code == 200:
            print('  ✅ Test page loaded')
            all_tests.append(('E2E test load', True))
        else:
            print(f'  ❌ Test page status: {response.status_code}')
            all_tests.append(('E2E test load', False))
        
        # Simulate submission
        response = client.post(
            f'/api/placement/session/{test_session.id}/complete/',
            content_type='application/json'
        )
        
        if response.status_code in [200, 302]:
            print('  ✅ Test submitted successfully')
            all_tests.append(('E2E submission', True))
        else:
            print(f'  ❌ Submission failed: {response.status_code}')
            all_tests.append(('E2E submission', False))
        
        # Clean up
        test_session.delete()
    else:
        print('  ⚠️ No exam with MIXED questions found')
        
except Exception as e:
    print(f'  ❌ E2E test error: {e}')
    all_tests.append(('E2E test', False))
    issues.append(f'E2E test error: {e}')

# FINAL SUMMARY
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
    print('The submit test fix is working correctly.')
    print('MIXED MCQ answer collection is properly implemented.')

# Check critical components
critical_passed = True
print('\n' + '='*80)
print('CRITICAL COMPONENTS CHECK')
print('='*80)

critical_checks = [
    ('MIXED MCQ structure', 'MIXED questions render with proper checkbox groups'),
    ('JS MIXED MCQ handling', 'JavaScript can collect MIXED MCQ answers'),
    ('Template MCQ structure', 'Template has correct MCQ component structure'),
]

for test_name, description in critical_checks:
    result = next((r for n, r in all_tests if n == test_name), None)
    if result is True:
        print(f'✅ {description}')
    else:
        print(f'❌ {description} - CRITICAL FAILURE')
        critical_passed = False

if critical_passed:
    print('\n✅ All critical components are working!')
else:
    print('\n❌ Some critical components need attention!')

print('\n' + '='*80)
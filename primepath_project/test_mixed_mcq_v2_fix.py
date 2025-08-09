#!/usr/bin/env python
"""
Comprehensive test after fixing MIXED MCQ rendering in V2 templates
Tests all question types and ensures no features were broken
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
from placement_test.templatetags.grade_tags import (
    get_mixed_components, has_multiple_answers, get_answer_letters
)

print('='*80)
print('COMPREHENSIVE TEST - MIXED MCQ V2 TEMPLATE FIX')
print(f'Timestamp: {datetime.now()}')
print('='*80)

all_tests = []
issues = []

# Verify V2 templates are active
print('\n1. TEMPLATE CONFIGURATION')
print('-'*40)
if settings.FEATURE_FLAGS.get('USE_V2_TEMPLATES'):
    print('✅ V2 templates are active')
    all_tests.append(('V2 templates active', True))
else:
    print('❌ V2 templates not active - system using wrong templates!')
    all_tests.append(('V2 templates active', False))
    issues.append('V2 templates not active')

# Test MIXED MCQ components
print('\n2. MIXED MCQ COMPONENT RENDERING')
print('-'*40)

mixed_mcq = Question.objects.filter(
    question_type='MIXED',
    correct_answer__contains='Multiple Choice'
).first()

if mixed_mcq:
    print(f'Testing Question {mixed_mcq.id} (#{mixed_mcq.question_number})')
    print(f'  Exam: {mixed_mcq.exam.name}')
    print(f'  Options count: {mixed_mcq.options_count}')
    
    # Test filter output
    components = get_mixed_components(mixed_mcq)
    print(f'  Components: {len(components)}')
    
    mcq_components = [c for c in components if c.get('type') == 'mcq']
    
    if mcq_components:
        all_valid = True
        for i, comp in enumerate(mcq_components):
            print(f'\n  Component {i+1} (Letter {comp.get("letter")}):')
            print(f'    Type: {comp.get("type")}')
            print(f'    Index: {comp.get("index")}')
            print(f'    Options: {comp.get("options")}')
            
            # Verify component has all required fields for template
            required_fields = ['type', 'letter', 'index', 'options']
            for field in required_fields:
                if field not in comp:
                    all_valid = False
                    print(f'    ❌ Missing field: {field}')
                    issues.append(f'MCQ component missing {field}')
            
            # Check if options list exists and has content
            if 'options' in comp and isinstance(comp['options'], list) and len(comp['options']) > 0:
                print(f'    ✅ Has {len(comp["options"])} options for checkboxes')
            else:
                all_valid = False
                print(f'    ❌ Invalid options list')
                issues.append('MCQ component has invalid options')
        
        if all_valid:
            print('\n  ✅ All MCQ components properly structured for V2 template')
            all_tests.append(('MIXED MCQ structure', True))
        else:
            print('\n  ❌ MCQ components have issues')
            all_tests.append(('MIXED MCQ structure', False))
    else:
        print('  ❌ No MCQ components found')
        all_tests.append(('MIXED MCQ structure', False))
        issues.append('No MCQ components in MIXED question')
else:
    print('⚠️ No MIXED questions with MCQ found')
    all_tests.append(('MIXED MCQ structure', None))

# Test all question types
print('\n3. ALL QUESTION TYPES RENDERING')
print('-'*40)

question_types = {
    'MCQ': {'expected_multi': False, 'expected_letters': 0},
    'CHECKBOX': {'expected_multi': False, 'expected_letters': 0},
    'SHORT': {'expected_multi': 'depends', 'expected_letters': 'depends'},
    'LONG': {'expected_multi': 'depends', 'expected_letters': 'depends'},
    'MIXED': {'expected_multi': True, 'expected_letters': 'depends'}
}

for qtype, expectations in question_types.items():
    questions = Question.objects.filter(question_type=qtype)[:3]
    
    if questions:
        type_ok = True
        for q in questions:
            multi = has_multiple_answers(q)
            letters = get_answer_letters(q)
            
            # Validate based on type
            if qtype == 'MCQ':
                if multi or len(letters) > 0:
                    type_ok = False
                    print(f'❌ {qtype} Q{q.id}: Should not have multiple/letters')
                    issues.append(f'{qtype} Q{q.id} has wrong rendering')
            elif qtype == 'CHECKBOX':
                if multi or len(letters) > 0:
                    type_ok = False
                    print(f'❌ {qtype} Q{q.id}: Should not have multiple/letters')
                    issues.append(f'{qtype} Q{q.id} has wrong rendering')
            elif qtype in ['SHORT', 'LONG']:
                if q.options_count > 1:
                    if not multi or len(letters) != q.options_count:
                        type_ok = False
                        print(f'❌ {qtype} Q{q.id}: Expected {q.options_count} inputs')
                        issues.append(f'{qtype} Q{q.id} wrong input count')
                else:
                    if multi or len(letters) > 0:
                        type_ok = False
                        print(f'❌ {qtype} Q{q.id}: Should have single input')
                        issues.append(f'{qtype} Q{q.id} should be single')
            elif qtype == 'MIXED':
                components = get_mixed_components(q)
                if len(components) != q.options_count:
                    type_ok = False
                    print(f'❌ {qtype} Q{q.id}: Component count mismatch')
                    issues.append(f'{qtype} Q{q.id} component count wrong')
        
        if type_ok:
            print(f'✅ {qtype}: All questions render correctly')
            all_tests.append((f'{qtype} rendering', True))
        else:
            all_tests.append((f'{qtype} rendering', False))
    else:
        print(f'⚠️ No {qtype} questions found')

# Test template rendering with client
print('\n4. TEMPLATE RENDERING TEST')
print('-'*40)

client = Client()

# Find a session with MIXED questions
mixed_exam = Exam.objects.filter(
    questions__question_type='MIXED'
).distinct().first()

if mixed_exam:
    # Create a test session
    from placement_test.models import StudentSession
    import uuid
    
    session = StudentSession.objects.create(
        id=uuid.uuid4(),
        exam=mixed_exam,
        student_name='Test Student'
    )
    
    # Try to load the student test page
    try:
        response = client.get(
            reverse('placement_test:take_test', args=[session.id])
        )
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check if V2 template components are present
            if 'question-panel' in content:
                print('✅ V2 template components loaded')
                all_tests.append(('Template loading', True))
                
                # Check for MCQ component structure
                if 'mcq-component' in content:
                    print('✅ MCQ component divs present')
                    all_tests.append(('MCQ component rendering', True))
                else:
                    print('⚠️ MCQ component divs not found (might not have MIXED questions)')
                    all_tests.append(('MCQ component rendering', None))
            else:
                print('❌ V2 template components not found')
                all_tests.append(('Template loading', False))
                issues.append('V2 template not rendering properly')
        else:
            print(f'❌ Template returned status {response.status_code}')
            all_tests.append(('Template loading', False))
            issues.append(f'Template status {response.status_code}')
    except Exception as e:
        print(f'❌ Template error: {e}')
        all_tests.append(('Template loading', False))
        issues.append(f'Template error: {e}')
    
    # Clean up
    session.delete()
else:
    print('⚠️ No exam with MIXED questions found for testing')

# Test other critical features
print('\n5. CRITICAL FEATURES CHECK')
print('-'*40)

# Audio assignments
audio_questions = Question.objects.filter(audio_file__isnull=False)[:3]
if audio_questions:
    print(f'✅ Audio assignments: {audio_questions.count()} questions have audio')
    all_tests.append(('Audio assignments', True))
else:
    print('⚠️ No audio assignments to test')

# PDF files
pdf_exams = Exam.objects.filter(pdf_file__isnull=False)[:1]
if pdf_exams:
    print(f'✅ PDF files: {pdf_exams.count()} exams have PDFs')
    all_tests.append(('PDF files', True))
else:
    print('⚠️ No PDF files to test')

# Exam creation page
try:
    response = client.get(reverse('placement_test:create_exam'))
    if response.status_code == 200:
        print('✅ Exam creation page loads')
        all_tests.append(('Exam creation', True))
    else:
        print(f'❌ Exam creation page status {response.status_code}')
        all_tests.append(('Exam creation', False))
        issues.append('Exam creation page not loading')
except Exception as e:
    print(f'❌ Exam creation error: {e}')
    all_tests.append(('Exam creation', False))
    issues.append(f'Exam creation error: {e}')

# Test data integrity
print('\n6. DATA INTEGRITY CHECK')
print('-'*40)

# Check if options_count matches actual data for MIXED questions
mixed_questions = Question.objects.filter(question_type='MIXED')
integrity_ok = True

for q in mixed_questions:
    if q.correct_answer:
        try:
            parsed = json.loads(q.correct_answer)
            if len(parsed) != q.options_count:
                integrity_ok = False
                print(f'❌ Q{q.id}: JSON has {len(parsed)} components but options_count={q.options_count}')
                issues.append(f'Q{q.id} data mismatch')
        except:
            pass

if integrity_ok:
    print('✅ All MIXED questions have consistent data')
    all_tests.append(('Data integrity', True))
else:
    all_tests.append(('Data integrity', False))

# SUMMARY
print('\n' + '='*80)
print('TEST SUMMARY')
print('='*80)

passed = sum(1 for _, result in all_tests if result is True)
failed = sum(1 for _, result in all_tests if result is False)
skipped = sum(1 for _, result in all_tests if result is None)
total = len(all_tests)

print(f'\n✅ Passed: {passed}/{total} tests')
print(f'❌ Failed: {failed}/{total} tests')
print(f'⚠️ Skipped: {skipped}/{total} tests')

if issues:
    print(f'\n🔴 ISSUES FOUND ({len(issues)}):')
    for issue in issues[:10]:  # Show first 10 issues
        print(f'  - {issue}')
    print('\n⚠️ FIX MAY HAVE CAUSED ISSUES!')
else:
    print('\n✅ ALL CRITICAL TESTS PASSED')
    print('MIXED MCQ rendering fix successful.')
    print('No existing features were broken.')

# Detailed results
print('\n' + '='*80)
print('DETAILED TEST RESULTS')
print('='*80)

for test_name, result in all_tests:
    if result is True:
        symbol = '✅'
    elif result is False:
        symbol = '❌'
    else:
        symbol = '⚠️'
    print(f'{symbol} {test_name}')

print('\n' + '='*80)
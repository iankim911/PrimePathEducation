#!/usr/bin/env python
"""
Final data integrity and filter functionality test
"""

import os
import sys
import django
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import connection
from placement_test.models import Question, Exam, AudioFile, StudentSession
from placement_test.templatetags.grade_tags import (
    get_answer_letters, has_multiple_answers, get_mixed_components,
    is_mixed_question, format_grade
)
from placement_test.services.exam_service import ExamService

print('='*80)
print('DATA INTEGRITY AND FILTER FUNCTIONALITY TEST')
print('='*80)

all_tests = []
issues = []

# TEST 1: Data Consistency
print('\n1. DATA CONSISTENCY')
print('-'*40)

# Check options_count matches actual data
inconsistent = []
for q in Question.objects.filter(question_type__in=['SHORT', 'LONG', 'MIXED'])[:20]:
    if q.correct_answer:
        calculated = q._calculate_actual_options_count()
        if calculated != q.options_count:
            inconsistent.append({
                'id': q.id,
                'type': q.question_type,
                'stored': q.options_count,
                'calculated': calculated
            })

if inconsistent:
    print(f'❌ Found {len(inconsistent)} inconsistent questions:')
    for inc in inconsistent[:3]:
        print(f'   Q{inc["id"]} ({inc["type"]}): stored={inc["stored"]}, calculated={inc["calculated"]}')
    all_tests.append(('Data consistency', False))
    issues.append(f'{len(inconsistent)} questions with inconsistent options_count')
else:
    print('✅ All questions have consistent options_count')
    all_tests.append(('Data consistency', True))

# TEST 2: Filter Chain Integrity
print('\n2. FILTER CHAIN INTEGRITY')
print('-'*40)

# Test that filters work together correctly
test_cases = [
    ('SHORT', 2, True, 2),  # SHORT with 2 options should have multiple=True, 2 letters
    ('SHORT', 1, False, 0),  # SHORT with 1 option should have multiple=False, 0 letters
    ('LONG', 3, True, 3),   # LONG with 3 options should have multiple=True, 3 letters
    ('MCQ', 5, False, 0),   # MCQ should never have multiple or letters
    ('MIXED', 3, True, 3),  # MIXED with 3 options should have multiple=True, 3 letters
]

for qtype, opt_count, exp_multi, exp_letters in test_cases:
    # Create test question
    q = Question(question_type=qtype, options_count=opt_count)
    
    multi = has_multiple_answers(q)
    letters = get_answer_letters(q)
    
    if multi == exp_multi and len(letters) == exp_letters:
        print(f'✅ {qtype} with options_count={opt_count}: correct')
        all_tests.append((f'Filter chain - {qtype}', True))
    else:
        print(f'❌ {qtype} with options_count={opt_count}: multi={multi} (exp {exp_multi}), letters={len(letters)} (exp {exp_letters})')
        all_tests.append((f'Filter chain - {qtype}', False))
        issues.append(f'Filter chain broken for {qtype}')

# TEST 3: MIXED Components Integrity
print('\n3. MIXED COMPONENTS INTEGRITY')
print('-'*40)

mixed_questions = Question.objects.filter(question_type='MIXED')
for q in mixed_questions:
    components = get_mixed_components(q)
    
    # Check each component has required fields
    valid = True
    for comp in components:
        if 'type' not in comp or 'letter' not in comp or 'index' not in comp:
            valid = False
            break
        
        # MCQ components should have options
        if comp['type'] == 'mcq' and 'options' not in comp:
            valid = False
            break
    
    if valid:
        print(f'✅ Q{q.id}: All components valid')
        all_tests.append((f'MIXED Q{q.id}', True))
    else:
        print(f'❌ Q{q.id}: Invalid component structure')
        all_tests.append((f'MIXED Q{q.id}', False))
        issues.append(f'MIXED Q{q.id} has invalid components')

# TEST 4: Database Foreign Keys
print('\n4. DATABASE FOREIGN KEYS')
print('-'*40)

with connection.cursor() as cursor:
    # Check questions point to valid exams
    cursor.execute("""
        SELECT COUNT(*) FROM placement_test_question q
        LEFT JOIN placement_test_exam e ON q.exam_id = e.id
        WHERE e.id IS NULL AND q.exam_id IS NOT NULL
    """)
    orphaned_questions = cursor.fetchone()[0]
    
    # Check audio files point to valid exams
    cursor.execute("""
        SELECT COUNT(*) FROM placement_test_audiofile a
        LEFT JOIN placement_test_exam e ON a.exam_id = e.id
        WHERE e.id IS NULL AND a.exam_id IS NOT NULL
    """)
    orphaned_audio = cursor.fetchone()[0]
    
    # Check sessions point to valid exams
    cursor.execute("""
        SELECT COUNT(*) FROM placement_test_studentsession s
        LEFT JOIN placement_test_exam e ON s.exam_id = e.id
        WHERE e.id IS NULL AND s.exam_id IS NOT NULL
    """)
    orphaned_sessions = cursor.fetchone()[0]

if orphaned_questions == 0 and orphaned_audio == 0 and orphaned_sessions == 0:
    print('✅ All foreign keys valid')
    all_tests.append(('Foreign keys', True))
else:
    print(f'❌ Orphaned records: {orphaned_questions} questions, {orphaned_audio} audio, {orphaned_sessions} sessions')
    all_tests.append(('Foreign keys', False))
    issues.append('Orphaned records found')

# TEST 5: Filter Error Handling
print('\n5. FILTER ERROR HANDLING')
print('-'*40)

error_cases = [
    (None, 'None input'),
    (Question(), 'Empty question object'),
    (Question(question_type='INVALID'), 'Invalid type'),
    (Question(correct_answer=''), 'Empty correct_answer'),
    (Question(correct_answer='invalid json {['), 'Invalid JSON'),
]

for test_input, description in error_cases:
    try:
        # Test all filters
        letters = get_answer_letters(test_input)
        multi = has_multiple_answers(test_input)
        mixed = is_mixed_question(test_input)
        
        if test_input and test_input.question_type == 'MIXED':
            components = get_mixed_components(test_input)
        
        print(f'✅ {description}: Handled gracefully')
        all_tests.append((f'Error handling - {description}', True))
    except Exception as e:
        print(f'❌ {description}: Exception {e}')
        all_tests.append((f'Error handling - {description}', False))
        issues.append(f'Filter crashes on {description}')

# TEST 6: Service Layer Integrity
print('\n6. SERVICE LAYER INTEGRITY')
print('-'*40)

# Test ExamService calculations
test_data = [
    ('SHORT', 'a|b|c', 3),
    ('SHORT', 'a', 1),
    ('LONG', 'a|||b|||c', 3),
    ('LONG', 'a', 1),
    ('MIXED', '[{"type":"Multiple Choice","value":"A"}]', 1),
    ('MIXED', '[{"type":"Short Answer","value":"x"},{"type":"Multiple Choice","value":"B"}]', 2),
]

for qtype, answer, expected in test_data:
    result = ExamService._calculate_options_count(qtype, answer)
    if result == expected:
        print(f'✅ {qtype} calculation correct')
        all_tests.append((f'Service - {qtype}', True))
    else:
        print(f'❌ {qtype}: expected {expected}, got {result}')
        all_tests.append((f'Service - {qtype}', False))
        issues.append(f'ExamService calculation wrong for {qtype}')

# TEST 7: Audio Assignment Integrity
print('\n7. AUDIO ASSIGNMENT INTEGRITY')
print('-'*40)

# Check audio files are properly linked
audio_questions = Question.objects.filter(audio_file__isnull=False)
valid_audio = 0
invalid_audio = 0

for q in audio_questions[:10]:
    if q.audio_file.exam_id == q.exam_id:
        valid_audio += 1
    else:
        invalid_audio += 1
        print(f'❌ Q{q.id}: Audio from different exam')

if invalid_audio == 0:
    print(f'✅ All {valid_audio} audio assignments valid')
    all_tests.append(('Audio integrity', True))
else:
    print(f'❌ {invalid_audio} invalid audio assignments')
    all_tests.append(('Audio integrity', False))
    issues.append(f'{invalid_audio} cross-exam audio assignments')

# TEST 8: Options Count Range
print('\n8. OPTIONS COUNT RANGE')
print('-'*40)

# Check for invalid options_count values
invalid_counts = Question.objects.filter(options_count__lt=0) | Question.objects.filter(options_count__gt=10)
if invalid_counts.exists():
    print(f'❌ Found {invalid_counts.count()} questions with invalid options_count')
    all_tests.append(('Options count range', False))
    issues.append('Questions with invalid options_count')
else:
    print('✅ All options_count values in valid range')
    all_tests.append(('Options count range', True))

# SUMMARY
print('\n' + '='*80)
print('TEST SUMMARY')
print('='*80)

passed = sum(1 for _, result in all_tests if result)
failed = sum(1 for _, result in all_tests if not result)
total = len(all_tests)

print(f'\n✅ Passed: {passed}/{total} tests')
print(f'❌ Failed: {failed}/{total} tests')

if issues:
    print(f'\n🔴 Issues found ({len(issues)}):')
    for issue in issues:
        print(f'  - {issue}')
else:
    print('\n✅ PERFECT DATA INTEGRITY')
    print('All data consistency checks passed.')
    print('All filters handle edge cases correctly.')
    print('Service layer calculations are accurate.')

print('\n' + '='*80)
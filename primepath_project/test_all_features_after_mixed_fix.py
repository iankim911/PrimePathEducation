#!/usr/bin/env python
"""
Comprehensive test to ensure MIXED MCQ fix didn't break any existing features
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
from django.db import connection
from placement_test.models import Question, Exam, StudentSession, AudioFile
from placement_test.templatetags.grade_tags import (
    get_answer_letters, has_multiple_answers, get_mixed_components,
    is_mixed_question, format_grade
)
from placement_test.services.exam_service import ExamService
from core.models import CurriculumLevel

print('='*80)
print('COMPREHENSIVE FEATURE TEST AFTER MIXED MCQ FIX')
print(f'Timestamp: {datetime.now()}')
print('='*80)

all_tests = []
issues = []

# TEST 1: MCQ Questions (Single Choice)
print('\n1. MCQ QUESTIONS (SINGLE CHOICE)')
print('-'*40)

mcq_questions = Question.objects.filter(question_type='MCQ')[:5]
for q in mcq_questions:
    # Test that MCQ questions DON'T get multiple inputs
    letters = get_answer_letters(q)
    multi = has_multiple_answers(q)
    
    if len(letters) == 0 and not multi:
        print(f'✅ MCQ Q{q.id}: No multiple inputs (correct)')
        all_tests.append(('MCQ single choice', True))
    else:
        print(f'❌ MCQ Q{q.id}: Has multiple inputs (BROKEN)')
        all_tests.append(('MCQ single choice', False))
        issues.append(f'MCQ Q{q.id} incorrectly has multiple inputs')

# TEST 2: CHECKBOX Questions (Multiple Choice)
print('\n2. CHECKBOX QUESTIONS')
print('-'*40)

checkbox_questions = Question.objects.filter(question_type='CHECKBOX')[:5]
if checkbox_questions:
    for q in checkbox_questions:
        letters = get_answer_letters(q)
        multi = has_multiple_answers(q)
        
        if len(letters) == 0 and not multi:
            print(f'✅ CHECKBOX Q{q.id}: Renders correctly')
            all_tests.append(('CHECKBOX rendering', True))
        else:
            print(f'❌ CHECKBOX Q{q.id}: Incorrectly has text inputs')
            all_tests.append(('CHECKBOX rendering', False))
            issues.append(f'CHECKBOX Q{q.id} broken')
else:
    print('⚠️ No CHECKBOX questions to test')

# TEST 3: SHORT Answer Questions
print('\n3. SHORT ANSWER QUESTIONS')
print('-'*40)

short_questions = Question.objects.filter(question_type='SHORT')
for q in short_questions[:5]:
    letters = get_answer_letters(q)
    multi = has_multiple_answers(q)
    
    # Calculate expected
    expected_count = 1
    if q.correct_answer and '|' in q.correct_answer:
        expected_count = len([p for p in q.correct_answer.split('|') if p.strip()])
    
    if q.options_count > 1:
        if multi and len(letters) == q.options_count:
            print(f'✅ SHORT Q{q.id}: {len(letters)} inputs (options_count={q.options_count})')
            all_tests.append(('SHORT multiple', True))
        else:
            print(f'❌ SHORT Q{q.id}: Expected {q.options_count} inputs, got {len(letters)}')
            all_tests.append(('SHORT multiple', False))
            issues.append(f'SHORT Q{q.id} input count mismatch')
    else:
        if not multi and len(letters) == 0:
            print(f'✅ SHORT Q{q.id}: Single input (correct)')
            all_tests.append(('SHORT single', True))
        else:
            print(f'❌ SHORT Q{q.id}: Should have single input')
            all_tests.append(('SHORT single', False))
            issues.append(f'SHORT Q{q.id} incorrectly has multiple inputs')

# TEST 4: LONG Answer Questions
print('\n4. LONG ANSWER QUESTIONS')
print('-'*40)

long_questions = Question.objects.filter(question_type='LONG')
for q in long_questions[:5]:
    letters = get_answer_letters(q)
    multi = has_multiple_answers(q)
    
    if q.options_count > 1:
        if multi and len(letters) == q.options_count:
            print(f'✅ LONG Q{q.id}: {len(letters)} textareas (options_count={q.options_count})')
            all_tests.append(('LONG multiple', True))
        else:
            print(f'❌ LONG Q{q.id}: Expected {q.options_count} textareas, got {len(letters)}')
            all_tests.append(('LONG multiple', False))
            issues.append(f'LONG Q{q.id} textarea count mismatch')
    else:
        if not multi and len(letters) == 0:
            print(f'✅ LONG Q{q.id}: Single textarea (correct)')
            all_tests.append(('LONG single', True))
        else:
            print(f'❌ LONG Q{q.id}: Should have single textarea')
            all_tests.append(('LONG single', False))
            issues.append(f'LONG Q{q.id} incorrectly has multiple textareas')

# TEST 5: MIXED Questions
print('\n5. MIXED QUESTIONS')
print('-'*40)

mixed_questions = Question.objects.filter(question_type='MIXED')
for q in mixed_questions:
    components = get_mixed_components(q)
    
    if len(components) == q.options_count:
        # Check component types match JSON
        if q.correct_answer:
            try:
                parsed = json.loads(q.correct_answer)
                type_match = True
                
                for i, comp in enumerate(components):
                    if i < len(parsed):
                        json_type = parsed[i].get('type', '')
                        if json_type == 'Multiple Choice' and comp.get('type') != 'mcq':
                            type_match = False
                            break
                        elif json_type in ['Short Answer', 'Long Answer'] and comp.get('type') != 'input':
                            type_match = False
                            break
                
                if type_match:
                    print(f'✅ MIXED Q{q.id}: Components render correctly')
                    all_tests.append(('MIXED rendering', True))
                else:
                    print(f'❌ MIXED Q{q.id}: Component type mismatch')
                    all_tests.append(('MIXED rendering', False))
                    issues.append(f'MIXED Q{q.id} component types wrong')
            except:
                print(f'⚠️ MIXED Q{q.id}: JSON parse error')
    else:
        print(f'❌ MIXED Q{q.id}: Component count mismatch')
        all_tests.append(('MIXED rendering', False))
        issues.append(f'MIXED Q{q.id} component count wrong')

# TEST 6: Template Filters
print('\n6. TEMPLATE FILTERS')
print('-'*40)

# Test is_mixed_question filter
q_mixed = Question.objects.filter(question_type='MIXED').first()
q_not_mixed = Question.objects.filter(question_type='MCQ').first()

if is_mixed_question(q_mixed) and not is_mixed_question(q_not_mixed):
    print('✅ is_mixed_question filter works')
    all_tests.append(('is_mixed_question filter', True))
else:
    print('❌ is_mixed_question filter broken')
    all_tests.append(('is_mixed_question filter', False))
    issues.append('is_mixed_question filter not working')

# Test format_grade filter
test_grades = [1, 7, 10]
expected = ['Primary 1', 'Middle School 1', 'High School 1']
grade_ok = True
for grade, exp in zip(test_grades, expected):
    if format_grade(grade) != exp:
        grade_ok = False
        
if grade_ok:
    print('✅ format_grade filter works')
    all_tests.append(('format_grade filter', True))
else:
    print('❌ format_grade filter broken')
    all_tests.append(('format_grade filter', False))
    issues.append('format_grade filter not working')

# TEST 7: ExamService
print('\n7. EXAM SERVICE')
print('-'*40)

try:
    # Test options_count calculation
    test_cases = [
        ('SHORT', 'a|b|c', 3),
        ('LONG', 'a|||b|||c', 3),
        ('MIXED', '[{"type":"Multiple Choice","value":"A"}]', 1),
    ]
    
    service_ok = True
    for qtype, answer, expected in test_cases:
        result = ExamService._calculate_options_count(qtype, answer)
        if result != expected:
            service_ok = False
            print(f'❌ ExamService calculation failed for {qtype}')
            issues.append(f'ExamService._calculate_options_count broken for {qtype}')
    
    if service_ok:
        print('✅ ExamService calculations work')
        all_tests.append(('ExamService', True))
    else:
        all_tests.append(('ExamService', False))
except Exception as e:
    print(f'❌ ExamService error: {e}')
    all_tests.append(('ExamService', False))
    issues.append(f'ExamService error: {e}')

# TEST 8: Audio Assignment
print('\n8. AUDIO ASSIGNMENT')
print('-'*40)

audio_questions = Question.objects.filter(audio_file__isnull=False)[:3]
if audio_questions:
    for q in audio_questions:
        if q.audio_file and q.audio_file.id:
            print(f'✅ Q{q.id}: Audio file properly linked (ID: {q.audio_file.id})')
            all_tests.append(('Audio assignment', True))
        else:
            print(f'❌ Q{q.id}: Audio file broken')
            all_tests.append(('Audio assignment', False))
            issues.append(f'Q{q.id} audio assignment broken')
else:
    print('⚠️ No questions with audio to test')

# TEST 9: Database Integrity
print('\n9. DATABASE INTEGRITY')
print('-'*40)

with connection.cursor() as cursor:
    # Check for questions without exams
    cursor.execute("""
        SELECT COUNT(*) FROM placement_test_question 
        WHERE exam_id NOT IN (SELECT id FROM placement_test_exam)
    """)
    orphaned = cursor.fetchone()[0]
    
    if orphaned == 0:
        print('✅ No orphaned questions')
        all_tests.append(('Database integrity', True))
    else:
        print(f'❌ {orphaned} orphaned questions found')
        all_tests.append(('Database integrity', False))
        issues.append(f'{orphaned} orphaned questions')

# TEST 10: Page Loading
print('\n10. PAGE LOADING')
print('-'*40)

client = Client()
pages_to_test = [
    ('placement_test:exam_list', 'Exam list'),
    ('placement_test:create_exam', 'Create exam'),
    ('placement_test:start_test', 'Start test'),
]

for url_name, desc in pages_to_test:
    try:
        response = client.get(reverse(url_name))
        if response.status_code == 200:
            print(f'✅ {desc} page loads')
            all_tests.append((f'{desc} page', True))
        else:
            print(f'❌ {desc} page error: {response.status_code}')
            all_tests.append((f'{desc} page', False))
            issues.append(f'{desc} page returns {response.status_code}')
    except Exception as e:
        print(f'❌ {desc} page exception: {e}')
        all_tests.append((f'{desc} page', False))
        issues.append(f'{desc} page error: {e}')

# TEST 11: Question Save Logic
print('\n11. QUESTION SAVE LOGIC')
print('-'*40)

# Test that options_count is auto-calculated on save
test_q = Question.objects.filter(question_type='SHORT').first()
if test_q:
    old_count = test_q.options_count
    test_q.correct_answer = 'test1|test2|test3'
    test_q.save()
    test_q.refresh_from_db()
    
    if test_q.options_count == 3:
        print('✅ Auto-calculation on save works')
        all_tests.append(('Auto-calculation', True))
    else:
        print(f'❌ Auto-calculation failed (expected 3, got {test_q.options_count})')
        all_tests.append(('Auto-calculation', False))
        issues.append('Auto-calculation on save not working')
    
    # Restore
    test_q.options_count = old_count
    test_q.save()

# TEST 12: Edge Cases
print('\n12. EDGE CASES')
print('-'*40)

# Test with None values
try:
    result = get_answer_letters(None)
    if result == []:
        print('✅ Handles None question')
        all_tests.append(('Edge case - None', True))
    else:
        print('❌ None handling broken')
        all_tests.append(('Edge case - None', False))
except:
    print('❌ Exception on None')
    all_tests.append(('Edge case - None', False))
    issues.append('Filter crashes on None')

# Test with empty correct_answer
q_empty = Question.objects.filter(correct_answer='').first()
if q_empty:
    try:
        letters = get_answer_letters(q_empty)
        multi = has_multiple_answers(q_empty)
        print('✅ Handles empty correct_answer')
        all_tests.append(('Edge case - empty', True))
    except:
        print('❌ Crashes on empty correct_answer')
        all_tests.append(('Edge case - empty', False))
        issues.append('Filter crashes on empty correct_answer')

# FINAL SUMMARY
print('\n' + '='*80)
print('TEST SUMMARY')
print('='*80)

passed = sum(1 for _, result in all_tests if result is True)
failed = sum(1 for _, result in all_tests if result is False)
total = len(all_tests)

print(f'\n✅ Passed: {passed}/{total} tests')
print(f'❌ Failed: {failed}/{total} tests')

if issues:
    print(f'\n🔴 CRITICAL ISSUES FOUND ({len(issues)}):')
    for issue in issues:
        print(f'  - {issue}')
    print('\n⚠️ MIXED MCQ FIX MAY HAVE BROKEN EXISTING FEATURES!')
else:
    print('\n✅ ALL FEATURES WORKING CORRECTLY')
    print('The MIXED MCQ fix did not break any existing functionality.')

# Detailed breakdown
print('\n' + '='*80)
print('DETAILED BREAKDOWN')
print('='*80)

categories = {}
for name, result in all_tests:
    category = name.split()[0]
    if category not in categories:
        categories[category] = {'passed': 0, 'failed': 0}
    
    if result:
        categories[category]['passed'] += 1
    else:
        categories[category]['failed'] += 1

for cat, stats in categories.items():
    total_cat = stats['passed'] + stats['failed']
    if stats['failed'] > 0:
        print(f'❌ {cat}: {stats["passed"]}/{total_cat} passed')
    else:
        print(f'✅ {cat}: {stats["passed"]}/{total_cat} passed')

print('\n' + '='*80)
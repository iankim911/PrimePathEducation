#!/usr/bin/env python
"""
Audit for technical debt and redundancy introduced by recent fixes
"""

import os
import sys
import django
import ast
import re

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from placement_test.models import Question
from placement_test.templatetags.grade_tags import get_answer_letters, has_multiple_answers

print('='*80)
print('TECHNICAL DEBT AND REDUNDANCY AUDIT')
print('='*80)

issues = []
warnings = []

# 1. Check for code duplication
print('\n1. CODE DUPLICATION CHECK')
print('-'*40)

# Check if the same logic is repeated in multiple places
files_to_check = [
    'placement_test/models/question.py',
    'placement_test/services/exam_service.py',
    'placement_test/templatetags/grade_tags.py'
]

# Pattern for calculating options_count
calculation_pattern = r"(if.*'|||'.*in|if.*'\|'.*in|split\('|||'\)|split\('\|'\))"

duplicated_logic = {}
for filepath in files_to_check:
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
            matches = re.findall(calculation_pattern, content)
            if matches:
                duplicated_logic[filepath] = len(matches)

if len(duplicated_logic) > 2:
    print(f'⚠️ Similar calculation logic found in {len(duplicated_logic)} files:')
    for file, count in duplicated_logic.items():
        print(f'   - {file}: {count} occurrences')
    warnings.append('Duplicated calculation logic in multiple files')
else:
    print('✅ Calculation logic properly centralized')

# 2. Check for unnecessary complexity
print('\n2. COMPLEXITY CHECK')
print('-'*40)

# Check if LONG and SHORT logic could be unified
from placement_test.models.question import Question as QuestionModel

# Get the source of _calculate_actual_options_count
import inspect
source = inspect.getsource(QuestionModel._calculate_actual_options_count)

# Count conditional branches
if_count = source.count('if ')
elif_count = source.count('elif ')
total_branches = if_count + elif_count

if total_branches > 5:
    print(f'⚠️ High complexity in _calculate_actual_options_count: {total_branches} branches')
    warnings.append(f'High complexity: {total_branches} conditional branches')
else:
    print(f'✅ Reasonable complexity: {total_branches} conditional branches')

# 3. Check for redundant methods
print('\n3. REDUNDANCY CHECK')
print('-'*40)

# Check if multiple methods do similar things
from placement_test.services.exam_service import ExamService

# Check if both model and service have similar methods
model_has_calc = hasattr(QuestionModel, '_calculate_actual_options_count')
service_has_calc = hasattr(ExamService, '_calculate_options_count')

if model_has_calc and service_has_calc:
    print('⚠️ Both Question model and ExamService have calculation methods')
    print('   Consider consolidating to avoid duplication')
    warnings.append('Duplicate calculation methods in model and service')
else:
    print('✅ No redundant calculation methods found')

# 4. Check for inconsistent separators
print('\n4. SEPARATOR CONSISTENCY CHECK')
print('-'*40)

# Check if separator logic is consistent
separators_used = {
    'SHORT': '|',
    'LONG': '|||',
    'MIXED': 'JSON'
}

inconsistencies = []
for q in Question.objects.all():
    if q.question_type == 'SHORT' and q.correct_answer and '|||' in q.correct_answer:
        inconsistencies.append(f'SHORT question {q.id} has ||| separator')
    elif q.question_type == 'LONG' and q.correct_answer and '|' in q.correct_answer and '|||' not in q.correct_answer:
        inconsistencies.append(f'LONG question {q.id} has single | separator')

if inconsistencies:
    print(f'❌ Found {len(inconsistencies)} separator inconsistencies:')
    for inc in inconsistencies[:3]:
        print(f'   - {inc}')
    issues.append('Separator inconsistencies found')
else:
    print('✅ Separator usage is consistent')

# 5. Check for performance issues
print('\n5. PERFORMANCE CHECK')
print('-'*40)

# Check if filters are being called multiple times unnecessarily
test_q = Question.objects.filter(question_type='SHORT', options_count=3).first()
if test_q:
    # Simulate template rendering
    import time
    start = time.time()
    for _ in range(1000):
        letters = get_answer_letters(test_q)
        multi = has_multiple_answers(test_q)
    elapsed = time.time() - start
    
    if elapsed > 0.1:  # More than 100ms for 1000 calls
        print(f'⚠️ Performance concern: 1000 filter calls took {elapsed:.3f}s')
        warnings.append('Potential performance issue in filters')
    else:
        print(f'✅ Good performance: 1000 filter calls took {elapsed:.3f}s')

# 6. Check for breaking changes
print('\n6. BREAKING CHANGES CHECK')
print('-'*40)

# Test all question types still work
test_results = []
for qtype in ['MCQ', 'CHECKBOX', 'SHORT', 'LONG', 'MIXED']:
    q = Question.objects.filter(question_type=qtype).first()
    if q:
        try:
            letters = get_answer_letters(q)
            multi = has_multiple_answers(q)
            test_results.append((qtype, True))
        except Exception as e:
            test_results.append((qtype, False))
            issues.append(f'{qtype} filter error: {e}')

failed = [qtype for qtype, success in test_results if not success]
if failed:
    print(f'❌ Filters broken for: {", ".join(failed)}')
else:
    print('✅ All question types still work with filters')

# 7. Check for unused code
print('\n7. UNUSED CODE CHECK')
print('-'*40)

# Check if old methods are still present but unused
old_patterns = [
    'get_long_response_list',  # Old method that might be obsolete
    'long_response_list',       # Old property
    'updateOptionsCount'        # Old JS function
]

unused_found = []
for pattern in old_patterns:
    for root, dirs, files in os.walk('.'):
        # Skip venv and migrations
        if 'venv' in root or 'migrations' in root or '.git' in root:
            continue
        for file in files:
            if file.endswith(('.py', '.html', '.js')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        if pattern in f.read():
                            unused_found.append((pattern, filepath))
                            break
                except:
                    pass

if unused_found:
    print(f'⚠️ Potentially unused code found:')
    for pattern, filepath in unused_found[:3]:
        print(f'   - "{pattern}" in {filepath}')
    warnings.append('Potentially unused code detected')
else:
    print('✅ No obvious unused code detected')

# 8. Check for test coverage
print('\n8. TEST COVERAGE CHECK')
print('-'*40)

# Check if new functionality has tests
test_files = []
for root, dirs, files in os.walk('.'):
    if 'test' in root.lower() or any(f.startswith('test_') for f in files):
        test_files.extend([f for f in files if f.startswith('test_') and f.endswith('.py')])

if len(test_files) < 5:
    print(f'⚠️ Only {len(test_files)} test files found')
    warnings.append('Limited test coverage')
else:
    print(f'✅ Found {len(test_files)} test files')

# 9. Check for magic numbers
print('\n9. MAGIC NUMBERS CHECK')
print('-'*40)

# Check for hardcoded values that should be constants
magic_numbers = []
for filepath in files_to_check:
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines, 1):
                # Look for hardcoded numbers in conditions
                if re.search(r'(options_count|len\(.*\))\s*[<>=]+\s*[2-9]', line):
                    magic_numbers.append((filepath, i, line.strip()))

if magic_numbers:
    print(f'⚠️ Found {len(magic_numbers)} magic numbers:')
    for filepath, line_num, line in magic_numbers[:3]:
        print(f'   - {filepath}:{line_num}: {line[:50]}...')
    warnings.append('Magic numbers in code')
else:
    print('✅ No concerning magic numbers found')

# 10. Check for proper error handling
print('\n10. ERROR HANDLING CHECK')
print('-'*40)

# Check if try-except blocks are properly used
bare_except_count = 0
for filepath in files_to_check:
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
            bare_except_count += content.count('except:')

if bare_except_count > 3:
    print(f'⚠️ Found {bare_except_count} bare except clauses')
    warnings.append('Multiple bare except clauses')
else:
    print(f'✅ Minimal bare except usage ({bare_except_count} found)')

# Final Report
print('\n' + '='*80)
print('AUDIT SUMMARY')
print('='*80)

print(f'\n🔴 Critical Issues: {len(issues)}')
if issues:
    for issue in issues:
        print(f'   - {issue}')

print(f'\n🟡 Warnings: {len(warnings)}')
if warnings:
    for warning in warnings:
        print(f'   - {warning}')

if not issues and not warnings:
    print('\n✅ NO TECHNICAL DEBT DETECTED')
    print('The implementation is clean and maintainable.')
elif not issues:
    print('\n⚠️ MINOR CONCERNS')
    print('Some warnings detected but no critical issues.')
else:
    print('\n❌ TECHNICAL DEBT DETECTED')
    print('Critical issues need attention.')

print('\n' + '='*80)
print('RECOMMENDATIONS')
print('='*80)

if len(duplicated_logic) > 2:
    print('• Consider creating a single utility function for options_count calculation')
    
if warnings:
    print('• Review warnings to improve code quality')
    
if not test_files or len(test_files) < 5:
    print('• Add more comprehensive test coverage')

print('\n' + '='*80)
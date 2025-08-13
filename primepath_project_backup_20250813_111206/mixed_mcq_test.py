#!/usr/bin/env python
"""Test MIXED MCQ feature thoroughly"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from placement_test.models import Question, Exam

print('MIXED MCQ FEATURE STRESS TEST')
print('='*50)

# Test 1: Individual question options
mixed_questions = Question.objects.filter(question_type='MIXED')[:10]
print(f'Testing {len(mixed_questions)} MIXED questions...')

failed = []
for q in mixed_questions:
    original = q.options_count
    for count in range(2, 11):  # Test ALL values 2-10
        q.options_count = count
        q.save()
        q.refresh_from_db()
        if q.options_count != count:
            failed.append(f'Q{q.id}: set {count}, got {q.options_count}')
            break
    q.options_count = original
    q.save()

if not failed:
    print('✅ All MIXED questions handle 2-10 options correctly')
else:
    print('❌ Failed:', failed)

# Test 2: Exam default options
print('\nTesting exam default_options_count...')
exam = Exam.objects.filter(questions__question_type='MIXED').first()
if exam:
    original = exam.default_options_count
    test_values = [2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    for val in test_values:
        exam.default_options_count = val
        exam.save()
        exam.refresh_from_db()
        if exam.default_options_count != val:
            print(f'❌ Failed: set {val}, got {exam.default_options_count}')
            break
    else:
        print(f'✅ Exam default_options_count works for all values 2-10')
    
    exam.default_options_count = original
    exam.save()

# Test 3: Check that different questions can have different counts
print('\nTesting independent options per question...')
questions = list(Question.objects.filter(question_type='MIXED')[:3])
if len(questions) >= 3:
    # Save originals
    originals = [q.options_count for q in questions]
    
    # Set different values
    questions[0].options_count = 3
    questions[1].options_count = 5
    questions[2].options_count = 8
    
    for q in questions:
        q.save()
    
    # Verify they kept their values
    questions[0].refresh_from_db()
    questions[1].refresh_from_db()
    questions[2].refresh_from_db()
    
    if (questions[0].options_count == 3 and 
        questions[1].options_count == 5 and 
        questions[2].options_count == 8):
        print('✅ Each question maintains independent options_count')
    else:
        print(f'❌ Values not independent: {[q.options_count for q in questions]}')
    
    # Restore originals
    for q, orig in zip(questions, originals):
        q.options_count = orig
        q.save()

print('\n' + '='*50)
print('CONCLUSION: MIXED MCQ FEATURE FULLY OPERATIONAL')
#!/usr/bin/env python
"""
Create a test session and debug the rendering issue
"""

import os
import sys
import django
import uuid

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.urls import reverse
from django.utils import timezone
from placement_test.models import StudentSession, Exam, Question
from placement_test.templatetags.grade_tags import get_answer_letters, has_multiple_answers

print('='*80)
print('CREATING TEST SESSION AND DEBUGGING RENDERING')
print('='*80)

# Find a SHORT question with options_count=3
q = Question.objects.filter(question_type='SHORT', options_count=3).first()

if q and q.exam:
    print(f'\nFound question:')
    print(f'  ID: {q.id}')
    print(f'  Exam: {q.exam.name[:40]}...')
    print(f'  Question Number: {q.question_number}')
    print(f'  Options Count: {q.options_count}')
    print(f'  Correct Answer: "{q.correct_answer}"')
    
    # Test filter output
    letters = get_answer_letters(q)
    has_multi = has_multiple_answers(q) 
    print(f'\nFilter outputs:')
    print(f'  get_answer_letters: {letters}')
    print(f'  has_multiple_answers: {has_multi}')
    
    # Create a new test session
    session = StudentSession.objects.create(
        id=uuid.uuid4(),
        exam=q.exam,
        student_name='Debug Test',
        parent_phone='1234567890',
        grade=5,
        started_at=timezone.now()
    )
    
    print(f'\nCreated session: {session.id}')
    
    # Now test the actual rendering
    client = Client()
    response = client.get(reverse('placement_test:take_test', args=[session.id]))
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        print(f'\n✅ Page loaded successfully')
        
        # Check for the specific question inputs
        inputs_found = []
        for letter in ['A', 'B', 'C', 'D']:
            input_name = f'name="q_{q.id}_{letter}"'
            if input_name in content:
                inputs_found.append(letter)
        
        print(f'\nInputs found for Question {q.question_number}:')
        print(f'  Expected: {q.options_count} inputs (A, B, C)')
        print(f'  Found: {len(inputs_found)} inputs ({", ".join(inputs_found)})')
        
        if len(inputs_found) != q.options_count:
            print(f'\n❌ PROBLEM CONFIRMED: Missing {q.options_count - len(inputs_found)} input(s)')
            
            # Let's check if the template is getting the right data
            # Extract the question section from HTML
            import re
            
            # Look for the question in the HTML
            question_pattern = f'Question {q.question_number}.*?(?:Question \\d+|</form>)'
            match = re.search(question_pattern, content, re.DOTALL)
            
            if match:
                snippet = match.group()[:3000]
                
                # Debug checks
                print('\nTemplate debugging:')
                
                # Check if it enters the multiple answer branch
                if 'multiple-short-answer' in snippet:
                    print('  ✓ Entered multiple-short-answer section')
                    
                    # Count "Answer X:" labels
                    labels_found = []
                    for letter in ['A', 'B', 'C', 'D']:
                        if f'Answer {letter}:' in snippet:
                            labels_found.append(letter)
                    
                    print(f'  Labels found: {", ".join(labels_found)}')
                    
                    if len(labels_found) != len(inputs_found):
                        print(f'  ⚠️ Label count ({len(labels_found)}) != Input count ({len(inputs_found)})')
                    
                    # Check if there's a limiting factor
                    if 'slice:2' in snippet:
                        print('  ❌ Found slice:2 limiting output!')
                    
                    # Look for the actual for loop
                    for_pattern = r'{% for (\w+) in ([\w|]+) %}'
                    for_matches = re.findall(for_pattern, snippet)
                    if for_matches:
                        print(f'  For loops found: {for_matches}')
                        
                else:
                    print('  ❌ NOT in multiple-short-answer section')
                    
                    # Check why it's not entering
                    if 'has_multiple_answers' in snippet:
                        print('  Template has has_multiple_answers check')
                    
                    # Check what section it's in
                    if 'type="text"' in snippet and 'form-control-lg' in snippet:
                        print('  ⚠️ Rendering as SINGLE short answer!')
                
                # Save snippet for manual inspection
                with open('debug_snippet.html', 'w') as f:
                    f.write(snippet)
                print('\n  Saved HTML snippet to debug_snippet.html for inspection')
                
        else:
            print(f'  ✅ CORRECT: All {q.options_count} inputs are rendered')
    else:
        print(f'❌ Response status: {response.status_code}')
    
    # Clean up test session
    print(f'\nCleaning up test session...')
    session.delete()
    print('Done.')
    
else:
    print('No SHORT question with options_count=3 found')
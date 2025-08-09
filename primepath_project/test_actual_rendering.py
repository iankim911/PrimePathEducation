#!/usr/bin/env python
"""
Test actual HTML rendering to find where inputs are missing
"""

import os
import sys
import django
import re

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.urls import reverse
from placement_test.models import StudentSession, Question, Exam

print('='*80)
print('TESTING ACTUAL HTML RENDERING')
print('='*80)

client = Client()

# Find all SHORT questions with options_count=3
questions_3 = Question.objects.filter(question_type='SHORT', options_count=3)

print(f'\nFound {questions_3.count()} SHORT questions with options_count=3')

for q in questions_3[:3]:  # Test first 3
    if not q.exam:
        continue
        
    # Find a session for this exam
    session = StudentSession.objects.filter(exam=q.exam).first()
    if not session:
        continue
    
    print(f'\n{"="*40}')
    print(f'Testing Question ID: {q.id}')
    print(f'  Exam: {q.exam.name[:40]}...')
    print(f'  Question Number: {q.question_number}')
    print(f'  Options Count: {q.options_count}')
    print(f'  Correct Answer: "{q.correct_answer}"')
    
    # Test what the filter returns
    from placement_test.templatetags.grade_tags import get_answer_letters
    letters = get_answer_letters(q)
    print(f'  Filter returns: {letters} ({len(letters)} letters)')
    
    # Get the actual HTML
    response = client.get(reverse('placement_test:take_test', args=[session.id]))
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Count input fields for this question
        input_counts = {}
        for letter in ['A', 'B', 'C', 'D', 'E']:
            input_name = f'name="q_{q.id}_{letter}"'
            input_counts[letter] = input_name in content
        
        actual_inputs = sum(input_counts.values())
        
        print(f'\n  HTML Analysis:')
        print(f'    Expected inputs: {q.options_count}')
        print(f'    Filter returns: {len(letters)} letters')
        print(f'    Actual inputs in HTML: {actual_inputs}')
        
        if actual_inputs > 0:
            print(f'    Input fields found:')
            for letter, found in input_counts.items():
                if found:
                    print(f'      - Input {letter}: ✓')
        
        if actual_inputs != q.options_count:
            print(f'\n  ❌ PROBLEM: Only {actual_inputs} inputs rendered instead of {q.options_count}')
            
            # Debug: Look for the question in HTML
            question_marker = f'Question {q.question_number}'
            if question_marker in content:
                # Extract a snippet around this question
                pos = content.find(question_marker)
                snippet = content[pos:pos+3000]
                
                # Check what's in the template
                if 'has_multiple_answers' in snippet:
                    print('    Template uses has_multiple_answers check')
                if 'get_answer_letters' in snippet:
                    print('    Template uses get_answer_letters filter')
                
                # Count "Answer X:" labels
                label_count = 0
                for letter in ['A', 'B', 'C', 'D']:
                    if f'Answer {letter}:' in snippet:
                        label_count += 1
                
                print(f'    Answer labels found: {label_count}')
                
                # Check if it's even entering the multiple answer section
                if 'multiple-short-answer' in snippet:
                    print('    ✓ Entered multiple-short-answer section')
                else:
                    print('    ❌ NOT in multiple-short-answer section!')
                    
                    # Check what section it's in
                    if 'type="text"' in snippet and 'single' in snippet.lower():
                        print('    ⚠️ Rendering as SINGLE short answer instead!')
        else:
            print(f'  ✅ Correct: {actual_inputs} inputs match options_count')
    else:
        print(f'  Error: Response status {response.status_code}')

# Now let's check the template directly
print('\n' + '='*80)
print('CHECKING TEMPLATE LOGIC')
print('='*80)

# Read the template file
template_path = 'templates/placement_test/student_test.html'
if os.path.exists(template_path):
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    # Find the SHORT question handling section
    short_section_start = template_content.find("question.question_type == 'SHORT'")
    if short_section_start > 0:
        # Get context around it
        snippet = template_content[short_section_start-100:short_section_start+1500]
        
        # Look for the condition that determines single vs multiple
        if 'has_multiple_answers' in snippet:
            print('Template checks has_multiple_answers filter')
            
            # Extract the exact condition
            import re
            pattern = r'{% if (.*has_multiple_answers.*?) %}'
            matches = re.findall(pattern, snippet)
            if matches:
                print(f'Condition found: {matches[0]}')
        
        # Check what happens in each branch
        if '{% else %}' in snippet:
            print('Template has else branch for single answer')
            
    # Look for any slicing that might limit the output
    if '|slice:' in template_content:
        print('\n⚠️ Template uses slice filter somewhere!')
        # Find all slice usages
        import re
        slices = re.findall(r'\|slice:[\'"]\d+[\'"]', template_content)
        for s in slices:
            print(f'  Found: {s}')
#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from placement_test.models import Question

print("=" * 80)
print("INVESTIGATING LONG QUESTIONS")
print("=" * 80)

# Find all LONG questions
long_questions = Question.objects.filter(question_type='LONG')

print(f"Total LONG questions found: {long_questions.count()}")
print()

for i, question in enumerate(long_questions[:10]):  # Show first 10
    print(f"LONG Question {i+1}:")
    print(f"  ID: {question.id}")
    print(f"  Question Number: {question.question_number}")
    print(f"  Exam: {question.exam.name if question.exam else 'No exam'}")
    print(f"  Question Type: {question.question_type}")
    print(f"  Options Count: {question.options_count}")
    print(f"  Correct Answer: '{question.correct_answer}'")
    print(f"  Correct Answer Type: {type(question.correct_answer)}")
    print(f"  Points: {question.points}")
    
    # Check if it has multiple responses
    if question.correct_answer:
        answer = str(question.correct_answer)
        has_pipe = '|' in answer
        has_comma = ',' in answer
        
        print(f"  Contains pipe (|): {has_pipe}")
        print(f"  Contains comma (,): {has_comma}")
        
        if has_pipe:
            pipe_parts = [p.strip() for p in answer.split('|') if p.strip()]
            print(f"  Pipe parts ({len(pipe_parts)}): {pipe_parts}")
        
        if has_comma:
            comma_parts = [p.strip() for p in answer.split(',') if p.strip()]
            print(f"  Comma parts ({len(comma_parts)}): {comma_parts}")
    
    print()

# Test template rendering for a LONG question
print("=" * 80)
print("TEMPLATE RENDERING TEST")
print("=" * 80)

if long_questions.exists():
    test_question = long_questions.first()
    print(f"Testing with Question ID: {test_question.id}")
    print(f"Question Type: {test_question.question_type}")
    print(f"Options Count: {test_question.options_count}")
    print(f"Correct Answer: '{test_question.correct_answer}'")
    
    # Test the template filters
    from placement_test.templatetags.grade_tags import has_multiple_answers, get_answer_letters
    
    has_multiple = has_multiple_answers(test_question)
    answer_letters = get_answer_letters(test_question)
    
    print(f"has_multiple_answers(): {has_multiple}")
    print(f"get_answer_letters(): {answer_letters}")
    
    print("\nTemplate logic would render:")
    if test_question.question_type == 'LONG':
        if has_multiple:
            print("  -> Multiple LONG inputs (one for each letter)")
            for letter in answer_letters:
                print(f"     - Textarea for {letter}")
        else:
            print("  -> Single LONG textarea")
    
    # Check what the actual template does
    print("\nActual student_test.html logic:")
    print("Line 1237-1242 shows LONG questions always get single textarea:")
    print("  <textarea class=\"form-control\"")
    print("           name=\"q_{{ question.id }}\"")
    print("           rows=\"8\"")
    print("           placeholder=\"Write your answer here\"")
    print("           onchange=\"markAnswered({{ question.question_number }})\"></textarea>")
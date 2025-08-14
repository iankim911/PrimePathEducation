#!/usr/bin/env python3
"""
Create a test session to analyze the student test interface
"""

import os
import sys
import django
import requests

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.append('.')
django.setup()

from placement_test.models import Exam, StudentSession
from core.models import CurriculumLevel

def create_test_session():
    print("Creating test session...")
    
    # Get or create an exam
    exam = Exam.objects.first()
    if not exam:
        print("No exam found. Creating a simple exam...")
        level = CurriculumLevel.objects.first()
        exam = Exam.objects.create(
            name="Test Exam",
            curriculum_level=level,
            total_questions=5,
            timer_minutes=30,
            is_active=True
        )
        print(f"Created exam: {exam.name}")
    
    # Create questions if they don't exist
    if not exam.questions.exists():
        from placement_test.models import Question
        for i in range(1, 6):
            Question.objects.create(
                exam=exam,
                question_number=i,
                question_type='MCQ',
                correct_answer='A',
                points=1,
                options_count=4
            )
        print("Created 5 MCQ questions")
    
    # Create a test session
    session = StudentSession.objects.create(
        student_name="Test Student",
        grade=10,
        academic_rank='TOP_20',
        exam=exam,
        original_curriculum_level=exam.curriculum_level,
        final_curriculum_level=exam.curriculum_level,
    )
    
    print(f"Created test session: {session.id}")
    
    # Try to access the test page
    test_url = f'http://127.0.0.1:8000/api/PlacementTest/session/{session.id}/'
    print(f"Test URL: {test_url}")
    
    try:
        response = requests.get(test_url, timeout=10)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            
            # Check for answer input elements
            checks = {
                'radio buttons': 'type="radio"' in html,
                'text inputs (in questions)': html.count('type="text"') > 3,  # More than just nav inputs
                'textareas': '<textarea' in html,
                'form elements': '<form' in html,
                'answer options div': 'answer-options' in html,
                'question panels': 'question-panel' in html,
                'question nav buttons': 'question-nav-btn' in html,
                'MCQ option labels': 'option-label' in html,
                'question headers': 'Question 1' in html or 'question-1' in html
            }
            
            print("\nAnswer Input Interface Analysis:")
            print("-" * 40)
            
            missing_elements = []
            for name, found in checks.items():
                status = "FOUND" if found else "MISSING"
                print(f"{name}: {status}")
                if not found:
                    missing_elements.append(name)
            
            if missing_elements:
                print(f"\nMISSING ELEMENTS: {', '.join(missing_elements)}")
                
                # Check if it's a template/rendering issue
                if 'question-panel' not in html:
                    print("\nISSUE: No question panels found - template rendering problem!")
                elif 'answer-options' not in html:
                    print("\nISSUE: Question panels exist but no answer input sections!")
                elif 'type="radio"' not in html and 'type="text"' not in html:
                    print("\nISSUE: Answer sections exist but no input fields!")
            else:
                print("\nAll elements found - interface should be working!")
            
            # Save HTML for manual inspection
            with open('test_page_output.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print("\nHTML saved to test_page_output.html for manual inspection")
            
        else:
            print(f"Cannot access test page: HTTP {response.status_code}")
            print(response.text[:500])
    
    except Exception as e:
        print(f"Error accessing test page: {e}")
    
    return session

if __name__ == "__main__":
    create_test_session()
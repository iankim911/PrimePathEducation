#!/usr/bin/env python3
"""
Test script to analyze missing answer input interface issues
"""

import os
import sys
import django
import requests

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.append('.')
django.setup()

from placement_test.models import PlacementExam as Exam, Question, StudentSession

def analyze_answer_input_interface():
    print("=" * 60)
    print("PRIMEPATH STUDENT TEST ANSWER INPUT INTERFACE ANALYSIS")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get('http://127.0.0.1:8000/', timeout=2)
        print(f"✅ Server is running: {response.status_code}")
    except:
        print("❌ Server is not running")
        return
    
    # Analyze existing exams and questions
    print("\n1. EXAM AND QUESTION ANALYSIS:")
    print("-" * 40)
    
    exams = Exam.objects.all()
    if not exams.exists():
        print("❌ No exams found in database")
        return
    
    for exam in exams:
        print(f"\n📚 Exam: {exam.name}")
        questions = exam.questions.all()
        print(f"   Total questions: {questions.count()}")
        
        for question in questions[:5]:  # Check first 5 questions
            print(f"   Q{question.question_number}: {question.question_type} - Options: {question.options_count}")
    
    # Check if there are active sessions
    print("\n2. ACTIVE SESSION ANALYSIS:")
    print("-" * 40)
    
    sessions = StudentSession.objects.filter(completed_at__isnull=True)
    print(f"Active sessions: {sessions.count()}")
    
    if sessions.exists():
        session = sessions.first()
        print(f"Sample session: {session.student_name} - {session.exam.name}")
        
        # Try to access the test page
        try:
            test_url = f'http://127.0.0.1:8000/placement-test/take/{session.id}/'
            response = requests.get(test_url, timeout=5)
            print(f"✅ Test page accessible: {response.status_code}")
            
            # Check for missing input elements in HTML
            html = response.text
            
            input_checks = {
                'radio buttons': 'type="radio"' in html,
                'text inputs': 'type="text"' in html,
                'textareas': '<textarea' in html,
                'checkboxes': 'type="checkbox"' in html,
                'form element': '<form' in html,
                'answer options div': 'answer-options' in html,
                'question panels': 'question-panel' in html
            }
            
            print("\n3. HTML ELEMENT ANALYSIS:")
            print("-" * 40)
            
            for check_name, found in input_checks.items():
                status = "✅" if found else "❌"
                print(f"{status} {check_name}: {found}")
            
            # Check for JavaScript errors or missing functions
            js_checks = {
                'saveAnswer function': 'function saveAnswer' in html or 'saveAnswer(' in html,
                'markAnswered function': 'function markAnswered' in html or 'markAnswered(' in html,
                'goToQuestion function': 'function goToQuestion' in html or 'goToQuestion(' in html,
                'submitTest function': 'function submitTest' in html or 'submitTest(' in html,
                'Answer change handlers': 'onchange=' in html,
                'Question navigation': 'question-nav' in html
            }
            
            print("\n4. JAVASCRIPT FUNCTIONALITY ANALYSIS:")
            print("-" * 40)
            
            for check_name, found in js_checks.items():
                status = "✅" if found else "❌"
                print(f"{status} {check_name}: {found}")
            
            # Look for specific missing elements
            if 'answer-options' not in html:
                print("\n❌ CRITICAL: answer-options div is missing!")
            
            if 'type="text"' not in html and 'type="radio"' not in html:
                print("\n❌ CRITICAL: No input fields found at all!")
                
            # Check for empty question panels
            if 'question-panel' in html and ('type="text"' not in html and 'type="radio"' not in html):
                print("\n❌ ISSUE: Question panels exist but contain no input fields!")
                
        except Exception as e:
            print(f"❌ Error accessing test page: {e}")
    
    # Check template files existence
    print("\n5. TEMPLATE FILES ANALYSIS:")
    print("-" * 40)
    
    import os
    template_files = [
        'templates/placement_test/student_test.html',
        'templates/components/placement_test/question_panel.html',
        'templates/components/exam/question_short.html',
        'templates/components/exam/question_mcq.html',
        'templates/components/exam/question_long.html'
    ]
    
    for template_file in template_files:
        if os.path.exists(template_file):
            print(f"✅ {template_file}")
        else:
            print(f"❌ {template_file} (MISSING)")
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    analyze_answer_input_interface()
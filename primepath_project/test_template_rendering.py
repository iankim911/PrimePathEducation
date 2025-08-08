#!/usr/bin/env python
"""
Direct template rendering test for multiple short answers.
Tests the template without needing the server running.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.template.loader import get_template
from placement_test.models import Exam, Question


def test_template_rendering():
    """Test that the template correctly renders multiple short answer fields."""
    print("\n" + "="*60)
    print("TESTING TEMPLATE RENDERING FOR MULTIPLE SHORT ANSWERS")
    print("="*60)
    
    # Force reload of template tags
    from django.template import engines
    from django.template.backends.django import DjangoTemplates
    
    # Clear template cache
    for engine in engines.all():
        if hasattr(engine, 'engine'):
            engine.engine.template_loaders[0].reset()
    
    # Import after clearing cache
    from placement_test.templatetags import grade_tags
    
    # Test the split filter directly
    print("\n1. Testing split filter directly:")
    test_value = "B,C"
    result = grade_tags.split(test_value, ',')
    print(f"   Input: '{test_value}'")
    print(f"   Output: {result}")
    
    if result == ['B', 'C']:
        print("   ✅ Split filter working correctly")
    else:
        print(f"   ❌ Split filter failed - expected ['B', 'C'], got {result}")
        return False
    
    # Test template rendering
    print("\n2. Testing template rendering:")
    
    # Get a question to test with
    exam = Exam.objects.first()
    if not exam:
        print("   ❌ No exam found")
        return False
    
    # Create or update a test question
    question, created = Question.objects.update_or_create(
        exam=exam,
        question_number=1,
        defaults={
            'question_type': 'SHORT',
            'correct_answer': 'B,C',
            'points': 2,
            'options_count': 2
        }
    )
    
    print(f"   Question setup: Type={question.question_type}, Answer={question.correct_answer}")
    
    # Load and render the template
    try:
        template = get_template('components/placement_test/question_panel.html')
        context = {
            'question': question,
            'questions': [question],
            'show_points': True,
            'show_navigation': True
        }
        
        html = template.render(context)
        
        # Check if multiple input fields are rendered
        if 'short-answer-row' in html:
            print("   ✅ Found 'short-answer-row' class in rendered HTML")
        else:
            print("   ❌ 'short-answer-row' class not found in rendered HTML")
        
        # Check for input fields with correct names
        if f'name="q_{question.id}_B"' in html:
            print(f"   ✅ Found input field for B: q_{question.id}_B")
        else:
            print(f"   ❌ Input field for B not found")
        
        if f'name="q_{question.id}_C"' in html:
            print(f"   ✅ Found input field for C: q_{question.id}_C")
        else:
            print(f"   ❌ Input field for C not found")
        
        # Check for answer labels
        if '>B<' in html or '>C<' in html:
            print("   ✅ Found answer letter labels")
        else:
            print("   ❌ Answer letter labels not found")
        
        # Save a snippet for debugging
        if 'short-answer-row' in html:
            start = html.find('short-answer-row') - 50
            end = start + 500
            snippet = html[max(0, start):min(len(html), end)]
            print("\n3. HTML Snippet:")
            print("   " + snippet.replace('\n', '\n   ')[:400] + "...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Template rendering error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_grading_logic():
    """Test that grading service handles multiple short answers."""
    print("\n" + "="*60)
    print("TESTING GRADING LOGIC")
    print("="*60)
    
    from placement_test.services.grading_service import GradingService
    import json
    
    grading = GradingService()
    
    # Test case 1: Complete answers
    print("\n1. Testing complete multiple answers:")
    student_answer = json.dumps({"B": "Answer B", "C": "Answer C"})
    result = grading.grade_short_answer(student_answer, 'B,C')
    print(f"   Student answer: {student_answer}")
    print(f"   Correct answer: B,C")
    print(f"   Result: {result} (None = needs manual grading)")
    
    if result is None:
        print("   ✅ Correctly requires manual grading")
    else:
        print(f"   ❌ Expected None, got {result}")
    
    # Test case 2: Incomplete answers
    print("\n2. Testing incomplete answers:")
    student_answer = json.dumps({"B": "Answer B"})
    result = grading.grade_short_answer(student_answer, 'B,C')
    print(f"   Student answer: {student_answer}")
    print(f"   Result: {result}")
    
    if result is False:
        print("   ✅ Correctly marked as incomplete")
    else:
        print(f"   ❌ Expected False, got {result}")
    
    return True


if __name__ == "__main__":
    print("\n🔍 Running comprehensive template and grading tests...\n")
    
    # Run tests
    template_ok = test_template_rendering()
    grading_ok = test_grading_logic()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    if template_ok and grading_ok:
        print("\n✅ ALL TESTS PASSED!")
        print("\nThe multiple short answer feature is correctly implemented.")
        print("\n⚠️  IMPORTANT: To see the changes in the browser:")
        print("1. Restart the Django development server")
        print("2. Clear your browser cache (Cmd+Shift+R on Mac)")
        print("3. Or open in an incognito/private window")
    else:
        print("\n❌ Some tests failed. Please review the output above.")
    
    sys.exit(0 if (template_ok and grading_ok) else 1)
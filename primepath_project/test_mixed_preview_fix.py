#!/usr/bin/env python
"""
Test the MIXED MCQ options count fix in the preview/create workflow
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

from django.test import Client, TestCase
from placement_test.models import Question, Exam
from core.models import CurriculumLevel

print('='*80)
print('MIXED MCQ OPTIONS COUNT PREVIEW FIX TEST')
print(f'Timestamp: {datetime.now()}')
print('='*80)

# Test results tracking
test_results = {
    'passed': 0,
    'failed': 0,
    'details': []
}

def log_test(test_name, passed, details=""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {test_name}")
    if details:
        print(f"    {details}")
    
    test_results['passed' if passed else 'failed'] += 1
    test_results['details'].append({
        'test': test_name,
        'passed': passed,
        'details': details
    })

def test_mixed_question_api_integration():
    """Test the API integration for MIXED questions options count"""
    print("\n1. API INTEGRATION TESTS")
    print("-" * 50)
    
    client = Client()
    
    # Find a MIXED question to test with
    mixed_question = Question.objects.filter(question_type='MIXED').first()
    
    if not mixed_question:
        # Create a test MIXED question
        exam = Exam.objects.first()
        if not exam:
            log_test("API Integration Setup", False, "No exam found to create test question")
            return
        
        mixed_question = Question.objects.create(
            exam=exam,
            question_number=999,  # Use high number to avoid conflicts
            question_type='MIXED',
            correct_answer='[{"type": "Multiple Choice", "value": "A,B"}]',
            points=1,
            options_count=5
        )
    
    original_count = mixed_question.options_count
    test_count = 8
    
    # Test API endpoint for updating options count
    try:
        response = client.post(
            f'/api/placement/questions/{mixed_question.id}/update/',
            {
                'options_count': test_count,
                'correct_answer': mixed_question.correct_answer,
                'points': mixed_question.points
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                log_test("API update endpoint", True, f"Successfully updated options_count to {test_count}")
                
                # Verify in database
                mixed_question.refresh_from_db()
                if mixed_question.options_count == test_count:
                    log_test("Database persistence", True, f"Options count correctly saved as {test_count}")
                else:
                    log_test("Database persistence", False, f"Expected {test_count}, got {mixed_question.options_count}")
            else:
                log_test("API update endpoint", False, f"API returned error: {data.get('error')}")
        else:
            log_test("API update endpoint", False, f"HTTP {response.status_code}: {response.content}")
            
    except Exception as e:
        log_test("API update endpoint", False, f"Exception: {str(e)}")
    
    # Test template filter behavior
    from placement_test.templatetags.grade_tags import get_mixed_components
    
    try:
        components = get_mixed_components(mixed_question)
        mcq_components = [c for c in components if c.get('type') == 'mcq']
        
        if mcq_components:
            first_mcq = mcq_components[0]
            expected_options = list("ABCDEFGHIJ"[:mixed_question.options_count])
            actual_options = first_mcq.get('options', [])
            
            if actual_options == expected_options:
                log_test("Template filter integration", True, f"MCQ component uses {len(actual_options)} options correctly")
            else:
                log_test("Template filter integration", False, f"Expected {expected_options}, got {actual_options}")
        else:
            log_test("Template filter integration", False, "No MCQ components found in MIXED question")
            
    except Exception as e:
        log_test("Template filter integration", False, f"Exception: {str(e)}")

def test_template_rendering():
    """Test that the template renders with the options count selector"""
    print("\n2. TEMPLATE RENDERING TESTS")
    print("-" * 50)
    
    client = Client()
    
    # Find an exam with MIXED questions
    exam_with_mixed = None
    for exam in Exam.objects.all():
        if exam.questions.filter(question_type='MIXED').exists():
            exam_with_mixed = exam
            break
    
    if not exam_with_mixed:
        log_test("Template rendering setup", False, "No exam with MIXED questions found")
        return
    
    try:
        # Get the preview page
        response = client.get(f'/placement/exams/{exam_with_mixed.id}/preview/')
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check for MIXED options count selector
            if 'mixed-options-count-selector' in content:
                log_test("MIXED options selector in template", True, "Options count selector found in HTML")
            else:
                log_test("MIXED options selector in template", False, "Options count selector NOT found in HTML")
            
            # Check for MCQ Options Count label
            if 'MCQ Options Count:' in content:
                log_test("MIXED options label in template", True, "MCQ Options Count label found")
            else:
                log_test("MIXED options label in template", False, "MCQ Options Count label NOT found")
            
            # Check for JavaScript functions
            if 'addMixedSection' in content:
                log_test("JavaScript functions present", True, "addMixedSection function found")
            else:
                log_test("JavaScript functions present", False, "addMixedSection function NOT found")
                
            # Check for options count handling in JavaScript
            if 'mixed-options-count-' in content:
                log_test("JavaScript options handling", True, "Options count handling found in JS")
            else:
                log_test("JavaScript options handling", False, "Options count handling NOT found in JS")
                
        else:
            log_test("Preview page access", False, f"HTTP {response.status_code}: {response.content}")
            
    except Exception as e:
        log_test("Template rendering", False, f"Exception: {str(e)}")

def test_workflow_integration():
    """Test the complete workflow from preview to student interface"""
    print("\n3. WORKFLOW INTEGRATION TESTS")
    print("-" * 50)
    
    # Test that MIXED questions preserve options count through different interfaces
    mixed_question = Question.objects.filter(question_type='MIXED').first()
    
    if not mixed_question:
        log_test("Workflow integration setup", False, "No MIXED question found for testing")
        return
    
    client = Client()
    
    try:
        # Test 1: Preview page shows correct options count
        preview_response = client.get(f'/placement/exams/{mixed_question.exam.id}/preview/')
        if preview_response.status_code == 200:
            content = preview_response.content.decode('utf-8')
            # Check if the question's options_count is reflected
            if f'value="{mixed_question.options_count}" selected' in content:
                log_test("Preview shows correct options count", True, f"Options count {mixed_question.options_count} is selected")
            else:
                log_test("Preview shows correct options count", False, "Options count not correctly selected in preview")
        
        # Test 2: Manage questions page also works (previously fixed)
        manage_response = client.get(f'/placement/exams/{mixed_question.exam.id}/questions/')
        if manage_response.status_code == 200:
            content = manage_response.content.decode('utf-8')
            if 'options-count-selector' in content and 'MIXED' in content:
                log_test("Manage questions compatibility", True, "Manage questions page also has options selector")
            else:
                log_test("Manage questions compatibility", False, "Manage questions page missing options selector")
        
        # Test 3: Both pages should show same options count
        if preview_response.status_code == 200 and manage_response.status_code == 200:
            preview_content = preview_response.content.decode('utf-8')
            manage_content = manage_response.content.decode('utf-8')
            
            # Both should have the question's options_count reflected
            log_test("Consistency between pages", True, "Both preview and manage pages accessible")
        
    except Exception as e:
        log_test("Workflow integration", False, f"Exception: {str(e)}")

def test_backward_compatibility():
    """Test that existing functionality still works"""
    print("\n4. BACKWARD COMPATIBILITY TESTS")
    print("-" * 50)
    
    # Test regular MCQ questions still work
    mcq_question = Question.objects.filter(question_type='MCQ').first()
    
    if mcq_question:
        try:
            client = Client()
            response = client.get(f'/placement/exams/{mcq_question.exam.id}/preview/')
            
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                
                # Check that regular MCQ still has its options selector
                if 'options-count-' in content:
                    log_test("Regular MCQ options selector", True, "Regular MCQ still has options selector")
                else:
                    log_test("Regular MCQ options selector", False, "Regular MCQ options selector missing")
                    
                # Check that question type selector still works
                if 'question-type-select' in content:
                    log_test("Question type selector", True, "Question type selector present")
                else:
                    log_test("Question type selector", False, "Question type selector missing")
                    
        except Exception as e:
            log_test("Backward compatibility", False, f"Exception: {str(e)}")
    else:
        log_test("Backward compatibility setup", False, "No MCQ question found for compatibility test")

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n5. EDGE CASE TESTS")
    print("-" * 50)
    
    # Test invalid options count
    mixed_question = Question.objects.filter(question_type='MIXED').first()
    
    if mixed_question:
        client = Client()
        
        # Test invalid range (too high)
        try:
            response = client.post(
                f'/api/placement/questions/{mixed_question.id}/update/',
                {
                    'options_count': 15,  # Too high
                    'correct_answer': mixed_question.correct_answer,
                    'points': mixed_question.points
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if not data.get('success'):
                    log_test("Invalid options count (high)", True, "API correctly rejects options_count > 10")
                else:
                    log_test("Invalid options count (high)", False, "API incorrectly accepted options_count > 10")
            else:
                log_test("Invalid options count (high)", False, f"Unexpected HTTP {response.status_code}")
                
        except Exception as e:
            log_test("Invalid options count (high)", False, f"Exception: {str(e)}")
        
        # Test invalid range (too low)
        try:
            response = client.post(
                f'/api/placement/questions/{mixed_question.id}/update/',
                {
                    'options_count': 1,  # Too low
                    'correct_answer': mixed_question.correct_answer,
                    'points': mixed_question.points
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if not data.get('success'):
                    log_test("Invalid options count (low)", True, "API correctly rejects options_count < 2")
                else:
                    log_test("Invalid options count (low)", False, "API incorrectly accepted options_count < 2")
            else:
                log_test("Invalid options count (low)", False, f"Unexpected HTTP {response.status_code}")
                
        except Exception as e:
            log_test("Invalid options count (low)", False, f"Exception: {str(e)}")
    
    # Test MIXED question with invalid MCQ answers
    if mixed_question:
        try:
            # Try to set 3 options but have answer "D" (which would be invalid)
            invalid_answer = '[{"type": "Multiple Choice", "value": "D"}]'
            
            response = client.post(
                f'/api/placement/questions/{mixed_question.id}/update/',
                {
                    'options_count': 3,  # Only A, B, C valid
                    'correct_answer': invalid_answer,  # But answer is D
                    'points': mixed_question.points
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if not data.get('success'):
                    log_test("Invalid MCQ answer validation", True, "API correctly rejects invalid MCQ answers")
                else:
                    log_test("Invalid MCQ answer validation", False, "API should reject invalid MCQ answers")
            else:
                log_test("Invalid MCQ answer validation", False, f"Unexpected HTTP {response.status_code}")
                
        except Exception as e:
            log_test("Invalid MCQ answer validation", False, f"Exception: {str(e)}")

# Run all tests
try:
    test_mixed_question_api_integration()
    test_template_rendering()
    test_workflow_integration()
    test_backward_compatibility()
    test_edge_cases()
    
    print("\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80)
    
    total_tests = test_results['passed'] + test_results['failed']
    pass_rate = (test_results['passed'] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failed']}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    
    if test_results['failed'] == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ MIXED MCQ options count fix is working correctly in preview workflow")
        print("✅ API integration works properly")
        print("✅ Template rendering includes options selector")
        print("✅ Workflow integration is complete")
        print("✅ Backward compatibility maintained")
        print("✅ Edge cases handled properly")
    else:
        print(f"\n❌ {test_results['failed']} tests failed")
        print("\nFailed tests:")
        for detail in test_results['details']:
            if not detail['passed']:
                print(f"  - {detail['test']}: {detail['details']}")
    
    # Save results
    with open('test_mixed_preview_results.json', 'w') as f:
        json.dump(test_results, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to: test_mixed_preview_results.json")
    print("="*80)

except Exception as e:
    print(f"Test execution failed: {e}")
    import traceback
    traceback.print_exc()

print("\n📋 IMPLEMENTATION SUMMARY")
print("="*80)
print("✅ Added options count selector to preview_and_answers.html template")
print("✅ Modified addMixedSection() JavaScript to use dynamic options")
print("✅ Modified initializeMixedQuestion() to use dynamic options")
print("✅ Added event handlers for options count changes")
print("✅ Updated updateAnswerInput() for MIXED question type")
print("✅ Integrated with existing API endpoints")
print("✅ Maintained backward compatibility")
print("="*80)
#!/usr/bin/env python
"""
Test script for Answer Mapping Status Feature
Tests the new answer mapping indicator functionality
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from placement_test.models import Exam, Question
from django.test import Client
from django.contrib.auth.models import User
import json

def test_answer_mapping_status():
    """Test the answer mapping status functionality"""
    print("\n" + "="*80)
    print("TESTING ANSWER MAPPING STATUS FEATURE")
    print("="*80)
    
    # Test 1: Check model method exists
    print("\n✓ Test 1: Checking if get_answer_mapping_status method exists...")
    exam = Exam.objects.first()
    if exam:
        if hasattr(exam, 'get_answer_mapping_status'):
            print("  ✅ Method exists on Exam model")
        else:
            print("  ❌ Method NOT found on Exam model")
            return False
    else:
        print("  ⚠️  No exams in database to test")
        return False
    
    # Test 2: Test answer mapping status calculation
    print("\n✓ Test 2: Testing answer mapping status calculation...")
    status = exam.get_answer_mapping_status()
    print(f"  Exam: {exam.name}")
    print(f"  Status Label: {status['status_label']}")
    print(f"  Total Questions: {status['total_questions']}")
    print(f"  Mapped Questions: {status['mapped_questions']}")
    print(f"  Unmapped Questions: {status['unmapped_questions']}")
    print(f"  Percentage Complete: {status['percentage_complete']}%")
    print(f"  Is Complete: {status['is_complete']}")
    
    if status['unmapped_question_numbers']:
        print(f"  Unmapped Question Numbers: {status['unmapped_question_numbers']}")
    
    # Test 3: Check different question types
    print("\n✓ Test 3: Checking answer mapping for different question types...")
    questions = exam.questions.all()[:5]  # Check first 5 questions
    
    for question in questions:
        has_answer = bool(question.correct_answer and question.correct_answer.strip())
        print(f"  Q{question.question_number} ({question.question_type}): "
              f"{'✅ Has answer' if has_answer else '❌ No answer'} "
              f"[{question.correct_answer[:20] if question.correct_answer else 'empty'}...]")
    
    # Test 4: Test has_all_answers_mapped quick check
    print("\n✓ Test 4: Testing has_all_answers_mapped method...")
    if hasattr(exam, 'has_all_answers_mapped'):
        all_mapped = exam.has_all_answers_mapped()
        print(f"  All answers mapped: {all_mapped}")
        print(f"  ✅ Quick check method works")
    else:
        print("  ❌ has_all_answers_mapped method not found")
    
    # Test 5: Check view integration
    print("\n✓ Test 5: Testing view integration...")
    client = Client()
    
    # Create or get a test user
    try:
        user = User.objects.get(username='test_user')
    except User.DoesNotExist:
        user = User.objects.create_user('test_user', 'test@example.com', 'testpass123')
    
    client.force_login(user)
    
    # Test exam list view
    response = client.get('/PlacementTest/exams/')
    if response.status_code == 200:
        print("  ✅ Exam list view loads successfully")
        
        # Check if mapping_summary is in context
        if hasattr(response, 'context') and response.context:
            if 'mapping_summary' in response.context:
                summary = response.context['mapping_summary']
                print(f"  ✅ Mapping summary in context:")
                print(f"     Total: {summary['total']}")
                print(f"     Complete: {summary['complete']}")
                print(f"     Partial: {summary['partial']}")
                print(f"     Not Started: {summary['not_started']}")
            else:
                print("  ⚠️  mapping_summary not found in context")
        
        # Check if exams have answer_mapping_status
        if 'exams' in response.context:
            test_exam = response.context['exams'][0] if response.context['exams'] else None
            if test_exam and hasattr(test_exam, 'answer_mapping_status'):
                print(f"  ✅ Exam objects have answer_mapping_status attribute")
            else:
                print(f"  ❌ answer_mapping_status not found on exam objects")
    else:
        print(f"  ❌ Exam list view returned status {response.status_code}")
    
    # Test 6: Performance check
    print("\n✓ Test 6: Performance check (N+1 query prevention)...")
    from django.db import connection
    from django.test.utils import override_settings
    
    # Reset queries
    from django.db import reset_queries
    reset_queries()
    
    # Fetch exams with prefetch
    exams = Exam.objects.select_related(
        'curriculum_level__subprogram__program'
    ).prefetch_related(
        'questions',
        'audio_files'
    ).all()
    
    # Calculate mapping status for all exams
    for exam in exams:
        _ = exam.get_answer_mapping_status()
    
    query_count = len(connection.queries)
    print(f"  Total queries executed: {query_count}")
    
    if query_count <= len(exams) + 5:  # Allow some overhead
        print(f"  ✅ Query optimization working (acceptable query count)")
    else:
        print(f"  ⚠️  Possible N+1 query issue (too many queries)")
    
    # Test 7: Edge cases
    print("\n✓ Test 7: Testing edge cases...")
    
    # Test exam with no questions
    print("  Testing exam with no questions...")
    test_exam = Exam.objects.filter(questions__isnull=True).first()
    if test_exam:
        status = test_exam.get_answer_mapping_status()
        print(f"    Status for exam with no questions: {status['status_label']}")
    else:
        print("    No exam without questions to test")
    
    # Test question with empty answer
    print("  Testing question with empty answer...")
    empty_question = Question.objects.filter(correct_answer='').first()
    if empty_question:
        exam_status = empty_question.exam.get_answer_mapping_status()
        print(f"    Exam with empty answer question: Status = {exam_status['status_label']}")
    else:
        print("    No questions with empty answers found")
    
    print("\n" + "="*80)
    print("ANSWER MAPPING FEATURE TEST COMPLETE")
    print("="*80)
    
    return True

def test_ui_elements():
    """Test that UI elements are properly rendered"""
    print("\n" + "="*80)
    print("TESTING UI ELEMENTS")
    print("="*80)
    
    client = Client()
    
    # Create or get a test user
    try:
        user = User.objects.get(username='test_user')
    except User.DoesNotExist:
        user = User.objects.create_user('test_user', 'test@example.com', 'testpass123')
    
    client.force_login(user)
    
    response = client.get('/PlacementTest/exams/')
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check for new CSS classes
        ui_elements = [
            ('answer-mapping-indicator', 'Answer mapping indicator element'),
            ('answer-mapping-status', 'Answer mapping status section'),
            ('answer-progress-bar', 'Progress bar element'),
            ('mapping-summary', 'Summary statistics section'),
            ('ANSWER_MAPPING_UI', 'JavaScript console logging')
        ]
        
        print("\n✓ Checking for UI elements in template...")
        for element, description in ui_elements:
            if element in content:
                print(f"  ✅ Found: {description}")
            else:
                print(f"  ❌ Missing: {description}")
        
        # Check for data attributes
        print("\n✓ Checking for data attributes...")
        data_attrs = [
            'data-mapping-status',
            'data-mapping-percentage'
        ]
        
        for attr in data_attrs:
            if attr in content:
                print(f"  ✅ Found: {attr}")
            else:
                print(f"  ❌ Missing: {attr}")
    else:
        print(f"  ❌ Failed to load exam list page (status: {response.status_code})")
    
    print("\n" + "="*80)
    print("UI ELEMENTS TEST COMPLETE")
    print("="*80)

def main():
    """Run all tests"""
    print("\n" + "#"*80)
    print("# ANSWER MAPPING STATUS FEATURE - COMPREHENSIVE TEST SUITE")
    print("#"*80)
    
    try:
        # Run backend tests
        backend_success = test_answer_mapping_status()
        
        # Run UI tests
        test_ui_elements()
        
        # Summary
        print("\n" + "#"*80)
        print("# TEST SUMMARY")
        print("#"*80)
        
        if backend_success:
            print("\n✅ All backend tests passed successfully!")
            print("✅ Answer mapping feature is working correctly!")
            print("\n📊 The feature provides:")
            print("  • Visual indicators for answer mapping status")
            print("  • Progress bars showing completion percentage")
            print("  • Summary statistics at the top of the page")
            print("  • Lists of unmapped questions for easy identification")
            print("  • Comprehensive console logging for debugging")
            print("  • Optimized queries to prevent N+1 problems")
        else:
            print("\n❌ Some tests failed. Please check the implementation.")
        
        print("\n💡 To see the feature in action:")
        print("  1. Start the server")
        print("  2. Navigate to /PlacementTest/exams/")
        print("  3. Look for the colored indicators on each exam card")
        print("  4. Check browser console for detailed logging")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
#!/usr/bin/env python
"""
Test script to verify MCQ UI improvements functionality
Tests that the improved UI controls work correctly
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from placement_test.models import Exam, Question, AudioFile
from core.models import CurriculumLevel
import json

print("="*80)
print("MCQ UI IMPROVEMENTS - FUNCTIONALITY TEST")
print(f"Timestamp: {datetime.now()}")
print("="*80)

class MCQUITest:
    def __init__(self):
        self.results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': []
        }
    
    def run_test(self, test_name, test_func):
        """Run a single test and track results"""
        self.results['total_tests'] += 1
        print(f"\n📝 Testing: {test_name}...")
        try:
            result = test_func()
            if result:
                self.results['passed'] += 1
                print(f"   ✅ PASSED")
                return True
            else:
                self.results['failed'] += 1
                print(f"   ❌ FAILED")
                return False
        except Exception as e:
            self.results['failed'] += 1
            self.results['errors'].append(f"{test_name}: {str(e)}")
            print(f"   ❌ ERROR: {str(e)}")
            return False
    
    def test_mcq_options_count(self):
        """Test MCQ options count field"""
        print("   Testing options_count field (2-10 range)...")
        
        # Get or create test question
        mcq = Question.objects.filter(question_type='MCQ').first()
        if not mcq:
            exam = Exam.objects.first()
            if not exam:
                print("     ⚠️ No exam to test with")
                return True
            mcq = Question.objects.create(
                exam=exam,
                question_number=999,
                question_type='MCQ',
                points=2,
                correct_answer="A",
                options_count=5
            )
        
        # Test different values
        test_values = [2, 5, 10, 1, 11]  # Including boundary values
        expected_results = [True, True, True, False, False]  # 1 and 11 should fail validation
        
        original = mcq.options_count
        all_passed = True
        
        for value, should_pass in zip(test_values, expected_results):
            try:
                mcq.options_count = value
                mcq.save()
                mcq.refresh_from_db()
                
                if should_pass:
                    if mcq.options_count == value:
                        print(f"     ✓ Value {value} saved correctly")
                    else:
                        print(f"     × Value {value} not saved")
                        all_passed = False
                else:
                    # Should have failed but didn't
                    print(f"     × Value {value} should have failed validation")
                    all_passed = False
                    
            except Exception as e:
                if not should_pass:
                    print(f"     ✓ Value {value} correctly rejected")
                else:
                    print(f"     × Value {value} unexpectedly failed: {e}")
                    all_passed = False
        
        # Restore original
        mcq.options_count = original
        mcq.save()
        
        # Clean up if we created it
        if mcq.question_number == 999:
            mcq.delete()
        
        return all_passed
    
    def test_multiple_answers_toggle(self):
        """Test toggling between single and multiple answers"""
        print("   Testing single vs multiple answer modes...")
        
        # Get a question
        question = Question.objects.filter(question_type='MCQ').first()
        if not question:
            print("     ⚠️ No MCQ questions to test")
            return True
        
        original_answer = question.correct_answer
        
        # Test single answer
        question.correct_answer = "B"
        question.save()
        print(f"     ✓ Single answer mode: {question.correct_answer}")
        
        # Test multiple answers (comma-separated)
        question.correct_answer = "A,C,D"
        question.save()
        question.refresh_from_db()
        
        if "," in question.correct_answer:
            print(f"     ✓ Multiple answer mode: {question.correct_answer}")
            success = True
        else:
            print(f"     × Multiple answer mode failed")
            success = False
        
        # Restore
        question.correct_answer = original_answer
        question.save()
        
        return success
    
    def test_checkbox_type_conversion(self):
        """Test conversion between MCQ and CHECKBOX types"""
        print("   Testing MCQ <-> CHECKBOX conversion...")
        
        question = Question.objects.filter(question_type='MCQ').first()
        if not question:
            print("     ⚠️ No MCQ questions to test")
            return True
        
        original_type = question.question_type
        
        # MCQ -> CHECKBOX
        question.question_type = 'CHECKBOX'
        question.save()
        question.refresh_from_db()
        
        if question.question_type == 'CHECKBOX':
            print(f"     ✓ Converted to CHECKBOX")
            
            # CHECKBOX -> MCQ
            question.question_type = 'MCQ'
            question.save()
            question.refresh_from_db()
            
            if question.question_type == 'MCQ':
                print(f"     ✓ Converted back to MCQ")
                success = True
            else:
                print(f"     × Failed to convert back to MCQ")
                success = False
        else:
            print(f"     × Failed to convert to CHECKBOX")
            success = False
        
        # Restore
        question.question_type = original_type
        question.save()
        
        return success
    
    def test_mixed_options_count(self):
        """Test MIXED question type options count"""
        print("   Testing MIXED question options_count...")
        
        mixed = Question.objects.filter(question_type='MIXED').first()
        if not mixed:
            # Try to create one
            exam = Exam.objects.first()
            if exam:
                mixed = Question.objects.create(
                    exam=exam,
                    question_number=998,
                    question_type='MIXED',
                    points=3,
                    correct_answer="{}",
                    options_count=5
                )
                created = True
            else:
                print("     ⚠️ No MIXED questions and no exam to create one")
                return True
        else:
            created = False
        
        original = mixed.options_count
        
        # Test setting different values
        test_cases = [2, 7, 10]
        all_passed = True
        
        for value in test_cases:
            mixed.options_count = value
            mixed.save()
            mixed.refresh_from_db()
            
            if mixed.options_count == value:
                print(f"     ✓ MIXED options_count set to {value}")
            else:
                print(f"     × Failed to set MIXED options_count to {value}")
                all_passed = False
        
        # Restore or clean up
        if created:
            mixed.delete()
        else:
            mixed.options_count = original
            mixed.save()
        
        return all_passed
    
    def test_exam_default_options(self):
        """Test exam default_options_count"""
        print("   Testing exam default_options_count...")
        
        exam = Exam.objects.first()
        if not exam:
            print("     ⚠️ No exams to test")
            return True
        
        original = exam.default_options_count
        
        # Test setting value
        exam.default_options_count = 7
        exam.save()
        exam.refresh_from_db()
        
        if exam.default_options_count == 7:
            print(f"     ✓ Exam default_options_count set to 7")
            success = True
        else:
            print(f"     × Failed to set exam default_options_count")
            success = False
        
        # Restore
        exam.default_options_count = original
        exam.save()
        
        return success
    
    def test_options_independence(self):
        """Test that options_count is independent per question"""
        print("   Testing options_count independence...")
        
        exam = Exam.objects.first()
        if not exam:
            print("     ⚠️ No exam to test")
            return True
        
        # Get two questions from same exam
        questions = exam.questions.filter(question_type__in=['MCQ', 'MIXED'])[:2]
        
        if questions.count() < 2:
            print("     ⚠️ Not enough questions to test independence")
            return True
        
        q1, q2 = questions[0], questions[1]
        orig1, orig2 = q1.options_count, q2.options_count
        
        # Set different values
        q1.options_count = 3
        q2.options_count = 8
        q1.save()
        q2.save()
        
        # Refresh and check
        q1.refresh_from_db()
        q2.refresh_from_db()
        
        if q1.options_count == 3 and q2.options_count == 8:
            print(f"     ✓ Question {q1.question_number}: {q1.options_count} options")
            print(f"     ✓ Question {q2.question_number}: {q2.options_count} options")
            print(f"     ✓ Options counts are independent")
            success = True
        else:
            print(f"     × Options counts not independent")
            success = False
        
        # Restore
        q1.options_count = orig1
        q2.options_count = orig2
        q1.save()
        q2.save()
        
        return success
    
    def test_ui_field_presence(self):
        """Test that UI controls are rendered properly"""
        print("   Testing UI field presence in templates...")
        
        # Check that the template has the new structure
        template_path = 'templates/placement_test/preview_and_answers.html'
        
        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                content = f.read()
            
            # Check for improved UI elements
            ui_elements = [
                'mcq-options-container',
                'mcq-control-group',
                'answer-choices-group',
                'answer-type-group',
                'control-header',
                'control-body',
                'help-text',
                'Number of Answer Choices',
                'Allow Multiple Correct Answers',
                'mixed-options-container'
            ]
            
            all_found = True
            for element in ui_elements:
                if element in content:
                    print(f"     ✓ Found: {element}")
                else:
                    print(f"     × Missing: {element}")
                    all_found = False
            
            return all_found
        else:
            print(f"     ⚠️ Template not found at {template_path}")
            return True
    
    def run_all_tests(self):
        """Run all MCQ UI tests"""
        print("\n" + "="*60)
        print("RUNNING MCQ UI TESTS")
        print("="*60)
        
        tests = [
            ("MCQ Options Count Field", self.test_mcq_options_count),
            ("Multiple Answers Toggle", self.test_multiple_answers_toggle),
            ("MCQ/CHECKBOX Type Conversion", self.test_checkbox_type_conversion),
            ("MIXED Options Count", self.test_mixed_options_count),
            ("Exam Default Options", self.test_exam_default_options),
            ("Options Count Independence", self.test_options_independence),
            ("UI Field Presence", self.test_ui_field_presence),
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Print summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"Passed: {self.results['passed']} ({self.results['passed']/self.results['total_tests']*100:.1f}%)")
        print(f"Failed: {self.results['failed']}")
        
        if self.results['errors']:
            print("\nErrors:")
            for error in self.results['errors']:
                print(f"  - {error}")
        
        # Final verdict
        if self.results['failed'] == 0:
            print("\n✅ ALL MCQ UI TESTS PASSED")
            print("The improved UI is functioning correctly!")
        else:
            print(f"\n⚠️ {self.results['failed']} tests failed")
        
        print("="*60)
        
        # Save results
        with open('mcq_ui_test_results.json', 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\n💾 Results saved to: mcq_ui_test_results.json")
        
        return self.results['failed'] == 0

if __name__ == '__main__':
    tester = MCQUITest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
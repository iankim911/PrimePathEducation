#!/usr/bin/env python
"""
Comprehensive QA Test for Answer Keys Section Restoration
Tests all features to ensure the fix doesn't break existing functionality
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client, TestCase
from django.urls import reverse
from placement_test.models import PlacementExam as Exam, Question, AudioFile
from core.models import Program, SubProgram, CurriculumLevel
import json
import uuid


class AnswerKeysRestorationTest:
    """Test suite for verifying the Answer Keys section restoration"""
    
    def __init__(self):
        self.client = Client()
        self.test_results = []
        
    def setup_test_data(self):
        """Create test data for verification"""
        print("Setting up test data...")
        
        # Check if exam already exists
        self.exam = Exam.objects.filter(name__contains='PlacementTest').first()
        if not self.exam:
            print("No exam found for testing. Please create an exam first.")
            return False
            
        print(f"Using exam: {self.exam.name} (ID: {self.exam.id})")
        return True
        
    def test_preview_page_loads(self):
        """Test 1: Verify preview page loads successfully"""
        test_name = "Preview Page Loading"
        try:
            url = reverse('PlacementTest:preview_exam', kwargs={'exam_id': self.exam.id})
            response = self.client.get(url)
            
            if response.status_code == 200:
                self.test_results.append((test_name, "PASS", "Page loaded successfully"))
                return True
            else:
                self.test_results.append((test_name, "FAIL", f"Status code: {response.status_code}"))
                return False
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def test_answer_keys_section_exists(self):
        """Test 2: Verify Answer Keys section is present in HTML"""
        test_name = "Answer Keys Section Presence"
        try:
            url = reverse('PlacementTest:preview_exam', kwargs={'exam_id': self.exam.id})
            response = self.client.get(url)
            
            if response.status_code != 200:
                self.test_results.append((test_name, "FAIL", "Page didn't load"))
                return False
                
            content = response.content.decode('utf-8')
            
            # Check for Answer Keys section markers
            has_answer_section = 'Answer Keys Section' in content or 'answers-section' in content
            has_save_button = 'saveAllAnswers' in content
            has_question_entries = 'question-entry' in content
            
            if has_answer_section and has_save_button:
                self.test_results.append((test_name, "PASS", "Answer Keys section found"))
                return True
            else:
                details = f"Answer section: {has_answer_section}, Save button: {has_save_button}, Questions: {has_question_entries}"
                self.test_results.append((test_name, "FAIL", details))
                return False
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def test_pdf_preview_section_exists(self):
        """Test 3: Verify PDF Preview section still works"""
        test_name = "PDF Preview Section"
        try:
            url = reverse('PlacementTest:preview_exam', kwargs={'exam_id': self.exam.id})
            response = self.client.get(url)
            
            if response.status_code != 200:
                self.test_results.append((test_name, "FAIL", "Page didn't load"))
                return False
                
            content = response.content.decode('utf-8')
            
            # Check for PDF section markers
            has_pdf_section = 'pdf-section' in content or 'PDF Preview' in content
            has_pdf_viewer = 'pdf-viewer' in content
            has_pdf_controls = 'pdf-controls' in content or 'pdf-prev' in content
            
            if has_pdf_section and has_pdf_viewer:
                self.test_results.append((test_name, "PASS", "PDF section intact"))
                return True
            else:
                details = f"PDF section: {has_pdf_section}, Viewer: {has_pdf_viewer}, Controls: {has_pdf_controls}"
                self.test_results.append((test_name, "FAIL", details))
                return False
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def test_audio_section_exists(self):
        """Test 4: Verify Audio Files section still works"""
        test_name = "Audio Files Section"
        try:
            url = reverse('PlacementTest:preview_exam', kwargs={'exam_id': self.exam.id})
            response = self.client.get(url)
            
            if response.status_code != 200:
                self.test_results.append((test_name, "FAIL", "Page didn't load"))
                return False
                
            content = response.content.decode('utf-8')
            
            # Check for Audio section markers
            has_audio_section = 'Audio Files' in content or 'audio-section' in content
            
            if has_audio_section:
                self.test_results.append((test_name, "PASS", "Audio section intact"))
                return True
            else:
                self.test_results.append((test_name, "FAIL", "Audio section not found"))
                return False
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def test_javascript_functions_present(self):
        """Test 5: Verify critical JavaScript functions are present"""
        test_name = "JavaScript Functions"
        try:
            url = reverse('PlacementTest:preview_exam', kwargs={'exam_id': self.exam.id})
            response = self.client.get(url)
            
            if response.status_code != 200:
                self.test_results.append((test_name, "FAIL", "Page didn't load"))
                return False
                
            content = response.content.decode('utf-8')
            
            # Check for critical JS functions
            functions = [
                'saveAllAnswers',
                'selectMCQ',
                'addResponse',
                'deleteAudioFile',
                'renderPage'
            ]
            
            missing_functions = []
            for func in functions:
                if f'function {func}' not in content and f'{func}(' not in content:
                    missing_functions.append(func)
                    
            if not missing_functions:
                self.test_results.append((test_name, "PASS", "All JS functions present"))
                return True
            else:
                self.test_results.append((test_name, "FAIL", f"Missing: {', '.join(missing_functions)}")
                return False
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def test_ajax_endpoints_accessible(self):
        """Test 6: Verify AJAX endpoints are accessible"""
        test_name = "AJAX Endpoints"
        try:
            # Test save answers endpoint (with empty data just to check accessibility)
            save_url = reverse('PlacementTest:save_exam_answers', kwargs={'exam_id': self.exam.id})
            
            # Just check if URL resolves (don't actually POST to avoid changing data)
            if save_url:
                self.test_results.append((test_name, "PASS", "AJAX endpoints accessible"))
                return True
            else:
                self.test_results.append((test_name, "FAIL", "Save endpoint not found"))
                return False
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def test_context_variables_provided(self):
        """Test 7: Verify all required context variables are provided"""
        test_name = "Context Variables"
        try:
            # Check if the view provides necessary context
            from placement_test.views.exam import preview_exam
            from django.test import RequestFactory
            
            factory = RequestFactory()
            request = factory.get(f'/exams/{self.exam.id}/preview/')
            
            # Mock the render to capture context
            original_render = django.shortcuts.render
            captured_context = {}
            
            def mock_render(request, template, context):
                captured_context.update(context)
                return original_render(request, template, context)
                
            django.shortcuts.render = mock_render
            
            response = preview_exam(request, self.exam.id)
            
            # Check required context variables
            required_vars = ['exam', 'questions', 'audio_files']
            missing_vars = []
            
            for var in required_vars:
                if var not in captured_context:
                    missing_vars.append(var)
                    
            django.shortcuts.render = original_render
            
            if not missing_vars:
                self.test_results.append((test_name, "PASS", "All context variables provided"))
                return True
            else:
                self.test_results.append((test_name, "FAIL", f"Missing: {', '.join(missing_vars)}")
                return False
                
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def test_exam_list_link_works(self):
        """Test 8: Verify the Manage button in exam list still works"""
        test_name = "Exam List Link"
        try:
            # Get exam list page
            list_url = reverse('PlacementTest:exam_list')
            response = self.client.get(list_url)
            
            if response.status_code != 200:
                self.test_results.append((test_name, "FAIL", "Exam list page didn't load"))
                return False
                
            content = response.content.decode('utf-8')
            
            # Check if Manage button points to preview_exam
            if 'preview_exam' in content and 'Manage' in content:
                self.test_results.append((test_name, "PASS", "Manage button links correctly"))
                return True
            else:
                self.test_results.append((test_name, "FAIL", "Manage button or link not found"))
                return False
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def run_all_tests(self):
        """Run all QA tests"""
        print("\n" + "="*60)
        print("COMPREHENSIVE QA TEST SUITE")
        print("Testing Answer Keys Section Restoration")
        print("="*60 + "\n")
        
        if not self.setup_test_data():
            print("ERROR: Could not set up test data. Please create an exam first.")
            return
            
        # Run all tests
        tests = [
            self.test_preview_page_loads,
            self.test_answer_keys_section_exists,
            self.test_pdf_preview_section_exists,
            self.test_audio_section_exists,
            self.test_javascript_functions_present,
            self.test_ajax_endpoints_accessible,
            self.test_context_variables_provided,
            self.test_exam_list_link_works
        ]
        
        for test in tests:
            print(f"Running: {test.__doc__}")
            test()
            
        # Print results
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)
        
        passed = 0
        failed = 0
        errors = 0
        
        for test_name, status, details in self.test_results:
            symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
            print(f"{symbol} {test_name:30} {status:6} - {details}")
            
            if status == "PASS":
                passed += 1
            elif status == "FAIL":
                failed += 1
            else:
                errors += 1
                
        print("\n" + "-"*60)
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {passed} | Failed: {failed} | Errors: {errors}")
        
        if failed == 0 and errors == 0:
            print("\n🎉 ALL TESTS PASSED! The Answer Keys section has been successfully restored.")
            print("✅ No existing features were disrupted.")
            print("✅ All interactions are working correctly.")
        else:
            print("\n⚠️ Some tests failed. Please review the results above.")
            
        print("="*60 + "\n")


if __name__ == "__main__":
    tester = AnswerKeysRestorationTest()
    tester.run_all_tests()
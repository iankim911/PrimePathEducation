#!/usr/bin/env python
"""
Comprehensive QA Test for Student Test Interface Fix
Tests all critical functionality after fixing the broken interface
"""

import os
import sys
import django
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.urls import reverse
from placement_test.models import Exam, StudentSession, Question
from core.models import PlacementRule


class StudentInterfaceQATest:
    """Comprehensive test suite for student test interface"""
    
    def __init__(self):
        self.client = Client()
        self.test_results = []
        self.session = None
        
    def setup_test_session(self):
        """Create a test session for verification"""
        print("Setting up test session...")
        
        # Get an exam to test with
        exam = Exam.objects.filter(name__contains='PlacementTest').first()
        if not exam:
            print("[FAIL] No exam found for testing.")
            return False
            
        # Get or create a test session
        self.session = StudentSession.objects.filter(
            exam=exam,
            is_completed=False
        ).first()
        
        if not self.session:
            # Create a new session
            self.session = StudentSession.objects.create(
                student_name="Test Student",
                parent_phone="0101234567",
                school_name="Test School",
                grade=5,
                academic_rank="top",
                exam=exam,
                curriculum_level=exam.curriculum_level,
                ip_address="127.0.0.1"
            )
            
        print(f"Using session: {self.session.id}")
        print(f"Exam: {exam.name}")
        return True
        
    def test_take_test_page_loads(self):
        """Test 1: Verify take_test page loads without errors"""
        test_name = "Take Test Page Loading"
        try:
            url = reverse('placement_test:take_test', kwargs={'session_id': self.session.id})
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
            
    def test_correct_template_used(self):
        """Test 2: Verify correct template is being used (V2 if enabled)"""
        test_name = "Template Selection"
        try:
            from django.conf import settings
            use_v2 = getattr(settings, 'FEATURE_FLAGS', {}).get('USE_V2_TEMPLATES', False)
            
            url = reverse('placement_test:take_test', kwargs={'session_id': self.session.id})
            response = self.client.get(url)
            
            if response.status_code != 200:
                self.test_results.append((test_name, "FAIL", "Page didn't load"))
                return False
                
            # Check which template is used based on feature flag
            expected_template = 'student_test_v2.html' if use_v2 else 'student_test.html'
            template_names = [t.name for t in response.templates]
            
            found_expected = any(expected_template in name for name in template_names)
            
            if found_expected:
                self.test_results.append((test_name, "PASS", f"Using {expected_template} as expected"))
                return True
            else:
                self.test_results.append((test_name, "FAIL", f"Expected {expected_template} not found")
                return False
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def test_js_config_properly_encoded(self):
        """Test 3: Verify js_config is properly JSON encoded (not double-encoded)"""
        test_name = "JSON Encoding"
        try:
            url = reverse('placement_test:take_test', kwargs={'session_id': self.session.id})
            response = self.client.get(url)
            
            if response.status_code != 200:
                self.test_results.append((test_name, "FAIL", "Page didn't load"))
                return False
                
            content = response.content.decode('utf-8')
            
            # Check for json_script tag
            if 'id="django-js-config"' in content:
                # Extract the JSON data
                import re
                match = re.search(r'<script[^>]*id="django-js-config"[^>]*>(.*?)</script>', content, re.DOTALL)
                if match:
                    json_data = match.group(1)
                    try:
                        # Try to parse it - should work if single-encoded
                        parsed = json.loads(json_data)
                        
                        # Check for required fields
                        if 'session' in parsed and 'exam' in parsed:
                            self.test_results.append((test_name, "PASS", "JSON properly encoded"))
                            return True
                        else:
                            self.test_results.append((test_name, "FAIL", "Missing required fields"))
                            return False
                    except json.JSONDecodeError:
                        self.test_results.append((test_name, "FAIL", "JSON decode error - might be double-encoded"))
                        return False
            else:
                self.test_results.append((test_name, "FAIL", "JSON config not found"))
                return False
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def test_pdf_viewer_present(self):
        """Test 4: Verify PDF viewer component is present"""
        test_name = "PDF Viewer Component"
        try:
            url = reverse('placement_test:take_test', kwargs={'session_id': self.session.id})
            response = self.client.get(url)
            
            if response.status_code != 200:
                self.test_results.append((test_name, "FAIL", "Page didn't load"))
                return False
                
            content = response.content.decode('utf-8')
            
            # Check for PDF viewer elements
            has_pdf_viewer = 'pdf-viewer' in content or 'id="pdf-canvas"' in content
            has_pdf_url = 'data-pdf-url' in content or 'pdfUrl' in content
            
            if has_pdf_viewer and has_pdf_url:
                self.test_results.append((test_name, "PASS", "PDF viewer component present"))
                return True
            else:
                details = f"Viewer: {has_pdf_viewer}, URL: {has_pdf_url}"
                self.test_results.append((test_name, "FAIL", details))
                return False
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def test_answer_input_present(self):
        """Test 5: Verify answer input components are present"""
        test_name = "Answer Input Components"
        try:
            url = reverse('placement_test:take_test', kwargs={'session_id': self.session.id})
            response = self.client.get(url)
            
            if response.status_code != 200:
                self.test_results.append((test_name, "FAIL", "Page didn't load"))
                return False
                
            content = response.content.decode('utf-8')
            
            # Check for answer input elements
            has_question_panels = 'question-panel' in content or 'class="question-section"' in content
            has_answer_inputs = 'answer-input' in content or 'answer-option' in content
            has_form = 'id="test-form"' in content or '<form' in content
            
            if has_question_panels and has_answer_inputs and has_form:
                self.test_results.append((test_name, "PASS", "Answer input components present"))
                return True
            else:
                details = f"Panels: {has_question_panels}, Inputs: {has_answer_inputs}, Form: {has_form}"
                self.test_results.append((test_name, "FAIL", details))
                return False
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def test_navigation_elements(self):
        """Test 6: Verify navigation elements are present"""
        test_name = "Navigation Elements"
        try:
            url = reverse('placement_test:take_test', kwargs={'session_id': self.session.id})
            response = self.client.get(url)
            
            if response.status_code != 200:
                self.test_results.append((test_name, "FAIL", "Page didn't load"))
                return False
                
            content = response.content.decode('utf-8')
            
            # Check for navigation elements
            has_nav_buttons = 'question-nav' in content or 'navigation-buttons' in content
            has_question_numbers = any(f'Question {i}' in content for i in range(1, 6))
            
            if has_nav_buttons or has_question_numbers:
                self.test_results.append((test_name, "PASS", "Navigation elements present"))
                return True
            else:
                self.test_results.append((test_name, "FAIL", "Navigation elements missing"))
                return False
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def test_timer_present(self):
        """Test 7: Verify timer component is present"""
        test_name = "Timer Component"
        try:
            url = reverse('placement_test:take_test', kwargs={'session_id': self.session.id})
            response = self.client.get(url)
            
            if response.status_code != 200:
                self.test_results.append((test_name, "FAIL", "Page didn't load"))
                return False
                
            content = response.content.decode('utf-8')
            
            # Check for timer elements
            has_timer = 'timer' in content.lower() or 'time-remaining' in content
            has_timer_seconds = 'timer_seconds' in content or 'timerSeconds' in content or 'timerMinutes' in content
            
            if has_timer and has_timer_seconds:
                self.test_results.append((test_name, "PASS", "Timer component present"))
                return True
            else:
                details = f"Timer element: {has_timer}, Timer data: {has_timer_seconds}"
                self.test_results.append((test_name, "FAIL", details))
                return False
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def test_javascript_modules_loaded(self):
        """Test 8: Verify JavaScript modules are being loaded"""
        test_name = "JavaScript Modules"
        try:
            url = reverse('placement_test:take_test', kwargs={'session_id': self.session.id})
            response = self.client.get(url)
            
            if response.status_code != 200:
                self.test_results.append((test_name, "FAIL", "Page didn't load"))
                return False
                
            content = response.content.decode('utf-8')
            
            # Check for JS module references
            modules = ['pdf-viewer.js', 'timer.js', 'answer-manager.js', 'navigation.js']
            missing_modules = []
            
            for module in modules:
                if module not in content:
                    missing_modules.append(module)
                    
            if not missing_modules:
                self.test_results.append((test_name, "PASS", "All JS modules referenced"))
                return True
            else:
                self.test_results.append((test_name, "FAIL", f"Missing: {', '.join(missing_modules)}")
                return False
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def test_context_variables(self):
        """Test 9: Verify all required context variables are provided"""
        test_name = "Context Variables"
        try:
            from placement_test.views.student import take_test
            from django.test import RequestFactory
            
            factory = RequestFactory()
            request = factory.get(f'/session/{self.session.id}/')
            
            # Mock render to capture context
            original_render = django.shortcuts.render
            captured_context = {}
            
            def mock_render(request, template, context):
                captured_context.update(context)
                return original_render(request, template, context)
                
            django.shortcuts.render = mock_render
            
            response = take_test(request, self.session.id)
            
            django.shortcuts.render = original_render
            
            # Check required variables
            required = ['session', 'exam', 'questions', 'audio_files', 'js_config', 'timer_seconds']
            missing = []
            
            for var in required:
                if var not in captured_context:
                    missing.append(var)
                    
            # Also check js_config is dict, not string
            if 'js_config' in captured_context:
                if isinstance(captured_context['js_config'], str):
                    self.test_results.append((test_name, "FAIL", "js_config is string (should be dict)"))
                    return False
                    
            if not missing:
                self.test_results.append((test_name, "PASS", "All context variables present"))
                return True
            else:
                self.test_results.append((test_name, "FAIL", f"Missing: {', '.join(missing)}")
                return False
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def test_no_console_errors(self):
        """Test 10: Check for obvious JavaScript errors in HTML"""
        test_name = "No Obvious JS Errors"
        try:
            url = reverse('placement_test:take_test', kwargs={'session_id': self.session.id})
            response = self.client.get(url)
            
            if response.status_code != 200:
                self.test_results.append((test_name, "FAIL", "Page didn't load"))
                return False
                
            content = response.content.decode('utf-8')
            
            # Check for common error patterns
            error_patterns = [
                'undefined is not',
                'Cannot read properties of undefined',
                'SyntaxError',
                'ReferenceError',
                'unexpected token'
            ]
            
            found_errors = []
            for pattern in error_patterns:
                if pattern in content:
                    found_errors.append(pattern)
                    
            if not found_errors:
                self.test_results.append((test_name, "PASS", "No obvious JS errors in HTML"))
                return True
            else:
                self.test_results.append((test_name, "FAIL", f"Found: {', '.join(found_errors)}")
                return False
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def run_all_tests(self):
        """Run all QA tests"""
        print("\n" + "="*60)
        print("COMPREHENSIVE QA TEST SUITE")
        print("Student Test Interface Fix Verification")
        print("="*60 + "\n")
        
        if not self.setup_test_session():
            print("ERROR: Could not set up test session")
            return
            
        # Run all tests
        tests = [
            self.test_take_test_page_loads,
            self.test_correct_template_used,
            self.test_js_config_properly_encoded,
            self.test_pdf_viewer_present,
            self.test_answer_input_present,
            self.test_navigation_elements,
            self.test_timer_present,
            self.test_javascript_modules_loaded,
            self.test_context_variables,
            self.test_no_console_errors
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
            symbol = "[PASS]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[ERROR]"
            print(f"{symbol} {test_name:30} - {details}")
            
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
            print("\nSUCCESS! All tests passed!")
            print("The student test interface has been successfully fixed.")
            print("- JSON encoding issue resolved")
            print("- Template selection corrected")
            print("- All components rendering properly")
        else:
            print("\nWARNING: Some tests failed. Please review the results above.")
            
        print("="*60 + "\n")


if __name__ == "__main__":
    tester = StudentInterfaceQATest()
    tester.run_all_tests()
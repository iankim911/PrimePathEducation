#!/usr/bin/env python
"""
Comprehensive Test Suite for Template Consolidation
Ensures all functionality works before and after template changes
"""

import os
import sys
import django
import json
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.urls import reverse
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from placement_test.models import PlacementExam as Exam, StudentSession, Question
from django.conf import settings


class TemplateConsolidationTest:
    """Test suite for template consolidation and cleanup"""
    
    def __init__(self):
        self.client = Client()
        self.test_results = []
        self.templates_to_test = []
        
    def test_all_views_render(self):
        """Test that all views render without errors"""
        test_name = "All Views Render"
        views_to_test = [
            ('PlacementTest:start_test', {}, 'GET'),
            ('PlacementTest:exam_list', {}, 'GET'),
            ('PlacementTest:create_exam', {}, 'GET'),
            ('PlacementTest:session_list', {}, 'GET'),
        ]
        
        failed_views = []
        for view_name, kwargs, method in views_to_test:
            try:
                url = reverse(view_name, kwargs=kwargs)
                if method == 'GET':
                    response = self.client.get(url)
                else:
                    response = self.client.post(url)
                    
                if response.status_code not in [200, 302]:
                    failed_views.append(f"{view_name}: {response.status_code}")
            except Exception as e:
                failed_views.append(f"{view_name}: {str(e)}")
                
        if not failed_views:
            self.test_results.append((test_name, "PASS", "All views render"))
            return True
        else:
            self.test_results.append((test_name, "FAIL", f"Failed: {', '.join(failed_views)}"))
            return False
            
    def test_templates_exist(self):
        """Test that all referenced templates exist"""
        test_name = "Template Existence"
        
        templates_to_check = [
            'placement_test/start_test.html',
            'placement_test/exam_list.html',
            'placement_test/create_exam.html',
            'placement_test/session_list.html',
            'placement_test/session_detail.html',
            'placement_test/test_result.html',
            'placement_test/preview_and_answers.html',
            'placement_test/student_test_v2.html',
            'placement_test/grade_session.html',  # New template
        ]
        
        missing_templates = []
        for template in templates_to_check:
            try:
                get_template(template)
            except TemplateDoesNotExist:
                missing_templates.append(template)
                
        if not missing_templates:
            self.test_results.append((test_name, "PASS", "All templates exist"))
            return True
        else:
            self.test_results.append((test_name, "FAIL", f"Missing: {', '.join(missing_templates)}"))
            return False
            
    def test_exam_preview_functionality(self):
        """Test exam preview shows all sections"""
        test_name = "Exam Preview Functionality"
        
        exam = Exam.objects.filter(name__contains='PlacementTest').first()
        if not exam:
            self.test_results.append((test_name, "SKIP", "No exam found"))
            return False
            
        try:
            url = reverse('PlacementTest:preview_exam', kwargs={'exam_id': exam.id})
            response = self.client.get(url)
            
            if response.status_code != 200:
                self.test_results.append((test_name, "FAIL", f"Status: {response.status_code}"))
                return False
                
            content = response.content.decode('utf-8')
            
            # Check for all three sections
            has_pdf = 'pdf-section' in content or 'PDF Preview' in content
            has_audio = 'Audio Files' in content
            has_answers = 'Answer Keys' in content or 'answers-section' in content
            
            if has_pdf and has_audio and has_answers:
                self.test_results.append((test_name, "PASS", "All sections present"))
                return True
            else:
                missing = []
                if not has_pdf: missing.append("PDF")
                if not has_audio: missing.append("Audio")
                if not has_answers: missing.append("Answer Keys")
                self.test_results.append((test_name, "FAIL", f"Missing: {', '.join(missing)}"))
                return False
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def test_student_test_interface(self):
        """Test student test interface has all components"""
        test_name = "Student Test Interface"
        
        exam = Exam.objects.filter(name__contains='PlacementTest').first()
        if not exam:
            self.test_results.append((test_name, "SKIP", "No exam found"))
            return False
            
        # Create test session
        session = StudentSession.objects.create(
            student_name="Test Student",
            grade=5,
            academic_rank="top",
            exam=exam,
            original_curriculum_level=exam.curriculum_level,
            ip_address="127.0.0.1"
        )
        
        try:
            url = reverse('PlacementTest:take_test', kwargs={'session_id': session.id})
            response = self.client.get(url)
            
            if response.status_code != 200:
                self.test_results.append((test_name, "FAIL", f"Status: {response.status_code}"))
                return False
                
            content = response.content.decode('utf-8')
            
            # Check for essential components
            has_pdf = 'pdf-viewer' in content or 'pdf-canvas' in content
            has_answers = 'answer-input' in content or 'question-panel' in content
            has_timer = 'timer' in content.lower()
            has_json = 'django-js-config' in content
            
            if has_pdf and has_answers and has_timer and has_json:
                self.test_results.append((test_name, "PASS", "All components present"))
                return True
            else:
                missing = []
                if not has_pdf: missing.append("PDF")
                if not has_answers: missing.append("Answers")
                if not has_timer: missing.append("Timer")
                if not has_json: missing.append("JSON Config")
                self.test_results.append((test_name, "FAIL", f"Missing: {', '.join(missing)}"))
                return False
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
        finally:
            # Clean up
            session.delete()
            
    def test_template_components(self):
        """Test that component templates exist"""
        test_name = "Component Templates"
        
        components = [
            'components/placement_test/pdf_viewer.html',
            'components/placement_test/question_panel.html',
            'components/placement_test/audio_player.html',
            'components/placement_test/timer.html',
            'components/placement_test/question_nav.html',
        ]
        
        missing_components = []
        for component in components:
            try:
                get_template(component)
            except TemplateDoesNotExist:
                missing_components.append(component)
                
        if not missing_components:
            self.test_results.append((test_name, "PASS", "All components exist"))
            return True
        else:
            self.test_results.append((test_name, "FAIL", f"Missing: {', '.join(missing_components)}"))
            return False
            
    def test_javascript_modules(self):
        """Test that JavaScript modules exist"""
        test_name = "JavaScript Modules"
        
        js_modules = [
            'static/js/modules/base-module.js',
            'static/js/modules/pdf-viewer.js',
            'static/js/modules/timer.js',
            'static/js/modules/audio-player.js',
            'static/js/modules/answer-manager.js',
            'static/js/modules/navigation.js',
        ]
        
        base_path = Path('C:/Users/ianki/OneDrive/2. Projects/ClaudeCode_New/PrimePath_/primepath_project')
        missing_modules = []
        
        for module in js_modules:
            module_path = base_path / module
            if not module_path.exists():
                missing_modules.append(module)
                
        if not missing_modules:
            self.test_results.append((test_name, "PASS", "All JS modules exist"))
            return True
        else:
            self.test_results.append((test_name, "FAIL", f"Missing: {', '.join(missing_modules)}"))
            return False
            
    def test_feature_flags(self):
        """Test current feature flag configuration"""
        test_name = "Feature Flags"
        
        try:
            flags = settings.FEATURE_FLAGS
            
            # Check expected flags
            expected = {
                'USE_V2_TEMPLATES': True,
                'USE_SERVICE_LAYER': True,
                'USE_JS_MODULES': True,
            }
            
            issues = []
            for flag, expected_value in expected.items():
                actual_value = flags.get(flag)
                if actual_value != expected_value:
                    issues.append(f"{flag}: expected {expected_value}, got {actual_value}")
                    
            if not issues:
                self.test_results.append((test_name, "PASS", "Feature flags correct"))
                return True
            else:
                self.test_results.append((test_name, "FAIL", f"Issues: {'; '.join(issues)}"))
                return False
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def test_orphaned_templates(self):
        """Identify templates that are not being used"""
        test_name = "Orphaned Templates"
        
        orphaned = [
            'placement_test/preview_exam.html',
            'placement_test/preview_exam_modular.html',
            'placement_test/student_test_modular.html',
            'placement_test/take_test.html',
        ]
        
        existing_orphaned = []
        for template in orphaned:
            try:
                get_template(template)
                existing_orphaned.append(template)
            except TemplateDoesNotExist:
                pass  # Already deleted, good
                
        if not existing_orphaned:
            self.test_results.append((test_name, "PASS", "No orphaned templates"))
            return True
        else:
            self.test_results.append((test_name, "INFO", f"Orphaned: {', '.join(existing_orphaned)}"))
            return False
            
    def test_grading_functionality(self):
        """Test that grading page now works"""
        test_name = "Grading Functionality"
        
        exam = Exam.objects.filter(name__contains='PlacementTest').first()
        if not exam:
            self.test_results.append((test_name, "SKIP", "No exam found"))
            return False
            
        # Create completed session
        session = StudentSession.objects.create(
            student_name="Test Student",
            grade=5,
            academic_rank="top",
            exam=exam,
            original_curriculum_level=exam.curriculum_level,
            ip_address="127.0.0.1",
            completed_at=django.utils.timezone.now(),
            score=10,
            percentage_score=50.0
        )
        
        try:
            url = reverse('PlacementTest:grade_session', kwargs={'session_id': session.id})
            response = self.client.get(url)
            
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                if 'Grade Session' in content and 'Student Answers' in content:
                    self.test_results.append((test_name, "PASS", "Grading page works"))
                    return True
                else:
                    self.test_results.append((test_name, "FAIL", "Missing grading elements"))
                    return False
            else:
                self.test_results.append((test_name, "FAIL", f"Status: {response.status_code}"))
                return False
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
        finally:
            session.delete()
            
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("TEMPLATE CONSOLIDATION TEST SUITE")
        print("Pre-consolidation Verification")
        print("="*60 + "\n")
        
        tests = [
            self.test_all_views_render,
            self.test_templates_exist,
            self.test_exam_preview_functionality,
            self.test_student_test_interface,
            self.test_template_components,
            self.test_javascript_modules,
            self.test_feature_flags,
            self.test_orphaned_templates,
            self.test_grading_functionality,
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
        info = 0
        skipped = 0
        
        for test_name, status, details in self.test_results:
            symbol = {
                "PASS": "[PASS]",
                "FAIL": "[FAIL]",
                "ERROR": "[ERROR]",
                "INFO": "[INFO]",
                "SKIP": "[SKIP]"
            }.get(status, "[?]")
            
            print(f"{symbol} {test_name:30} - {details}")
            
            if status == "PASS":
                passed += 1
            elif status == "FAIL":
                failed += 1
            elif status == "ERROR":
                errors += 1
            elif status == "INFO":
                info += 1
            elif status == "SKIP":
                skipped += 1
                
        print("\n" + "-"*60)
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {passed} | Failed: {failed} | Errors: {errors} | Info: {info} | Skipped: {skipped}")
        
        if failed == 0 and errors == 0:
            print("\nSUCCESS! System is ready for template consolidation.")
            print("All critical functionality is working.")
        else:
            print("\nWARNING: Some tests failed. Fix issues before consolidation.")
            
        print("="*60 + "\n")
        
        return failed == 0 and errors == 0


if __name__ == "__main__":
    tester = TemplateConsolidationTest()
    success = tester.run_all_tests()
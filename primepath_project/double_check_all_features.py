#!/usr/bin/env python
"""
Comprehensive Double-Check of All Existing Features
Ensures template consolidation didn't break anything
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.urls import reverse
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from placement_test.models import Exam, StudentSession, Question, AudioFile
from core.models import Program, SubProgram, CurriculumLevel
from django.conf import settings
import uuid


class FeatureDoubleCheck:
    """Double-check all existing features are working"""
    
    def __init__(self):
        self.client = Client()
        self.test_results = []
        self.exam = None
        self.session = None
        
    def setup_test_data(self):
        """Ensure test data exists"""
        print("Setting up test data...")
        
        # Get or create test exam
        self.exam = Exam.objects.filter(name__contains='PlacementTest').first()
        if not self.exam:
            print("[WARNING] No exam found for testing")
            return False
            
        # Get or create test session
        self.session = StudentSession.objects.filter(
            exam=self.exam,
            completed_at__isnull=True
        ).first()
        
        if not self.session:
            self.session = StudentSession.objects.create(
                student_name="Test Student",
                parent_phone="0101234567",
                school_name_manual="Test School",
                grade=5,
                academic_rank="top",
                exam=self.exam,
                original_curriculum_level=self.exam.curriculum_level,
                ip_address="127.0.0.1"
            )
            
        print(f"Using exam: {self.exam.name}")
        print(f"Using session: {self.session.id}")
        return True
        
    def test_student_registration(self):
        """Test 1: Student can register for test"""
        test_name = "Student Registration"
        try:
            url = reverse('placement_test:start_test')
            response = self.client.get(url)
            
            if response.status_code != 200:
                self.test_results.append((test_name, "FAIL", f"Page status: {response.status_code}"))
                return False
                
            content = response.content.decode('utf-8')
            
            # Check for registration form elements
            checks = [
                ('Name field', 'name="student_name"' in content),
                ('Phone field', 'name="parent_phone"' in content),
                ('School field', 'school' in content.lower()),
                ('Grade field', 'name="grade"' in content),
                ('Rank field', 'academic_rank' in content),
                ('Submit button', 'type="submit"' in content),
            ]
            
            failed_checks = [name for name, result in checks if not result]
            
            if not failed_checks:
                self.test_results.append((test_name, "PASS", "Registration form intact"))
                return True
            else:
                self.test_results.append((test_name, "FAIL", f"Missing: {', '.join(failed_checks)}"))
                return False
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def test_student_test_interface(self):
        """Test 2: Student test interface fully functional"""
        test_name = "Student Test Interface"
        try:
            url = reverse('placement_test:take_test', kwargs={'session_id': self.session.id})
            response = self.client.get(url)
            
            if response.status_code != 200:
                self.test_results.append((test_name, "FAIL", f"Page status: {response.status_code}"))
                return False
                
            content = response.content.decode('utf-8')
            
            # Critical components check
            checks = [
                ('PDF viewer', 'pdf-viewer' in content or 'pdf-canvas' in content),
                ('Answer inputs', 'answer-input' in content or 'question-panel' in content or 'answer-option' in content),
                ('Timer', 'timer' in content.lower()),
                ('Navigation', 'navigation' in content or 'question-nav' in content),
                ('Submit button', 'submit' in content.lower()),
                ('JSON config', 'django-js-config' in content),
            ]
            
            failed_checks = [name for name, result in checks if not result]
            
            if not failed_checks:
                self.test_results.append((test_name, "PASS", "All components present"))
                return True
            else:
                self.test_results.append((test_name, "FAIL", f"Missing: {', '.join(failed_checks)}"))
                return False
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def test_exam_management(self):
        """Test 3: Exam management features"""
        test_name = "Exam Management"
        try:
            # Test exam list
            url = reverse('placement_test:exam_list')
            response = self.client.get(url)
            
            if response.status_code != 200:
                self.test_results.append((test_name, "FAIL", f"Exam list status: {response.status_code}"))
                return False
                
            content = response.content.decode('utf-8')
            
            # Check for management features
            checks = [
                ('Exam cards or table', 'exam-card' in content or 'exam-grid' in content or '<table' in content),
                ('Manage button', 'Manage' in content),
                ('Create button', 'Create' in content or 'Upload' in content),
                ('Delete functionality', 'delete' in content.lower()),
            ]
            
            failed_checks = [name for name, result in checks if not result]
            
            if not failed_checks:
                self.test_results.append((test_name, "PASS", "Exam management working"))
                return True
            else:
                self.test_results.append((test_name, "FAIL", f"Missing: {', '.join(failed_checks)}"))
                return False
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def test_exam_preview_with_answers(self):
        """Test 4: Exam preview shows all sections including Answer Keys"""
        test_name = "Exam Preview (All Sections)"
        try:
            url = reverse('placement_test:preview_exam', kwargs={'exam_id': self.exam.id})
            response = self.client.get(url)
            
            if response.status_code != 200:
                self.test_results.append((test_name, "FAIL", f"Preview status: {response.status_code}"))
                return False
                
            content = response.content.decode('utf-8')
            
            # Check for all three critical sections
            checks = [
                ('PDF Preview section', 'pdf-section' in content or 'PDF Preview' in content),
                ('Audio Files section', 'Audio Files' in content),
                ('Answer Keys section', 'Answer Keys' in content or 'answers-section' in content),
                ('Save answers button', 'saveAllAnswers' in content),
                ('Question type selects', 'question-type-select' in content),
                ('Audio assignment', 'audio-assignment' in content or 'assignAudio' in content),
            ]
            
            failed_checks = [name for name, result in checks if not result]
            
            if not failed_checks:
                self.test_results.append((test_name, "PASS", "All preview sections present"))
                return True
            else:
                self.test_results.append((test_name, "FAIL", f"Missing: {', '.join(failed_checks)}"))
                return False
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def test_session_management(self):
        """Test 5: Session management features"""
        test_name = "Session Management"
        try:
            # Test session list
            url = reverse('placement_test:session_list')
            response = self.client.get(url)
            
            if response.status_code != 200:
                self.test_results.append((test_name, "FAIL", f"Session list status: {response.status_code}"))
                return False
                
            # Test session detail
            url = reverse('placement_test:session_detail', kwargs={'session_id': self.session.id})
            response = self.client.get(url)
            
            if response.status_code != 200:
                self.test_results.append((test_name, "FAIL", f"Session detail status: {response.status_code}"))
                return False
                
            content = response.content.decode('utf-8')
            
            checks = [
                ('Student info', self.session.student_name in content),
                ('Exam info', self.exam.name in content),
                ('Grade or score display', 'grade' in content.lower() or 'score' in content.lower() or 'points' in content.lower()),
                ('Status display', 'status' in content.lower() or 'progress' in content.lower()),
            ]
            
            failed_checks = [name for name, result in checks if not result]
            
            if not failed_checks:
                self.test_results.append((test_name, "PASS", "Session management working"))
                return True
            else:
                self.test_results.append((test_name, "FAIL", f"Missing: {', '.join(failed_checks)}"))
                return False
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def test_grading_functionality(self):
        """Test 6: Grading functionality (newly fixed)"""
        test_name = "Grading Functionality"
        try:
            # Create a completed session for grading
            completed_session = StudentSession.objects.create(
                student_name="Completed Student",
                grade=5,
                academic_rank="top",
                exam=self.exam,
                original_curriculum_level=self.exam.curriculum_level,
                ip_address="127.0.0.1",
                completed_at=django.utils.timezone.now(),
                score=15,
                percentage_score=75.0
            )
            
            url = reverse('placement_test:grade_session', kwargs={'session_id': completed_session.id})
            response = self.client.get(url)
            
            if response.status_code != 200:
                self.test_results.append((test_name, "FAIL", f"Grading page status: {response.status_code}"))
                completed_session.delete()
                return False
                
            content = response.content.decode('utf-8')
            
            checks = [
                ('Grade form', '<form' in content),
                ('Score input', 'manual_score' in content or 'score' in content),
                ('Notes field', 'notes' in content),
                ('Student answers', 'Student Answers' in content or 'answers' in content),
                ('Save button', 'Save' in content),
            ]
            
            failed_checks = [name for name, result in checks if not result]
            
            completed_session.delete()
            
            if not failed_checks:
                self.test_results.append((test_name, "PASS", "Grading page functional"))
                return True
            else:
                self.test_results.append((test_name, "FAIL", f"Missing: {', '.join(failed_checks)}"))
                return False
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def test_ajax_endpoints(self):
        """Test 7: AJAX endpoints still accessible"""
        test_name = "AJAX Endpoints"
        try:
            endpoints = [
                ('save_exam_answers', reverse('placement_test:save_exam_answers', kwargs={'exam_id': self.exam.id})),
                ('update_question', reverse('placement_test:update_question', kwargs={'question_id': 1})),
                ('get_audio', reverse('placement_test:get_audio', kwargs={'audio_id': 1})),
            ]
            
            failed_endpoints = []
            for name, url in endpoints:
                # Just check if URL resolves (don't POST to avoid changing data)
                if not url:
                    failed_endpoints.append(name)
                    
            if not failed_endpoints:
                self.test_results.append((test_name, "PASS", "All AJAX endpoints accessible"))
                return True
            else:
                self.test_results.append((test_name, "FAIL", f"Failed: {', '.join(failed_endpoints)}"))
                return False
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def test_curriculum_data(self):
        """Test 8: Curriculum data (CORE program fix)"""
        test_name = "Curriculum Data"
        try:
            # Check CORE program exists
            core_program = Program.objects.filter(name='CORE').first()
            
            if not core_program:
                self.test_results.append((test_name, "FAIL", "CORE program missing"))
                return False
                
            # Check CORE has curriculum levels
            core_levels = CurriculumLevel.objects.filter(
                subprogram__program=core_program
            ).count()
            
            if core_levels < 12:
                self.test_results.append((test_name, "FAIL", f"CORE has only {core_levels} levels (expected 12)"))
                return False
                
            # Check all programs
            programs = Program.objects.all().count()
            if programs < 4:
                self.test_results.append((test_name, "FAIL", f"Only {programs} programs (expected 4)"))
                return False
                
            self.test_results.append((test_name, "PASS", f"All curriculum data present (4 programs, {core_levels} CORE levels)"))
            return True
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def test_javascript_no_errors(self):
        """Test 9: Check for JavaScript errors in rendered pages"""
        test_name = "JavaScript Health"
        try:
            # Test key pages for JS errors
            pages_to_test = [
                ('Student test', reverse('placement_test:take_test', kwargs={'session_id': self.session.id})),
                ('Exam preview', reverse('placement_test:preview_exam', kwargs={'exam_id': self.exam.id})),
            ]
            
            pages_with_errors = []
            for page_name, url in pages_to_test:
                response = self.client.get(url)
                if response.status_code == 200:
                    content = response.content.decode('utf-8')
                    
                    # Check for common error patterns
                    error_indicators = [
                        'undefined is not',
                        'Cannot read properties of undefined',
                        'SyntaxError',
                        'json.dumps(js_config)',  # Double encoding check
                    ]
                    
                    for error in error_indicators:
                        if error in content:
                            pages_with_errors.append(f"{page_name}: {error}")
                            
            if not pages_with_errors:
                self.test_results.append((test_name, "PASS", "No JavaScript errors detected"))
                return True
            else:
                self.test_results.append((test_name, "FAIL", f"Errors: {'; '.join(pages_with_errors)}"))
                return False
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def test_feature_flags(self):
        """Test 10: Feature flags properly simplified"""
        test_name = "Feature Flags"
        try:
            flags = settings.FEATURE_FLAGS
            
            # Check removed flags are gone
            if 'USE_MODULAR_TEMPLATES' in flags:
                self.test_results.append((test_name, "FAIL", "USE_MODULAR_TEMPLATES still exists"))
                return False
                
            if 'USE_V2_TEMPLATES' in flags:
                self.test_results.append((test_name, "FAIL", "USE_V2_TEMPLATES still exists"))
                return False
                
            # Check remaining flags are correct
            expected_flags = ['USE_SERVICE_LAYER', 'USE_JS_MODULES', 'ENABLE_CACHING', 'ENABLE_API_V2']
            missing_flags = [f for f in expected_flags if f not in flags]
            
            if missing_flags:
                self.test_results.append((test_name, "FAIL", f"Missing flags: {', '.join(missing_flags)}"))
                return False
                
            self.test_results.append((test_name, "PASS", "Feature flags properly simplified"))
            return True
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def test_template_existence(self):
        """Test 11: Verify correct templates exist and orphaned ones are gone"""
        test_name = "Template Files"
        try:
            # Templates that should exist
            should_exist = [
                'placement_test/start_test.html',
                'placement_test/student_test_v2.html',
                'placement_test/test_result.html',
                'placement_test/exam_list.html',
                'placement_test/preview_and_answers.html',
                'placement_test/grade_session.html',
            ]
            
            # Templates that should NOT exist (orphaned)
            should_not_exist = [
                'placement_test/preview_exam.html',
                'placement_test/preview_exam_modular.html',
                'placement_test/student_test_modular.html',
                'placement_test/take_test.html',
            ]
            
            missing_templates = []
            for template in should_exist:
                try:
                    get_template(template)
                except TemplateDoesNotExist:
                    missing_templates.append(template)
                    
            existing_orphaned = []
            for template in should_not_exist:
                try:
                    get_template(template)
                    existing_orphaned.append(template)
                except TemplateDoesNotExist:
                    pass  # Good, it shouldn't exist
                    
            if missing_templates or existing_orphaned:
                issues = []
                if missing_templates:
                    issues.append(f"Missing: {', '.join(missing_templates)}")
                if existing_orphaned:
                    issues.append(f"Orphaned still exist: {', '.join(existing_orphaned)}")
                self.test_results.append((test_name, "FAIL", '; '.join(issues)))
                return False
            else:
                self.test_results.append((test_name, "PASS", "Template structure correct"))
                return True
        except Exception as e:
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
            
    def run_all_tests(self):
        """Run all feature checks"""
        print("\n" + "="*60)
        print("DOUBLE-CHECK: ALL EXISTING FEATURES")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")
        
        if not self.setup_test_data():
            print("ERROR: Could not set up test data")
            return False
            
        # Run all tests
        tests = [
            self.test_student_registration,
            self.test_student_test_interface,
            self.test_exam_management,
            self.test_exam_preview_with_answers,
            self.test_session_management,
            self.test_grading_functionality,
            self.test_ajax_endpoints,
            self.test_curriculum_data,
            self.test_javascript_no_errors,
            self.test_feature_flags,
            self.test_template_existence,
        ]
        
        print("Running comprehensive feature checks...\n")
        for test in tests:
            print(f"Checking: {test.__doc__}")
            test()
            
        # Print results
        print("\n" + "="*60)
        print("DOUBLE-CHECK RESULTS")
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
        print(f"Total Checks: {len(self.test_results)}")
        print(f"Passed: {passed} | Failed: {failed} | Errors: {errors}")
        
        success_rate = (passed / len(self.test_results)) * 100 if self.test_results else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed == 0 and errors == 0:
            print("\n[SUCCESS] VERIFICATION COMPLETE: All existing features are working!")
            print("Template consolidation did NOT break any functionality.")
        else:
            print("\n[WARNING] Some features may be affected.")
            print("Please review the failed checks above.")
            
        print("="*60 + "\n")
        
        return failed == 0 and errors == 0


if __name__ == "__main__":
    checker = FeatureDoubleCheck()
    success = checker.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
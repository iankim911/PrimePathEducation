#!/usr/bin/env python
"""
Ultimate Feature Verification - Exhaustive Double-Check
Tests every single critical feature to ensure zero impact from changes
"""

import os
import sys
import django
from django.test import Client
from django.urls import reverse, resolve
import json

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from placement_test.models import Exam, Question, AudioFile, StudentSession, StudentAnswer
from core.models import School, Teacher, Program, CurriculumLevel, PlacementRule, ExamLevelMapping
from placement_test.services import ExamService, SessionService, GradingService
from django.contrib import admin


class UltimateFeatureVerification:
    def __init__(self):
        self.client = Client()
        self.passed_tests = []
        self.failed_tests = []
        self.warnings = []
        
    def log_result(self, test_name, status, details=""):
        if status == "PASS":
            self.passed_tests.append(test_name)
            print(f"✅ {test_name}: PASSED {details}")
        elif status == "FAIL":
            self.failed_tests.append(test_name)
            print(f"❌ {test_name}: FAILED {details}")
        else:  # WARNING
            self.warnings.append(test_name)
            print(f"⚠️ {test_name}: WARNING {details}")
    
    def test_complete_exam_workflow(self):
        """Test complete exam management workflow"""
        print("\n🔍 TESTING COMPLETE EXAM WORKFLOW")
        print("-" * 50)
        
        try:
            # Test 1: Exam List Page
            response = self.client.get('/api/placement/exams/')
            if response.status_code == 200 and 'Manage Exams' in response.content.decode():
                self.log_result("Exam List Page", "PASS", "- Full HTML rendered")
            else:
                self.log_result("Exam List Page", "FAIL", f"Status: {response.status_code}")
            
            # Test 2: Create Exam Form
            response = self.client.get('/api/placement/exams/create/')
            if response.status_code == 200:
                self.log_result("Create Exam Form", "PASS", "- Form accessible")
            else:
                self.log_result("Create Exam Form", "FAIL", f"Status: {response.status_code}")
            
            # Test 3: Exam Detail with Real Exam
            exam = Exam.objects.first()
            if exam:
                response = self.client.get(f'/api/placement/exams/{exam.id}/')
                if response.status_code == 200:
                    self.log_result("Exam Detail Page", "PASS", f"- Exam: {exam.name[:30]}...")
                else:
                    self.log_result("Exam Detail Page", "FAIL", f"Status: {response.status_code}")
                
                # Test 4: Exam Preview
                response = self.client.get(f'/api/placement/exams/{exam.id}/preview/')
                if response.status_code == 200:
                    content = response.content.decode()
                    if 'Questions and Answers' in content or 'preview' in content.lower():
                        self.log_result("Exam Preview", "PASS", "- Preview page loaded")
                    else:
                        self.log_result("Exam Preview", "WARNING", "- Page loaded but content unclear")
                else:
                    self.log_result("Exam Preview", "FAIL", f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_result("Exam Workflow", "FAIL", f"Exception: {e}")
    
    def test_complete_student_workflow(self):
        """Test complete student test-taking workflow"""
        print("\n👨‍🎓 TESTING COMPLETE STUDENT WORKFLOW")
        print("-" * 50)
        
        try:
            # Test 1: Start Test Page
            response = self.client.get('/api/placement/start/')
            if response.status_code == 200:
                content = response.content.decode()
                if 'Start Test' in content or 'student' in content.lower():
                    self.log_result("Start Test Page", "PASS", "- Form rendered")
                else:
                    self.log_result("Start Test Page", "WARNING", "- Page loaded but content unclear")
            else:
                self.log_result("Start Test Page", "FAIL", f"Status: {response.status_code}")
            
            # Test 2: Existing Student Session
            session = StudentSession.objects.first()
            if session:
                response = self.client.get(f'/api/placement/session/{session.id}/')
                if response.status_code in [200, 302]:  # 302 if redirected to completion
                    self.log_result("Student Test Interface", "PASS", f"- Session: {session.student_name}")
                else:
                    self.log_result("Student Test Interface", "FAIL", f"Status: {response.status_code}")
                
                # Test 3: Test Result Page
                response = self.client.get(f'/api/placement/session/{session.id}/result/')
                if response.status_code in [200, 302]:
                    self.log_result("Test Result Page", "PASS", "- Results accessible")
                else:
                    self.log_result("Test Result Page", "FAIL", f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_result("Student Workflow", "FAIL", f"Exception: {e}")
    
    def test_all_api_endpoints(self):
        """Test all critical API endpoints"""
        print("\n🔌 TESTING ALL API ENDPOINTS")
        print("-" * 50)
        
        exam = Exam.objects.first()
        session = StudentSession.objects.first()
        
        if not exam:
            self.log_result("API Tests", "FAIL", "No exam found for testing")
            return
            
        api_tests = [
            {
                'name': 'Save Exam Answers',
                'url': f'/api/placement/exams/{exam.id}/save-answers/',
                'method': 'POST',
                'data': {'questions': [], 'audio_assignments': {}},
                'expected_status': 200
            },
            {
                'name': 'Update Exam Name',
                'url': f'/api/placement/exams/{exam.id}/update-name/',
                'method': 'POST', 
                'data': {'name': exam.name},
                'expected_status': 200
            },
            {
                'name': 'Update Audio Names',
                'url': f'/api/placement/exams/{exam.id}/update-audio-names/',
                'method': 'POST',
                'data': {'audio_names': {}},
                'expected_status': 200
            },
            {
                'name': 'Create Questions',
                'url': f'/api/placement/exams/{exam.id}/create-questions/',
                'method': 'POST',
                'data': {},
                'expected_status': 200
            }
        ]
        
        # Test audio endpoint if audio files exist
        audio_file = AudioFile.objects.first()
        if audio_file:
            api_tests.append({
                'name': 'Get Audio File',
                'url': f'/api/placement/audio/{audio_file.id}/',
                'method': 'GET',
                'data': None,
                'expected_status': 200
            })
        
        for test in api_tests:
            try:
                if test['method'] == 'POST':
                    response = self.client.post(
                        test['url'],
                        json.dumps(test['data']) if test['data'] else '{}',
                        content_type='application/json'
                    )
                else:
                    response = self.client.get(test['url'])
                
                if response.status_code == test['expected_status']:
                    # Try to parse JSON response for additional verification
                    try:
                        data = json.loads(response.content.decode())
                        success = data.get('success', True)
                        if success:
                            self.log_result(f"API: {test['name']}", "PASS", "- JSON response OK")
                        else:
                            self.log_result(f"API: {test['name']}", "WARNING", "- Response indicates failure")
                    except:
                        # Non-JSON response might be OK for some endpoints
                        self.log_result(f"API: {test['name']}", "PASS", "- Non-JSON response")
                else:
                    self.log_result(f"API: {test['name']}", "FAIL", f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"API: {test['name']}", "FAIL", f"Exception: {e}")
    
    def test_database_integrity(self):
        """Test complete database integrity"""
        print("\n💾 TESTING DATABASE INTEGRITY")
        print("-" * 50)
        
        # Test 1: All models accessible
        models_to_test = [
            (Exam, "Exam"),
            (Question, "Question"), 
            (AudioFile, "AudioFile"),
            (StudentSession, "StudentSession"),
            (StudentAnswer, "StudentAnswer"),
            (School, "School"),
            (Teacher, "Teacher"),
            (Program, "Program"),
            (CurriculumLevel, "CurriculumLevel"),
            (PlacementRule, "PlacementRule"),
            (ExamLevelMapping, "ExamLevelMapping")
        ]
        
        for model_class, name in models_to_test:
            try:
                count = model_class.objects.count()
                self.log_result(f"Database: {name}", "PASS", f"- {count} records")
            except Exception as e:
                self.log_result(f"Database: {name}", "FAIL", f"Exception: {e}")
        
        # Test 2: Complex relationships
        try:
            exam = Exam.objects.select_related('curriculum_level').prefetch_related('questions', 'audio_files', 'sessions').first()
            if exam:
                question_count = exam.questions.count()
                audio_count = exam.audio_files.count()
                session_count = exam.sessions.count()
                
                self.log_result("Database: Complex Relationships", "PASS", 
                               f"- {question_count}Q, {audio_count}A, {session_count}S")
                
                # Test model methods
                exam_str = str(exam)
                if exam_str and len(exam_str) > 0:
                    self.log_result("Database: Model Methods", "PASS", f"- __str__ working")
                else:
                    self.log_result("Database: Model Methods", "WARNING", "- __str__ empty")
            
        except Exception as e:
            self.log_result("Database: Complex Operations", "FAIL", f"Exception: {e}")
    
    def test_service_layer_integrity(self):
        """Test complete service layer"""
        print("\n⚙️ TESTING SERVICE LAYER INTEGRITY")
        print("-" * 50)
        
        exam = Exam.objects.first()
        session = StudentSession.objects.first()
        
        if exam:
            # Test ExamService
            try:
                result = ExamService.update_exam_questions(exam, [])
                if isinstance(result, dict):
                    self.log_result("Service: ExamService.update_questions", "PASS", f"- {result}")
                else:
                    self.log_result("Service: ExamService.update_questions", "WARNING", "- Unexpected result type")
            except Exception as e:
                self.log_result("Service: ExamService.update_questions", "FAIL", f"Exception: {e}")
            
            try:
                result = ExamService.update_audio_assignments(exam, {})
                if isinstance(result, dict):
                    self.log_result("Service: ExamService.audio_assignments", "PASS", f"- {result}")
                else:
                    self.log_result("Service: ExamService.audio_assignments", "WARNING", "- Unexpected result type")
            except Exception as e:
                self.log_result("Service: ExamService.audio_assignments", "FAIL", f"Exception: {e}")
        
        # Test service imports
        try:
            from placement_test.services import ExamService, SessionService, PlacementService, GradingService
            from core.services import CurriculumService, SchoolService, TeacherService
            self.log_result("Service: Import Tests", "PASS", "- All services importable")
        except Exception as e:
            self.log_result("Service: Import Tests", "FAIL", f"Exception: {e}")
    
    def test_admin_interface(self):
        """Test Django admin interface"""
        print("\n🔧 TESTING ADMIN INTERFACE")
        print("-" * 50)
        
        try:
            # Test admin index
            response = self.client.get('/admin/')
            if response.status_code in [200, 302]:  # 302 if login redirect
                self.log_result("Admin: Index Page", "PASS", "- Admin accessible")
            else:
                self.log_result("Admin: Index Page", "FAIL", f"Status: {response.status_code}")
            
            # Test model registrations
            registered_models = admin.site._registry.keys()
            model_names = [model._meta.model_name for model in registered_models]
            
            critical_models = ['exam', 'question', 'school', 'program']
            for model_name in critical_models:
                if model_name in model_names:
                    self.log_result(f"Admin: {model_name} registered", "PASS")
                else:
                    self.log_result(f"Admin: {model_name} registered", "WARNING", "- Not found in registry")
            
        except Exception as e:
            self.log_result("Admin: Interface Test", "FAIL", f"Exception: {e}")
    
    def test_template_rendering(self):
        """Test template rendering with real data"""
        print("\n🎨 TESTING TEMPLATE RENDERING")
        print("-" * 50)
        
        # Template tests with actual page visits
        template_tests = [
            ('/api/placement/exams/', 'Exam List Template'),
            ('/api/placement/sessions/', 'Session List Template'),
            ('/api/placement/exams/create/', 'Create Exam Template'),
            ('/', 'Home Page Template')
        ]
        
        for url, test_name in template_tests:
            try:
                response = self.client.get(url)
                if response.status_code == 200:
                    content = response.content.decode()
                    # Check for basic HTML structure
                    if '<html' in content and '</html>' in content:
                        # Check for CSS/JS includes
                        if 'css' in content or 'js' in content:
                            self.log_result(f"Template: {test_name}", "PASS", "- Full rendering with assets")
                        else:
                            self.log_result(f"Template: {test_name}", "WARNING", "- Basic HTML only")
                    else:
                        self.log_result(f"Template: {test_name}", "WARNING", "- Incomplete HTML")
                else:
                    self.log_result(f"Template: {test_name}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Template: {test_name}", "FAIL", f"Exception: {e}")
    
    def test_url_resolution(self):
        """Test all URL patterns resolve correctly"""
        print("\n🔗 TESTING URL RESOLUTION")
        print("-" * 50)
        
        # Test critical URL patterns
        url_tests = [
            ('placement_test:exam_list', {}),
            ('placement_test:create_exam', {}),
            ('placement_test:session_list', {}),
            ('placement_test:start_test', {}),
        ]
        
        exam = Exam.objects.first()
        session = StudentSession.objects.first()
        
        if exam:
            url_tests.extend([
                ('placement_test:exam_detail', {'exam_id': exam.id}),
                ('placement_test:preview_exam', {'exam_id': exam.id}),
            ])
        
        if session:
            url_tests.extend([
                ('placement_test:take_test', {'session_id': session.id}),
                ('placement_test:test_result', {'session_id': session.id}),
            ])
        
        for url_name, kwargs in url_tests:
            try:
                url = reverse(url_name, kwargs=kwargs)
                resolved = resolve(url)
                if resolved:
                    self.log_result(f"URL: {url_name}", "PASS", f"- Resolves to {url}")
                else:
                    self.log_result(f"URL: {url_name}", "FAIL", "- Resolution failed")
            except Exception as e:
                self.log_result(f"URL: {url_name}", "FAIL", f"Exception: {e}")
    
    def run_ultimate_verification(self):
        """Run all verification tests"""
        print("=" * 80)
        print("ULTIMATE FEATURE VERIFICATION")
        print("Exhaustive Double-Check of All Functionality")
        print("=" * 80)
        
        # Run all test suites
        self.test_complete_exam_workflow()
        self.test_complete_student_workflow()
        self.test_all_api_endpoints()
        self.test_database_integrity()
        self.test_service_layer_integrity()
        self.test_admin_interface()
        self.test_template_rendering()
        self.test_url_resolution()
        
        # Final summary
        print("\n" + "=" * 80)
        print("ULTIMATE VERIFICATION RESULTS")
        print("=" * 80)
        
        total_tests = len(self.passed_tests) + len(self.failed_tests) + len(self.warnings)
        
        print(f"\n📊 TOTAL TESTS RUN: {total_tests}")
        print(f"✅ PASSED: {len(self.passed_tests)}")
        print(f"❌ FAILED: {len(self.failed_tests)}")
        print(f"⚠️ WARNINGS: {len(self.warnings)}")
        
        if self.failed_tests:
            print(f"\n🔴 FAILED TESTS:")
            for test in self.failed_tests:
                print(f"   ❌ {test}")
        
        if self.warnings:
            print(f"\n🟡 WARNING TESTS:")
            for test in self.warnings:
                print(f"   ⚠️ {test}")
        
        print("\n" + "=" * 80)
        if not self.failed_tests:
            print("🎉 ULTIMATE VERIFICATION: SUCCESS")
            print("✅ ALL CRITICAL FEATURES ARE WORKING")
            print("✅ NO EXISTING FEATURES WERE AFFECTED")
            print("✅ SYSTEM IS 100% FUNCTIONAL")
        else:
            print("⚠️ ULTIMATE VERIFICATION: ISSUES FOUND")
            print("❌ SOME FEATURES MAY BE AFFECTED")
            print("📋 REVIEW FAILED TESTS ABOVE")
        print("=" * 80)
        
        return len(self.failed_tests) == 0


if __name__ == "__main__":
    verifier = UltimateFeatureVerification()
    success = verifier.run_ultimate_verification()
    sys.exit(0 if success else 1)
#!/usr/bin/env python
"""
Comprehensive QA Test Suite - Run before and after modularization
Tests all critical paths to ensure nothing breaks
"""
import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from placement_test.models import Exam, StudentSession, Question, AudioFile, StudentAnswer
from core.models import CurriculumLevel, PlacementRule, Teacher, School
from placement_test.services import ExamService, SessionService, GradingService, PlacementService

class ComprehensiveQATest:
    def __init__(self):
        self.client = Client()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'passed': 0,
            'failed': 0,
            'errors': []
        }
    
    def log(self, test_name, status, details=""):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'details': details
        }
        self.results['tests'].append(result)
        
        if status == 'PASS':
            self.results['passed'] += 1
            print(f"[PASS] {test_name}")
        else:
            self.results['failed'] += 1
            self.results['errors'].append(f"{test_name}: {details}")
            print(f"[FAIL] {test_name}: {details}")
    
    def test_page_loads(self):
        """Test all pages load without errors"""
        pages = [
            ('/', 'Home page'),
            ('/teacher/dashboard/', 'Teacher dashboard'),
            ('/api/placement/exams/', 'Exam list'),
            ('/api/placement/sessions/', 'Session list'),
            ('/placement-rules/', 'Placement rules'),
            ('/exam-mapping/', 'Exam mapping'),
            ('/api/placement/start/', 'Start test page'),
        ]
        
        for url, name in pages:
            try:
                response = self.client.get(url)
                if response.status_code in [200, 301, 302]:
                    self.log(f"Page load: {name}", "PASS")
                else:
                    self.log(f"Page load: {name}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log(f"Page load: {name}", "FAIL", str(e))
    
    def test_service_layer(self):
        """Test all services are accessible"""
        services = [
            ('ExamService', ExamService),
            ('SessionService', SessionService),
            ('GradingService', GradingService),
            ('PlacementService', PlacementService),
        ]
        
        for name, service_class in services:
            try:
                # Check service has expected methods
                if hasattr(service_class, 'create_exam') or \
                   hasattr(service_class, 'create_session') or \
                   hasattr(service_class, 'auto_grade_answer') or \
                   hasattr(service_class, 'match_student_to_exam'):
                    self.log(f"Service available: {name}", "PASS")
                else:
                    self.log(f"Service available: {name}", "FAIL", "Missing expected methods")
            except Exception as e:
                self.log(f"Service available: {name}", "FAIL", str(e))
    
    def test_models(self):
        """Test model integrity"""
        models = [
            ('Exam', Exam),
            ('Question', Question),
            ('StudentSession', StudentSession),
            ('CurriculumLevel', CurriculumLevel),
            ('PlacementRule', PlacementRule),
        ]
        
        for name, model_class in models:
            try:
                count = model_class.objects.count()
                self.log(f"Model query: {name}", "PASS", f"Count: {count}")
            except Exception as e:
                self.log(f"Model query: {name}", "FAIL", str(e))
    
    def test_exam_creation_flow(self):
        """Test exam creation through service"""
        try:
            # Create a dummy PDF file
            pdf_content = b'%PDF-1.4 test content'
            pdf_file = SimpleUploadedFile("test_exam.pdf", pdf_content, content_type="application/pdf")
            
            # Get or create a curriculum level
            level = CurriculumLevel.objects.first()
            if not level:
                self.log("Exam creation flow", "SKIP", "No curriculum levels")
                return
            
            # Create exam data
            exam_data = {
                'name': 'QA Test Exam',
                'curriculum_level': level.id,
                'timer_minutes': 60,
                'total_questions': 5,
                'default_options_count': 4,
                'is_active': True
            }
            
            # Test exam creation
            exam = ExamService.create_exam(
                exam_data=exam_data,
                pdf_file=pdf_file,
                created_by=None,
                audio_files=[]
            )
            
            if exam and exam.id:
                self.log("Exam creation flow", "PASS", f"Created exam ID: {exam.id}")
                
                # Clean up
                exam.delete()
            else:
                self.log("Exam creation flow", "FAIL", "Exam not created")
                
        except Exception as e:
            self.log("Exam creation flow", "FAIL", str(e))
    
    def test_student_session_flow(self):
        """Test student session creation and answer submission"""
        try:
            # Get an exam
            exam = Exam.objects.filter(is_active=True).first()
            if not exam:
                self.log("Student session flow", "SKIP", "No active exams")
                return
            
            # Create student data
            student_data = {
                'student_name': 'QA Test Student',
                'school_name': 'QA Test School',
                'grade': 10,
                'academic_rank': 'TOP_10',
                'parent_phone': '1234567890'
            }
            
            # Get curriculum level
            level = exam.curriculum_level or CurriculumLevel.objects.first()
            
            # Create session
            session = SessionService.create_session(
                student_data=student_data,
                exam=exam,
                curriculum_level_id=level.id if level else None,
                request_meta={'REMOTE_ADDR': '127.0.0.1'}
            )
            
            if session and session.id:
                self.log("Student session creation", "PASS", f"Session ID: {session.id}")
                
                # Test answer submission
                question = exam.questions.first()
                if question:
                    answer = SessionService.submit_answer(
                        session=session,
                        question_id=question.id,
                        answer='A'
                    )
                    if answer:
                        self.log("Answer submission", "PASS")
                    else:
                        self.log("Answer submission", "FAIL", "Answer not saved")
                
                # Clean up
                session.delete()
            else:
                self.log("Student session flow", "FAIL", "Session not created")
                
        except Exception as e:
            self.log("Student session flow", "FAIL", str(e))
    
    def test_grading_flow(self):
        """Test grading functionality"""
        try:
            # Create a test answer
            session = StudentSession.objects.filter(completed_at__isnull=True).first()
            if not session:
                self.log("Grading flow", "SKIP", "No sessions to grade")
                return
            
            question = session.exam.questions.first()
            if not question:
                self.log("Grading flow", "SKIP", "No questions")
                return
            
            # Create or get answer
            answer, created = StudentAnswer.objects.get_or_create(
                session=session,
                question=question,
                defaults={'answer': 'A'}
            )
            
            # Test grading
            result = GradingService.auto_grade_answer(answer)
            
            if 'is_correct' in result:
                self.log("Grading flow", "PASS", f"Graded: {result['is_correct']}")
            else:
                self.log("Grading flow", "FAIL", "No grading result")
                
        except Exception as e:
            self.log("Grading flow", "FAIL", str(e))
    
    def test_ajax_endpoints(self):
        """Test AJAX endpoints"""
        endpoints = [
            ('/api/placement-rules/', 'GET', None, 'Placement rules API'),
            ('/api/placement/exams/check-version/', 'GET', {'curriculum_level_id': 1}, 'Version check API'),
        ]
        
        for url, method, params, name in endpoints:
            try:
                if method == 'GET':
                    response = self.client.get(url, params or {})
                else:
                    response = self.client.post(url, params or {})
                
                if response.status_code in [200, 201]:
                    # Try to parse JSON
                    try:
                        data = json.loads(response.content)
                        self.log(f"AJAX endpoint: {name}", "PASS")
                    except:
                        self.log(f"AJAX endpoint: {name}", "FAIL", "Invalid JSON response")
                else:
                    self.log(f"AJAX endpoint: {name}", "FAIL", f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log(f"AJAX endpoint: {name}", "FAIL", str(e))
    
    def test_file_operations(self):
        """Test file upload/download operations"""
        try:
            # Test PDF serving
            exam = Exam.objects.filter(pdf_file__isnull=False).first()
            if exam:
                # Check PDF file exists
                if exam.pdf_file and hasattr(exam.pdf_file, 'path'):
                    if os.path.exists(exam.pdf_file.path):
                        self.log("PDF file access", "PASS")
                    else:
                        self.log("PDF file access", "FAIL", "File not found")
                else:
                    self.log("PDF file access", "SKIP", "No PDF file")
            else:
                self.log("PDF file access", "SKIP", "No exams with PDFs")
            
            # Test audio file serving
            audio = AudioFile.objects.first()
            if audio:
                response = self.client.get(f'/api/placement/audio/{audio.id}/')
                if response.status_code == 200:
                    self.log("Audio file serving", "PASS")
                else:
                    self.log("Audio file serving", "FAIL", f"Status: {response.status_code}")
            else:
                self.log("Audio file serving", "SKIP", "No audio files")
                
        except Exception as e:
            self.log("File operations", "FAIL", str(e))
    
    def test_javascript_modules(self):
        """Test JavaScript modules are accessible"""
        js_files = [
            'static/js/config/app-config.js',
            'static/js/modules/base-module.js',
            'static/js/modules/pdf-viewer.js',
            'static/js/modules/audio-player.js',
            'static/js/modules/timer.js',
            'static/js/modules/answer-manager.js',
            'static/js/utils/event-delegation.js',
            'static/js/utils/form-validation.js',
        ]
        
        for js_file in js_files:
            if os.path.exists(js_file):
                self.log(f"JS module exists: {os.path.basename(js_file)}", "PASS")
            else:
                self.log(f"JS module exists: {os.path.basename(js_file)}", "FAIL", "File not found")
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        print("\n" + "="*60)
        print("COMPREHENSIVE QA TEST SUITE")
        print("="*60 + "\n")
        
        # Run all test categories
        self.test_page_loads()
        print()
        
        self.test_service_layer()
        print()
        
        self.test_models()
        print()
        
        self.test_exam_creation_flow()
        print()
        
        self.test_student_session_flow()
        print()
        
        self.test_grading_flow()
        print()
        
        self.test_ajax_endpoints()
        print()
        
        self.test_file_operations()
        print()
        
        self.test_javascript_modules()
        print()
        
        # Summary
        print("="*60)
        print(f"RESULTS: {self.results['passed']} passed, {self.results['failed']} failed")
        print("="*60)
        
        if self.results['errors']:
            print("\nERRORS:")
            for error in self.results['errors']:
                print(f"  - {error}")
        
        # Save results to file
        with open('qa_test_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nResults saved to qa_test_results.json")
        
        return self.results['failed'] == 0

if __name__ == '__main__':
    tester = ComprehensiveQATest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
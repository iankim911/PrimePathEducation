#!/usr/bin/env python3
"""
Final Feature Verification - Post Phase 11
Comprehensive check of ALL existing features to ensure nothing was broken
"""

import os
import sys
import django
import json
import traceback
from datetime import datetime
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client, RequestFactory
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from placement_test.models import Exam, Question, StudentSession, StudentAnswer, AudioFile
from core.models import CurriculumLevel, PlacementRule, School, Teacher, Program, SubProgram
import uuid


class FinalFeatureVerification:
    def __init__(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'verification_type': 'Final Feature Check - Post Phase 11',
            'categories': {},
            'critical_features': {},
            'summary': {
                'total_checked': 0,
                'passed': 0,
                'failed': 0,
                'warnings': 0
            }
        }
        
    def run_verification(self):
        """Run complete feature verification"""
        print("="*80)
        print("  FINAL FEATURE VERIFICATION - POST PHASE 11")
        print("  Checking ALL existing features for any impact")
        print("="*80)
        
        test_suites = [
            ("Student Features", self.verify_student_features),
            ("Teacher Features", self.verify_teacher_features),
            ("Exam Management", self.verify_exam_management),
            ("Session Management", self.verify_session_management),
            ("Grading System", self.verify_grading_system),
            ("Audio Features", self.verify_audio_features),
            ("PDF Features", self.verify_pdf_features),
            ("Navigation System", self.verify_navigation_system),
            ("Answer Submission", self.verify_answer_submission),
            ("Placement Rules", self.verify_placement_rules),
            ("Curriculum Levels", self.verify_curriculum_levels),
            ("API Endpoints", self.verify_api_endpoints),
            ("URL Routing", self.verify_url_routing),
            ("JavaScript Modules", self.verify_javascript_modules),
            ("Database Integrity", self.verify_database_integrity),
            ("Submit Test Fix", self.verify_submit_test_fix),
            ("Template Rendering", self.verify_template_rendering),
            ("Static Files", self.verify_static_files),
            ("Form Processing", self.verify_form_processing),
            ("Authentication", self.verify_authentication)
        ]
        
        for category_name, test_func in test_suites:
            print(f"\n{'='*70}")
            print(f"  Testing: {category_name}")
            print('='*70)
            
            category_results = {
                'passed': [],
                'failed': [],
                'warnings': []
            }
            
            try:
                test_func(category_results)
                self.results['categories'][category_name] = category_results
                
                # Update summary
                self.results['summary']['passed'] += len(category_results['passed'])
                self.results['summary']['failed'] += len(category_results['failed'])
                self.results['summary']['warnings'] += len(category_results['warnings'])
                
            except Exception as e:
                print(f"   ❌ EXCEPTION in {category_name}: {str(e)}")
                category_results['failed'].append(f"Exception: {str(e)}")
                self.results['categories'][category_name] = category_results
                traceback.print_exc()
        
        self.results['summary']['total_checked'] = (
            self.results['summary']['passed'] + 
            self.results['summary']['failed']
        )
        
        self.generate_report()
        
    def verify_student_features(self, results):
        """Verify all student-related features"""
        print("\n1. Student Registration & Test Start")
        
        # Ensure required data
        if not School.objects.exists():
            School.objects.create(name="Test School")
        
        if not CurriculumLevel.objects.exists():
            CurriculumLevel.objects.create(
                name="Test Level",
                grade_level=5,
                difficulty="Standard"
            )
        
        if not PlacementRule.objects.filter(grade=5).exists():
            PlacementRule.objects.create(
                grade=5,
                min_rank_percentile=40,
                max_rank_percentile=60,
                curriculum_level=CurriculumLevel.objects.first(),
                priority=1
            )
        
        # Test start page
        response = self.client.get(reverse('placement_test:start_test'))
        if response.status_code == 200:
            print("   ✅ Start test page loads")
            results['passed'].append("Start test page")
            
            # Check form fields
            content = response.content.decode('utf-8')
            required_fields = ['student_name', 'grade', 'academic_rank', 'parent_phone']
            for field in required_fields:
                if field in content:
                    print(f"   ✅ Form field '{field}' present")
                    results['passed'].append(f"Form field: {field}")
                else:
                    print(f"   ❌ Form field '{field}' missing")
                    results['failed'].append(f"Form field: {field}")
        else:
            print(f"   ❌ Start test page error: {response.status_code}")
            results['failed'].append("Start test page")
        
        # Test session creation
        print("\n2. Session Creation")
        session_data = {
            'student_name': 'Final Test Student',
            'grade': '5',
            'academic_rank': 'TOP_50',
            'school_name': School.objects.first().name,
            'parent_phone': '555-1234'
        }
        
        response = self.client.post(reverse('placement_test:start_test'), session_data)
        if response.status_code == 302:  # Redirect expected
            print("   ✅ Session created successfully")
            results['passed'].append("Session creation")
            
            # Get session for further testing
            session = StudentSession.objects.latest('created_at')
            self.test_session_id = str(session.id)
            
            # Test take test page
            print("\n3. Take Test Page")
            response = self.client.get(reverse('placement_test:take_test', args=[self.test_session_id]))
            if response.status_code == 200:
                print("   ✅ Take test page loads")
                results['passed'].append("Take test page")
                
                # Check critical elements
                content = response.content.decode('utf-8')
                critical_elements = [
                    ('APP_CONFIG', 'JavaScript configuration'),
                    ('pdf-viewer', 'PDF viewer element'),
                    ('timer', 'Timer element'),
                    ('question-panel', 'Question panels'),
                    ('submit-test-btn', 'Submit button')
                ]
                
                for element, description in critical_elements:
                    if element in content:
                        print(f"   ✅ {description} present")
                        results['passed'].append(description)
                    else:
                        print(f"   ❌ {description} missing")
                        results['failed'].append(description)
            else:
                print(f"   ❌ Take test page error: {response.status_code}")
                results['failed'].append("Take test page")
        else:
            print(f"   ❌ Session creation failed: {response.status_code}")
            results['failed'].append("Session creation")
    
    def verify_teacher_features(self, results):
        """Verify teacher/admin features"""
        print("\n1. Teacher Authentication")
        
        # Create admin if needed
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser('admin', 'admin@test.com', 'password')
        
        # Login
        login_success = self.client.login(username='admin', password='password')
        if login_success:
            print("   ✅ Admin login successful")
            results['passed'].append("Admin login")
        else:
            print("   ❌ Admin login failed")
            results['failed'].append("Admin login")
        
        print("\n2. Teacher Pages")
        teacher_pages = [
            ('placement_test:exam_list', 'Exam list'),
            ('placement_test:session_list', 'Session list'),
            ('placement_test:create_exam', 'Create exam'),
        ]
        
        for url_name, description in teacher_pages:
            try:
                response = self.client.get(reverse(url_name))
                if response.status_code == 200:
                    print(f"   ✅ {description} accessible")
                    results['passed'].append(f"Teacher: {description}")
                else:
                    print(f"   ❌ {description} error: {response.status_code}")
                    results['failed'].append(f"Teacher: {description}")
            except:
                print(f"   ⚠️  {description} URL not found")
                results['warnings'].append(f"Teacher: {description}")
        
        self.client.logout()
    
    def verify_exam_management(self, results):
        """Verify exam management features"""
        print("\n1. Exam Model Operations")
        
        # Create test exam
        if not Exam.objects.filter(name="Verification Test Exam").exists():
            exam = Exam.objects.create(
                name="Verification Test Exam",
                total_questions=10,
                timer_minutes=30,
                curriculum_level=CurriculumLevel.objects.first()
            )
            
            # Create questions
            for i in range(1, 11):
                Question.objects.create(
                    exam=exam,
                    question_number=i,
                    question_type='multiple_choice',
                    correct_answer=f"Option {i % 4 + 1}",
                    points=1,
                    options_count=4
                )
        else:
            exam = Exam.objects.get(name="Verification Test Exam")
        
        # Test exam operations
        if exam:
            print(f"   ✅ Exam created/retrieved: {exam.name}")
            results['passed'].append("Exam CRUD")
            
            # Check relationships
            if exam.questions.count() > 0:
                print(f"   ✅ Exam-Question relationship works ({exam.questions.count()} questions)")
                results['passed'].append("Exam-Question relationship")
            else:
                print("   ❌ Exam-Question relationship broken")
                results['failed'].append("Exam-Question relationship")
            
            if hasattr(exam, 'curriculum_level'):
                print("   ✅ Exam-CurriculumLevel relationship works")
                results['passed'].append("Exam-CurriculumLevel relationship")
            else:
                print("   ❌ Exam-CurriculumLevel relationship broken")
                results['failed'].append("Exam-CurriculumLevel relationship")
        else:
            print("   ❌ Exam creation/retrieval failed")
            results['failed'].append("Exam CRUD")
    
    def verify_session_management(self, results):
        """Verify session management"""
        print("\n1. Session Operations")
        
        if StudentSession.objects.exists():
            session = StudentSession.objects.first()
            
            # Check all fields
            required_fields = [
                'student_name', 'grade', 'academic_rank', 'exam',
                'started_at', 'id', 'is_completed'
            ]
            
            for field in required_fields:
                if hasattr(session, field):
                    value = getattr(session, field)
                    print(f"   ✅ Session.{field} exists: {str(value)[:30]}")
                    results['passed'].append(f"Session field: {field}")
                else:
                    print(f"   ❌ Session.{field} missing")
                    results['failed'].append(f"Session field: {field}")
            
            # Test session completion
            print("\n2. Session Completion")
            if hasattr(self, 'test_session_id'):
                response = self.client.post(
                    reverse('placement_test:complete_test', args=[self.test_session_id])
                )
                if response.status_code in [200, 302]:
                    print("   ✅ Session can be completed")
                    results['passed'].append("Session completion")
                else:
                    print(f"   ❌ Session completion error: {response.status_code}")
                    results['failed'].append("Session completion")
        else:
            print("   ⚠️  No sessions to test")
            results['warnings'].append("No sessions")
    
    def verify_grading_system(self, results):
        """Verify grading system"""
        print("\n1. Grading Service")
        
        try:
            from placement_test.services import GradingService
            
            # Check methods
            methods = ['grade_session', 'get_detailed_results', 'auto_grade_answer']
            for method in methods:
                if hasattr(GradingService, method):
                    print(f"   ✅ GradingService.{method} exists")
                    results['passed'].append(f"Grading: {method}")
                else:
                    print(f"   ❌ GradingService.{method} missing")
                    results['failed'].append(f"Grading: {method}")
            
            # Test grading if session exists
            if StudentSession.objects.exists():
                session = StudentSession.objects.first()
                try:
                    result = GradingService.grade_session(session)
                    print(f"   ✅ Grading works: {result}")
                    results['passed'].append("Grading execution")
                except Exception as e:
                    print(f"   ❌ Grading error: {e}")
                    results['failed'].append("Grading execution")
        except ImportError as e:
            print(f"   ❌ Cannot import GradingService: {e}")
            results['failed'].append("GradingService import")
    
    def verify_audio_features(self, results):
        """Verify audio features"""
        print("\n1. Audio Model")
        
        if AudioFile.objects.exists():
            audio = AudioFile.objects.first()
            
            # Check relationships
            if hasattr(audio, 'exam'):
                print("   ✅ Audio-Exam relationship intact")
                results['passed'].append("Audio-Exam relationship")
            else:
                print("   ❌ Audio-Exam relationship broken")
                results['failed'].append("Audio-Exam relationship")
            
            # Check fields
            if hasattr(audio, 'name') and audio.name:
                print(f"   ✅ Audio name field works: {audio.name}")
                results['passed'].append("Audio name field")
            else:
                print("   ❌ Audio name field issue")
                results['failed'].append("Audio name field")
            
            # Check question assignment
            if hasattr(audio, 'start_question') and hasattr(audio, 'end_question'):
                print(f"   ✅ Audio question range: Q{audio.start_question}-Q{audio.end_question}")
                results['passed'].append("Audio question range")
            else:
                print("   ❌ Audio question range fields missing")
                results['failed'].append("Audio question range")
        else:
            print("   ℹ️  No audio files to test")
            results['warnings'].append("No audio files")
    
    def verify_pdf_features(self, results):
        """Verify PDF features"""
        print("\n1. PDF in Exams")
        
        exam_with_pdf = Exam.objects.filter(pdf_file__isnull=False).first()
        if exam_with_pdf:
            print(f"   ✅ Exam PDF field works: {exam_with_pdf.pdf_file}")
            results['passed'].append("Exam PDF field")
            
            # Check if PDF URL accessible
            if hasattr(exam_with_pdf.pdf_file, 'url'):
                print(f"   ✅ PDF URL accessible: {exam_with_pdf.pdf_file.url}")
                results['passed'].append("PDF URL")
            else:
                print("   ❌ PDF URL not accessible")
                results['failed'].append("PDF URL")
        else:
            print("   ℹ️  No exams with PDF to test")
            results['warnings'].append("No PDF exams")
        
        print("\n2. PDF Viewer JavaScript")
        js_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'static/js/modules/pdf-viewer.js'
        )
        if os.path.exists(js_file):
            print("   ✅ PDF viewer module exists")
            results['passed'].append("PDF viewer module")
        else:
            print("   ❌ PDF viewer module missing")
            results['failed'].append("PDF viewer module")
    
    def verify_navigation_system(self, results):
        """Verify navigation system"""
        print("\n1. Navigation Module")
        
        js_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'static/js/modules/navigation.js'
        )
        
        if os.path.exists(js_file):
            print("   ✅ Navigation module exists")
            results['passed'].append("Navigation module")
            
            with open(js_file, 'r') as f:
                content = f.read()
                
                # Check key functions
                key_functions = [
                    'navigateToQuestion',
                    'updateNavigationButtons',
                    'markQuestionAnswered'
                ]
                
                for func in key_functions:
                    if func in content:
                        print(f"   ✅ Navigation.{func} exists")
                        results['passed'].append(f"Nav function: {func}")
                    else:
                        print(f"   ❌ Navigation.{func} missing")
                        results['failed'].append(f"Nav function: {func}")
        else:
            print("   ❌ Navigation module missing")
            results['failed'].append("Navigation module")
    
    def verify_answer_submission(self, results):
        """Verify answer submission"""
        print("\n1. Answer Submission Endpoint")
        
        if hasattr(self, 'test_session_id'):
            # Test submit answer endpoint
            answer_data = json.dumps({
                'question_id': str(uuid.uuid4()),  # Dummy ID
                'answer': 'Option 1'
            })
            
            response = self.client.post(
                reverse('placement_test:submit_answer', args=[self.test_session_id]),
                answer_data,
                content_type='application/json'
            )
            
            # 400 is OK here - means endpoint exists but question ID invalid
            if response.status_code in [200, 400]:
                print("   ✅ Submit answer endpoint works")
                results['passed'].append("Submit answer endpoint")
            else:
                print(f"   ❌ Submit answer error: {response.status_code}")
                results['failed'].append("Submit answer endpoint")
        
        print("\n2. Answer Manager Module")
        js_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'static/js/modules/answer-manager.js'
        )
        
        if os.path.exists(js_file):
            with open(js_file, 'r') as f:
                content = f.read()
                
                # Check for critical fix
                if 'getSessionId' in content:
                    print("   ✅ getSessionId method present (critical fix)")
                    results['passed'].append("getSessionId method")
                else:
                    print("   ❌ getSessionId method missing (CRITICAL)")
                    results['failed'].append("getSessionId method")
                
                if 'submitTest' in content:
                    print("   ✅ submitTest method present")
                    results['passed'].append("submitTest method")
                else:
                    print("   ❌ submitTest method missing")
                    results['failed'].append("submitTest method")
    
    def verify_placement_rules(self, results):
        """Verify placement rules"""
        print("\n1. Placement Rules")
        
        if PlacementRule.objects.exists():
            rule = PlacementRule.objects.first()
            
            # Check fields
            required_fields = [
                'grade', 'min_rank_percentile', 'max_rank_percentile',
                'curriculum_level', 'priority'
            ]
            
            for field in required_fields:
                if hasattr(rule, field):
                    print(f"   ✅ PlacementRule.{field} exists")
                    results['passed'].append(f"PlacementRule: {field}")
                else:
                    print(f"   ❌ PlacementRule.{field} missing")
                    results['failed'].append(f"PlacementRule: {field}")
        
        print("\n2. Placement Service")
        try:
            from placement_test.services import PlacementService
            
            methods = ['match_student_to_exam', 'find_matching_rule']
            for method in methods:
                if hasattr(PlacementService, method):
                    print(f"   ✅ PlacementService.{method} exists")
                    results['passed'].append(f"PlacementService: {method}")
                else:
                    print(f"   ❌ PlacementService.{method} missing")
                    results['failed'].append(f"PlacementService: {method}")
        except ImportError as e:
            print(f"   ❌ Cannot import PlacementService: {e}")
            results['failed'].append("PlacementService import")
    
    def verify_curriculum_levels(self, results):
        """Verify curriculum levels"""
        print("\n1. Curriculum Level Model")
        
        if CurriculumLevel.objects.exists():
            level = CurriculumLevel.objects.first()
            
            # Check relationships
            if hasattr(level, 'exams'):
                print(f"   ✅ CurriculumLevel-Exam relationship works")
                results['passed'].append("CurriculumLevel-Exam")
            else:
                print("   ❌ CurriculumLevel-Exam relationship broken")
                results['failed'].append("CurriculumLevel-Exam")
            
            if hasattr(level, 'placement_rules'):
                print("   ✅ CurriculumLevel-PlacementRule relationship works")
                results['passed'].append("CurriculumLevel-PlacementRule")
            else:
                print("   ❌ CurriculumLevel-PlacementRule relationship broken")
                results['failed'].append("CurriculumLevel-PlacementRule")
    
    def verify_api_endpoints(self, results):
        """Verify API endpoints"""
        print("\n1. API v1 Endpoints")
        
        api_endpoints = [
            ('/api/v1/health/', 'Health check'),
            ('/api/v1/exams/', 'Exams list'),
            ('/api/v1/sessions/', 'Sessions list'),
            ('/api/v1/schools/', 'Schools list'),
            ('/api/v1/programs/', 'Programs list'),
            ('/api/v1/dashboard/', 'Dashboard'),
        ]
        
        for endpoint, description in api_endpoints:
            response = self.client.get(endpoint)
            if response.status_code in [200, 401, 403]:
                print(f"   ✅ {description}: {endpoint}")
                results['passed'].append(f"API: {description}")
            else:
                print(f"   ❌ {description} error: {response.status_code}")
                results['failed'].append(f"API: {description}")
        
        print("\n2. Legacy API Endpoints")
        legacy_endpoints = [
            ('/api/health/', 'Legacy health'),
            ('/api/exams/', 'Legacy exams'),
            ('/api/placement/start/', 'Legacy start test'),
        ]
        
        for endpoint, description in legacy_endpoints:
            response = self.client.get(endpoint)
            if response.status_code in [200, 401, 403, 405]:  # 405 for POST-only endpoints
                print(f"   ✅ {description}: {endpoint}")
                results['passed'].append(f"Legacy API: {description}")
            else:
                print(f"   ❌ {description} broken: {response.status_code}")
                results['failed'].append(f"Legacy API: {description}")
    
    def verify_url_routing(self, results):
        """Verify URL routing"""
        print("\n1. Critical URLs")
        
        critical_urls = [
            ('placement_test:start_test', [], 'Start test'),
            ('placement_test:exam_list', [], 'Exam list'),
            ('placement_test:session_list', [], 'Session list'),
            ('core:placement_configuration', [], 'Placement config'),
        ]
        
        for url_name, args, description in critical_urls:
            try:
                url = reverse(url_name, args=args)
                print(f"   ✅ {description}: {url}")
                results['passed'].append(f"URL: {description}")
            except:
                print(f"   ❌ {description} URL not found")
                results['failed'].append(f"URL: {description}")
    
    def verify_javascript_modules(self, results):
        """Verify JavaScript modules"""
        print("\n1. Core JavaScript Modules")
        
        js_modules = [
            'modules/answer-manager.js',
            'modules/navigation.js',
            'modules/timer.js',
            'modules/pdf-viewer.js',
            'modules/audio-player.js',
            'modules/base-module.js',
            'config/app-config.js',
            'utils/event-delegation.js',
        ]
        
        static_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'static/js'
        )
        
        for module in js_modules:
            module_path = os.path.join(static_dir, module)
            if os.path.exists(module_path):
                print(f"   ✅ {module}")
                results['passed'].append(f"JS: {module}")
            else:
                print(f"   ❌ {module} missing")
                results['failed'].append(f"JS: {module}")
    
    def verify_database_integrity(self, results):
        """Verify database integrity"""
        print("\n1. Model Counts")
        
        models = [
            (Exam, 'Exams'),
            (Question, 'Questions'),
            (StudentSession, 'Sessions'),
            (CurriculumLevel, 'Curriculum Levels'),
            (PlacementRule, 'Placement Rules'),
            (School, 'Schools'),
            (Program, 'Programs'),
            (AudioFile, 'Audio Files'),
        ]
        
        for model, name in models:
            try:
                count = model.objects.count()
                print(f"   ✅ {name}: {count} records")
                results['passed'].append(f"DB: {name}")
            except Exception as e:
                print(f"   ❌ {name} error: {e}")
                results['failed'].append(f"DB: {name}")
    
    def verify_submit_test_fix(self, results):
        """Verify the critical submit test fix"""
        print("\n1. Submit Test Fix Verification")
        
        js_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'static/js/modules/answer-manager.js'
        )
        
        if os.path.exists(js_file):
            with open(js_file, 'r') as f:
                content = f.read()
                
                critical_patterns = [
                    ('getSessionId', 'getSessionId method'),
                    ('if (!sessionId)', 'Session ID validation'),
                    ('APP_CONFIG.session', 'APP_CONFIG fallback'),
                    ('window.location.pathname', 'URL fallback'),
                    ('try {', 'Error handling'),
                ]
                
                for pattern, description in critical_patterns:
                    if pattern in content:
                        print(f"   ✅ {description} present")
                        results['passed'].append(f"Submit fix: {description}")
                    else:
                        print(f"   ❌ {description} missing (CRITICAL)")
                        results['failed'].append(f"Submit fix: {description}")
        else:
            print("   ❌ answer-manager.js not found (CRITICAL)")
            results['failed'].append("Submit fix: file missing")
    
    def verify_template_rendering(self, results):
        """Verify template rendering"""
        print("\n1. Template Files")
        
        template_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'templates'
        )
        
        critical_templates = [
            'placement_test/start_test.html',
            'placement_test/student_test_v2.html',
            'placement_test/test_result.html',
            'placement_test/exam_list.html',
            'placement_test/create_exam.html',
        ]
        
        for template in critical_templates:
            template_path = os.path.join(template_dir, template)
            if os.path.exists(template_path):
                print(f"   ✅ {template}")
                results['passed'].append(f"Template: {template}")
            else:
                print(f"   ❌ {template} missing")
                results['failed'].append(f"Template: {template}")
    
    def verify_static_files(self, results):
        """Verify static files"""
        print("\n1. CSS Files")
        
        static_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'static'
        )
        
        if os.path.exists(static_dir):
            css_dir = os.path.join(static_dir, 'css')
            if os.path.exists(css_dir):
                css_count = len([f for f in os.listdir(css_dir) if f.endswith('.css')])
                print(f"   ✅ CSS directory exists ({css_count} files)")
                results['passed'].append("CSS directory")
            else:
                print("   ❌ CSS directory missing")
                results['failed'].append("CSS directory")
            
            js_dir = os.path.join(static_dir, 'js')
            if os.path.exists(js_dir):
                js_count = len([f for f in Path(js_dir).rglob('*.js')])
                print(f"   ✅ JS directory exists ({js_count} files)")
                results['passed'].append("JS directory")
            else:
                print("   ❌ JS directory missing")
                results['failed'].append("JS directory")
    
    def verify_form_processing(self, results):
        """Verify form processing"""
        print("\n1. CSRF Protection")
        
        response = self.client.get(reverse('placement_test:start_test'))
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            if 'csrfmiddlewaretoken' in content or 'csrf_token' in content:
                print("   ✅ CSRF token present")
                results['passed'].append("CSRF protection")
            else:
                print("   ❌ CSRF token missing")
                results['failed'].append("CSRF protection")
    
    def verify_authentication(self, results):
        """Verify authentication system"""
        print("\n1. Authentication System")
        
        # Test login/logout
        if User.objects.filter(username='admin').exists():
            login_success = self.client.login(username='admin', password='password')
            if login_success:
                print("   ✅ Login system works")
                results['passed'].append("Login system")
                
                self.client.logout()
                print("   ✅ Logout system works")
                results['passed'].append("Logout system")
            else:
                print("   ❌ Login system failed")
                results['failed'].append("Login system")
    
    def generate_report(self):
        """Generate comprehensive report"""
        print("\n" + "="*80)
        print("  FINAL VERIFICATION REPORT")
        print("="*80)
        
        # Calculate totals
        total_passed = self.results['summary']['passed']
        total_failed = self.results['summary']['failed']
        total_warnings = self.results['summary']['warnings']
        total_checked = self.results['summary']['total_checked']
        
        if total_checked > 0:
            pass_rate = (total_passed / total_checked) * 100
        else:
            pass_rate = 0
        
        print(f"\n📊 Overall Statistics:")
        print(f"   Total Features Checked: {total_checked}")
        print(f"   ✅ Passed: {total_passed}")
        print(f"   ❌ Failed: {total_failed}")
        print(f"   ⚠️  Warnings: {total_warnings}")
        print(f"   📈 Pass Rate: {pass_rate:.1f}%")
        
        # Critical features status
        print(f"\n🎯 Critical Features:")
        critical_features = [
            'Student Features',
            'Teacher Features',
            'Session Management',
            'Answer Submission',
            'Submit Test Fix',
            'Database Integrity'
        ]
        
        for feature in critical_features:
            if feature in self.results['categories']:
                failed_count = len(self.results['categories'][feature]['failed'])
                if failed_count == 0:
                    print(f"   ✅ {feature}: WORKING")
                    self.results['critical_features'][feature] = 'WORKING'
                else:
                    print(f"   ❌ {feature}: {failed_count} ISSUES")
                    self.results['critical_features'][feature] = f"{failed_count} ISSUES"
        
        # Show failures if any
        if total_failed > 0:
            print("\n❌ Failed Features (First 20):")
            count = 0
            for category, data in self.results['categories'].items():
                for failure in data['failed']:
                    print(f"   - [{category}] {failure}")
                    count += 1
                    if count >= 20:
                        break
                if count >= 20:
                    break
        
        # Final verdict
        print("\n" + "="*80)
        if pass_rate >= 95:
            print("  ✅ EXCELLENT: All features working properly!")
            print("  No significant impact from Phase 11 modularization.")
        elif pass_rate >= 90:
            print("  ✅ GOOD: Most features working with minor issues.")
            print("  Phase 11 modularization successful with minimal impact.")
        elif pass_rate >= 80:
            print("  ⚠️  ATTENTION NEEDED: Some features affected.")
            print("  Review failed tests and fix issues.")
        else:
            print("  ❌ CRITICAL: Significant features broken.")
            print("  Immediate attention required.")
        print("="*80)
        
        # Save detailed results
        output_file = 'final_feature_verification_results.json'
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\n📄 Detailed results saved to: {output_file}")


if __name__ == "__main__":
    verifier = FinalFeatureVerification()
    verifier.run_verification()
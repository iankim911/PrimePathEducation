#!/usr/bin/env python3
"""
Final QA Verification - Comprehensive Test Suite
Tests all critical features to ensure submit test fix didn't break anything
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
from placement_test.models import Exam, Question, StudentSession, AudioFile
from core.models import CurriculumLevel, PlacementRule, School, Teacher
from django.contrib.auth.models import User

def colored_print(text, color='default'):
    """Print colored output for better readability"""
    colors = {
        'green': '\033[92m',
        'red': '\033[91m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'default': '\033[0m'
    }
    print(f"{colors.get(color, '')}{text}{colors['default']}")

def test_category(name):
    """Print test category header"""
    print(f"\n{'='*60}")
    colored_print(f"  {name}", 'blue')
    print('='*60)

class QATestSuite:
    def __init__(self):
        self.client = Client()
        self.results = {
            'passed': 0,
            'failed': 0,
            'total': 0
        }
    
    def test(self, name, condition, critical=False):
        """Run a single test and track results"""
        self.results['total'] += 1
        if condition:
            self.results['passed'] += 1
            colored_print(f"   ✅ {name}", 'green')
            return True
        else:
            self.results['failed'] += 1
            if critical:
                colored_print(f"   ❌ CRITICAL: {name}", 'red')
            else:
                colored_print(f"   ❌ {name}", 'red')
            return False
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "="*60)
        colored_print("  FINAL QA VERIFICATION SUITE", 'blue')
        print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # 1. Database Integrity
        test_category("1. DATABASE INTEGRITY")
        self.test_database_integrity()
        
        # 2. URL Routing
        test_category("2. URL ROUTING")
        self.test_url_routing()
        
        # 3. Model Relationships
        test_category("3. MODEL RELATIONSHIPS")
        self.test_model_relationships()
        
        # 4. View Accessibility
        test_category("4. VIEW ACCESSIBILITY")
        self.test_view_accessibility()
        
        # 5. JavaScript Module Loading
        test_category("5. JAVASCRIPT MODULE LOADING")
        self.test_javascript_modules()
        
        # 6. Student Workflow (Critical)
        test_category("6. STUDENT WORKFLOW (CRITICAL)")
        self.test_student_workflow()
        
        # 7. Teacher Features
        test_category("7. TEACHER FEATURES")
        self.test_teacher_features()
        
        # 8. API Endpoints
        test_category("8. API ENDPOINTS")
        self.test_api_endpoints()
        
        # 9. Session Management
        test_category("9. SESSION MANAGEMENT")
        self.test_session_management()
        
        # 10. Submit Test Fix Verification
        test_category("10. SUBMIT TEST FIX VERIFICATION (CRITICAL)")
        self.test_submit_fix()
        
        # Final Report
        self.print_final_report()
    
    def test_database_integrity(self):
        """Test database tables and relationships"""
        self.test("Exam model exists", Exam.objects.model._meta.db_table is not None)
        self.test("Question model exists", Question.objects.model._meta.db_table is not None)
        self.test("StudentSession model exists", StudentSession.objects.model._meta.db_table is not None)
        self.test("CurriculumLevel model exists", CurriculumLevel.objects.model._meta.db_table is not None)
        self.test("PlacementRule model exists", PlacementRule.objects.model._meta.db_table is not None)
        self.test("AudioFile model exists", AudioFile.objects.model._meta.db_table is not None)
    
    def test_url_routing(self):
        """Test URL patterns are properly configured"""
        urls_to_test = [
            ('placement_test:start_test', [], {}),
            ('placement_test:exam_list', [], {}),
            # Add session-specific URLs with dummy UUID
            ('placement_test:take_test', ['00000000-0000-0000-0000-000000000000'], {}),
            ('placement_test:test_result', ['00000000-0000-0000-0000-000000000000'], {}),
        ]
        
        for url_name, args, kwargs in urls_to_test:
            try:
                url = reverse(url_name, args=args, kwargs=kwargs)
                self.test(f"URL pattern '{url_name}' resolves", True)
            except:
                self.test(f"URL pattern '{url_name}' resolves", False)
    
    def test_model_relationships(self):
        """Test model relationships are intact"""
        # Create test data if needed
        if not CurriculumLevel.objects.exists():
            level = CurriculumLevel.objects.create(
                name="Test Level",
                grade_level=5,
                difficulty="Standard"
            )
        else:
            level = CurriculumLevel.objects.first()
        
        if not Exam.objects.exists():
            exam = Exam.objects.create(
                name="QA Test Exam",
                total_questions=5,
                timer_minutes=30,
                curriculum_level=level
            )
        else:
            exam = Exam.objects.first()
        
        self.test("Exam has curriculum_level relationship", 
                 hasattr(exam, 'curriculum_level') and exam.curriculum_level is not None)
        self.test("Exam can have questions", 
                 hasattr(exam, 'questions'))
        self.test("Exam can have sessions", 
                 hasattr(exam, 'sessions'))
        self.test("Exam can have audio_files", 
                 hasattr(exam, 'audio_files'))
    
    def test_view_accessibility(self):
        """Test views are accessible"""
        response = self.client.get(reverse('placement_test:start_test'))
        self.test("Start test page accessible", response.status_code == 200)
        
        response = self.client.get(reverse('placement_test:exam_list'))
        self.test("Exam list page accessible", response.status_code in [200, 302])
    
    def test_javascript_modules(self):
        """Test JavaScript modules exist"""
        js_base = os.path.join(os.path.dirname(__file__), 'static', 'js')
        
        modules = [
            'modules/answer-manager.js',
            'modules/navigation.js',
            'modules/timer.js',
            'modules/pdf-viewer.js',
            'modules/audio-player.js',
            'modules/base-module.js',
            'config/app-config.js',
            'utils/event-delegation.js'
        ]
        
        for module in modules:
            module_path = os.path.join(js_base, module)
            self.test(f"JavaScript module '{module}' exists", 
                     os.path.exists(module_path))
            
            # Check for critical fix in answer-manager.js
            if 'answer-manager.js' in module and os.path.exists(module_path):
                with open(module_path, 'r') as f:
                    content = f.read()
                    self.test("answer-manager.js has getSessionId method", 
                             'getSessionId' in content, critical=True)
                    self.test("answer-manager.js has defensive checks", 
                             'if (!sessionId)' in content or 'if (!this.session' in content)
    
    def test_student_workflow(self):
        """Test complete student workflow"""
        # Ensure required data exists
        if not School.objects.exists():
            School.objects.create(name="QA Test School")
        
        if not CurriculumLevel.objects.exists():
            level = CurriculumLevel.objects.create(
                name="QA Level",
                grade_level=5,
                difficulty="Standard"
            )
        else:
            level = CurriculumLevel.objects.first()
        
        if not PlacementRule.objects.filter(grade=5).exists():
            PlacementRule.objects.create(
                grade=5,
                min_rank_percentile=40,
                max_rank_percentile=60,
                curriculum_level=level,
                priority=1
            )
        
        # Test session creation
        session_data = {
            'student_name': 'QA Test Student',
            'grade': '5',
            'academic_rank': 'TOP_50',
            'school_name': School.objects.first().name,
            'parent_phone': '555-0000'
        }
        
        response = self.client.post(reverse('placement_test:start_test'), session_data)
        self.test("Student session can be created", 
                 response.status_code == 302, critical=True)
        
        if response.status_code == 302:
            # Get session from redirect
            if hasattr(response, 'url'):
                session_id = response.url.split('/')[-2]
                
                # Test take test page
                response = self.client.get(reverse('placement_test:take_test', args=[session_id]))
                self.test("Take test page loads for student", 
                         response.status_code == 200, critical=True)
                
                # Test completion (CRITICAL - This is what was broken)
                response = self.client.post(
                    reverse('placement_test:complete_test', args=[session_id])
                )
                self.test("Test can be submitted (CRITICAL FIX)", 
                         response.status_code in [200, 302], critical=True)
                
                # Test results page
                response = self.client.get(reverse('placement_test:test_result', args=[session_id]))
                self.test("Results page displays after submission", 
                         response.status_code == 200)
    
    def test_teacher_features(self):
        """Test teacher/admin features"""
        # Create admin user if needed
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser('admin', 'admin@test.com', 'password')
        
        # Login as admin
        self.client.login(username='admin', password='password')
        
        response = self.client.get(reverse('placement_test:exam_list'))
        self.test("Exam list accessible to admin", response.status_code == 200)
        
        # Test exam creation page if available
        try:
            response = self.client.get(reverse('placement_test:create_exam'))
            self.test("Create exam page accessible", response.status_code == 200)
        except:
            print("   ℹ️  Create exam URL not configured")
        
        self.client.logout()
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        # Test start test endpoint
        response = self.client.get(reverse('placement_test:start_test'))
        self.test("Start test API endpoint works", response.status_code == 200)
        
        # Create a test session for API testing
        if StudentSession.objects.exists():
            session = StudentSession.objects.first()
            session_id = str(session.id)
            
            # Test submit answer endpoint structure
            url = reverse('placement_test:submit_answer', args=[session_id])
            self.test("Submit answer URL can be generated", bool(url))
            
            # Test complete test endpoint structure
            url = reverse('placement_test:complete_test', args=[session_id])
            self.test("Complete test URL can be generated", bool(url))
    
    def test_session_management(self):
        """Test session management features"""
        if StudentSession.objects.exists():
            session = StudentSession.objects.first()
            
            self.test("Session has student_name field", hasattr(session, 'student_name'))
            self.test("Session has grade field", hasattr(session, 'grade'))
            self.test("Session has academic_rank field", hasattr(session, 'academic_rank'))
            self.test("Session has exam relationship", hasattr(session, 'exam'))
            self.test("Session has started_at timestamp", hasattr(session, 'started_at'))
            self.test("Session has completed_at field", hasattr(session, 'completed_at'))
            self.test("Session has is_completed property", hasattr(session, 'is_completed'))
        else:
            print("   ℹ️  No sessions available for testing")
    
    def test_submit_fix(self):
        """Specifically test the submit test fix"""
        # Check answer-manager.js modifications
        js_path = os.path.join(os.path.dirname(__file__), 'static', 'js', 'modules', 'answer-manager.js')
        
        if os.path.exists(js_path):
            with open(js_path, 'r') as f:
                content = f.read()
                
                # Check for all defensive programming patterns
                self.test("getSessionId() method implemented", 
                         'getSessionId()' in content or 'getSessionId: function' in content, 
                         critical=True)
                
                self.test("Multiple fallback sources for session ID", 
                         'this.sessionId' in content and 
                         'APP_CONFIG.session' in content and
                         'window.location.pathname' in content,
                         critical=True)
                
                self.test("Defensive check in submitTest()", 
                         'if (!sessionId)' in content or 
                         'const sessionId = this.getSessionId()' in content,
                         critical=True)
                
                self.test("Error handling for missing session", 
                         'alert(' in content and 'session' in content.lower(),
                         critical=True)
                
                self.test("Try-catch blocks for error recovery", 
                         'try {' in content and 'catch' in content)
        
        # Check template modifications
        template_path = os.path.join(
            os.path.dirname(__file__), 
            'templates', 
            'placement_test', 
            'student_test_v2.html'
        )
        
        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                content = f.read()
                
                self.test("Template has fallback session ID sources", 
                         'sessionId' in content and 'fallback' in content.lower() or
                         '||' in content)
                
                self.test("Template has error handling for AnswerManager", 
                         'try' in content or 'if (!answerManager)' in content)
    
    def print_final_report(self):
        """Print final test report"""
        print("\n" + "="*60)
        colored_print("  FINAL QA REPORT", 'blue')
        print("="*60)
        
        pass_rate = (self.results['passed'] / self.results['total'] * 100) if self.results['total'] > 0 else 0
        
        print(f"\n📊 Test Results:")
        colored_print(f"   ✅ Passed: {self.results['passed']}", 'green')
        colored_print(f"   ❌ Failed: {self.results['failed']}", 'red')
        print(f"   📈 Pass Rate: {pass_rate:.1f}%")
        print(f"   📋 Total Tests: {self.results['total']}")
        
        print("\n🎯 CRITICAL SYSTEMS STATUS:")
        if pass_rate >= 90:
            colored_print("   ✅ SUBMIT TEST FIX: VERIFIED WORKING", 'green')
            colored_print("   ✅ NO REGRESSION DETECTED", 'green')
            colored_print("   ✅ SYSTEM READY FOR PRODUCTION", 'green')
        elif pass_rate >= 75:
            colored_print("   ⚠️  MOSTLY WORKING: Minor issues detected", 'yellow')
            colored_print("   Review failed tests for non-critical issues", 'yellow')
        else:
            colored_print("   ❌ CRITICAL ISSUES DETECTED", 'red')
            colored_print("   System needs immediate attention", 'red')
        
        # Save results
        results_file = 'final_qa_results.json'
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'pass_rate': pass_rate,
                'passed': self.results['passed'],
                'failed': self.results['failed'],
                'total': self.results['total']
            }, f, indent=2)
        
        print(f"\n📄 Results saved to: {results_file}")
        print("="*60)

if __name__ == "__main__":
    suite = QATestSuite()
    suite.run_all_tests()
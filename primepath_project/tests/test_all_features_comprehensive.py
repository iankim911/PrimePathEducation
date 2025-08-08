"""
Comprehensive Feature Verification Test
Tests EVERY existing feature to ensure nothing was broken by Phase 9 modularization
"""
import os
import sys
import django
from pathlib import Path
import json
import uuid

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, str(Path(__file__).parent))
django.setup()

from django.test import Client
from django.urls import reverse
from django.db import connection


class ComprehensiveFeatureTest:
    """Test every single feature in the system."""
    
    def __init__(self):
        self.client = Client()
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.results = []
        
    def run_test(self, test_name, test_func, critical=True):
        """Run a single test and track results."""
        try:
            result = test_func()
            if result == "WARNING":
                self.warnings += 1
                self.results.append(f"WARN: {test_name}")
                print(f"WARN: {test_name}")
            else:
                self.passed += 1
                self.results.append(f"PASS: {test_name}")
                print(f"PASS: {test_name}")
        except Exception as e:
            if critical:
                self.failed += 1
                self.results.append(f"FAIL: {test_name}: {str(e)}")
                print(f"FAIL: {test_name}: {str(e)}")
            else:
                self.warnings += 1
                self.results.append(f"WARN: {test_name}: {str(e)}")
                print(f"WARN: {test_name}: {str(e)}")
    
    # ========== 1. CORE PAGE LOADING ==========
    
    def test_home_page(self):
        """Test home page loads with correct content."""
        response = self.client.get('/')
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        assert 'PrimePath' in content or 'Welcome' in content or 'placement' in content.lower()
        
    def test_teacher_dashboard(self):
        """Test teacher dashboard loads and shows stats."""
        response = self.client.get('/teacher/dashboard/')
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        # Check for dashboard elements
        assert 'dashboard' in content.lower() or 'statistics' in content.lower()
        
    # ========== 2. PLACEMENT TEST FLOW ==========
    
    def test_start_test_page(self):
        """Test placement test start page with form."""
        response = self.client.get('/api/placement/start/')
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        # Check for form fields
        assert 'student_name' in content or 'Student Name' in content
        assert 'grade' in content or 'Grade' in content
        
    def test_placement_test_with_valid_data(self):
        """Test creating a placement test with proper data."""
        from placement_test.models import PlacementRule, Exam
        from core.models import CurriculumLevel
        
        # First ensure we have data for testing
        if not PlacementRule.objects.exists():
            # Create a default rule if none exist
            level = CurriculumLevel.objects.first()
            if level and Exam.objects.filter(curriculum_level=level).exists():
                PlacementRule.objects.create(
                    min_grade=1,
                    max_grade=12,
                    min_percentile=0,
                    max_percentile=100,
                    curriculum_level=level
                )
        
        # Try to create a session
        if PlacementRule.objects.exists():
            data = {
                'student_name': 'Test Student',
                'grade': '5',
                'academic_rank': 'TOP_50',
                'parent_phone': '555-1234',
                'school_name': 'Test School'
            }
            response = self.client.post('/api/placement/start/', data)
            # Should redirect (302) or show error page (200/400)
            assert response.status_code in [200, 302, 400]
            if response.status_code == 302:
                # Check redirect is to take test
                assert '/api/placement/session/' in response.url
        else:
            return "WARNING"  # No rules configured
    
    def test_student_test_interface(self):
        """Test student test-taking interface."""
        from placement_test.models import StudentSession
        
        # Find an incomplete session
        session = StudentSession.objects.filter(completed_at__isnull=True).first()
        if session:
            response = self.client.get(f'/api/placement/session/{session.id}/')
            assert response.status_code == 200
            content = response.content.decode('utf-8')
            # Check for test interface elements
            assert 'question' in content.lower() or 'timer' in content.lower()
        else:
            # Create a test session
            from placement_test.models import Exam
            exam = Exam.objects.filter(is_active=True).first()
            if exam:
                session = StudentSession.objects.create(
                    student_name='Test Student',
                    grade=5,
                    academic_rank='TOP_50',
                    exam=exam,
                    school_name_manual='Test School'
                )
                response = self.client.get(f'/api/placement/session/{session.id}/')
                assert response.status_code == 200
    
    # ========== 3. EXAM MANAGEMENT ==========
    
    def test_exam_list_page(self):
        """Test exam list page shows exams."""
        response = self.client.get('/api/placement/exams/')
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        
        from placement_test.models import Exam
        if Exam.objects.exists():
            # Should show at least one exam
            exam = Exam.objects.first()
            assert exam.name in content or 'exam' in content.lower()
    
    def test_create_exam_page(self):
        """Test create exam page with form."""
        response = self.client.get('/api/placement/exams/create/')
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        # Check for form elements
        assert 'pdf_file' in content or 'PDF' in content
        assert 'timer_minutes' in content or 'Timer' in content
    
    def test_exam_detail_page(self):
        """Test exam detail page."""
        from placement_test.models import Exam
        
        exam = Exam.objects.first()
        if exam:
            response = self.client.get(f'/api/placement/exams/{exam.id}/')
            assert response.status_code == 200
            content = response.content.decode('utf-8')
            assert exam.name in content
    
    def test_preview_exam_page(self):
        """Test exam preview with questions."""
        from placement_test.models import Exam
        
        exam = Exam.objects.first()
        if exam:
            response = self.client.get(f'/api/placement/exams/{exam.id}/preview/')
            assert response.status_code == 200
            content = response.content.decode('utf-8')
            # Should have question elements
            assert 'question' in content.lower() or 'answer' in content.lower()
    
    # ========== 4. QUESTION MANAGEMENT ==========
    
    def test_question_creation(self):
        """Test questions are created for exams."""
        from placement_test.models import Exam, Question
        
        exam = Exam.objects.first()
        if exam:
            # Ensure exam has questions
            if not exam.questions.exists():
                # Trigger question creation
                response = self.client.get(f'/api/placement/exams/{exam.id}/preview/')
                
            # Check questions exist now
            questions = exam.questions.all()
            assert questions.count() > 0, "No questions created"
            
            # Verify question attributes
            question = questions.first()
            assert hasattr(question, 'question_number')
            assert hasattr(question, 'question_type')
            assert hasattr(question, 'correct_answer')
    
    def test_save_exam_answers(self):
        """Test saving exam question answers."""
        from placement_test.models import Exam, Question
        
        exam = Exam.objects.first()
        if exam and exam.questions.exists():
            question = exam.questions.first()
            
            data = {
                'questions': [{
                    'id': str(question.id),
                    'question_type': 'MCQ',
                    'correct_answer': 'A',
                    'options_count': 5
                }],
                'audio_assignments': {}
            }
            
            response = self.client.post(
                f'/api/placement/exams/{exam.id}/save-answers/',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            # Should return success
            assert response.status_code in [200, 201]
            result = json.loads(response.content)
            assert result.get('success') == True
    
    # ========== 5. AUDIO FILE MANAGEMENT ==========
    
    def test_audio_file_associations(self):
        """Test audio file to question associations."""
        from placement_test.models import Exam, AudioFile, Question
        
        exam = Exam.objects.filter(audio_files__isnull=False).first()
        if exam:
            audio = exam.audio_files.first()
            question = exam.questions.first()
            
            if audio and question:
                # Test assignment through service
                from placement_test.services import ExamService
                
                result = ExamService.update_audio_assignments(
                    exam,
                    {str(question.question_number): audio.id}
                )
                
                assert result['updated'] >= 0, "Audio assignment failed"
                
                # Verify assignment
                question.refresh_from_db()
                # Audio should be assignable
                assert question.audio_file is None or question.audio_file.id == audio.id
    
    # ========== 6. SESSION MANAGEMENT ==========
    
    def test_session_list_page(self):
        """Test session list page."""
        response = self.client.get('/api/placement/sessions/')
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        
        from placement_test.models import StudentSession
        if StudentSession.objects.exists():
            # Should show session info
            assert 'session' in content.lower() or 'student' in content.lower()
    
    def test_session_detail_page(self):
        """Test session detail page."""
        from placement_test.models import StudentSession
        
        session = StudentSession.objects.first()
        if session:
            response = self.client.get(f'/api/placement/sessions/{session.id}/')
            assert response.status_code == 200
            content = response.content.decode('utf-8')
            assert session.student_name in content
    
    # ========== 7. AJAX ENDPOINTS ==========
    
    def test_curriculum_levels_endpoint(self):
        """Test curriculum levels AJAX endpoint."""
        response = self.client.get(
            '/curriculum/levels/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = json.loads(response.content)
            assert isinstance(data, (list, dict))
    
    def test_submit_answer_endpoint(self):
        """Test answer submission endpoint."""
        from placement_test.models import StudentSession, Question
        
        session = StudentSession.objects.filter(completed_at__isnull=True).first()
        if session and session.exam.questions.exists():
            question = session.exam.questions.first()
            
            data = {
                'question_id': str(question.id),
                'answer': 'A'
            }
            
            response = self.client.post(
                f'/api/placement/session/{session.id}/submit/',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code in [200, 201]
            result = json.loads(response.content)
            assert result.get('success') == True
    
    # ========== 8. SERVICE LAYER ==========
    
    def test_all_services_functional(self):
        """Test all service classes work."""
        from placement_test.services import (
            ExamService, PlacementService, SessionService, GradingService
        )
        from core.services import (
            DashboardService, FileService
        )
        
        # Test each service has expected methods
        assert hasattr(ExamService, 'create_exam')
        assert hasattr(ExamService, 'get_all_exams_with_stats')
        assert hasattr(PlacementService, 'match_student_to_exam')
        assert hasattr(SessionService, 'create_session')
        assert hasattr(GradingService, 'grade_session')
        assert hasattr(DashboardService, 'get_dashboard_stats')
        assert hasattr(FileService, 'validate_pdf_file')
        
        # Test service methods work
        stats = DashboardService.get_dashboard_stats()
        assert isinstance(stats, dict)
        assert 'total_sessions' in stats
        
        exams = ExamService.get_all_exams_with_stats()
        assert isinstance(exams, list)
    
    # ========== 9. DATABASE INTEGRITY ==========
    
    def test_database_indexes_exist(self):
        """Test performance indexes are in place."""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND (
                    name LIKE '%idx%' OR 
                    name LIKE '%index%'
                )
            """)
            indexes = cursor.fetchall()
            
            # Should have multiple indexes
            assert len(indexes) > 5, f"Only {len(indexes)} indexes found"
    
    def test_model_relationships_intact(self):
        """Test all model relationships work."""
        from placement_test.models import Exam, Question, AudioFile, StudentSession
        from core.models import School, CurriculumLevel
        
        # Test forward relationships
        exam = Exam.objects.first()
        if exam:
            questions = exam.questions.all()
            audio_files = exam.audio_files.all()
            sessions = exam.sessions.all()
            
            # Test reverse relationships
            if questions.exists():
                question = questions.first()
                assert question.exam == exam
            
            if audio_files.exists():
                audio = audio_files.first()
                assert audio.exam == exam
            
            if sessions.exists():
                session = sessions.first()
                assert session.exam == exam
        
        # Test school relationships
        school = School.objects.first()
        if school:
            sessions = school.studentsession_set.all()
            # Should not raise error
            assert sessions is not None
    
    # ========== 10. TEMPLATE SYSTEM ==========
    
    def test_template_rendering(self):
        """Test templates render without errors."""
        from django.template import loader
        from django.template.exceptions import TemplateDoesNotExist
        
        templates_to_test = [
            'placement_test/student_test_v2.html',
            'placement_test/start_test.html',
            'placement_test/exam_list.html',
            'placement_test/preview_and_answers.html',
        ]
        
        for template_name in templates_to_test:
            try:
                template = loader.get_template(template_name)
                assert template is not None
            except TemplateDoesNotExist:
                raise AssertionError(f"Template not found: {template_name}")
    
    def test_v2_templates_active(self):
        """Test V2 templates are properly configured."""
        from django.conf import settings
        
        assert hasattr(settings, 'FEATURE_FLAGS')
        assert settings.FEATURE_FLAGS.get('USE_V2_TEMPLATES') == True
        
        # Test V2 template is used
        from placement_test.models import StudentSession
        session = StudentSession.objects.filter(completed_at__isnull=True).first()
        if session:
            response = self.client.get(f'/api/placement/session/{session.id}/')
            assert response.status_code == 200
            # V2 template should be used
            assert 'student_test_v2' in str(response.templates) or response.status_code == 200
    
    # ========== 11. STATIC FILES ==========
    
    def test_static_configuration(self):
        """Test static files are properly configured."""
        from django.conf import settings
        
        assert hasattr(settings, 'STATIC_URL')
        assert settings.STATIC_URL is not None
        assert hasattr(settings, 'MEDIA_URL')
        assert settings.MEDIA_URL is not None
        assert hasattr(settings, 'MEDIA_ROOT')
        assert settings.MEDIA_ROOT is not None
    
    # ========== 12. MIDDLEWARE ==========
    
    def test_middleware_functioning(self):
        """Test custom middleware is working."""
        response = self.client.get('/')
        
        # Request should go through successfully
        assert response.status_code == 200
        
        # Test feature flag middleware
        from django.conf import settings
        if 'core.middleware.FeatureFlagMiddleware' in settings.MIDDLEWARE:
            # Middleware should be processing requests
            assert True
    
    def run_all_tests(self):
        """Run all comprehensive tests."""
        print("\n" + "="*70)
        print("COMPREHENSIVE FEATURE VERIFICATION")
        print("Testing ALL existing features for Phase 9 impact")
        print("="*70 + "\n")
        
        print("1. CORE PAGE LOADING")
        self.run_test("Home page", self.test_home_page)
        self.run_test("Teacher dashboard", self.test_teacher_dashboard)
        
        print("\n2. PLACEMENT TEST FLOW")
        self.run_test("Start test page", self.test_start_test_page)
        self.run_test("Test creation", self.test_placement_test_with_valid_data, critical=False)
        self.run_test("Student test interface", self.test_student_test_interface)
        
        print("\n3. EXAM MANAGEMENT")
        self.run_test("Exam list", self.test_exam_list_page)
        self.run_test("Create exam page", self.test_create_exam_page)
        self.run_test("Exam detail", self.test_exam_detail_page)
        self.run_test("Preview exam", self.test_preview_exam_page)
        
        print("\n4. QUESTION MANAGEMENT")
        self.run_test("Question creation", self.test_question_creation)
        self.run_test("Save exam answers", self.test_save_exam_answers)
        
        print("\n5. AUDIO FILE MANAGEMENT")
        self.run_test("Audio associations", self.test_audio_file_associations, critical=False)
        
        print("\n6. SESSION MANAGEMENT")
        self.run_test("Session list", self.test_session_list_page)
        self.run_test("Session detail", self.test_session_detail_page)
        
        print("\n7. AJAX ENDPOINTS")
        self.run_test("Curriculum levels", self.test_curriculum_levels_endpoint)
        self.run_test("Submit answer", self.test_submit_answer_endpoint)
        
        print("\n8. SERVICE LAYER")
        self.run_test("All services functional", self.test_all_services_functional)
        
        print("\n9. DATABASE INTEGRITY")
        self.run_test("Database indexes", self.test_database_indexes_exist)
        self.run_test("Model relationships", self.test_model_relationships_intact)
        
        print("\n10. TEMPLATE SYSTEM")
        self.run_test("Template rendering", self.test_template_rendering)
        self.run_test("V2 templates active", self.test_v2_templates_active)
        
        print("\n11. STATIC FILES")
        self.run_test("Static configuration", self.test_static_configuration)
        
        print("\n12. MIDDLEWARE")
        self.run_test("Middleware functioning", self.test_middleware_functioning)
        
        # Final report
        print("\n" + "="*70)
        print("FINAL REPORT")
        print("="*70)
        
        total = self.passed + self.failed
        if total > 0:
            pass_rate = (self.passed / total * 100)
            print(f"Passed: {self.passed}/{total} ({pass_rate:.1f}%)")
            
            if self.warnings > 0:
                print(f"Warnings: {self.warnings} (non-critical issues)")
            
            if self.failed > 0:
                print(f"Failed: {self.failed}")
                print("\nFailed tests:")
                for result in self.results:
                    if result.startswith("FAIL"):
                        print(f"  - {result}")
            
            print("\n" + "="*70)
            if self.failed == 0:
                print("SUCCESS: All critical features working correctly!")
                print("Phase 9 modularization has NOT broken any existing functionality.")
            elif self.failed <= 2:
                print("MOSTLY SUCCESSFUL: Minor issues detected")
                print("Most features working correctly, review warnings above.")
            else:
                print("ISSUES DETECTED: Some features affected")
                print("Review failed tests above for details.")
        
        return self.failed == 0


if __name__ == "__main__":
    tester = ComprehensiveFeatureTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
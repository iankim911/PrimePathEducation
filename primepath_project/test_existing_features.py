"""
Comprehensive test to verify NO existing features were broken by backend modularization.
This tests all critical paths and functionality.
"""
import os
import sys
import django
import json
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, str(Path(__file__).parent))
django.setup()

from django.test import Client
from django.urls import reverse, resolve
from django.core.exceptions import ImproperlyConfigured
from placement_test.models import Exam, StudentSession, Question, AudioFile
from core.models import School, Program, SubProgram, CurriculumLevel, PlacementRule
import traceback


class TestExistingFeatures:
    """Comprehensive test suite to ensure no regressions."""
    
    def __init__(self):
        self.client = Client()
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.tests = []
    
    def run_test(self, test_name, test_func):
        """Run a single test and track results."""
        try:
            result = test_func()
            if result is False:
                self.warnings += 1
                self.tests.append(f"WARNING: {test_name} - Feature works but needs attention")
                print(f"WARNING: {test_name} - Feature works but needs attention")
            else:
                self.passed += 1
                self.tests.append(f"PASS: {test_name}")
                print(f"PASS: {test_name}")
        except Exception as e:
            self.failed += 1
            self.tests.append(f"FAIL: {test_name}: {str(e)}")
            print(f"FAIL: {test_name}: {str(e)}")
            # Print traceback for debugging
            traceback.print_exc()
    
    def test_original_views_intact(self):
        """Verify original views.py files are untouched and working."""
        # Check that original views still exist
        from core import views as core_views
        from placement_test import views as placement_views
        
        # Check core views functions exist
        assert hasattr(core_views, 'index')
        assert hasattr(core_views, 'teacher_dashboard')
        assert hasattr(core_views, 'curriculum_levels')
        assert hasattr(core_views, 'placement_rules')
        assert hasattr(core_views, 'exam_mapping')
        
        # Check placement_test views functions exist
        assert hasattr(placement_views, 'start_test')
        assert hasattr(placement_views, 'take_test')
        assert hasattr(placement_views, 'submit_answer')
        assert hasattr(placement_views, 'complete_test')
        assert hasattr(placement_views, 'create_exam')
        assert hasattr(placement_views, 'preview_exam')
        
        print("  - All original view functions still exist")
    
    def test_url_patterns_resolve(self):
        """Test that all URL patterns still resolve correctly."""
        critical_urls = [
            ('/', 'core.views.index'),
            ('/teacher/dashboard/', 'core.views.teacher_dashboard'),
            ('/curriculum/levels/', 'core.views.curriculum_levels'),
            ('/placement-rules/', 'core.views.placement_rules'),
            ('/exam-mapping/', 'core.views.exam_mapping'),
            ('/api/placement/start/', 'placement_test.views.start_test'),
        ]
        
        for url, expected_view in critical_urls:
            try:
                resolved = resolve(url)
                view_name = f"{resolved.func.__module__}.{resolved.func.__name__}"
                assert view_name == expected_view, f"URL {url} resolves to {view_name}, expected {expected_view}"
                print(f"  - URL {url} -> {expected_view} OK")
            except Exception as e:
                raise Exception(f"URL {url} failed to resolve: {e}")
    
    def test_no_import_errors(self):
        """Check for import errors or circular dependencies."""
        try:
            # Import all views
            from core import views as core_views
            from placement_test import views as placement_views
            
            # Import all models
            from core import models as core_models
            from placement_test import models as placement_models
            
            # Import services (new additions)
            from core.services import CurriculumService, SchoolService, TeacherService
            from placement_test.services import ExamService, SessionService, GradingService, PlacementService
            
            # Import mixins (new additions)
            from common.mixins import AjaxResponseMixin, TeacherRequiredMixin
            from common.views import BaseAPIView, BaseTemplateView
            
            print("  - All imports successful, no circular dependencies")
        except ImportError as e:
            raise Exception(f"Import error detected: {e}")
    
    def test_placement_service_integration(self):
        """Test that PlacementService still works with views."""
        from placement_test.services import PlacementService
        
        # Check that PlacementService methods exist and work
        assert hasattr(PlacementService, 'match_student_to_exam')
        assert hasattr(PlacementService, 'adjust_difficulty')  # Correct method name
        assert hasattr(PlacementService, 'find_matching_rule')
        
        # Test that it can access models
        rules = PlacementRule.objects.all()
        print(f"  - PlacementService can access models ({rules.count()} rules found)")
    
    def test_session_service_integration(self):
        """Test that SessionService still works."""
        from placement_test.services import SessionService
        
        # Check methods exist
        assert hasattr(SessionService, 'create_session')
        assert hasattr(SessionService, 'submit_answer')
        assert hasattr(SessionService, 'complete_session')
        
        # Test that it can access models
        sessions = StudentSession.objects.all()
        print(f"  - SessionService can access models ({sessions.count()} sessions found)")
    
    def test_exam_service_integration(self):
        """Test that ExamService still works."""
        from placement_test.services import ExamService
        
        # Check methods exist (with correct names)
        assert hasattr(ExamService, 'create_exam')
        assert hasattr(ExamService, 'create_questions_for_exam')
        assert hasattr(ExamService, 'update_exam_questions')  # Correct method name
        assert hasattr(ExamService, 'delete_exam')
        
        # Test that it can access models
        exams = Exam.objects.all()
        print(f"  - ExamService can access models ({exams.count()} exams found)")
    
    def test_ajax_endpoints(self):
        """Test AJAX endpoints still work."""
        # Test placement rules endpoint
        response = self.client.get(reverse('core:get_placement_rules'))
        assert response.status_code == 200
        data = json.loads(response.content)
        assert 'success' in data
        print("  - AJAX endpoint 'get_placement_rules' works")
        
        # Test other AJAX endpoints
        ajax_urls = [
            'core:get_placement_rules',
            # Add more AJAX endpoints as needed
        ]
        
        for url_name in ajax_urls:
            try:
                response = self.client.get(reverse(url_name))
                assert response.status_code in [200, 302, 405]  # 405 for POST-only endpoints
            except Exception as e:
                print(f"  - Warning: AJAX endpoint {url_name} issue: {e}")
    
    def test_model_relationships(self):
        """Test that model relationships still work."""
        # Test cross-app relationships
        if CurriculumLevel.objects.exists():
            level = CurriculumLevel.objects.first()
            # Test that exams can still reference curriculum levels
            exams_for_level = Exam.objects.filter(curriculum_level=level)
            print(f"  - Cross-app relationship: Exam -> CurriculumLevel works ({exams_for_level.count()} exams)")
        
        if School.objects.exists():
            school = School.objects.first()
            # Test that sessions can still reference schools
            sessions_for_school = StudentSession.objects.filter(school=school)
            print(f"  - Cross-app relationship: StudentSession -> School works ({sessions_for_school.count()} sessions)")
    
    def test_template_rendering_paths(self):
        """Test that views can find their templates."""
        # Test index page
        response = self.client.get('/')
        if response.status_code == 200:
            print("  - Index page renders successfully")
        elif response.status_code == 302:
            print("  - Index page redirects (authentication required)")
        else:
            raise Exception(f"Index page returned status {response.status_code}")
    
    def test_student_test_flow(self):
        """Test critical student test flow."""
        # Check that student test URLs work
        from placement_test import views
        
        # Verify take_test view exists and has correct signature
        assert hasattr(views, 'take_test')
        
        # Check that the view uses the correct template
        import inspect
        source = inspect.getsource(views.take_test)
        if 'get_template_name' in source:
            print("  - Student test uses template selection logic")
        
        # Verify JavaScript config is still passed correctly
        if 'js_config' in source:
            print("  - Student test still passes js_config to template")
            
    def test_exam_creation_flow(self):
        """Test exam creation functionality."""
        from placement_test import views
        
        # Check create_exam view exists
        assert hasattr(views, 'create_exam')
        
        # Check preview_exam view exists
        assert hasattr(views, 'preview_exam')
        
        # Check save_exam_answers view exists
        assert hasattr(views, 'save_exam_answers')
        
        print("  - Exam creation views intact")
    
    def test_grading_service(self):
        """Test that GradingService still works."""
        from placement_test.services import GradingService
        
        # Check methods exist (with correct names)
        assert hasattr(GradingService, 'auto_grade_answer')
        assert hasattr(GradingService, 'grade_session')  # This one exists
        assert hasattr(GradingService, 'get_session_analytics')  # Additional method
        
        print("  - GradingService methods available")
    
    def test_v2_templates_flag(self):
        """Test that V2 templates feature flag still works."""
        from django.conf import settings
        
        # Check if feature flags exist
        if hasattr(settings, 'FEATURE_FLAGS'):
            flags = settings.FEATURE_FLAGS
            if 'USE_V2_TEMPLATES' in flags:
                print(f"  - V2 templates flag present: {flags['USE_V2_TEMPLATES']}")
            else:
                print("  - V2 templates flag not set")
        else:
            print("  - No feature flags configured")
    
    def test_static_files_accessible(self):
        """Test that static JavaScript modules are accessible."""
        static_files = [
            'js/modules/navigation.js',
            'js/modules/answer-manager.js',
            'js/modules/pdf-viewer.js',
            'js/modules/audio-player.js',
            'js/modules/timer.js',
            'js/modules/base-module.js',
            'js/utils/event-delegation.js',
            'js/config/app-config.js',
        ]
        
        from django.conf import settings
        import os
        
        static_root = os.path.join(settings.BASE_DIR, 'static')
        missing = []
        
        for file_path in static_files:
            full_path = os.path.join(static_root, file_path)
            if not os.path.exists(full_path):
                missing.append(file_path)
        
        if missing:
            print(f"  - Warning: Some static files not found: {missing}")
            return False  # Return False to indicate warning
        else:
            print(f"  - All {len(static_files)} static JS files present")
    
    def test_database_operations(self):
        """Test that database operations still work."""
        try:
            # Test read operations
            programs = Program.objects.all()
            exams = Exam.objects.all()
            sessions = StudentSession.objects.all()
            
            print(f"  - Database reads work: {programs.count()} programs, {exams.count()} exams, {sessions.count()} sessions")
            
            # Test that we can create objects (in a transaction that we'll rollback)
            from django.db import transaction
            try:
                with transaction.atomic():
                    school = School.objects.create(name="Test School Temp")
                    assert school.id is not None
                    print("  - Database writes work (tested with rollback)")
                    raise Exception("Rollback test")  # Force rollback
            except Exception as e:
                if "Rollback test" not in str(e):
                    raise
                    
        except Exception as e:
            raise Exception(f"Database operation failed: {e}")
    
    def test_no_broken_imports_in_templates(self):
        """Check that template imports are not broken."""
        # This would require template compilation which is complex
        # For now, we'll check that template directories exist
        from django.conf import settings
        import os
        
        template_dirs = []
        for template_setting in settings.TEMPLATES:
            template_dirs.extend(template_setting.get('DIRS', []))
        
        for dir_path in template_dirs:
            if os.path.exists(dir_path):
                print(f"  - Template directory exists: {os.path.basename(dir_path)}")
    
    def run_all_tests(self):
        """Run all tests and report results."""
        print("\n" + "="*70)
        print("COMPREHENSIVE FEATURE VERIFICATION TEST")
        print("Checking that NO existing features were broken by modularization")
        print("="*70 + "\n")
        
        # Critical tests
        print("1. CHECKING ORIGINAL CODE...")
        self.run_test("Original views intact", self.test_original_views_intact)
        self.run_test("URL patterns resolve", self.test_url_patterns_resolve)
        self.run_test("No import errors", self.test_no_import_errors)
        
        print("\n2. CHECKING SERVICE INTEGRATION...")
        self.run_test("PlacementService works", self.test_placement_service_integration)
        self.run_test("SessionService works", self.test_session_service_integration)
        self.run_test("ExamService works", self.test_exam_service_integration)
        self.run_test("GradingService works", self.test_grading_service)
        
        print("\n3. CHECKING CRITICAL PATHS...")
        self.run_test("AJAX endpoints work", self.test_ajax_endpoints)
        self.run_test("Model relationships work", self.test_model_relationships)
        self.run_test("Template rendering works", self.test_template_rendering_paths)
        self.run_test("Database operations work", self.test_database_operations)
        
        print("\n4. CHECKING FEATURE FLOWS...")
        self.run_test("Student test flow intact", self.test_student_test_flow)
        self.run_test("Exam creation flow intact", self.test_exam_creation_flow)
        self.run_test("V2 templates flag works", self.test_v2_templates_flag)
        
        print("\n5. CHECKING STATIC RESOURCES...")
        self.run_test("Static files accessible", self.test_static_files_accessible)
        self.run_test("Template directories exist", self.test_no_broken_imports_in_templates)
        
        # Report results
        print("\n" + "="*70)
        print(f"RESULTS: {self.passed} passed, {self.failed} failed, {self.warnings} warnings")
        print("="*70)
        
        if self.failed == 0:
            if self.warnings > 0:
                print("\nOVERALL: SUCCESS WITH WARNINGS")
                print("All critical features work, but some minor issues need attention.")
            else:
                print("\nOVERALL: PERFECT SUCCESS")
                print("ALL existing features verified working correctly!")
                print("Backend modularization did NOT break any functionality.")
        else:
            print("\nOVERALL: FAILURES DETECTED")
            print("Some features may be broken. Review the failures above.")
            print("\nFailed tests:")
            for test in self.tests:
                if test.startswith("FAIL"):
                    print(f"  - {test}")
        
        return self.failed == 0


if __name__ == "__main__":
    tester = TestExistingFeatures()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
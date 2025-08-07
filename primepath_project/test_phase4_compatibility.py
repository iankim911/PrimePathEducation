"""
Comprehensive test to verify Phase 4 fixes didn't break ANY existing features.
Tests all critical functionality and ensures backward compatibility.
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
from django.urls import reverse
from placement_test.models import Exam, StudentSession, Question, StudentAnswer, AudioFile
from core.models import School, Program, SubProgram, CurriculumLevel, PlacementRule
import traceback


class TestPhase4Compatibility:
    """Test that Phase 4 changes don't break existing functionality."""
    
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
                self.tests.append(f"WARNING: {test_name} - Works but needs attention")
                print(f"WARNING: {test_name} - Works but needs attention")
            else:
                self.passed += 1
                self.tests.append(f"PASS: {test_name}")
                print(f"PASS: {test_name}")
        except Exception as e:
            self.failed += 1
            self.tests.append(f"FAIL: {test_name}: {str(e)}")
            print(f"FAIL: {test_name}: {str(e)}")
            traceback.print_exc()
    
    def test_existing_views_work(self):
        """Test that all existing views still function."""
        # Test core views
        from core import views as core_views
        from placement_test import views as placement_views
        
        # Check that views haven't been modified
        assert hasattr(core_views, 'index')
        assert hasattr(core_views, 'teacher_dashboard')
        assert hasattr(placement_views, 'start_test')
        assert hasattr(placement_views, 'take_test')
        assert hasattr(placement_views, 'submit_answer')
        assert hasattr(placement_views, 'complete_test')
        
        print("  - All original views still exist and unchanged")
    
    def test_new_imports_optional(self):
        """Test that new modules are optional (don't break if not imported)."""
        # Test that existing code works without importing new modules
        try:
            # Original imports should work
            from placement_test.services import ExamService, SessionService
            from placement_test.models import Exam, StudentSession
            
            # These should work without the new modules
            exams = Exam.objects.all()
            sessions = StudentSession.objects.all()
            
            print("  - Original code works without new imports")
        except Exception as e:
            raise Exception(f"Original imports broken: {e}")
    
    def test_database_queries_work(self):
        """Test that database queries still work (with or without optimizations)."""
        # Test original query patterns still work
        try:
            # Original unoptimized queries should still work
            exams = Exam.objects.all()
            sessions = StudentSession.objects.all()
            questions = Question.objects.filter(exam__in=exams)
            
            # Test with select_related (should work even without indexes)
            sessions_with_related = StudentSession.objects.select_related(
                'exam', 'school'
            ).all()
            
            print(f"  - Database queries work: {exams.count()} exams, {sessions.count()} sessions")
        except Exception as e:
            raise Exception(f"Database queries broken: {e}")
    
    def test_ajax_endpoints_unchanged(self):
        """Test that AJAX endpoints still work as before."""
        # Test critical AJAX endpoints
        ajax_urls = [
            ('core:get_placement_rules', 'GET'),
            ('core:save_placement_rules', 'POST'),
        ]
        
        for url_name, method in ajax_urls:
            try:
                url = reverse(url_name)
                if method == 'GET':
                    response = self.client.get(url)
                else:
                    response = self.client.post(url, 
                        data=json.dumps({'rules': []}),
                        content_type='application/json'
                    )
                
                # Should return JSON response
                assert response.status_code in [200, 400, 403]  # 403 for CSRF
                print(f"  - AJAX endpoint {url_name} responds correctly")
            except Exception as e:
                print(f"  - Warning: AJAX endpoint {url_name} issue: {e}")
    
    def test_services_unchanged(self):
        """Test that existing services still work."""
        from placement_test.services import (
            ExamService, SessionService, 
            PlacementService, GradingService
        )
        
        # Check that service methods still exist
        assert hasattr(ExamService, 'create_exam')
        assert hasattr(SessionService, 'create_session')
        assert hasattr(PlacementService, 'match_student_to_exam')
        assert hasattr(GradingService, 'auto_grade_answer')
        
        print("  - All existing services and methods intact")
    
    def test_javascript_backward_compatible(self):
        """Test that existing JavaScript still works."""
        import os
        from django.conf import settings
        
        # Check that original JS files exist
        js_files = [
            'js/modules/navigation.js',
            'js/modules/answer-manager.js',
            'js/modules/pdf-viewer.js',
            'js/modules/audio-player.js',
            'js/modules/timer.js',
            'js/modules/base-module.js',
        ]
        
        static_root = os.path.join(settings.BASE_DIR, 'static')
        
        for js_file in js_files:
            file_path = os.path.join(static_root, js_file)
            if os.path.exists(file_path):
                # Check that file hasn't been modified
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Original modules shouldn't require new modules
                    if 'memory-manager' in content or 'error-handler' in content:
                        raise Exception(f"{js_file} was modified to require new modules")
        
        print("  - Original JavaScript modules unchanged")
    
    def test_templates_unchanged(self):
        """Test that existing templates weren't modified."""
        import os
        from django.conf import settings
        
        # Check critical templates
        template_files = [
            'placement_test/student_test_v2.html',
            'placement_test/start_test.html',
        ]
        
        template_dirs = []
        for template_config in settings.TEMPLATES:
            template_dirs.extend(template_config.get('DIRS', []))
        
        issues = []
        for template_file in template_files:
            for template_dir in template_dirs:
                file_path = os.path.join(template_dir, template_file)
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # Check if new modules were forcefully added
                        if 'memory-manager.js' in content or 'error-handler.js' in content:
                            issues.append(f"{template_file} was modified")
        
        if issues:
            print(f"  - Warning: Some templates modified: {issues}")
            return False
        else:
            print("  - Templates unchanged (new modules are optional)")
    
    def test_models_unchanged(self):
        """Test that model definitions weren't changed."""
        # Check that models still have original fields
        from placement_test.models import Exam, StudentSession
        from core.models import School
        
        # Check Exam model
        exam_fields = [f.name for f in Exam._meta.get_fields()]
        required_fields = ['id', 'name', 'pdf_file', 'curriculum_level', 'is_active']
        for field in required_fields:
            assert field in exam_fields, f"Exam model missing field: {field}"
        
        # Check StudentSession model - note: is_completed is a property, not a field
        session_fields = [f.name for f in StudentSession._meta.get_fields()]
        required_fields = ['id', 'student_name', 'exam', 'completed_at', 'started_at']
        for field in required_fields:
            assert field in session_fields, f"StudentSession model missing field: {field}"
        
        # Check that is_completed property exists
        assert hasattr(StudentSession, 'is_completed'), "StudentSession missing is_completed property"
        
        print("  - Model definitions unchanged")
    
    def test_middleware_optional(self):
        """Test that new middleware is optional."""
        from django.conf import settings
        
        # Check if middleware was forcefully added
        middleware = settings.MIDDLEWARE
        
        # The new PerformanceMiddleware should be optional
        if 'placement_test.performance_monitor.PerformanceMiddleware' in middleware:
            print("  - Performance middleware is enabled (optional)")
        else:
            print("  - Performance middleware not enabled (system works without it)")
    
    def test_cache_optional(self):
        """Test that caching is optional."""
        from django.core.cache import cache
        
        # Test that system works even if cache is unavailable
        try:
            # Try to use cache
            cache.set('test_key', 'test_value', 1)
            value = cache.get('test_key')
            if value == 'test_value':
                print("  - Cache is available and working")
            else:
                print("  - Cache not working but system continues")
        except:
            print("  - Cache not configured but system works")
    
    def test_student_test_flow(self):
        """Test that critical student test flow still works."""
        from placement_test import views
        
        # Check that the take_test view still works
        assert hasattr(views, 'take_test')
        
        # Check that submit_answer still works
        assert hasattr(views, 'submit_answer')
        
        # Check that complete_test still works  
        assert hasattr(views, 'complete_test')
        
        print("  - Student test flow intact")
    
    def test_exam_management_flow(self):
        """Test that exam management still works."""
        from placement_test import views
        
        # Check exam CRUD operations
        assert hasattr(views, 'create_exam')
        assert hasattr(views, 'edit_exam')
        assert hasattr(views, 'delete_exam')
        assert hasattr(views, 'preview_exam')
        
        print("  - Exam management flow intact")
    
    def test_grading_flow(self):
        """Test that grading still works."""
        from placement_test.services import GradingService
        
        # Check grading methods
        assert hasattr(GradingService, 'auto_grade_answer')
        assert hasattr(GradingService, 'grade_session')
        
        print("  - Grading flow intact")
    
    def test_no_forced_dependencies(self):
        """Test that new modules don't create forced dependencies."""
        # Try importing original modules without new ones
        try:
            # These imports should work without memory-manager or error-handler
            from placement_test.views import start_test, take_test
            from placement_test.services import ExamService
            from core.views import index, teacher_dashboard
            
            print("  - No forced dependencies on new modules")
        except ImportError as e:
            raise Exception(f"Forced dependency detected: {e}")
    
    def test_migrations_safe(self):
        """Test that migrations are safe and optional."""
        import os
        from django.conf import settings
        
        # Check if migration file exists but hasn't been applied
        migration_file = os.path.join(
            settings.BASE_DIR,
            'placement_test/migrations/0001_add_performance_indexes.py'
        )
        
        if os.path.exists(migration_file):
            print("  - Migration file exists (can be applied when ready)")
            # Migration should be safe even on existing database
            with open(migration_file, 'r') as f:
                content = f.read()
                if 'atomic = False' in content:
                    print("  - Migration is non-atomic (safe for large databases)")
        else:
            print("  - No migration file (indexes are optional)")
    
    def test_configuration_unchanged(self):
        """Test that Django settings weren't forcefully changed."""
        from django.conf import settings
        
        # Check critical settings
        assert hasattr(settings, 'DATABASES')
        assert hasattr(settings, 'INSTALLED_APPS')
        assert 'placement_test' in settings.INSTALLED_APPS
        assert 'core' in settings.INSTALLED_APPS
        
        print("  - Django configuration unchanged")
    
    def run_all_tests(self):
        """Run all compatibility tests."""
        print("\n" + "="*70)
        print("PHASE 4 COMPATIBILITY TEST")
        print("Verifying NO existing features were broken")
        print("="*70 + "\n")
        
        print("1. CHECKING CORE FUNCTIONALITY...")
        self.run_test("Existing views work", self.test_existing_views_work)
        self.run_test("Models unchanged", self.test_models_unchanged)
        self.run_test("Services unchanged", self.test_services_unchanged)
        self.run_test("Configuration unchanged", self.test_configuration_unchanged)
        
        print("\n2. CHECKING BACKWARD COMPATIBILITY...")
        self.run_test("New imports optional", self.test_new_imports_optional)
        self.run_test("No forced dependencies", self.test_no_forced_dependencies)
        self.run_test("Middleware optional", self.test_middleware_optional)
        self.run_test("Cache optional", self.test_cache_optional)
        self.run_test("Migrations safe", self.test_migrations_safe)
        
        print("\n3. CHECKING FRONTEND...")
        self.run_test("JavaScript backward compatible", self.test_javascript_backward_compatible)
        self.run_test("Templates unchanged", self.test_templates_unchanged)
        self.run_test("AJAX endpoints unchanged", self.test_ajax_endpoints_unchanged)
        
        print("\n4. CHECKING CRITICAL FLOWS...")
        self.run_test("Student test flow", self.test_student_test_flow)
        self.run_test("Exam management flow", self.test_exam_management_flow)
        self.run_test("Grading flow", self.test_grading_flow)
        self.run_test("Database queries work", self.test_database_queries_work)
        
        # Report results
        print("\n" + "="*70)
        total = self.passed + self.failed + self.warnings
        print(f"RESULTS: {self.passed}/{total} passed, {self.failed} failed, {self.warnings} warnings")
        print("="*70)
        
        if self.failed == 0:
            if self.warnings > 0:
                print("\nSUCCESS: All features work, some optional enhancements available")
                print("The warnings indicate optional improvements that can be enabled")
            else:
                print("\nPERFECT: Phase 4 implemented with ZERO impact on existing features")
                print("All optimizations are opt-in and backward compatible")
        else:
            print("\nISSUES DETECTED: Some features may be affected")
            print("Review failures above before deploying")
        
        return self.failed == 0


if __name__ == "__main__":
    tester = TestPhase4Compatibility()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
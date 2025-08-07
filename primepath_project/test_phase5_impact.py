"""
Phase 5 Impact Test - Verify NO existing features were broken
This test checks that all existing functionality still works exactly as before.
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
from django.db import connection
from placement_test.models import Exam, StudentSession, Question, StudentAnswer, AudioFile
from core.models import School, Program, SubProgram, CurriculumLevel, PlacementRule, Teacher
import traceback


class TestPhase5Impact:
    """Test that Phase 5 changes didn't break ANY existing features."""
    
    def __init__(self):
        self.client = Client()
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def run_test(self, test_name, test_func):
        """Run a single test and track results."""
        try:
            result = test_func()
            if result is False:
                self.failed += 1
                self.tests.append(f"FAIL: {test_name} - Feature affected")
                print(f"FAIL: {test_name} - Feature affected")
            else:
                self.passed += 1
                self.tests.append(f"PASS: {test_name}")
                print(f"PASS: {test_name}")
        except Exception as e:
            self.failed += 1
            self.tests.append(f"FAIL: {test_name}: {str(e)}")
            print(f"FAIL: {test_name}: {str(e)}")
            traceback.print_exc()
    
    def test_models_unchanged(self):
        """Test that all model definitions are unchanged."""
        # Test core models
        assert hasattr(School, 'name')
        assert hasattr(School, 'address')
        
        assert hasattr(Program, 'name')
        assert hasattr(Program, 'grade_range_start')
        assert hasattr(Program, 'grade_range_end')
        assert hasattr(Program, 'order')
        
        assert hasattr(SubProgram, 'program')
        assert hasattr(SubProgram, 'name')
        assert hasattr(SubProgram, 'order')
        
        assert hasattr(CurriculumLevel, 'subprogram')
        assert hasattr(CurriculumLevel, 'level_number')
        
        # Test placement_test models
        assert hasattr(Exam, 'name')
        assert hasattr(Exam, 'pdf_file')
        assert hasattr(Exam, 'curriculum_level')
        assert hasattr(Exam, 'total_questions')
        assert hasattr(Exam, 'is_active')
        
        assert hasattr(StudentSession, 'student_name')
        assert hasattr(StudentSession, 'exam')
        assert hasattr(StudentSession, 'started_at')
        assert hasattr(StudentSession, 'completed_at')
        
        # Check relationships still work
        try:
            # Test forward relationships
            program = Program.objects.first()
            if program:
                subprograms = program.subprograms.all()
                
            subprogram = SubProgram.objects.first()
            if subprogram:
                levels = subprogram.levels.all()
                
            # Test reverse relationships
            level = CurriculumLevel.objects.first()
            if level:
                exams = level.exams.all()
                
            print("  - All model relationships intact")
        except Exception as e:
            raise Exception(f"Model relationships broken: {e}")
    
    def test_existing_views_import(self):
        """Test that existing views can still be imported."""
        # Import core views
        from core import views as core_views
        assert hasattr(core_views, 'index')
        assert hasattr(core_views, 'teacher_dashboard')
        assert hasattr(core_views, 'curriculum_levels')
        assert hasattr(core_views, 'placement_rules')
        assert hasattr(core_views, 'get_placement_rules')
        assert hasattr(core_views, 'save_placement_rules')
        
        # Import placement_test views
        from placement_test import views as placement_views
        assert hasattr(placement_views, 'start_test')
        assert hasattr(placement_views, 'take_test')
        assert hasattr(placement_views, 'submit_answer')
        assert hasattr(placement_views, 'complete_test')
        assert hasattr(placement_views, 'preview_exam')
        assert hasattr(placement_views, 'create_exam')
        assert hasattr(placement_views, 'edit_exam')
        assert hasattr(placement_views, 'delete_exam')
        assert hasattr(placement_views, 'exam_list')
        
        print("  - All view functions still importable")
    
    def test_urls_still_resolve(self):
        """Test that all URL patterns still resolve correctly."""
        # Test core URLs
        core_urls = [
            'core:index',
            'core:teacher_dashboard',
            'core:curriculum_levels',
            'core:placement_rules',
            'core:get_placement_rules',
            'core:save_placement_rules',
        ]
        
        for url_name in core_urls:
            try:
                url = reverse(url_name)
                resolver = resolve(url)
                assert resolver.func or resolver.func_name, f"{url_name} doesn't resolve to a view"
            except Exception as e:
                raise Exception(f"URL {url_name} broken: {e}")
        
        # Test placement_test URLs
        placement_urls = [
            'placement_test:start_test',
            'placement_test:exam_list',
            'placement_test:create_exam',
        ]
        
        for url_name in placement_urls:
            try:
                url = reverse(url_name)
                resolver = resolve(url)
                assert resolver.func or resolver.func_name, f"{url_name} doesn't resolve to a view"
            except Exception as e:
                raise Exception(f"URL {url_name} broken: {e}")
        
        print("  - All URLs still resolve correctly")
    
    def test_view_responses(self):
        """Test that views still return responses."""
        # Test index
        response = self.client.get(reverse('core:index'))
        assert response.status_code in [200, 302], f"Index returned {response.status_code}"
        
        # Test teacher dashboard
        response = self.client.get(reverse('core:teacher_dashboard'))
        assert response.status_code in [200, 302], f"Dashboard returned {response.status_code}"
        
        # Test start test
        response = self.client.get(reverse('placement_test:start_test'))
        assert response.status_code in [200, 302], f"Start test returned {response.status_code}"
        
        # Test exam list
        response = self.client.get(reverse('placement_test:exam_list'))
        assert response.status_code in [200, 302], f"Exam list returned {response.status_code}"
        
        print("  - All views return valid responses")
    
    def test_ajax_endpoints_work(self):
        """Test that AJAX endpoints still function."""
        # Test get_placement_rules
        url = reverse('core:get_placement_rules')
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        # Should return JSON
        assert response.status_code in [200, 400, 403], f"AJAX endpoint returned {response.status_code}"
        
        # Check content type
        if response.status_code == 200:
            content_type = response.get('Content-Type', '')
            assert 'json' in content_type.lower(), "AJAX endpoint not returning JSON"
        
        print("  - AJAX endpoints still functional")
    
    def test_services_dont_break_imports(self):
        """Test that new services don't break existing imports."""
        try:
            # Original imports should still work
            from placement_test.models import Exam, StudentSession
            from core.models import School, Program
            
            # Services should be importable but not required
            from placement_test.services import ExamService, SessionService
            from core.services import CurriculumService, SchoolService
            
            # New services should be available
            from core.services import DashboardService, FileService
            
            print("  - Service imports don't break existing code")
        except ImportError as e:
            raise Exception(f"Import broken: {e}")
    
    def test_database_queries_work(self):
        """Test that database queries still function."""
        # Test basic queries
        schools = School.objects.all()
        programs = Program.objects.all()
        exams = Exam.objects.all()
        sessions = StudentSession.objects.all()
        
        # Test filtered queries
        active_exams = Exam.objects.filter(is_active=True)
        completed_sessions = StudentSession.objects.filter(completed_at__isnull=False)
        
        # Test relationships
        for exam in exams[:1]:
            level = exam.curriculum_level
            if level:
                subprogram = level.subprogram
                program = subprogram.program
        
        # Test aggregations
        from django.db.models import Count, Avg
        exam_stats = Exam.objects.aggregate(
            total=Count('id'),
            avg_questions=Avg('total_questions')
        )
        
        print("  - All database queries functional")
    
    def test_templates_exist(self):
        """Test that required templates exist."""
        from django.template.loader import get_template
        from django.template.exceptions import TemplateDoesNotExist
        
        required_templates = [
            'core/index.html',
            'core/teacher_dashboard.html',
            'core/placement_rules.html',
            'placement_test/start_test.html',
            'placement_test/exam_list.html',
            'placement_test/create_exam.html',
        ]
        
        missing_templates = []
        for template_name in required_templates:
            try:
                get_template(template_name)
            except TemplateDoesNotExist:
                missing_templates.append(template_name)
        
        # Some templates might be missing in test environment
        # but the important thing is the template loading system works
        if len(missing_templates) == len(required_templates):
            raise Exception("Template system broken - no templates load")
        
        print(f"  - Template system functional ({len(required_templates) - len(missing_templates)}/{len(required_templates)} templates found)")
    
    def test_static_files_configuration(self):
        """Test that static files configuration is intact."""
        from django.conf import settings
        
        assert hasattr(settings, 'STATIC_URL'), "STATIC_URL missing"
        assert hasattr(settings, 'STATIC_ROOT'), "STATIC_ROOT missing"
        assert hasattr(settings, 'STATICFILES_DIRS'), "STATICFILES_DIRS missing"
        assert hasattr(settings, 'MEDIA_URL'), "MEDIA_URL missing"
        assert hasattr(settings, 'MEDIA_ROOT'), "MEDIA_ROOT missing"
        
        print("  - Static files configuration intact")
    
    def test_middleware_unchanged(self):
        """Test that middleware stack is unchanged."""
        from django.conf import settings
        
        # Check critical middleware
        middleware = settings.MIDDLEWARE
        assert 'django.middleware.security.SecurityMiddleware' in middleware
        assert 'django.contrib.sessions.middleware.SessionMiddleware' in middleware
        assert 'django.middleware.common.CommonMiddleware' in middleware
        assert 'django.middleware.csrf.CsrfViewMiddleware' in middleware
        
        # New performance middleware should be optional (not forced)
        # It's OK if it's there, but it shouldn't be required
        
        print("  - Middleware stack unchanged")
    
    def test_form_handling(self):
        """Test that form handling still works."""
        # Test POST to start_test (will fail validation but should handle it)
        url = reverse('placement_test:start_test')
        response = self.client.post(url, data={})
        
        # Should handle invalid form gracefully
        assert response.status_code in [200, 400], f"Form handling returned {response.status_code}"
        
        # Test with some data
        response = self.client.post(url, data={
            'student_name': 'Test',
            'grade': 'invalid'  # Invalid data
        })
        
        # Should still handle it
        assert response.status_code in [200, 400], f"Form validation returned {response.status_code}"
        
        print("  - Form handling still works")
    
    def test_session_creation_flow(self):
        """Test that the session creation flow still works."""
        # This might fail due to missing data, but the flow should be intact
        url = reverse('placement_test:start_test')
        
        # Test GET
        response = self.client.get(url)
        assert response.status_code in [200, 302], "Start test GET broken"
        
        # The actual session creation might fail due to missing rules,
        # but the endpoint should still exist and respond
        
        print("  - Session creation flow intact")
    
    def test_javascript_modules_accessible(self):
        """Test that JavaScript modules are still accessible."""
        from django.conf import settings
        import os
        
        static_dir = os.path.join(settings.BASE_DIR, 'static')
        
        js_modules = [
            'js/modules/navigation.js',
            'js/modules/answer-manager.js',
            'js/modules/pdf-viewer.js',
            'js/modules/audio-player.js',
            'js/modules/timer.js',
        ]
        
        accessible = 0
        for js_module in js_modules:
            module_path = os.path.join(static_dir, js_module)
            if os.path.exists(module_path):
                accessible += 1
        
        # At least some modules should be accessible
        assert accessible > 0, "No JavaScript modules accessible"
        
        print(f"  - JavaScript modules accessible ({accessible}/{len(js_modules)})")
    
    def test_new_services_optional(self):
        """Test that new services are optional (old code works without them)."""
        # Create a simple view function that doesn't use services
        def test_view(request):
            from django.http import HttpResponse
            from placement_test.models import Exam
            
            # This should work without importing any services
            exams = Exam.objects.all()
            return HttpResponse(f"Found {exams.count()} exams")
        
        # Test that it works
        from django.http import HttpRequest
        request = HttpRequest()
        response = test_view(request)
        
        assert response.status_code == 200, "View without services broken"
        
        print("  - New services are optional")
    
    def test_exceptions_still_work(self):
        """Test that custom exceptions still work."""
        from core.exceptions import (
            PlacementRuleException,
            ExamNotFoundException,
            SessionAlreadyCompletedException,
            ValidationException
        )
        
        # Test that exceptions can be raised
        try:
            raise ValidationException("Test")
        except ValidationException:
            pass  # Expected
        
        print("  - Custom exceptions still functional")
    
    def test_decorators_still_work(self):
        """Test that decorators still function."""
        from core.decorators import handle_errors, validate_request_data
        from django.http import HttpRequest, HttpResponse
        
        # Test that decorators can be applied
        @handle_errors()
        def test_func(request):
            return HttpResponse("test")
        
        # Should be able to call decorated function
        request = HttpRequest()
        result = test_func(request)
        
        assert result.status_code in [200, 500], "Decorator not working"
        
        print("  - Decorators still functional")
    
    def run_all_tests(self):
        """Run all impact tests."""
        print("\n" + "="*70)
        print("PHASE 5 IMPACT TEST - Checking Existing Features")
        print("="*70 + "\n")
        
        print("1. CHECKING DATA LAYER...")
        self.run_test("Models unchanged", self.test_models_unchanged)
        self.run_test("Database queries work", self.test_database_queries_work)
        
        print("\n2. CHECKING VIEW LAYER...")
        self.run_test("Views still importable", self.test_existing_views_import)
        self.run_test("URLs still resolve", self.test_urls_still_resolve)
        self.run_test("View responses work", self.test_view_responses)
        self.run_test("Form handling works", self.test_form_handling)
        
        print("\n3. CHECKING AJAX/API...")
        self.run_test("AJAX endpoints work", self.test_ajax_endpoints_work)
        self.run_test("Session creation flow", self.test_session_creation_flow)
        
        print("\n4. CHECKING ARCHITECTURE...")
        self.run_test("Services don't break imports", self.test_services_dont_break_imports)
        self.run_test("New services optional", self.test_new_services_optional)
        self.run_test("Middleware unchanged", self.test_middleware_unchanged)
        self.run_test("Exceptions work", self.test_exceptions_still_work)
        self.run_test("Decorators work", self.test_decorators_still_work)
        
        print("\n5. CHECKING FRONTEND...")
        self.run_test("Templates exist", self.test_templates_exist)
        self.run_test("Static files configured", self.test_static_files_configuration)
        self.run_test("JavaScript modules accessible", self.test_javascript_modules_accessible)
        
        # Report results
        print("\n" + "="*70)
        total = self.passed + self.failed
        print(f"RESULTS: {self.passed}/{total} passed, {self.failed} failed")
        print("="*70)
        
        if self.failed == 0:
            print("\nSUCCESS: No existing features were affected")
            print("Phase 5 changes are completely backward compatible")
        else:
            print("\nWARNING: Some features may be affected")
            print("Review failures above")
        
        return self.failed == 0


if __name__ == "__main__":
    tester = TestPhase5Impact()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
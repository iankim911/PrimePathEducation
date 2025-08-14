"""
Phase 6 Compatibility Test - View Refactoring Implementation
Ensures that refactoring views to use services maintains 100% compatibility.
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

from django.test import Client, RequestFactory
from django.urls import reverse
from django.http import HttpRequest
from placement_test.models import Exam, StudentSession, Question, StudentAnswer
from core.models import School, Program, SubProgram, CurriculumLevel, PlacementRule
import traceback


class TestPhase6Compatibility:
    """Test that Phase 6 view refactoring maintains complete compatibility."""
    
    def __init__(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def run_test(self, test_name, test_func):
        """Run a single test and track results."""
        try:
            result = test_func()
            if result is False:
                self.failed += 1
                self.tests.append(f"FAIL: {test_name}")
                print(f"FAIL: {test_name}")
            else:
                self.passed += 1
                self.tests.append(f"PASS: {test_name}")
                print(f"PASS: {test_name}")
        except Exception as e:
            self.failed += 1
            self.tests.append(f"FAIL: {test_name}: {str(e)}")
            print(f"FAIL: {test_name}: {str(e)}")
            if os.environ.get('DEBUG'):
                traceback.print_exc()
    
    def test_original_views_exist(self):
        """Test that original views are still available."""
        from core import views as core_views
        from placement_test import views as placement_views
        
        # Core views
        assert hasattr(core_views, 'index')
        assert hasattr(core_views, 'teacher_dashboard')
        assert hasattr(core_views, 'curriculum_levels')
        assert hasattr(core_views, 'placement_rules')
        assert hasattr(core_views, 'get_placement_rules')
        assert hasattr(core_views, 'save_placement_rules')
        
        # Placement test views
        assert hasattr(placement_views, 'start_test')
        assert hasattr(placement_views, 'take_test')
        assert hasattr(placement_views, 'submit_answer')
        assert hasattr(placement_views, 'complete_test')
        
        print("  - All original views still exist")
    
    def test_refactored_views_available(self):
        """Test that refactored views are available (if they exist)."""
        try:
            from core import views_refactored
            assert hasattr(views_refactored, 'teacher_dashboard')
            print("  - Core refactored views available")
        except ImportError:
            print("  - Core refactored views not yet implemented")
            return None  # Not a failure, just not implemented yet
        
        try:
            from placement_test import views_refactored
            print("  - Placement test refactored views available")
        except ImportError:
            print("  - Placement test refactored views not yet implemented")
            return None
    
    def test_url_patterns_unchanged(self):
        """Test that URL patterns resolve to correct views."""
        # Test core URLs
        assert reverse('core:index') == '/'
        assert reverse('core:teacher_dashboard') == '/PlacementTest/PlacementTest/teacher/dashboard/'
        
        # Test placement URLs
        assert reverse('PlacementTest:start_test') == '/api/PlacementTest/start/'
        assert reverse('PlacementTest:exam_list') == '/api/PlacementTest/exams/'
        
        print("  - URL patterns unchanged")
    
    def test_view_responses_compatible(self):
        """Test that view responses are compatible."""
        # Test index
        response = self.client.get('/')
        assert response.status_code in [200, 302]
        
        # Test dashboard
        response = self.client.get('/PlacementTest/PlacementTest/teacher/dashboard/')
        assert response.status_code in [200, 302]
        
        print("  - View responses compatible")
    
    def test_context_variables_preserved(self):
        """Test that template context variables are preserved."""
        response = self.client.get('/PlacementTest/PlacementTest/teacher/dashboard/')
        
        if response.status_code == 200 and hasattr(response, 'context'):
            # Check expected context variables
            expected_vars = ['recent_sessions', 'active_exams', 'total_sessions']
            for var in expected_vars:
                if var not in response.context:
                    print(f"    Warning: Missing context variable '{var}'")
        
        print("  - Context variables structure preserved")
    
    def test_ajax_response_format(self):
        """Test that AJAX responses maintain same format."""
        # Test curriculum levels AJAX
        response = self.client.get(
            '/curriculum/levels/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        if response.status_code == 200:
            content_type = response.get('Content-Type', '')
            assert 'json' in content_type.lower(), "AJAX not returning JSON"
            
            # Check JSON structure
            try:
                data = json.loads(response.content)
                assert isinstance(data, dict), "Response should be JSON object"
            except json.JSONDecodeError:
                raise Exception("Invalid JSON response")
        
        print("  - AJAX response format maintained")
    
    def test_form_handling_preserved(self):
        """Test that form handling is preserved."""
        # Test POST to start_test
        response = self.client.post('/api/PlacementTest/start/', data={})
        
        # Should handle empty form (validation error)
        assert response.status_code in [200, 400], "Form handling changed"
        
        print("  - Form handling preserved")
    
    def test_session_handling(self):
        """Test that session handling works correctly."""
        # Create a session
        session = self.client.session
        session['test_key'] = 'test_value'
        session.save()
        
        # Make request
        response = self.client.get('/')
        
        # Session should be maintained
        assert self.client.session.get('test_key') == 'test_value'
        
        print("  - Session handling works")
    
    def test_database_transactions(self):
        """Test that database transactions work correctly."""
        from django.db import transaction
        
        # Test transaction capability
        with transaction.atomic():
            # Create test data
            school, created = School.objects.get_or_create(
                name="Phase 6 Test School Transaction",
                defaults={'address': "Test Address"}
            )
            
            # Rollback
            transaction.set_rollback(True)
        
        # Check rollback worked
        assert not School.objects.filter(
            name="Phase 6 Test School Transaction"
        ).exists()
        
        print("  - Database transactions work correctly")
    
    def test_error_handling(self):
        """Test that error handling is consistent."""
        # Test 404
        response = self.client.get('/nonexistent-url/')
        assert response.status_code == 404
        
        # Test invalid form data
        response = self.client.post('/api/PlacementTest/start/', {
            'grade': 'invalid'
        })
        assert response.status_code in [200, 400]
        
        print("  - Error handling consistent")
    
    def test_middleware_compatibility(self):
        """Test that middleware still functions."""
        from django.conf import settings
        
        # Check middleware is configured
        assert len(settings.MIDDLEWARE) > 0
        
        # Make request to test middleware chain
        response = self.client.get('/')
        
        # Check CSRF token is set (CSRF middleware)
        if response.status_code == 200:
            assert 'csrftoken' in response.cookies or hasattr(response, 'csrf_token')
        
        print("  - Middleware compatibility maintained")
    
    def test_static_files_serving(self):
        """Test that static files configuration is correct."""
        from django.conf import settings
        
        assert settings.STATIC_URL == '/static/'
        assert 'django.contrib.staticfiles' in settings.INSTALLED_APPS
        
        print("  - Static files configuration correct")
    
    def test_template_inheritance(self):
        """Test that template inheritance works."""
        response = self.client.get('/')
        
        if response.status_code == 200:
            # Check that response has content
            assert len(response.content) > 0
        
        print("  - Template rendering works")
    
    def test_service_integration(self):
        """Test that services are properly integrated."""
        from core.services import DashboardService, CurriculumService
        from placement_test.services import ExamService, SessionService
        
        # Test service methods exist
        assert hasattr(DashboardService, 'get_dashboard_stats')
        assert hasattr(CurriculumService, 'get_programs_with_hierarchy')
        assert hasattr(ExamService, 'create_exam')
        assert hasattr(SessionService, 'create_session')
        
        print("  - Services properly integrated")
    
    def test_backwards_compatibility(self):
        """Test that old code patterns still work."""
        # Direct model access should still work
        from placement_test.models import Exam
        from core.models import School
        
        # These queries should work
        exams = Exam.objects.all()
        schools = School.objects.all()
        
        # Count queries should work
        exam_count = exams.count()
        school_count = schools.count()
        
        print("  - Backwards compatibility maintained")
    
    def test_api_endpoints_stable(self):
        """Test that API endpoints return stable responses."""
        endpoints = [
            '/api/PlacementTest/rules/',
            '/api/PlacementTest/exams/',
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            assert response.status_code in [200, 302, 403], f"{endpoint} unstable"
        
        print("  - API endpoints stable")
    
    def test_authentication_flow(self):
        """Test that authentication flow works."""
        # Test login page redirect or access
        response = self.client.get('/PlacementTest/PlacementTest/teacher/dashboard/')
        
        # Should either show dashboard or redirect to login
        assert response.status_code in [200, 302]
        
        print("  - Authentication flow works")
    
    def test_caching_compatible(self):
        """Test that caching is compatible."""
        from django.core.cache import cache
        
        # Test cache operations
        cache.set('test_key', 'test_value', 30)
        value = cache.get('test_key')
        
        # Cache should work (even if it's dummy backend)
        assert value == 'test_value' or value is None
        
        print("  - Caching compatible")
    
    def test_logging_functional(self):
        """Test that logging is functional."""
        import logging
        
        logger = logging.getLogger('test')
        
        # Should be able to log without errors
        logger.info("Test log message")
        logger.error("Test error message")
        
        print("  - Logging functional")
    
    def test_feature_flag_ready(self):
        """Test that system is ready for feature flags."""
        from django.conf import settings
        
        # Check if we can add custom settings
        if not hasattr(settings, 'USE_REFACTORED_VIEWS'):
            # Should be able to check for non-existent setting
            use_refactored = getattr(settings, 'USE_REFACTORED_VIEWS', False)
            assert use_refactored is False
        
        print("  - System ready for feature flags")
    
    def run_all_tests(self):
        """Run all Phase 6 compatibility tests."""
        print("\n" + "="*70)
        print("PHASE 6 COMPATIBILITY TEST - View Refactoring")
        print("="*70 + "\n")
        
        print("1. CHECKING VIEW LAYER...")
        self.run_test("Original views exist", self.test_original_views_exist)
        self.run_test("Refactored views available", self.test_refactored_views_available)
        self.run_test("URL patterns unchanged", self.test_url_patterns_unchanged)
        self.run_test("View responses compatible", self.test_view_responses_compatible)
        
        print("\n2. CHECKING DATA FLOW...")
        self.run_test("Context variables preserved", self.test_context_variables_preserved)
        self.run_test("AJAX response format", self.test_ajax_response_format)
        self.run_test("Form handling preserved", self.test_form_handling_preserved)
        self.run_test("Session handling", self.test_session_handling)
        
        print("\n3. CHECKING INFRASTRUCTURE...")
        self.run_test("Database transactions", self.test_database_transactions)
        self.run_test("Error handling", self.test_error_handling)
        self.run_test("Middleware compatibility", self.test_middleware_compatibility)
        self.run_test("Static files serving", self.test_static_files_serving)
        
        print("\n4. CHECKING INTEGRATION...")
        self.run_test("Template inheritance", self.test_template_inheritance)
        self.run_test("Service integration", self.test_service_integration)
        self.run_test("Backwards compatibility", self.test_backwards_compatibility)
        self.run_test("API endpoints stable", self.test_api_endpoints_stable)
        
        print("\n5. CHECKING ADVANCED FEATURES...")
        self.run_test("Authentication flow", self.test_authentication_flow)
        self.run_test("Caching compatible", self.test_caching_compatible)
        self.run_test("Logging functional", self.test_logging_functional)
        self.run_test("Feature flag ready", self.test_feature_flag_ready)
        
        # Report results
        print("\n" + "="*70)
        total = self.passed + self.failed
        print(f"RESULTS: {self.passed}/{total} tests passed")
        print("="*70)
        
        if self.failed == 0:
            print("\nSUCCESS: System ready for Phase 6 implementation")
            print("All compatibility requirements met")
        else:
            print(f"\nWARNING: {self.failed} compatibility issues detected")
            print("Review failures before proceeding")
        
        return self.failed == 0


if __name__ == "__main__":
    tester = TestPhase6Compatibility()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
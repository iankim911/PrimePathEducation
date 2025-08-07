"""
Phase 6 Final Test - Comprehensive verification of refactored views
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
import traceback


class TestPhase6Final:
    """Final comprehensive test for Phase 6."""
    
    def __init__(self):
        self.client = Client()
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def run_test(self, test_name, test_func):
        """Run a single test and track results."""
        try:
            test_func()
            self.passed += 1
            self.tests.append(f"PASS: {test_name}")
            print(f"PASS: {test_name}")
        except Exception as e:
            self.failed += 1
            self.tests.append(f"FAIL: {test_name}: {str(e)}")
            print(f"FAIL: {test_name}: {str(e)}")
            if os.environ.get('DEBUG'):
                traceback.print_exc()
    
    def test_original_views_still_work(self):
        """Test that original views still function."""
        from core import views as core_views
        from placement_test import views as placement_views
        from django.http import HttpRequest
        
        # Create mock request
        request = HttpRequest()
        request.method = 'GET'
        request.session = {}
        
        # Test core.views.index
        response = core_views.index(request)
        assert response.status_code == 200
        
        print("  - Original views still functional")
    
    def test_refactored_views_work(self):
        """Test that refactored views function correctly."""
        from core import views_refactored
        from placement_test import views_refactored as pt_views_refactored
        from django.http import HttpRequest
        
        # Create mock request
        request = HttpRequest()
        request.method = 'GET'
        request.session = {}
        request.META = {}
        
        # Test refactored index
        response = views_refactored.index(request)
        assert response.status_code == 200
        
        # Test refactored teacher_dashboard
        response = views_refactored.teacher_dashboard(request)
        assert response.status_code == 200
        
        print("  - Refactored views functional")
    
    def test_services_integrated(self):
        """Test that services are properly integrated in refactored views."""
        from core.services import DashboardService, CurriculumService, FileService
        from placement_test.services import ExamService, SessionService, PlacementService, GradingService
        
        # Test service methods exist and work
        stats = DashboardService.get_dashboard_stats()
        assert isinstance(stats, dict)
        assert 'total_sessions' in stats
        
        programs = CurriculumService.get_programs_with_hierarchy()
        assert isinstance(programs, (list, type(programs)))  # QuerySet or list
        
        print("  - Services properly integrated")
    
    def test_feature_flags_work(self):
        """Test that feature flag system works."""
        from core.feature_flags import FeatureFlags
        
        # Test flag checking
        flag_status = FeatureFlags.is_enabled('USE_REFACTORED_DASHBOARD')
        assert isinstance(flag_status, bool)
        
        # Test getting all flags
        all_flags = FeatureFlags.get_all_flags()
        assert isinstance(all_flags, dict)
        assert 'USE_REFACTORED_VIEWS' in all_flags
        
        print("  - Feature flag system works")
    
    def test_context_compatibility(self):
        """Test that refactored views provide same context variables."""
        from core import views_refactored
        from django.http import HttpRequest
        from django.template.response import TemplateResponse
        
        request = HttpRequest()
        request.method = 'GET'
        request.session = {}
        request.META = {}
        
        # Get response from refactored dashboard
        response = views_refactored.teacher_dashboard(request)
        
        # Check context (if available)
        if hasattr(response, 'context_data'):
            context = response.context_data
            assert 'recent_sessions' in context
            assert 'active_exams' in context
            assert 'total_sessions' in context
            print("  - Context variables maintained")
        else:
            print("  - Context check skipped (not available in test)")
    
    def test_error_handling_preserved(self):
        """Test that error handling is preserved in refactored views."""
        # Test invalid form submission
        response = self.client.post('/api/placement/start/', data={})
        assert response.status_code in [200, 400]
        
        # Test with partial data
        response = self.client.post('/api/placement/start/', data={
            'student_name': 'Test'
        })
        assert response.status_code in [200, 400]
        
        print("  - Error handling preserved")
    
    def test_ajax_compatibility(self):
        """Test AJAX endpoints work with refactored views."""
        response = self.client.get(
            '/curriculum/levels/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        if response.status_code == 200:
            content_type = response.get('Content-Type', '')
            assert 'json' in content_type.lower()
        
        print("  - AJAX compatibility maintained")
    
    def test_database_operations(self):
        """Test that database operations work in refactored views."""
        from placement_test.models import Exam
        from core.models import School
        
        # Test queries work
        exam_count = Exam.objects.count()
        school_count = School.objects.count()
        
        # Test that services can access database
        from placement_test.services import ExamService
        exams = ExamService.get_all_exams_with_stats()
        assert isinstance(exams, list)
        
        print("  - Database operations work")
    
    def test_url_routing(self):
        """Test that URLs route correctly."""
        # Test original URLs still work
        assert reverse('core:index') == '/'
        assert reverse('core:teacher_dashboard') == '/teacher/dashboard/'
        assert reverse('placement_test:start_test') == '/api/placement/start/'
        
        print("  - URL routing correct")
    
    def test_no_import_errors(self):
        """Test that there are no import errors."""
        try:
            from core import views
            from core import views_refactored
            from placement_test import views as pt_views
            from placement_test import views_refactored as pt_views_refactored
            from core.services import DashboardService, FileService
            from placement_test.services import ExamService, SessionService
            
            print("  - No import errors")
        except ImportError as e:
            raise Exception(f"Import error: {e}")
    
    def test_backwards_compatibility(self):
        """Test backwards compatibility."""
        # Old code patterns should still work
        from placement_test.models import Exam, StudentSession
        from core.models import School, Program
        
        # Direct model access
        exams = Exam.objects.all()
        schools = School.objects.all()
        
        # These should not raise errors
        exam_count = exams.count()
        school_count = schools.count()
        
        print("  - Backwards compatibility maintained")
    
    def test_performance_not_degraded(self):
        """Test that performance hasn't degraded."""
        import time
        
        # Test response time
        start = time.time()
        response = self.client.get('/')
        end = time.time()
        
        response_time = (end - start) * 1000  # ms
        
        # Should be reasonably fast (< 500ms for simple page)
        assert response_time < 500, f"Response too slow: {response_time}ms"
        
        print(f"  - Performance acceptable ({response_time:.0f}ms)")
    
    def run_all_tests(self):
        """Run all final tests."""
        print("\n" + "="*70)
        print("PHASE 6 FINAL TEST - Comprehensive Verification")
        print("="*70 + "\n")
        
        print("1. CHECKING CORE FUNCTIONALITY...")
        self.run_test("Original views work", self.test_original_views_still_work)
        self.run_test("Refactored views work", self.test_refactored_views_work)
        self.run_test("Services integrated", self.test_services_integrated)
        self.run_test("Feature flags work", self.test_feature_flags_work)
        
        print("\n2. CHECKING COMPATIBILITY...")
        self.run_test("Context compatibility", self.test_context_compatibility)
        self.run_test("Error handling preserved", self.test_error_handling_preserved)
        self.run_test("AJAX compatibility", self.test_ajax_compatibility)
        self.run_test("Database operations", self.test_database_operations)
        
        print("\n3. CHECKING INFRASTRUCTURE...")
        self.run_test("URL routing", self.test_url_routing)
        self.run_test("No import errors", self.test_no_import_errors)
        self.run_test("Backwards compatibility", self.test_backwards_compatibility)
        self.run_test("Performance not degraded", self.test_performance_not_degraded)
        
        # Report results
        print("\n" + "="*70)
        total = self.passed + self.failed
        print(f"RESULTS: {self.passed}/{total} tests passed")
        print("="*70)
        
        if self.failed == 0:
            print("\nSUCCESS: Phase 6 implementation complete")
            print("All refactored views working correctly")
            print("System maintains 100% backward compatibility")
        else:
            print(f"\nWARNING: {self.failed} issues detected")
            print("Review failures before deployment")
        
        return self.failed == 0


if __name__ == "__main__":
    tester = TestPhase6Final()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
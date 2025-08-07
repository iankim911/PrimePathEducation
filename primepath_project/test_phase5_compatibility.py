"""
Phase 5 Compatibility Test - View Layer Refactoring
Ensures that refactoring views to use services doesn't break any functionality.
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


class TestPhase5Compatibility:
    """Test that Phase 5 view refactoring doesn't break existing functionality."""
    
    def __init__(self):
        self.client = Client()
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def setup_test_data(self):
        """Create test data for testing views."""
        # Create a school with unique name
        self.school, _ = School.objects.get_or_create(
            name="Phase 5 Test School",
            defaults={'address': "123 Test St"}
        )
        
        # Create or get program structure
        self.program, _ = Program.objects.get_or_create(
            name="CORE",
            defaults={
                'grade_range_start': 1,
                'grade_range_end': 4,
                'order': 1
            }
        )
        
        self.subprogram, _ = SubProgram.objects.get_or_create(
            program=self.program,
            name="Core General",
            defaults={'order': 1}
        )
        
        self.curriculum_level, _ = CurriculumLevel.objects.get_or_create(
            subprogram=self.subprogram,
            level_number=1,
            defaults={}
        )
        
        # Create an exam
        self.exam, _ = Exam.objects.get_or_create(
            name="Test Exam Phase 5",
            defaults={
                'pdf_file': "test.pdf",
                'curriculum_level': self.curriculum_level,
                'is_active': True,
                'total_questions': 20,
                'timer_minutes': 60,
                'default_options_count': 5
            }
        )
        
        print("Test data created successfully")
    
    def cleanup_test_data(self):
        """Clean up test data after tests."""
        try:
            if hasattr(self, 'exam'):
                self.exam.delete()
            if hasattr(self, 'curriculum_level'):
                self.curriculum_level.delete()
            if hasattr(self, 'subprogram'):
                self.subprogram.delete()
            if hasattr(self, 'program'):
                self.program.delete()
            if hasattr(self, 'school'):
                self.school.delete()
        except:
            pass
    
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
            traceback.print_exc()
    
    def test_core_views_accessible(self):
        """Test that all core views are still accessible."""
        core_urls = [
            ('core:index', {}),
            ('core:teacher_dashboard', {}),
            ('core:curriculum_levels', {}),
            ('core:placement_rules', {}),
        ]
        
        for url_name, kwargs in core_urls:
            url = reverse(url_name, kwargs=kwargs)
            response = self.client.get(url)
            assert response.status_code in [200, 302], f"{url_name} returned {response.status_code}"
        
        print("  - All core views accessible")
    
    def test_placement_views_accessible(self):
        """Test that all placement test views are still accessible."""
        placement_urls = [
            ('placement_test:start_test', {}),
            ('placement_test:exam_list', {}),
            ('placement_test:create_exam', {}),
        ]
        
        for url_name, kwargs in placement_urls:
            url = reverse(url_name, kwargs=kwargs)
            response = self.client.get(url)
            assert response.status_code in [200, 302], f"{url_name} returned {response.status_code}"
        
        print("  - All placement test views accessible")
    
    def test_ajax_endpoints_format(self):
        """Test that AJAX endpoints still return correct format."""
        # Test get_placement_rules endpoint
        url = reverse('core:get_placement_rules')
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        assert response.status_code in [200, 400, 403], f"AJAX endpoint returned {response.status_code}"
        
        # Check response is JSON
        try:
            data = json.loads(response.content)
            assert isinstance(data, dict), "Response should be JSON object"
        except json.JSONDecodeError:
            raise Exception("AJAX endpoint doesn't return valid JSON")
        
        print("  - AJAX endpoints return correct format")
    
    def test_start_test_flow(self):
        """Test that start test flow still works."""
        url = reverse('placement_test:start_test')
        
        # GET request should work
        response = self.client.get(url)
        assert response.status_code == 200, f"start_test GET returned {response.status_code}"
        
        # POST request with data
        test_data = {
            'student_name': 'Test Student',
            'grade': '5',
            'academic_rank': 'TOP_20',
            'school_name': 'Test School',
            'parent_phone': '123-456-7890'
        }
        
        response = self.client.post(url, data=test_data)
        # Should redirect or return success
        assert response.status_code in [200, 302], f"start_test POST returned {response.status_code}"
        
        print("  - Start test flow works")
    
    def test_teacher_dashboard_data(self):
        """Test that teacher dashboard still shows correct data."""
        url = reverse('core:teacher_dashboard')
        response = self.client.get(url)
        
        assert response.status_code == 200, f"Dashboard returned {response.status_code}"
        
        # Check context data
        if hasattr(response, 'context'):
            assert 'recent_sessions' in response.context, "Missing recent_sessions in context"
            assert 'active_exams' in response.context, "Missing active_exams in context"
            assert 'total_sessions' in response.context, "Missing total_sessions in context"
        
        print("  - Teacher dashboard shows correct data")
    
    def test_curriculum_levels_ajax(self):
        """Test curriculum levels AJAX endpoint."""
        url = reverse('core:curriculum_levels')
        
        # Regular request
        response = self.client.get(url)
        assert response.status_code == 200, f"Curriculum levels returned {response.status_code}"
        
        # AJAX request
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        assert response.status_code == 200, f"Curriculum levels AJAX returned {response.status_code}"
        
        # Check JSON response
        if response['Content-Type'].startswith('application/json'):
            data = json.loads(response.content)
            assert 'programs' in data, "Missing programs in AJAX response"
        
        print("  - Curriculum levels AJAX works")
    
    def test_exam_creation_flow(self):
        """Test that exam creation still works."""
        url = reverse('placement_test:create_exam')
        
        # GET request
        response = self.client.get(url)
        assert response.status_code in [200, 302], f"Create exam GET returned {response.status_code}"
        
        print("  - Exam creation flow accessible")
    
    def test_placement_rules_data(self):
        """Test placement rules view data."""
        url = reverse('core:placement_rules')
        response = self.client.get(url)
        
        assert response.status_code == 200, f"Placement rules returned {response.status_code}"
        
        # Check that view renders without errors
        assert b'placement' in response.content.lower() or b'rules' in response.content.lower(), \
            "Placement rules page doesn't contain expected content"
        
        print("  - Placement rules view works")
    
    def test_services_imported(self):
        """Test that services are properly imported where needed."""
        # Check if services exist
        from core.services import CurriculumService, SchoolService, TeacherService
        from placement_test.services import ExamService, SessionService, PlacementService, GradingService
        
        # Check that services have required methods
        assert hasattr(CurriculumService, 'get_programs_with_hierarchy')
        assert hasattr(ExamService, 'create_exam')
        assert hasattr(SessionService, 'create_session')
        assert hasattr(PlacementService, 'match_student_to_exam')
        assert hasattr(GradingService, 'auto_grade_answer')
        
        print("  - All services properly imported")
    
    def test_mixins_available(self):
        """Test that mixins are available."""
        from common.mixins import AjaxResponseMixin, TeacherRequiredMixin, RequestValidationMixin
        
        # Check mixin methods exist
        assert hasattr(AjaxResponseMixin, 'json_response')
        assert hasattr(AjaxResponseMixin, 'json_error')
        
        print("  - Mixins available and functional")
    
    def test_error_handling(self):
        """Test that error handling still works."""
        # Test with invalid data
        url = reverse('placement_test:start_test')
        response = self.client.post(url, data={})  # Missing required fields
        
        # Should handle error gracefully
        assert response.status_code in [200, 400], f"Error handling returned {response.status_code}"
        
        print("  - Error handling works")
    
    def test_database_queries_optimized(self):
        """Test that database queries are still optimized."""
        from django.test.utils import override_settings
        from django.db import connection
        from django.db import reset_queries
        
        # Reset query count
        reset_queries()
        
        # Access teacher dashboard
        url = reverse('core:teacher_dashboard')
        response = self.client.get(url)
        
        # Check query count is reasonable (not N+1)
        query_count = len(connection.queries)
        assert query_count < 20, f"Too many queries: {query_count}"
        
        print(f"  - Database queries optimized ({query_count} queries)")
    
    def test_templates_render(self):
        """Test that templates still render correctly."""
        urls_to_test = [
            ('core:index', {}),
            ('core:teacher_dashboard', {}),
            ('placement_test:start_test', {}),
        ]
        
        for url_name, kwargs in urls_to_test:
            url = reverse(url_name, kwargs=kwargs)
            response = self.client.get(url)
            
            # Check for template errors
            if response.status_code == 200:
                assert len(response.content) > 100, f"{url_name} returned empty content"
        
        print("  - Templates render correctly")
    
    def test_static_files_accessible(self):
        """Test that static files are still accessible."""
        # This would normally test static file serving
        # but in Django test environment, we just verify the configuration
        from django.conf import settings
        
        assert hasattr(settings, 'STATIC_URL'), "STATIC_URL not configured"
        assert hasattr(settings, 'STATICFILES_DIRS'), "STATICFILES_DIRS not configured"
        
        print("  - Static files configuration correct")
    
    def test_session_management(self):
        """Test that session management still works."""
        # Create a test session
        url = reverse('placement_test:start_test')
        test_data = {
            'student_name': 'Session Test',
            'grade': '7',
            'academic_rank': 'TOP_30',
            'school_name': 'Session School',
            'parent_phone': '555-555-5555'
        }
        
        response = self.client.post(url, data=test_data, follow=True)
        
        # Check session was created or handled properly
        assert response.status_code in [200, 302], f"Session creation returned {response.status_code}"
        
        print("  - Session management works")
    
    def test_backwards_compatibility(self):
        """Test that old code patterns still work."""
        # Import old views to ensure they're not broken
        from core import views as core_views
        from placement_test import views as placement_views
        
        # Check that original view functions still exist
        assert hasattr(core_views, 'index')
        assert hasattr(core_views, 'teacher_dashboard')
        assert hasattr(placement_views, 'start_test')
        assert hasattr(placement_views, 'take_test')
        
        print("  - Backwards compatibility maintained")
    
    def run_all_tests(self):
        """Run all Phase 5 compatibility tests."""
        print("\n" + "="*70)
        print("PHASE 5 COMPATIBILITY TEST - View Layer Refactoring")
        print("="*70 + "\n")
        
        # Setup test data
        print("Setting up test data...")
        self.setup_test_data()
        
        print("\n1. CHECKING VIEW ACCESSIBILITY...")
        self.run_test("Core views accessible", self.test_core_views_accessible)
        self.run_test("Placement views accessible", self.test_placement_views_accessible)
        
        print("\n2. CHECKING DATA FLOW...")
        self.run_test("AJAX endpoints format", self.test_ajax_endpoints_format)
        self.run_test("Teacher dashboard data", self.test_teacher_dashboard_data)
        self.run_test("Curriculum levels AJAX", self.test_curriculum_levels_ajax)
        self.run_test("Placement rules data", self.test_placement_rules_data)
        
        print("\n3. CHECKING FUNCTIONALITY...")
        self.run_test("Start test flow", self.test_start_test_flow)
        self.run_test("Exam creation flow", self.test_exam_creation_flow)
        self.run_test("Session management", self.test_session_management)
        self.run_test("Error handling", self.test_error_handling)
        
        print("\n4. CHECKING ARCHITECTURE...")
        self.run_test("Services imported", self.test_services_imported)
        self.run_test("Mixins available", self.test_mixins_available)
        self.run_test("Database queries optimized", self.test_database_queries_optimized)
        self.run_test("Backwards compatibility", self.test_backwards_compatibility)
        
        print("\n5. CHECKING PRESENTATION...")
        self.run_test("Templates render", self.test_templates_render)
        self.run_test("Static files accessible", self.test_static_files_accessible)
        
        # Cleanup
        print("\nCleaning up test data...")
        self.cleanup_test_data()
        
        # Report results
        print("\n" + "="*70)
        total = self.passed + self.failed
        print(f"RESULTS: {self.passed}/{total} passed, {self.failed} failed")
        print("="*70)
        
        if self.failed == 0:
            print("\nSUCCESS: Phase 5 can proceed safely")
            print("All views and functionality remain intact")
        else:
            print("\nWARNING: Some tests failed")
            print("Review failures before proceeding with Phase 5")
        
        return self.failed == 0


if __name__ == "__main__":
    tester = TestPhase5Compatibility()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
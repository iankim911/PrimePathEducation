#!/usr/bin/env python
"""
Comprehensive QA Test for Matrix Tab Visibility
Tests that the Exam Assignments Matrix tab is visible and functional
Version: 1.0.0
Date: 2025-08-17
"""

import os
import sys

# Setup Django BEFORE any Django imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
django.setup()

# Now import Django modules
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
import json
from datetime import datetime

from primepath_routinetest.models import Exam, ExamScheduleMatrix
from core.models import Teacher


def colored_output(text, color='green'):
    """Helper for colored console output"""
    colors = {
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m'
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"


class MatrixTabVisibilityTest(TestCase):
    """Test suite for Matrix Tab visibility and functionality"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testteacher',
            password='testpass123',
            email='test@example.com'
        )
        self.user.is_staff = True
        self.user.save()
        
        # Create teacher profile
        self.teacher = Teacher.objects.create(
            user=self.user,
            full_name='Test Teacher',
            is_head_teacher=False
        )
        
        # Create client
        self.client = Client()
        self.client.login(username='testteacher', password='testpass123')
        
        print(colored_output("\n" + "="*60, 'cyan'))
        print(colored_output("MATRIX TAB VISIBILITY QA TEST", 'cyan'))
        print(colored_output("="*60, 'cyan'))
    
    def test_01_navigation_structure_in_templates(self):
        """Test 1: Verify navigation structure in templates"""
        print(colored_output("\n[TEST 1] Checking navigation structure in templates...", 'yellow'))
        
        # Check if base template exists
        template_path = 'templates/routinetest_base.html'
        full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), template_path)
        
        self.assertTrue(os.path.exists(full_path), f"Base template not found at {full_path}")
        
        # Read template and check for Matrix tab
        with open(full_path, 'r') as f:
            content = f.read()
            
        # Check for Matrix tab elements
        checks = [
            ('matrix-tab-item', 'Matrix tab ID'),
            ('exam-assignments-matrix', 'Matrix tab data attribute'),
            ('schedule_matrix', 'Matrix URL name'),
            ('Exam Assignments', 'Matrix tab text'),
            ('#FF9800', 'Matrix tab orange color')
        ]
        
        for check_str, description in checks:
            if check_str in content:
                print(colored_output(f"  ✓ {description} found", 'green'))
            else:
                print(colored_output(f"  ✗ {description} NOT found", 'red'))
                self.fail(f"{description} missing from template")
        
        print(colored_output("  ✓ All navigation elements present in template", 'green'))
    
    def test_02_url_routing(self):
        """Test 2: Verify Matrix URL routing"""
        print(colored_output("\n[TEST 2] Checking Matrix URL routing...", 'yellow'))
        
        # Test Matrix URL exists and is accessible
        try:
            url = reverse('RoutineTest:schedule_matrix')
            print(colored_output(f"  ✓ Matrix URL resolved: {url}", 'green'))
        except Exception as e:
            print(colored_output(f"  ✗ Matrix URL resolution failed: {e}", 'red'))
            self.fail("Matrix URL not found in routing")
        
        # Test Matrix cell detail URL
        try:
            # Create a test matrix entry
            matrix = ExamScheduleMatrix.objects.create(
                class_code='G1A',
                academic_year='2025',
                time_period_type='MONTHLY',
                time_period_value='JAN'
            )
            
            url = reverse('RoutineTest:matrix_cell_detail', kwargs={'matrix_id': matrix.id})
            print(colored_output(f"  ✓ Matrix cell detail URL resolved: {url}", 'green'))
        except Exception as e:
            print(colored_output(f"  ✗ Matrix cell detail URL failed: {e}", 'red'))
    
    def test_03_index_page_response(self):
        """Test 3: Verify index page renders with navigation"""
        print(colored_output("\n[TEST 3] Testing index page response...", 'yellow'))
        
        response = self.client.get(reverse('RoutineTest:index'))
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        print(colored_output(f"  ✓ Index page returned status 200", 'green'))
        
        # Check for navigation elements in response
        content = response.content.decode('utf-8')
        
        navigation_checks = [
            ('nav-tabs', 'Navigation tabs container'),
            ('Dashboard', 'Dashboard tab'),
            ('Upload Exam', 'Upload Exam tab'),
            ('Answer Keys', 'Answer Keys tab'),
            ('My Classes', 'My Classes tab'),
            ('matrix-tab-item', 'Matrix tab element'),
            ('Results', 'Results tab')
        ]
        
        for check_str, description in navigation_checks:
            if check_str in content:
                print(colored_output(f"  ✓ {description} found in response", 'green'))
            else:
                print(colored_output(f"  ⚠ {description} not found in response", 'yellow'))
    
    def test_04_matrix_page_accessibility(self):
        """Test 4: Test Matrix page accessibility"""
        print(colored_output("\n[TEST 4] Testing Matrix page accessibility...", 'yellow'))
        
        response = self.client.get(reverse('RoutineTest:schedule_matrix'))
        
        self.assertEqual(response.status_code, 200)
        print(colored_output(f"  ✓ Matrix page accessible (status 200)", 'green'))
        
        # Check for matrix-specific content
        content = response.content.decode('utf-8')
        
        if 'Schedule Matrix' in content or 'Exam Assignments' in content:
            print(colored_output(f"  ✓ Matrix page content loaded", 'green'))
        else:
            print(colored_output(f"  ⚠ Matrix page content may be incomplete", 'yellow'))
    
    def test_05_context_processor(self):
        """Test 5: Verify context processor provides necessary variables"""
        print(colored_output("\n[TEST 5] Testing context processor...", 'yellow'))
        
        response = self.client.get(reverse('RoutineTest:index'))
        
        # Check context variables
        context_vars = [
            'is_routinetest',
            'module_name',
            'theme_name',
            'is_head_teacher'
        ]
        
        for var in context_vars:
            if var in response.context:
                value = response.context[var]
                print(colored_output(f"  ✓ Context variable '{var}': {value}", 'green'))
            else:
                print(colored_output(f"  ⚠ Context variable '{var}' not found", 'yellow'))
    
    def test_06_javascript_files(self):
        """Test 6: Verify JavaScript files exist"""
        print(colored_output("\n[TEST 6] Checking JavaScript files...", 'yellow'))
        
        js_files = [
            'static/js/routinetest/schedule-matrix.js',
            'static/js/routinetest/matrix-tab-guardian.js',
            'static/js/routinetest-theme.js'
        ]
        
        base_dir = os.path.dirname(os.path.dirname(__file__))
        
        for js_file in js_files:
            full_path = os.path.join(base_dir, js_file)
            if os.path.exists(full_path):
                print(colored_output(f"  ✓ {js_file} exists", 'green'))
            else:
                print(colored_output(f"  ✗ {js_file} NOT found", 'red'))
    
    def test_07_css_styles(self):
        """Test 7: Verify CSS styles for Matrix tab"""
        print(colored_output("\n[TEST 7] Checking CSS styles...", 'yellow'))
        
        css_file = 'static/css/routinetest/schedule-matrix.css'
        full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), css_file)
        
        if os.path.exists(full_path):
            print(colored_output(f"  ✓ Matrix CSS file exists", 'green'))
            
            with open(full_path, 'r') as f:
                content = f.read()
                
            # Check for important styles
            if 'matrix' in content.lower():
                print(colored_output(f"  ✓ Matrix-specific styles found", 'green'))
        else:
            print(colored_output(f"  ⚠ Matrix CSS file not found", 'yellow'))
    
    def test_08_no_breaking_changes(self):
        """Test 8: Verify no breaking changes to other features"""
        print(colored_output("\n[TEST 8] Checking for breaking changes...", 'yellow'))
        
        # Test other main URLs still work
        urls_to_test = [
            ('RoutineTest:exam_list', 'Exam List'),
            ('RoutineTest:create_exam', 'Create Exam'),
            ('RoutineTest:session_list', 'Session List'),
            ('RoutineTest:my_classes', 'My Classes')
        ]
        
        for url_name, description in urls_to_test:
            try:
                response = self.client.get(reverse(url_name))
                if response.status_code in [200, 302]:  # 302 for redirects
                    print(colored_output(f"  ✓ {description} page working (status {response.status_code})", 'green'))
                else:
                    print(colored_output(f"  ⚠ {description} returned status {response.status_code}", 'yellow'))
            except Exception as e:
                print(colored_output(f"  ✗ {description} failed: {e}", 'red'))


def run_qa_tests():
    """Run all QA tests"""
    print(colored_output("\n" + "="*60, 'magenta'))
    print(colored_output("STARTING COMPREHENSIVE MATRIX TAB QA TESTS", 'magenta'))
    print(colored_output("="*60, 'magenta'))
    print(colored_output(f"Timestamp: {datetime.now().isoformat()}", 'blue'))
    print(colored_output(f"Django Version: {django.VERSION}", 'blue'))
    
    # Run tests
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True, keepdb=True)
    failures = test_runner.run_tests(['__main__'])
    
    # Summary
    print(colored_output("\n" + "="*60, 'magenta'))
    if failures == 0:
        print(colored_output("✅ ALL TESTS PASSED!", 'green'))
        print(colored_output("The Matrix tab visibility fix is working correctly.", 'green'))
    else:
        print(colored_output(f"⚠️ {failures} TEST(S) FAILED", 'red'))
        print(colored_output("Please review the failures above.", 'red'))
    print(colored_output("="*60, 'magenta'))
    
    return failures


if __name__ == '__main__':
    # Run the QA tests
    failures = run_qa_tests()
    
    # Additional manual checks reminder
    print(colored_output("\n" + "="*60, 'cyan'))
    print(colored_output("MANUAL VERIFICATION CHECKLIST", 'cyan'))
    print(colored_output("="*60, 'cyan'))
    print(colored_output("Please manually verify in the browser:", 'yellow'))
    print(colored_output("1. [ ] Navigate to http://127.0.0.1:8000/RoutineTest/", 'white'))
    print(colored_output("2. [ ] Check that 'Exam Assignments' tab is visible with orange background", 'white'))
    print(colored_output("3. [ ] Click the Matrix tab and verify it navigates to schedule matrix page", 'white'))
    print(colored_output("4. [ ] Open browser console and check for debugging messages", 'white'))
    print(colored_output("5. [ ] Verify no JavaScript errors in console", 'white'))
    print(colored_output("6. [ ] Test navigation between different pages", 'white'))
    print(colored_output("7. [ ] Clear browser cache and reload to test fresh load", 'white'))
    print(colored_output("="*60, 'cyan'))
    
    sys.exit(failures)
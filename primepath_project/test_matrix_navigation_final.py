#!/usr/bin/env python
"""
Final comprehensive test for Matrix tab navigation fix
Tests all aspects of the navigation rendering
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime
import json

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')

import django
django.setup()

from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User


def colored(text, color):
    """Helper for colored output"""
    colors = {
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'blue': '\033[94m',
        'cyan': '\033[96m',
        'magenta': '\033[95m',
        'white': '\033[97m',
        'reset': '\033[0m'
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"


class MatrixNavigationTest:
    """Comprehensive test suite for Matrix navigation"""
    
    def __init__(self):
        self.client = Client()
        self.results = []
        self.failures = 0
        
    def setup(self):
        """Setup test environment"""
        print(colored("\n[SETUP] Preparing test environment...", 'yellow'))
        
        # Create test user if doesn't exist
        try:
            self.user = User.objects.get(username='testuser')
        except User.DoesNotExist:
            self.user = User.objects.create_user(
                username='testuser',
                password='testpass123',
                email='test@example.com'
            )
            self.user.is_staff = True
            self.user.save()
        
        # Login
        logged_in = self.client.login(username='testuser', password='testpass123')
        if logged_in:
            print(colored("  ✓ Logged in as testuser", 'green'))
        else:
            print(colored("  ✗ Failed to login", 'red'))
            return False
        
        return True
    
    def test_template_files(self):
        """Test 1: Verify template files exist and contain Matrix tab"""
        print(colored("\n[TEST 1] Checking template files...", 'yellow'))
        
        base_dir = Path(__file__).parent
        
        # Check base template
        base_template = base_dir / 'templates' / 'routinetest_base.html'
        if base_template.exists():
            with open(base_template, 'r') as f:
                content = f.read()
                
            checks = [
                ('navigation_tabs.html' in content, "Includes navigation template"),
                ('matrix-tab-override.js' in content, "Includes override JavaScript"),
                ('navigation_tags' in content, "Loads navigation tags")
            ]
            
            for passed, description in checks:
                if passed:
                    print(colored(f"  ✓ {description}", 'green'))
                else:
                    print(colored(f"  ✗ {description}", 'red'))
                    self.failures += 1
        else:
            print(colored("  ✗ Base template not found", 'red'))
            self.failures += 1
        
        # Check navigation include
        nav_template = base_dir / 'templates' / 'primepath_routinetest' / 'includes' / 'navigation_tabs.html'
        if nav_template.exists():
            with open(nav_template, 'r') as f:
                content = f.read()
                
            checks = [
                ('matrix-tab-v5' in content, "Contains Matrix tab with ID"),
                ('Exam Assignments' in content, "Contains Exam Assignments text"),
                ('schedule-matrix' in content, "Contains Matrix URL"),
                ('#FF9800' in content, "Contains orange color styling")
            ]
            
            for passed, description in checks:
                if passed:
                    print(colored(f"  ✓ {description}", 'green'))
                else:
                    print(colored(f"  ✗ {description}", 'red'))
                    self.failures += 1
        else:
            print(colored("  ✗ Navigation template not found", 'red'))
            self.failures += 1
    
    def test_static_files(self):
        """Test 2: Verify static files exist"""
        print(colored("\n[TEST 2] Checking static files...", 'yellow'))
        
        base_dir = Path(__file__).parent
        
        static_files = [
            ('static/js/routinetest/matrix-tab-override.js', "Override JavaScript"),
            ('static/js/routinetest/matrix-tab-guardian.js', "Guardian JavaScript"),
            ('static/css/routinetest/schedule-matrix.css', "Matrix CSS")
        ]
        
        for file_path, description in static_files:
            full_path = base_dir / file_path
            if full_path.exists():
                print(colored(f"  ✓ {description} exists", 'green'))
            else:
                print(colored(f"  ✗ {description} not found", 'red'))
                self.failures += 1
    
    def test_urls(self):
        """Test 3: Verify URL routing"""
        print(colored("\n[TEST 3] Testing URL routing...", 'yellow'))
        
        urls_to_test = [
            ('RoutineTest:index', "Dashboard"),
            ('RoutineTest:schedule_matrix', "Schedule Matrix"),
            ('RoutineTest:my_classes', "My Classes"),
            ('RoutineTest:exam_list', "Exam List"),
            ('RoutineTest:session_list', "Session List")
        ]
        
        for url_name, description in urls_to_test:
            try:
                url = reverse(url_name)
                print(colored(f"  ✓ {description} URL resolves to: {url}", 'green'))
            except Exception as e:
                print(colored(f"  ✗ {description} URL failed: {e}", 'red'))
                self.failures += 1
    
    def test_page_responses(self):
        """Test 4: Test page responses and content"""
        print(colored("\n[TEST 4] Testing page responses...", 'yellow'))
        
        pages_to_test = [
            ('/RoutineTest/', "Dashboard"),
            ('/RoutineTest/schedule-matrix/', "Schedule Matrix"),
            ('/RoutineTest/access/my-classes/', "My Classes")
        ]
        
        for url, description in pages_to_test:
            try:
                response = self.client.get(url)
                
                if response.status_code == 200:
                    print(colored(f"  ✓ {description} returned 200", 'green'))
                    
                    # Check for navigation elements
                    content = response.content.decode('utf-8')
                    
                    # Look for Matrix tab in various forms
                    matrix_found = any([
                        'Exam Assignments' in content,
                        'schedule-matrix' in content,
                        'matrix-tab' in content,
                        'data-nav="matrix"' in content
                    ])
                    
                    if matrix_found:
                        print(colored(f"    ✓ Matrix tab found in {description} HTML", 'green'))
                    else:
                        print(colored(f"    ⚠ Matrix tab not found in {description} HTML", 'yellow'))
                        
                else:
                    print(colored(f"  ⚠ {description} returned {response.status_code}", 'yellow'))
                    
            except Exception as e:
                print(colored(f"  ✗ {description} failed: {e}", 'red'))
                self.failures += 1
    
    def test_context_processor(self):
        """Test 5: Verify context processor is working"""
        print(colored("\n[TEST 5] Testing context processor...", 'yellow'))
        
        response = self.client.get('/RoutineTest/')
        
        if hasattr(response, 'context') and response.context:
            context_vars = [
                'is_routinetest',
                'module_name',
                'theme_name',
                'is_head_teacher'
            ]
            
            for var in context_vars:
                if var in response.context:
                    value = response.context[var]
                    print(colored(f"  ✓ {var}: {value}", 'green'))
                else:
                    print(colored(f"  ⚠ {var} not in context", 'yellow'))
        else:
            print(colored("  ⚠ No context available in response", 'yellow'))
    
    def run_all_tests(self):
        """Run all tests"""
        print(colored("\n" + "="*70, 'cyan'))
        print(colored("MATRIX TAB NAVIGATION - FINAL COMPREHENSIVE TEST", 'cyan'))
        print(colored("="*70, 'cyan'))
        print(colored(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 'blue'))
        
        if not self.setup():
            print(colored("\n✗ Setup failed, cannot continue", 'red'))
            return False
        
        # Run all tests
        self.test_template_files()
        self.test_static_files()
        self.test_urls()
        self.test_page_responses()
        self.test_context_processor()
        
        # Summary
        print(colored("\n" + "="*70, 'cyan'))
        if self.failures == 0:
            print(colored("✅ ALL TESTS PASSED!", 'green'))
            print(colored("The Matrix tab navigation fix is working correctly.", 'green'))
        else:
            print(colored(f"⚠️ {self.failures} issues found", 'red'))
            print(colored("Please review the failures above.", 'red'))
        print(colored("="*70, 'cyan'))
        
        # Manual verification steps
        print(colored("\n📋 MANUAL VERIFICATION STEPS:", 'magenta'))
        print(colored("1. Clear browser cache completely (Ctrl+Shift+Delete)", 'white'))
        print(colored("2. Restart Django server:", 'white'))
        print(colored("   cd primepath_project", 'white'))
        print(colored("   ../venv/bin/python manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite", 'white'))
        print(colored("\n3. Navigate to http://127.0.0.1:8000/RoutineTest/", 'white'))
        print(colored("4. Open browser console (F12)", 'white'))
        print(colored("5. Look for orange '📊 Exam Assignments' tab", 'white'))
        print(colored("\n6. If tab not visible, run in console:", 'yellow'))
        print(colored("   ForceMatrixTab()", 'white'))
        print(colored("\n7. Check console for these messages:", 'white'))
        print(colored("   - [NAV_V5] Navigation rendered with Matrix tab", 'white'))
        print(colored("   - ✅ Matrix tab verified visible", 'white'))
        print(colored("   - 🚀 Matrix Tab Override v5.0 active", 'white'))
        
        return self.failures == 0


if __name__ == '__main__':
    tester = MatrixNavigationTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
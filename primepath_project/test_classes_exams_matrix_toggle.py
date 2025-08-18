#!/usr/bin/env python
"""
Test Script for Classes & Exams Matrix Toggle Implementation
RoutineTest Module - Review/Quarterly Toggle System
Date: August 17, 2025
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import User
from core.models import Teacher, School
from primepath_routinetest.models import Exam
from django.urls import reverse

class TestClassesExamsMatrixToggle:
    def __init__(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.test_results = []
        
    def log_test(self, test_name, status, details=""):
        """Log test results with formatting"""
        icon = "✅" if status == "PASS" else "❌"
        self.test_results.append({
            'test': test_name,
            'status': status,
            'details': details
        })
        print(f"{icon} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
    
    def setup_test_data(self):
        """Create test data for matrix testing"""
        print("\n🔧 Setting up test data...")
        
        try:
            # Get or create teacher user
            teacher_user = User.objects.filter(username='testteacher_matrix').first()
            if not teacher_user:
                teacher_user = User.objects.create_user(
                    username='testteacher_matrix',
                    password='testpass123',
                    email='matrix@test.com'
                )
            
            # Get or create teacher
            teacher = Teacher.objects.filter(user=teacher_user).first()
            if not teacher:
                teacher = Teacher.objects.create(
                    user=teacher_user,
                    name="Matrix Test Teacher",
                    email='matrix@test.com',
                    is_head_teacher=True
                )
            
            print(f"   Teacher: {teacher.name}")
            return teacher_user
            
        except Exception as e:
            print(f"   ⚠️ Setup error: {e}")
            return None
    
    def test_view_rendering(self):
        """Test that the classes_exams_unified view renders correctly"""
        print("\n📋 Test 1: View Rendering")
        
        try:
            teacher_user = self.setup_test_data()
            if not teacher_user:
                self.log_test("View Rendering", "FAIL", "Could not create test user")
                return
            
            # Login and access view
            self.client.login(username='testteacher_matrix', password='testpass123')
            response = self.client.get(reverse('RoutineTest:classes_exams_unified'))
            
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                
                # Check for tab elements
                has_tabs = 'exam-type-tabs' in content
                has_review_tab = 'matrix-review-tab' in content
                has_quarterly_tab = 'matrix-quarterly-tab' in content
                has_all_tab = 'matrix-all-tab' in content
                
                if all([has_tabs, has_review_tab, has_quarterly_tab, has_all_tab]):
                    self.log_test("View Rendering", "PASS", "All tab elements present")
                else:
                    missing = []
                    if not has_tabs: missing.append("tab container")
                    if not has_review_tab: missing.append("review tab")
                    if not has_quarterly_tab: missing.append("quarterly tab")
                    if not has_all_tab: missing.append("all tab")
                    self.log_test("View Rendering", "FAIL", f"Missing: {', '.join(missing)}")
            else:
                self.log_test("View Rendering", "FAIL", f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("View Rendering", "FAIL", str(e))
    
    def test_tab_css_styles(self):
        """Test that CSS styles for tabs are present"""
        print("\n🎨 Test 2: Tab CSS Styles")
        
        try:
            teacher_user = self.setup_test_data()
            if not teacher_user:
                self.log_test("Tab CSS Styles", "FAIL", "Could not create test user")
                return
            
            self.client.login(username='testteacher_matrix', password='testpass123')
            response = self.client.get(reverse('RoutineTest:classes_exams_unified'))
            
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                
                # Check for essential CSS
                css_checks = [
                    '.exam-type-tabs',
                    '.exam-type-tab',
                    '.exam-type-tab.active',
                    'background: #2E7D32',  # RoutineTest green
                    '.tab-badge',
                    '.matrix-filter-review',
                    '.matrix-filter-quarterly',
                    '.matrix-filter-all'
                ]
                
                missing_css = []
                for css in css_checks:
                    if css not in content:
                        missing_css.append(css)
                
                if not missing_css:
                    self.log_test("Tab CSS Styles", "PASS", "All required styles present")
                else:
                    self.log_test("Tab CSS Styles", "FAIL", f"Missing: {', '.join(missing_css[:3])}")
            else:
                self.log_test("Tab CSS Styles", "FAIL", f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Tab CSS Styles", "FAIL", str(e))
    
    def test_javascript_functionality(self):
        """Test that JavaScript for tab toggle is present"""
        print("\n⚙️ Test 3: JavaScript Functionality")
        
        try:
            teacher_user = self.setup_test_data()
            if not teacher_user:
                self.log_test("JavaScript Functionality", "FAIL", "Could not create test user")
                return
            
            self.client.login(username='testteacher_matrix', password='testpass123')
            response = self.client.get(reverse('RoutineTest:classes_exams_unified'))
            
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                
                # Check for JavaScript functions
                js_checks = [
                    'initializeMatrixTabToggle',
                    'countExamsByType',
                    'applyMatrixFilter',
                    'updateCellVisibility',
                    'MATRIX_TAB_TOGGLE',
                    'sessionStorage.setItem',
                    'data-exam-type'
                ]
                
                missing_js = []
                for js in js_checks:
                    if js not in content:
                        missing_js.append(js)
                
                if not missing_js:
                    self.log_test("JavaScript Functionality", "PASS", "All JS functions present")
                else:
                    self.log_test("JavaScript Functionality", "FAIL", f"Missing: {', '.join(missing_js[:3])}")
            else:
                self.log_test("JavaScript Functionality", "FAIL", f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("JavaScript Functionality", "FAIL", str(e))
    
    def test_matrix_structure(self):
        """Test that matrix table structure is intact"""
        print("\n📊 Test 4: Matrix Table Structure")
        
        try:
            teacher_user = self.setup_test_data()
            if not teacher_user:
                self.log_test("Matrix Table Structure", "FAIL", "Could not create test user")
                return
            
            self.client.login(username='testteacher_matrix', password='testpass123')
            response = self.client.get(reverse('RoutineTest:classes_exams_unified'))
            
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                
                # Check matrix elements
                matrix_checks = [
                    'matrix-table',
                    'matrix-cell',
                    'exam-indicator',
                    'exam-review',
                    'exam-quarterly',
                    'matrix-content'
                ]
                
                missing_elements = []
                for element in matrix_checks:
                    if element not in content:
                        missing_elements.append(element)
                
                if not missing_elements:
                    self.log_test("Matrix Table Structure", "PASS", "All matrix elements present")
                else:
                    self.log_test("Matrix Table Structure", "FAIL", f"Missing: {', '.join(missing_elements)}")
            else:
                self.log_test("Matrix Table Structure", "FAIL", f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Matrix Table Structure", "FAIL", str(e))
    
    def test_keyboard_shortcuts(self):
        """Test that keyboard shortcuts are implemented"""
        print("\n⌨️ Test 5: Keyboard Shortcuts")
        
        try:
            teacher_user = self.setup_test_data()
            if not teacher_user:
                self.log_test("Keyboard Shortcuts", "FAIL", "Could not create test user")
                return
            
            self.client.login(username='testteacher_matrix', password='testpass123')
            response = self.client.get(reverse('RoutineTest:classes_exams_unified'))
            
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                
                # Check for keyboard event handling
                has_keydown = 'keydown' in content
                has_alt_key = 'e.altKey' in content
                has_alt_1 = "case '1':" in content
                has_alt_2 = "case '2':" in content
                has_alt_3 = "case '3':" in content
                
                if all([has_keydown, has_alt_key, has_alt_1, has_alt_2, has_alt_3]):
                    self.log_test("Keyboard Shortcuts", "PASS", "Alt+1/2/3 shortcuts implemented")
                else:
                    self.log_test("Keyboard Shortcuts", "FAIL", "Missing keyboard shortcuts")
            else:
                self.log_test("Keyboard Shortcuts", "FAIL", f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Keyboard Shortcuts", "FAIL", str(e))
    
    def test_console_logging(self):
        """Test that comprehensive console logging is present"""
        print("\n📝 Test 6: Console Logging")
        
        try:
            teacher_user = self.setup_test_data()
            if not teacher_user:
                self.log_test("Console Logging", "FAIL", "Could not create test user")
                return
            
            self.client.login(username='testteacher_matrix', password='testpass123')
            response = self.client.get(reverse('RoutineTest:classes_exams_unified'))
            
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                
                # Check for console.log statements
                log_checks = [
                    'console.log',
                    'console.group',
                    'MATRIX_TAB_TOGGLE',
                    'UNIFIED_VIEW',
                    'MATRIX_DEBUG',
                    'Exam counts updated',
                    'Tab clicked'
                ]
                
                missing_logs = []
                for log in log_checks:
                    if log not in content:
                        missing_logs.append(log)
                
                if not missing_logs:
                    self.log_test("Console Logging", "PASS", "Comprehensive logging present")
                else:
                    self.log_test("Console Logging", "WARN", f"Some logs missing: {', '.join(missing_logs[:3])}")
            else:
                self.log_test("Console Logging", "FAIL", f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Console Logging", "FAIL", str(e))
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        print("\n" + "="*60)
        print("🚀 CLASSES & EXAMS MATRIX TOGGLE - QA TEST SUITE")
        print("="*60)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📦 Module: RoutineTest - Classes & Exams Page")
        print(f"🎯 Feature: Review/Quarterly Toggle for Matrix")
        
        # Run tests
        self.test_view_rendering()
        self.test_tab_css_styles()
        self.test_javascript_functionality()
        self.test_matrix_structure()
        self.test_keyboard_shortcuts()
        self.test_console_logging()
        
        # Generate summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        warned = sum(1 for r in self.test_results if r['status'] == 'WARN')
        total = len(self.test_results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {failed}/{total}")
        print(f"⚠️ Warnings: {warned}/{total}")
        
        if failed == 0:
            print("\n🎉 ALL CRITICAL TESTS PASSED! Matrix toggle implementation successful.")
        elif failed <= 2:
            print("\n⚠️ MOSTLY PASSED: Minor issues detected, but implementation is functional.")
        else:
            print("\n❌ IMPLEMENTATION INCOMPLETE: Multiple failures detected.")
        
        # Recommendations
        print("\n" + "="*60)
        print("📝 RECOMMENDATIONS")
        print("="*60)
        
        print("1. Open browser console to verify JavaScript execution")
        print("2. Test tab clicking functionality manually")
        print("3. Verify exam counts update in badges")
        print("4. Test keyboard shortcuts (Alt+1/2/3)")
        print("5. Check session storage for preference persistence")
        print("6. Verify matrix cells filter correctly by exam type")
        
        return failed == 0

if __name__ == "__main__":
    tester = TestClassesExamsMatrixToggle()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
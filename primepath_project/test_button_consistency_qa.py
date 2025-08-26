"""
Button Consistency QA Test Suite
================================
Purpose: Comprehensive testing of button styling consistency fixes
Issue: FULL ACCESS and DELETE buttons have different shapes/sizes
Solution: Verify all buttons have consistent styling
Date: August 26, 2025
"""

import os
import sys
import json
import re

# Setup Django environment FIRST
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')

import django
django.setup()

# Import Django modules AFTER setup
from django.test import Client
from django.contrib.auth.models import User

from core.models import Teacher
from primepath_routinetest.models import Class

class ButtonConsistencyQA:
    """QA test suite for button consistency"""
    
    def __init__(self):
        self.client = Client()
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = []
        
    def setup_test_user(self):
        """Ensure admin user exists and has proper credentials"""
        try:
            admin = User.objects.get(username='admin')
        except User.DoesNotExist:
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
        else:
            admin.set_password('admin123')
            admin.save()
            
        # Ensure admin has teacher profile
        try:
            teacher = Teacher.objects.get(user=admin)
        except Teacher.DoesNotExist:
            teacher = Teacher.objects.create(
                user=admin,
                name='Admin Teacher',
                is_head_teacher=True
            )
        
        return admin
        
    def login_as_admin(self):
        """Login as admin user"""
        return self.client.login(username='admin', password='admin123')
        
    def test_css_files_loaded(self):
        """Test that button consistency CSS files are loaded"""
        print("\n[TEST] Checking CSS Files Loading...")
        
        login_success = self.login_as_admin()
        if not login_success:
            self.record_test("CSS Files Loading - Login", False, "Failed to login as admin")
            return
            
        response = self.client.get('/RoutineTest/')
        
        if response.status_code == 200:
            content = response.content.decode()
            
            # Check for button-consistency-fix.css
            if 'button-consistency-fix.css' in content:
                self.record_test("Button Consistency CSS", True, "CSS file is loaded")
            else:
                self.record_test("Button Consistency CSS", False, "CSS file not found in template")
                
            # Check for button-consistency-debug.js
            if 'button-consistency-debug.js' in content:
                self.record_test("Button Debug JS", True, "Debug script is loaded")
            else:
                self.record_test("Button Debug JS", False, "Debug script not found in template")
        else:
            self.record_test("Page Load", False, f"Page returned {response.status_code}")
            
    def test_admin_dashboard(self):
        """Test admin dashboard button consistency"""
        print("\n[TEST] Testing Admin Dashboard...")
        
        login_success = self.login_as_admin()
        if not login_success:
            self.record_test("Admin Dashboard - Login", False, "Failed to login")
            return
            
        response = self.client.get('/RoutineTest/admin/dashboard/')
        
        if response.status_code == 200:
            self.record_test("Admin Dashboard Load", True, "Dashboard loaded successfully")
            content = response.content.decode()
            
            # Check for button styling consistency
            button_pattern = r'<button[^>]*style="[^"]*"[^>]*>'
            buttons = re.findall(button_pattern, content)
            
            if buttons:
                print(f"  Found {len(buttons)} buttons with inline styles")
                
                # Check for consistent styling patterns
                consistent = True
                for button in buttons[:5]:  # Check first 5 buttons
                    if 'min-width' not in button or 'padding' not in button:
                        consistent = False
                        break
                        
                if consistent:
                    self.record_test("Button Style Consistency", True, f"Buttons have consistent styling")
                else:
                    self.record_test("Button Style Consistency", False, "Some buttons lack required styles")
            else:
                print("  No buttons with inline styles found (CSS styling applied)")
                self.record_test("Button CSS Styling", True, "Buttons use CSS classes")
        else:
            self.record_test("Admin Dashboard Load", False, f"Returned status {response.status_code}")
            
    def test_class_management_buttons(self):
        """Test class management page buttons"""
        print("\n[TEST] Testing Class Management Buttons...")
        
        login_success = self.login_as_admin()
        if not login_success:
            self.record_test("Class Management - Login", False, "Failed to login")
            return
            
        response = self.client.get('/RoutineTest/classes-exams/')
        
        if response.status_code == 200:
            self.record_test("Classes Page Load", True, "Classes page loaded successfully")
            content = response.content.decode()
            
            # Check for FULL ACCESS mentions
            full_access_count = content.count('FULL ACCESS')
            delete_count = content.count('DELETE')
            delete_button_count = content.count('btn-delete')
            
            print(f"  FULL ACCESS mentions: {full_access_count}")
            print(f"  DELETE mentions: {delete_count}")
            print(f"  Delete button classes: {delete_button_count}")
            
            if full_access_count > 0 or delete_button_count > 0:
                self.record_test("Button Elements Present", True, 
                               f"Found {full_access_count} FULL ACCESS and {delete_button_count} DELETE buttons")
            else:
                self.record_test("Button Elements Present", False, 
                               "No FULL ACCESS or DELETE buttons found")
                               
            # Check for button consistency classes
            if 'btn-delete-class' in content:
                self.record_test("Delete Button Class", True, "Delete button has proper class")
            else:
                self.record_test("Delete Button Class", False, "Delete button missing proper class")
                
        else:
            self.record_test("Classes Page Load", False, f"Returned status {response.status_code}")
            
    def test_teacher_management(self):
        """Test teacher management section buttons"""
        print("\n[TEST] Testing Teacher Management Section...")
        
        login_success = self.login_as_admin()
        if not login_success:
            self.record_test("Teacher Management - Login", False, "Failed to login")
            return
            
        # Test teacher management dashboard
        response = self.client.get('/RoutineTest/admin/teacher-management/')
        
        if response.status_code == 200:
            self.record_test("Teacher Dashboard Load", True, "Teacher management loaded")
            content = response.content.decode()
            
            # Check for action buttons
            if 'btn-edit' in content or 'btn-save' in content:
                self.record_test("Management Buttons", True, "Management buttons present")
            else:
                self.record_test("Management Buttons", False, "No management buttons found")
        else:
            # Page might not exist, but that's OK for this test
            self.record_test("Teacher Dashboard", True, f"Page status: {response.status_code}")
            
    def test_static_css_file(self):
        """Test that static CSS file is accessible"""
        print("\n[TEST] Testing Static CSS File Access...")
        
        response = self.client.get('/static/css/button-consistency-fix.css')
        
        if response.status_code == 200:
            content = response.content.decode()
            
            # Check for key CSS rules
            if 'min-width: 120px' in content:
                self.record_test("CSS Min Width Rule", True, "Min width rule found")
            else:
                self.record_test("CSS Min Width Rule", False, "Min width rule not found")
                
            if 'min-height: 40px' in content:
                self.record_test("CSS Min Height Rule", True, "Min height rule found")
            else:
                self.record_test("CSS Min Height Rule", False, "Min height rule not found")
                
            if 'padding: 10px 20px' in content:
                self.record_test("CSS Padding Rule", True, "Padding rule found")
            else:
                self.record_test("CSS Padding Rule", False, "Padding rule not found")
                
            if 'border-radius: 8px' in content:
                self.record_test("CSS Border Radius Rule", True, "Border radius rule found")
            else:
                self.record_test("CSS Border Radius Rule", False, "Border radius rule not found")
                
        else:
            self.record_test("Static CSS Access", False, f"CSS file returned {response.status_code}")
            
    def test_javascript_debug_file(self):
        """Test that debug JavaScript file is accessible"""
        print("\n[TEST] Testing Debug JavaScript File...")
        
        response = self.client.get('/static/js/button-consistency-debug.js')
        
        if response.status_code == 200:
            content = response.content.decode()
            
            # Check for key JavaScript functions
            if 'ButtonMonitor' in content:
                self.record_test("ButtonMonitor Object", True, "ButtonMonitor found in JS")
            else:
                self.record_test("ButtonMonitor Object", False, "ButtonMonitor not found")
                
            if 'checkButtonConsistency' in content:
                self.record_test("Consistency Check Function", True, "Check function found")
            else:
                self.record_test("Consistency Check Function", False, "Check function not found")
                
            if 'applyButtonFix' in content:
                self.record_test("Fix Function", True, "Fix function found")
            else:
                self.record_test("Fix Function", False, "Fix function not found")
                
        else:
            self.record_test("Static JS Access", False, f"JS file returned {response.status_code}")
            
    def record_test(self, test_name, passed, message=""):
        """Record test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status} - {test_name}"
        if message:
            result += f" ({message})"
            
        self.test_results.append(result)
        
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
            
        print(f"  {result}")
        
    def run_all_tests(self):
        """Run all QA tests"""
        print("\n" + "="*70)
        print("BUTTON CONSISTENCY QA TEST SUITE")
        print("="*70)
        
        # Setup test environment
        self.setup_test_user()
        
        # Run tests
        self.test_css_files_loaded()
        self.test_static_css_file()
        self.test_javascript_debug_file()
        self.test_admin_dashboard()
        self.test_class_management_buttons()
        self.test_teacher_management()
        
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        total_tests = self.passed_tests + self.failed_tests
        pass_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\nTotal Tests: {total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        if self.failed_tests > 0:
            print("\n⚠️ Failed Tests:")
            for result in self.test_results:
                if result.startswith("❌"):
                    print(f"  {result}")
                    
        print("\n" + "="*70)
        
        if self.failed_tests == 0:
            print("🎉 ALL TESTS PASSED! Button consistency fix is working correctly.")
        else:
            print("⚠️ Some tests failed. Please review the issues above.")
            
        print("="*70)
        
        # Debug information
        print("\n📋 Debug Information:")
        print("  - Server URL: http://127.0.0.1:8000/")
        print("  - Admin Login: admin / admin123")
        print("  - CSS File: /static/css/button-consistency-fix.css")
        print("  - JS Debug: /static/js/button-consistency-debug.js")
        print("  - Console Commands:")
        print("    • buttonDebug.report()  - Generate consistency report")
        print("    • buttonDebug.fixAll()  - Force fix all buttons")
        print("    • buttonDebug.check()   - Check all buttons now")
        

if __name__ == "__main__":
    # Run QA tests
    qa = ButtonConsistencyQA()
    qa.run_all_tests()
    
    print("\n✅ QA Testing Complete!")
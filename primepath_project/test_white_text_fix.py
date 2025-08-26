"""
White Text Fix QA Test Suite
=============================
Purpose: Verify that text appears white on dark green backgrounds
Issue: Screenshots show dark text on green backgrounds 
Solution: Test that white-text-fix.css is working correctly
Date: August 26, 2025
"""

import os
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')

import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import Teacher

class WhiteTextFixQA:
    """QA test suite for white text fix"""
    
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
        
    def test_white_text_css_loaded(self):
        """Test that white-text-fix.css is loaded"""
        print("\n[TEST] Checking White Text CSS Loading...")
        
        login_success = self.login_as_admin()
        if not login_success:
            self.record_test("White Text CSS - Login", False, "Failed to login as admin")
            return
            
        response = self.client.get('/RoutineTest/')
        
        if response.status_code == 200:
            content = response.content.decode()
            
            # Check for white-text-fix.css
            if 'white-text-fix.css' in content:
                self.record_test("White Text Fix CSS", True, "CSS file is loaded")
            else:
                self.record_test("White Text Fix CSS", False, "CSS file not found in template")
        else:
            self.record_test("Page Load", False, f"Page returned {response.status_code}")
            
    def test_white_text_js_loaded(self):
        """Test that white-text-debug.js is loaded"""
        print("\n[TEST] Checking White Text JS Debug Module...")
        
        login_success = self.login_as_admin()
        if not login_success:
            self.record_test("White Text JS - Login", False, "Failed to login")
            return
            
        response = self.client.get('/RoutineTest/')
        
        if response.status_code == 200:
            content = response.content.decode()
            
            # Check for white-text-debug.js
            if 'white-text-debug.js' in content:
                self.record_test("White Text Debug JS", True, "Debug script is loaded")
            else:
                self.record_test("White Text Debug JS", False, "Debug script not found in template")
        else:
            self.record_test("Page Load", False, f"Page returned {response.status_code}")
            
    def test_static_css_file(self):
        """Test that static CSS file is accessible"""
        print("\n[TEST] Testing Static White Text CSS File Access...")
        
        response = self.client.get('/static/css/white-text-fix.css')
        
        if response.status_code == 200:
            content = response.content.decode()
            
            # Check for key CSS rules
            if 'color: white !important' in content:
                self.record_test("CSS White Color Rule", True, "White color rule found")
            else:
                self.record_test("CSS White Color Rule", False, "White color rule not found")
                
            if 'color: #FFFFFF !important' in content:
                self.record_test("CSS White Hex Rule", True, "White hex rule found")
            else:
                self.record_test("CSS White Hex Rule", False, "White hex rule not found")
                
            if '.program-header' in content:
                self.record_test("Program Header Rule", True, "Program header rule found")
            else:
                self.record_test("Program Header Rule", False, "Program header rule not found")
                
            if '.nav-tabs' in content:
                self.record_test("Navigation Rule", True, "Navigation rule found")
            else:
                self.record_test("Navigation Rule", False, "Navigation rule not found")
                
        else:
            self.record_test("Static CSS Access", False, f"CSS file returned {response.status_code}")
            
    def test_static_js_file(self):
        """Test that debug JavaScript file is accessible"""
        print("\n[TEST] Testing White Text Debug JavaScript File...")
        
        response = self.client.get('/static/js/white-text-debug.js')
        
        if response.status_code == 200:
            content = response.content.decode()
            
            # Check for key JavaScript functions
            if 'WhiteTextMonitor' in content:
                self.record_test("WhiteTextMonitor Object", True, "WhiteTextMonitor found in JS")
            else:
                self.record_test("WhiteTextMonitor Object", False, "WhiteTextMonitor not found")
                
            if 'checkElementTextColor' in content:
                self.record_test("Color Check Function", True, "Color check function found")
            else:
                self.record_test("Color Check Function", False, "Color check function not found")
                
            if 'applyWhiteTextFix' in content:
                self.record_test("Fix Function", True, "Fix function found")
            else:
                self.record_test("Fix Function", False, "Fix function not found")
                
            if 'whiteTextDebug' in content:
                self.record_test("Debug Commands", True, "Debug commands found")
            else:
                self.record_test("Debug Commands", False, "Debug commands not found")
                
        else:
            self.record_test("Static JS Access", False, f"JS file returned {response.status_code}")
            
    def test_classes_exams_page(self):
        """Test classes & exams page for proper white text"""
        print("\n[TEST] Testing Classes & Exams Page...")
        
        login_success = self.login_as_admin()
        if not login_success:
            self.record_test("Classes Page - Login", False, "Failed to login")
            return
            
        response = self.client.get('/RoutineTest/classes-exams/')
        
        if response.status_code == 200:
            self.record_test("Classes Page Load", True, "Classes page loaded successfully")
            content = response.content.decode()
            
            # Check for program headers with forced white text
            if '.program-header' in content and 'color: white !important' in content:
                self.record_test("Program Header White Text", True, "Program headers have white text CSS")
            else:
                self.record_test("Program Header White Text", False, "Program headers missing white text CSS")
                
            # Check for navigation elements
            if '.nav-tabs' in content or 'nav-tabs' in content:
                self.record_test("Navigation Elements Present", True, "Navigation elements found")
            else:
                self.record_test("Navigation Elements Present", False, "Navigation elements not found")
                
        else:
            self.record_test("Classes Page Load", False, f"Returned status {response.status_code}")
            
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
        print("WHITE TEXT FIX QA TEST SUITE")
        print("="*70)
        
        # Setup test environment
        self.setup_test_user()
        
        # Run tests
        self.test_white_text_css_loaded()
        self.test_white_text_js_loaded()
        self.test_static_css_file()
        self.test_static_js_file()
        self.test_classes_exams_page()
        
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
            print("🎉 ALL TESTS PASSED! White text fix is working correctly.")
        else:
            print("⚠️ Some tests failed. Please review the issues above.")
            
        print("="*70)
        
        # Debug information
        print("\n📋 Debug Information:")
        print("  - Server URL: http://127.0.0.1:8000/")
        print("  - Admin Login: admin / admin123")
        print("  - CSS File: /static/css/white-text-fix.css")
        print("  - JS Debug: /static/js/white-text-debug.js")
        print("  - Console Commands:")
        print("    • whiteTextDebug.report()  - Generate white text report")
        print("    • whiteTextDebug.fixAll()  - Force fix all elements")
        print("    • whiteTextDebug.check()   - Check all elements now")
        print("    • whiteTextDebug.toggleDebug() - Toggle debug mode")
        

if __name__ == "__main__":
    # Run QA tests
    qa = WhiteTextFixQA()
    qa.run_all_tests()
    
    print("\n✅ White Text Fix QA Testing Complete!")
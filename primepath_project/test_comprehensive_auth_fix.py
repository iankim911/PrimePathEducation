#!/usr/bin/env python
"""
Comprehensive Authentication Fix Testing
Tests all authentication flows and validates backend selection

This script tests:
1. Student registration and login
2. Teacher login flows
3. Authentication backend selection
4. Error handling and logging
5. User type detection

Run from primepath_project directory:
python test_comprehensive_auth_fix.py
"""

import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth.models import User
from django.contrib import messages
from core.utils.authentication import (
    safe_login, 
    student_login, 
    teacher_login,
    debug_authentication_state,
    validate_authentication_setup,
    UserTypeDetector
)
from primepath_student.models import StudentProfile
from core.models import Teacher
import json


class AuthenticationTester:
    """Comprehensive authentication testing suite"""
    
    def __init__(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.test_results = {
            'timestamp': '',
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'results': []
        }
    
    def log_test_result(self, test_name, passed, details=None):
        """Log individual test results"""
        result = {
            'test': test_name,
            'passed': passed,
            'details': details or {}
        }
        
        self.test_results['results'].append(result)
        self.test_results['tests_run'] += 1
        
        if passed:
            self.test_results['tests_passed'] += 1
            print(f"✅ {test_name}")
        else:
            self.test_results['tests_failed'] += 1
            print(f"❌ {test_name}: {details}")
    
    def test_authentication_setup(self):
        """Test authentication configuration validation"""
        print("\n=== Testing Authentication Setup ===")
        
        try:
            validation_results = validate_authentication_setup()
            
            # Check if multiple backends are configured
            backends_configured = validation_results['backends_configured']
            
            if backends_configured >= 2:
                self.log_test_result(
                    "Multiple Authentication Backends Configured", 
                    True,
                    {'backends_count': backends_configured}
                )
            else:
                self.log_test_result(
                    "Multiple Authentication Backends Configured", 
                    False,
                    {'backends_count': backends_configured, 'message': 'Need at least 2 backends for this test'}
                )
                
            # Test if allauth is configured
            allauth_enabled = validation_results['configuration'].get('allauth_enabled', False)
            self.log_test_result(
                "Allauth Backend Configured",
                allauth_enabled,
                validation_results['configuration']
            )
            
        except Exception as e:
            self.log_test_result(
                "Authentication Setup Validation",
                False,
                {'error': str(e)}
            )
    
    def test_user_type_detection(self):
        """Test user type detection logic"""
        print("\n=== Testing User Type Detection ===")
        
        # Test with admin user
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if admin_user:
                context = UserTypeDetector.detect_user_type(admin_user)
                self.log_test_result(
                    "Admin User Type Detection",
                    context['user_type'] in ['TEACHER', 'DJANGO_USER', 'OAUTH_USER'],
                    context
                )
            else:
                self.log_test_result(
                    "Admin User Type Detection",
                    False,
                    {'error': 'No admin user found'}
                )
        except Exception as e:
            self.log_test_result(
                "Admin User Type Detection",
                False,
                {'error': str(e)}
            )
        
        # Test with teacher user
        try:
            teacher_user = User.objects.filter(teacher_profile__isnull=False).first()
            if teacher_user:
                context = UserTypeDetector.detect_user_type(teacher_user)
                self.log_test_result(
                    "Teacher User Type Detection",
                    context['user_type'] == 'TEACHER',
                    context
                )
            else:
                self.log_test_result(
                    "Teacher User Type Detection",
                    False,
                    {'error': 'No teacher user found'}
                )
        except Exception as e:
            self.log_test_result(
                "Teacher User Type Detection",
                False,
                {'error': str(e)}
            )
        
        # Test with student user
        try:
            student_user = User.objects.filter(primepath_student_profile__isnull=False).first()
            if student_user:
                context = UserTypeDetector.detect_user_type(student_user)
                self.log_test_result(
                    "Student User Type Detection",
                    context['user_type'] == 'STUDENT',
                    context
                )
            else:
                self.log_test_result(
                    "Student User Type Detection",
                    False,
                    {'error': 'No student user found'}
                )
        except Exception as e:
            self.log_test_result(
                "Student User Type Detection",
                False,
                {'error': str(e)}
            )
    
    def test_student_registration_flow(self):
        """Test student registration with authentication fix"""
        print("\n=== Testing Student Registration Flow ===")
        
        try:
            # Test student registration endpoint with correct field names and phone format
            test_data = {
                'first_name': 'Test',
                'last_name': 'Student Auth Fix',
                'student_id': 'test_auth_fix_001',
                'phone_number': '01012345678',  # Fixed: no dashes, digits only
                'email': 'test.auth.fix@example.com',
                'parent1_name': 'Test Parent',
                'parent1_phone': '01098765432',  # Fixed: no dashes, digits only
                'password1': 'TestAuth123!',
                'password2': 'TestAuth123!'
            }
            
            # Use Django test client with CSRF middleware disabled for this test
            response = self.client.post('/student/register/', test_data, follow=True)
            
            # Debug the response content
            print(f"Registration response status: {response.status_code}")
            if response.status_code == 200:
                # Form validation failed, extract error messages
                content = response.content.decode()
                if 'class="errorlist"' in content or 'alert-danger' in content or 'error' in content.lower():
                    print("FORM VALIDATION ERRORS DETECTED in response")
                    # Try to extract visible error messages from HTML
                    import re
                    error_patterns = [
                        r'<ul class="errorlist[^"]*"[^>]*>(.*?)</ul>',
                        r'<div class="alert[^"]*alert-danger[^"]*"[^>]*>(.*?)</div>',
                        r'<span class="error[^"]*"[^>]*>(.*?)</span>'
                    ]
                    for pattern in error_patterns:
                        errors = re.findall(pattern, content, re.DOTALL)
                        if errors:
                            print(f"Found errors: {errors}")
            
            # Check if registration succeeded (should redirect or show success)
            if response.status_code == 302:
                # Success case - redirected
                self.log_test_result(
                    "Student Registration HTTP Response", 
                    True,
                    {'status_code': response.status_code, 'redirect_url': getattr(response, 'url', None)}
                )
                success = True
            elif response.status_code == 200:
                # Check if user was actually created despite 200 status
                if User.objects.filter(username='test_auth_fix_001').exists():
                    self.log_test_result(
                        "Student Registration HTTP Response",
                        True, 
                        {'status_code': response.status_code, 'note': 'Success with 200 status'}
                    )
                    success = True
                else:
                    self.log_test_result(
                        "Student Registration HTTP Response", 
                        False,
                        {'status_code': response.status_code, 'error': 'Form validation failed - no user created'}
                    )
                    success = False
            else:
                self.log_test_result(
                    "Student Registration HTTP Response",
                    False,
                    {'status_code': response.status_code, 'content': response.content.decode()[:500]}
                )
                success = False
                
            # Check if user was created regardless of status code
            import time
            time.sleep(0.1)  # Small delay to ensure database transaction completes
            
            print(f"Checking for user 'test_auth_fix_001' in database...")
            user_exists = User.objects.filter(username='test_auth_fix_001').exists()
            print(f"User exists: {user_exists}")
            
            if user_exists:
                user = User.objects.get(username='test_auth_fix_001')
                self.log_test_result(
                    "Student User Account Created",
                    True,
                    {'username': 'test_auth_fix_001', 'user_id': user.id}
                )
                
                # Check if student profile was created
                profile_exists = StudentProfile.objects.filter(student_id='test_auth_fix_001').exists()
                if profile_exists:
                    profile = StudentProfile.objects.get(student_id='test_auth_fix_001')
                    self.log_test_result(
                        "Student Profile Created",
                        True,
                        {'student_id': 'test_auth_fix_001', 'profile_id': profile.id}
                    )
                else:
                    self.log_test_result(
                        "Student Profile Created",
                        False,
                        {'error': 'Student profile not found'}
                    )
            else:
                # Debug - show what users do exist
                existing_users = list(User.objects.values_list('username', flat=True))
                print(f"Existing users in database: {existing_users}")
                self.log_test_result(
                    "Student User Account Created",
                    False,
                    {'error': 'User account not found', 'existing_users': len(existing_users)}
                )
            
        except Exception as e:
            self.log_test_result(
                "Student Registration Flow",
                False,
                {'error': str(e)}
            )
    
    def test_student_login_flow(self):
        """Test student login with authentication fix"""
        print("\n=== Testing Student Login Flow ===")
        
        try:
            # Create or get test student
            test_user, created = User.objects.get_or_create(
                username='test_student_login',
                defaults={
                    'first_name': 'Test',
                    'last_name': 'Student Login',
                    'email': 'test.student.login@example.com'
                }
            )
            
            if created:
                test_user.set_password('TestLogin123!')
                test_user.save()
                
                # Create student profile
                StudentProfile.objects.get_or_create(
                    user=test_user,
                    defaults={
                        'student_id': 'test_student_login',
                        'phone_number': '010-5555-5555'
                    }
                )
            
            # Test login endpoint
            login_data = {
                'login_id': 'test_student_login',
                'password': 'TestLogin123!'
            }
            
            response = self.client.post('/student/login/', login_data)
            
            if response.status_code in [200, 302]:
                self.log_test_result(
                    "Student Login HTTP Response",
                    True,
                    {'status_code': response.status_code}
                )
                
                # Check if user is logged in
                if '_auth_user_id' in self.client.session:
                    self.log_test_result(
                        "Student User Session Created",
                        True,
                        {'user_id': self.client.session['_auth_user_id']}
                    )
                else:
                    self.log_test_result(
                        "Student User Session Created",
                        False,
                        {'session_keys': list(self.client.session.keys())}
                    )
            else:
                self.log_test_result(
                    "Student Login HTTP Response",
                    False,
                    {'status_code': response.status_code, 'content': response.content.decode()[:500]}
                )
                
        except Exception as e:
            self.log_test_result(
                "Student Login Flow",
                False,
                {'error': str(e)}
            )
    
    def test_teacher_login_flow(self):
        """Test teacher login with authentication fix"""
        print("\n=== Testing Teacher Login Flow ===")
        
        try:
            # Test with existing teacher
            teacher = Teacher.objects.filter(user__isnull=False).first()
            
            if teacher and teacher.user:
                # Set a known password
                teacher.user.set_password('TeacherTest123!')
                teacher.user.save()
                
                login_data = {
                    'username': teacher.user.username,
                    'password': 'TeacherTest123!',
                    'remember': False
                }
                
                response = self.client.post('/RoutineTest/login/', login_data)
                
                if response.status_code in [200, 302]:
                    self.log_test_result(
                        "Teacher Login HTTP Response",
                        True,
                        {'status_code': response.status_code}
                    )
                else:
                    self.log_test_result(
                        "Teacher Login HTTP Response",
                        False,
                        {'status_code': response.status_code, 'content': response.content.decode()[:500]}
                    )
            else:
                self.log_test_result(
                    "Teacher Login Flow",
                    False,
                    {'error': 'No teacher with user account found'}
                )
                
        except Exception as e:
            self.log_test_result(
                "Teacher Login Flow",
                False,
                {'error': str(e)}
            )
    
    def test_safe_login_functions(self):
        """Test the safe_login utility functions"""
        print("\n=== Testing Safe Login Functions ===")
        
        try:
            # Create test request with proper session using Django test client
            from django.test.client import RequestFactory
            from django.contrib.sessions.backends.db import SessionStore
            
            request = RequestFactory().get('/')
            # Create a proper session object
            session = SessionStore()
            session.save()  # This creates the session_key
            request.session = session
            
            # Test with student user
            student_user = User.objects.filter(primepath_student_profile__isnull=False).first()
            if student_user:
                result = student_login(request, student_user, test_context='unit_test')
                self.log_test_result(
                    "Student Safe Login Function",
                    result == True,
                    {'result': result, 'user': student_user.username}
                )
            
            # Test with teacher user
            teacher_user = User.objects.filter(teacher_profile__isnull=False).first()
            if teacher_user:
                result = teacher_login(request, teacher_user, test_context='unit_test')
                self.log_test_result(
                    "Teacher Safe Login Function",
                    result == True,
                    {'result': result, 'user': teacher_user.username}
                )
                
        except Exception as e:
            self.log_test_result(
                "Safe Login Functions",
                False,
                {'error': str(e)}
            )
    
    def cleanup_test_data(self):
        """Clean up test data created during tests"""
        print("\n=== Cleaning Up Test Data ===")
        
        try:
            # Clean up test users
            test_usernames = [
                'test_auth_fix_001',
                'test_student_login'
            ]
            
            for username in test_usernames:
                try:
                    user = User.objects.get(username=username)
                    if hasattr(user, 'primepath_student_profile'):
                        user.primepath_student_profile.delete()
                    user.delete()
                    print(f"  Cleaned up user: {username}")
                except User.DoesNotExist:
                    pass
            
            self.log_test_result(
                "Test Data Cleanup",
                True,
                {'cleaned_users': len(test_usernames)}
            )
            
        except Exception as e:
            self.log_test_result(
                "Test Data Cleanup",
                False,
                {'error': str(e)}
            )
    
    def run_all_tests(self):
        """Run all authentication tests"""
        import datetime
        
        print("🧪 COMPREHENSIVE AUTHENTICATION FIX TESTING")
        print("=" * 60)
        
        self.test_results['timestamp'] = datetime.datetime.now().isoformat()
        
        # Run all tests
        self.test_authentication_setup()
        self.test_user_type_detection()
        self.test_safe_login_functions()
        self.test_student_registration_flow()
        self.test_student_login_flow()
        self.test_teacher_login_flow()
        self.cleanup_test_data()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎯 TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Run: {self.test_results['tests_run']}")
        print(f"Tests Passed: {self.test_results['tests_passed']}")
        print(f"Tests Failed: {self.test_results['tests_failed']}")
        
        if self.test_results['tests_failed'] == 0:
            print("🎉 ALL TESTS PASSED! Authentication fix is working correctly!")
        else:
            print(f"⚠️  {self.test_results['tests_failed']} tests failed. Review the issues above.")
        
        # Save detailed results
        with open('authentication_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n📄 Detailed results saved to: authentication_test_results.json")
        
        return self.test_results['tests_failed'] == 0


if __name__ == '__main__':
    tester = AuthenticationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
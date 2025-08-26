#!/usr/bin/env python3
"""
Phase 2 Security Testing Suite
Tests all security fixes and credential management

Created: August 26, 2025
Tests:
- OAuth credential security
- SECRET_KEY management
- Password strength validation
- Security logging and monitoring
- User creation security
"""

import os
import sys
import django
import tempfile
from unittest.mock import patch, MagicMock

# Setup Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.core.cache import cache
from core.services.security_service import SecurityService, get_oauth_credentials, validate_password_strength
from core.oauth_config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, KAKAO_CLIENT_ID, KAKAO_CLIENT_SECRET


class Phase2SecurityTest:
    """Comprehensive test suite for Phase 2 security changes"""
    
    def __init__(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        print("🔐 Phase 2 Security Testing Suite")
        print("=" * 60)
    
    def log_test(self, test_name, passed, message=""):
        """Log test results"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"   {message}")
        
        if passed:
            self.results['passed'] += 1
        else:
            self.results['failed'] += 1
            self.results['errors'].append(f"{test_name}: {message}")
    
    def test_secret_key_security(self):
        """Test SECRET_KEY security enhancements"""
        print("\n🔑 Testing SECRET_KEY Security")
        
        # Test secret key validation
        valid_secret = SecurityService.generate_secure_secret_key()
        self.log_test(
            "Generated Secret Key Validation",
            SecurityService.validate_secret_key(valid_secret),
            f"Generated key length: {len(valid_secret)}"
        )
        
        # Test invalid secret keys
        invalid_secrets = [
            'django-insecure-test',
            'your-secret-key-here',
            '123456',
            'short',
            ''
        ]
        
        for invalid_secret in invalid_secrets:
            self.log_test(
                f"Invalid Secret Rejection: {invalid_secret[:20]}...",
                not SecurityService.validate_secret_key(invalid_secret),
                f"Correctly rejected insecure secret"
            )
        
        # Test secret key generation
        secret1 = SecurityService.generate_secure_secret_key()
        secret2 = SecurityService.generate_secure_secret_key()
        self.log_test(
            "Secret Key Uniqueness",
            secret1 != secret2,
            "Each generated secret is unique"
        )
    
    def test_oauth_credential_security(self):
        """Test OAuth credential security"""
        print("\n🌐 Testing OAuth Credential Security")
        
        # Test with environment variables not set (should return None)
        with patch.dict(os.environ, {}, clear=True):
            google_creds = get_oauth_credentials('GOOGLE')
            self.log_test(
                "OAuth Google - No Credentials",
                google_creds is None,
                "Returns None when credentials not configured"
            )
            
            kakao_creds = get_oauth_credentials('KAKAO')
            self.log_test(
                "OAuth Kakao - No Credentials", 
                kakao_creds is None,
                "Returns None when credentials not configured"
            )
        
        # Test with secure credentials
        secure_env = {
            'GOOGLE_CLIENT_ID': 'secure-google-client-id.apps.googleusercontent.com',
            'GOOGLE_CLIENT_SECRET': 'secure-google-client-secret-long-random-string',
            'GOOGLE_REDIRECT_URI': 'https://example.com/auth/google/callback/',
            'KAKAO_REST_API_KEY': 'secure-kakao-rest-api-key-long-random',
            'KAKAO_CLIENT_SECRET': 'secure-kakao-client-secret-long-random',
            'KAKAO_REDIRECT_URI': 'https://example.com/auth/kakao/callback/',
        }
        
        with patch.dict(os.environ, secure_env):
            google_creds = get_oauth_credentials('GOOGLE')
            self.log_test(
                "OAuth Google - Secure Credentials",
                google_creds is not None and 'client_id' in google_creds,
                f"Loaded secure Google credentials: {bool(google_creds)}"
            )
            
            kakao_creds = get_oauth_credentials('KAKAO')
            self.log_test(
                "OAuth Kakao - Secure Credentials",
                kakao_creds is not None and 'client_id' in kakao_creds,
                f"Loaded secure Kakao credentials: {bool(kakao_creds)}"
            )
        
        # Test placeholder detection
        placeholder_env = {
            'GOOGLE_CLIENT_ID': 'your-google-client-id.apps.googleusercontent.com',
            'GOOGLE_CLIENT_SECRET': 'your-google-client-secret',
            'KAKAO_REST_API_KEY': 'your-kakao-rest-api-key',
            'KAKAO_CLIENT_SECRET': 'your-kakao-client-secret',
        }
        
        with patch.dict(os.environ, placeholder_env):
            google_creds = get_oauth_credentials('GOOGLE')
            self.log_test(
                "OAuth Placeholder Detection",
                google_creds is None,
                "Correctly rejects placeholder credentials"
            )
    
    def test_password_strength_validation(self):
        """Test password strength validation"""
        print("\n🛡️ Testing Password Strength Validation")
        
        # Test weak passwords
        weak_passwords = [
            ('', 0),
            ('123', 0),
            ('password', 1), 
            ('Password', 2),
            ('Password123', 3),
        ]
        
        for password, expected_min_score in weak_passwords:
            score, feedback = validate_password_strength(password)
            self.log_test(
                f"Weak Password: '{password[:10]}...'",
                score <= expected_min_score,
                f"Score: {score}, Feedback: {len(feedback)} issues"
            )
        
        # Test strong passwords
        strong_passwords = [
            'MySecureP@ssw0rd!',
            'Sup3r$tr0ng#P@ssw0rd123',
            'C0mpl3x!ty#M@tt3rs$2025',
        ]
        
        for password in strong_passwords:
            score, feedback = validate_password_strength(password)
            self.log_test(
                f"Strong Password Test",
                score >= 4,
                f"Score: {score}/6, Issues: {len(feedback)}"
            )
        
        # Test password generation
        generated_password = SecurityService.generate_secure_password()
        score, feedback = validate_password_strength(generated_password)
        self.log_test(
            "Generated Password Strength",
            score >= 4,
            f"Generated password score: {score}/6"
        )
    
    def test_login_rate_limiting(self):
        """Test login attempt tracking and rate limiting"""
        print("\n🚫 Testing Login Rate Limiting")
        
        # Clear any existing cache
        cache.clear()
        
        username = 'test_user_ratelimit'
        ip_address = '192.168.1.100'
        
        # Test successful login (should not be rate limited)
        self.log_test(
            "Account Not Initially Locked",
            not SecurityService.is_account_locked(username, ip_address),
            "New account should not be locked"
        )
        
        # Simulate failed login attempts
        for i in range(SecurityService.MAX_LOGIN_ATTEMPTS):
            SecurityService.track_login_attempt(username, ip_address, success=False)
        
        # Check if account is now locked
        self.log_test(
            "Account Locked After Max Attempts",
            SecurityService.is_account_locked(username, ip_address),
            f"Account locked after {SecurityService.MAX_LOGIN_ATTEMPTS} attempts"
        )
        
        # Test successful login clears attempts
        username2 = 'test_user_success'
        SecurityService.track_login_attempt(username2, ip_address, success=False)
        SecurityService.track_login_attempt(username2, ip_address, success=True)
        
        self.log_test(
            "Successful Login Clears Attempts",
            not SecurityService.is_account_locked(username2, ip_address),
            "Account unlocked after successful login"
        )
    
    def test_security_logging(self):
        """Test security event logging"""
        print("\n📊 Testing Security Event Logging")
        
        # Clear cache
        cache.clear()
        
        # Log various security events
        SecurityService.log_security_event('test_event', 'test_subject', success=True)
        SecurityService.log_security_event('test_event', 'test_subject2', success=False)
        SecurityService.log_security_event('login_success', 'test_user', ip_address='127.0.0.1')
        
        # Get security status
        status = SecurityService.get_security_status()
        
        self.log_test(
            "Security Status Generation",
            isinstance(status, dict) and 'recent_events' in status,
            f"Status contains: {list(status.keys())}"
        )
        
        self.log_test(
            "OAuth Provider Status",
            'oauth_providers' in status and 'GOOGLE' in status['oauth_providers'],
            f"OAuth providers tracked: {list(status.get('oauth_providers', {}).keys())}"
        )
    
    def test_secure_user_creation(self):
        """Test secure user creation"""
        print("\n👤 Testing Secure User Creation")
        
        # Test user creation with generated password
        try:
            username = f'test_secure_user_{os.getpid()}'
            email = f'{username}@test.com'
            
            user, generated_password = SecurityService.create_secure_user(
                username=username,
                email=email
            )
            
            self.log_test(
                "Secure User Creation with Generated Password",
                user is not None and generated_password is not None,
                f"User created: {username}, Password generated: {len(generated_password)} chars"
            )
            
            # Test password strength of generated password
            score, feedback = validate_password_strength(generated_password)
            self.log_test(
                "Generated Password Meets Requirements",
                score >= SecurityService.PASSWORD_COMPLEXITY_SCORE,
                f"Password score: {score}/{SecurityService.PASSWORD_COMPLEXITY_SCORE}"
            )
            
        except Exception as e:
            self.log_test(
                "Secure User Creation",
                False,
                f"Error: {str(e)}"
            )
        
        # Test user creation with weak password (should fail)
        try:
            weak_username = f'test_weak_user_{os.getpid()}'
            weak_email = f'{weak_username}@test.com'
            
            SecurityService.create_secure_user(
                username=weak_username,
                email=weak_email,
                password='weak'
            )
            
            self.log_test(
                "Weak Password Rejection",
                False,
                "Should have rejected weak password"
            )
        except ValueError:
            self.log_test(
                "Weak Password Rejection",
                True,
                "Correctly rejected weak password"
            )
        except Exception as e:
            self.log_test(
                "Weak Password Rejection",
                False,
                f"Unexpected error: {str(e)}"
            )
    
    def test_configuration_integration(self):
        """Test integration with configuration service"""
        print("\n⚙️ Testing Configuration Integration")
        
        # Test OAuth configuration warnings
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # This should trigger warnings for placeholder credentials
            try:
                # Import will trigger validation warnings
                import importlib
                import core.oauth_config
                importlib.reload(core.oauth_config)
                
                warning_messages = [str(warning.message) for warning in w]
                oauth_warnings = [msg for msg in warning_messages if 'OAuth' in msg]
                
                self.log_test(
                    "OAuth Configuration Warnings",
                    len(oauth_warnings) > 0,
                    f"Generated {len(oauth_warnings)} OAuth security warnings"
                )
                
            except Exception as e:
                self.log_test(
                    "OAuth Configuration Warnings",
                    False,
                    f"Error testing warnings: {str(e)}"
                )
    
    def test_ip_address_extraction(self):
        """Test client IP address extraction"""
        print("\n🌐 Testing IP Address Extraction")
        
        # Test normal request
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        ip = SecurityService.get_client_ip(request)
        
        self.log_test(
            "Basic IP Extraction",
            ip == '192.168.1.1',
            f"Extracted IP: {ip}"
        )
        
        # Test X-Forwarded-For header (proxy scenario)
        request_proxy = self.factory.get('/')
        request_proxy.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.195, 192.168.1.1'
        request_proxy.META['REMOTE_ADDR'] = '192.168.1.1'
        ip_proxy = SecurityService.get_client_ip(request_proxy)
        
        self.log_test(
            "Proxy IP Extraction",
            ip_proxy == '203.0.113.195',
            f"Extracted real IP through proxy: {ip_proxy}"
        )
    
    def test_authentication_wrapper(self):
        """Test secure authentication wrapper"""
        print("\n🔐 Testing Secure Authentication Wrapper")
        
        # Create a test user
        username = f'auth_test_user_{os.getpid()}'
        password = 'TestP@ssw0rd123!'
        
        try:
            test_user = User.objects.create_user(
                username=username,
                password=password,
                email=f'{username}@test.com'
            )
            
            # Test successful authentication
            request = self.factory.post('/login/')
            request.META['REMOTE_ADDR'] = '127.0.0.1'
            
            authenticated_user = SecurityService.secure_authenticate(
                request, username, password
            )
            
            self.log_test(
                "Secure Authentication Success",
                authenticated_user == test_user,
                f"Successfully authenticated: {username}"
            )
            
            # Test failed authentication
            failed_user = SecurityService.secure_authenticate(
                request, username, 'wrong_password'
            )
            
            self.log_test(
                "Secure Authentication Failure",
                failed_user is None,
                "Correctly rejected wrong password"
            )
            
        except Exception as e:
            self.log_test(
                "Secure Authentication Test",
                False,
                f"Error: {str(e)}"
            )
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Phase 2 Security Tests\n")
        
        test_suites = [
            self.test_secret_key_security,
            self.test_oauth_credential_security,
            self.test_password_strength_validation,
            self.test_login_rate_limiting,
            self.test_security_logging,
            self.test_secure_user_creation,
            self.test_configuration_integration,
            self.test_ip_address_extraction,
            self.test_authentication_wrapper,
        ]
        
        for test_suite in test_suites:
            try:
                test_suite()
            except Exception as e:
                self.log_test(
                    f"Test Suite: {test_suite.__name__}",
                    False,
                    f"Suite failed with error: {str(e)}"
                )
        
        self.print_summary()
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("🎯 Phase 2 Security Test Results")
        print("=" * 60)
        
        total_tests = self.results['passed'] + self.results['failed']
        pass_rate = (self.results['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Tests Passed: {self.results['passed']}")
        print(f"❌ Tests Failed: {self.results['failed']}")
        print(f"📊 Pass Rate: {pass_rate:.1f}%")
        
        if self.results['errors']:
            print(f"\n⚠️ Failed Tests:")
            for error in self.results['errors']:
                print(f"   - {error}")
        
        if pass_rate >= 90:
            print(f"\n🎉 Excellent! Phase 2 security is production-ready.")
        elif pass_rate >= 75:
            print(f"\n✅ Good! Phase 2 security is mostly working with minor issues.")
        else:
            print(f"\n⚠️ Issues detected. Phase 2 security needs attention before proceeding.")
        
        # Security-specific recommendations
        print(f"\n🔐 Security Recommendations:")
        if self.results['failed'] == 0:
            print("   • Set production environment variables for all OAuth providers")
            print("   • Configure proper SECRET_KEY in production environment")
            print("   • Enable security logging monitoring in production")
            print("   • Review and update password policies if needed")
        else:
            print("   • Fix failing security tests before deploying to production")
            print("   • Ensure all credentials use environment variables")
            print("   • Review security service configuration")
        
        print(f"\n📋 Next Steps:")
        if self.results['failed'] == 0:
            print("   • Phase 2 is complete - proceed to Phase 3 (Data Layer Flexibility)")
            print("   • Configure production OAuth credentials")
            print("   • Set up security monitoring and alerting")
        else:
            print("   • Address security vulnerabilities before proceeding")
            print("   • Ensure all hardcoded credentials are removed")
            print("   • Test with production-like environment variables")
        
        return pass_rate >= 75


if __name__ == '__main__':
    tester = Phase2SecurityTest()
    success = tester.run_all_tests()
    
    print(f"\n🏁 Phase 2 Security Testing Complete")
    print(f"Result: {'SUCCESS' if success else 'NEEDS ATTENTION'}")
    
    sys.exit(0 if success else 1)
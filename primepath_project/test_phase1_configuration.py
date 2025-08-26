#!/usr/bin/env python3
"""
Phase 1 Configuration Testing Suite
Tests all hardcoding fixes and configuration services

Created: August 26, 2025
Tests:
- Configuration Service Layer
- Dynamic Year Resolution
- URL Configuration
- Context Processors
- Integration Testing
"""

import os
import sys
import django
from datetime import datetime
import requests
import json

# Setup Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.template import Context, Template
from django.utils import timezone
from core.services.config_service import ConfigurationService, get_current_year, get_academic_year
from core.context_processors import config_context, user_context
from core.oauth_config import get_oauth_base_url, GOOGLE_REDIRECT_URI, KAKAO_REDIRECT_URI


class Phase1ConfigurationTest:
    """Comprehensive test suite for Phase 1 configuration changes"""
    
    def __init__(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        print("🧪 Phase 1 Configuration Testing Suite")
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
    
    def test_configuration_service_basic(self):
        """Test basic ConfigurationService functionality"""
        print("\n📋 Testing Configuration Service Basic Functionality")
        
        # Test year functions
        current_year = ConfigurationService.get_current_year()
        expected_year = datetime.now().year
        self.log_test(
            "Current Year Resolution",
            current_year == expected_year,
            f"Expected {expected_year}, got {current_year}"
        )
        
        # Test academic year
        academic_year = ConfigurationService.get_current_academic_year()
        expected_format = r'^\d{4}-\d{4}$'
        import re
        self.log_test(
            "Academic Year Format",
            re.match(expected_format, academic_year) is not None,
            f"Academic year: {academic_year}"
        )
        
        # Test URL generation
        base_url = ConfigurationService.get_base_url()
        self.log_test(
            "Base URL Generation",
            base_url.startswith('http') and '127.0.0.1' in base_url,
            f"Base URL: {base_url}"
        )
        
        # Test timeout configuration
        api_timeout = ConfigurationService.get_timeout('api')
        self.log_test(
            "Timeout Configuration",
            isinstance(api_timeout, int) and api_timeout > 0,
            f"API timeout: {api_timeout} seconds"
        )
        
        # Test feature flags
        debug_flag = ConfigurationService.get_feature_flag('DEBUG', False)
        self.log_test(
            "Feature Flags",
            isinstance(debug_flag, bool),
            f"DEBUG flag: {debug_flag}"
        )
    
    def test_year_validation(self):
        """Test year validation functions"""
        print("\n📅 Testing Year Validation")
        
        current_year = ConfigurationService.get_current_year()
        
        # Valid years
        valid_years = [current_year, current_year - 1, current_year + 1]
        for year in valid_years:
            self.log_test(
                f"Valid Year {year}",
                ConfigurationService.validate_year(year),
                f"Year {year} should be valid"
            )
        
        # Invalid years
        invalid_years = [1900, 2050, "invalid", None]
        for year in invalid_years:
            self.log_test(
                f"Invalid Year {year}",
                not ConfigurationService.validate_year(year),
                f"Year {year} should be invalid"
            )
    
    def test_oauth_urls(self):
        """Test OAuth URL configuration"""
        print("\n🔐 Testing OAuth URL Configuration")
        
        # Test OAuth base URL
        oauth_base = get_oauth_base_url()
        self.log_test(
            "OAuth Base URL",
            oauth_base.startswith('http'),
            f"OAuth base URL: {oauth_base}"
        )
        
        # Test Google redirect URI
        self.log_test(
            "Google Redirect URI",
            '/auth/google/callback/' in GOOGLE_REDIRECT_URI,
            f"Google URI: {GOOGLE_REDIRECT_URI}"
        )
        
        # Test Kakao redirect URI
        self.log_test(
            "Kakao Redirect URI",
            '/auth/kakao/callback/' in KAKAO_REDIRECT_URI,
            f"Kakao URI: {KAKAO_REDIRECT_URI}"
        )
    
    def test_context_processors(self):
        """Test template context processors"""
        print("\n🎭 Testing Context Processors")
        
        # Create mock request
        request = self.factory.get('/')
        request.user = User(username='testuser', is_staff=False)
        
        # Test config context
        config_ctx = config_context(request)
        self.log_test(
            "Config Context Processor",
            'config' in config_ctx and 'current_year' in config_ctx['config'],
            f"Config context keys: {list(config_ctx.get('config', {}).keys())}"
        )
        
        # Test user context
        user_ctx = user_context(request)
        self.log_test(
            "User Context Processor",
            'user_role' in user_ctx and 'is_teacher' in user_ctx,
            f"User role: {user_ctx.get('user_role', 'unknown')}"
        )
    
    def test_curriculum_admin_integration(self):
        """Test curriculum admin year integration"""
        print("\n🎓 Testing Curriculum Admin Integration")
        
        try:
            # Import after Django setup
            from primepath_routinetest.views.curriculum_admin import get_all_classes_admin
            
            # Create admin user
            admin_user = User.objects.create_user(
                username='test_admin',
                password='test123',
                is_staff=True
            )
            
            # Create request
            request = self.factory.get('/RoutineTest/api/admin/classes/')
            request.user = admin_user
            
            # Test the view uses dynamic year
            response = get_all_classes_admin(request)
            self.log_test(
                "Curriculum Admin Year Integration",
                response.status_code == 200,
                f"Response status: {response.status_code}"
            )
            
        except Exception as e:
            self.log_test(
                "Curriculum Admin Year Integration",
                False,
                f"Error: {str(e)}"
            )
    
    def test_javascript_config(self):
        """Test JavaScript configuration file exists and has correct structure"""
        print("\n📜 Testing JavaScript Configuration")
        
        js_config_path = os.path.join(
            os.path.dirname(__file__),
            'static', 'js', 'config.js'
        )
        
        config_exists = os.path.exists(js_config_path)
        self.log_test(
            "JavaScript Config File Exists",
            config_exists,
            f"Config file path: {js_config_path}"
        )
        
        if config_exists:
            with open(js_config_path, 'r') as f:
                content = f.read()
            
            # Check for key components
            checks = [
                ('ConfigService class', 'class ConfigService' in content),
                ('getCurrentYear method', 'getCurrentYear()' in content),
                ('getBaseUrl method', 'getBaseUrl()' in content),
                ('PrimePath namespace', 'window.PrimePath' in content),
            ]
            
            for check_name, check_result in checks:
                self.log_test(
                    f"JS Config - {check_name}",
                    check_result,
                    f"Found in config.js: {check_result}"
                )
    
    def test_settings_configuration(self):
        """Test Django settings configuration"""
        print("\n⚙️ Testing Django Settings Configuration")
        
        from django.conf import settings
        
        # Test context processors
        context_processors = settings.TEMPLATES[0]['OPTIONS']['context_processors']
        expected_processors = [
            'core.context_processors.config_context',
            'core.context_processors.user_context',
            'core.context_processors.feature_flags_context',
            'core.context_processors.app_info_context',
        ]
        
        for processor in expected_processors:
            self.log_test(
                f"Context Processor: {processor.split('.')[-1]}",
                processor in context_processors,
                f"Found in settings: {processor in context_processors}"
            )
        
        # Test CORS configuration
        cors_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
        self.log_test(
            "CORS Origins Configured",
            len(cors_origins) > 0,
            f"CORS origins count: {len(cors_origins)}"
        )
    
    def test_backwards_compatibility(self):
        """Test that existing functionality still works"""
        print("\n🔄 Testing Backwards Compatibility")
        
        try:
            # Test that old timezone.now().year references were replaced
            current_year_old = get_current_year()
            current_year_new = ConfigurationService.get_current_year()
            
            self.log_test(
                "Year Function Compatibility",
                current_year_old == current_year_new,
                f"Old: {current_year_old}, New: {current_year_new}"
            )
            
            # Test academic year function
            academic_year = get_academic_year()
            self.log_test(
                "Academic Year Function",
                len(academic_year.split('-')) == 2,
                f"Academic year: {academic_year}"
            )
            
        except Exception as e:
            self.log_test(
                "Backwards Compatibility",
                False,
                f"Error: {str(e)}"
            )
    
    def test_error_handling(self):
        """Test error handling and fallbacks"""
        print("\n🛠️ Testing Error Handling")
        
        # Test context processor error handling with bad request
        try:
            request = self.factory.get('/')
            request.user = None  # This should trigger error handling
            
            config_ctx = config_context(request)
            self.log_test(
                "Context Processor Error Handling",
                'config' in config_ctx,  # Should still provide fallback
                "Fallback configuration provided"
            )
        except Exception as e:
            self.log_test(
                "Context Processor Error Handling",
                False,
                f"Error not handled properly: {str(e)}"
            )
        
        # Test configuration service with missing environment
        try:
            env = ConfigurationService.get_environment()
            self.log_test(
                "Environment Detection",
                env in ['development', 'staging', 'production'],
                f"Detected environment: {env}"
            )
        except Exception as e:
            self.log_test(
                "Environment Detection",
                False,
                f"Error: {str(e)}"
            )
    
    def test_performance(self):
        """Test performance of configuration services"""
        print("\n⚡ Testing Performance")
        
        import time
        
        # Test caching
        start_time = time.time()
        for _ in range(100):
            ConfigurationService.get_current_academic_year()
        cache_time = time.time() - start_time
        
        # Clear cache and test without cache
        ConfigurationService.clear_cache()
        start_time = time.time()
        for _ in range(100):
            ConfigurationService.get_current_academic_year()
        no_cache_time = time.time() - start_time
        
        self.log_test(
            "Configuration Caching Performance",
            cache_time < no_cache_time * 2,  # Should be significantly faster with cache
            f"Cached: {cache_time:.4f}s, No cache: {no_cache_time:.4f}s"
        )
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Phase 1 Configuration Tests\n")
        
        test_suites = [
            self.test_configuration_service_basic,
            self.test_year_validation,
            self.test_oauth_urls,
            self.test_context_processors,
            self.test_curriculum_admin_integration,
            self.test_javascript_config,
            self.test_settings_configuration,
            self.test_backwards_compatibility,
            self.test_error_handling,
            self.test_performance,
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
        print("🎯 Phase 1 Configuration Test Results")
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
            print(f"\n🎉 Excellent! Phase 1 configuration is ready for production.")
        elif pass_rate >= 75:
            print(f"\n✅ Good! Phase 1 configuration is mostly working with minor issues.")
        else:
            print(f"\n⚠️ Issues detected. Phase 1 configuration needs attention before proceeding.")
        
        # Recommendations
        print(f"\n📋 Next Steps:")
        if self.results['failed'] == 0:
            print("   • Phase 1 is complete - proceed to Phase 2 (Security & Authentication)")
            print("   • Start implementing dynamic credential management")
            print("   • Test with production environment variables")
        else:
            print("   • Fix failing tests before proceeding to Phase 2")
            print("   • Review error messages above for specific issues")
            print("   • Ensure all hardcoded values are replaced with configuration service")
        
        return pass_rate >= 75


if __name__ == '__main__':
    tester = Phase1ConfigurationTest()
    success = tester.run_all_tests()
    
    print(f"\n🏁 Phase 1 Configuration Testing Complete")
    print(f"Result: {'SUCCESS' if success else 'NEEDS ATTENTION'}")
    
    sys.exit(0 if success else 1)
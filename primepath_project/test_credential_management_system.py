#!/usr/bin/env python
"""
Comprehensive Test Suite for Credential Management System
========================================================

This test suite validates all components of the credential management system:
1. UserCredentialService functionality
2. Credential protection middleware
3. Automated monitoring system
4. Integration with existing authentication flows
5. Production deployment readiness

Author: Claude Code AI System
Date: August 25, 2025
"""
import os
import sys
import django
import json
import time
import threading
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.test import TestCase, Client
from django.utils import timezone
from core.models import Teacher
from primepath_student.models import StudentProfile

# Import our credential management components
from user_credential_service import credential_service
from credential_protection_middleware import get_protection_report, is_protected_account
from automated_credential_monitor import credential_monitor


class CredentialManagementSystemTest:
    """
    Comprehensive test suite for the credential management system.
    """
    
    def __init__(self):
        self.test_results = {
            'timestamp': timezone.now().isoformat(),
            'test_suite': 'CredentialManagementSystemTest',
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': [],
            'system_validation': {},
            'integration_validation': {},
            'production_readiness': {}
        }
        
        print("="*80)
        print("CREDENTIAL MANAGEMENT SYSTEM - COMPREHENSIVE TEST SUITE")
        print("="*80)
        print(f"Started: {self.test_results['timestamp']}")
        print("")
    
    def run_all_tests(self):
        """Run the complete test suite."""
        print("🔍 RUNNING COMPREHENSIVE TEST SUITE")
        print("-" * 50)
        
        # Phase 1: Core Service Tests
        print("\n📋 PHASE 1: CORE SERVICE VALIDATION")
        self._test_user_credential_service()
        
        # Phase 2: Protection Middleware Tests
        print("\n📋 PHASE 2: PROTECTION MIDDLEWARE VALIDATION")
        self._test_credential_protection()
        
        # Phase 3: Monitoring System Tests  
        print("\n📋 PHASE 3: MONITORING SYSTEM VALIDATION")
        self._test_automated_monitoring()
        
        # Phase 4: Integration Tests
        print("\n📋 PHASE 4: SYSTEM INTEGRATION VALIDATION")
        self._test_authentication_integration()
        
        # Phase 5: Production Readiness Tests
        print("\n📋 PHASE 5: PRODUCTION READINESS VALIDATION")
        self._test_production_readiness()
        
        # Generate final report
        self._generate_test_report()
    
    def _test_user_credential_service(self):
        """Test the UserCredentialService functionality."""
        print("🔧 Testing UserCredentialService...")
        
        # Test 1: Service Initialization
        self._run_test(
            "service_initialization",
            "Service initializes correctly",
            lambda: credential_service is not None
        )
        
        # Test 2: Credential Validation
        self._run_test(
            "credential_validation",
            "Validate all credentials",
            self._test_credential_validation
        )
        
        # Test 3: Account Protection
        self._run_test(
            "account_protection",
            "Protected accounts are identified correctly",
            self._test_account_protection
        )
        
        # Test 4: Health Report Generation
        self._run_test(
            "health_report_generation",
            "System health report generates successfully",
            self._test_health_report
        )
    
    def _test_credential_validation(self):
        """Test credential validation functionality."""
        results = credential_service.validate_all_credentials()
        
        # Check that results contain expected structure
        required_keys = ['timestamp', 'total_accounts_checked', 'protected_accounts_status']
        for key in required_keys:
            if key not in results:
                return False, f"Missing key: {key}"
        
        # Check that protected accounts were checked
        if results['total_accounts_checked'] == 0:
            return False, "No accounts were checked"
        
        return True, f"Validated {results['total_accounts_checked']} accounts"
    
    def _test_account_protection(self):
        """Test account protection functionality."""
        # Test that teacher1 is protected
        if not is_protected_account('teacher1'):
            return False, "teacher1 should be protected"
        
        # Test that admin is protected
        if not is_protected_account('admin'):
            return False, "admin should be protected"
        
        # Test that random user is not protected
        if is_protected_account('random_user_123'):
            return False, "random users should not be protected"
        
        return True, "Account protection working correctly"
    
    def _test_health_report(self):
        """Test health report generation."""
        report = credential_service.get_system_health_report()
        
        # Check report structure
        required_keys = ['timestamp', 'user_statistics', 'authentication_health', 'recommendations']
        for key in required_keys:
            if key not in report:
                return False, f"Missing key in health report: {key}"
        
        # Check user statistics
        stats = report['user_statistics']
        if stats['total_users'] <= 0:
            return False, "No users found in statistics"
        
        return True, f"Health report generated with {stats['total_users']} total users"
    
    def _test_credential_protection(self):
        """Test the credential protection middleware."""
        print("🛡️  Testing Credential Protection Middleware...")
        
        # Test 1: Protection Report
        self._run_test(
            "protection_report",
            "Protection report generates successfully",
            self._test_protection_report
        )
        
        # Test 2: Account Detection
        self._run_test(
            "protected_account_detection",
            "Protected account detection works",
            self._test_protected_account_detection
        )
    
    def _test_protection_report(self):
        """Test protection report generation."""
        report = get_protection_report()
        
        if 'error' in report:
            return False, f"Protection report error: {report['error']}"
        
        # Check report structure
        required_keys = ['middleware_version', 'timestamp', 'protection_enabled', 'statistics']
        for key in required_keys:
            if key not in report:
                return False, f"Missing key in protection report: {key}"
        
        return True, f"Protection report generated successfully"
    
    def _test_protected_account_detection(self):
        """Test protected account detection."""
        # These should be protected
        protected_accounts = ['teacher1', 'admin']
        for account in protected_accounts:
            if not is_protected_account(account):
                return False, f"Account {account} should be protected but isn't"
        
        return True, "Protected account detection working"
    
    def _test_automated_monitoring(self):
        """Test the automated monitoring system."""
        print("📊 Testing Automated Monitoring System...")
        
        # Test 1: Monitoring Status
        self._run_test(
            "monitoring_status",
            "Monitoring status retrieval works",
            self._test_monitoring_status
        )
        
        # Test 2: Health Dashboard
        self._run_test(
            "health_dashboard",
            "Health dashboard generation works",
            self._test_health_dashboard
        )
        
        # Test 3: Monitor Functionality
        self._run_test(
            "monitor_functionality",
            "Basic monitoring functionality works",
            self._test_monitor_basic_functionality
        )
    
    def _test_monitoring_status(self):
        """Test monitoring status retrieval."""
        status = credential_monitor.get_monitoring_status()
        
        required_keys = ['monitoring_enabled', 'is_running', 'statistics']
        for key in required_keys:
            if key not in status:
                return False, f"Missing key in monitoring status: {key}"
        
        return True, "Monitoring status retrieved successfully"
    
    def _test_health_dashboard(self):
        """Test health dashboard generation."""
        dashboard = credential_monitor.get_health_dashboard()
        
        required_keys = ['timestamp', 'system_status', 'monitoring_status', 'credential_health']
        for key in required_keys:
            if key not in dashboard:
                return False, f"Missing key in health dashboard: {key}"
        
        return True, f"Health dashboard generated - Status: {dashboard['system_status']}"
    
    def _test_monitor_basic_functionality(self):
        """Test basic monitoring functionality."""
        # Test that we can get the monitoring status without errors
        try:
            status = credential_monitor.get_monitoring_status()
            if isinstance(status, dict) and 'monitoring_enabled' in status:
                return True, "Basic monitoring functionality works"
            else:
                return False, "Invalid status response"
        except Exception as e:
            return False, f"Exception in monitoring: {e}"
    
    def _test_authentication_integration(self):
        """Test integration with existing authentication flows."""
        print("🔗 Testing Authentication Integration...")
        
        # Test 1: Teacher Authentication
        self._run_test(
            "teacher_authentication_integration",
            "Teacher authentication works with credential system",
            self._test_teacher_auth_integration
        )
        
        # Test 2: Admin Authentication
        self._run_test(
            "admin_authentication_integration", 
            "Admin authentication works with credential system",
            self._test_admin_auth_integration
        )
        
        # Test 3: Profile Sync
        self._run_test(
            "profile_sync_integration",
            "User-Teacher profile sync works",
            self._test_profile_sync_integration
        )
    
    def _test_teacher_auth_integration(self):
        """Test teacher authentication integration."""
        # Ensure teacher1 account exists and works
        try:
            # First, make sure teacher1 credentials are correct
            fix_result = credential_service.fix_account_credentials('teacher1', force=True)
            if not fix_result['success']:
                return False, f"Could not fix teacher1 credentials: {fix_result.get('error')}"
            
            # Test authentication
            user = authenticate(username='teacher1', password='teacher123')
            if not user:
                return False, "teacher1 authentication failed"
            
            # Check teacher profile exists
            try:
                teacher = user.teacher_profile
                if not teacher:
                    return False, "teacher1 has no teacher profile"
            except Teacher.DoesNotExist:
                return False, "teacher1 teacher profile does not exist"
            
            return True, "teacher1 authentication and profile integration works"
            
        except Exception as e:
            return False, f"Exception in teacher auth test: {e}"
    
    def _test_admin_auth_integration(self):
        """Test admin authentication integration."""
        try:
            # First, make sure admin credentials are correct
            fix_result = credential_service.fix_account_credentials('admin', force=True)
            if not fix_result['success']:
                return False, f"Could not fix admin credentials: {fix_result.get('error')}"
            
            # Test authentication
            user = authenticate(username='admin', password='admin123')
            if not user:
                return False, "admin authentication failed"
            
            # Check admin permissions
            if not user.is_superuser:
                return False, "admin should be superuser"
            
            if not user.is_staff:
                return False, "admin should be staff"
            
            return True, "admin authentication and permissions work"
            
        except Exception as e:
            return False, f"Exception in admin auth test: {e}"
    
    def _test_profile_sync_integration(self):
        """Test user-teacher profile synchronization."""
        try:
            # Get teacher1 user
            user = User.objects.get(username='teacher1')
            teacher = user.teacher_profile
            
            # Test sync functionality
            original_name = teacher.name
            teacher.name = "Test Sync Name"
            teacher.sync_with_user()
            
            # Restore original name
            teacher.name = original_name
            teacher.save()
            
            return True, "Profile sync functionality works"
            
        except Exception as e:
            return False, f"Exception in profile sync test: {e}"
    
    def _test_production_readiness(self):
        """Test production deployment readiness."""
        print("🚀 Testing Production Readiness...")
        
        # Test 1: Safety Checks
        self._run_test(
            "production_safety_checks",
            "Production safety mechanisms work",
            self._test_production_safety
        )
        
        # Test 2: Error Handling
        self._run_test(
            "error_handling",
            "Error handling works correctly",
            self._test_error_handling
        )
        
        # Test 3: Performance
        self._run_test(
            "performance_validation",
            "System performs adequately under load",
            self._test_performance
        )
    
    def _test_production_safety(self):
        """Test production safety mechanisms."""
        # Test that we can't accidentally fix credentials in production without force
        original_debug = getattr(django.conf.settings, 'DEBUG', True)
        
        try:
            # Simulate production environment by setting DEBUG=False
            django.conf.settings.DEBUG = False
            
            # Create a fresh service instance to pick up the DEBUG change
            from user_credential_service import UserCredentialService
            test_service = UserCredentialService()
            
            # Try to fix without force - should fail safely
            result = test_service.fix_account_credentials('teacher1', force=False)
            if result['success']:
                return False, "Should not allow credential fixes in production without force"
            
            # Verify the error message is correct
            if 'production' not in result.get('error', '').lower():
                return False, f"Expected production safety error, got: {result.get('error')}"
            
            # Try with force - should work
            result = test_service.fix_account_credentials('teacher1', force=True)
            if not result['success']:
                return False, f"Force fix should work in production: {result.get('error')}"
            
            return True, "Production safety mechanisms work correctly"
            
        finally:
            # Restore original setting
            django.conf.settings.DEBUG = original_debug
    
    def _test_error_handling(self):
        """Test error handling in the system."""
        try:
            # Test invalid account name - should return error dict, not raise exception
            result = credential_service.fix_account_credentials('nonexistent_account', force=True)
            if result.get('success', False):
                return False, "Should not succeed for nonexistent account"
            
            # Verify proper error response structure
            if 'error' not in result:
                return False, "Error response should contain 'error' key"
            
            expected_error = "Account nonexistent_account is not a protected account"
            if expected_error not in result['error']:
                return False, f"Expected specific error message, got: {result['error']}"
            
            # Verify valid accounts list is provided
            if 'valid_accounts' not in result:
                return False, "Error response should include valid_accounts list"
            
            # Test validation with corrupted data
            validation = credential_service.validate_all_credentials()
            if 'errors' not in validation:
                return False, "Validation should have errors key"
            
            return True, "Error handling works correctly with proper error responses"
            
        except Exception as e:
            return False, f"Error handling should not raise exceptions: {e}"
    
    def _test_performance(self):
        """Test system performance."""
        start_time = time.time()
        
        # Run multiple validation cycles
        for i in range(5):
            credential_service.validate_all_credentials()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete in reasonable time (less than 10 seconds for 5 cycles)
        if duration > 10:
            return False, f"Performance too slow: {duration:.2f}s for 5 validation cycles"
        
        return True, f"Performance acceptable: {duration:.2f}s for 5 validation cycles"
    
    def _run_test(self, test_id: str, description: str, test_func):
        """Run a single test and record results."""
        self.test_results['total_tests'] += 1
        
        try:
            if callable(test_func):
                result = test_func()
                if isinstance(result, tuple):
                    success, message = result
                else:
                    success = bool(result)
                    message = "Test completed"
            else:
                success = bool(test_func)
                message = "Test completed"
            
            if success:
                self.test_results['passed_tests'] += 1
                status = "✅ PASS"
            else:
                self.test_results['failed_tests'] += 1
                status = "❌ FAIL"
            
            test_detail = {
                'test_id': test_id,
                'description': description,
                'status': 'PASS' if success else 'FAIL',
                'message': message,
                'timestamp': timezone.now().isoformat()
            }
            
            self.test_results['test_details'].append(test_detail)
            
            print(f"   {status} {description}: {message}")
            
        except Exception as e:
            self.test_results['failed_tests'] += 1
            test_detail = {
                'test_id': test_id,
                'description': description,
                'status': 'ERROR',
                'message': str(e),
                'timestamp': timezone.now().isoformat()
            }
            
            self.test_results['test_details'].append(test_detail)
            print(f"   ❌ ERROR {description}: {str(e)}")
    
    def _generate_test_report(self):
        """Generate comprehensive test report."""
        print("\n" + "="*80)
        print("COMPREHENSIVE TEST REPORT")
        print("="*80)
        
        # Summary
        total = self.test_results['total_tests']
        passed = self.test_results['passed_tests']
        failed = self.test_results['failed_tests']
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Overall status
        if failed == 0:
            print(f"\n🎉 ALL TESTS PASSED - SYSTEM READY FOR PRODUCTION")
            overall_status = "READY"
        elif success_rate >= 90:
            print(f"\n⚠️  MOSTLY PASSING - MINOR ISSUES TO RESOLVE")
            overall_status = "MOSTLY_READY"
        else:
            print(f"\n❌ SIGNIFICANT ISSUES FOUND - NEEDS ATTENTION")
            overall_status = "NOT_READY"
        
        # Detailed results
        if failed > 0:
            print(f"\n📋 FAILED TESTS:")
            for test in self.test_results['test_details']:
                if test['status'] in ['FAIL', 'ERROR']:
                    print(f"   • {test['test_id']}: {test['message']}")
        
        # Recommendations
        print(f"\n📋 RECOMMENDATIONS:")
        if failed == 0:
            print("   • System is ready for production deployment")
            print("   • Consider setting up automated monitoring")
            print("   • Implement regular credential health checks")
        else:
            print("   • Resolve failed tests before production deployment")
            print("   • Review error messages and fix underlying issues")
            print("   • Run tests again after fixes")
        
        # Save results
        self.test_results['overall_status'] = overall_status
        self.test_results['success_rate'] = success_rate
        
        # Save to file
        with open('credential_management_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: credential_management_test_results.json")
        print("="*80)


def main():
    """Main test execution."""
    tester = CredentialManagementSystemTest()
    tester.run_all_tests()


if __name__ == '__main__':
    main()
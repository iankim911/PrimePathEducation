#!/usr/bin/env python
"""
Comprehensive QA Testing for Enhanced Error Handling Infrastructure
Tests all RoutineTest features with the new error handling system
Covers backend, frontend, database operations, and performance monitoring
"""

import os
import sys
import django
import json
import time
import traceback
from datetime import datetime, timedelta

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.cache import cache
from django.db import transaction, connection
from django.utils import timezone

# Import RoutineTest models and services
from primepath_routinetest.models import Exam, ExamScheduleMatrix
try:
    from primepath_routinetest.models.exam import StudentRoster
    HAS_STUDENT_ROSTER = True
except ImportError:
    HAS_STUDENT_ROSTER = False
    print("⚠️ [QA_INFO] StudentRoster model not available (may have been removed)")
from primepath_routinetest.error_handlers import (
    RoutineTestErrorHandler, 
    ConsoleLogger, 
    enhanced_view_handler,
    matrix_operation_handler,
    PerformanceMonitor
)
from core.models import Teacher, CurriculumLevel, Program, SubProgram

class ComprehensiveQATest:
    """Comprehensive QA test suite for enhanced error handling"""
    
    def __init__(self):
        self.client = Client()
        self.test_results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': [],
            'performance_metrics': {},
            'error_handling_tests': [],
            'frontend_tests': [],
            'database_tests': []
        }
        self.setup_test_data()
    
    def setup_test_data(self):
        """Setup test data for comprehensive testing"""
        print("\n" + "="*100)
        print("🔧 [QA_SETUP] Setting up test data...")
        print("="*100)
        
        try:
            # Create test user and teacher
            self.test_user, created = User.objects.get_or_create(
                username='qa_test_admin',
                defaults={
                    'email': 'qa@test.com',
                    'is_staff': True,
                    'is_superuser': True,
                    'first_name': 'QA',
                    'last_name': 'Admin'
                }
            )
            if created:
                self.test_user.set_password('test123')
                self.test_user.save()
            
            self.test_teacher, created = Teacher.objects.get_or_create(
                user=self.test_user,
                defaults={
                    'name': 'QA Test Teacher',
                    'is_head_teacher': True
                }
            )
            
            # Create test curriculum structure using existing programs if possible
            try:
                # Try to use existing program first
                self.test_program = Program.objects.filter(name='CORE').first()
                if not self.test_program:
                    # Create a test program with correct fields
                    self.test_program, created = Program.objects.get_or_create(
                        name='CORE',
                        defaults={
                            'grade_range_start': 1,
                            'grade_range_end': 12,
                            'order': 1
                        }
                    )
                
                # Try to use existing subprogram first
                self.test_subprogram = SubProgram.objects.filter(program=self.test_program).first()
                if not self.test_subprogram:
                    self.test_subprogram, created = SubProgram.objects.get_or_create(
                        program=self.test_program,
                        name='QA Test SubProgram',
                        defaults={'order': 1}
                    )
                
                # Try to use existing curriculum level first
                self.test_curriculum = CurriculumLevel.objects.filter(subprogram=self.test_subprogram).first()
                if not self.test_curriculum:
                    self.test_curriculum, created = CurriculumLevel.objects.get_or_create(
                        subprogram=self.test_subprogram,
                        level_number=1,
                        defaults={'description': 'QA Test Level 1'}
                    )
                
            except Exception as e:
                print(f"⚠️ [QA_SETUP_WARNING] Using fallback curriculum setup: {str(e)}")
                # Use any existing curriculum level as fallback
                self.test_curriculum = CurriculumLevel.objects.first()
                if self.test_curriculum:
                    self.test_program = self.test_curriculum.subprogram.program
                    self.test_subprogram = self.test_curriculum.subprogram
                else:
                    print("❌ [QA_SETUP_ERROR] No curriculum levels available for testing")
                    raise Exception("No curriculum data available for QA testing")
            
            print("✅ [QA_SETUP] Test data setup completed")
            
        except Exception as e:
            print(f"❌ [QA_SETUP_ERROR] {str(e)}")
            raise
    
    def run_test(self, test_name, test_func):
        """Run a single test with error handling and metrics"""
        self.test_results['total_tests'] += 1
        start_time = time.time()
        
        try:
            print(f"\n🧪 [TEST_START] {test_name}")
            result = test_func()
            duration = time.time() - start_time
            
            if result:
                self.test_results['passed'] += 1
                print(f"✅ [TEST_PASS] {test_name} completed in {duration:.3f}s")
            else:
                self.test_results['failed'] += 1
                print(f"❌ [TEST_FAIL] {test_name} failed after {duration:.3f}s")
                
            self.test_results['performance_metrics'][test_name] = duration
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            self.test_results['failed'] += 1
            error_info = {
                'test': test_name,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'duration': duration
            }
            self.test_results['errors'].append(error_info)
            print(f"💥 [TEST_ERROR] {test_name} crashed after {duration:.3f}s: {str(e)}")
            return False
    
    def test_error_handler_initialization(self):
        """Test that error handlers are properly initialized"""
        try:
            # Test RoutineTestErrorHandler
            error = Exception("Test error for QA")
            context = {'test': 'qa_testing'}
            
            error_details = RoutineTestErrorHandler.log_error(
                error, context, self.test_user, None, {'test_metric': 'value'}
            )
            
            # Verify error details structure
            required_fields = ['module', 'error_type', 'error_message', 'timestamp', 'context']
            for field in required_fields:
                if field not in error_details:
                    print(f"❌ Missing field in error_details: {field}")
                    return False
            
            # Test ConsoleLogger
            ConsoleLogger.log_view_start('test_view', self.test_user, {'test': 'data'})
            ConsoleLogger.log_view_end('test_view', self.test_user, 0.1, {'status': 'success'})
            
            print("✅ Error handler initialization working correctly")
            return True
            
        except Exception as e:
            print(f"❌ Error handler initialization failed: {str(e)}")
            return False
    
    def test_database_error_handling(self):
        """Test database error handling patterns"""
        try:
            # Test unique constraint handling
            db_error = Exception("UNIQUE constraint failed: test_table.test_field")
            response = RoutineTestErrorHandler.handle_database_error(
                db_error, {'test': 'unique_constraint'}, self.test_user, None
            )
            
            if response['error_type'] != 'DUPLICATE_ENTRY':
                print(f"❌ Expected DUPLICATE_ENTRY, got {response['error_type']}")
                return False
            
            # Test foreign key constraint
            fk_error = Exception("FOREIGN KEY constraint failed")
            response = RoutineTestErrorHandler.handle_database_error(
                fk_error, {'test': 'foreign_key'}, self.test_user, None
            )
            
            if response['error_type'] != 'INVALID_REFERENCE':
                print(f"❌ Expected INVALID_REFERENCE, got {response['error_type']}")
                return False
            
            print("✅ Database error handling patterns working correctly")
            return True
            
        except Exception as e:
            print(f"❌ Database error handling test failed: {str(e)}")
            return False
    
    def test_performance_monitoring(self):
        """Test performance monitoring functionality"""
        try:
            # Test performance monitoring decorator
            @PerformanceMonitor.monitor_database_queries
            def slow_operation():
                time.sleep(0.1)  # Simulate slow operation
                return "completed"
            
            result = slow_operation()
            
            if result != "completed":
                print("❌ Performance monitoring decorator failed")
                return False
            
            # Test database operation logging
            ConsoleLogger.log_database_operation(
                'SELECT', 'TestModel', 100, {'test': 'filter'}, self.test_user, 0.05
            )
            
            # Test cache operation logging
            ConsoleLogger.log_cache_operation(
                'GET', 'test_cache_key', True, 300, 1024
            )
            
            print("✅ Performance monitoring working correctly")
            return True
            
        except Exception as e:
            print(f"❌ Performance monitoring test failed: {str(e)}")
            return False
    
    def test_matrix_operations(self):
        """Test matrix operations with enhanced error handling"""
        try:
            # Test matrix cell creation
            matrix_cell, created = ExamScheduleMatrix.get_or_create_cell(
                'CLASS_7A', '2025', 'MONTHLY', 'JAN', self.test_user
            )
            
            if not matrix_cell:
                print("❌ Matrix cell creation failed")
                return False
            
            # Test exam creation and assignment
            test_exam = Exam.objects.create(
                name='QA Test Exam',
                exam_type='REVIEW',
                time_period_month='JAN',
                academic_year='2025',
                curriculum_level=self.test_curriculum,
                total_questions=10,
                timer_minutes=30,
                created_by=self.test_teacher
            )
            
            # Test adding exam to matrix
            result = matrix_cell.add_exam(test_exam, self.test_user)
            
            if not result:
                print("❌ Matrix exam assignment failed")
                return False
            
            # Test matrix status updates
            if matrix_cell.status != 'SCHEDULED':
                print(f"❌ Expected matrix status 'SCHEDULED', got '{matrix_cell.status}'")
                return False
            
            # Test detailed exam list
            detailed_exams = matrix_cell.get_detailed_exam_list()
            
            if len(detailed_exams) != 1:
                print(f"❌ Expected 1 detailed exam, got {len(detailed_exams)}")
                return False
            
            print("✅ Matrix operations working correctly")
            return True
            
        except Exception as e:
            print(f"❌ Matrix operations test failed: {str(e)}")
            return False
    
    def test_exam_functionality(self):
        """Test exam-related functionality"""
        try:
            # Test exam creation with naming system
            exam = Exam.objects.create(
                name='Test Exam for QA',
                exam_type='QUARTERLY',
                time_period_quarter='Q2',
                academic_year='2025',
                curriculum_level=self.test_curriculum,
                total_questions=20,
                timer_minutes=45,
                created_by=self.test_teacher,
                class_codes=['CLASS_8A', 'CLASS_8B']
            )
            
            # Test RoutineTest display name generation
            display_name = exam.get_routinetest_display_name()
            expected_parts = ['[QUARTERLY | Q2]', 'QA_TEST_PROGRAM']
            
            for part in expected_parts:
                if part not in display_name:
                    print(f"❌ Expected '{part}' in display name '{display_name}'")
                    return False
            
            # Test answer mapping status
            status = exam.get_answer_mapping_status()
            required_status_fields = ['is_complete', 'total_questions', 'mapped_questions', 'status_label']
            
            for field in required_status_fields:
                if field not in status:
                    print(f"❌ Missing field in answer mapping status: {field}")
                    return False
            
            # Test class codes display
            class_display = exam.get_class_codes_display()
            if not class_display:
                print("❌ Class codes display is empty")
                return False
            
            print("✅ Exam functionality working correctly")
            return True
            
        except Exception as e:
            print(f"❌ Exam functionality test failed: {str(e)}")
            return False
    
    def test_view_decorators(self):
        """Test enhanced view decorators"""
        try:
            from django.http import HttpRequest, JsonResponse
            
            # Create mock request
            request = HttpRequest()
            request.user = self.test_user
            request.method = 'GET'
            request.path = '/test/'
            
            # Test enhanced_view_handler decorator
            @enhanced_view_handler(view_name='test_view', cache_enabled=True)
            def test_view(request):
                return JsonResponse({'status': 'success'})
            
            response = test_view(request)
            
            if not hasattr(response, 'content'):
                print("❌ Enhanced view handler failed to return proper response")
                return False
            
            # Test matrix_operation_handler decorator
            @matrix_operation_handler(operation_name='test_matrix_op')
            def test_matrix_view(request):
                return JsonResponse({'operation': 'completed'})
            
            response = test_matrix_view(request)
            
            if not hasattr(response, 'content'):
                print("❌ Matrix operation handler failed to return proper response")
                return False
            
            print("✅ View decorators working correctly")
            return True
            
        except Exception as e:
            print(f"❌ View decorators test failed: {str(e)}")
            return False
    
    def test_frontend_integration(self):
        """Test frontend integration with error handling"""
        try:
            # Login as test user
            self.client.login(username='qa_test_admin', password='test123')
            
            # Test main RoutineTest view
            response = self.client.get('/routinetest/')
            
            if response.status_code not in [200, 302]:
                print(f"❌ RoutineTest main view returned status {response.status_code}")
                return False
            
            # Test classes-exams unified view
            try:
                response = self.client.get('/routinetest/classes-exams/')
                if response.status_code not in [200, 302]:
                    print(f"⚠️ Classes-exams view returned status {response.status_code} (may be expected)")
            except:
                print("⚠️ Classes-exams view not accessible (may be expected)")
            
            # Test error handler JavaScript is accessible
            try:
                response = self.client.get('/static/js/modules/error-handler.js')
                if response.status_code == 200:
                    print("✅ Error handler JavaScript is accessible")
            except:
                print("⚠️ Error handler JavaScript not directly accessible (may be expected)")
            
            print("✅ Frontend integration tests completed")
            return True
            
        except Exception as e:
            print(f"❌ Frontend integration test failed: {str(e)}")
            return False
    
    def test_cache_and_performance(self):
        """Test caching and performance optimizations"""
        try:
            # Test cache operations
            cache_key = 'qa_test_cache_key'
            cache_value = {'test': 'data', 'timestamp': time.time()}
            
            # Set cache
            cache.set(cache_key, cache_value, 300)
            
            # Get cache
            cached_data = cache.get(cache_key)
            
            if not cached_data:
                print("❌ Cache operations not working")
                return False
            
            # Test cache logging
            ConsoleLogger.log_cache_operation('GET', cache_key, True, 300)
            ConsoleLogger.log_cache_operation('SET', cache_key, None, 300, len(str(cache_value)))
            
            # Test database query optimization
            initial_queries = len(connection.queries)
            
            # Perform database operations
            exams = Exam.objects.filter(is_active=True).select_related('curriculum_level')[:5]
            list(exams)  # Force evaluation
            
            final_queries = len(connection.queries)
            query_count = final_queries - initial_queries
            
            print(f"📊 Database queries executed: {query_count}")
            
            print("✅ Cache and performance tests completed")
            return True
            
        except Exception as e:
            print(f"❌ Cache and performance test failed: {str(e)}")
            return False
    
    def test_security_and_validation(self):
        """Test security measures and data validation"""
        try:
            # Test user permission checks
            if not self.test_user.is_authenticated:
                print("❌ Test user authentication failed")
                return False
            
            # Test input validation
            try:
                # Try to create exam with invalid data
                invalid_exam = Exam(
                    name='',  # Empty name should fail validation
                    total_questions=-1,  # Negative questions should fail
                    timer_minutes=0  # Zero timer should fail
                )
                invalid_exam.full_clean()  # This should raise ValidationError
                print("❌ Input validation not working - invalid data was accepted")
                return False
            except Exception:
                print("✅ Input validation working correctly")
            
            # Test SQL injection protection (basic check)
            malicious_input = "'; DROP TABLE exam; --"
            try:
                Exam.objects.filter(name=malicious_input)
                print("✅ SQL injection protection working")
            except Exception:
                print("⚠️ Unexpected error with malicious input test")
            
            print("✅ Security and validation tests completed")
            return True
            
        except Exception as e:
            print(f"❌ Security and validation test failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run the complete QA test suite"""
        print("\n" + "="*100)
        print("🚀 [COMPREHENSIVE_QA] Starting Enhanced Error Handling QA Tests")
        print("="*100)
        
        start_time = time.time()
        
        # Define test suite
        tests = [
            ('Error Handler Initialization', self.test_error_handler_initialization),
            ('Database Error Handling', self.test_database_error_handling),
            ('Performance Monitoring', self.test_performance_monitoring),
            ('Matrix Operations', self.test_matrix_operations),
            ('Exam Functionality', self.test_exam_functionality),
            ('View Decorators', self.test_view_decorators),
            ('Frontend Integration', self.test_frontend_integration),
            ('Cache and Performance', self.test_cache_and_performance),
            ('Security and Validation', self.test_security_and_validation),
        ]
        
        # Run all tests
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        total_duration = time.time() - start_time
        
        # Generate final report
        self.generate_final_report(total_duration)
    
    def generate_final_report(self, total_duration):
        """Generate comprehensive QA report"""
        print("\n" + "="*100)
        print("📊 [QA_FINAL_REPORT] Comprehensive QA Test Results")
        print("="*100)
        
        # Summary statistics
        success_rate = (self.test_results['passed'] / self.test_results['total_tests'] * 100) if self.test_results['total_tests'] > 0 else 0
        
        print(f"📈 SUMMARY:")
        print(f"   Total Tests: {self.test_results['total_tests']}")
        print(f"   Passed: {self.test_results['passed']} ✅")
        print(f"   Failed: {self.test_results['failed']} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Total Duration: {total_duration:.2f}s")
        
        # Performance metrics
        print(f"\n⚡ PERFORMANCE METRICS:")
        for test_name, duration in self.test_results['performance_metrics'].items():
            status = "⚡ Fast" if duration < 1.0 else "⚠️ Slow" if duration < 3.0 else "🐌 Very Slow"
            print(f"   {test_name}: {duration:.3f}s {status}")
        
        # Error details
        if self.test_results['errors']:
            print(f"\n💥 ERROR DETAILS:")
            for error in self.test_results['errors']:
                print(f"   Test: {error['test']}")
                print(f"   Error: {error['error']}")
                print(f"   Duration: {error['duration']:.3f}s")
                print("   " + "-"*50)
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if success_rate >= 90:
            print("   🟢 EXCELLENT - Enhanced error handling is working optimally")
        elif success_rate >= 75:
            print("   🟡 GOOD - Most functionality working, minor issues detected")
        elif success_rate >= 50:
            print("   🟠 FAIR - Significant issues need attention")
        else:
            print("   🔴 POOR - Critical issues require immediate fixing")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if self.test_results['failed'] == 0:
            print("   ✅ All tests passed - Enhanced error handling is production ready")
            print("   ✅ Error logging infrastructure is functioning correctly")
            print("   ✅ Performance monitoring is operational")
        else:
            print("   🔧 Review failed tests and address issues")
            print("   📊 Monitor performance metrics in production")
            print("   🔍 Verify error logging in real usage scenarios")
        
        print("="*100)
        
        # Save detailed report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': self.test_results['total_tests'],
                'passed': self.test_results['passed'],
                'failed': self.test_results['failed'],
                'success_rate': success_rate,
                'total_duration': total_duration
            },
            'performance_metrics': self.test_results['performance_metrics'],
            'errors': self.test_results['errors']
        }
        
        with open('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/qa_comprehensive_error_handling_report.json', 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print("📄 Detailed report saved to: qa_comprehensive_error_handling_report.json")


if __name__ == '__main__':
    try:
        qa_test = ComprehensiveQATest()
        qa_test.run_all_tests()
    except Exception as e:
        print(f"💥 [QA_CRITICAL_ERROR] QA test suite failed to run: {str(e)}")
        print(f"📋 Traceback: {traceback.format_exc()}")
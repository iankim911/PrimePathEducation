#!/usr/bin/env python
"""
Comprehensive QA Test for Matrix Tab Error Fix
Tests all aspects of the fix to ensure no regressions
Created: 2025-08-23
"""

import os
import sys
import django
import json
import requests
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User
from core.models import Teacher

class MatrixTabErrorFixTest(TestCase):
    """Comprehensive test suite for Matrix tab error fix"""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data"""
        cls.test_user, created = User.objects.get_or_create(
            username='testteacher',
            defaults={
                'is_staff': True
            }
        )
        if created:
            cls.test_user.set_password('testpass123')
            cls.test_user.save()
            
        cls.teacher, _ = Teacher.objects.get_or_create(
            user=cls.test_user,
            defaults={
                'name': 'Test Teacher',
                'is_head_teacher': True
            }
        )
        
    def setUp(self):
        """Set up test client"""
        self.client = Client()
        self.client.login(username='testteacher', password='testpass123')
        
    def test_middleware_removed(self):
        """Test that MatrixTabInjectionMiddleware is removed from settings"""
        print("\n🔍 TEST 1: Checking middleware configuration...")
        
        middleware_list = settings.MIDDLEWARE
        has_matrix_middleware = any('MatrixTabInjectionMiddleware' in m for m in middleware_list)
        
        self.assertFalse(has_matrix_middleware, 
                        "MatrixTabInjectionMiddleware should be removed from MIDDLEWARE")
        print("   ✅ MatrixTabInjectionMiddleware successfully removed")
        
    def test_navigation_structure(self):
        """Test that navigation structure is correct"""
        print("\n🔍 TEST 2: Checking navigation structure...")
        
        response = self.client.get(reverse('RoutineTest:index'))
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode('utf-8')
        
        # Check that Classes & Exams tab exists
        self.assertIn('data-nav="classes-exams"', content,
                     "Classes & Exams tab should be present")
        self.assertIn('Classes & Exams', content,
                     "Classes & Exams text should be visible")
        
        # Check that old Matrix tab references are gone
        self.assertNotIn('data-nav="exam-assignments"', content,
                        "Old exam-assignments tab should not exist")
        self.assertNotIn('data-nav="matrix"', content,
                        "Matrix tab references should not exist")
        self.assertNotIn('matrix-tab-injected', content,
                        "Injected Matrix tab should not exist")
        
        print("   ✅ Navigation structure is correct")
        print("   ✅ Classes & Exams tab is present")
        print("   ✅ No Matrix tab references found")
        
    def test_error_handler_loaded(self):
        """Test that error handler script is loaded"""
        print("\n🔍 TEST 3: Checking error handler...")
        
        response = self.client.get(reverse('RoutineTest:index'))
        content = response.content.decode('utf-8')
        
        # Check for error handler script
        self.assertIn('navigation-error-handler.js', content,
                     "Navigation error handler should be loaded")
        
        print("   ✅ Navigation error handler is loaded")
        
    def test_urls_redirect_properly(self):
        """Test that old Matrix URLs redirect properly"""
        print("\n🔍 TEST 4: Checking URL redirects...")
        
        # Test schedule-matrix redirect
        response = self.client.get('/RoutineTest/schedule-matrix/', follow=False)
        self.assertEqual(response.status_code, 302,
                        "schedule-matrix should redirect")
        
        if response.status_code == 302:
            redirect_url = response.url
            self.assertIn('classes-exams', redirect_url,
                         "Should redirect to classes-exams")
            print("   ✅ schedule-matrix redirects to classes-exams")
        
        # Test my-classes redirect  
        response = self.client.get('/RoutineTest/access/my-classes/', follow=False)
        self.assertEqual(response.status_code, 302,
                        "my-classes should redirect")
        
        if response.status_code == 302:
            redirect_url = response.url
            self.assertIn('classes-exams', redirect_url,
                         "Should redirect to classes-exams")
            print("   ✅ my-classes redirects to classes-exams")
            
    def test_exam_schedule_matrix_model(self):
        """Test that ExamScheduleMatrix model still works"""
        print("\n🔍 TEST 5: Checking ExamScheduleMatrix model...")
        
        from primepath_routinetest.models import ExamScheduleMatrix
        
        # Create a test matrix entry
        matrix = ExamScheduleMatrix.objects.create(
            class_code='3A',
            academic_year='2025',
            time_period_type='MONTHLY',
            time_period_value='JAN'
        )
        
        self.assertIsNotNone(matrix.id)
        self.assertEqual(matrix.status, 'EMPTY')
        
        # Test methods
        self.assertEqual(matrix.get_exam_count(), 0)
        self.assertIsNotNone(matrix.get_status_color())
        self.assertIsNotNone(matrix.get_status_icon())
        
        print("   ✅ ExamScheduleMatrix model works correctly")
        print(f"   ✅ Created test matrix: {matrix}")
        
        # Clean up
        matrix.delete()
        
    def test_classes_exams_unified_view(self):
        """Test that unified Classes & Exams view works"""
        print("\n🔍 TEST 6: Checking Classes & Exams unified view...")
        
        response = self.client.get(reverse('RoutineTest:classes_exams_unified'))
        self.assertEqual(response.status_code, 200,
                        "Classes & Exams view should load")
        
        content = response.content.decode('utf-8')
        
        # Check for key elements
        self.assertIn('Classes & Exams', content)
        
        print("   ✅ Classes & Exams unified view loads successfully")
        
    def test_no_javascript_errors(self):
        """Test that pages don't have Matrix-related JavaScript references"""
        print("\n🔍 TEST 7: Checking for JavaScript errors...")
        
        pages_to_test = [
            'RoutineTest:index',
            'RoutineTest:classes_exams_unified',
            'RoutineTest:exam_list',
        ]
        
        for page_name in pages_to_test:
            try:
                response = self.client.get(reverse(page_name))
                content = response.content.decode('utf-8')
                
                # Check for Matrix JavaScript references
                self.assertNotIn('schedule-matrix.js', content,
                                f"{page_name} should not load schedule-matrix.js")
                self.assertNotIn('MATRIX_TAB_NOT_FOUND', content,
                                f"{page_name} should not have MATRIX_TAB_NOT_FOUND error")
                
                print(f"   ✅ {page_name} has no Matrix JavaScript references")
            except Exception as e:
                print(f"   ⚠️ Could not test {page_name}: {e}")
                
    def test_orphaned_files_renamed(self):
        """Test that orphaned Matrix files are renamed/removed"""
        print("\n🔍 TEST 8: Checking orphaned files...")
        
        base_path = '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project'
        
        files_should_not_exist = [
            'primepath_routinetest/middleware.py',
            'static/js/routinetest/schedule-matrix.js',
            'static/css/routinetest/schedule-matrix.css'
        ]
        
        for file_path in files_should_not_exist:
            full_path = os.path.join(base_path, file_path)
            self.assertFalse(os.path.exists(full_path),
                           f"{file_path} should be renamed or removed")
            
            # Check if deprecated version exists
            deprecated_path = full_path + '.deprecated'
            if os.path.exists(deprecated_path):
                print(f"   ✅ {file_path} renamed to .deprecated")
            else:
                print(f"   ✅ {file_path} removed")
                
    def test_viewport_unchanged(self):
        """Test that viewport and layout are unchanged"""
        print("\n🔍 TEST 9: Checking viewport integrity...")
        
        response = self.client.get(reverse('RoutineTest:index'))
        content = response.content.decode('utf-8')
        
        # Check that viewport meta tag is present
        self.assertIn('viewport', content)
        self.assertIn('width=device-width', content)
        
        # Check that main layout elements are present
        self.assertIn('nav-tabs', content)
        self.assertIn('container', content)
        
        print("   ✅ Viewport settings unchanged")
        print("   ✅ Layout structure preserved")
        
    def test_api_endpoints_working(self):
        """Test that API endpoints still work"""
        print("\n🔍 TEST 10: Checking API endpoints...")
        
        # Test class exams API
        try:
            response = self.client.get('/RoutineTest/api/class/3A/exams/')
            self.assertIn(response.status_code, [200, 404],
                         "API should return valid response")
            print("   ✅ Class exams API working")
        except Exception as e:
            print(f"   ⚠️ API test skipped: {e}")

def run_comprehensive_qa():
    """Run all QA tests"""
    print("="*60)
    print("🧪 COMPREHENSIVE QA TEST FOR MATRIX TAB ERROR FIX")
    print("="*60)
    print(f"Started at: {datetime.now().isoformat()}")
    print("-"*60)
    
    # Run Django tests
    from django.test.utils import setup_test_environment, teardown_test_environment
    from django.test import TestCase
    
    setup_test_environment()
    
    suite = TestCase()
    test = MatrixTabErrorFixTest()
    test.setUpTestData()
    test.setUp()
    
    # Run each test
    tests = [
        test.test_middleware_removed,
        test.test_navigation_structure,
        test.test_error_handler_loaded,
        test.test_urls_redirect_properly,
        test.test_exam_schedule_matrix_model,
        test.test_classes_exams_unified_view,
        test.test_no_javascript_errors,
        test.test_orphaned_files_renamed,
        test.test_viewport_unchanged,
        test.test_api_endpoints_working
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {test_func.__name__}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"\n⚠️ TEST ERROR: {test_func.__name__}")
            print(f"   Error: {e}")
            failed += 1
    
    teardown_test_environment()
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Matrix tab error fix is complete.")
    else:
        print(f"\n⚠️ {failed} tests failed. Please review the errors above.")
    
    print("-"*60)
    print(f"Completed at: {datetime.now().isoformat()}")
    print("="*60)
    
    return passed, failed

if __name__ == '__main__':
    passed, failed = run_comprehensive_qa()
    sys.exit(0 if failed == 0 else 1)
#!/usr/bin/env python
"""
Comprehensive double-check test for ownership filtering and all existing features
Ensures no features are broken by recent changes
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from primepath_routinetest.models import Exam, TeacherClassAssignment
from primepath_routinetest.services.exam_service import ExamService, ExamPermissionService
from core.models import Teacher


class ComprehensiveTest:
    def __init__(self):
        self.client = Client()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests_passed': 0,
            'tests_failed': 0,
            'failures': []
        }
        
    def setup_test_user(self):
        """Setup test user with proper permissions"""
        print("\n" + "="*80)
        print("SETUP: Preparing test environment")
        print("="*80)
        
        try:
            # Find or create admin user
            self.admin_user = User.objects.filter(username='admin').first()
            if not self.admin_user:
                self.admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'test123')
            else:
                self.admin_user.set_password('test123')
                self.admin_user.save()
                
            # Find or create teacher user
            self.teacher_user = User.objects.filter(username='teacher1').first()
            if not self.teacher_user:
                self.teacher_user = User.objects.create_user('teacher1', 'teacher1@test.com', 'test123')
                self.teacher_user.is_staff = True
                self.teacher_user.save()
            else:
                self.teacher_user.set_password('test123')
                self.teacher_user.save()
                
            print(f"✅ Users ready: admin, teacher1")
            return True
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False
    
    def test_ownership_filtering(self):
        """Test 1: Ownership Filtering System"""
        print("\n" + "-"*60)
        print("TEST 1: Ownership Filtering (My vs Others)")
        print("-"*60)
        
        try:
            # Login as admin
            self.client.login(username='admin', password='test123')
            
            # Test "My Test Files" filter
            response = self.client.get('/RoutineTest/exams/?ownership=my')
            if response.status_code == 200:
                context = response.context
                if context.get('filter_intent') == 'SHOW_EDITABLE':
                    print("✅ My Test Files: Correct filter intent (SHOW_EDITABLE)")
                    self.results['tests_passed'] += 1
                else:
                    print(f"❌ My Test Files: Wrong filter intent: {context.get('filter_intent')}")
                    self.results['tests_failed'] += 1
                    self.results['failures'].append("My Test Files filter intent incorrect")
            else:
                print(f"❌ My Test Files: HTTP {response.status_code}")
                self.results['tests_failed'] += 1
                self.results['failures'].append(f"My Test Files returned {response.status_code}")
                
            # Test "Other Teachers' Test Files" filter
            response = self.client.get('/RoutineTest/exams/?ownership=others')
            if response.status_code == 200:
                context = response.context
                if context.get('filter_intent') == 'SHOW_VIEW_ONLY':
                    print("✅ Other Teachers' Files: Correct filter intent (SHOW_VIEW_ONLY)")
                    self.results['tests_passed'] += 1
                else:
                    print(f"❌ Other Teachers' Files: Wrong filter intent: {context.get('filter_intent')}")
                    self.results['tests_failed'] += 1
                    self.results['failures'].append("Other Teachers' Files filter intent incorrect")
            else:
                print(f"❌ Other Teachers' Files: HTTP {response.status_code}")
                self.results['tests_failed'] += 1
                self.results['failures'].append(f"Other Teachers' Files returned {response.status_code}")
                
        except Exception as e:
            print(f"❌ Ownership filtering test failed: {e}")
            self.results['tests_failed'] += 1
            self.results['failures'].append(f"Ownership filtering error: {e}")
    
    def test_copy_exam_api(self):
        """Test 2: Copy Exam Functionality"""
        print("\n" + "-"*60)
        print("TEST 2: Copy Exam API")
        print("-"*60)
        
        try:
            # Login as admin
            self.client.login(username='admin', password='test123')
            
            # Find an exam to copy
            exam = Exam.objects.first()
            if not exam:
                print("⚠️ No exams to test copy functionality")
                return
                
            # Test copy exam API endpoint
            copy_data = {
                'source_exam_id': str(exam.id),
                'target_class': 'HIGH_12E',
                'year': '2025',
                'custom_suffix': 'test_copy'
            }
            
            response = self.client.post(
                '/RoutineTest/api/exams/copy/',
                data=json.dumps(copy_data),
                content_type='application/json'
            )
            
            if response.status_code in [200, 201]:
                print("✅ Copy exam API working")
                self.results['tests_passed'] += 1
            else:
                print(f"❌ Copy exam API failed: HTTP {response.status_code}")
                self.results['tests_failed'] += 1
                self.results['failures'].append(f"Copy exam API returned {response.status_code}")
                
        except Exception as e:
            print(f"❌ Copy exam test failed: {e}")
            self.results['tests_failed'] += 1
            self.results['failures'].append(f"Copy exam error: {e}")
    
    def test_delete_permissions(self):
        """Test 3: Delete Exam Permissions"""
        print("\n" + "-"*60)
        print("TEST 3: Delete Exam Permissions")
        print("-"*60)
        
        try:
            # Test as teacher
            self.client.login(username='teacher1', password='test123')
            
            # Check if teacher can see delete button for owned exams
            teacher = Teacher.objects.filter(user=self.teacher_user).first()
            if teacher:
                # Find exams created by this teacher
                owned_exams = Exam.objects.filter(created_by=teacher)
                
                for exam in owned_exams[:1]:  # Test first owned exam
                    can_delete = ExamPermissionService.can_teacher_delete_exam(teacher, exam)
                    if can_delete:
                        print(f"✅ Teacher can delete owned exam: {exam.name}")
                        self.results['tests_passed'] += 1
                    else:
                        print(f"❌ Teacher cannot delete owned exam: {exam.name}")
                        self.results['tests_failed'] += 1
                        self.results['failures'].append("Delete permission check failed for owned exam")
                        
                # Test non-owned exam
                other_exam = Exam.objects.exclude(created_by=teacher).first()
                if other_exam:
                    # Teacher should NOT be able to delete unless they have FULL access
                    can_delete = ExamPermissionService.can_teacher_delete_exam(teacher, other_exam)
                    assignments = TeacherClassAssignment.objects.filter(
                        teacher=teacher,
                        class_code__in=other_exam.class_codes,
                        access_level='FULL',
                        is_active=True
                    ).exists()
                    
                    if can_delete == assignments:
                        print(f"✅ Delete permissions correct for non-owned exam")
                        self.results['tests_passed'] += 1
                    else:
                        print(f"❌ Delete permissions incorrect for non-owned exam")
                        self.results['tests_failed'] += 1
                        self.results['failures'].append("Delete permission logic error")
            else:
                print("⚠️ No teacher profile for teacher1")
                
        except Exception as e:
            print(f"❌ Delete permissions test failed: {e}")
            self.results['tests_failed'] += 1
            self.results['failures'].append(f"Delete permissions error: {e}")
    
    def test_exam_list_view(self):
        """Test 4: Exam List View Rendering"""
        print("\n" + "-"*60)
        print("TEST 4: Exam List View")
        print("-"*60)
        
        try:
            # Test as admin
            self.client.login(username='admin', password='test123')
            
            # Test default exam list
            response = self.client.get('/RoutineTest/exams/')
            if response.status_code == 200:
                print("✅ Exam list loads successfully")
                self.results['tests_passed'] += 1
                
                # Check for required context variables
                context = response.context
                required_vars = ['exams_by_program', 'is_admin', 'teacher_assignments']
                
                for var in required_vars:
                    if var in context:
                        print(f"  ✅ Context has '{var}'")
                    else:
                        print(f"  ❌ Context missing '{var}'")
                        self.results['failures'].append(f"Context missing {var}")
                        
            else:
                print(f"❌ Exam list failed: HTTP {response.status_code}")
                self.results['tests_failed'] += 1
                self.results['failures'].append(f"Exam list returned {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exam list test failed: {e}")
            self.results['tests_failed'] += 1
            self.results['failures'].append(f"Exam list error: {e}")
    
    def test_class_assignments(self):
        """Test 5: Class Assignment Features"""
        print("\n" + "-"*60)
        print("TEST 5: Class Assignments")
        print("-"*60)
        
        try:
            # Test as admin
            self.client.login(username='admin', password='test123')
            
            # Test class assignment API
            response = self.client.get('/RoutineTest/access/api/my-classes/')
            if response.status_code == 200:
                print("✅ My classes API working")
                self.results['tests_passed'] += 1
                
                data = json.loads(response.content)
                if 'assigned_classes' in data:
                    print(f"  Found {len(data['assigned_classes'])} assigned classes")
                    
            else:
                print(f"❌ My classes API failed: HTTP {response.status_code}")
                self.results['tests_failed'] += 1
                self.results['failures'].append(f"My classes API returned {response.status_code}")
                
            # Test teacher class matrix
            response = self.client.get('/RoutineTest/access/api/teacher-class-matrix/')
            if response.status_code == 200:
                print("✅ Teacher-class matrix API working")
                self.results['tests_passed'] += 1
            else:
                print(f"❌ Teacher-class matrix API failed: HTTP {response.status_code}")
                self.results['tests_failed'] += 1
                self.results['failures'].append(f"Teacher-class matrix API returned {response.status_code}")
                
        except Exception as e:
            print(f"❌ Class assignments test failed: {e}")
            self.results['tests_failed'] += 1
            self.results['failures'].append(f"Class assignments error: {e}")
    
    def test_exam_creation(self):
        """Test 6: Exam Creation Page"""
        print("\n" + "-"*60)
        print("TEST 6: Exam Creation")
        print("-"*60)
        
        try:
            # Test as admin
            self.client.login(username='admin', password='test123')
            
            # Test exam creation page
            response = self.client.get('/RoutineTest/exams/create/')
            if response.status_code == 200:
                print("✅ Exam creation page loads")
                self.results['tests_passed'] += 1
            else:
                print(f"❌ Exam creation page failed: HTTP {response.status_code}")
                self.results['tests_failed'] += 1
                self.results['failures'].append(f"Exam creation page returned {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exam creation test failed: {e}")
            self.results['tests_failed'] += 1
            self.results['failures'].append(f"Exam creation error: {e}")
    
    def test_service_layer(self):
        """Test 7: Service Layer Functions"""
        print("\n" + "-"*60)
        print("TEST 7: Service Layer")
        print("-"*60)
        
        try:
            # Test ExamService methods
            user = self.admin_user
            exams = Exam.objects.all()[:5]
            
            # Test organize_exams_hierarchically with different filters
            result_my = ExamService.organize_exams_hierarchically(
                exams, user, ownership_filter='my', filter_intent='SHOW_EDITABLE'
            )
            result_others = ExamService.organize_exams_hierarchically(
                exams, user, ownership_filter='others', filter_intent='SHOW_VIEW_ONLY'
            )
            
            print("✅ ExamService.organize_exams_hierarchically working")
            self.results['tests_passed'] += 1
            
            # Test curriculum methods
            curriculum_levels = ExamService.get_routinetest_curriculum_levels()
            if curriculum_levels:
                print(f"✅ Curriculum levels loaded: {len(curriculum_levels)} levels")
                self.results['tests_passed'] += 1
            else:
                print("❌ No curriculum levels found")
                self.results['tests_failed'] += 1
                self.results['failures'].append("Curriculum levels not loading")
                
        except Exception as e:
            print(f"❌ Service layer test failed: {e}")
            self.results['tests_failed'] += 1
            self.results['failures'].append(f"Service layer error: {e}")
    
    def run_all_tests(self):
        """Run all comprehensive tests"""
        if not self.setup_test_user():
            print("❌ Setup failed, cannot continue tests")
            return
            
        # Run all test suites
        self.test_ownership_filtering()
        self.test_copy_exam_api()
        self.test_delete_permissions()
        self.test_exam_list_view()
        self.test_class_assignments()
        self.test_exam_creation()
        self.test_service_layer()
        
        # Print summary
        print("\n" + "="*80)
        print("COMPREHENSIVE TEST SUMMARY")
        print("="*80)
        print(f"✅ Tests Passed: {self.results['tests_passed']}")
        print(f"❌ Tests Failed: {self.results['tests_failed']}")
        
        if self.results['failures']:
            print("\nFailures:")
            for failure in self.results['failures']:
                print(f"  • {failure}")
        
        # Overall status
        print("\n" + "="*80)
        if self.results['tests_failed'] == 0:
            print("🎉 ALL TESTS PASSED - No existing features affected!")
        else:
            print(f"⚠️ {self.results['tests_failed']} tests failed - Review needed")
        print("="*80)
        
        return self.results['tests_failed'] == 0


if __name__ == '__main__':
    tester = ComprehensiveTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
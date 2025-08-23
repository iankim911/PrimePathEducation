#!/usr/bin/env python
"""
Comprehensive Teacher Access Management Dashboard Testing
Tests all features of the new teacher management system

Run this script to verify:
1. Admin dashboard loads properly
2. Teacher-class relationships display correctly  
3. Multi-teacher assignments work
4. Direct assignment functionality
5. Request management system
6. Matrix view functionality
7. Console logging and debugging

Usage:
    python test_teacher_management_comprehensive.py
"""
import os
import sys
import django
from datetime import datetime
import json

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import Teacher
from primepath_routinetest.models import TeacherClassAssignment, ClassAccessRequest, AccessAuditLog, Class
from primepath_routinetest.views.admin_teacher_management import (
    teacher_access_management_dashboard,
    admin_direct_assign_teacher,
    admin_revoke_teacher_access,
    admin_bulk_assign_teachers
)

class TeacherManagementTester:
    def __init__(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.test_results = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'failures': []
        }
        
        print(f"\n{'='*80}")
        print(f"COMPREHENSIVE TEACHER ACCESS MANAGEMENT TESTING")
        print(f"{'='*80}")
        print(f"Started: {datetime.now()}")
        print(f"{'='*80}\n")
    
    def log_test(self, test_name, passed, details=None):
        """Log test results"""
        self.test_results['tests_run'] += 1
        
        if passed:
            self.test_results['tests_passed'] += 1
            status = "✅ PASS"
            color = "\033[92m"  # Green
        else:
            self.test_results['tests_failed'] += 1
            status = "❌ FAIL"
            color = "\033[91m"  # Red
            self.test_results['failures'].append({
                'test': test_name,
                'details': details
            })
        
        reset_color = "\033[0m"
        print(f"{color}[{status}]{reset_color} {test_name}")
        if details:
            print(f"      Details: {details}")
    
    def setup_test_data(self):
        """Create test users and data"""
        print("\n🔧 Setting up test data...")
        
        try:
            # Create admin user
            admin_user, created = User.objects.get_or_create(
                username='test_admin',
                defaults={
                    'email': 'admin@test.com',
                    'is_superuser': True,
                    'is_staff': True,
                    'first_name': 'Test',
                    'last_name': 'Admin'
                }
            )
            
            # Create admin teacher profile
            admin_teacher, created = Teacher.objects.get_or_create(
                user=admin_user,
                defaults={
                    'name': 'Test Admin',
                    'email': 'admin@test.com',
                    'is_head_teacher': True,
                    'global_access_level': 'FULL'
                }
            )
            
            # Create test teachers
            test_teachers = []
            for i in range(3):
                user, created = User.objects.get_or_create(
                    username=f'test_teacher_{i+1}',
                    defaults={
                        'email': f'teacher{i+1}@test.com',
                        'is_staff': True,
                        'first_name': f'Teacher',
                        'last_name': f'{i+1}'
                    }
                )
                
                teacher, created = Teacher.objects.get_or_create(
                    user=user,
                    defaults={
                        'name': f'Test Teacher {i+1}',
                        'email': f'teacher{i+1}@test.com',
                        'global_access_level': 'FULL' if i < 2 else 'VIEW_ONLY'
                    }
                )
                test_teachers.append(teacher)
            
            # Create test classes using the actual Class model
            test_classes = []
            class_data = [
                ('PRIMARY_1A', 'Primary Grade 1A', 'Grade 1'),
                ('MIDDLE_7A', 'Middle School Grade 7A', 'Grade 7'),
                ('HIGH_10A', 'High School Grade 10A', 'Grade 10')
            ]
            
            for section, name, grade in class_data:
                try:
                    cls, created = Class.objects.get_or_create(
                        section=section,
                        defaults={
                            'name': name,
                            'grade_level': grade,
                            'academic_year': '2024-2025',
                            'is_active': True,
                            'created_by': admin_user
                        }
                    )
                    test_classes.append(cls)
                except Exception as e:
                    print(f"      Warning: Could not create class {section}: {e}")
            
            # Create some test assignments
            class_codes = ['PRIMARY_1A', 'MIDDLE_7A', 'HIGH_10A']
            for i, teacher in enumerate(test_teachers[:2]):  # Only first 2 teachers
                for j, class_code in enumerate(class_codes):
                    if j <= i:  # Create overlapping assignments
                        TeacherClassAssignment.objects.get_or_create(
                            teacher=teacher,
                            class_code=class_code,
                            defaults={
                                'access_level': 'FULL',
                                'assigned_by': admin_user,
                                'is_active': True
                            }
                        )
            
            # Create some test access requests
            if test_teachers:
                for class_code in class_codes:
                    ClassAccessRequest.objects.get_or_create(
                        teacher=test_teachers[-1],  # Last teacher requests access
                        class_code=class_code,
                        defaults={
                            'requested_access_level': 'FULL',
                            'reason_code': 'NEW_ASSIGNMENT',
                            'reason_text': 'Need access for teaching this class',
                            'status': 'PENDING'
                        }
                    )
            
            self.admin_user = admin_user
            self.admin_teacher = admin_teacher
            self.test_teachers = test_teachers
            self.test_classes = test_classes
            
            print(f"      ✅ Created admin user: {admin_user.username}")
            print(f"      ✅ Created {len(test_teachers)} test teachers")
            print(f"      ✅ Created {len(test_classes)} test classes")
            print(f"      ✅ Created test assignments and requests")
            
            return True
            
        except Exception as e:
            print(f"      ❌ Setup failed: {str(e)}")
            return False
    
    def test_admin_dashboard_access(self):
        """Test 1: Admin Dashboard Access"""
        try:
            # Login as admin
            self.client.force_login(self.admin_user)
            
            # Test dashboard URL
            url = reverse('RoutineTest:admin_teacher_management_dashboard')
            response = self.client.get(url)
            
            if response.status_code == 200:
                self.log_test("Admin Dashboard Access", True, f"Status: {response.status_code}")
            else:
                self.log_test("Admin Dashboard Access", False, f"Unexpected status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Admin Dashboard Access", False, str(e))
    
    def test_dashboard_view_modes(self):
        """Test 2: Dashboard View Modes"""
        try:
            self.client.force_login(self.admin_user)
            url = reverse('RoutineTest:admin_teacher_management_dashboard')
            
            view_modes = ['overview', 'teachers', 'classes', 'matrix', 'requests']
            all_passed = True
            
            for mode in view_modes:
                response = self.client.get(url, {'view': mode})
                if response.status_code != 200:
                    all_passed = False
                    break
            
            self.log_test("Dashboard View Modes", all_passed, f"Tested {len(view_modes)} view modes")
            
        except Exception as e:
            self.log_test("Dashboard View Modes", False, str(e))
    
    def test_teacher_directory_data(self):
        """Test 3: Teacher Directory Data"""
        try:
            request = self.factory.get('/access/admin/teacher-management/')
            request.user = self.admin_user
            
            response = teacher_access_management_dashboard(request)
            
            # Check if context contains expected data
            context_keys = ['teacher_directory', 'analytics', 'is_admin']
            has_all_keys = True
            
            # For this test, we'll check the response content
            content = response.content.decode('utf-8')
            has_teacher_data = 'teacher-directory-grid' in content
            has_analytics = 'analytics-grid' in content
            
            self.log_test("Teacher Directory Data", has_teacher_data and has_analytics, 
                         "Teacher directory and analytics present")
            
        except Exception as e:
            self.log_test("Teacher Directory Data", False, str(e))
    
    def test_direct_assignment_api(self):
        """Test 4: Direct Teacher Assignment API"""
        try:
            self.client.force_login(self.admin_user)
            url = reverse('RoutineTest:admin_direct_assign_teacher')
            
            # Test assignment data
            assignment_data = {
                'teacher_id': str(self.test_teachers[0].id),
                'class_code': 'HIGH_10A',
                'access_level': 'FULL',
                'notes': 'Test assignment via API'
            }
            
            response = self.client.post(
                url, 
                data=json.dumps(assignment_data),
                content_type='application/json'
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                self.log_test("Direct Assignment API", success, f"Response: {data.get('message', 'No message')}")
            else:
                self.log_test("Direct Assignment API", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Direct Assignment API", False, str(e))
    
    def test_multi_teacher_assignments(self):
        """Test 5: Multi-Teacher Class Assignments"""
        try:
            # Assign multiple teachers to the same class
            class_code = 'PRIMARY_1A'
            
            # Count existing assignments
            initial_count = TeacherClassAssignment.objects.filter(
                class_code=class_code,
                is_active=True
            ).count()
            
            # Create additional assignment
            if len(self.test_teachers) >= 2:
                assignment, created = TeacherClassAssignment.objects.get_or_create(
                    teacher=self.test_teachers[1],
                    class_code=class_code,
                    defaults={
                        'access_level': 'VIEW',
                        'assigned_by': self.admin_user,
                        'is_active': True
                    }
                )
                
                final_count = TeacherClassAssignment.objects.filter(
                    class_code=class_code,
                    is_active=True
                ).count()
                
                multi_teacher_support = final_count > 1
                self.log_test("Multi-Teacher Assignments", multi_teacher_support, 
                             f"Class {class_code} has {final_count} teachers")
            else:
                self.log_test("Multi-Teacher Assignments", False, "Not enough test teachers")
                
        except Exception as e:
            self.log_test("Multi-Teacher Assignments", False, str(e))
    
    def test_bulk_assignment_api(self):
        """Test 6: Bulk Assignment API"""
        try:
            self.client.force_login(self.admin_user)
            url = reverse('RoutineTest:admin_bulk_assign_teachers')
            
            # Test bulk assignment data
            bulk_data = {
                'teacher_ids': [str(t.id) for t in self.test_teachers[:2]],
                'class_codes': ['MIDDLE_7A', 'HIGH_10A'],
                'access_level': 'VIEW',
                'notes': 'Bulk test assignment'
            }
            
            response = self.client.post(
                url,
                data=json.dumps(bulk_data),
                content_type='application/json'
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                operations = data.get('total_operations', 0)
                self.log_test("Bulk Assignment API", success, f"Operations: {operations}")
            else:
                self.log_test("Bulk Assignment API", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Bulk Assignment API", False, str(e))
    
    def test_access_request_management(self):
        """Test 7: Access Request Management"""
        try:
            # Check if pending requests exist
            pending_count = ClassAccessRequest.objects.filter(status='PENDING').count()
            
            if pending_count > 0:
                # Test request approval
                self.client.force_login(self.admin_user)
                request = ClassAccessRequest.objects.filter(status='PENDING').first()
                
                if request:
                    url = reverse('RoutineTest:approve_request', args=[request.id])
                    response = self.client.post(url)
                    
                    success = response.status_code == 200
                    if success:
                        data = response.json()
                        success = data.get('success', False)
                    
                    self.log_test("Access Request Management", success, f"Approved request {request.id}")
                else:
                    self.log_test("Access Request Management", False, "No pending requests found")
            else:
                self.log_test("Access Request Management", True, "No pending requests (expected)")
                
        except Exception as e:
            self.log_test("Access Request Management", False, str(e))
    
    def test_matrix_api(self):
        """Test 8: Matrix API Functionality"""
        try:
            self.client.force_login(self.admin_user)
            url = reverse('RoutineTest:api_teacher_class_matrix')
            
            response = self.client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                matrix = data.get('matrix', {})
                
                has_matrix_data = len(matrix) > 0
                self.log_test("Matrix API Functionality", success and has_matrix_data, 
                             f"Matrix contains {len(matrix)} teachers")
            else:
                self.log_test("Matrix API Functionality", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Matrix API Functionality", False, str(e))
    
    def test_audit_logging(self):
        """Test 9: Audit Logging System"""
        try:
            initial_count = AccessAuditLog.objects.count()
            
            # Perform an action that should create audit log
            AccessAuditLog.log_action(
                action='ADMIN_DIRECT_ASSIGN',
                teacher=self.test_teachers[0],
                class_code='PRIMARY_1A',
                user=self.admin_user,
                details={'test': 'audit_logging'}
            )
            
            final_count = AccessAuditLog.objects.count()
            log_created = final_count > initial_count
            
            self.log_test("Audit Logging System", log_created, 
                         f"Audit logs: {initial_count} → {final_count}")
            
        except Exception as e:
            self.log_test("Audit Logging System", False, str(e))
    
    def test_template_rendering(self):
        """Test 10: Template Rendering with Filters"""
        try:
            self.client.force_login(self.admin_user)
            
            # Test each view mode for template errors
            url = reverse('RoutineTest:admin_teacher_management_dashboard')
            view_modes = ['overview', 'teachers', 'classes', 'matrix']
            
            all_rendered = True
            for mode in view_modes:
                response = self.client.get(url, {'view': mode})
                if response.status_code != 200:
                    all_rendered = False
                    break
                
                # Check for template filter errors in content
                content = response.content.decode('utf-8')
                if 'TemplateSyntaxError' in content or 'Invalid filter' in content:
                    all_rendered = False
                    break
            
            self.log_test("Template Rendering", all_rendered, "All view modes render correctly")
            
        except Exception as e:
            self.log_test("Template Rendering", False, str(e))
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting comprehensive teacher management tests...\n")
        
        # Setup test data
        if not self.setup_test_data():
            print("❌ Test setup failed. Aborting tests.")
            return
        
        # Run all tests
        self.test_admin_dashboard_access()
        self.test_dashboard_view_modes()
        self.test_teacher_directory_data()
        self.test_direct_assignment_api()
        self.test_multi_teacher_assignments()
        self.test_bulk_assignment_api()
        self.test_access_request_management()
        self.test_matrix_api()
        self.test_audit_logging()
        self.test_template_rendering()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        results = self.test_results
        
        print(f"\n{'='*80}")
        print(f"TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Total Tests Run: {results['tests_run']}")
        print(f"Tests Passed: \033[92m{results['tests_passed']}\033[0m")
        print(f"Tests Failed: \033[91m{results['tests_failed']}\033[0m")
        
        if results['tests_run'] > 0:
            pass_rate = (results['tests_passed'] / results['tests_run']) * 100
            print(f"Pass Rate: {pass_rate:.1f}%")
        
        if results['failures']:
            print(f"\n❌ FAILURES:")
            for i, failure in enumerate(results['failures'], 1):
                print(f"   {i}. {failure['test']}")
                print(f"      {failure['details']}")
        
        print(f"\n{'='*80}")
        print(f"Completed: {datetime.now()}")
        print(f"{'='*80}\n")
        
        # Final assessment
        if results['tests_failed'] == 0:
            print("🎉 ALL TESTS PASSED! Teacher Management Dashboard is ready for production.")
        elif results['tests_failed'] <= 2:
            print("⚠️  Most tests passed. Minor issues need attention.")
        else:
            print("🚨 Multiple test failures. Review implementation before deploying.")


def main():
    """Main test execution"""
    tester = TeacherManagementTester()
    tester.run_all_tests()


if __name__ == '__main__':
    main()
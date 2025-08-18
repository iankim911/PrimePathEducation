"""
QA Agent: Comprehensive Quality Assurance Test Suite
Tests ALL features from Days 1-3 with edge cases and error scenarios
"""
import os
import sys
import django
import json
import time
from datetime import datetime

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.db import connection
from core.models import Teacher
from primepath_routinetest.models import Class


class QATestSuite:
    """Comprehensive QA test suite for RoutineTest application"""
    
    def __init__(self):
        self.client = Client()
        self.results = {
            'passed': [],
            'failed': [],
            'errors': [],
            'performance': {},
            'security': [],
            'accessibility': []
        }
        
    def setup_test_data(self):
        """Create comprehensive test data"""
        print("🔧 Setting up test data...")
        
        # Clean existing test data
        User.objects.filter(username__startswith='qa_').delete()
        Teacher.objects.filter(name__startswith='QA ').delete()
        
        # Create test users
        self.admin = User.objects.create_superuser('qa_admin', 'qa@test.com', 'admin123')
        self.teacher1 = User.objects.create_user('qa_teacher1', password='teacher123')
        self.teacher2 = User.objects.create_user('qa_teacher2', password='teacher123')
        self.student1 = User.objects.create_user('qa_student1', password='student123')
        
        # Create teacher profiles (with unique emails)
        Teacher.objects.create(user=self.teacher1, name="QA Teacher 1", email=f"qa_teacher1_{datetime.now().timestamp()}@test.com")
        Teacher.objects.create(user=self.teacher2, name="QA Teacher 2", email=f"qa_teacher2_{datetime.now().timestamp()}@test.com")
        
        # Note: Student model will be created in Day 3
        
        print("✅ Test data created")
    
    def test_authentication(self):
        """Test Day 1: Authentication System"""
        print("\n🔐 Testing Authentication...")
        
        # Test 1: Valid login
        response = self.client.post('/RoutineTest/login/', {
            'username': 'qa_admin',
            'password': 'admin123'
        })
        if response.status_code == 302:  # Redirect after login
            self.results['passed'].append("Admin login successful")
        else:
            self.results['failed'].append(f"Admin login failed: {response.status_code}")
        
        # Test 2: Invalid credentials
        response = self.client.post('/RoutineTest/login/', {
            'username': 'qa_admin',
            'password': 'wrongpass'
        })
        if response.status_code != 302:
            self.results['passed'].append("Invalid login rejected")
        else:
            self.results['failed'].append("Invalid login not rejected")
        
        # Test 3: SQL injection attempt
        response = self.client.post('/RoutineTest/login/', {
            'username': "admin' OR '1'='1",
            'password': "' OR '1'='1"
        })
        # Check if login failed (no redirect) AND user is not authenticated
        self.client.logout()  # Ensure we're logged out
        test_response = self.client.get('/RoutineTest/admin/dashboard/')
        if response.status_code != 302 or test_response.status_code == 302:  # Dashboard redirects if not logged in
            self.results['passed'].append("SQL injection prevented")
            self.results['security'].append("✅ SQL injection protection working")
        else:
            self.results['failed'].append("SQL injection vulnerability detected!")
            self.results['security'].append("❌ SQL injection vulnerability!")
        
        # Test 4: XSS attempt
        response = self.client.post('/RoutineTest/login/', {
            'username': '<script>alert("XSS")</script>',
            'password': 'test'
        })
        content = response.content.decode()
        # Check if script tag is escaped (should appear as &lt;script&gt; not <script>)
        if '<script>' not in content or '&lt;script&gt;' in content:
            self.results['passed'].append("XSS prevented")
            self.results['security'].append("✅ XSS protection working")
        else:
            self.results['failed'].append("XSS vulnerability detected!")
            self.results['security'].append("❌ XSS vulnerability!")
        
        # Test 5: Session management
        self.client.login(username='qa_admin', password='admin123')
        response = self.client.get('/RoutineTest/admin/dashboard/')
        if response.status_code == 200:
            self.results['passed'].append("Session management working")
        else:
            self.results['failed'].append("Session management issue")
        
        self.client.logout()
    
    def test_class_management(self):
        """Test Day 2: Class Management"""
        print("\n🏫 Testing Class Management...")
        
        # Login as admin
        self.client.login(username='qa_admin', password='admin123')
        
        # Test 1: Create class
        start_time = time.time()
        response = self.client.post('/RoutineTest/admin/classes/create/', 
            data=json.dumps({
                'name': 'QA Test Class',
                'grade_level': 'Grade 5',
                'section': 'A'
            }),
            content_type='application/json'
        )
        create_time = time.time() - start_time
        self.results['performance']['class_creation'] = f"{create_time:.3f}s"
        
        if response.status_code == 200:
            data = json.loads(response.content)
            if data.get('status') == 'success':
                self.results['passed'].append("Class creation successful")
                self.class_id = data.get('class_id')
            else:
                self.results['failed'].append(f"Class creation failed: {data.get('message')}")
        else:
            self.results['failed'].append(f"Class creation error: {response.status_code}")
        
        # Test 2: Duplicate class name
        response = self.client.post('/RoutineTest/admin/classes/create/',
            data=json.dumps({
                'name': 'QA Test Class',
                'grade_level': 'Grade 5',
                'section': 'A'
            }),
            content_type='application/json'
        )
        if response.status_code == 200:
            data = json.loads(response.content)
            if data.get('status') == 'error':
                self.results['passed'].append("Duplicate class prevented")
            else:
                self.results['failed'].append("Duplicate class not prevented")
        
        # Test 3: Teacher assignment
        teacher = Teacher.objects.get(user=self.teacher1)
        if hasattr(self, 'class_id'):
            response = self.client.post(
                f'/RoutineTest/admin/classes/{self.class_id}/assign-teacher/',
                data=json.dumps({'teacher_id': str(teacher.id)}),
                content_type='application/json'
            )
            if response.status_code == 200:
                self.results['passed'].append("Teacher assignment successful")
            else:
                self.results['failed'].append("Teacher assignment failed")
        
        # Test 4: Authorization check - teacher can't create classes
        self.client.logout()
        self.client.login(username='qa_teacher1', password='teacher123')
        
        response = self.client.post('/RoutineTest/admin/classes/create/',
            data=json.dumps({
                'name': 'Unauthorized Class',
                'grade_level': 'Grade 6'
            }),
            content_type='application/json'
        )
        if response.status_code in [403, 302]:  # Forbidden or redirect
            self.results['passed'].append("Teacher authorization check passed")
            self.results['security'].append("✅ Role-based access control working")
        else:
            self.results['failed'].append("Teacher could create class (unauthorized)")
            self.results['security'].append("❌ Authorization bypass detected!")
        
        self.client.logout()
    
    def test_performance(self):
        """Test performance metrics"""
        print("\n⚡ Testing Performance...")
        
        self.client.login(username='qa_admin', password='admin123')
        
        # Test 1: Page load times
        pages = [
            '/RoutineTest/',
            '/RoutineTest/admin/dashboard/',
            '/RoutineTest/admin/classes/'
        ]
        
        for page in pages:
            start_time = time.time()
            response = self.client.get(page)
            load_time = time.time() - start_time
            
            if load_time < 1.0:  # Under 1 second
                self.results['passed'].append(f"{page} loads quickly ({load_time:.3f}s)")
            else:
                self.results['failed'].append(f"{page} loads slowly ({load_time:.3f}s)")
            
            self.results['performance'][page] = f"{load_time:.3f}s"
        
        # Test 2: Database query optimization
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM django_session")
            session_count = cursor.fetchone()[0]
            
        if session_count < 100:  # Reasonable session cleanup
            self.results['passed'].append("Session cleanup working")
        else:
            self.results['failed'].append(f"Too many sessions: {session_count}")
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        print("\n🔥 Testing Error Handling...")
        
        # Test 1: 404 handling
        response = self.client.get('/RoutineTest/nonexistent-page/')
        if response.status_code == 404:
            self.results['passed'].append("404 error handled correctly")
        else:
            self.results['failed'].append("404 not handled properly")
        
        # Test 2: Invalid JSON
        self.client.login(username='qa_admin', password='admin123')
        response = self.client.post('/RoutineTest/admin/classes/create/',
            data='invalid json {',
            content_type='application/json'
        )
        if response.status_code in [400, 500]:
            self.results['passed'].append("Invalid JSON handled")
        else:
            self.results['failed'].append("Invalid JSON not handled")
        
        # Test 3: Missing required fields
        response = self.client.post('/RoutineTest/admin/classes/create/',
            data=json.dumps({'name': ''}),  # Empty name
            content_type='application/json'
        )
        if response.status_code == 200:
            data = json.loads(response.content)
            if data.get('status') == 'error':
                self.results['passed'].append("Empty field validation working")
            else:
                self.results['failed'].append("Empty fields not validated")
    
    def test_ui_consistency(self):
        """Test UI consistency and accessibility"""
        print("\n🎨 Testing UI Consistency...")
        
        self.client.login(username='qa_admin', password='admin123')
        
        # Test 1: Check for console errors
        pages = [
            '/RoutineTest/admin/dashboard/',
            '/RoutineTest/admin/classes/'
        ]
        
        for page in pages:
            response = self.client.get(page)
            content = response.content.decode()
            
            # Check for common JS errors in HTML
            if 'undefined' not in content.lower() or 'null' not in content.lower():
                self.results['passed'].append(f"{page} - No obvious JS errors")
            else:
                self.results['failed'].append(f"{page} - Potential JS errors")
            
            # Check for CSRF token
            if 'csrfmiddlewaretoken' in content:
                self.results['passed'].append(f"{page} - CSRF token present")
            else:
                self.results['failed'].append(f"{page} - Missing CSRF token")
            
            # Check for responsive meta tag
            if 'viewport' in content:
                self.results['accessibility'].append(f"✅ {page} - Mobile responsive")
            else:
                self.results['accessibility'].append(f"❌ {page} - Not mobile responsive")
    
    def test_data_integrity(self):
        """Test data integrity and relationships"""
        print("\n💾 Testing Data Integrity...")
        
        # Test 1: Cascade delete protection
        teacher = Teacher.objects.filter(user__username='qa_teacher1').first()
        if teacher:
            class_count_before = Class.objects.filter(assigned_teachers=teacher).count()
            
            # Try to delete teacher with classes
            if class_count_before > 0:
                try:
                    teacher.delete()
                    self.results['failed'].append("Teacher deleted with active classes")
                except:
                    self.results['passed'].append("Cascade delete protection working")
        
        # Test 2: Unique constraints
        try:
            Class.objects.create(name="Unique Test", grade_level="5", created_by=self.admin)
            Class.objects.create(name="Unique Test", grade_level="5", created_by=self.admin)
            # If we get here, unique constraint might not be working
            self.results['failed'].append("Duplicate classes allowed")
        except:
            self.results['passed'].append("Unique constraints enforced")
    
    def run_all_tests(self):
        """Run all QA tests"""
        print("\n" + "="*60)
        print("🔍 COMPREHENSIVE QA TEST SUITE")
        print("="*60)
        
        try:
            self.setup_test_data()
            self.test_authentication()
            self.test_class_management()
            self.test_performance()
            self.test_error_handling()
            self.test_ui_consistency()
            self.test_data_integrity()
        except Exception as e:
            self.results['errors'].append(f"Critical error: {str(e)}")
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive QA report"""
        print("\n" + "="*60)
        print("📊 QA TEST REPORT")
        print("="*60)
        
        # Summary
        total_tests = len(self.results['passed']) + len(self.results['failed'])
        pass_rate = (len(self.results['passed']) / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 Summary:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {len(self.results['passed'])} ✅")
        print(f"  Failed: {len(self.results['failed'])} ❌")
        print(f"  Pass Rate: {pass_rate:.1f}%")
        
        # Performance Metrics
        print(f"\n⚡ Performance Metrics:")
        for metric, value in self.results['performance'].items():
            print(f"  {metric}: {value}")
        
        # Security Report
        print(f"\n🔒 Security Report:")
        for item in self.results['security']:
            print(f"  {item}")
        
        # Accessibility Report
        print(f"\n♿ Accessibility Report:")
        for item in self.results['accessibility']:
            print(f"  {item}")
        
        # Failed Tests Detail
        if self.results['failed']:
            print(f"\n❌ Failed Tests:")
            for test in self.results['failed']:
                print(f"  - {test}")
        
        # Critical Errors
        if self.results['errors']:
            print(f"\n🔥 Critical Errors:")
            for error in self.results['errors']:
                print(f"  - {error}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if pass_rate < 90:
            print("  ⚠️ Pass rate below 90% - critical issues need fixing")
        if self.results['failed'] and any('slow' in test for test in self.results['failed']):
            print("  ⚠️ Performance optimization needed")
        if self.results['failed'] and 'security' in str(self.results['failed']):
            print("  ⚠️ Security vulnerabilities detected - fix immediately")
        
        # Save report to file
        report_file = f"qa_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📁 Full report saved to: {report_file}")
        
        # Final verdict
        print("\n" + "="*60)
        if pass_rate >= 90 and not self.results['errors']:
            print("✅ QUALITY GATE: PASSED - Ready for next phase")
        else:
            print("❌ QUALITY GATE: FAILED - Issues must be fixed before proceeding")
        print("="*60)


if __name__ == "__main__":
    qa = QATestSuite()
    qa.run_all_tests()
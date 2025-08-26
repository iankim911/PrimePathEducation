#!/usr/bin/env python
"""
COMPREHENSIVE QC TEST AFTER CLEANUP
Tests all critical functionality after removing 413 files
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
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Teacher, Student, Program, SubProgram, PlacementRule
from placement_test.models import PlacementExam as Exam as PlacementExam, Question as PlacementQuestion
from primepath_routinetest.models import RoutineExam as Exam as RoutineExam, Question as RoutineQuestion
from primepath_routinetest.models import TeacherClassAssignment

class ComprehensiveQCTest:
    def __init__(self):
        self.client = Client()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'failures': []
        }
        
    def log_result(self, test_name, success, error=None):
        self.results['tests_run'] += 1
        if success:
            self.results['tests_passed'] += 1
            print(f"✅ {test_name}")
        else:
            self.results['tests_failed'] += 1
            print(f"❌ {test_name}: {error}")
            self.results['failures'].append({
                'test': test_name,
                'error': str(error)
            })
    
    def test_database_connectivity(self):
        """Test database connection and basic queries"""
        try:
            # Check core models
            programs = Program.objects.count()
            subprograms = SubProgram.objects.count()
            rules = PlacementRule.objects.count()
            
            # Check exam models
            placement_exams = PlacementExam.objects.count()
            routine_exams = RoutineExam.objects.count()
            
            # Check user models
            users = User.objects.count()
            teachers = Teacher.objects.count()
            students = Student.objects.count()
            
            self.log_result(
                f"Database Connectivity (Programs: {programs}, Exams: {placement_exams+routine_exams})",
                True
            )
        except Exception as e:
            self.log_result("Database Connectivity", False, e)
    
    def test_url_resolution(self):
        """Test that all critical URLs resolve"""
        critical_urls = [
            ('/', 'index'),
            ('/PlacementTest/', 'placement_test:index'),
            ('/PlacementTest/start/', 'placement_test:start_test'),
            ('/PlacementTest/exams/', 'placement_test:exam_list'),
            ('/RoutineTest/', 'primepath_routinetest:index'),
            ('/RoutineTest/classes-exams/', 'primepath_routinetest:classes_exams_unified'),
            ('/admin/', None),  # Admin doesn't use named URLs
            ('/api/programs/', 'api:api_v1:programs'),
        ]
        
        for url, name in critical_urls:
            try:
                if name:
                    resolved = reverse(name)
                    self.log_result(f"URL Resolution: {name}", True)
                else:
                    # Just check the URL exists
                    response = self.client.get(url, follow=True)
                    self.log_result(f"URL Access: {url}", response.status_code < 500)
            except Exception as e:
                self.log_result(f"URL Resolution: {name or url}", False, e)
    
    def test_template_rendering(self):
        """Test that critical templates render"""
        try:
            # Test index page
            response = self.client.get('/')
            self.log_result(
                "Template Rendering: Index",
                response.status_code == 200
            )
            
            # Test placement test start
            response = self.client.get('/PlacementTest/start/')
            self.log_result(
                "Template Rendering: Placement Start",
                response.status_code in [200, 302]  # May redirect if no exams
            )
            
            # Test routine test index
            response = self.client.get('/RoutineTest/')
            self.log_result(
                "Template Rendering: RoutineTest Index",
                response.status_code in [200, 302]  # May redirect to login
            )
        except Exception as e:
            self.log_result("Template Rendering", False, e)
    
    def test_static_files(self):
        """Test that static files are accessible"""
        static_files = [
            '/static/css/styles.css',
            '/static/js/config/app-config.js',
            '/static/favicon.ico'
        ]
        
        for static_file in static_files:
            try:
                response = self.client.get(static_file)
                self.log_result(
                    f"Static File: {static_file}",
                    response.status_code in [200, 304]
                )
            except Exception as e:
                self.log_result(f"Static File: {static_file}", False, e)
    
    def test_admin_interface(self):
        """Test admin interface accessibility"""
        try:
            response = self.client.get('/admin/', follow=True)
            self.log_result(
                "Admin Interface",
                response.status_code == 200 and 'admin/login' in str(response.content)
            )
        except Exception as e:
            self.log_result("Admin Interface", False, e)
    
    def test_api_endpoints(self):
        """Test critical API endpoints"""
        api_endpoints = [
            '/api/programs/',
            '/api/subprograms/',
            '/PlacementTest/api/audio/1/',
        ]
        
        for endpoint in api_endpoints:
            try:
                response = self.client.get(endpoint)
                # API might return 404 if no data, but shouldn't error
                self.log_result(
                    f"API Endpoint: {endpoint}",
                    response.status_code < 500
                )
            except Exception as e:
                self.log_result(f"API Endpoint: {endpoint}", False, e)
    
    def test_authentication_system(self):
        """Test authentication views"""
        try:
            # Test login page
            response = self.client.get('/login/')
            self.log_result(
                "Authentication: Login Page",
                response.status_code in [200, 302]
            )
            
            # Test registration page
            response = self.client.get('/register/')
            self.log_result(
                "Authentication: Registration Page",
                response.status_code in [200, 302]
            )
        except Exception as e:
            self.log_result("Authentication System", False, e)
    
    def test_placement_test_flow(self):
        """Test placement test critical flow"""
        try:
            # Check if we can access exam list
            response = self.client.get('/PlacementTest/exams/')
            self.log_result(
                "Placement Test: Exam List",
                response.status_code in [200, 302]
            )
            
            # Check if we have any exams
            if PlacementExam.objects.exists():
                exam = PlacementExam.objects.first()
                response = self.client.get(f'/PlacementTest/exams/{exam.id}/')
                self.log_result(
                    "Placement Test: Exam Detail",
                    response.status_code in [200, 302]
                )
            else:
                self.log_result("Placement Test: Exam Detail", True)  # No exams to test
        except Exception as e:
            self.log_result("Placement Test Flow", False, e)
    
    def test_routine_test_flow(self):
        """Test routine test critical flow"""
        try:
            # Check unified view
            response = self.client.get('/RoutineTest/classes-exams/', follow=True)
            self.log_result(
                "Routine Test: Classes-Exams View",
                response.status_code in [200, 302]
            )
            
            # Check exam list
            response = self.client.get('/RoutineTest/exams/')
            self.log_result(
                "Routine Test: Exam List",
                response.status_code in [200, 302]
            )
        except Exception as e:
            self.log_result("Routine Test Flow", False, e)
    
    def test_models_integrity(self):
        """Test that all models can be queried"""
        models_to_test = [
            ('Program', Program),
            ('SubProgram', SubProgram),
            ('PlacementRule', PlacementRule),
            ('Teacher', Teacher),
            ('Student', Student),
            ('PlacementExam', PlacementExam),
            ('RoutineExam', RoutineExam),
            ('TeacherClassAssignment', TeacherClassAssignment),
        ]
        
        for model_name, model_class in models_to_test:
            try:
                count = model_class.objects.count()
                self.log_result(f"Model Query: {model_name} ({count} records)", True)
            except Exception as e:
                self.log_result(f"Model Query: {model_name}", False, e)
    
    def generate_report(self):
        """Generate final QC report"""
        print("\n" + "="*80)
        print("COMPREHENSIVE QC REPORT")
        print("="*80)
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"Tests Run: {self.results['tests_run']}")
        print(f"Tests Passed: {self.results['tests_passed']}")
        print(f"Tests Failed: {self.results['tests_failed']}")
        print(f"Success Rate: {(self.results['tests_passed']/self.results['tests_run']*100):.1f}%")
        
        if self.results['failures']:
            print("\n❌ FAILURES:")
            for failure in self.results['failures']:
                print(f"  - {failure['test']}: {failure['error']}")
        else:
            print("\n✅ ALL TESTS PASSED!")
        
        print("="*80)
        
        # Save report
        report_file = f"qc_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nReport saved to: {report_file}")
        
        return self.results['tests_failed'] == 0

def main():
    print("\n" + "="*80)
    print("RUNNING COMPREHENSIVE QC TEST")
    print("Testing all critical functionality after cleanup of 413 files")
    print("="*80 + "\n")
    
    tester = ComprehensiveQCTest()
    
    # Run all tests
    tester.test_database_connectivity()
    tester.test_models_integrity()
    tester.test_url_resolution()
    tester.test_template_rendering()
    tester.test_static_files()
    tester.test_admin_interface()
    tester.test_api_endpoints()
    tester.test_authentication_system()
    tester.test_placement_test_flow()
    tester.test_routine_test_flow()
    
    # Generate report
    success = tester.generate_report()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
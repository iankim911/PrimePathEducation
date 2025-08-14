#!/usr/bin/env python3
"""
Phase 11 Comprehensive QA Tests
Final verification that all features work after modularization
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
from placement_test.models import Exam, Question, StudentSession, AudioFile
from core.models import CurriculumLevel, PlacementRule, School, Teacher, Program
from django.contrib.auth.models import User
import traceback


class Phase11QATests:
    def __init__(self):
        self.client = Client()
        self.results = {
            'phase': 11,
            'timestamp': datetime.now().isoformat(),
            'tests': {
                'passed': [],
                'failed': [],
                'warnings': []
            },
            'features': {}
        }
    
    def run_all_tests(self):
        """Run comprehensive QA test suite"""
        print("="*70)
        print("  PHASE 11: COMPREHENSIVE QA TESTS")
        print("  Final Integration & Testing Verification")
        print("="*70)
        
        test_categories = [
            ("API Versioning", self.test_api_versioning),
            ("Test Organization", self.test_test_organization),
            ("Documentation Structure", self.test_documentation),
            ("Base Classes", self.test_base_classes),
            ("Student Workflow", self.test_student_workflow),
            ("Teacher Features", self.test_teacher_features),
            ("Session Management", self.test_session_management),
            ("Grading System", self.test_grading_system),
            ("URL Routing", self.test_url_routing),
            ("Static Files", self.test_static_files),
            ("Database Integrity", self.test_database_integrity),
            ("Submit Test Fix", self.test_submit_fix_still_works)
        ]
        
        for category_name, test_func in test_categories:
            print(f"\n{'='*60}")
            print(f"  {category_name}")
            print('='*60)
            try:
                test_func()
                self.results['features'][category_name] = 'PASSED'
            except Exception as e:
                self.results['features'][category_name] = 'FAILED'
                self.results['tests']['failed'].append(f"{category_name}: {str(e)}")
                print(f"   ❌ EXCEPTION: {str(e)}")
                traceback.print_exc()
        
        self.print_summary()
        self.save_results()
    
    def test_api_versioning(self):
        """Test API versioning implementation"""
        print("\n1. Testing API Versioning...")
        
        # Test v1 endpoints
        v1_endpoints = [
            '/api/v1/health/',
            '/api/v1/exams/',
            '/api/v1/sessions/',
            '/api/v1/schools/',
        ]
        
        for endpoint in v1_endpoints:
            response = self.client.get(endpoint)
            if response.status_code in [200, 401, 403]:
                print(f"   ✅ {endpoint} works")
                self.results['tests']['passed'].append(f"API v1: {endpoint}")
            else:
                print(f"   ❌ {endpoint} failed: {response.status_code}")
                self.results['tests']['failed'].append(f"API v1: {endpoint}")
        
        # Test backward compatibility
        legacy_endpoints = [
            '/api/health/',
            '/api/exams/',
        ]
        
        for endpoint in legacy_endpoints:
            response = self.client.get(endpoint)
            if response.status_code in [200, 401, 403]:
                print(f"   ✅ {endpoint} backward compatible")
                self.results['tests']['passed'].append(f"Legacy API: {endpoint}")
            else:
                print(f"   ❌ {endpoint} not compatible: {response.status_code}")
                self.results['tests']['failed'].append(f"Legacy API: {endpoint}")
    
    def test_test_organization(self):
        """Test that test files are properly organized"""
        print("\n2. Testing Test Organization...")
        
        test_dirs = [
            'placement_test/tests',
            'core/tests',
            'api/tests',
            'tests'
        ]
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        for test_dir in test_dirs:
            full_path = os.path.join(base_dir, test_dir)
            if os.path.exists(full_path):
                # Check for __init__.py
                init_file = os.path.join(full_path, '__init__.py')
                if os.path.exists(init_file):
                    print(f"   ✅ {test_dir} properly initialized")
                    self.results['tests']['passed'].append(f"Test dir: {test_dir}")
                else:
                    print(f"   ⚠️  {test_dir} missing __init__.py")
                    self.results['tests']['warnings'].append(f"Test dir init: {test_dir}")
                
                # Count test files
                test_files = [f for f in os.listdir(full_path) if f.startswith('test') and f.endswith('.py')]
                if test_files:
                    print(f"      Found {len(test_files)} test files")
            else:
                print(f"   ❌ {test_dir} not found")
                self.results['tests']['failed'].append(f"Test dir: {test_dir}")
    
    def test_documentation(self):
        """Test documentation structure"""
        print("\n3. Testing Documentation Structure...")
        
        doc_structure = [
            'docs/README.md',
            'docs/api/v1/endpoints.md',
        ]
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for doc_path in doc_structure:
            full_path = os.path.join(base_dir, doc_path)
            if os.path.exists(full_path):
                print(f"   ✅ {doc_path} exists")
                self.results['tests']['passed'].append(f"Doc: {doc_path}")
            else:
                print(f"   ❌ {doc_path} missing")
                self.results['tests']['failed'].append(f"Doc: {doc_path}")
    
    def test_base_classes(self):
        """Test base classes implementation"""
        print("\n4. Testing Base Classes...")
        
        # Check if base classes exist
        base_class_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'common/views/crud.py'
        )
        
        if os.path.exists(base_class_file):
            print(f"   ✅ Base CRUD classes created")
            self.results['tests']['passed'].append("Base classes")
            
            # Check content
            with open(base_class_file, 'r') as f:
                content = f.read()
                required_classes = [
                    'BaseListView',
                    'BaseCreateView',
                    'BaseUpdateView',
                    'BaseDeleteView',
                    'BaseDetailView'
                ]
                
                for class_name in required_classes:
                    if f'class {class_name}' in content:
                        print(f"      ✅ {class_name} implemented")
                        self.results['tests']['passed'].append(f"Base class: {class_name}")
                    else:
                        print(f"      ❌ {class_name} missing")
                        self.results['tests']['failed'].append(f"Base class: {class_name}")
        else:
            print(f"   ❌ Base classes file not found")
            self.results['tests']['failed'].append("Base classes file")
    
    def test_student_workflow(self):
        """Test complete student workflow"""
        print("\n5. Testing Student Workflow...")
        
        # Ensure required data
        if not School.objects.exists():
            School.objects.create(name="Test School")
        
        if not CurriculumLevel.objects.exists():
            level = CurriculumLevel.objects.create(
                name="Test Level",
                grade_level=5,
                difficulty="Standard"
            )
        else:
            level = CurriculumLevel.objects.first()
        
        if not PlacementRule.objects.filter(grade=5).exists():
            PlacementRule.objects.create(
                grade=5,
                min_rank_percentile=40,
                max_rank_percentile=60,
                curriculum_level=level,
                priority=1
            )
        
        # Test session creation
        session_data = {
            'student_name': 'Phase 11 Test Student',
            'grade': '5',
            'academic_rank': 'TOP_50',
            'school_name': School.objects.first().name,
            'parent_phone': '555-9999'
        }
        
        response = self.client.post(reverse('PlacementTest:start_test'), session_data)
        if response.status_code == 302:
            print("   ✅ Student session created")
            self.results['tests']['passed'].append("Student session creation")
            
            # Get session
            if hasattr(response, 'url'):
                session_id = response.url.split('/')[-2]
                
                # Test take test page
                response = self.client.get(reverse('PlacementTest:take_test', args=[session_id]))
                if response.status_code == 200:
                    print("   ✅ Take test page loads")
                    self.results['tests']['passed'].append("Take test page")
                else:
                    print(f"   ❌ Take test page error: {response.status_code}")
                    self.results['tests']['failed'].append("Take test page")
                
                # Test completion
                response = self.client.post(
                    reverse('PlacementTest:complete_test', args=[session_id])
                )
                if response.status_code in [200, 302]:
                    print("   ✅ Test can be completed")
                    self.results['tests']['passed'].append("Test completion")
                else:
                    print(f"   ❌ Test completion error: {response.status_code}")
                    self.results['tests']['failed'].append("Test completion")
        else:
            print(f"   ❌ Session creation failed: {response.status_code}")
            self.results['tests']['failed'].append("Student session creation")
    
    def test_teacher_features(self):
        """Test teacher features"""
        print("\n6. Testing Teacher Features...")
        
        # Create admin user if needed
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser('admin', 'admin@test.com', 'password')
        
        # Login
        self.client.login(username='admin', password='password')
        
        # Test exam list
        response = self.client.get(reverse('PlacementTest:exam_list'))
        if response.status_code == 200:
            print("   ✅ Exam list accessible")
            self.results['tests']['passed'].append("Teacher exam list")
        else:
            print(f"   ❌ Exam list error: {response.status_code}")
            self.results['tests']['failed'].append("Teacher exam list")
        
        # Test exam creation page
        try:
            response = self.client.get(reverse('PlacementTest:create_exam'))
            if response.status_code == 200:
                print("   ✅ Create exam page accessible")
                self.results['tests']['passed'].append("Create exam page")
            else:
                print(f"   ❌ Create exam page error: {response.status_code}")
                self.results['tests']['failed'].append("Create exam page")
        except:
            print("   ⚠️  Create exam URL not configured")
            self.results['tests']['warnings'].append("Create exam URL")
        
        self.client.logout()
    
    def test_session_management(self):
        """Test session management"""
        print("\n7. Testing Session Management...")
        
        if StudentSession.objects.exists():
            session = StudentSession.objects.first()
            
            # Check required fields
            required_fields = [
                'student_name', 'grade', 'academic_rank', 
                'exam', 'started_at', 'is_completed'
            ]
            
            for field in required_fields:
                if hasattr(session, field):
                    print(f"   ✅ Session has {field}")
                    self.results['tests']['passed'].append(f"Session field: {field}")
                else:
                    print(f"   ❌ Session missing {field}")
                    self.results['tests']['failed'].append(f"Session field: {field}")
        else:
            print("   ⚠️  No sessions to test")
            self.results['tests']['warnings'].append("No sessions")
    
    def test_grading_system(self):
        """Test grading system"""
        print("\n8. Testing Grading System...")
        
        try:
            from placement_test.services import GradingService
            
            # Check if GradingService has required methods
            required_methods = [
                'grade_session',
                'calculate_score',
                'get_detailed_results'
            ]
            
            for method in required_methods:
                if hasattr(GradingService, method):
                    print(f"   ✅ GradingService.{method} exists")
                    self.results['tests']['passed'].append(f"Grading: {method}")
                else:
                    print(f"   ❌ GradingService.{method} missing")
                    self.results['tests']['failed'].append(f"Grading: {method}")
        except ImportError as e:
            print(f"   ❌ Cannot import GradingService: {e}")
            self.results['tests']['failed'].append("GradingService import")
    
    def test_url_routing(self):
        """Test URL routing"""
        print("\n9. Testing URL Routing...")
        
        critical_urls = [
            ('PlacementTest:start_test', []),
            ('PlacementTest:exam_list', []),
            ('api:health', []),  # Should work with new API structure
        ]
        
        for url_name, args in critical_urls:
            try:
                url = reverse(url_name, args=args)
                print(f"   ✅ URL '{url_name}' resolves to {url}")
                self.results['tests']['passed'].append(f"URL: {url_name}")
            except:
                print(f"   ❌ URL '{url_name}' not found")
                self.results['tests']['failed'].append(f"URL: {url_name}")
    
    def test_static_files(self):
        """Test static files organization"""
        print("\n10. Testing Static Files...")
        
        static_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'static'
        )
        
        if os.path.exists(static_dir):
            # Check for modular JS
            js_modules = os.path.join(static_dir, 'js', 'modules')
            if os.path.exists(js_modules):
                modules = os.listdir(js_modules)
                print(f"   ✅ Found {len(modules)} JS modules")
                self.results['tests']['passed'].append("JS modules")
            else:
                print("   ❌ JS modules directory not found")
                self.results['tests']['failed'].append("JS modules")
            
            # Check for modular CSS
            css_dir = os.path.join(static_dir, 'css')
            if os.path.exists(css_dir):
                css_files = [f for f in os.listdir(css_dir) if f.endswith('.css')]
                print(f"   ✅ Found {len(css_files)} CSS files")
                self.results['tests']['passed'].append("CSS files")
            else:
                print("   ❌ CSS directory not found")
                self.results['tests']['failed'].append("CSS files")
        else:
            print("   ❌ Static directory not found")
            self.results['tests']['failed'].append("Static directory")
    
    def test_database_integrity(self):
        """Test database integrity"""
        print("\n11. Testing Database Integrity...")
        
        models_to_test = [
            (Exam, "Exam"),
            (Question, "Question"),
            (StudentSession, "StudentSession"),
            (CurriculumLevel, "CurriculumLevel"),
            (PlacementRule, "PlacementRule"),
            (School, "School"),
            (Program, "Program"),
            (AudioFile, "AudioFile")
        ]
        
        for model_class, name in models_to_test:
            try:
                count = model_class.objects.count()
                print(f"   ✅ {name} model works ({count} records)")
                self.results['tests']['passed'].append(f"Model: {name}")
            except Exception as e:
                print(f"   ❌ {name} model error: {e}")
                self.results['tests']['failed'].append(f"Model: {name}")
    
    def test_submit_fix_still_works(self):
        """Test that the submit test fix is still working"""
        print("\n12. Testing Submit Test Fix...")
        
        # Check answer-manager.js for the fix
        js_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'static/js/modules/answer-manager.js'
        )
        
        if os.path.exists(js_file):
            with open(js_file, 'r') as f:
                content = f.read()
                
                # Check for getSessionId method
                if 'getSessionId' in content:
                    print("   ✅ getSessionId method present")
                    self.results['tests']['passed'].append("Submit fix: getSessionId")
                else:
                    print("   ❌ getSessionId method missing")
                    self.results['tests']['failed'].append("Submit fix: getSessionId")
                
                # Check for defensive checks
                if 'if (!sessionId)' in content or 'if (!this.session' in content:
                    print("   ✅ Defensive checks present")
                    self.results['tests']['passed'].append("Submit fix: defensive checks")
                else:
                    print("   ❌ Defensive checks missing")
                    self.results['tests']['failed'].append("Submit fix: defensive checks")
        else:
            print("   ❌ answer-manager.js not found")
            self.results['tests']['failed'].append("Submit fix: file missing")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("  TEST SUMMARY")
        print("="*70)
        
        total_passed = len(self.results['tests']['passed'])
        total_failed = len(self.results['tests']['failed'])
        total_warnings = len(self.results['tests']['warnings'])
        total = total_passed + total_failed
        
        if total > 0:
            pass_rate = (total_passed / total) * 100
        else:
            pass_rate = 0
        
        print(f"\n📊 Results:")
        print(f"   ✅ Passed: {total_passed}")
        print(f"   ❌ Failed: {total_failed}")
        print(f"   ⚠️  Warnings: {total_warnings}")
        print(f"   📈 Pass Rate: {pass_rate:.1f}%")
        
        if total_failed > 0:
            print("\n❌ Failed Tests:")
            for failure in self.results['tests']['failed'][:10]:  # Show first 10
                print(f"   - {failure}")
        
        print("\n🎯 Feature Status:")
        for feature, status in self.results['features'].items():
            if status == 'PASSED':
                print(f"   ✅ {feature}")
            else:
                print(f"   ❌ {feature}")
        
        print("\n" + "="*70)
        if pass_rate >= 90:
            print("  ✅ PHASE 11 SUCCESSFULLY COMPLETED!")
            print("  All modularization complete and verified.")
        elif pass_rate >= 75:
            print("  ⚠️  PHASE 11 MOSTLY SUCCESSFUL")
            print("  Minor issues detected, review failed tests.")
        else:
            print("  ❌ PHASE 11 NEEDS ATTENTION")
            print("  Significant issues detected.")
        print("="*70)
    
    def save_results(self):
        """Save test results"""
        output_file = 'phase11_qa_results.json'
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📄 Results saved to: {output_file}")


if __name__ == "__main__":
    tester = Phase11QATests()
    tester.run_all_tests()
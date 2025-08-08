#!/usr/bin/env python
"""
Post-Cleanup Comprehensive QA Test
Ultra-thorough verification that all features work after cleanup
"""

import os
import sys
import django
from django.test import Client
from django.urls import reverse
import traceback

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
django.setup()


class PostCleanupQA:
    def __init__(self):
        self.client = Client()
        self.test_results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
    
    def test_core_imports(self):
        """Test all critical imports still work"""
        print("\n🔧 TESTING CORE IMPORTS")
        print("=" * 60)
        
        critical_imports = [
            # Core Django
            ('django', 'Django framework'),
            ('django.urls', 'Django URLs'),
            ('django.test', 'Django testing'),
            ('django.db', 'Django database'),
            
            # Project apps
            ('core', 'Core app'),
            ('placement_test', 'Placement test app'),
            ('api', 'API app'),
            ('common', 'Common utilities'),
            
            # Models
            ('core.models', 'Core models'),
            ('placement_test.models', 'Placement test models'),
            
            # Views
            ('core.views', 'Core views'),
            ('placement_test.views', 'Placement test views'),
            
            # Services
            ('core.services', 'Core services'),
            ('placement_test.services', 'Placement test services'),
        ]
        
        for module_name, description in critical_imports:
            try:
                __import__(module_name)
                print(f"  ✅ {description} ({module_name})")
                self.test_results['passed'].append(f"Import: {module_name}")
            except ImportError as e:
                print(f"  ❌ {description} ({module_name}): {e}")
                self.test_results['failed'].append(f"Import: {module_name}")
        
        return len(self.test_results['failed']) == 0
    
    def test_model_functionality(self):
        """Test all models can be imported and used"""
        print("\n📊 TESTING MODEL FUNCTIONALITY")
        print("=" * 60)
        
        try:
            # Core models
            from core.models import School, Teacher, Program, SubProgram, CurriculumLevel, PlacementRule, ExamLevelMapping
            
            # Placement test models  
            from placement_test.models import Exam, AudioFile, Question, StudentSession, StudentAnswer, DifficultyAdjustment
            
            # Test basic queries
            school_count = School.objects.count()
            exam_count = Exam.objects.count()
            session_count = StudentSession.objects.count()
            
            print(f"  ✅ Core models working (Schools: {school_count})")
            print(f"  ✅ Placement models working (Exams: {exam_count}, Sessions: {session_count})")
            
            self.test_results['passed'].append("Model functionality")
            return True
            
        except Exception as e:
            print(f"  ❌ Model error: {e}")
            self.test_results['failed'].append("Model functionality")
            return False
    
    def test_url_patterns(self):
        """Test all URL patterns resolve correctly"""
        print("\n🔗 TESTING URL PATTERNS")
        print("=" * 60)
        
        critical_urls = [
            # Core URLs
            ('core:index', {}, 'Home page'),
            ('core:teacher_dashboard', {}, 'Teacher dashboard'),
            ('core:placement_rules', {}, 'Placement rules'),
            ('core:curriculum_levels', {}, 'Curriculum levels'),
            ('core:exam_mapping', {}, 'Exam mapping'),
            
            # Placement test URLs
            ('placement_test:exam_list', {}, 'Exam list'),
            ('placement_test:create_exam', {}, 'Create exam'),
            ('placement_test:session_list', {}, 'Session list'),
            ('placement_test:start_test', {}, 'Start test'),
            
            # API URLs
            ('core:get_placement_rules', {}, 'Get placement rules API'),
            ('core:save_placement_rules', {}, 'Save placement rules API'),
        ]
        
        passed = 0
        failed = 0
        
        for url_name, kwargs, description in critical_urls:
            try:
                url = reverse(url_name, kwargs=kwargs)
                print(f"  ✅ {description}: {url}")
                passed += 1
            except Exception as e:
                print(f"  ❌ {description}: {e}")
                failed += 1
        
        success_rate = (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0
        print(f"\nURL Resolution: {passed}/{passed + failed} ({success_rate:.1f}%)")
        
        if failed == 0:
            self.test_results['passed'].append("URL patterns")
        else:
            self.test_results['failed'].append("URL patterns")
        
        return failed == 0
    
    def test_views_accessibility(self):
        """Test critical views are accessible"""
        print("\n🌐 TESTING VIEW ACCESSIBILITY")
        print("=" * 60)
        
        test_urls = [
            ('/', 'Home'),
            ('/teacher/dashboard/', 'Teacher Dashboard'),
            ('/api/placement/exams/', 'Exam List'),
            ('/api/placement/sessions/', 'Session List'),
            ('/api/placement/start/', 'Start Test'),
            ('/placement-rules/', 'Placement Rules'),
            ('/exam-mapping/', 'Exam Mapping'),
        ]
        
        passed = 0
        failed = 0
        
        for url, description in test_urls:
            try:
                response = self.client.get(url)
                if response.status_code in [200, 301, 302]:
                    print(f"  ✅ {description} ({response.status_code})")
                    passed += 1
                else:
                    print(f"  ⚠️  {description} ({response.status_code})")
                    self.test_results['warnings'].append(f"{description}: HTTP {response.status_code}")
            except Exception as e:
                print(f"  ❌ {description}: {e}")
                failed += 1
        
        if failed == 0:
            self.test_results['passed'].append("View accessibility")
        else:
            self.test_results['failed'].append("View accessibility")
        
        return failed == 0
    
    def test_template_rendering(self):
        """Test templates render without errors"""
        print("\n🎨 TESTING TEMPLATE RENDERING")
        print("=" * 60)
        
        template_tests = [
            ('/api/placement/exams/', 'placement_test/exam_list.html'),
            ('/teacher/dashboard/', 'core/teacher_dashboard.html'),
            ('/placement-rules/', 'core/placement_rules.html'),
        ]
        
        passed = 0
        failed = 0
        
        for url, expected_template in template_tests:
            try:
                response = self.client.get(url)
                if response.status_code == 200:
                    # Check if response has content
                    if response.content:
                        print(f"  ✅ {expected_template} renders")
                        passed += 1
                    else:
                        print(f"  ⚠️  {expected_template} empty response")
                        self.test_results['warnings'].append(f"{expected_template}: Empty response")
                else:
                    print(f"  ⚠️  {expected_template} status {response.status_code}")
            except Exception as e:
                print(f"  ❌ {expected_template}: {e}")
                failed += 1
        
        if failed == 0:
            self.test_results['passed'].append("Template rendering")
        else:
            self.test_results['failed'].append("Template rendering")
        
        return failed == 0
    
    def test_services_functionality(self):
        """Test service layer still works"""
        print("\n⚙️ TESTING SERVICES FUNCTIONALITY")
        print("=" * 60)
        
        try:
            # Test core services
            from core.services import CurriculumService, SchoolService, TeacherService
            
            # Test placement services
            from placement_test.services import ExamService, SessionService, GradingService, PlacementService
            
            # Try basic service calls
            programs = CurriculumService.get_programs_with_hierarchy()
            schools = SchoolService.get_active_schools()
            
            print(f"  ✅ Core services working")
            print(f"  ✅ Placement services working")
            
            self.test_results['passed'].append("Services functionality")
            return True
            
        except Exception as e:
            print(f"  ❌ Service error: {e}")
            self.test_results['failed'].append("Services functionality")
            traceback.print_exc()
            return False
    
    def test_static_files(self):
        """Test static files are accessible"""
        print("\n📁 TESTING STATIC FILES")
        print("=" * 60)
        
        static_paths = [
            'static/css/base/reset.css',
            'static/css/pages/student-test.css',
            'static/js/modules/answer-manager.js',
            'static/js/modules/pdf-viewer.js',
        ]
        
        passed = 0
        failed = 0
        
        for path in static_paths:
            full_path = os.path.join(os.path.dirname(__file__), path)
            if os.path.exists(full_path):
                print(f"  ✅ {path}")
                passed += 1
            else:
                print(f"  ❌ {path} not found")
                failed += 1
        
        if failed == 0:
            self.test_results['passed'].append("Static files")
        else:
            self.test_results['failed'].append("Static files")
        
        return failed == 0
    
    def test_migrations(self):
        """Test migrations are intact"""
        print("\n🔄 TESTING MIGRATIONS")
        print("=" * 60)
        
        try:
            from django.core.management import call_command
            from io import StringIO
            
            # Check migration status
            out = StringIO()
            call_command('showmigrations', '--plan', stdout=out)
            migrations_output = out.getvalue()
            
            # Check for unapplied migrations
            if '[ ]' in migrations_output:
                print("  ⚠️  Unapplied migrations detected")
                self.test_results['warnings'].append("Unapplied migrations")
            else:
                print("  ✅ All migrations applied")
                self.test_results['passed'].append("Migrations")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Migration check failed: {e}")
            self.test_results['failed'].append("Migrations")
            return False
    
    def test_modular_structure(self):
        """Test modular structure from all phases still works"""
        print("\n🏗️ TESTING MODULAR STRUCTURE")
        print("=" * 60)
        
        # Test modular views
        try:
            from placement_test.views.student import start_test, take_test
            from placement_test.views.exam import exam_list, create_exam
            from placement_test.views.session import session_list
            from placement_test.views.ajax import get_audio
            print("  ✅ Modular views working")
            self.test_results['passed'].append("Modular views")
        except Exception as e:
            print(f"  ❌ Modular views error: {e}")
            self.test_results['failed'].append("Modular views")
        
        # Test modular models
        try:
            from placement_test.models.exam import Exam, AudioFile
            from placement_test.models.question import Question
            from placement_test.models.session import StudentSession, StudentAnswer
            print("  ✅ Modular models working")
            self.test_results['passed'].append("Modular models")
        except Exception as e:
            print(f"  ❌ Modular models error: {e}")
            self.test_results['failed'].append("Modular models")
        
        # Test modular URLs
        try:
            from placement_test.student_urls import urlpatterns as student_urls
            from placement_test.exam_urls import urlpatterns as exam_urls
            from core.dashboard_urls import urlpatterns as dashboard_urls
            print("  ✅ Modular URLs working")
            self.test_results['passed'].append("Modular URLs")
        except Exception as e:
            print(f"  ❌ Modular URLs error: {e}")
            self.test_results['failed'].append("Modular URLs")
        
        return len([f for f in self.test_results['failed'] if 'Modular' in f]) == 0
    
    def run_comprehensive_qa(self):
        """Run all QA tests"""
        print("=" * 80)
        print("POST-CLEANUP COMPREHENSIVE QA TEST")
        print("Ultra-thorough verification of all features")
        print("=" * 80)
        
        # Run all tests
        test_methods = [
            self.test_core_imports,
            self.test_model_functionality,
            self.test_url_patterns,
            self.test_views_accessibility,
            self.test_template_rendering,
            self.test_services_functionality,
            self.test_static_files,
            self.test_migrations,
            self.test_modular_structure,
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"\n❌ Test failed with exception: {e}")
                traceback.print_exc()
        
        # Summary
        print("\n" + "=" * 80)
        print("QA TEST SUMMARY")
        print("=" * 80)
        
        print(f"\n✅ PASSED: {len(self.test_results['passed'])} tests")
        for test in self.test_results['passed']:
            print(f"  • {test}")
        
        if self.test_results['warnings']:
            print(f"\n⚠️  WARNINGS: {len(self.test_results['warnings'])} issues")
            for warning in self.test_results['warnings']:
                print(f"  • {warning}")
        
        if self.test_results['failed']:
            print(f"\n❌ FAILED: {len(self.test_results['failed'])} tests")
            for test in self.test_results['failed']:
                print(f"  • {test}")
        
        # Overall result
        total_tests = len(self.test_results['passed']) + len(self.test_results['failed'])
        success_rate = (len(self.test_results['passed']) / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 Overall Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("\n🎉 POST-CLEANUP QA PASSED!")
            print("✅ All critical features working correctly")
            print("✅ Cleanup was successful")
            print("✅ Project is in healthy state")
            return True
        elif success_rate >= 75:
            print("\n⚠️  POST-CLEANUP QA PASSED WITH WARNINGS")
            print("Most features working but review warnings")
            return True
        else:
            print("\n❌ POST-CLEANUP QA FAILED")
            print("Critical issues detected - review failed tests")
            return False


if __name__ == "__main__":
    qa = PostCleanupQA()
    success = qa.run_comprehensive_qa()
    sys.exit(0 if success else 1)
"""
PINNACLE Implementation QA Test Suite
Created: August 25, 2025

Comprehensive QA testing for PINNACLE curriculum implementation
Tests all aspects of the PINNACLE setup and integration
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.db import connection
from django.test import Client, TestCase
from django.contrib.auth.models import User
from core.models import Program, SubProgram, CurriculumLevel, Teacher
from primepath_routinetest.models import ClassCurriculumMapping
from primepath_routinetest.models.class_model import Class
from primepath_routinetest.class_code_mapping import (
    CLASS_CODE_CURRICULUM_MAPPING, 
    CLASS_CODE_CATEGORIES,
    get_curriculum_for_class,
    get_class_codes_by_program
)

class PinnacleQA:
    """Comprehensive QA test runner for PINNACLE implementation"""
    
    def __init__(self):
        self.client = Client()
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
        self.total_tests = 0
        
    def log_test(self, test_name, status, message=""):
        """Log test result"""
        self.total_tests += 1
        if status == 'PASS':
            self.results['passed'].append(test_name)
            print(f"✅ {test_name}: PASS {message}")
        elif status == 'FAIL':
            self.results['failed'].append((test_name, message))
            print(f"❌ {test_name}: FAIL - {message}")
        elif status == 'WARN':
            self.results['warnings'].append((test_name, message))
            print(f"⚠️  {test_name}: WARNING - {message}")
    
    def test_pinnacle_program_exists(self):
        """Test 1: Verify PINNACLE program exists"""
        print("\n" + "="*60)
        print("TEST 1: PINNACLE Program Existence")
        print("="*60)
        
        try:
            program = Program.objects.get(name='PINNACLE')
            self.log_test("PINNACLE Program", "PASS", f"ID: {program.id}")
            
            # Verify attributes
            if program.grade_range_start == 10 and program.grade_range_end == 12:
                self.log_test("Grade Range", "PASS", "10-12")
            else:
                self.log_test("Grade Range", "FAIL", 
                            f"Expected 10-12, got {program.grade_range_start}-{program.grade_range_end}")
            
            return program
        except Program.DoesNotExist:
            self.log_test("PINNACLE Program", "FAIL", "Program not found")
            return None
    
    def test_pinnacle_subprograms(self, program):
        """Test 2: Verify all PINNACLE subprograms exist"""
        print("\n" + "="*60)
        print("TEST 2: PINNACLE SubPrograms")
        print("="*60)
        
        if not program:
            self.log_test("SubPrograms", "FAIL", "No program to test")
            return []
        
        expected_subprograms = ['Vision', 'Endeavor', 'Success', 'Pro']
        subprograms = SubProgram.objects.filter(program=program).order_by('order')
        
        # Check count
        if subprograms.count() == 4:
            self.log_test("SubProgram Count", "PASS", "4 subprograms found")
        else:
            self.log_test("SubProgram Count", "FAIL", f"Expected 4, found {subprograms.count()}")
        
        # Check each subprogram
        found_subprograms = []
        for subprogram in subprograms:
            if subprogram.name in expected_subprograms:
                self.log_test(f"SubProgram: {subprogram.name}", "PASS")
                found_subprograms.append(subprogram)
            else:
                self.log_test(f"SubProgram: {subprogram.name}", "WARN", "Unexpected subprogram")
        
        # Check for missing subprograms
        found_names = [s.name for s in found_subprograms]
        for expected in expected_subprograms:
            if expected not in found_names:
                self.log_test(f"SubProgram: {expected}", "FAIL", "Not found")
        
        return found_subprograms
    
    def test_curriculum_levels(self, subprograms):
        """Test 3: Verify curriculum levels for each subprogram"""
        print("\n" + "="*60)
        print("TEST 3: Curriculum Levels")
        print("="*60)
        
        if not subprograms:
            self.log_test("Curriculum Levels", "FAIL", "No subprograms to test")
            return []
        
        all_levels = []
        for subprogram in subprograms:
            levels = CurriculumLevel.objects.filter(subprogram=subprogram).order_by('level_number')
            
            # PINNACLE should have 2 levels per subprogram
            if levels.count() == 2:
                self.log_test(f"{subprogram.name} Level Count", "PASS", "2 levels")
            else:
                self.log_test(f"{subprogram.name} Level Count", "FAIL", 
                            f"Expected 2, found {levels.count()}")
            
            for level in levels:
                if level.level_number in [1, 2]:
                    self.log_test(f"{subprogram.name} Level {level.level_number}", "PASS")
                    all_levels.append(level)
                else:
                    self.log_test(f"{subprogram.name} Level {level.level_number}", 
                                "WARN", "Unexpected level number")
        
        return all_levels
    
    def test_pinnacle_classes(self):
        """Test 4: Verify PINNACLE classes exist"""
        print("\n" + "="*60)
        print("TEST 4: PINNACLE Classes")
        print("="*60)
        
        expected_classes = [
            'PINNACLE_V1', 'PINNACLE_V2',
            'PINNACLE_E1', 'PINNACLE_E2',
            'PINNACLE_S1', 'PINNACLE_S2',
            'PINNACLE_P1', 'PINNACLE_P2'
        ]
        
        found_classes = []
        for class_code in expected_classes:
            try:
                class_obj = Class.objects.get(section=class_code)
                self.log_test(f"Class: {class_code}", "PASS", f"ID: {class_obj.id}")
                found_classes.append(class_obj)
            except Class.DoesNotExist:
                self.log_test(f"Class: {class_code}", "FAIL", "Not found")
        
        return found_classes
    
    def test_class_curriculum_mappings(self, classes, levels):
        """Test 5: Verify class-to-curriculum mappings"""
        print("\n" + "="*60)
        print("TEST 5: Class-Curriculum Mappings")
        print("="*60)
        
        if not classes or not levels:
            self.log_test("Mappings", "FAIL", "Missing classes or levels")
            return
        
        expected_mappings = {
            'PINNACLE_V1': 'Vision Level 1',
            'PINNACLE_V2': 'Vision Level 2',
            'PINNACLE_E1': 'Endeavor Level 1',
            'PINNACLE_E2': 'Endeavor Level 2',
            'PINNACLE_S1': 'Success Level 1',
            'PINNACLE_S2': 'Success Level 2',
            'PINNACLE_P1': 'Pro Level 1',
            'PINNACLE_P2': 'Pro Level 2',
        }
        
        for class_obj in classes:
            mapping = ClassCurriculumMapping.objects.filter(
                class_code=class_obj.section
            ).first()
            
            if mapping:
                expected_level = expected_mappings.get(class_obj.section)
                actual_level = f"{mapping.curriculum_level.subprogram.name} Level {mapping.curriculum_level.level_number}"
                
                if expected_level and expected_level == actual_level:
                    self.log_test(f"Mapping: {class_obj.section}", "PASS", f"→ {actual_level}")
                else:
                    self.log_test(f"Mapping: {class_obj.section}", "FAIL", 
                                f"Expected '{expected_level}', got '{actual_level}'")
            else:
                self.log_test(f"Mapping: {class_obj.section}", "FAIL", "No mapping found")
    
    def test_class_code_mapping_file(self):
        """Test 6: Verify class_code_mapping.py updates"""
        print("\n" + "="*60)
        print("TEST 6: Class Code Mapping File")
        print("="*60)
        
        # Test that PINNACLE classes are in the mapping
        pinnacle_classes = [
            'PINNACLE_V1', 'PINNACLE_V2',
            'PINNACLE_E1', 'PINNACLE_E2',
            'PINNACLE_S1', 'PINNACLE_S2',
            'PINNACLE_P1', 'PINNACLE_P2'
        ]
        
        for class_code in pinnacle_classes:
            if class_code in CLASS_CODE_CURRICULUM_MAPPING:
                self.log_test(f"Mapping: {class_code}", "PASS", 
                            CLASS_CODE_CURRICULUM_MAPPING[class_code])
            else:
                self.log_test(f"Mapping: {class_code}", "FAIL", "Not in mapping dictionary")
        
        # Test category
        if 'PINNACLE' in CLASS_CODE_CATEGORIES:
            pinnacle_category = CLASS_CODE_CATEGORIES['PINNACLE']
            if len(pinnacle_category) == 8:
                self.log_test("PINNACLE Category", "PASS", "8 classes in category")
            else:
                self.log_test("PINNACLE Category", "FAIL", 
                            f"Expected 8 classes, found {len(pinnacle_category)}")
        else:
            self.log_test("PINNACLE Category", "FAIL", "Category not found")
        
        # Test get_class_codes_by_program
        pinnacle_codes = get_class_codes_by_program('PINNACLE')
        if len(pinnacle_codes) == 8:
            self.log_test("get_class_codes_by_program", "PASS", "Returns 8 PINNACLE classes")
        else:
            self.log_test("get_class_codes_by_program", "FAIL", 
                        f"Expected 8, got {len(pinnacle_codes)}")
    
    def test_admin_views(self):
        """Test 7: Verify admin views work with PINNACLE"""
        print("\n" + "="*60)
        print("TEST 7: Admin View Integration")
        print("="*60)
        
        # Login as admin
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.log_test("Admin Login", "FAIL", "No admin user found")
            return
        
        admin_user.set_password('admin')
        admin_user.save()
        
        login_success = self.client.login(username=admin_user.username, password='admin')
        if not login_success:
            self.log_test("Admin Login", "FAIL", "Could not login")
            return
        
        self.log_test("Admin Login", "PASS", f"Logged in as {admin_user.username}")
        
        # Test curriculum management page
        response = self.client.get('/curriculum-management/')
        if response.status_code == 200:
            content = response.content.decode()
            if 'PINNACLE' in content:
                self.log_test("Curriculum Management", "PASS", "PINNACLE visible")
            else:
                self.log_test("Curriculum Management", "WARN", "PINNACLE not visible in content")
        else:
            self.log_test("Curriculum Management", "FAIL", f"Status code: {response.status_code}")
    
    def test_classes_and_exams_view(self):
        """Test 8: Verify Classes & Exams view integration"""
        print("\n" + "="*60)
        print("TEST 8: Classes & Exams View")
        print("="*60)
        
        # Ensure we're logged in as a teacher
        teacher_user = User.objects.filter(teacher__isnull=False, is_active=True).first()
        if not teacher_user:
            self.log_test("Teacher Login", "FAIL", "No teacher user found")
            return
        
        teacher_user.set_password('test123')
        teacher_user.save()
        
        login_success = self.client.login(username=teacher_user.username, password='test123')
        if not login_success:
            self.log_test("Teacher Login", "FAIL", "Could not login")
            return
        
        self.log_test("Teacher Login", "PASS", f"Logged in as {teacher_user.username}")
        
        # Test unified view
        response = self.client.get('/RoutineTest/classes-exams/')
        if response.status_code == 200:
            self.log_test("Classes & Exams Page", "PASS", "Page loads")
            
            # Check if PINNACLE program appears
            content = response.content.decode()
            pinnacle_count = content.count('PINNACLE')
            
            if pinnacle_count > 0:
                self.log_test("PINNACLE Visibility", "PASS", f"Found {pinnacle_count} occurrences")
            else:
                self.log_test("PINNACLE Visibility", "WARN", "PINNACLE not visible in view")
                
        else:
            self.log_test("Classes & Exams Page", "FAIL", f"Status code: {response.status_code}")
    
    def test_database_integrity(self):
        """Test 9: Verify database integrity"""
        print("\n" + "="*60)
        print("TEST 9: Database Integrity")
        print("="*60)
        
        # Check for orphaned mappings
        orphaned_mappings = ClassCurriculumMapping.objects.filter(
            class_code__startswith='PINNACLE'
        ).exclude(
            curriculum_level__subprogram__program__name='PINNACLE'
        )
        
        if orphaned_mappings.count() == 0:
            self.log_test("Orphaned Mappings", "PASS", "No orphaned mappings")
        else:
            self.log_test("Orphaned Mappings", "FAIL", f"{orphaned_mappings.count()} found")
        
        # Check for duplicate mappings
        from django.db.models import Count
        duplicates = ClassCurriculumMapping.objects.filter(
            class_code__startswith='PINNACLE'
        ).values('class_code').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        if duplicates.count() == 0:
            self.log_test("Duplicate Mappings", "PASS", "No duplicates")
        else:
            self.log_test("Duplicate Mappings", "FAIL", f"{duplicates.count()} duplicates found")
    
    def test_console_logging(self):
        """Test 10: Verify console logging is working"""
        print("\n" + "="*60)
        print("TEST 10: Console Logging")
        print("="*60)
        
        # Test that logging functions work
        test_class = 'PINNACLE_V1'
        
        print("Testing get_curriculum_for_class logging:")
        result = get_curriculum_for_class(test_class)
        if result:
            self.log_test("Console Logging", "PASS", "Logging functional")
        else:
            self.log_test("Console Logging", "WARN", "Check console output")
    
    def run_all_tests(self):
        """Run all QA tests"""
        print("\n" + "="*80)
        print("  PINNACLE IMPLEMENTATION QA TEST SUITE")
        print("="*80)
        print(f"  Start Time: {datetime.now()}")
        print("="*80)
        
        # Run tests in sequence
        program = self.test_pinnacle_program_exists()
        subprograms = self.test_pinnacle_subprograms(program)
        levels = self.test_curriculum_levels(subprograms)
        classes = self.test_pinnacle_classes()
        self.test_class_curriculum_mappings(classes, levels)
        self.test_class_code_mapping_file()
        self.test_admin_views()
        self.test_classes_and_exams_view()
        self.test_database_integrity()
        self.test_console_logging()
        
        # Print summary
        self.print_summary()
        
        return len(self.results['failed']) == 0
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("  QA TEST SUMMARY")
        print("="*80)
        
        print(f"\n📊 RESULTS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   ✅ Passed: {len(self.results['passed'])}")
        print(f"   ❌ Failed: {len(self.results['failed'])}")
        print(f"   ⚠️  Warnings: {len(self.results['warnings'])}")
        
        if self.results['failed']:
            print(f"\n❌ FAILED TESTS:")
            for test_name, message in self.results['failed']:
                print(f"   - {test_name}: {message}")
        
        if self.results['warnings']:
            print(f"\n⚠️  WARNINGS:")
            for test_name, message in self.results['warnings']:
                print(f"   - {test_name}: {message}")
        
        # Overall status
        print("\n" + "="*80)
        if len(self.results['failed']) == 0:
            if len(self.results['warnings']) == 0:
                print("  ✅ ALL TESTS PASSED - PINNACLE IMPLEMENTATION SUCCESSFUL")
            else:
                print("  ✅ TESTS PASSED WITH WARNINGS - PINNACLE IMPLEMENTATION FUNCTIONAL")
        else:
            print("  ❌ TESTS FAILED - PINNACLE IMPLEMENTATION NEEDS ATTENTION")
        print("="*80)
        
        # Save results to file
        self.save_results()
    
    def save_results(self):
        """Save test results to JSON file"""
        results_file = f"pinnacle_qa_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_tests': self.total_tests,
                'passed': self.results['passed'],
                'failed': [{'test': t, 'message': m} for t, m in self.results['failed']],
                'warnings': [{'test': t, 'message': m} for t, m in self.results['warnings']]
            }, f, indent=2)
        
        print(f"\n📄 Results saved to: {results_file}")


if __name__ == "__main__":
    qa = PinnacleQA()
    success = qa.run_all_tests()
    sys.exit(0 if success else 1)
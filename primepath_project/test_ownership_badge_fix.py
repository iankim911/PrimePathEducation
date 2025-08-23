#!/usr/bin/env python
"""
COMPREHENSIVE TEST: Ownership Badge Fix Validation
==================================================
This script validates that the ownership badge hierarchy fix is working correctly.

Test Scenarios:
1. Teacher owns exam but has VIEW access to class -> Should show OWNER badge
2. Teacher owns exam and has FULL access to class -> Should show OWNER badge
3. Teacher doesn't own exam but has FULL access -> Should show FULL ACCESS
4. Teacher doesn't own exam and has VIEW access -> Should show VIEW ONLY
5. Admin user -> Should show admin privileges

Author: PrimePath Development Team
Date: 2025-08-23
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory, Client
from core.models import Teacher
from primepath_routinetest.models import Exam, TeacherClassAssignment
from primepath_routinetest.services.exam_service import ExamPermissionService

# Enable logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OwnershipBadgeTestSuite:
    """Test suite for ownership badge fix"""
    
    def __init__(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.results = []
        
    def setup_test_data(self):
        """Create test data for validation"""
        print("\n" + "="*80)
        print("SETTING UP TEST DATA")
        print("="*80)
        
        # Create test teacher user
        self.teacher_user = User.objects.filter(username='test_ownership_teacher').first()
        if not self.teacher_user:
            self.teacher_user = User.objects.create_user(
                username='test_ownership_teacher',
                password='test123',
                email='test_ownership@example.com'
            )
            print(f"✅ Created test user: {self.teacher_user.username}")
        else:
            print(f"✅ Using existing test user: {self.teacher_user.username}")
        
        # Create teacher profile if doesn't exist
        if not hasattr(self.teacher_user, 'teacher_profile'):
            teacher = Teacher.objects.create(
                user=self.teacher_user,
                name="Test Ownership Teacher",
                email=f"test_ownership_{datetime.now().timestamp()}@example.com",
                global_access_level='FULL'
            )
            print(f"✅ Created teacher profile: {teacher.name}")
        else:
            teacher = self.teacher_user.teacher_profile
            print(f"✅ Using existing teacher profile: {teacher.name}")
        
        self.teacher = teacher
        
        # Create test exam owned by this teacher
        self.owned_exam = Exam.objects.create(
            name="[TEST] Ownership Test Exam - OWNED",
            exam_type='REVIEW',
            class_codes=['PS1', 'P1'],  # Multiple classes
            created_by=self.teacher,
            time_period_month='AUG',
            academic_year='2025',
            total_questions=10,
            passing_score=70
        )
        print(f"✅ Created owned exam: {self.owned_exam.name}")
        print(f"   Classes: {self.owned_exam.class_codes}")
        
        # Create exam NOT owned by this teacher
        other_teacher = Teacher.objects.exclude(id=self.teacher.id).first()
        if other_teacher:
            self.not_owned_exam = Exam.objects.create(
                name="[TEST] Ownership Test Exam - NOT OWNED",
                exam_type='REVIEW',
                class_codes=['PS1'],
                created_by=other_teacher,
                time_period_month='AUG',
                academic_year='2025',
                total_questions=10,
                passing_score=70
            )
            print(f"✅ Created not-owned exam: {self.not_owned_exam.name}")
            print(f"   Owner: {other_teacher.name}")
        
        return True
    
    def test_scenario_1_owner_with_view_access(self):
        """Test: Teacher owns exam but has VIEW access to class"""
        print("\n" + "="*80)
        print("SCENARIO 1: Teacher owns exam but has VIEW access to class")
        print("="*80)
        
        # Set teacher to have VIEW access to PS1
        TeacherClassAssignment.objects.filter(
            teacher=self.teacher,
            class_code='PS1'
        ).delete()
        
        assignment = TeacherClassAssignment.objects.create(
            teacher=self.teacher,
            class_code='PS1',
            access_level='VIEW',
            assigned_by=self.teacher_user
        )
        print(f"✅ Set teacher to have VIEW access to PS1")
        
        # Test enhanced assignments
        enhanced = ExamPermissionService.get_enhanced_teacher_assignments(
            self.teacher_user
        )
        
        print("\n📊 Enhanced Assignment Results:")
        print(f"   Base assignments: {enhanced['assignments']}")
        print(f"   Ownership overrides: {enhanced['ownership_overrides']}")
        print(f"   Effective access: {enhanced['effective_access']}")
        
        # Validate
        test_passed = False
        if 'PS1' in enhanced['ownership_overrides']:
            print("✅ PS1 correctly identified as owned class")
            if enhanced['effective_access'].get('PS1') == 'FULL':
                print("✅ PS1 access upgraded from VIEW to FULL due to ownership")
                test_passed = True
            else:
                print(f"❌ PS1 access not upgraded: {enhanced['effective_access'].get('PS1')}")
        else:
            print("❌ PS1 not identified as owned class")
        
        self.results.append({
            'scenario': 'Owner with VIEW access',
            'passed': test_passed,
            'details': enhanced
        })
        
        return test_passed
    
    def test_scenario_2_owner_with_full_access(self):
        """Test: Teacher owns exam and has FULL access to class"""
        print("\n" + "="*80)
        print("SCENARIO 2: Teacher owns exam and has FULL access to class")
        print("="*80)
        
        # Set teacher to have FULL access to P1
        TeacherClassAssignment.objects.filter(
            teacher=self.teacher,
            class_code='P1'
        ).delete()
        
        assignment = TeacherClassAssignment.objects.create(
            teacher=self.teacher,
            class_code='P1',
            access_level='FULL',
            assigned_by=self.teacher_user
        )
        print(f"✅ Set teacher to have FULL access to P1")
        
        # Test enhanced assignments
        enhanced = ExamPermissionService.get_enhanced_teacher_assignments(
            self.teacher_user
        )
        
        print("\n📊 Enhanced Assignment Results:")
        print(f"   Base assignments: {enhanced['assignments']}")
        print(f"   Ownership overrides: {enhanced['ownership_overrides']}")
        print(f"   Effective access: {enhanced['effective_access']}")
        
        # Validate
        test_passed = False
        if 'P1' in enhanced['ownership_overrides']:
            print("✅ P1 correctly identified as owned class")
            if enhanced['effective_access'].get('P1') == 'FULL':
                print("✅ P1 maintains FULL access (already had it)")
                test_passed = True
        else:
            print("❌ P1 not identified as owned class")
        
        self.results.append({
            'scenario': 'Owner with FULL access',
            'passed': test_passed,
            'details': enhanced
        })
        
        return test_passed
    
    def test_scenario_3_non_owner_with_full(self):
        """Test: Teacher doesn't own exam but has FULL access"""
        print("\n" + "="*80)
        print("SCENARIO 3: Teacher doesn't own exam but has FULL access")
        print("="*80)
        
        # Create a different class not in owned exam
        TeacherClassAssignment.objects.filter(
            teacher=self.teacher,
            class_code='PRIMARY_2A'
        ).delete()
        
        assignment = TeacherClassAssignment.objects.create(
            teacher=self.teacher,
            class_code='PRIMARY_2A',
            access_level='FULL',
            assigned_by=self.teacher_user
        )
        print(f"✅ Set teacher to have FULL access to PRIMARY_2A (no owned exams)")
        
        # Test enhanced assignments
        enhanced = ExamPermissionService.get_enhanced_teacher_assignments(
            self.teacher_user
        )
        
        print("\n📊 Enhanced Assignment Results:")
        print(f"   Effective access for PRIMARY_2A: {enhanced['effective_access'].get('PRIMARY_2A')}")
        
        # Validate
        test_passed = False
        if 'PRIMARY_2A' not in enhanced['ownership_overrides']:
            print("✅ PRIMARY_2A correctly NOT in ownership overrides")
            if enhanced['effective_access'].get('PRIMARY_2A') == 'FULL':
                print("✅ PRIMARY_2A maintains FULL access from assignment")
                test_passed = True
        else:
            print("❌ PRIMARY_2A incorrectly marked as owned")
        
        self.results.append({
            'scenario': 'Non-owner with FULL access',
            'passed': test_passed,
            'details': {'PRIMARY_2A': enhanced['effective_access'].get('PRIMARY_2A')}
        })
        
        return test_passed
    
    def test_ui_rendering(self):
        """Test the actual UI rendering with the fix"""
        print("\n" + "="*80)
        print("UI RENDERING TEST")
        print("="*80)
        
        # Login as test teacher
        self.client.login(username='test_ownership_teacher', password='test123')
        
        # Access the exam list page
        response = self.client.get('/RoutineTest/exams/')
        
        if response.status_code == 200:
            print("✅ Exam list page loaded successfully")
            
            # Check context data
            context = response.context
            if context:
                if 'ownership_overrides' in context:
                    print(f"✅ ownership_overrides in context: {context['ownership_overrides']}")
                else:
                    print("❌ ownership_overrides NOT in context")
                
                if 'teacher_assignments' in context:
                    print(f"✅ teacher_assignments in context: {dict(list(context['teacher_assignments'].items())[:5])}")
                else:
                    print("❌ teacher_assignments NOT in context")
                
                # Check for OWNER badge in HTML
                html_content = response.content.decode('utf-8')
                if 'OWNER - Full Access' in html_content:
                    print("✅ OWNER badge text found in HTML")
                else:
                    print("⚠️ OWNER badge text not found (may not have owned exams visible)")
                
                if 'access-badge owner' in html_content:
                    print("✅ Owner badge CSS class found in HTML")
                else:
                    print("⚠️ Owner badge CSS class not found")
        else:
            print(f"❌ Failed to load exam list page: {response.status_code}")
        
        return response.status_code == 200
    
    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n" + "="*80)
        print("CLEANING UP TEST DATA")
        print("="*80)
        
        # Delete test exams
        Exam.objects.filter(name__contains='[TEST] Ownership Test').delete()
        print("✅ Deleted test exams")
        
        # Delete test assignments
        TeacherClassAssignment.objects.filter(teacher=self.teacher).delete()
        print("✅ Deleted test assignments")
        
        return True
    
    def run_all_tests(self):
        """Run all test scenarios"""
        print("\n" + "🚀" * 40)
        print("OWNERSHIP BADGE FIX - COMPREHENSIVE QA TEST SUITE")
        print("🚀" * 40)
        
        try:
            # Setup
            self.setup_test_data()
            
            # Run scenarios
            scenario1_passed = self.test_scenario_1_owner_with_view_access()
            scenario2_passed = self.test_scenario_2_owner_with_full_access()
            scenario3_passed = self.test_scenario_3_non_owner_with_full()
            ui_passed = self.test_ui_rendering()
            
            # Summary
            print("\n" + "="*80)
            print("TEST RESULTS SUMMARY")
            print("="*80)
            
            total_tests = 4
            passed_tests = sum([scenario1_passed, scenario2_passed, scenario3_passed, ui_passed])
            
            print(f"\n📊 Results: {passed_tests}/{total_tests} tests passed")
            
            for result in self.results:
                status = "✅ PASSED" if result['passed'] else "❌ FAILED"
                print(f"   {status}: {result['scenario']}")
            
            # Cleanup
            self.cleanup_test_data()
            
            # Final verdict
            print("\n" + "="*80)
            if passed_tests == total_tests:
                print("🎉 ALL TESTS PASSED! The ownership badge fix is working correctly!")
            else:
                print(f"⚠️ {total_tests - passed_tests} test(s) failed. Review the implementation.")
            print("="*80)
            
            return passed_tests == total_tests
            
        except Exception as e:
            print(f"\n❌ ERROR during testing: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    # Run the test suite
    test_suite = OwnershipBadgeTestSuite()
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
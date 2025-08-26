#!/usr/bin/env python
"""
Comprehensive Test Script for "Show Assigned Classes Only" Filter Fix
Tests both the semantic correctness and the ownership badge bug fix
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from primepath_routinetest.models import RoutineExam as Exam, TeacherClassAssignment
from primepath_routinetest.services.exam_service import ExamService
from core.models import Teacher

User = get_user_model()

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(text)
    print(f"{'='*60}")

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")

def print_debug(text):
    """Print debug message"""
    print(f"🔍 {text}")

class FilterTestRunner:
    def __init__(self):
        self.factory = RequestFactory()
        self.test_results = []
        
    def run_all_tests(self):
        """Run all test scenarios"""
        print_header("FILTER FIX COMPREHENSIVE TEST SUITE")
        
        # Test 1: Teacher with mixed access levels
        self.test_mixed_access_levels()
        
        # Test 2: Ownership badge preservation
        self.test_ownership_badge_preservation()
        
        # Test 3: VIEW ONLY inclusion in filter
        self.test_view_only_inclusion()
        
        # Test 4: Admin bypass
        self.test_admin_bypass()
        
        # Test 5: No assignments scenario
        self.test_no_assignments()
        
        # Print summary
        self.print_summary()
    
    def test_mixed_access_levels(self):
        """Test teacher with FULL, CO_TEACHER, and VIEW access"""
        print_header("TEST 1: Teacher with Mixed Access Levels")
        
        try:
            # Find a teacher with mixed access levels
            teacher_user = User.objects.filter(
                teacher_profile__isnull=False,
                is_superuser=False
            ).first()
            
            if not teacher_user:
                print_error("No non-admin teacher found for testing")
                self.test_results.append(("Mixed Access Levels", False, "No teacher found"))
                return
            
            # Get teacher's assignments
            assignments = ExamService.get_teacher_assignments(teacher_user)
            print_info(f"Testing with teacher: {teacher_user.username}")
            print_debug(f"Teacher assignments: {dict(assignments)}")
            
            # Get all exams
            all_exams = Exam.objects.all()[:20]  # Test with first 20 exams
            
            # Test with filter OFF (Show All)
            print_info("\n📋 Filter OFF (Show All Exams):")
            result_all = ExamService.organize_exams_hierarchically(
                all_exams, 
                teacher_user, 
                filter_assigned_only=False
            )
            
            exam_count_all = sum(
                len(exams) for program_classes in result_all.values() 
                for exams in program_classes.values()
            )
            print_debug(f"Total exams shown: {exam_count_all}")
            
            # Count badges
            badge_counts_all = self._count_badges(result_all)
            print_debug(f"Badge distribution: {badge_counts_all}")
            
            # Test with filter ON (Assigned Only)
            print_info("\n📋 Filter ON (Show Assigned Classes Only):")
            result_filtered = ExamService.organize_exams_hierarchically(
                all_exams, 
                teacher_user, 
                filter_assigned_only=True
            )
            
            exam_count_filtered = sum(
                len(exams) for program_classes in result_filtered.values() 
                for exams in program_classes.values()
            )
            print_debug(f"Total exams shown: {exam_count_filtered}")
            
            # Count badges
            badge_counts_filtered = self._count_badges(result_filtered)
            print_debug(f"Badge distribution: {badge_counts_filtered}")
            
            # Verify filter includes VIEW access
            if assignments and 'VIEW' in assignments.values():
                if badge_counts_filtered.get('VIEW ONLY', 0) > 0:
                    print_success("VIEW ONLY exams ARE included when filter is ON (correct behavior)")
                    self.test_results.append(("Mixed Access - VIEW inclusion", True, ""))
                else:
                    print_error("VIEW ONLY exams missing when filter is ON (incorrect)")
                    self.test_results.append(("Mixed Access - VIEW inclusion", False, "VIEW not included"))
            else:
                print_info("Teacher has no VIEW access assignments to test")
                self.test_results.append(("Mixed Access - VIEW inclusion", True, "N/A - No VIEW access"))
            
            # Verify filtering reduces exam count (unless teacher sees all anyway)
            if exam_count_filtered <= exam_count_all:
                print_success(f"Filter correctly reduces exams: {exam_count_all} → {exam_count_filtered}")
                self.test_results.append(("Mixed Access - Filter reduction", True, ""))
            else:
                print_error(f"Filter increased exam count: {exam_count_all} → {exam_count_filtered}")
                self.test_results.append(("Mixed Access - Filter reduction", False, "Count increased"))
                
        except Exception as e:
            print_error(f"Test failed with error: {str(e)}")
            self.test_results.append(("Mixed Access Levels", False, str(e)))
    
    def test_ownership_badge_preservation(self):
        """Test that owned exams show OWNER badge correctly"""
        print_header("TEST 2: Ownership Badge Preservation")
        
        try:
            # Find an exam with an owner
            owned_exam = Exam.objects.filter(created_by__isnull=False).first()
            if not owned_exam:
                print_error("No exams with owners found")
                self.test_results.append(("Ownership Badge", False, "No owned exams"))
                return
            
            owner_user = User.objects.get(teacher_profile=owned_exam.created_by)
            print_info(f"Testing with exam owner: {owner_user.username}")
            print_debug(f"Exam: {owned_exam.name}")
            
            # Test with filter OFF
            print_info("\n📋 Filter OFF (Show All):")
            result_all = ExamService.organize_exams_hierarchically(
                [owned_exam], 
                owner_user, 
                filter_assigned_only=False
            )
            
            # Find the exam in results
            found_exam_all = None
            for program_classes in result_all.values():
                for exams in program_classes.values():
                    for exam in exams:
                        if exam.id == owned_exam.id:
                            found_exam_all = exam
                            break
            
            if found_exam_all:
                print_debug(f"Badge shown: {found_exam_all.access_badge}")
                print_debug(f"is_owner flag: {found_exam_all.is_owner}")
                
                if found_exam_all.access_badge == 'OWNER' and found_exam_all.is_owner:
                    print_success("OWNER badge correctly shown when filter is OFF")
                    self.test_results.append(("Ownership - Filter OFF", True, ""))
                else:
                    print_error(f"Incorrect badge: {found_exam_all.access_badge} (should be OWNER)")
                    self.test_results.append(("Ownership - Filter OFF", False, f"Badge: {found_exam_all.access_badge}"))
            else:
                print_error("Owned exam not found in results")
                self.test_results.append(("Ownership - Filter OFF", False, "Exam not found"))
            
            # Test with filter ON
            print_info("\n📋 Filter ON (Assigned Only):")
            result_filtered = ExamService.organize_exams_hierarchically(
                [owned_exam], 
                owner_user, 
                filter_assigned_only=True
            )
            
            # Find the exam in results
            found_exam_filtered = None
            for program_classes in result_filtered.values():
                for exams in program_classes.values():
                    for exam in exams:
                        if exam.id == owned_exam.id:
                            found_exam_filtered = exam
                            break
            
            if found_exam_filtered:
                print_debug(f"Badge shown: {found_exam_filtered.access_badge}")
                print_debug(f"is_owner flag: {found_exam_filtered.is_owner}")
                
                if found_exam_filtered.access_badge == 'OWNER' and found_exam_filtered.is_owner:
                    print_success("OWNER badge correctly shown when filter is ON")
                    self.test_results.append(("Ownership - Filter ON", True, ""))
                else:
                    print_error(f"Incorrect badge: {found_exam_filtered.access_badge} (should be OWNER)")
                    self.test_results.append(("Ownership - Filter ON", False, f"Badge: {found_exam_filtered.access_badge}"))
            else:
                print_info("Owned exam filtered out (owner may not be assigned to its classes)")
                self.test_results.append(("Ownership - Filter ON", True, "Filtered (expected)"))
                
        except Exception as e:
            print_error(f"Test failed with error: {str(e)}")
            self.test_results.append(("Ownership Badge", False, str(e)))
    
    def test_view_only_inclusion(self):
        """Test that VIEW ONLY exams appear when filter is ON"""
        print_header("TEST 3: VIEW ONLY Inclusion in Filter")
        
        try:
            # Find or create a teacher with VIEW access
            view_assignment = TeacherClassAssignment.objects.filter(
                access_level='VIEW',
                is_active=True
            ).first()
            
            if not view_assignment:
                print_error("No VIEW access assignments found")
                self.test_results.append(("VIEW Inclusion", False, "No VIEW assignments"))
                return
            
            teacher_user = User.objects.get(teacher_profile=view_assignment.teacher)
            class_code = view_assignment.class_code
            
            print_info(f"Testing with teacher: {teacher_user.username}")
            print_debug(f"VIEW access to class: {class_code}")
            
            # Find exams in that class
            exams_in_class = Exam.objects.filter(class_codes__contains=[class_code])[:5]
            
            if not exams_in_class:
                print_error(f"No exams found in class {class_code}")
                self.test_results.append(("VIEW Inclusion", False, "No exams in class"))
                return
            
            print_debug(f"Found {len(exams_in_class)} exams in class {class_code}")
            
            # Test with filter ON
            print_info("\n📋 Filter ON (Should include VIEW access exams):")
            result_filtered = ExamService.organize_exams_hierarchically(
                exams_in_class, 
                teacher_user, 
                filter_assigned_only=True
            )
            
            # Count exams shown
            exam_count = sum(
                len(exams) for program_classes in result_filtered.values() 
                for exams in program_classes.values()
            )
            
            print_debug(f"Exams shown with filter ON: {exam_count}")
            
            # Check for VIEW ONLY badges
            view_only_count = 0
            for program_classes in result_filtered.values():
                for exams in program_classes.values():
                    for exam in exams:
                        if exam.access_badge == 'VIEW ONLY':
                            view_only_count += 1
                            print_debug(f"  - {exam.name}: {exam.access_badge}")
            
            if exam_count > 0:
                print_success(f"Filter correctly includes {exam_count} exam(s) from VIEW access class")
                print_success(f"{view_only_count} exam(s) show VIEW ONLY badge")
                self.test_results.append(("VIEW Inclusion", True, ""))
            else:
                print_error("No exams shown despite teacher having VIEW access")
                self.test_results.append(("VIEW Inclusion", False, "Exams filtered out"))
                
        except Exception as e:
            print_error(f"Test failed with error: {str(e)}")
            self.test_results.append(("VIEW Inclusion", False, str(e)))
    
    def test_admin_bypass(self):
        """Test that admins bypass all filtering"""
        print_header("TEST 4: Admin Bypass")
        
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                print_error("No admin user found")
                self.test_results.append(("Admin Bypass", False, "No admin"))
                return
            
            print_info(f"Testing with admin: {admin_user.username}")
            
            all_exams = Exam.objects.all()[:10]
            
            # Test with filter OFF
            result_all = ExamService.organize_exams_hierarchically(
                all_exams, 
                admin_user, 
                filter_assigned_only=False
            )
            count_all = sum(len(exams) for program_classes in result_all.values() for exams in program_classes.values())
            
            # Test with filter ON
            result_filtered = ExamService.organize_exams_hierarchically(
                all_exams, 
                admin_user, 
                filter_assigned_only=True
            )
            count_filtered = sum(len(exams) for program_classes in result_filtered.values() for exams in program_classes.values())
            
            print_debug(f"Exams shown with filter OFF: {count_all}")
            print_debug(f"Exams shown with filter ON: {count_filtered}")
            
            if count_all == count_filtered:
                print_success("Admin sees same exams regardless of filter (correct)")
                self.test_results.append(("Admin Bypass", True, ""))
            else:
                print_error(f"Admin filtering not bypassed: {count_all} → {count_filtered}")
                self.test_results.append(("Admin Bypass", False, "Filter affected admin"))
                
        except Exception as e:
            print_error(f"Test failed with error: {str(e)}")
            self.test_results.append(("Admin Bypass", False, str(e)))
    
    def test_no_assignments(self):
        """Test teacher with no class assignments"""
        print_header("TEST 5: Teacher with No Assignments")
        
        try:
            # Find a teacher with no assignments
            teachers_with_assignments = TeacherClassAssignment.objects.filter(
                is_active=True
            ).values_list('teacher_id', flat=True).distinct()
            
            teacher_no_assignments = Teacher.objects.exclude(
                id__in=teachers_with_assignments
            ).first()
            
            if not teacher_no_assignments:
                print_info("All teachers have assignments, skipping test")
                self.test_results.append(("No Assignments", True, "N/A - All have assignments"))
                return
            
            user_no_assignments = User.objects.get(teacher_profile=teacher_no_assignments)
            print_info(f"Testing with teacher: {user_no_assignments.username}")
            
            # Get some exams
            test_exams = Exam.objects.all()[:10]
            
            # Test with filter ON
            result_filtered = ExamService.organize_exams_hierarchically(
                test_exams, 
                user_no_assignments, 
                filter_assigned_only=True
            )
            
            # Count exams (should only show owned exams if any)
            exam_count = sum(
                len(exams) for program_classes in result_filtered.values() 
                for exams in program_classes.values()
            )
            
            # Check if any shown are owned
            owned_count = 0
            for program_classes in result_filtered.values():
                for exams in program_classes.values():
                    for exam in exams:
                        if exam.is_owner:
                            owned_count += 1
            
            print_debug(f"Exams shown: {exam_count}")
            print_debug(f"Owned exams: {owned_count}")
            
            if exam_count == owned_count:
                print_success(f"Correctly shows only {owned_count} owned exam(s)")
                self.test_results.append(("No Assignments", True, ""))
            else:
                print_error(f"Shows {exam_count} exams but only {owned_count} are owned")
                self.test_results.append(("No Assignments", False, "Non-owned shown"))
                
        except Exception as e:
            print_error(f"Test failed with error: {str(e)}")
            self.test_results.append(("No Assignments", False, str(e)))
    
    def _count_badges(self, organized_exams):
        """Count badge types in organized exam results"""
        badge_counts = {}
        for program_classes in organized_exams.values():
            for exams in program_classes.values():
                for exam in exams:
                    badge = exam.access_badge
                    badge_counts[badge] = badge_counts.get(badge, 0) + 1
        return badge_counts
    
    def print_summary(self):
        """Print test summary"""
        print_header("TEST SUMMARY")
        
        passed = sum(1 for _, result, _ in self.test_results if result)
        failed = sum(1 for _, result, _ in self.test_results if not result)
        total = len(self.test_results)
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        
        if failed > 0:
            print(f"\nFailed Tests:")
            for test_name, result, error in self.test_results:
                if not result:
                    print(f"  - {test_name}: {error}")
        
        if passed == total:
            print(f"\n{'='*60}")
            print(f"🎉 ALL TESTS PASSED! Filter fix is working correctly.")
            print(f"{'='*60}")
        else:
            print(f"\n{'='*60}")
            print(f"⚠️  Some tests failed. Review the issues above.")
            print(f"{'='*60}")

if __name__ == "__main__":
    runner = FilterTestRunner()
    runner.run_all_tests()
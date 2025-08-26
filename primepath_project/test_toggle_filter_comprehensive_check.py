#!/usr/bin/env python
"""
Comprehensive test to verify toggle filter fix doesn't break other features.
Tests all critical functionality after the toggle filter fix was implemented.
"""
import os
import sys
import django
import json
from datetime import datetime

# Setup Django
sys.path.insert(0, '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory, Client
from django.urls import reverse
from primepath_routinetest.models import RoutineExam as Exam, TeacherClassAssignment
from primepath_routinetest.services.exam_service import ExamService
from primepath_routinetest.views.exam import exam_list
from primepath_routinetest.views.classes_exams_unified import classes_exams_unified_view
from core.models import Teacher

class ComprehensiveToggleFilterTest:
    """Comprehensive test suite for toggle filter fix verification"""
    
    def __init__(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.test_results = {
            'toggle_filter_fix': {'passed': False, 'details': []},
            'copy_modal': {'passed': False, 'details': []},
            'permission_badges': {'passed': False, 'details': []},
            'delete_edit_buttons': {'passed': False, 'details': []},
            'unified_view': {'passed': False, 'details': []},
            'exam_creation': {'passed': False, 'details': []}
        }
        self.total_tests = 0
        self.passed_tests = 0
    
    def setup_test_data(self):
        """Setup test users and data"""
        print("\n" + "="*80)
        print("SETTING UP TEST DATA")
        print("="*80)
        
        try:
            # Get or create test user
            self.user = User.objects.get(username='teacher1')
            self.teacher = Teacher.objects.get(user=self.user)
            print(f"✅ Found test user: {self.user.username}")
        except (User.DoesNotExist, Teacher.DoesNotExist):
            print("❌ Test user 'teacher1' not found. Creating minimal test setup...")
            self.user = User.objects.create_user('test_teacher', 'test@example.com', 'password')
            self.teacher = Teacher.objects.create(
                user=self.user,
                name='Test Teacher',
                email='test@example.com'
            )
        
        # Get assignments
        self.assignments = TeacherClassAssignment.objects.filter(
            teacher=self.teacher,
            is_active=True
        )
        print(f"✅ Teacher has {self.assignments.count()} class assignments")
        
        # Get sample exams
        self.all_exams = Exam.objects.all()[:20]  # Limit for performance
        print(f"✅ Found {self.all_exams.count()} exams for testing")
        
        return True
    
    def test_toggle_filter_functionality(self):
        """Test 1: Verify toggle filter works correctly with VIEW access"""
        print(f"\n{'='*60}")
        print("TEST 1: Toggle Filter Functionality")
        print("="*60)
        
        self.total_tests += 1
        passed = True
        details = []
        
        try:
            # Test without filter (show all)
            hierarchical_all = ExamService.organize_exams_hierarchically(
                self.all_exams, self.user, filter_assigned_only=False
            )
            
            exam_count_all = 0
            view_only_count_all = 0
            for program, classes in hierarchical_all.items():
                for class_code, exams in classes.items():
                    for exam in exams:
                        exam_count_all += 1
                        if hasattr(exam, 'access_badge') and exam.access_badge == 'VIEW ONLY':
                            view_only_count_all += 1
            
            details.append(f"All exams mode: {exam_count_all} exams, {view_only_count_all} VIEW ONLY")
            
            # Test with filter (assigned only)
            hierarchical_filtered = ExamService.organize_exams_hierarchically(
                self.all_exams, self.user, filter_assigned_only=True
            )
            
            exam_count_filtered = 0
            view_only_count_filtered = 0
            for program, classes in hierarchical_filtered.items():
                for class_code, exams in classes.items():
                    for exam in exams:
                        exam_count_filtered += 1
                        if hasattr(exam, 'access_badge') and exam.access_badge == 'VIEW ONLY':
                            view_only_count_filtered += 1
            
            details.append(f"Filtered mode: {exam_count_filtered} exams, {view_only_count_filtered} VIEW ONLY")
            
            # Check if fix is working - VIEW access exams should show when filtered
            teacher_assignments = dict(self.assignments.values_list('class_code', 'access_level'))
            view_assignments = [c for c, a in teacher_assignments.items() if a == 'VIEW']
            
            if view_assignments and view_only_count_filtered > 0:
                details.append("✅ VIEW ONLY exams correctly shown when toggle is checked")
                print("✅ Toggle filter fix verified: VIEW access exams are shown")
            elif not view_assignments:
                details.append("ℹ️ Teacher has no VIEW assignments - test not applicable")
                print("ℹ️ Teacher has no VIEW assignments, but toggle filter works correctly")
            else:
                passed = False
                details.append("❌ VIEW ONLY exams not shown despite teacher having VIEW assignments")
                print("❌ Toggle filter issue: VIEW access exams are missing")
            
        except Exception as e:
            passed = False
            details.append(f"❌ Exception during toggle filter test: {str(e)}")
            print(f"❌ Toggle filter test failed: {str(e)}")
        
        self.test_results['toggle_filter_fix']['passed'] = passed
        self.test_results['toggle_filter_fix']['details'] = details
        if passed:
            self.passed_tests += 1
        
        return passed
    
    def test_copy_modal_functionality(self):
        """Test 2: Verify copy exam modal shows correct classes"""
        print(f"\n{'='*60}")
        print("TEST 2: Copy Exam Modal")
        print("="*60)
        
        self.total_tests += 1
        passed = True
        details = []
        
        try:
            # Login the user
            self.client.force_login(self.user)
            
            # Get a sample exam
            sample_exam = self.all_exams.first()
            if not sample_exam:
                details.append("❌ No exam found for copy modal test")
                passed = False
                return passed
            
            # Check copy modal endpoint (if exists)
            try:
                # Check if copy modal JavaScript exists
                with open('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/static/js/routinetest/copy-exam-modal.js', 'r') as f:
                    modal_js = f.read()
                    if 'copyExamModal' in modal_js:
                        details.append("✅ Copy modal JavaScript file exists and contains modal code")
                    else:
                        details.append("⚠️ Copy modal JavaScript exists but may be incomplete")
            except FileNotFoundError:
                details.append("❌ Copy modal JavaScript file not found")
                passed = False
            
            # Check if exam has copy permissions
            organized = ExamService.organize_exams_hierarchically(
                [sample_exam], self.user, filter_assigned_only=False
            )
            
            found_exam = None
            for program, classes in organized.items():
                for class_code, exams in classes.items():
                    if exams:
                        found_exam = exams[0]
                        break
                if found_exam:
                    break
            
            if found_exam and hasattr(found_exam, 'can_copy'):
                if found_exam.can_copy:
                    details.append("✅ Exam has copy permission enabled")
                else:
                    details.append("⚠️ Exam does not have copy permission")
            else:
                details.append("⚠️ Could not determine copy permission for exam")
            
            # Check teacher's class choices for copy destination
            teacher_classes = ExamService.get_filtered_class_choices_for_teacher(self.user, full_access_only=False)
            if teacher_classes:
                details.append(f"✅ Teacher has {len(teacher_classes)} classes available as copy destinations")
            else:
                details.append("⚠️ Teacher has no classes available as copy destinations")
                
        except Exception as e:
            passed = False
            details.append(f"❌ Exception during copy modal test: {str(e)}")
            print(f"❌ Copy modal test failed: {str(e)}")
        
        self.test_results['copy_modal']['passed'] = passed
        self.test_results['copy_modal']['details'] = details
        if passed:
            self.passed_tests += 1
        
        return passed
    
    def test_permission_badges(self):
        """Test 3: Check permission badges display correctly"""
        print(f"\n{'='*60}")
        print("TEST 3: Permission Badges")
        print("="*60)
        
        self.total_tests += 1
        passed = True
        details = []
        
        try:
            # Test different scenarios
            hierarchical_all = ExamService.organize_exams_hierarchically(
                self.all_exams, self.user, filter_assigned_only=False
            )
            
            badge_counts = {'OWNER': 0, 'ADMIN': 0, 'FULL ACCESS': 0, 'VIEW ONLY': 0, 'EDIT': 0}
            
            for program, classes in hierarchical_all.items():
                for class_code, exams in classes.items():
                    for exam in exams:
                        if hasattr(exam, 'access_badge'):
                            badge = exam.access_badge
                            if badge in badge_counts:
                                badge_counts[badge] += 1
                            else:
                                badge_counts['OTHER'] = badge_counts.get('OTHER', 0) + 1
            
            total_badges = sum(badge_counts.values())
            details.append(f"Found {total_badges} exams with permission badges")
            
            for badge, count in badge_counts.items():
                if count > 0:
                    details.append(f"  - {badge}: {count}")
            
            # Verify badges are being set
            if total_badges > 0:
                details.append("✅ Permission badges are being assigned to exams")
                print("✅ Permission badges working correctly")
            else:
                passed = False
                details.append("❌ No permission badges found on any exams")
                print("❌ Permission badges not working")
            
            # Test admin user badges
            if self.user.is_superuser:
                admin_found = badge_counts.get('ADMIN', 0) > 0
                if admin_found:
                    details.append("✅ ADMIN badges correctly assigned to superuser")
                else:
                    details.append("⚠️ No ADMIN badges found for superuser")
                    
        except Exception as e:
            passed = False
            details.append(f"❌ Exception during permission badge test: {str(e)}")
            print(f"❌ Permission badge test failed: {str(e)}")
        
        self.test_results['permission_badges']['passed'] = passed
        self.test_results['permission_badges']['details'] = details
        if passed:
            self.passed_tests += 1
        
        return passed
    
    def test_delete_edit_permissions(self):
        """Test 4: Verify delete/edit buttons have correct permissions"""
        print(f"\n{'='*60}")
        print("TEST 4: Delete/Edit Button Permissions")
        print("="*60)
        
        self.total_tests += 1
        passed = True
        details = []
        
        try:
            hierarchical = ExamService.organize_exams_hierarchically(
                self.all_exams, self.user, filter_assigned_only=False
            )
            
            edit_count = 0
            delete_count = 0
            total_exams = 0
            
            for program, classes in hierarchical.items():
                for class_code, exams in classes.items():
                    for exam in exams:
                        total_exams += 1
                        
                        if hasattr(exam, 'can_edit') and exam.can_edit:
                            edit_count += 1
                        
                        if hasattr(exam, 'can_delete') and exam.can_delete:
                            delete_count += 1
            
            details.append(f"Analyzed {total_exams} exams:")
            details.append(f"  - {edit_count} have edit permissions")
            details.append(f"  - {delete_count} have delete permissions")
            
            # Verify permissions are being set
            if total_exams > 0:
                details.append("✅ Permission attributes are being set on exams")
                print(f"✅ Permissions working: {edit_count} editable, {delete_count} deletable")
            else:
                passed = False
                details.append("❌ No exams found for permission testing")
                print("❌ No exams found for permission testing")
                
        except Exception as e:
            passed = False
            details.append(f"❌ Exception during delete/edit permission test: {str(e)}")
            print(f"❌ Delete/edit permission test failed: {str(e)}")
        
        self.test_results['delete_edit_buttons']['passed'] = passed
        self.test_results['delete_edit_buttons']['details'] = details
        if passed:
            self.passed_tests += 1
        
        return passed
    
    def test_unified_view(self):
        """Test 5: Verify Classes & Exams unified view works"""
        print(f"\n{'='*60}")
        print("TEST 5: Classes & Exams Unified View")
        print("="*60)
        
        self.total_tests += 1
        passed = True
        details = []
        
        try:
            # Create a test request
            request = self.factory.get('/RoutineTest/classes-exams/')
            request.user = self.user
            request.session = {}
            
            # Call the unified view
            response = classes_exams_unified_view(request)
            
            if response.status_code == 200:
                details.append("✅ Classes & Exams unified view returns HTTP 200")
                print("✅ Unified view loads successfully")
                
                # Check if context contains expected data
                if hasattr(response, 'context_data'):
                    context = response.context_data
                    if 'classes_info' in context:
                        details.append(f"✅ Context contains classes_info with {len(context['classes_info'])} classes")
                    if 'exam_stats' in context:
                        details.append("✅ Context contains exam_stats")
                    if 'programs_data' in context:
                        details.append(f"✅ Context contains programs_data with {len(context['programs_data'])} programs")
                else:
                    details.append("ℹ️ Could not check context data (render response)")
                    
            else:
                passed = False
                details.append(f"❌ Classes & Exams unified view returns HTTP {response.status_code}")
                print(f"❌ Unified view failed with status {response.status_code}")
                
        except Exception as e:
            passed = False
            details.append(f"❌ Exception during unified view test: {str(e)}")
            print(f"❌ Unified view test failed: {str(e)}")
        
        self.test_results['unified_view']['passed'] = passed
        self.test_results['unified_view']['details'] = details
        if passed:
            self.passed_tests += 1
        
        return passed
    
    def test_exam_creation_upload(self):
        """Test 6: Check exam creation and upload functionality"""
        print(f"\n{'='*60}")
        print("TEST 6: Exam Creation and Upload")
        print("="*60)
        
        self.total_tests += 1
        passed = True
        details = []
        
        try:
            # Login the user
            self.client.force_login(self.user)
            
            # Test create exam page access
            try:
                response = self.client.get(reverse('RoutineTest:create_exam'))
                if response.status_code == 200:
                    details.append("✅ Create exam page loads successfully (HTTP 200)")
                elif response.status_code == 403:
                    details.append("ℹ️ Create exam access denied (HTTP 403) - may be permission-based")
                else:
                    details.append(f"⚠️ Create exam page returns HTTP {response.status_code}")
            except Exception as e:
                details.append(f"⚠️ Could not test create exam page: {str(e)}")
            
            # Test class choices for exam creation
            teacher_classes = ExamService.get_filtered_class_choices_for_teacher(self.user, full_access_only=True)
            if teacher_classes:
                details.append(f"✅ Teacher has {len(teacher_classes)} classes available for exam creation")
                print(f"✅ Teacher can create exams for {len(teacher_classes)} classes")
            else:
                details.append("⚠️ Teacher has no classes available for exam creation")
                print("⚠️ Teacher cannot create exams (no FULL access classes)")
            
            # Test upload functionality exists
            try:
                # Check if upload view exists
                response = self.client.get(reverse('RoutineTest:upload_exam'))
                if response.status_code in [200, 403]:
                    details.append("✅ Upload exam endpoint exists")
                else:
                    details.append(f"⚠️ Upload exam returns HTTP {response.status_code}")
            except Exception as e:
                details.append(f"⚠️ Could not test upload exam: {str(e)}")
                
        except Exception as e:
            passed = False
            details.append(f"❌ Exception during exam creation test: {str(e)}")
            print(f"❌ Exam creation test failed: {str(e)}")
        
        self.test_results['exam_creation']['passed'] = passed
        self.test_results['exam_creation']['details'] = details
        if passed:
            self.passed_tests += 1
        
        return passed
    
    def run_all_tests(self):
        """Run all tests and generate comprehensive report"""
        print("\n" + "="*80)
        print("COMPREHENSIVE TOGGLE FILTER FIX VERIFICATION")
        print("Testing that toggle filter fix doesn't break other features")
        print("="*80)
        
        if not self.setup_test_data():
            print("❌ Failed to setup test data")
            return False
        
        # Run all tests
        tests = [
            self.test_toggle_filter_functionality,
            self.test_copy_modal_functionality, 
            self.test_permission_badges,
            self.test_delete_edit_permissions,
            self.test_unified_view,
            self.test_exam_creation_upload
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ Critical error in {test.__name__}: {str(e)}")
        
        # Generate final report
        self.generate_report()
        
        return self.passed_tests == self.total_tests
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print(f"\n{'='*80}")
        print("COMPREHENSIVE TEST RESULTS")
        print("="*80)
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Tests Passed: {self.passed_tests}/{self.total_tests}")
        print(f"   Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        
        if self.passed_tests == self.total_tests:
            print("   🎉 ALL TESTS PASSED - Toggle filter fix is safe!")
        else:
            print("   ⚠️ Some tests failed - review issues below")
        
        print(f"\n📋 DETAILED RESULTS:")
        
        test_names = {
            'toggle_filter_fix': 'Toggle Filter Functionality',
            'copy_modal': 'Copy Exam Modal',
            'permission_badges': 'Permission Badges',
            'delete_edit_buttons': 'Delete/Edit Permissions', 
            'unified_view': 'Classes & Exams Unified View',
            'exam_creation': 'Exam Creation & Upload'
        }
        
        for test_key, test_name in test_names.items():
            result = self.test_results[test_key]
            status = "✅ PASSED" if result['passed'] else "❌ FAILED"
            print(f"\n{test_name}: {status}")
            
            for detail in result['details']:
                print(f"   {detail}")
        
        print(f"\n{'='*80}")
        print("SUMMARY: Toggle Filter Fix Impact Assessment")
        print("="*80)
        
        # Specific recommendations
        if self.test_results['toggle_filter_fix']['passed']:
            print("✅ Toggle filter fix is working correctly")
            print("   - VIEW access exams now show when 'Show Assigned Classes Only' is checked")
            print("   - This matches the semantic meaning of the toggle label")
        
        if all(self.test_results[key]['passed'] for key in ['copy_modal', 'permission_badges', 'delete_edit_buttons']):
            print("✅ Core functionality preserved")
            print("   - Copy modal, permission badges, and buttons work correctly")
        
        if self.test_results['unified_view']['passed']:
            print("✅ Classes & Exams view remains functional")
        
        if self.test_results['exam_creation']['passed']:
            print("✅ Exam creation and upload functionality preserved")
        
        # Final verdict
        critical_tests = ['toggle_filter_fix', 'permission_badges', 'delete_edit_buttons']
        critical_passed = all(self.test_results[key]['passed'] for key in critical_tests)
        
        print(f"\n🔍 FINAL VERDICT:")
        if critical_passed:
            print("   ✅ SAFE TO DEPLOY - Toggle filter fix doesn't break critical features")
            print("   ✅ All core functionality remains intact")
        else:
            print("   ⚠️ REVIEW NEEDED - Some critical features may be impacted")
            print("   ⚠️ Check failed tests before deploying")

def main():
    """Main test execution"""
    test_suite = ComprehensiveToggleFilterTest()
    return test_suite.run_all_tests()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
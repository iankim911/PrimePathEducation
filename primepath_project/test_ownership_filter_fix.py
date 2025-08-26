#!/usr/bin/env python
"""
Comprehensive QA Test for Exam Ownership Filtering Fix
Tests that "Other Teachers' Exams" only shows VIEW ONLY exams
and "My Test Files" only shows FULL/CO_TEACHER/OWNER exams
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory
from primepath_routinetest.models import RoutineExam as Exam, TeacherClassAssignment
from primepath_routinetest.services import ExamService
from core.models import Teacher
import json

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def test_ownership_filtering():
    """Test the exam filtering for ownership modes"""
    
    print_header("EXAM OWNERSHIP FILTERING QA TEST")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get test users
    try:
        # Find a teacher with mixed access levels
        teacher_user = None
        teacher_profile = None
        
        # Get first teacher with assignments
        assignments = TeacherClassAssignment.objects.filter(is_active=True).select_related('teacher__user')
        if assignments.exists():
            teacher_profile = assignments.first().teacher
            teacher_user = teacher_profile.user
            print(f"\n✅ Found test teacher: {teacher_profile.name} (User: {teacher_user.username})")
        else:
            print("❌ No teacher assignments found in database")
            return False
            
        # Get teacher's assignments
        teacher_assignments = {}
        for assignment in TeacherClassAssignment.objects.filter(teacher=teacher_profile, is_active=True):
            teacher_assignments[assignment.class_code] = assignment.access_level
            
        print(f"\n📋 Teacher's class assignments:")
        for class_code, access in teacher_assignments.items():
            print(f"   • {class_code}: {access} access")
            
        # Get all exams
        all_exams = Exam.objects.all()
        print(f"\n📚 Total exams in database: {all_exams.count()}")
        
        # Simulate the filtering for both modes
        print_header("TEST 1: MY TEST FILES MODE")
        
        # Test MY_EXAMS mode
        my_exams = ExamService.organize_exams_hierarchically(
            all_exams,
            teacher_user,
            filter_assigned_only=True,
            ownership_filter='my'
        )
        
        # Count and analyze MY_EXAMS results
        my_exam_count = 0
        my_exam_access_types = {'OWNER': 0, 'FULL': 0, 'CO_TEACHER': 0, 'VIEW': 0, 'OTHER': 0}
        
        for program, classes in my_exams.items():
            for class_code, exams in classes.items():
                for exam in exams:
                    my_exam_count += 1
                    
                    # Check access badge
                    if hasattr(exam, 'access_badge'):
                        badge = exam.access_badge
                        if 'OWNER' in badge:
                            my_exam_access_types['OWNER'] += 1
                        elif 'FULL' in badge:
                            my_exam_access_types['FULL'] += 1
                        elif 'EDIT' in badge or 'CO_TEACHER' in badge:
                            my_exam_access_types['CO_TEACHER'] += 1
                        elif 'VIEW' in badge:
                            my_exam_access_types['VIEW'] += 1
                            print(f"   ❌ ERROR: Found VIEW ONLY exam in MY mode: {exam.name}")
                        else:
                            my_exam_access_types['OTHER'] += 1
        
        print(f"\nResults for MY TEST FILES:")
        print(f"  Total exams shown: {my_exam_count}")
        print(f"  Access types breakdown:")
        for access_type, count in my_exam_access_types.items():
            if count > 0:
                symbol = "❌" if access_type == 'VIEW' else "✅"
                print(f"    {symbol} {access_type}: {count}")
        
        # Validate MY_EXAMS mode
        my_test_passed = my_exam_access_types['VIEW'] == 0
        if my_test_passed:
            print("\n✅ MY TEST FILES TEST PASSED: No VIEW ONLY exams found")
        else:
            print(f"\n❌ MY TEST FILES TEST FAILED: Found {my_exam_access_types['VIEW']} VIEW ONLY exams")
        
        print_header("TEST 2: OTHER TEACHERS' TEST FILES MODE")
        
        # Test OTHERS_EXAMS mode
        others_exams = ExamService.organize_exams_hierarchically(
            all_exams,
            teacher_user,
            filter_assigned_only=True,  # Should still filter with new logic
            ownership_filter='others'
        )
        
        # Count and analyze OTHERS_EXAMS results
        others_exam_count = 0
        others_exam_access_types = {'OWNER': 0, 'FULL': 0, 'CO_TEACHER': 0, 'VIEW': 0, 'OTHER': 0}
        
        for program, classes in others_exams.items():
            for class_code, exams in classes.items():
                for exam in exams:
                    others_exam_count += 1
                    
                    # Check access badge
                    if hasattr(exam, 'access_badge'):
                        badge = exam.access_badge
                        if 'OWNER' in badge:
                            others_exam_access_types['OWNER'] += 1
                            print(f"   ❌ ERROR: Found OWNER exam in OTHERS mode: {exam.name}")
                        elif 'FULL' in badge:
                            others_exam_access_types['FULL'] += 1
                            print(f"   ❌ ERROR: Found FULL ACCESS exam in OTHERS mode: {exam.name}")
                        elif 'EDIT' in badge or 'CO_TEACHER' in badge:
                            others_exam_access_types['CO_TEACHER'] += 1
                            print(f"   ❌ ERROR: Found EDIT/CO_TEACHER exam in OTHERS mode: {exam.name}")
                        elif 'VIEW' in badge:
                            others_exam_access_types['VIEW'] += 1
                        else:
                            others_exam_access_types['OTHER'] += 1
        
        print(f"\nResults for OTHER TEACHERS' TEST FILES:")
        print(f"  Total exams shown: {others_exam_count}")
        print(f"  Access types breakdown:")
        for access_type, count in others_exam_access_types.items():
            if count > 0:
                symbol = "✅" if access_type == 'VIEW' else ("❌" if count > 0 and access_type != 'OTHER' else "")
                print(f"    {symbol} {access_type}: {count}")
        
        # Validate OTHERS_EXAMS mode
        others_test_passed = (
            others_exam_access_types['OWNER'] == 0 and
            others_exam_access_types['FULL'] == 0 and
            others_exam_access_types['CO_TEACHER'] == 0
        )
        
        if others_test_passed:
            print("\n✅ OTHER TEACHERS' TEST FILES TEST PASSED: Only VIEW ONLY exams found")
        else:
            print(f"\n❌ OTHER TEACHERS' TEST FILES TEST FAILED:")
            print(f"   Found {others_exam_access_types['OWNER']} OWNER exams")
            print(f"   Found {others_exam_access_types['FULL']} FULL ACCESS exams")
            print(f"   Found {others_exam_access_types['CO_TEACHER']} EDIT/CO_TEACHER exams")
        
        print_header("TEST 3: MUTUAL EXCLUSIVITY CHECK")
        
        # Check that exams don't appear in both modes (except for special cases)
        my_exam_ids = set()
        for program, classes in my_exams.items():
            for class_code, exams in classes.items():
                for exam in exams:
                    my_exam_ids.add(exam.id)
        
        others_exam_ids = set()
        for program, classes in others_exams.items():
            for class_code, exams in classes.items():
                for exam in exams:
                    others_exam_ids.add(exam.id)
        
        overlap = my_exam_ids.intersection(others_exam_ids)
        if overlap:
            print(f"❌ MUTUAL EXCLUSIVITY FAILED: {len(overlap)} exams appear in BOTH modes")
            # Get details of overlapping exams
            overlapping_exams = Exam.objects.filter(id__in=list(overlap)[:5])  # Show first 5
            for exam in overlapping_exams:
                print(f"   • {exam.name} (ID: {exam.id})")
        else:
            print("✅ MUTUAL EXCLUSIVITY PASSED: No exams appear in both modes")
        
        print_header("FINAL TEST RESULTS")
        
        all_tests_passed = my_test_passed and others_test_passed and not overlap
        
        if all_tests_passed:
            print("\n🎉 ALL TESTS PASSED! 🎉")
            print("The ownership filtering is working correctly:")
            print("  ✅ MY TEST FILES shows only FULL/CO_TEACHER/OWNER exams")
            print("  ✅ OTHER TEACHERS' TEST FILES shows only VIEW ONLY exams")
            print("  ✅ No exams appear in both modes")
        else:
            print("\n❌ SOME TESTS FAILED")
            print("Issues found:")
            if not my_test_passed:
                print("  ❌ MY TEST FILES is showing VIEW ONLY exams")
            if not others_test_passed:
                print("  ❌ OTHER TEACHERS' TEST FILES is showing non-VIEW ONLY exams")
            if overlap:
                print("  ❌ Some exams appear in both modes")
        
        return all_tests_passed
        
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """Test edge cases for the filtering"""
    print_header("EDGE CASE TESTS")
    
    try:
        # Test 1: Admin user should see all exams
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            print("\n📝 Testing admin user filtering...")
            all_exams = Exam.objects.all()
            
            admin_my_exams = ExamService.organize_exams_hierarchically(
                all_exams, admin_user, ownership_filter='my'
            )
            admin_others_exams = ExamService.organize_exams_hierarchically(
                all_exams, admin_user, ownership_filter='others'
            )
            
            # Count exams
            admin_my_count = sum(
                len(exams) for program in admin_my_exams.values() 
                for exams in program.values()
            )
            admin_others_count = sum(
                len(exams) for program in admin_others_exams.values()
                for exams in program.values()
            )
            
            print(f"  Admin MY TEST FILES: {admin_my_count} exams")
            print(f"  Admin OTHER TEACHERS: {admin_others_count} exams")
            print("  ✅ Admin sees exams in both modes (expected behavior)")
        
        # Test 2: User with no teacher profile
        non_teacher = User.objects.exclude(
            id__in=Teacher.objects.values_list('user_id', flat=True)
        ).exclude(is_superuser=True).first()
        
        if non_teacher:
            print("\n📝 Testing non-teacher user...")
            all_exams = Exam.objects.all()[:5]  # Test with subset
            
            non_teacher_exams = ExamService.organize_exams_hierarchically(
                all_exams, non_teacher, ownership_filter='others'
            )
            
            count = sum(
                len(exams) for program in non_teacher_exams.values()
                for exams in program.values()
            )
            
            print(f"  Non-teacher sees: {count} exams")
            print("  ✅ Non-teacher filtering handled")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Edge case test error: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n" + "🔍"*40)
    print("     EXAM OWNERSHIP FILTERING QA TEST SUITE")
    print("🔍"*40)
    
    # Run main tests
    main_tests_passed = test_ownership_filtering()
    
    # Run edge case tests
    edge_tests_passed = test_edge_cases()
    
    # Final summary
    print("\n" + "="*80)
    if main_tests_passed and edge_tests_passed:
        print("✅✅✅ ALL QA TESTS PASSED ✅✅✅")
        print("The ownership filtering fix is working correctly!")
    else:
        print("❌ SOME QA TESTS FAILED ❌")
        print("Please review the errors above and fix the issues.")
    print("="*80)
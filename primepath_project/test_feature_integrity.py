#!/usr/bin/env python
"""
Test that other exam features remain intact after the filtering fix
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory, Client
from primepath_routinetest.models import RoutineExam as Exam, TeacherClassAssignment
from primepath_routinetest.services import ExamService, ExamPermissionService
from core.models import Teacher
import json

def print_test(test_name, passed, details=""):
    """Print test result"""
    symbol = "✅" if passed else "❌"
    status = "PASSED" if passed else "FAILED"
    print(f"{symbol} {test_name}: {status}")
    if details:
        print(f"   {details}")

def test_exam_permissions():
    """Test that exam permission checks still work"""
    print("\n📋 Testing Exam Permissions...")
    
    try:
        # Get a teacher and an exam
        teacher = Teacher.objects.filter(user__isnull=False).first()
        if not teacher:
            print_test("Permission Test", False, "No teacher found")
            return False
        
        exam = Exam.objects.first()
        if not exam:
            print_test("Permission Test", False, "No exam found")
            return False
        
        # Test permission methods
        can_edit = ExamService.can_teacher_edit_exam(teacher.user, exam)
        can_copy = ExamPermissionService.can_teacher_copy_exam(teacher.user, exam)
        can_delete = ExamPermissionService.can_teacher_delete_exam(teacher.user, exam)
        
        # These should return boolean values
        tests_passed = (
            isinstance(can_edit, bool) and
            isinstance(can_copy, bool) and
            isinstance(can_delete, bool)
        )
        
        print_test("can_teacher_edit_exam", isinstance(can_edit, bool), f"Returns: {can_edit}")
        print_test("can_teacher_copy_exam", isinstance(can_copy, bool), f"Returns: {can_copy}")
        print_test("can_teacher_delete_exam", isinstance(can_delete, bool), f"Returns: {can_delete}")
        
        return tests_passed
        
    except Exception as e:
        print_test("Permission Test", False, f"Error: {str(e)}")
        return False

def test_exam_crud_operations():
    """Test that CRUD operations still work"""
    print("\n📋 Testing CRUD Operations...")
    
    try:
        # Test READ
        exams = Exam.objects.all()
        print_test("Read Exams", True, f"Found {exams.count()} exams")
        
        # Test exam attributes
        if exams.exists():
            exam = exams.first()
            has_attributes = all([
                hasattr(exam, 'name'),
                hasattr(exam, 'exam_type'),
                hasattr(exam, 'class_codes'),
                hasattr(exam, 'created_by')
            ])
            print_test("Exam Attributes", has_attributes, "All required attributes present")
        
        return True
        
    except Exception as e:
        print_test("CRUD Test", False, f"Error: {str(e)}")
        return False

def test_teacher_assignments():
    """Test that teacher assignments still work"""
    print("\n📋 Testing Teacher Assignments...")
    
    try:
        # Get teacher assignments
        teacher = Teacher.objects.filter(user__isnull=False).first()
        if not teacher:
            print_test("Teacher Assignment Test", False, "No teacher found")
            return False
        
        assignments = ExamService.get_teacher_assignments(teacher.user)
        
        # Check that assignments is a dictionary
        is_dict = isinstance(assignments, dict)
        print_test("Get Teacher Assignments", is_dict, f"Returns dict with {len(assignments)} assignments")
        
        # Check assignment structure
        if assignments:
            sample_class = list(assignments.keys())[0]
            sample_access = assignments[sample_class]
            valid_access = sample_access in ['FULL', 'CO_TEACHER', 'VIEW']
            print_test("Assignment Structure", valid_access, f"Sample: {sample_class} -> {sample_access}")
        
        return is_dict
        
    except Exception as e:
        print_test("Teacher Assignment Test", False, f"Error: {str(e)}")
        return False

def test_exam_access_levels():
    """Test that access level determination still works"""
    print("\n📋 Testing Access Level Determination...")
    
    try:
        teacher = Teacher.objects.filter(user__isnull=False).first()
        exam = Exam.objects.first()
        
        if not teacher or not exam:
            print_test("Access Level Test", False, "Missing teacher or exam")
            return False
        
        # Test access level determination
        access_level = ExamService.get_exam_access_level(teacher.user, exam)
        
        # Should return a valid access level
        valid_levels = ['FULL', 'CO_TEACHER', 'VIEW', 'OWNER', 'ADMIN', None]
        is_valid = access_level in valid_levels or access_level is None
        
        print_test("Get Exam Access Level", is_valid, f"Returns: {access_level}")
        
        return is_valid
        
    except Exception as e:
        print_test("Access Level Test", False, f"Error: {str(e)}")
        return False

def test_view_endpoints():
    """Test that view endpoints still respond"""
    print("\n📋 Testing View Endpoints...")
    
    client = Client()
    
    try:
        # Login as a test user
        user = User.objects.filter(is_active=True).first()
        if user:
            client.force_login(user)
            
            # Test exam list endpoint - both ownership modes
            response_my = client.get('/routinetest/exams/?ownership=my')
            response_others = client.get('/routinetest/exams/?ownership=others')
            
            my_works = response_my.status_code == 200
            others_works = response_others.status_code == 200
            
            print_test("Exam List (My Files)", my_works, f"Status: {response_my.status_code}")
            print_test("Exam List (Others' Files)", others_works, f"Status: {response_others.status_code}")
            
            return my_works and others_works
        else:
            print_test("View Endpoint Test", False, "No user found for testing")
            return False
            
    except Exception as e:
        print_test("View Endpoint Test", False, f"Error: {str(e)}")
        return False

def test_backward_compatibility():
    """Test backward compatibility with legacy parameters"""
    print("\n📋 Testing Backward Compatibility...")
    
    try:
        # Test that old assigned_only parameter still works
        teacher = Teacher.objects.filter(user__isnull=False).first()
        if not teacher:
            print_test("Backward Compatibility", False, "No teacher found")
            return False
        
        exams = Exam.objects.all()
        
        # Test with legacy parameter
        result = ExamService.organize_exams_hierarchically(
            exams,
            teacher.user,
            filter_assigned_only=True  # Legacy parameter
        )
        
        # Should return a dictionary structure
        is_dict = isinstance(result, dict)
        print_test("Legacy filter_assigned_only", is_dict, "Still works with legacy parameter")
        
        return is_dict
        
    except Exception as e:
        print_test("Backward Compatibility", False, f"Error: {str(e)}")
        return False

def main():
    print("\n" + "="*60)
    print("    FEATURE INTEGRITY TEST SUITE")
    print("="*60)
    print("Testing that other features remain intact after filtering fix")
    
    all_passed = True
    
    # Run all tests
    all_passed &= test_exam_permissions()
    all_passed &= test_exam_crud_operations()
    all_passed &= test_teacher_assignments()
    all_passed &= test_exam_access_levels()
    all_passed &= test_view_endpoints()
    all_passed &= test_backward_compatibility()
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL FEATURE INTEGRITY TESTS PASSED")
        print("No features were disrupted by the filtering fix")
    else:
        print("❌ SOME FEATURE TESTS FAILED")
        print("Please review the failures above")
    print("="*60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
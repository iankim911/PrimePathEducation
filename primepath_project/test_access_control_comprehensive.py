#!/usr/bin/env python
"""
Comprehensive Access Control Test
Tests the entire access control system for PrimePath
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from core.models import Teacher
from primepath_student.models import StudentProfile
from primepath_routinetest.models import RoutineExam as Exam, TeacherClassAssignment
from primepath_routinetest.services.exam_service import ExamService
import json

def test_student_access_block():
    """Test that students cannot access RoutineTest"""
    print("\n" + "="*80)
    print("TEST 1: Student Access Block")
    print("="*80)
    
    client = Client()
    
    # Create or get a student user
    try:
        student_user = User.objects.get(username='student1')
    except User.DoesNotExist:
        student_user = User.objects.create_user(
            username='student1',
            password='test123',
            email='student1@test.com'
        )
        StudentProfile.objects.create(
            user=student_user,
            student_id='STU001',
            name='Test Student',
            phone_number='010-1234-5678'
        )
    
    # Try to access RoutineTest as student
    client.login(username='student1', password='test123')
    
    # Test various RoutineTest URLs
    test_urls = [
        '/RoutineTest/',
        '/RoutineTest/exams/',
        '/RoutineTest/students/',
        '/RoutineTest/classes/',
    ]
    
    blocked_count = 0
    for url in test_urls:
        response = client.get(url, follow=True)
        if response.status_code == 302 or 'student' in response.redirect_chain[0][0] if response.redirect_chain else False:
            print(f"  ✅ {url} - Student blocked (redirected)")
            blocked_count += 1
        else:
            print(f"  ❌ {url} - Student NOT blocked! Status: {response.status_code}")
    
    print(f"\nResult: {blocked_count}/{len(test_urls)} URLs properly blocked")
    return blocked_count == len(test_urls)

def test_teacher_default_view_access():
    """Test that all teachers get VIEW access to all exams by default"""
    print("\n" + "="*80)
    print("TEST 2: Teacher Default VIEW Access")
    print("="*80)
    
    # Get teacher2 (no class assignments)
    try:
        teacher2_user = User.objects.get(username='teacher2')
        print(f"Testing with: {teacher2_user.username}")
    except User.DoesNotExist:
        print("❌ teacher2 not found")
        return False
    
    # Get all exams
    all_exams = Exam.objects.all()
    print(f"Total exams in database: {all_exams.count()}")
    
    # Test "Other Teachers' Test Files" filter
    hierarchical_exams = ExamService.organize_exams_hierarchically(
        all_exams,
        teacher2_user,
        filter_assigned_only=True,
        ownership_filter='others',
        filter_intent='SHOW_VIEW_ONLY'
    )
    
    # Count visible exams
    visible_count = sum(len(exams) for classes in hierarchical_exams.values() for exams in classes.values())
    print(f"Exams visible in 'Other Teachers Test Files': {visible_count}")
    
    # Check permissions on a sample exam
    if visible_count > 0:
        for program, classes in hierarchical_exams.items():
            for class_code, exams in classes.items():
                if exams:
                    sample_exam = exams[0]
                    print(f"\nSample exam: {sample_exam.name}")
                    print(f"  Access badge: {getattr(sample_exam, 'access_badge', 'N/A')}")
                    print(f"  Can edit: {getattr(sample_exam, 'can_edit', False)}")
                    print(f"  Can copy: {getattr(sample_exam, 'can_copy', True)}")
                    print(f"  Can delete: {getattr(sample_exam, 'can_delete', False)}")
                    break
            if exams:
                break
    
    success = visible_count > 0
    print(f"\n{'✅ PASS' if success else '❌ FAIL'}: Teacher can see {visible_count} exams with VIEW access")
    return success

def test_teacher_class_assignments():
    """Test teacher class assignment system"""
    print("\n" + "="*80)
    print("TEST 3: Teacher Class Assignment System")
    print("="*80)
    
    # Create test teacher if needed
    try:
        test_teacher_user = User.objects.get(username='testteacher3')
    except User.DoesNotExist:
        test_teacher_user = User.objects.create_user(
            username='testteacher3',
            password='test123',
            email='testteacher3@test.com'
        )
        Teacher.objects.create(
            user=test_teacher_user,
            name='Test Teacher 3',
            email='testteacher3@test.com',
            global_access_level='FULL'
        )
    
    teacher = test_teacher_user.teacher_profile
    
    # Assign a class to the teacher
    assignment, created = TeacherClassAssignment.objects.get_or_create(
        teacher=teacher,
        class_code='PRIMARY_1A',
        defaults={'access_level': 'FULL', 'is_active': True}
    )
    
    print(f"Teacher: {teacher.name}")
    print(f"Assigned class: PRIMARY_1A with {assignment.access_level} access")
    
    # Check teacher's assignments
    assignments = ExamService.get_teacher_assignments(test_teacher_user)
    print(f"Teacher assignments: {assignments}")
    
    # Test "My Test Files" filter
    all_exams = Exam.objects.all()
    my_exams = ExamService.organize_exams_hierarchically(
        all_exams,
        test_teacher_user,
        filter_assigned_only=True,
        ownership_filter='my',
        filter_intent='SHOW_EDITABLE'
    )
    
    my_exam_count = sum(len(exams) for classes in my_exams.values() for exams in classes.values())
    print(f"Exams in 'My Test Files': {my_exam_count}")
    
    success = 'PRIMARY_1A' in assignments and assignments['PRIMARY_1A'] == 'FULL'
    print(f"\n{'✅ PASS' if success else '❌ FAIL'}: Class assignment system working")
    return success

def test_admin_full_access():
    """Test that admin has full access to everything"""
    print("\n" + "="*80)
    print("TEST 4: Admin Full Access")
    print("="*80)
    
    # Get admin user
    try:
        admin_user = User.objects.get(username='admin')
    except User.DoesNotExist:
        print("❌ Admin user not found")
        return False
    
    print(f"Admin user: {admin_user.username}")
    print(f"Is superuser: {admin_user.is_superuser}")
    print(f"Is staff: {admin_user.is_staff}")
    
    # Check admin assignments (should be all classes)
    assignments = ExamService.get_teacher_assignments(admin_user)
    print(f"Admin has access to {len(assignments)} classes")
    
    # Sample check
    if assignments:
        sample_class = list(assignments.keys())[0]
        print(f"Sample: {sample_class} -> {assignments[sample_class]}")
    
    success = len(assignments) > 0 and all(level == 'FULL' for level in assignments.values())
    print(f"\n{'✅ PASS' if success else '❌ FAIL'}: Admin has FULL access to all classes")
    return success

def test_access_control_decorators():
    """Test that access control decorators work"""
    print("\n" + "="*80)
    print("TEST 5: Access Control Decorators")
    print("="*80)
    
    client = Client()
    
    # Test unauthenticated access
    response = client.get('/RoutineTest/exams/')
    if response.status_code == 302:  # Should redirect to login
        print("  ✅ Unauthenticated users redirected to login")
        success = True
    else:
        print(f"  ❌ Unauthenticated users NOT redirected! Status: {response.status_code}")
        success = False
    
    # Test authenticated teacher access
    client.login(username='teacher2', password='teacher123')
    response = client.get('/RoutineTest/exams/')
    if response.status_code == 200:
        print("  ✅ Authenticated teacher can access RoutineTest")
    else:
        print(f"  ❌ Authenticated teacher cannot access! Status: {response.status_code}")
        success = False
    
    print(f"\n{'✅ PASS' if success else '❌ FAIL'}: Access control decorators working")
    return success

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("COMPREHENSIVE ACCESS CONTROL AUDIT")
    print("="*80)
    
    tests = [
        ("Student Access Block", test_student_access_block),
        ("Teacher Default VIEW Access", test_teacher_default_view_access),
        ("Teacher Class Assignments", test_teacher_class_assignments),
        ("Admin Full Access", test_admin_full_access),
        ("Access Control Decorators", test_access_control_decorators),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ ERROR in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*80)
    print("AUDIT SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ACCESS CONTROL SYSTEM IS WORKING CORRECTLY!")
    else:
        print("\n⚠️  ACCESS CONTROL ISSUES DETECTED - REVIEW FAILED TESTS")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
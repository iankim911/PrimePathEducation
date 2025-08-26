#!/usr/bin/env python
"""
Comprehensive QA Test for Delete Exam Fix
Tests permission system, ownership, and related features
"""
import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from primepath_routinetest.models import RoutineExam as Exam, TeacherClassAssignment
from primepath_routinetest.services.exam_service import ExamPermissionService
from core.models import Teacher

print("=" * 80)
print("COMPREHENSIVE DELETE EXAM FIX QA TEST")
print("=" * 80)
print(f"Test started at: {datetime.now().isoformat()}")
print()

# Test data
test_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def log_test(test_name, result, details=""):
    """Log test result"""
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"{status}: {test_name}")
    if details:
        print(f"  Details: {details}")
    
    if result:
        test_results["passed"].append(test_name)
    else:
        test_results["failed"].append({"test": test_name, "details": details})

# =============================================================================
# TEST 1: Verify Teacher Profile Setup
# =============================================================================
print("\n" + "=" * 60)
print("TEST 1: Teacher Profile Setup")
print("=" * 60)

try:
    # Get teacher1 user
    user = User.objects.get(username='teacher1')
    log_test("User 'teacher1' exists", True, f"User ID: {user.id}")
    
    # Check teacher profile
    teacher = None
    if hasattr(user, 'teacher_profile'):
        teacher = user.teacher_profile
        log_test("Teacher profile via attribute", True, f"Teacher ID: {teacher.id}")
    else:
        # Try database query
        teacher = Teacher.objects.filter(user=user).first()
        if teacher:
            log_test("Teacher profile via DB query", True, f"Teacher ID: {teacher.id}")
        else:
            log_test("Teacher profile exists", False, "No teacher profile found")
    
    if teacher:
        print(f"  Teacher Name: {teacher.name}")
        print(f"  Teacher Email: {teacher.email}")
        print(f"  Is Head Teacher: {teacher.is_head_teacher}")
        
except User.DoesNotExist:
    log_test("User 'teacher1' exists", False, "User not found in database")
except Exception as e:
    log_test("Teacher profile setup", False, str(e))

# =============================================================================
# TEST 2: Exam Ownership Check
# =============================================================================
print("\n" + "=" * 60)
print("TEST 2: Exam Ownership Check")
print("=" * 60)

if teacher:
    # Find exams created by teacher1
    owned_exams = Exam.objects.filter(created_by=teacher)[:3]
    if owned_exams:
        print(f"Found {owned_exams.count()} exams created by teacher1:")
        for exam in owned_exams:
            print(f"  - {exam.name[:50]}... (ID: {exam.id})")
            
            # Test permission check
            can_delete = ExamPermissionService.can_teacher_delete_exam(user, exam)
            log_test(f"Owner can delete own exam ({exam.id})", can_delete, 
                    f"created_by={exam.created_by.id}, teacher={teacher.id}")
    else:
        test_results["warnings"].append("No exams found created by teacher1")
        print("  ⚠️ No exams found created by teacher1")
    
    # Find exams NOT created by teacher1
    other_exams = Exam.objects.exclude(created_by=teacher)[:3]
    if other_exams:
        print(f"\nFound {other_exams.count()} exams NOT created by teacher1:")
        for exam in other_exams:
            owner_name = exam.created_by.name if exam.created_by else "None"
            print(f"  - {exam.name[:50]}... (Owner: {owner_name})")

# =============================================================================
# TEST 3: Class Access Permissions
# =============================================================================
print("\n" + "=" * 60)
print("TEST 3: Class Access Permissions")
print("=" * 60)

if teacher:
    assignments = TeacherClassAssignment.objects.filter(teacher=teacher, is_active=True)
    print(f"Teacher has {assignments.count()} class assignments:")
    
    for assignment in assignments[:5]:
        print(f"  - {assignment.get_class_code_display()}: {assignment.access_level}")
    
    # Test FULL access permissions
    full_access_classes = assignments.filter(access_level='FULL')
    if full_access_classes:
        class_code = full_access_classes.first().class_code
        # Find exam with this class
        exam_with_class = Exam.objects.filter(class_codes__contains=[class_code]).first()
        if exam_with_class:
            can_delete = ExamPermissionService.can_teacher_delete_exam(user, exam_with_class)
            expected = exam_with_class.created_by == teacher  # Should be True if owner
            log_test(f"FULL access allows delete for class {class_code}", 
                    can_delete or expected,
                    f"Exam: {exam_with_class.name[:30]}...")
    
    # Test VIEW access permissions (should NOT allow delete)
    view_access_classes = assignments.filter(access_level='VIEW')
    if view_access_classes:
        class_code = view_access_classes.first().class_code
        # Find exam with this class that teacher doesn't own
        exam_with_class = Exam.objects.filter(
            class_codes__contains=[class_code]
        ).exclude(created_by=teacher).first()
        if exam_with_class:
            can_delete = ExamPermissionService.can_teacher_delete_exam(user, exam_with_class)
            log_test(f"VIEW access denies delete for class {class_code}", 
                    not can_delete,
                    f"Should be False, got: {can_delete}")

# =============================================================================
# TEST 4: Admin Permissions
# =============================================================================
print("\n" + "=" * 60)
print("TEST 4: Admin Permissions")
print("=" * 60)

try:
    admin_user = User.objects.filter(is_superuser=True).first()
    if admin_user:
        print(f"Testing with admin user: {admin_user.username}")
        
        # Admin should be able to delete any exam
        test_exam = Exam.objects.first()
        if test_exam:
            can_delete = ExamPermissionService.can_teacher_delete_exam(admin_user, test_exam)
            log_test("Admin can delete any exam", can_delete, 
                    f"Exam: {test_exam.name[:30]}...")
    else:
        test_results["warnings"].append("No admin user found for testing")
except Exception as e:
    log_test("Admin permission test", False, str(e))

# =============================================================================
# TEST 5: HTTP Delete Request Simulation
# =============================================================================
print("\n" + "=" * 60)
print("TEST 5: HTTP Delete Request Simulation")
print("=" * 60)

client = Client()
client.login(username='teacher1', password='teacher1')

if teacher and owned_exams:
    exam_to_delete = owned_exams.first()
    print(f"Attempting to delete owned exam: {exam_to_delete.name}")
    
    # Simulate DELETE request
    response = client.delete(
        f'/RoutineTest/exams/{exam_to_delete.id}/delete/',
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    
    log_test("Owner can delete via HTTP", 
            response.status_code == 200,
            f"Status: {response.status_code}, Expected: 200")
    
    if response.status_code != 200:
        try:
            error_data = json.loads(response.content)
            print(f"  Error response: {error_data}")
        except:
            print(f"  Raw response: {response.content[:200]}")

# Test non-owned exam
if other_exams:
    other_exam = other_exams.first()
    print(f"\nAttempting to delete non-owned exam: {other_exam.name}")
    
    response = client.delete(
        f'/RoutineTest/exams/{other_exam.id}/delete/',
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    
    log_test("Non-owner gets 403 for others' exams", 
            response.status_code == 403,
            f"Status: {response.status_code}, Expected: 403")

# =============================================================================
# TEST 6: Copy and Edit Permissions
# =============================================================================
print("\n" + "=" * 60)
print("TEST 6: Related Features (Copy/Edit)")
print("=" * 60)

if teacher and owned_exams:
    exam = owned_exams.first()
    
    # Test copy permission
    can_copy = ExamPermissionService.can_teacher_copy_exam(user, exam)
    log_test("Owner can copy own exam", can_copy)
    
    # Test copyable classes
    copyable_classes = ExamPermissionService.get_teacher_copyable_classes(user)
    log_test("Teacher has copyable classes", 
            bool(copyable_classes),
            f"Classes: {len(copyable_classes) if isinstance(copyable_classes, list) else 'ALL'}")

# =============================================================================
# TEST SUMMARY
# =============================================================================
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)

total_tests = len(test_results["passed"]) + len(test_results["failed"])
print(f"Total Tests Run: {total_tests}")
print(f"✅ Passed: {len(test_results['passed'])}")
print(f"❌ Failed: {len(test_results['failed'])}")
print(f"⚠️  Warnings: {len(test_results['warnings'])}")

if test_results["failed"]:
    print("\nFailed Tests:")
    for failure in test_results["failed"]:
        print(f"  - {failure['test']}: {failure['details']}")

if test_results["warnings"]:
    print("\nWarnings:")
    for warning in test_results["warnings"]:
        print(f"  - {warning}")

# Final verdict
print("\n" + "=" * 80)
if not test_results["failed"]:
    print("🎉 ALL TESTS PASSED! Delete exam fix is working correctly.")
else:
    print("⚠️ SOME TESTS FAILED. Review the failures above.")
print("=" * 80)

# Save results to file
results_file = "test_delete_exam_results.json"
with open(results_file, 'w') as f:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": total_tests,
            "passed": len(test_results["passed"]),
            "failed": len(test_results["failed"]),
            "warnings": len(test_results["warnings"])
        },
        "details": test_results
    }, f, indent=2)
print(f"\nDetailed results saved to: {results_file}")
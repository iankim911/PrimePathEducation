#!/usr/bin/env python
"""
Test Delete Exam Permissions
Tests the permission checking for exam deletion
"""

import os
import sys
import django
import json

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from primepath_routinetest.models import RoutineExam as Exam, TeacherClassAssignment
from primepath_routinetest.views.exam import delete_exam
from primepath_routinetest.services.exam_service import ExamPermissionService
from core.models import Teacher

def test_delete_permissions():
    """Test the delete exam permission checking"""
    print("\n" + "="*80)
    print("TESTING DELETE EXAM PERMISSIONS")
    print("="*80)
    
    # Get a test user and exam
    admin_user = User.objects.filter(is_superuser=True).first()
    teacher_user = User.objects.filter(username='teacher1').first()
    
    if not admin_user:
        print("❌ No admin user found")
        return
    
    if not teacher_user:
        print("❌ No teacher user found")
        return
    
    print(f"✅ Admin user: {admin_user.username}")
    print(f"✅ Teacher user: {teacher_user.username}")
    
    # Get teacher profile
    teacher_profile = getattr(teacher_user, 'teacher_profile', None)
    if not teacher_profile:
        print("❌ Teacher has no profile")
        return
    
    print(f"✅ Teacher profile: {teacher_profile.name}")
    
    # Get an exam to test with
    exam = Exam.objects.first()
    if not exam:
        print("❌ No exams found")
        return
    
    print(f"✅ Test exam: {exam.name} (ID: {exam.id})")
    
    # Check exam's assigned classes
    exam_classes = []
    if hasattr(exam, 'class_codes') and exam.class_codes:
        exam_classes = exam.class_codes
        print(f"  Exam assigned to classes: {', '.join(exam_classes)}")
    else:
        print("  Exam has no assigned classes")
    
    # Test 1: Check if teacher can delete exam
    print("\n--- Test 1: Permission Check ---")
    can_delete = ExamPermissionService.can_teacher_delete_exam(teacher_user, exam)
    print(f"Can teacher delete exam: {'✅ Yes' if can_delete else '❌ No'}")
    
    # Check teacher's class assignments
    print("\n--- Teacher's Class Assignments ---")
    assignments = TeacherClassAssignment.objects.filter(
        teacher=teacher_profile,
        is_active=True
    )
    
    if assignments.exists():
        for assignment in assignments:
            print(f"  {assignment.class_code}: {assignment.access_level} access")
            if exam_classes and assignment.class_code in exam_classes:
                print(f"    ✅ Assigned to exam's class")
                if assignment.access_level == 'FULL':
                    print(f"    ✅ Has FULL access")
                else:
                    print(f"    ❌ Only has {assignment.access_level} access (needs FULL)")
    else:
        print("  No class assignments")
    
    # Test 2: Simulate DELETE request as teacher
    print("\n--- Test 2: Delete Request as Teacher ---")
    factory = RequestFactory()
    request = factory.delete(f'/RoutineTest/exams/{exam.id}/delete/')
    request.user = teacher_user
    request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
    
    try:
        response = delete_exam(request, str(exam.id))
        response_data = json.loads(response.content.decode())
        
        if response.status_code == 200:
            print(f"✅ Delete allowed: {response_data.get('message', 'Success')}")
        elif response.status_code == 403:
            print(f"❌ Delete denied (403): {response_data.get('error', 'Permission denied')}")
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            print(f"  Response: {response_data}")
    except Exception as e:
        print(f"❌ Error during delete request: {str(e)}")
    
    # Test 3: Simulate DELETE request as admin
    print("\n--- Test 3: Delete Request as Admin ---")
    request_admin = factory.delete(f'/RoutineTest/exams/{exam.id}/delete/')
    request_admin.user = admin_user
    request_admin.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
    
    try:
        response = delete_exam(request_admin, str(exam.id))
        response_data = json.loads(response.content.decode())
        
        if response.status_code == 200:
            print(f"✅ Admin can always delete: {response_data.get('message', 'Success')}")
        else:
            print(f"⚠️ Unexpected response for admin: {response.status_code}")
    except Exception as e:
        print(f"❌ Error during admin delete: {str(e)}")
    
    print("\n" + "="*80)
    print("PERMISSION TEST COMPLETE")
    print("="*80)

if __name__ == '__main__':
    test_delete_permissions()
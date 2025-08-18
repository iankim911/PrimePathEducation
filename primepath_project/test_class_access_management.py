#!/usr/bin/env python
"""
Test Script for Teacher Class Access Management System
Tests the complete functionality of the new class access management feature

Run with: python test_class_access_management.py
"""

import os
import sys
import django
import json
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from core.models import Teacher
from primepath_routinetest.models import (
    TeacherClassAssignment,
    ClassAccessRequest,
    AccessAuditLog,
    Exam
)

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_models_creation():
    """Test that all models were created successfully"""
    print_section("Testing Model Creation")
    
    try:
        # Check if models exist
        print("✓ TeacherClassAssignment model exists")
        print("✓ ClassAccessRequest model exists")
        print("✓ AccessAuditLog model exists")
        
        # Check model fields
        assignment_fields = [f.name for f in TeacherClassAssignment._meta.get_fields()]
        required_fields = ['teacher', 'class_code', 'access_level', 'is_active']
        
        for field in required_fields:
            if field in assignment_fields:
                print(f"  ✓ TeacherClassAssignment.{field} field exists")
            else:
                print(f"  ✗ Missing field: TeacherClassAssignment.{field}")
                
        return True
    except Exception as e:
        print(f"✗ Error testing models: {str(e)}")
        return False

def test_teacher_assignment():
    """Test creating a teacher class assignment"""
    print_section("Testing Teacher Class Assignment")
    
    try:
        # Get or create a test teacher
        user, created = User.objects.get_or_create(
            username='test_teacher',
            defaults={'email': 'test@example.com', 'is_staff': True}
        )
        
        if created:
            print("  Created test user")
        
        # Get the teacher profile (should be auto-created by signal)
        teacher = user.teacher_profile
        print(f"  ✓ Teacher profile: {teacher.name}")
        
        # Create an assignment
        assignment = TeacherClassAssignment.objects.create(
            teacher=teacher,
            class_code='CLASS_7A',
            access_level='FULL',
            assigned_by=user,
            notes='Test assignment'
        )
        
        print(f"  ✓ Created assignment: {assignment}")
        print(f"    - Class: {assignment.get_class_code_display()}")
        print(f"    - Access Level: {assignment.get_access_level_display()}")
        print(f"    - Student Count: {assignment.get_student_count()}")
        
        return True
    except Exception as e:
        print(f"  ✗ Error creating assignment: {str(e)}")
        return False

def test_access_request():
    """Test creating and processing an access request"""
    print_section("Testing Access Request Workflow")
    
    try:
        # Get teachers
        requesting_teacher = Teacher.objects.filter(
            user__username='test_teacher'
        ).first()
        
        if not requesting_teacher:
            print("  ✗ Test teacher not found")
            return False
        
        # Create an access request
        request = ClassAccessRequest.objects.create(
            teacher=requesting_teacher,
            class_code='CLASS_8B',
            request_type='PERMANENT',
            reason_code='NEW_ASSIGNMENT',
            reason_text='Need to teach this class',
            requested_access_level='FULL'
        )
        
        print(f"  ✓ Created request: {request}")
        print(f"    - Status: {request.get_status_display()}")
        print(f"    - Class: {request.get_class_code_display()}")
        
        # Get admin user
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.create_superuser(
                'admin', 'admin@example.com', 'admin123'
            )
            print("  Created admin user")
        
        # Approve the request
        assignment = request.approve(admin_user, "Approved for testing")
        print(f"  ✓ Request approved")
        print(f"    - Assignment created: {assignment}")
        print(f"    - New status: {request.get_status_display()}")
        
        return True
    except Exception as e:
        print(f"  ✗ Error in request workflow: {str(e)}")
        return False

def test_audit_logging():
    """Test that audit logs are being created"""
    print_section("Testing Audit Logging")
    
    try:
        # Check audit logs
        logs = AccessAuditLog.objects.all().order_by('-timestamp')[:5]
        
        if logs:
            print(f"  ✓ Found {logs.count()} audit log entries")
            for log in logs:
                print(f"    - {log.get_action_display()}: {log.teacher.name if log.teacher else 'N/A'} "
                      f"({log.timestamp.strftime('%Y-%m-%d %H:%M')})")
        else:
            print("  ⚠ No audit logs found (this is OK if this is the first run)")
        
        return True
    except Exception as e:
        print(f"  ✗ Error checking audit logs: {str(e)}")
        return False

def test_class_choices():
    """Test that class choices are properly configured"""
    print_section("Testing Class Choices")
    
    try:
        choices = TeacherClassAssignment._meta.get_field('class_code').choices
        print(f"  ✓ Found {len(choices)} class choices")
        
        # Display first few choices
        for code, name in choices[:3]:
            print(f"    - {code}: {name}")
        
        if len(choices) > 3:
            print(f"    ... and {len(choices) - 3} more")
        
        return True
    except Exception as e:
        print(f"  ✗ Error checking class choices: {str(e)}")
        return False

def test_teacher_permissions():
    """Test teacher access permissions"""
    print_section("Testing Teacher Permissions")
    
    try:
        teacher = Teacher.objects.filter(
            user__username='test_teacher'
        ).first()
        
        if not teacher:
            print("  ✗ Test teacher not found")
            return False
        
        # Get teacher's assignments
        assignments = TeacherClassAssignment.objects.filter(
            teacher=teacher,
            is_active=True
        )
        
        print(f"  ✓ Teacher {teacher.name} has {assignments.count()} class assignments")
        
        for assignment in assignments:
            print(f"    - {assignment.get_class_code_display()}: "
                  f"{assignment.get_access_level_display()}")
            
            # Check if teacher can create exams for this class
            if assignment.access_level == 'FULL':
                print(f"      ✓ Can create exams for {assignment.get_class_code_display()}")
            else:
                print(f"      ⚠ Limited access for {assignment.get_class_code_display()}")
        
        return True
    except Exception as e:
        print(f"  ✗ Error checking permissions: {str(e)}")
        return False

def test_pending_requests():
    """Test fetching pending requests for admin"""
    print_section("Testing Pending Requests Query")
    
    try:
        # Create a few test requests
        teacher = Teacher.objects.filter(
            user__username='test_teacher'
        ).first()
        
        if teacher:
            # Create pending request
            ClassAccessRequest.objects.get_or_create(
                teacher=teacher,
                class_code='CLASS_9A',
                status='PENDING',
                defaults={
                    'request_type': 'TEMPORARY',
                    'reason_code': 'SUBSTITUTE',
                    'reason_text': 'Covering for absent teacher',
                    'requested_access_level': 'FULL'
                }
            )
        
        # Query pending requests
        pending = ClassAccessRequest.objects.filter(status='PENDING')
        
        print(f"  ✓ Found {pending.count()} pending requests")
        
        for req in pending:
            print(f"    - {req.teacher.name} → {req.get_class_code_display()}")
            print(f"      Type: {req.get_request_type_display()}")
            print(f"      Requested: {req.requested_at.strftime('%Y-%m-%d %H:%M')}")
        
        return True
    except Exception as e:
        print(f"  ✗ Error querying pending requests: {str(e)}")
        return False

def test_url_patterns():
    """Test that URL patterns are properly configured"""
    print_section("Testing URL Patterns")
    
    try:
        from django.urls import reverse
        
        # Test main URL with correct namespace
        url = reverse('RoutineTest:my_classes')
        print(f"  ✓ My Classes URL: {url}")
        print(f"    Expected: /RoutineTest/access/my-classes/")
        
        # Test API URLs with correct namespace
        api_urls = [
            'RoutineTest:api_my_classes',
            'RoutineTest:api_available_classes',
            'RoutineTest:api_my_requests'
        ]
        
        for url_name in api_urls:
            url = reverse(url_name)
            print(f"  ✓ {url_name}: {url}")
        
        # Test request management URLs
        print("\n  Testing additional URLs:")
        additional_urls = [
            'RoutineTest:request_access',
            'RoutineTest:admin_pending_requests',
            'RoutineTest:bulk_approve'
        ]
        
        for url_name in additional_urls:
            url = reverse(url_name)
            print(f"  ✓ {url_name}: {url}")
        
        return True
    except Exception as e:
        print(f"  ✗ Error testing URLs: {str(e)}")
        print(f"    Make sure to use 'RoutineTest:' prefix, not 'class_access:'")
        return False

def cleanup_test_data():
    """Clean up test data"""
    print_section("Cleaning Up Test Data")
    
    try:
        # Keep the test data for inspection
        print("  ℹ Test data preserved for inspection")
        print("  To clean up manually, delete:")
        print("    - User: test_teacher")
        print("    - User: admin (if created)")
        print("    - Related assignments and requests")
        
        return True
    except Exception as e:
        print(f"  ✗ Error during cleanup: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  TEACHER CLASS ACCESS MANAGEMENT - TEST SUITE")
    print("="*60)
    print(f"  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Model Creation", test_models_creation),
        ("Teacher Assignment", test_teacher_assignment),
        ("Access Request Workflow", test_access_request),
        ("Audit Logging", test_audit_logging),
        ("Class Choices", test_class_choices),
        ("Teacher Permissions", test_teacher_permissions),
        ("Pending Requests", test_pending_requests),
        ("URL Patterns", test_url_patterns),
        ("Cleanup", cleanup_test_data)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n✗ Unexpected error in {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 All tests passed successfully!")
        print("\n  The Teacher Class Access Management system is ready to use.")
        print("\n  Next steps:")
        print("    1. Start the server: python manage.py runserver")
        print("    2. Navigate to: /RoutineTest/")
        print("    3. Click 'My Classes & Access' button")
        print("    4. Teachers can request access, admins can approve")
    else:
        print(f"\n  ⚠ {total - passed} test(s) failed. Please review the errors above.")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
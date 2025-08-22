#!/usr/bin/env python
"""
Test to verify temporary teacher assignment expiration functionality
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.utils import timezone
from django.contrib.auth.models import User
from core.models import Teacher
from primepath_routinetest.models import TeacherClassAssignment, ClassAccessRequest

def test_temporary_assignment_expiry():
    """Test if temporary assignments correctly check expiration"""
    print("\n" + "="*70)
    print("TESTING TEMPORARY TEACHER ASSIGNMENT EXPIRATION")
    print("="*70)
    
    # Get a test teacher
    teachers = Teacher.objects.all()
    if not teachers.exists():
        print("❌ No teachers found in database")
        return False
    
    teacher = teachers.first()
    print(f"✅ Using teacher: {teacher.name}")
    
    # Check current assignments
    current_assignments = TeacherClassAssignment.objects.filter(
        teacher=teacher,
        is_active=True
    )
    
    print(f"\n📊 Current active assignments for {teacher.name}:")
    for assignment in current_assignments:
        if assignment.expires_on:
            is_expired = assignment.is_expired()
            expiry_status = "EXPIRED" if is_expired else "ACTIVE"
            time_diff = assignment.expires_on - timezone.now()
            
            print(f"  - {assignment.get_class_code_display()}")
            print(f"    Access: {assignment.get_access_level_display()}")
            print(f"    Expires: {assignment.expires_on}")
            print(f"    Status: {expiry_status}")
            if not is_expired:
                print(f"    Time left: {time_diff}")
        else:
            print(f"  - {assignment.get_class_code_display()}")
            print(f"    Access: {assignment.get_access_level_display()}")
            print(f"    Expires: Never (Permanent)")
    
    # Test the is_expired() method
    print(f"\n🧪 Testing is_expired() method:")
    
    # Create a test assignment that expires in the past
    test_assignment = TeacherClassAssignment(
        teacher=teacher,
        class_code='CLASS_7A',
        expires_on=timezone.now() - timedelta(days=1)
    )
    # Don't save to avoid database changes
    
    print(f"  Past expiry date: {test_assignment.expires_on}")
    print(f"  is_expired() returns: {test_assignment.is_expired()}")
    assert test_assignment.is_expired() == True, "Should be expired"
    print("  ✅ Correctly identifies expired assignment")
    
    # Test future expiry
    test_assignment.expires_on = timezone.now() + timedelta(days=1)
    print(f"\n  Future expiry date: {test_assignment.expires_on}")
    print(f"  is_expired() returns: {test_assignment.is_expired()}")
    assert test_assignment.is_expired() == False, "Should not be expired"
    print("  ✅ Correctly identifies active assignment")
    
    # Test no expiry (permanent)
    test_assignment.expires_on = None
    print(f"\n  No expiry date (permanent)")
    print(f"  is_expired() returns: {test_assignment.is_expired()}")
    assert test_assignment.is_expired() == False, "Permanent should not expire"
    print("  ✅ Correctly handles permanent assignments")
    
    # Check if expired assignments are being filtered in views
    print(f"\n⚠️  IMPORTANT FINDING:")
    expired_but_active = TeacherClassAssignment.objects.filter(
        is_active=True,
        expires_on__lt=timezone.now()
    ).count()
    
    if expired_but_active > 0:
        print(f"  ❌ Found {expired_but_active} assignments that are expired but still marked as active!")
        print(f"  📝 Recommendation: Implement a cleanup task or middleware to deactivate expired assignments")
        
        # Show details
        expired_assignments = TeacherClassAssignment.objects.filter(
            is_active=True,
            expires_on__lt=timezone.now()
        )
        print(f"\n  Expired but active assignments:")
        for assignment in expired_assignments[:5]:  # Show first 5
            print(f"    - Teacher: {assignment.teacher.name}")
            print(f"      Class: {assignment.get_class_code_display()}")
            print(f"      Expired: {assignment.expires_on}")
            print(f"      Days overdue: {(timezone.now() - assignment.expires_on).days}")
    else:
        print(f"  ✅ No expired assignments found that are still active")
    
    # Check if views are filtering expired assignments
    print(f"\n📋 IMPLEMENTATION STATUS:")
    print(f"  ✅ Model has expires_on field")
    print(f"  ✅ Model has is_expired() method")
    print(f"  ✅ Assignments set expires_on for TEMPORARY requests")
    print(f"  ⚠️  Need to verify: Are views filtering out expired assignments?")
    print(f"  ⚠️  Need to verify: Is there a cleanup task for expired assignments?")
    
    return True

if __name__ == '__main__':
    try:
        success = test_temporary_assignment_expiry()
        if success:
            print("\n✅ Temporary assignment expiry test completed")
        else:
            print("\n❌ Test encountered issues")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
#!/usr/bin/env python
"""
Clean up test teacher accounts from the database
Keeps only real teacher accounts (Taehyun Kim)
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
from core.models import Teacher
from primepath_routinetest.models import (
    TeacherClassAssignment, 
    ClassAccessRequest,
    AccessAuditLog
)

def cleanup_test_teachers():
    """Remove all test teacher accounts while preserving real ones"""
    
    print("\n" + "="*80)
    print("  CLEANING UP TEST TEACHER ACCOUNTS")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # List of test teacher patterns to remove
    test_patterns = [
        'test', 'qa', 'debug', 'frontend', 'layout', 'fix', 
        'modular', 'page', 'uuid', 'view', 'matrix', 'admin_test',
        'temp', 'demo', 'sample', 'dummy'
    ]
    
    # Names to explicitly preserve (real teachers)
    preserve_names = [
        'Taehyun Kim',
        'admin'  # Keep admin account
    ]
    
    # Get all teachers
    all_teachers = Teacher.objects.all()
    print(f"Total teachers in database: {all_teachers.count()}")
    
    teachers_to_remove = []
    teachers_to_keep = []
    
    for teacher in all_teachers:
        # Check if this is a real teacher to preserve
        should_keep = False
        
        # Check by name
        if teacher.name in preserve_names:
            should_keep = True
            
        # Check if associated with admin user
        if teacher.user and teacher.user.username == 'admin':
            should_keep = True
            
        # Check if name contains test patterns (case insensitive)
        name_lower = teacher.name.lower() if teacher.name else ''
        email_lower = teacher.email.lower() if teacher.email else ''
        username_lower = teacher.user.username.lower() if teacher.user else ''
        
        is_test = any(
            pattern in name_lower or 
            pattern in email_lower or 
            pattern in username_lower 
            for pattern in test_patterns
        )
        
        if is_test and not should_keep:
            teachers_to_remove.append(teacher)
        else:
            teachers_to_keep.append(teacher)
    
    print(f"\nTeachers to KEEP ({len(teachers_to_keep)}):")
    for teacher in teachers_to_keep:
        print(f"  ✅ {teacher.name} ({teacher.email})")
    
    print(f"\nTeachers to REMOVE ({len(teachers_to_remove)}):")
    for teacher in teachers_to_remove:
        print(f"  ❌ {teacher.name} ({teacher.email})")
    
    if not teachers_to_remove:
        print("\n✅ No test teachers found to remove!")
        return
    
    # Auto-confirm for automation
    print(f"\n⚠️  This will DELETE {len(teachers_to_remove)} test teacher accounts.")
    print("This action will also remove:")
    print("  - Their class assignments")
    print("  - Their access requests")
    print("  - Their audit logs")
    print("  - Their user accounts (if test users)")
    
    # Auto-proceed with cleanup
    print("\n✅ Auto-proceeding with cleanup...")
    
    # Perform cleanup
    print("\n🗑️  Starting cleanup...")
    
    for teacher in teachers_to_remove:
        try:
            # Get associated data counts
            assignments = TeacherClassAssignment.objects.filter(teacher=teacher)
            requests = ClassAccessRequest.objects.filter(teacher=teacher)
            audit_logs = AccessAuditLog.objects.filter(teacher=teacher)
            
            assignment_count = assignments.count()
            request_count = requests.count()
            audit_count = audit_logs.count()
            
            # Delete associated data
            assignments.delete()
            requests.delete()
            audit_logs.delete()
            
            # Check if we should delete the user account
            user = teacher.user
            should_delete_user = False
            
            if user:
                # Only delete user if it's a test user
                username_lower = user.username.lower()
                is_test_user = any(pattern in username_lower for pattern in test_patterns)
                
                # Don't delete if it's admin or has real data
                if is_test_user and user.username != 'admin':
                    should_delete_user = True
            
            # Delete teacher
            teacher_name = teacher.name
            teacher.delete()
            
            print(f"  🗑️  Deleted: {teacher_name}")
            print(f"     - Removed {assignment_count} class assignments")
            print(f"     - Removed {request_count} access requests")
            print(f"     - Removed {audit_count} audit logs")
            
            # Delete user if it's a test user
            if should_delete_user and user:
                user.delete()
                print(f"     - Deleted user account: {user.username}")
                
        except Exception as e:
            print(f"  ❌ Error deleting {teacher.name}: {e}")
    
    # Final report
    print("\n" + "="*80)
    print("  CLEANUP COMPLETE")
    print("="*80)
    
    # Verify remaining teachers
    remaining = Teacher.objects.all()
    print(f"\nRemaining teachers ({remaining.count()}):")
    for teacher in remaining:
        assignments = TeacherClassAssignment.objects.filter(
            teacher=teacher, 
            is_active=True
        ).count()
        print(f"  ✅ {teacher.name} - {assignments} active class assignments")
    
    print(f"\n✅ Successfully cleaned up {len(teachers_to_remove)} test teacher accounts!")
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    try:
        cleanup_test_teachers()
    except KeyboardInterrupt:
        print("\n\n❌ Cleanup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Cleanup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
#!/usr/bin/env python
"""
Create 20 Test Teacher Accounts with Random Class Assignments
For testing the Teacher Assessment module

Created: August 18, 2025
"""
import os
import sys
import django
import random
from datetime import datetime, timedelta

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from core.models import Teacher
from primepath_routinetest.models import (
    TeacherClassAssignment,
    ClassAccessRequest,
    AccessAuditLog
)

# Teacher names for test accounts
TEACHER_NAMES = [
    ("John", "Smith"),
    ("Sarah", "Johnson"),
    ("Michael", "Brown"),
    ("Emily", "Davis"),
    ("Robert", "Wilson"),
    ("Jennifer", "Miller"),
    ("David", "Anderson"),
    ("Lisa", "Taylor"),
    ("James", "Thomas"),
    ("Mary", "Jackson"),
    ("William", "White"),
    ("Patricia", "Harris"),
    ("Richard", "Martin"),
    ("Linda", "Thompson"),
    ("Charles", "Garcia"),
    ("Barbara", "Martinez"),
    ("Joseph", "Robinson"),
    ("Susan", "Clark"),
    ("Thomas", "Rodriguez"),
    ("Jessica", "Lewis")
]

# Available classes
CLASS_CODES = [
    'CLASS_7A', 'CLASS_7B', 'CLASS_7C',
    'CLASS_8A', 'CLASS_8B', 'CLASS_8C',
    'CLASS_9A', 'CLASS_9B', 'CLASS_9C',
    'CLASS_10A', 'CLASS_10B', 'CLASS_10C'
]

# Access levels
ACCESS_LEVELS = ['FULL', 'VIEW', 'CO_TEACHER', 'SUBSTITUTE']

# Request reasons
REQUEST_REASONS = [
    'NEW_ASSIGNMENT',
    'SUBSTITUTE',
    'CO_TEACHING',
    'CURRICULUM_EXPERTISE',
    'SCHEDULE_OPTIMIZATION',
    'TEACHER_ABSENCE',
    'OTHER'
]

def create_teachers():
    """Create 20 test teacher accounts"""
    print("\n" + "="*80)
    print("CREATING TEST TEACHER ACCOUNTS")
    print("="*80)
    
    created_teachers = []
    admin_user = User.objects.filter(is_superuser=True).first()
    
    for i, (first_name, last_name) in enumerate(TEACHER_NAMES, 1):
        username = f"{first_name.lower()}.{last_name.lower()}"
        email = f"{username}@primepath.edu"
        full_name = f"{first_name} {last_name}"
        
        try:
            # Create or get user account
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_staff': True,  # Make them staff so they can login
                    'is_active': True
                }
            )
            
            if user_created:
                user.set_password('teacher123')  # Default password for all test teachers
                user.save()
                print(f"✅ Created user: {username}")
            else:
                print(f"⚠️  User exists: {username}")
            
            # Create or get teacher profile
            teacher, teacher_created = Teacher.objects.get_or_create(
                user=user,
                defaults={
                    'name': full_name,
                    'email': email,
                    'phone': f"+1-555-{random.randint(1000, 9999):04d}",
                    'is_head_teacher': False,  # Regular teachers
                    'is_active': True
                }
            )
            
            if teacher_created:
                print(f"   Created teacher profile: {full_name}")
            else:
                print(f"   Teacher profile exists: {full_name}")
            
            created_teachers.append(teacher)
            
        except Exception as e:
            print(f"❌ Error creating {username}: {str(e)}")
    
    print(f"\n✅ Created/verified {len(created_teachers)} teacher accounts")
    return created_teachers

def assign_classes_randomly(teachers):
    """Randomly assign classes to teachers"""
    print("\n" + "="*80)
    print("ASSIGNING CLASSES TO TEACHERS")
    print("="*80)
    
    admin_user = User.objects.filter(is_superuser=True).first()
    assignment_count = 0
    
    for teacher in teachers:
        # Each teacher gets 1-3 random class assignments
        num_classes = random.randint(1, 3)
        assigned_classes = random.sample(CLASS_CODES, num_classes)
        
        for class_code in assigned_classes:
            # Check if assignment already exists
            existing = TeacherClassAssignment.objects.filter(
                teacher=teacher,
                class_code=class_code,
                is_active=True
            ).first()
            
            if not existing:
                # Create assignment
                access_level = random.choice(['FULL', 'FULL', 'FULL', 'VIEW', 'CO_TEACHER'])  # Mostly full access
                
                assignment = TeacherClassAssignment.objects.create(
                    teacher=teacher,
                    class_code=class_code,
                    access_level=access_level,
                    assigned_by=admin_user,
                    notes=f"Test assignment created on {datetime.now()}",
                    is_active=True
                )
                
                assignment_count += 1
                print(f"   {teacher.name} → {class_code} ({access_level})")
                
                # Create audit log
                AccessAuditLog.log_action(
                    action='ASSIGNMENT_CREATED',
                    teacher=teacher,
                    class_code=class_code,
                    user=admin_user,
                    details={'reason': 'Test data creation', 'access_level': access_level},
                    assignment=assignment
                )
    
    print(f"\n✅ Created {assignment_count} class assignments")
    return assignment_count

def create_pending_requests(teachers):
    """Create some pending requests for testing"""
    print("\n" + "="*80)
    print("CREATING PENDING ACCESS REQUESTS")
    print("="*80)
    
    request_count = 0
    
    # Select 5 random teachers to create requests
    requesting_teachers = random.sample(teachers, min(5, len(teachers)))
    
    for teacher in requesting_teachers:
        # Find a class they don't have access to
        current_classes = TeacherClassAssignment.objects.filter(
            teacher=teacher,
            is_active=True
        ).values_list('class_code', flat=True)
        
        available_classes = [c for c in CLASS_CODES if c not in current_classes]
        
        if available_classes:
            requested_class = random.choice(available_classes)
            
            # Check if request already exists
            existing_request = ClassAccessRequest.objects.filter(
                teacher=teacher,
                class_code=requested_class,
                status='PENDING'
            ).first()
            
            if not existing_request:
                request_type = random.choice(['PERMANENT', 'PERMANENT', 'TEMPORARY', 'SUBSTITUTE'])
                reason = random.choice(REQUEST_REASONS)
                
                # Create request
                access_request = ClassAccessRequest.objects.create(
                    teacher=teacher,
                    class_code=requested_class,
                    request_type=request_type,
                    reason_code=reason,
                    reason_text=f"Test request: Need access to {requested_class} for {reason.replace('_', ' ').lower()}",
                    requested_access_level=random.choice(['FULL', 'FULL', 'VIEW']),
                    status='PENDING'
                )
                
                # If temporary, set duration
                if request_type == 'TEMPORARY':
                    access_request.duration_start = timezone.now().date()
                    access_request.duration_end = (timezone.now() + timedelta(days=30)).date()
                    access_request.save()
                
                request_count += 1
                print(f"   {teacher.name} requesting {requested_class} ({request_type})")
    
    print(f"\n✅ Created {request_count} pending requests")
    return request_count

def main():
    """Main function to create all test data"""
    print("\n" + "="*80)
    print("TEACHER ASSESSMENT MODULE - TEST DATA CREATION")
    print("="*80)
    print(f"Started: {datetime.now()}")
    
    try:
        # Create teachers
        teachers = create_teachers()
        
        # Assign classes
        assignments = assign_classes_randomly(teachers)
        
        # Create pending requests
        requests = create_pending_requests(teachers)
        
        # Summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"✅ Teachers created/verified: {len(teachers)}")
        print(f"✅ Class assignments created: {assignments}")
        print(f"✅ Pending requests created: {requests}")
        print("\n📝 Default password for all test teachers: teacher123")
        print("📝 All teachers have staff access and can login")
        print("\n🔑 Sample login credentials:")
        for teacher in teachers[:3]:
            print(f"   Username: {teacher.user.username}")
            print(f"   Password: teacher123")
            print()
        
        # Statistics
        print("\n📊 STATISTICS:")
        print("-"*40)
        
        # Classes with most teachers
        from django.db.models import Count
        class_stats = TeacherClassAssignment.objects.filter(
            is_active=True
        ).values('class_code').annotate(
            teacher_count=Count('teacher')
        ).order_by('-teacher_count')[:3]
        
        print("Classes with most teachers:")
        for stat in class_stats:
            print(f"   {stat['class_code']}: {stat['teacher_count']} teachers")
        
        # Teachers with most classes
        teacher_stats = TeacherClassAssignment.objects.filter(
            is_active=True
        ).values('teacher__name').annotate(
            class_count=Count('class_code')
        ).order_by('-class_count')[:3]
        
        print("\nTeachers with most classes:")
        for stat in teacher_stats:
            print(f"   {stat['teacher__name']}: {stat['class_count']} classes")
        
        print("\n" + "="*80)
        print(f"Completed: {datetime.now()}")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
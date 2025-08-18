"""
BUILDER: Create test users for RoutineTest Day 1 testing
Creates:
- Admin user (superuser)
- Teacher user (with Teacher profile)
- Student user (regular user)
"""
import os
import sys
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from core.models import Teacher

def create_test_users():
    print("BUILDER: Creating RoutineTest test users...")
    
    # 1. Create Admin User
    admin_username = 'admin'
    admin_password = 'admin123'
    
    admin_user, created = User.objects.get_or_create(
        username=admin_username,
        defaults={
            'email': 'admin@primepath.com',
            'is_superuser': True,
            'is_staff': True,
            'first_name': 'Admin',
            'last_name': 'User'
        }
    )
    if created:
        admin_user.set_password(admin_password)
        admin_user.save()
        print(f"✅ Created ADMIN user: {admin_username} / {admin_password}")
    else:
        print(f"✓ ADMIN user already exists: {admin_username}")
    
    # 2. Create Teacher User
    teacher_username = 'teacher1'
    teacher_password = 'teacher123'
    
    teacher_user, created = User.objects.get_or_create(
        username=teacher_username,
        defaults={
            'email': 'teacher1@primepath.com',
            'is_staff': False,
            'first_name': 'John',
            'last_name': 'Smith'
        }
    )
    if created:
        teacher_user.set_password(teacher_password)
        teacher_user.save()
        print(f"✅ Created TEACHER user: {teacher_username} / {teacher_password}")
    else:
        print(f"✓ TEACHER user already exists: {teacher_username}")
    
    # Create Teacher profile
    teacher_profile, created = Teacher.objects.get_or_create(
        user=teacher_user,
        defaults={
            'name': 'John Smith',
            'email': 'teacher1@primepath.com',
            'phone': '555-0101'
        }
    )
    if created:
        print(f"✅ Created Teacher profile for {teacher_username}")
    else:
        print(f"✓ Teacher profile already exists for {teacher_username}")
    
    # 3. Create Student User
    student_username = 'student1'
    student_password = 'student123'
    
    student_user, created = User.objects.get_or_create(
        username=student_username,
        defaults={
            'email': 'student1@primepath.com',
            'is_staff': False,
            'first_name': 'Jane',
            'last_name': 'Doe'
        }
    )
    if created:
        student_user.set_password(student_password)
        student_user.save()
        print(f"✅ Created STUDENT user: {student_username} / {student_password}")
    else:
        print(f"✓ STUDENT user already exists: {student_username}")
    
    print("\n" + "="*50)
    print("BUILDER: Test users ready for Day 1!")
    print("="*50)
    print("\nLogin credentials:")
    print(f"  ADMIN:   {admin_username} / {admin_password}")
    print(f"  TEACHER: {teacher_username} / {teacher_password}")
    print(f"  STUDENT: {student_username} / {student_password}")
    print("\nTest at: http://127.0.0.1:8000/RoutineTest/login/")
    print("="*50)

if __name__ == "__main__":
    create_test_users()
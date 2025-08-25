"""
Fix admin user to be a head teacher
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from core.models import Teacher

def fix_admin_head_teacher():
    print("\n=== FIXING ADMIN HEAD TEACHER STATUS ===\n")
    
    # Get admin user
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No admin user found")
        return False
    
    print(f"Admin user: {admin_user.username}")
    
    # Get or create teacher profile
    teacher, created = Teacher.objects.get_or_create(
        user=admin_user,
        defaults={
            'name': admin_user.username,
            'is_head_teacher': True
        }
    )
    
    if created:
        print(f"✅ Created Teacher profile as head teacher")
    else:
        # Update existing teacher to be head teacher
        if not teacher.is_head_teacher:
            teacher.is_head_teacher = True
            teacher.save()
            print(f"✅ Updated {teacher.name} to be head teacher")
        else:
            print(f"✓ {teacher.name} is already a head teacher")
    
    print(f"\nFinal status:")
    print(f"  Teacher: {teacher.name}")
    print(f"  Is head teacher: {teacher.is_head_teacher}")
    print(f"  User is superuser: {admin_user.is_superuser}")
    print(f"  User is staff: {admin_user.is_staff}")
    
    return True

if __name__ == "__main__":
    success = fix_admin_head_teacher()
    sys.exit(0 if success else 1)
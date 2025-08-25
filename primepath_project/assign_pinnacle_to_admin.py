"""
Assign PINNACLE classes to admin teacher
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from core.models import Teacher
from primepath_routinetest.models import TeacherClassAssignment
from primepath_routinetest.models.class_model import Class

def assign_pinnacle_to_admin():
    print("\n=== ASSIGNING PINNACLE CLASSES TO ADMIN ===\n")
    
    # Get admin user and their teacher profile
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No admin user found")
        return False
    
    # Get or create Teacher profile for admin
    teacher, created = Teacher.objects.get_or_create(
        user=admin_user,
        defaults={
            'name': admin_user.username,
            'is_head_teacher': True
        }
    )
    
    if created:
        print(f"✅ Created Teacher profile for {admin_user.username}")
    else:
        print(f"✅ Using existing Teacher profile for {admin_user.username}")
    
    # Get all PINNACLE classes
    pinnacle_classes = Class.objects.filter(section__startswith='PINNACLE')
    print(f"\n📚 Found {pinnacle_classes.count()} PINNACLE classes")
    
    # Assign each PINNACLE class to admin teacher
    assignments_created = 0
    for class_obj in pinnacle_classes:
        assignment, created = TeacherClassAssignment.objects.get_or_create(
            teacher=teacher,
            class_code=class_obj.section,
            defaults={
                'access_level': 'FULL',
                'is_active': True
            }
        )
        
        if created:
            print(f"✅ Assigned {class_obj.section} to {teacher.name}")
            assignments_created += 1
        else:
            print(f"✓ {class_obj.section} already assigned to {teacher.name}")
    
    print(f"\n=== SUMMARY ===")
    print(f"Teacher: {teacher.name} (ID: {teacher.id})")
    print(f"PINNACLE classes: {pinnacle_classes.count()}")
    print(f"New assignments: {assignments_created}")
    print(f"Total assignments: {TeacherClassAssignment.objects.filter(teacher=teacher, class_code__startswith='PINNACLE').count()}")
    
    return True

if __name__ == "__main__":
    success = assign_pinnacle_to_admin()
    sys.exit(0 if success else 1)
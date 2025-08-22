#!/usr/bin/env python
"""
Set the password for teacher1 user
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User

# Find teacher1 user
teacher1 = User.objects.filter(username='teacher1').first()

if teacher1:
    # Set the password to teacher123
    teacher1.set_password('teacher123')
    teacher1.save()
    print(f"✅ Password set successfully for user: {teacher1.username}")
    print(f"   Username: teacher1")
    print(f"   Password: teacher123")
    print(f"   User ID: {teacher1.id}")
    print(f"   Is active: {teacher1.is_active}")
    print(f"   Is staff: {teacher1.is_staff}")
    
    # Check if user has teacher profile
    if hasattr(teacher1, 'teacher_profile'):
        print(f"   Has teacher profile: Yes")
        print(f"   Teacher name: {teacher1.teacher_profile.name}")
    else:
        print(f"   Has teacher profile: No")
else:
    print("❌ Error: teacher1 user not found in database")
    
    # List all users to help debug
    print("\nAvailable users in database:")
    for user in User.objects.all():
        print(f"   - {user.username} (ID: {user.id})")
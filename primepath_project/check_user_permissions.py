#!/usr/bin/env python3
"""Check user permissions for delete button visibility"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from core.models import Teacher

print("\n" + "="*80)
print("USER PERMISSION CHECK FOR DELETE BUTTON")
print("="*80 + "\n")

# Check all users
users = User.objects.all()
for user in users:
    print(f"User: {user.username}")
    print(f"  - is_superuser: {user.is_superuser}")
    print(f"  - is_staff: {user.is_staff}")
    print(f"  - is_active: {user.is_active}")
    print(f"  - Delete button visible: {'YES' if (user.is_superuser or user.is_staff) else 'NO'}")
    
    # Check if user has teacher profile
    try:
        teacher = Teacher.objects.get(user=user)
        print(f"  - Has teacher profile: {teacher.name}")
        print(f"  - Is head teacher: {teacher.is_head_teacher}")
    except Teacher.DoesNotExist:
        print(f"  - No teacher profile")
    
    print()

print("\n" + "="*80)
print("SOLUTION:")
print("="*80)
print("\nTo make the delete button visible for a user, you need to:")
print("1. Make them a superuser (is_superuser=True)")
print("2. OR make them staff (is_staff=True)")
print("\nFor the admin user, run this command:")
print("python manage.py shell")
print(">>> from django.contrib.auth.models import User")
print(">>> user = User.objects.get(username='admin')")
print(">>> user.is_superuser = True")
print(">>> user.is_staff = True")
print(">>> user.save()")
print(">>> print(f'User {user.username} now has admin privileges')")
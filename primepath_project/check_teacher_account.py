#!/usr/bin/env python
"""Check and fix teacher1 account"""
import os
import sys
import django

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

# Check if teacher1 exists
try:
    user = User.objects.get(username='teacher1')
    print(f"✅ User 'teacher1' exists")
    print(f"   Email: {user.email}")
    print(f"   Active: {user.is_active}")
    print(f"   Staff: {user.is_staff}")
    
    # Test authentication with ModelBackend directly
    from django.contrib.auth.backends import ModelBackend
    backend = ModelBackend()
    auth_user = backend.authenticate(None, username='teacher1', password='teacher123')
    
    if auth_user:
        print("✅ Password 'teacher123' is correct (ModelBackend)")
    else:
        print("❌ Password 'teacher123' is incorrect")
        print("   Resetting password to 'teacher123'...")
        user.set_password('teacher123')
        user.save()
        print("✅ Password has been reset to 'teacher123'")
        
except User.DoesNotExist:
    print("❌ User 'teacher1' does not exist")
    print("   Creating user 'teacher1' with password 'teacher123'...")
    user = User.objects.create_user(
        username='teacher1',
        password='teacher123',
        email='teacher1@example.com',
        is_staff=True
    )
    print("✅ User 'teacher1' created successfully")

# Test authentication with full Django auth
print("\nTesting full Django authentication:")
test_user = authenticate(username='teacher1', password='teacher123')
if test_user:
    print("✅ Authentication successful with Django authenticate()")
    print(f"   User: {test_user.username}")
else:
    print("❌ Authentication failed with Django authenticate()")
    print("   This might be due to authentication backend issues")

# Check for Teacher profile
try:
    from core.models import Teacher
    teacher = Teacher.objects.get(user=user)
    print(f"\n✅ Teacher profile exists")
    print(f"   Name: {teacher.name}")
    print(f"   Head Teacher: {teacher.is_head_teacher}")
except:
    print("\n⚠️  No Teacher profile found (this is okay for basic login)")
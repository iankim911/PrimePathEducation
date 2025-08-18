#!/usr/bin/env python
"""
Consolidate duplicate admin teacher profiles
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from core.models import Teacher
from primepath_routinetest.models import TeacherClassAssignment

# Get admin user
admin_user = User.objects.get(username='admin')

# Find all teacher profiles linked to admin
admin_teachers = Teacher.objects.filter(user=admin_user)
print(f'Found {admin_teachers.count()} teacher profiles for admin user:')
for t in admin_teachers:
    print(f'  - ID: {t.id}, Name: "{t.name}", Email: {t.email}')

if admin_teachers.count() > 1:
    # Keep the one with the best data
    primary = None
    for t in admin_teachers:
        if t.name == 'admin' and t.email == 'admin@example.com':
            primary = t
            break
    
    if not primary:
        primary = admin_teachers.first()
    
    print(f'\nKeeping primary admin teacher: ID {primary.id}, "{primary.name}"')
    
    # Delete duplicates
    for t in admin_teachers:
        if t.id != primary.id:
            print(f'  🗑️  Removing duplicate: ID {t.id}')
            # Transfer any assignments
            TeacherClassAssignment.objects.filter(teacher=t).update(teacher=primary)
            t.delete()

# Final clean list
print('\n✅ FINAL CLEAN TEACHER LIST:')
for t in Teacher.objects.all().order_by('name'):
    assignments = TeacherClassAssignment.objects.filter(teacher=t, is_active=True).count()
    user_info = f'(User: {t.user.username})' if t.user else '(No user)'
    print(f'  • {t.name} - {t.email} - {assignments} classes {user_info}')
#!/usr/bin/env python
"""
Create Student Account Script
============================
Creates a student account with ID: student1 and password: student123
"""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from primepath_student.models import StudentProfile

def create_student_account():
    """Create student account with specified credentials"""
    
    print("="*60)
    print("CREATING STUDENT ACCOUNT")
    print("="*60)
    
    try:
        # Create user account
        if User.objects.filter(username='student1').exists():
            print('⚠️  User student1 already exists, updating password...')
            user = User.objects.get(username='student1')
            user.set_password('student123')
            user.save()
            print('✅ Updated password for existing student1')
        else:
            user = User.objects.create_user(
                username='student1',
                password='student123',
                email='student1@example.com',
                first_name='Student',
                last_name='One'
            )
            print('✅ Created user account: student1')
        
        # Create student profile
        student_profile, created = StudentProfile.objects.get_or_create(
            user=user,
            defaults={
                'student_id': 'student1',
                'phone_number': '010-1234-5678',
                'grade': '10',
                'school_name': 'Test School'
            }
        )
        
        if created:
            print('✅ Created student profile')
        else:
            print('✅ Student profile already exists')
            
        print()
        print('=' * 40)
        print('STUDENT ACCOUNT CREATED SUCCESSFULLY')
        print('=' * 40)
        print(f'Student ID: {student_profile.student_id}')
        print(f'Username: {user.username}')
        print(f'Password: student123')
        print(f'Full Name: {user.get_full_name()}')
        print(f'Phone: {student_profile.phone_number}')
        print(f'Grade: {student_profile.get_grade_display()}')
        print(f'School: {student_profile.school_name}')
        print()
        print('🌐 Student Login URL: http://127.0.0.1:8000/student/login/')
        print('📝 Registration URL: http://127.0.0.1:8000/student/register/')
        print()
        
        return True
        
    except Exception as e:
        print(f'❌ Error creating student account: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = create_student_account()
    sys.exit(0 if success else 1)
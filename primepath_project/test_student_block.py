#!/usr/bin/env python
"""
Test that students are properly blocked from accessing teacher system
"""
import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from primepath_student.models import StudentProfile

def test_student_block():
    """Test that students cannot access teacher system"""
    print("\n" + "="*80)
    print("TESTING STUDENT BLOCK FROM TEACHER SYSTEM")
    print("="*80)
    
    client = Client()
    
    # Try to find a student user
    try:
        # Check if student1 exists
        student_user = User.objects.get(username='student1')
        print(f"✅ Found student user: {student_user.username}")
        
        # Check if they have a student profile
        if hasattr(student_user, 'primepath_student_profile'):
            student_profile = student_user.primepath_student_profile
            print(f"✅ Student has profile: ID={student_profile.student_id}")
        else:
            print("❌ Student user doesn't have student profile")
            return
            
    except User.DoesNotExist:
        print("❌ No student1 user found, creating one for testing...")
        student_user = User.objects.create_user(
            username='student1',
            password='test123'
        )
        StudentProfile.objects.create(
            user=student_user,
            student_id='student1',
            phone_number='010-1234-5678',
            name='Test Student',
            email='student1@test.com'
        )
        print(f"✅ Created test student: {student_user.username}")
    
    # Try to login as student
    login_success = client.login(username='student1', password='test123')
    if login_success:
        print("✅ Student logged in successfully")
    else:
        print("❌ Failed to login as student")
        # Try setting password
        student_user.set_password('test123')
        student_user.save()
        login_success = client.login(username='student1', password='test123')
        if login_success:
            print("✅ Student logged in after password reset")
        else:
            print("❌ Still can't login")
            return
    
    # Test accessing teacher URLs
    teacher_urls = [
        '/RoutineTest/',
        '/RoutineTest/exams/',
        '/RoutineTest/classes-exams/',
        '/RoutineTest/exams/create/',
        '/RoutineTest/access/my-classes/',
    ]
    
    print("\n" + "-"*40)
    print("Testing teacher URL access as student:")
    print("-"*40)
    
    for url in teacher_urls:
        response = client.get(url, follow=True)
        
        # Check if redirected away from teacher area
        if response.status_code == 200:
            # Check if we're still in RoutineTest area (bad) or redirected (good)
            final_url = response.wsgi_request.path
            if '/RoutineTest/' in final_url:
                print(f"❌ {url} -> ACCESSIBLE (BAD!)")
                print(f"   Final URL: {final_url}")
            else:
                print(f"✅ {url} -> BLOCKED (redirected to {final_url})")
        else:
            print(f"✅ {url} -> Status {response.status_code} (blocked)")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == '__main__':
    test_student_block()
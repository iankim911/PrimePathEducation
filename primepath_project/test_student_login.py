#!/usr/bin/env python3
"""
Test script to verify student login functionality works properly
"""
import os
import sys
import django

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from primepath_student.models import StudentProfile

def test_student_login():
    """Test student login functionality"""
    print("=" * 60)
    print("TESTING STUDENT LOGIN FUNCTIONALITY")
    print("=" * 60)
    
    client = Client()
    
    # Step 1: Create a test student
    print("\n1. Creating test student account...")
    try:
        # Delete existing test user and profile if exists
        try:
            existing_profile = StudentProfile.objects.get(phone_number='010-9999-8888')
            existing_profile.user.delete()  # This also deletes the profile
        except StudentProfile.DoesNotExist:
            pass
            
        User.objects.filter(username='test_student_001').delete()
        
        # Create new test user
        user = User.objects.create_user(
            username='test_student_001',
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='Student'
        )
        
        # Create student profile with unique phone number
        profile = StudentProfile.objects.create(
            user=user,
            student_id='test_student_001',
            phone_number='010-9999-8888',  # Using a different test phone number
            grade='10'
        )
        
        print("   ✅ Test student created successfully")
        print(f"   📝 Student ID: {profile.student_id}")
        print(f"   📱 Phone: {profile.phone_number}")
        
    except Exception as e:
        print(f"   ❌ Failed to create test student: {e}")
        return False
    
    # Step 2: Test login page loads
    print("\n2. Testing login page...")
    response = client.get('/student/login/')
    if response.status_code == 200:
        print("   ✅ Login page loads successfully")
        
        # Check for Kakao references
        content = response.content.decode('utf-8')
        if 'kakao' in content.lower():
            print("   ⚠️  Warning: Kakao references still present in login page")
        else:
            print("   ✅ No Kakao references in login page")
    else:
        print(f"   ❌ Login page failed: {response.status_code}")
        return False
    
    # Step 3: Test login with student ID
    print("\n3. Testing login with Student ID...")
    response = client.post('/student/login/', {
        'login_id': 'test_student_001',
        'password': 'TestPass123!'
    }, follow=True)
    
    if response.status_code == 200:
        if response.wsgi_request.user.is_authenticated:
            print("   ✅ Login successful with Student ID")
            print(f"   👤 Logged in as: {response.wsgi_request.user.username}")
        else:
            print("   ❌ Login failed - user not authenticated")
    else:
        print(f"   ❌ Login request failed: {response.status_code}")
    
    # Step 4: Logout and test login with phone number
    client.logout()
    print("\n4. Testing login with Phone Number...")
    response = client.post('/student/login/', {
        'login_id': '010-9999-8888',  # Use the test phone number
        'password': 'TestPass123!'
    }, follow=True)
    
    if response.status_code == 200:
        if response.wsgi_request.user.is_authenticated:
            print("   ✅ Login successful with Phone Number")
            print(f"   👤 Logged in as: {response.wsgi_request.user.username}")
        else:
            print("   ❌ Login failed with phone number")
    else:
        print(f"   ❌ Login request failed: {response.status_code}")
    
    # Step 5: Test registration page doesn't have Kakao button
    print("\n5. Checking registration page...")
    response = client.get('/student/register/')
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        if 'kakao_login' in content:
            print("   ❌ Kakao login URL still present in registration page")
        elif 'social-btn kakao' in content:
            print("   ❌ Kakao button styling still present")
        else:
            print("   ✅ Kakao button removed from registration page")
    
    # Cleanup
    print("\n6. Cleaning up test data...")
    try:
        user.delete()
        print("   ✅ Test data cleaned up")
    except:
        print("   ⚠️  Cleanup failed")
    
    print("\n" + "=" * 60)
    print("✅ STUDENT LOGIN TEST COMPLETED")
    print("=" * 60)
    return True

if __name__ == '__main__':
    test_student_login()
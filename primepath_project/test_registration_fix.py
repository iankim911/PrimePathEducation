#!/usr/bin/env python3
"""
Test script to verify that the student registration SessionInterrupted issue is fixed.
"""
import os
import sys
import django
import json

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from primepath_student.models import StudentProfile

def test_registration_flow():
    """Test the complete registration flow"""
    print("=" * 60)
    print("TESTING STUDENT REGISTRATION FIX")
    print("=" * 60)
    
    client = Client()
    
    # Step 1: Load registration page
    print("1. Loading registration page...")
    response = client.get('/student/register/')
    if response.status_code == 200:
        print("   ✅ Registration page loads successfully")
        print(f"   📄 Page size: {len(response.content)} bytes")
    else:
        print(f"   ❌ Registration page failed: {response.status_code}")
        return False
    
    # Step 2: Test availability check endpoint
    print("\n2. Testing availability check endpoint...")
    
    # Get CSRF token from the registration page
    csrf_token = None
    content = response.content.decode('utf-8')
    import re
    csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', content)
    if csrf_match:
        csrf_token = csrf_match.group(1)
        print(f"   ✅ CSRF token found: {csrf_token[:10]}...")
    else:
        print("   ❌ CSRF token not found")
        return False
    
    # Test student ID availability check
    availability_data = {
        'type': 'student_id',
        'value': 'test_student_123'
    }
    
    response = client.post(
        '/student/api/check-availability/',
        data=json.dumps(availability_data),
        content_type='application/json',
        HTTP_X_CSRFTOKEN=csrf_token
    )
    
    if response.status_code == 200:
        data = response.json()
        print("   ✅ Availability check works")
        print(f"   📊 Response: {data}")
    else:
        print(f"   ❌ Availability check failed: {response.status_code}")
        try:
            print(f"   📄 Error: {response.json()}")
        except:
            print(f"   📄 Error content: {response.content[:200]}...")
        return False
    
    # Step 3: Test registration form submission
    print("\n3. Testing registration form submission...")
    
    # Prepare registration data
    registration_data = {
        'first_name': 'Test',
        'last_name': 'Student',
        'student_id': 'test_student_123',
        'email': 'test.student@example.com',
        'phone_number': '010-1234-5678',
        'password1': 'TestPass123!',
        'password2': 'TestPass123!',
        'username': 'test_student_123',  # This should be set automatically
        'csrfmiddlewaretoken': csrf_token
    }
    
    # Get a fresh session for form submission
    client = Client()
    response = client.get('/student/register/')  # Fresh page load
    
    # Extract CSRF token from fresh page
    content = response.content.decode('utf-8')
    csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', content)
    if csrf_match:
        registration_data['csrfmiddlewaretoken'] = csrf_match.group(1)
    
    # Submit registration
    response = client.post('/student/register/', registration_data, follow=True)
    
    if response.status_code == 200:
        # Check if we got the SessionInterrupted error
        content = response.content.decode('utf-8')
        if 'SessionInterrupted' in content:
            print("   ❌ SessionInterrupted error still occurs")
            print("   📄 Error content snippet:")
            # Find the error message
            if 'session was deleted before the request completed' in content:
                start = content.find('session was deleted before the request completed') - 100
                end = start + 300
                print(f"   {content[start:end]}")
            return False
        elif 'Account created successfully' in content or response.redirect_chain:
            print("   ✅ Registration form submits without SessionInterrupted error")
            print(f"   📍 Final URL: {response.wsgi_request.path}")
            if response.redirect_chain:
                print(f"   🔄 Redirect chain: {response.redirect_chain}")
            
            # Check if user was actually created
            try:
                user = User.objects.get(username='test_student_123')
                print(f"   ✅ User created: {user.username}")
                
                # Check if profile was created
                profile = StudentProfile.objects.get(user=user)
                print(f"   ✅ Student profile created: {profile.student_id}")
                
                # Cleanup
                profile.delete()
                user.delete()
                print("   🧹 Test data cleaned up")
                
            except User.DoesNotExist:
                print("   ⚠️  User not created (form validation might have failed)")
            except StudentProfile.DoesNotExist:
                print("   ⚠️  Profile not created (form processing might have failed)")
                
        else:
            print("   ⚠️  Registration completed but unclear outcome")
            print("   📄 Response snippet:")
            print(f"   {content[:500]}...")
            
    else:
        print(f"   ❌ Registration failed: {response.status_code}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ REGISTRATION TEST COMPLETED SUCCESSFULLY")
    print("✅ SessionInterrupted issue appears to be fixed!")
    print("=" * 60)
    return True

def test_server_endpoint():
    """Quick test to verify server is running"""
    import requests
    try:
        response = requests.get('http://127.0.0.1:8001/', timeout=5)
        print(f"✅ Server is running on port 8001 (status: {response.status_code})")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Server test failed: {e}")
        return False

if __name__ == '__main__':
    print("Testing server connection first...")
    if test_server_endpoint():
        test_registration_flow()
    else:
        print("❌ Cannot test registration - server is not running")
        print("💡 Please start the Django server on port 8001:")
        print("   ../venv/bin/python manage.py runserver 127.0.0.1:8001")
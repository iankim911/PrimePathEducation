#!/usr/bin/env python
"""Test modern login/signup form"""

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

print("=" * 60)
print("TESTING MODERN LOGIN/SIGNUP FORM")
print("=" * 60)

client = Client()

# Test 1: Check if login page loads with modern template
print("\n1. Testing Login Page:")
response = client.get('/student/login/')
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    content = response.content.decode()
    if 'tab-btn' in content and 'Sign In' in content and 'Sign Up' in content:
        print("   ✅ Modern toggle form loaded")
    else:
        print("   ❌ Old form still loading")
    
    if 'password-toggle' in content:
        print("   ✅ Password visibility toggle present")
    else:
        print("   ❌ Password toggle missing")

# Test 2: Check if register page loads with modern template
print("\n2. Testing Register Page:")
response = client.get('/student/register/')
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    content = response.content.decode()
    if 'tab-btn' in content and 'Sign In' in content and 'Sign Up' in content:
        print("   ✅ Modern toggle form loaded")
    else:
        print("   ❌ Old form still loading")
    
    if 'Check' in content and 'checkAvailability' in content:
        print("   ✅ Check ID button present")
    else:
        print("   ❌ Check ID button missing")
    
    if 'password-strength' in content:
        print("   ✅ Password strength indicator present")
    else:
        print("   ❌ Password strength missing")

# Test 3: Test registration with modern form data
print("\n3. Testing Registration Submission:")
test_data = {
    'full_name': 'Test Student',
    'student_id': 'TEST123',
    'phone_number': '010-1234-5678',
    'password1': 'TestPass123!',
    'password2': 'TestPass123!',
    'username': 'TEST123',
    'first_name': 'Test',
    'last_name': 'Student',
    'grade': '10'
}

response = client.post('/student/register/', test_data, follow=True)
print(f"   Status: {response.status_code}")

# Check if user was created
if User.objects.filter(username='TEST123').exists():
    print("   ✅ User created successfully")
    user = User.objects.get(username='TEST123')
    
    # Check profile
    if hasattr(user, 'primepath_student_profile'):
        profile = user.primepath_student_profile
        print(f"   ✅ Profile created: ID={profile.student_id}, Phone={profile.phone_number}")
        if profile.grade == '10':
            print("   ✅ Grade saved correctly")
    else:
        print("   ❌ Profile not created")
    
    # Clean up
    user.delete()
else:
    print("   ❌ User creation failed")
    if 'errors' in response.context:
        print(f"   Errors: {response.context['errors']}")

# Test 4: Check availability endpoint
print("\n4. Testing Check Availability Endpoint:")
import json
response = client.post('/student/api/check-availability/', 
    json.dumps({'type': 'student_id', 'value': 'NEWID123'}),
    content_type='application/json')

if response.status_code == 200:
    data = json.loads(response.content)
    if data.get('available'):
        print("   ✅ Availability check working")
    else:
        print(f"   ⚠️ ID marked unavailable: {data}")
else:
    print(f"   ❌ Endpoint error: {response.status_code}")

print("\n" + "=" * 60)
print("SUMMARY:")
print("Modern auth form should now be active at:")
print("  http://127.0.0.1:8000/student/login/")
print("  http://127.0.0.1:8000/student/register/")
print("Both URLs use the same template with toggle functionality")
print("=" * 60)
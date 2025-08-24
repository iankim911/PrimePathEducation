#!/usr/bin/env python
"""Test login functionality"""
import os
import sys
import django

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth import authenticate
from django.test import Client

print("Testing login functionality...")
print("=" * 50)

# Test with authenticate function
print("\n1. Testing with Django authenticate():")
user = authenticate(username='teacher1', password='teacher123')
if user:
    print(f"✅ Authentication successful")
    print(f"   User: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Is active: {user.is_active}")
else:
    print("❌ Authentication failed")

# Test with test client
print("\n2. Testing with Django test client:")
client = Client()
response = client.post('/RoutineTest/login/', {
    'username': 'teacher1',
    'password': 'teacher123',
})

print(f"   Response status: {response.status_code}")
if response.status_code == 302:  # Redirect after successful login
    print(f"✅ Login successful (redirecting to: {response.url})")
elif response.status_code == 200:
    print("⚠️  Login page returned (might have errors)")
    # Check if user is authenticated
    response = client.get('/RoutineTest/')
    if response.status_code == 200:
        print("   But can access protected pages - login might be working")
else:
    print(f"❌ Unexpected status code: {response.status_code}")

print("\n" + "=" * 50)
print("Login test complete!")
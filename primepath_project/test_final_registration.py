#!/usr/bin/env python
"""
Test registration with password that passes Django validation
"""
import requests
import time

url = 'http://127.0.0.1:8000/student/register/'
session = requests.Session()

print("=== FINAL REGISTRATION TEST ===")

# Get CSRF token
response = session.get(url)
import re
csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', response.text)
csrf_token = csrf_match.group(1) if csrf_match else 'dummy'

# Use completely different password from student ID
test_data = {
    'first_name': 'Final',
    'last_name': 'TestUser',
    'student_id': 'student789',  # Short and simple
    'phone_number': '01011111111',
    'email': 'finaltest@example.com', 
    'parent1_name': 'Final Parent',
    'parent1_phone': '01022222222',
    'password1': 'ComplexPassword456!',  # Completely different from username
    'password2': 'ComplexPassword456!',
    'csrfmiddlewaretoken': csrf_token
}

print(f"Student ID: {test_data['student_id']}")
print(f"Password: {test_data['password1']}")
print("(Password is completely different from student ID)")

response = session.post(url, data=test_data)
print(f"\nResponse status: {response.status_code}")

if response.status_code == 302:
    location = response.headers.get('Location', 'No location')
    print(f"✅ SUCCESS! Redirected to: {location}")
elif response.status_code == 200:
    if 'Account created successfully' in response.text:
        print("✅ SUCCESS! Account created")
    elif 'UNIQUE constraint failed' in response.text:
        print("❌ UNIQUE constraint error still present")
        if 'auth_user.username' in response.text:
            print("   Username already exists")
        elif 'auth_user.email' in response.text:
            print("   Email already exists")
    else:
        # Look for form errors
        errors = re.findall(r'<ul class="errorlist"[^>]*>(.*?)</ul>', response.text, re.DOTALL)
        if errors:
            print("❌ Form errors found:")
            for error_block in errors:
                items = re.findall(r'<li[^>]*>([^<]+)</li>', error_block)
                for item in items:
                    print(f"   -> {item.strip()}")
        else:
            print("❌ Unknown validation issue")

print("\n=== CHECKING IF USER WAS CREATED ===")
# Test if we can now login with these credentials
login_url = 'http://127.0.0.1:8000/student/login/'
login_response = session.get(login_url)
csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', login_response.text)
login_csrf = csrf_match.group(1) if csrf_match else 'dummy'

login_data = {
    'identifier': test_data['student_id'],
    'password': test_data['password1'], 
    'login_method': 'student_id',
    'csrfmiddlewaretoken': login_csrf
}

login_result = session.post(login_url, data=login_data)
if login_result.status_code == 302:
    print("✅ Can login - user was created successfully!")
else:
    print("❌ Cannot login - user was not created")
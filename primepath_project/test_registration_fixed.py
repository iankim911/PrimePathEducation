#!/usr/bin/env python
"""
Test registration with correct field lengths
"""
import requests
import time

url = 'http://127.0.0.1:8000/student/register/'
session = requests.Session()

print("=== TESTING REGISTRATION WITH CORRECT FIELD LENGTHS ===")

# Get CSRF token
response = session.get(url)
import re
csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', response.text)
csrf_token = csrf_match.group(1) if csrf_match else 'dummy'

# Use shorter student ID (max 20 chars)
short_id = f'test{int(time.time()) % 1000000}'  # Much shorter
short_email = f'test{int(time.time()) % 1000000}@example.com'

test_data = {
    'first_name': 'Test',
    'last_name': 'User',
    'student_id': short_id,  # Short student ID
    'phone_number': '01099999999',
    'email': short_email,
    'parent1_name': 'Test Parent',
    'parent1_phone': '01088888888',
    'password1': 'Test123!',
    'password2': 'Test123!',
    'csrfmiddlewaretoken': csrf_token
}

print(f"Using student_id: {short_id} ({len(short_id)} chars)")
print(f"Using email: {short_email}")

response = session.post(url, data=test_data)
print(f"Response status: {response.status_code}")

if response.status_code == 302:
    print("✅ SUCCESS: Registration successful (redirected)")
    print(f"Redirect location: {response.headers.get('Location', 'No location')}")
elif response.status_code == 200:
    if 'Account created successfully' in response.text:
        print("✅ SUCCESS: Account created")
    elif 'UNIQUE constraint failed' in response.text:
        print("❌ Still getting UNIQUE constraint error")
    else:
        print("❌ Form validation failed")
        # Look for error messages
        errors = re.findall(r'<li[^>]*>([^<]+)</li>', response.text)
        if errors:
            print("Errors found:")
            for error in errors:
                print(f"   -> {error.strip()}")
        else:
            print("No specific errors found in response")

print(f"\nRegistration test completed.")
#!/usr/bin/env python
"""
Test live registration and capture server logs
"""
import requests
import time

url = 'http://127.0.0.1:8000/student/register/'
session = requests.Session()

print("=== TESTING LIVE REGISTRATION WITH NEW DEBUG ===")

# Get CSRF token
response = session.get(url)
import re
csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', response.text)
csrf_token = csrf_match.group(1) if csrf_match else 'dummy'

# Test unique student ID
test_data = {
    'first_name': 'Live',
    'last_name': 'Debug Test',
    'student_id': f'live_debug_{int(time.time())}',  # Unique ID with timestamp
    'phone_number': '01077777777',
    'email': f'live.debug.{int(time.time())}@example.com',  # Unique email
    'parent1_name': 'Debug Parent',
    'parent1_phone': '01088888888',
    'password1': 'LiveDebug123!',
    'password2': 'LiveDebug123!',
    'csrfmiddlewaretoken': csrf_token
}

print(f"Submitting with unique student_id: {test_data['student_id']}")
print(f"Submitting with unique email: {test_data['email']}")

response = session.post(url, data=test_data)
print(f"Response status: {response.status_code}")

if response.status_code == 302:
    print("✅ SUCCESS: Registration redirected (successful)")
    print(f"Redirect location: {response.headers.get('Location', 'No location header')}")
elif 'UNIQUE constraint failed' in response.text:
    print("❌ UNIQUE constraint error still present")
    # Look for the specific constraint that failed
    if 'auth_user.username' in response.text:
        print("   -> Username constraint failed")
    elif 'auth_user.email' in response.text:
        print("   -> Email constraint failed")
elif 'error' in response.text.lower() or 'errorlist' in response.text:
    print("❌ Form validation errors:")
    errors = re.findall(r'<li[^>]*>([^<]+)</li>', response.text)
    for error in errors:
        print(f"   -> {error.strip()}")
else:
    print(f"Response returned form (status 200). Checking for success messages...")
    if 'Account created successfully' in response.text:
        print("✅ Account created successfully")
    else:
        print("❌ Unknown issue - form returned but no clear error")

print(f"\nCheck server console for [REGISTRATION_DEBUG] messages")
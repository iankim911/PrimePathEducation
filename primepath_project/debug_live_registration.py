#!/usr/bin/env python
"""
Debug the actual live registration issue
"""
import requests
import json

# Test the real registration endpoint
url = 'http://127.0.0.1:8000/student/register/'

# Get the form page first to check for CSRF tokens
print("=== TESTING LIVE REGISTRATION ===")
session = requests.Session()

# Get the registration page
try:
    response = session.get(url)
    print(f"GET registration page status: {response.status_code}")
    
    # Look for CSRF token in the HTML
    if 'csrf' in response.text.lower():
        print("✅ CSRF token found in page")
    else:
        print("❌ No CSRF token found")
        
    # Try to extract CSRF token from HTML
    import re
    csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', response.text)
    if csrf_match:
        csrf_token = csrf_match.group(1)
        print(f"CSRF token extracted: {csrf_token[:20]}...")
    else:
        print("Could not extract CSRF token")
        csrf_token = None
        
    # Now test form submission
    test_data = {
        'first_name': 'Live',
        'last_name': 'Test User',
        'student_id': 'live_test_001',
        'phone_number': '01011112222',
        'email': 'live.test@example.com',
        'parent1_name': 'Test Parent',
        'parent1_phone': '01099998888',
        'password1': 'LiveTest123!',
        'password2': 'LiveTest123!'
    }
    
    if csrf_token:
        test_data['csrfmiddlewaretoken'] = csrf_token
    
    print(f"\nSubmitting registration data...")
    post_response = session.post(url, data=test_data)
    print(f"POST response status: {post_response.status_code}")
    
    # Check response content for specific errors
    content = post_response.text
    if 'UNIQUE constraint failed' in content:
        print("❌ UNIQUE constraint error still present!")
    elif 'errorlist' in content:
        print("❌ Form validation errors present")
        # Extract error messages
        error_matches = re.findall(r'<li>([^<]+)</li>', content)
        for error in error_matches:
            print(f"  Error: {error}")
    elif post_response.status_code == 302:
        print("✅ Registration successful (redirected)")
    else:
        print(f"Response content preview: {content[:500]}")
        
except requests.exceptions.ConnectionError:
    print("❌ Could not connect to server. Is it running on 127.0.0.1:8000?")
except Exception as e:
    print(f"❌ Error testing registration: {e}")
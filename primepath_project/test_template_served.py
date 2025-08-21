#!/usr/bin/env python
"""Test what template content is actually being served"""

import requests
from bs4 import BeautifulSoup

# First, we need to login
session = requests.Session()

# Get login page for CSRF token
login_url = "http://127.0.0.1:8000/login/"
login_page = session.get(login_url)
soup = BeautifulSoup(login_page.text, 'html.parser')
csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']

print(f"Got CSRF token: {csrf_token[:20]}...")

# Login
login_data = {
    'username': 'teacher1',
    'password': 'teacher123',
    'csrfmiddlewaretoken': csrf_token
}

login_response = session.post(login_url, data=login_data)
print(f"Login response: {login_response.status_code}")

# Now get the exams page
exams_url = "http://127.0.0.1:8000/RoutineTest/exams/"
exams_response = session.get(exams_url)

print(f"Exams page status: {exams_response.status_code}")
print(f"Exams page size: {len(exams_response.text)} bytes")

# Check for our function
if 'window.openCopyModal' in exams_response.text:
    print("✅ window.openCopyModal FOUND in served HTML!")
    # Count occurrences
    count = exams_response.text.count('window.openCopyModal')
    print(f"   Found {count} occurrences")
else:
    print("❌ window.openCopyModal NOT found in served HTML")

if 'function openCopyModal' in exams_response.text:
    print("✅ function openCopyModal FOUND in served HTML!")
else:
    print("❌ function openCopyModal NOT found in served HTML")

# Check for copy buttons
soup = BeautifulSoup(exams_response.text, 'html.parser')
copy_buttons = soup.find_all('button', class_='btn-copy')
print(f"\nFound {len(copy_buttons)} copy buttons")

if copy_buttons:
    first_button = copy_buttons[0]
    onclick = first_button.get('onclick', '')
    print(f"First button onclick: {onclick[:100]}...")

# Save the served HTML for inspection
with open('/tmp/served_exam_list.html', 'w') as f:
    f.write(exams_response.text)
    print("\nServed HTML saved to /tmp/served_exam_list.html")
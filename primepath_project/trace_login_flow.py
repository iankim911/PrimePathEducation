#!/usr/bin/env python
"""
Trace the complete login flow to see what happens after login
"""

import requests
from bs4 import BeautifulSoup

print("="*80)
print("TRACING COMPLETE LOGIN FLOW")
print("="*80)

session = requests.Session()

# Step 1: GET login page
print("\n1. GET /login/")
print("-"*40)
login_page = session.get("http://127.0.0.1:8000/login/")
print(f"   Status: {login_page.status_code}")
print(f"   URL: {login_page.url}")

soup = BeautifulSoup(login_page.content, 'html.parser')
csrf = soup.find('input', {'name': 'csrfmiddlewaretoken'})
if csrf:
    csrf_token = csrf.get('value')
    print(f"   CSRF Token: {csrf_token[:20]}...")
else:
    print("   No CSRF token found")
    csrf_token = None

# Check for navigation on login page
nav_on_login = len(soup.find_all(class_='nav-tabs')) > 0
print(f"   Navigation present: {'YES ❌' if nav_on_login else 'NO ✅'}")

# Step 2: POST login credentials
print("\n2. POST /login/ (attempting login)")
print("-"*40)
login_data = {
    'username': 'admin',  # Try common username
    'password': 'wrongpassword',  # Wrong password intentionally
    'csrfmiddlewaretoken': csrf_token or 'test'
}

response = session.post("http://127.0.0.1:8000/login/", data=login_data, allow_redirects=False)
print(f"   Status: {response.status_code}")
print(f"   Location header: {response.headers.get('Location', 'None')}")

# Step 3: Follow redirect if any
if response.status_code in [301, 302, 303, 307, 308]:
    print("\n3. Following redirect")
    print("-"*40)
    redirect_url = response.headers.get('Location')
    if not redirect_url.startswith('http'):
        redirect_url = f"http://127.0.0.1:8000{redirect_url}"
    print(f"   Redirecting to: {redirect_url}")
    
    final_response = session.get(redirect_url)
    print(f"   Final status: {final_response.status_code}")
    print(f"   Final URL: {final_response.url}")
    
    # Check final page for navigation
    final_soup = BeautifulSoup(final_response.content, 'html.parser')
    nav_tabs = final_soup.find_all(class_='nav-tabs')
    nav_elements = final_soup.find_all('nav')
    
    print(f"\n   Final page analysis:")
    print(f"   - Nav elements: {len(nav_elements)}")
    print(f"   - Nav-tabs: {len(nav_tabs)}")
    
    # Check what page we're on
    title = final_soup.find('title')
    if title:
        print(f"   - Page title: {title.text}")
    
    # Check for error messages
    messages = final_soup.find_all(class_=['error-message', 'alert-error', 'alert-danger'])
    if messages:
        print(f"   - Error messages found: {len(messages)}")
        for msg in messages:
            print(f"     * {msg.get_text().strip()[:100]}")
else:
    print("\n3. No redirect (staying on login page)")
    print("-"*40)
    # We're still on login page after failed login
    soup = BeautifulSoup(response.content, 'html.parser')
    nav_tabs = soup.find_all(class_='nav-tabs')
    nav_elements = soup.find_all('nav')
    
    print(f"   Nav elements: {len(nav_elements)}")
    print(f"   Nav-tabs: {len(nav_tabs)}")
    
    # Check for error messages
    error_shown = "Invalid username or password" in response.text
    print(f"   Login error shown: {'YES ✅' if error_shown else 'NO ❌'}")

print("\n" + "="*80)
print("DIAGNOSIS:")
print("-"*80)

if nav_on_login:
    print("❌ PROBLEM: Navigation is present on the login page itself")
    print("   The template is not using base_clean.html correctly")
else:
    print("✅ Login page is clean (no navigation)")
    print("\nPossible issues if you see navigation:")
    print("1. Clear browser cache: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)")
    print("2. Try incognito/private mode")
    print("3. Check if you're actually logged in and on a different page")
    print("4. The navigation might appear AFTER successful login (which is correct)")

print("="*80)
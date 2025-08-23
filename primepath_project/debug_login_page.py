#!/usr/bin/env python
"""
Debug what's actually being served at /login/
"""

import requests
from bs4 import BeautifulSoup

url = "http://127.0.0.1:8000/login/"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

print("="*80)
print("LOGIN PAGE ANALYSIS")
print("="*80)

# Check for any nav elements
nav_elements = soup.find_all('nav')
print(f"\n1. Nav elements found: {len(nav_elements)}")
if nav_elements:
    for nav in nav_elements:
        print(f"   - Nav with {len(nav.find_all('a'))} links")
        
# Check for nav-tabs class
nav_tabs = soup.find_all(class_='nav-tabs')
print(f"\n2. Elements with 'nav-tabs' class: {len(nav_tabs)}")
if nav_tabs:
    for tab in nav_tabs:
        links = tab.find_all('a')
        print(f"   - Nav tabs with {len(links)} links:")
        for link in links[:5]:  # Show first 5 links
            print(f"     * {link.get_text().strip()}")

# Check for specific navigation text
nav_texts = ['Dashboard', 'Start Test', 'View Results', 'Upload Exam', 'Manage Exams']
print(f"\n3. Navigation text search:")
for text in nav_texts:
    links = soup.find_all('a', string=lambda s: s and text in s)
    if links:
        print(f"   ❌ Found '{text}': {len(links)} occurrences")
        for link in links:
            print(f"      - href: {link.get('href')}")
    else:
        print(f"   ✅ '{text}' not found")

# Check what's in the header area
print(f"\n4. Header analysis:")
header = soup.find('header')
if header:
    print(f"   - Header found with {len(header.find_all('a'))} links")
else:
    print(f"   - No header element")

# Check for any divs with navigation-like classes
nav_divs = soup.find_all('div', class_=lambda c: c and any(x in c for x in ['nav', 'menu', 'header', 'toolbar']))
print(f"\n5. Divs with navigation-like classes: {len(nav_divs)}")
for div in nav_divs[:3]:  # Show first 3
    print(f"   - Div with class: {div.get('class')}")

# Check the auth-info section (from base_clean)
auth_info = soup.find(class_='auth-info')
print(f"\n6. Auth info section:")
if auth_info:
    print(f"   - Found auth-info with content: {auth_info.get_text().strip()[:100]}")
else:
    print(f"   - No auth-info section (correct for login page)")

# Check form action
form = soup.find('form', id='loginForm')
print(f"\n7. Login form:")
if form:
    print(f"   - Form action: {form.get('action')}")
    print(f"   - Form method: {form.get('method')}")
else:
    print(f"   - No login form found!")

print("\n" + "="*80)
print("CONCLUSION:")
if nav_elements or nav_tabs or any(soup.find_all('a', string=lambda s: s and text in s) for text in nav_texts):
    print("❌ Navigation elements ARE present in the login page")
    print("   The template might not be using base_clean.html correctly")
else:
    print("✅ No navigation elements found in the served HTML")
    print("   The page is clean. If you see navigation, it might be:")
    print("   1. Browser cache issue - Try Cmd+Shift+R (hard refresh)")
    print("   2. Browser extension injecting content")
    print("   3. You might be on a different page after login")
print("="*80)
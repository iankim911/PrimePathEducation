#!/usr/bin/env python3
"""Test what template content is being served"""
import requests
from bs4 import BeautifulSoup

# Try to get the page (will redirect to login)
response = requests.get('http://127.0.0.1:8000/RoutineTest/exams/create/', allow_redirects=False)
print(f"Status: {response.status_code}")

if response.status_code == 302:
    print(f"Redirects to: {response.headers.get('Location')}")
    print("\nThe page requires authentication. Testing template content directly...")
    
    # Load template directly
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
    django.setup()
    
    from django.template.loader import get_template
    
    template = get_template('primepath_routinetest/create_exam.html')
    content = open(template.origin.name, 'r').read()
    
    # Check for Quick Select
    if 'Quick Select' in content:
        print("\n❌ ERROR: 'Quick Select' FOUND in template!")
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'Quick Select' in line:
                print(f"  Line {i}: {line.strip()}")
    else:
        print("\n✅ SUCCESS: 'Quick Select' NOT found in template")
    
    # Check for our marker comment
    if 'QUICK SELECT REMOVED: 2025-08-21' in content:
        print("✅ Marker comment found - template has been updated")
    else:
        print("❌ Marker comment NOT found - template may not be updated")
    
    # Check for button text
    button_texts = ['All Classes', 'Clear All', 'Grade 7', 'Grade 8', 'Grade 9', 'Grade 10']
    for text in button_texts:
        if f'>{text}<' in content:
            print(f"❌ Button text '{text}' found in template")
            
    print(f"\n📁 Template path: {template.origin.name}")
    print(f"📅 File modified: {os.path.getmtime(template.origin.name)}")
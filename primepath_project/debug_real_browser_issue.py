#!/usr/bin/env python
"""
Find exactly why browser shows VIEW ONLY but tests don't
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from bs4 import BeautifulSoup

# Test exactly what browser is requesting
client = Client()
teacher1 = User.objects.get(username='teacher1')
teacher1.set_password('teacher123')
teacher1.save()

# Login
login = client.login(username='teacher1', password='teacher123')
print(f"Logged in: {login}")

# Make the exact request with filter ON
print("\n" + "="*60)
print("MAKING REQUEST: /RoutineTest/exams/?assigned_only=true")
print("="*60)

response = client.get('/RoutineTest/exams/?assigned_only=true')
print(f"Status: {response.status_code}")

# Parse HTML and look for VIEW ONLY badges
soup = BeautifulSoup(response.content, 'html.parser')

# Find all badge spans
badges = soup.find_all('span', class_='badge')
print(f"\nFound {len(badges)} badge elements")

view_only_found = []
for i, badge in enumerate(badges):
    badge_text = badge.get_text().strip()
    print(f"Badge {i+1}: '{badge_text}'")
    
    if 'VIEW' in badge_text.upper():
        view_only_found.append(badge_text)
        
        # Find the parent exam card
        exam_card = badge.find_parent('div', class_='exam-card')
        if exam_card:
            title_elem = exam_card.find('div', class_='exam-title')
            exam_name = title_elem.get_text().strip() if title_elem else 'Unknown'
            print(f"  ❌ VIEW ONLY EXAM: {exam_name}")
            
            # Show the HTML around this badge
            print(f"  HTML snippet: {str(badge)[:100]}...")

print(f"\n❌ TOTAL VIEW ONLY BADGES: {len(view_only_found)}")

if len(view_only_found) > 0:
    print("\n💥 SMOKING GUN: The test client also shows VIEW ONLY badges!")
    print("This means the backend filtering is NOT working.")
    print("The template fix should have hidden these but it's not working either.")
else:
    print("\n✅ Test client shows no VIEW ONLY badges")
    print("This means there's a difference between test client and browser.")

# Check the context variable
if hasattr(response, 'context') and response.context:
    show_assigned = response.context.get('show_assigned_only', False)
    print(f"\nContext show_assigned_only: {show_assigned}")
    if not show_assigned:
        print("❌ BUG: Context should show True but shows False!")
    
    # Check if hierarchical_exams has VIEW ONLY exams
    hierarchical = response.context.get('hierarchical_exams', {})
    total_in_context = 0
    view_only_in_context = 0
    
    for program, classes in hierarchical.items():
        for class_code, exams in classes.items():
            for exam in exams:
                total_in_context += 1
                if hasattr(exam, 'access_badge') and exam.access_badge == 'VIEW ONLY':
                    view_only_in_context += 1
                    print(f"❌ VIEW ONLY IN CONTEXT: {exam.name}")
    
    print(f"\nContext data: {total_in_context} exams, {view_only_in_context} VIEW ONLY")

# Final verdict
print("\n" + "="*60)
if len(view_only_found) > 0:
    print("❌ BACKEND FILTER IS BROKEN")
    print("The filtering logic is not working as expected.")
    print("VIEW ONLY exams are still getting through to the template.")
else:
    print("✅ Backend seems OK - browser issue might be elsewhere")
print("="*60)
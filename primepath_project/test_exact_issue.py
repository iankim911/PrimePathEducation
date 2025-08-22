#!/usr/bin/env python
"""
Test EXACTLY what the user is seeing
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
from primepath_routinetest.models import Exam
from bs4 import BeautifulSoup

# Test as teacher1 (Taehyun Kim)
client = Client()
teacher1 = User.objects.get(username='teacher1')
teacher1.set_password('teacher123')
teacher1.save()

login = client.login(username='teacher1', password='teacher123')
print(f"Logged in as teacher1 (Taehyun Kim): {login}")

# Make the EXACT same request the browser is making
print("\n" + "="*80)
print("MAKING EXACT REQUEST: /RoutineTest/exams/?assigned_only=true")
print("="*80)

response = client.get('/RoutineTest/exams/?assigned_only=true')
print(f"Response status: {response.status_code}")

# Parse the HTML
soup = BeautifulSoup(response.content, 'html.parser')

# Find the checkbox
checkbox = soup.find('input', {'id': 'assignedOnlyFilter'})
if checkbox:
    print(f"\nCheckbox found:")
    print(f"  Checked attribute: {checkbox.get('checked')}")
    
# Find Chung-cho1 section
chung_section = soup.find('div', {'data-class': 'Chung-cho1'})
if chung_section:
    print(f"\nChung-cho1 section found")
    # Look for VIEW ONLY badges in this section
    badges = chung_section.find_all('span', class_='badge')
    print(f"  Badges in Chung-cho1 section: {len(badges)}")
    for badge in badges:
        print(f"    - {badge.get_text(strip=True)}")

# Check for the test exams
test_exam_cards = []
all_cards = soup.find_all('div', class_='exam-card')
for card in all_cards:
    title_elem = card.find('div', class_='exam-title')
    if title_elem and 'Toggle Testing' in title_elem.get_text():
        test_exam_cards.append(card)
        print(f"\nFound test exam: {title_elem.get_text(strip=True)}")
        # Check for VIEW ONLY badge near this card
        parent = card.parent
        if parent:
            badge = parent.find('span', string='VIEW ONLY')
            if badge:
                print(f"  ❌ HAS VIEW ONLY BADGE")
            else:
                print(f"  ✅ No VIEW ONLY badge")

print(f"\nTotal test exam cards found: {len(test_exam_cards)}")

# Check what the template context had
if hasattr(response, 'context'):
    context = response.context
    if context:
        show_assigned = context.get('show_assigned_only')
        print(f"\nContext show_assigned_only: {show_assigned}")
        
        # Check if test exams are in the hierarchical data
        hierarchical = context.get('hierarchical_exams', {})
        for program, classes in hierarchical.items():
            for class_code, exams in classes.items():
                for exam in exams:
                    if 'Toggle Testing' in exam.name:
                        print(f"❌❌❌ TEST EXAM IN CONTEXT: {exam.name}")
                        if hasattr(exam, 'access_badge'):
                            print(f"  Badge: {exam.access_badge}")
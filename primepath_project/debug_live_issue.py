#!/usr/bin/env python
"""
Debug what's ACTUALLY happening when the page loads
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

# Create client and login
client = Client()
teacher1 = User.objects.get(username='teacher1')
teacher1.set_password('teacher123')
teacher1.save()

login = client.login(username='teacher1', password='teacher123')
print(f"Login successful: {login}")

# Make request with filter ON
print("\n" + "="*80)
print("REQUESTING WITH FILTER ON")
print("="*80)

response = client.get('/RoutineTest/exams/?assigned_only=true')
print(f"Response status: {response.status_code}")

# Parse HTML
soup = BeautifulSoup(response.content, 'html.parser')

# Find all VIEW ONLY badges
view_only_badges = soup.find_all('span', string='VIEW ONLY')
print(f"\nFound {len(view_only_badges)} VIEW ONLY badge elements")

# Find exam cards with VIEW ONLY
exam_cards = soup.find_all('div', class_='exam-card')
print(f"Total exam cards: {len(exam_cards)}")

# Check which exams have VIEW ONLY
for card in exam_cards:
    title_elem = card.find('div', class_='exam-title')
    if title_elem:
        title = title_elem.get_text(strip=True)
        # Look for VIEW ONLY badge in this card
        badge = card.find_parent().find('span', string='VIEW ONLY')
        if badge:
            print(f"  ❌ {title} - HAS VIEW ONLY BADGE")
        
# Check context data if available
if hasattr(response, 'context'):
    context = response.context
    if context:
        show_assigned = context.get('show_assigned_only')
        hierarchical_exams = context.get('hierarchical_exams', {})
        
        print(f"\nContext data:")
        print(f"  show_assigned_only: {show_assigned}")
        
        # Count VIEW ONLY in context
        view_only_count = 0
        total_count = 0
        for program in hierarchical_exams.values():
            for class_exams in program.values():
                for exam in class_exams:
                    total_count += 1
                    if hasattr(exam, 'access_badge') and exam.access_badge == 'VIEW ONLY':
                        view_only_count += 1
                        print(f"    ❌ Context has VIEW ONLY: {exam.name}")
        
        print(f"  Total exams in context: {total_count}")
        print(f"  VIEW ONLY in context: {view_only_count}")
#!/usr/bin/env python
"""
Debug exactly what badge elements are being rendered
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
import re
from bs4 import BeautifulSoup

def debug_actual_badges():
    """Debug actual badge HTML elements only"""
    
    print("🔍 DEBUGGING ACTUAL BADGE ELEMENTS")
    print("="*60)
    
    # Set up test client
    client = Client()
    teacher1 = User.objects.get(username='teacher1')
    teacher1.set_password('teacher123')
    teacher1.save()
    
    login = client.login(username='teacher1', password='teacher123')
    print(f"✅ Logged in as teacher1: {login}")
    
    def analyze_badges(response, test_name):
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find all badge elements
            badge_elements = soup.find_all('span', class_='badge')
            
            print(f"\n{test_name}")
            print(f"Status: {response.status_code}")
            print(f"Total badge elements found: {len(badge_elements)}")
            
            view_only_badges = 0
            all_badges = {}
            
            for badge in badge_elements:
                badge_text = badge.get_text().strip()
                all_badges[badge_text] = all_badges.get(badge_text, 0) + 1
                
                if 'VIEW' in badge_text.upper():
                    view_only_badges += 1
                    print(f"   🚨 VIEW badge found: '{badge_text}'")
            
            print(f"VIEW ONLY badge elements: {view_only_badges}")
            print(f"All badge types: {all_badges}")
            
            # Also check for raw text occurrences (for comparison)
            raw_view_only = len(re.findall(r'VIEW\s*ONLY', content))
            print(f"Raw 'VIEW ONLY' text occurrences: {raw_view_only}")
            
            return view_only_badges
        else:
            print(f"❌ Error: Status {response.status_code}")
            return 0
    
    # Test filter OFF
    response_off = client.get('/RoutineTest/exams/')
    badges_off = analyze_badges(response_off, "1️⃣ FILTER OFF")
    
    # Test filter ON
    response_on = client.get('/RoutineTest/exams/?assigned_only=true')
    badges_on = analyze_badges(response_on, "2️⃣ FILTER ON")
    
    print("\n" + "="*60)
    print("📊 FINAL SUMMARY")
    print("="*60)
    print(f"Filter OFF: {badges_off} VIEW ONLY badge elements")
    print(f"Filter ON:  {badges_on} VIEW ONLY badge elements")
    
    if badges_on == 0:
        print("✅ FILTER WORKING - No VIEW ONLY badge elements when filter is on!")
    else:
        print("❌ FILTER NOT WORKING - Still showing VIEW ONLY badge elements")

if __name__ == "__main__":
    debug_actual_badges()
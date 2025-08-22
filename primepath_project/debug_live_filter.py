#!/usr/bin/env python
"""
Live debugging tool - checks what's actually happening when user toggles filter
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

def test_filter_with_logged_user():
    """Test the filter behavior with actual logged-in user"""
    client = Client()
    
    # Log in as teacher1
    teacher1 = User.objects.get(username='teacher1')
    teacher1.set_password('teacher123')
    teacher1.save()
    
    login = client.login(username='teacher1', password='teacher123')
    print(f"✅ Logged in as teacher1: {login}")
    
    print("\n" + "="*80)
    print("🔍 TESTING FILTER BEHAVIOR")
    print("="*80)
    
    # Test 1: Filter OFF
    print("\n1️⃣ TESTING FILTER OFF")
    response_off = client.get('/RoutineTest/exams/')
    print(f"   URL: /RoutineTest/exams/")
    print(f"   Status: {response_off.status_code}")
    
    content_off = response_off.content.decode('utf-8')
    view_only_badges_off = len(re.findall(r'VIEW\s*ONLY', content_off))
    print(f"   VIEW ONLY badges found: {view_only_badges_off}")
    
    # Test 2: Filter ON
    print("\n2️⃣ TESTING FILTER ON")
    response_on = client.get('/RoutineTest/exams/?assigned_only=true')
    print(f"   URL: /RoutineTest/exams/?assigned_only=true")
    print(f"   Status: {response_on.status_code}")
    
    content_on = response_on.content.decode('utf-8')
    view_only_badges_on = len(re.findall(r'VIEW\s*ONLY', content_on))
    print(f"   VIEW ONLY badges found: {view_only_badges_on}")
    
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    print(f"Filter OFF: {view_only_badges_off} VIEW ONLY badges")
    print(f"Filter ON:  {view_only_badges_on} VIEW ONLY badges")
    
    if view_only_badges_on == 0:
        print("✅ FILTER WORKING CORRECTLY")
    else:
        print("❌ FILTER NOT WORKING - STILL SHOWING VIEW ONLY BADGES")
        
        # Check if our template fix comment is present
        if 'CRITICAL FIX: Never show VIEW ONLY badge when filter is active' in content_on:
            print("✅ Our template fix comment IS present")
        else:
            print("❌ Our template fix comment is MISSING")
            
        # Check if our JavaScript safety net is present
        if 'NUCLEAR_SAFETY' in content_on:
            print("✅ Our JavaScript safety net IS present")
        else:
            print("❌ Our JavaScript safety net is MISSING")
            
        # Look for the actual VIEW ONLY text
        view_only_matches = re.finditer(r'VIEW\s*ONLY', content_on)
        print(f"\n🔍 Found VIEW ONLY text at these positions:")
        for i, match in enumerate(view_only_matches):
            start = max(0, match.start() - 100)
            end = min(len(content_on), match.end() + 100)
            context = content_on[start:end].replace('\n', ' ').replace('  ', ' ')
            print(f"   {i+1}. ...{context}...")

if __name__ == "__main__":
    test_filter_with_logged_user()
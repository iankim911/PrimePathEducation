#!/usr/bin/env python
"""
Debug script to understand navigation rendering issue
"""
import os
import sys
import django
from pathlib import Path
import json
import traceback
from datetime import datetime

# Setup Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import Teacher
from bs4 import BeautifulSoup


def analyze_navigation():
    """Analyze what navigation is being rendered"""
    print("\n" + "="*80)
    print("NAVIGATION RENDERING ANALYSIS")
    print("="*80)
    print(f"Time: {datetime.now()}")
    
    # Create client and login
    client = Client()
    
    # Try to get admin user
    admin_user = User.objects.filter(username='admin').first()
    if admin_user:
        client.force_login(admin_user)
        print(f"✅ Logged in as: {admin_user.username}")
    else:
        print("⚠️ No admin user found, testing as anonymous")
    
    # Test different pages
    test_urls = [
        '/RoutineTest/',
        '/RoutineTest/classes-exams/',
        '/RoutineTest/create-exam/',
    ]
    
    for url in test_urls:
        print(f"\n📋 Testing URL: {url}")
        print("-" * 40)
        
        try:
            response = client.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find navigation
                nav = soup.find('nav', class_='nav-tabs')
                if not nav:
                    nav = soup.find('nav')
                
                if nav:
                    print(f"✅ Navigation found")
                    
                    # Get navigation ID and version
                    nav_id = nav.get('id', 'No ID')
                    nav_version = nav.get('data-version', 'No version')
                    print(f"   Navigation ID: {nav_id}")
                    print(f"   Navigation Version: {nav_version}")
                    
                    # Get all tabs
                    tabs = nav.find_all('a')
                    navigation_items = []
                    
                    print(f"\n   Found {len(tabs)} navigation items:")
                    for i, tab in enumerate(tabs, 1):
                        text = tab.text.strip()
                        href = tab.get('href', '')
                        data_nav = tab.get('data-nav', '')
                        classes = tab.get('class', [])
                        
                        # Skip user/logout tabs
                        if '👤' in text or text in ['Logout', 'Login']:
                            continue
                        
                        print(f"   {i}. {text}")
                        print(f"      - URL: {href}")
                        print(f"      - data-nav: {data_nav}")
                        print(f"      - classes: {classes}")
                        
                        # Check for problematic tabs
                        if 'My Classes' in text and 'Access' in text:
                            print(f"      ❌ OLD TAB FOUND: My Classes & Access")
                        elif 'Exam Assignments' in text:
                            print(f"      ❌ OLD TAB FOUND: Exam Assignments")
                        elif 'Classes & Exams' in text:
                            print(f"      ✅ NEW UNIFIED TAB FOUND")
                        
                        navigation_items.append({
                            'text': text,
                            'href': href,
                            'data_nav': data_nav
                        })
                    
                    # Check template source
                    print(f"\n   Checking template source...")
                    
                    # Look for template comments
                    html_str = str(response.content)
                    if 'VERSION 7.0' in html_str:
                        print("   ✅ Found VERSION 7.0 in HTML")
                    if 'UNIFIED FINAL' in html_str:
                        print("   ✅ Found UNIFIED FINAL in HTML")
                    if 'navigation_tabs.html' in html_str:
                        print("   📄 Using navigation_tabs.html include")
                    if 'render_routinetest_navigation' in html_str:
                        print("   📄 Using render_routinetest_navigation template tag")
                    
                    # Check JavaScript
                    scripts = soup.find_all('script')
                    for script in scripts:
                        if script.string and 'NAV_V7' in script.string:
                            print("   ✅ Found NAV_V7 JavaScript")
                            break
                    
                else:
                    print(f"❌ No navigation found in HTML")
                    
            else:
                print(f"❌ Page returned status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing {url}: {e}")
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    
    # Check template files directly
    print("\n📁 Checking template files...")
    
    template_path = Path('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/templates/primepath_routinetest/includes/navigation_tabs.html')
    if template_path.exists():
        with open(template_path, 'r') as f:
            content = f.read()
            if 'My Classes & Access' in content:
                print("❌ Template file contains 'My Classes & Access'")
            elif 'Classes & Exams' in content:
                print("✅ Template file contains 'Classes & Exams'")
            else:
                print("⚠️ Template file doesn't contain either")
    
    # Check if template cache exists
    cache_dir = Path('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/cache')
    if cache_dir.exists():
        print(f"⚠️ Cache directory exists at {cache_dir}")
        print("   Consider clearing: rm -rf cache/*")
    
    return True


if __name__ == '__main__':
    analyze_navigation()
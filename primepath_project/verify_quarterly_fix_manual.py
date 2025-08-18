#!/usr/bin/env python
"""
Manual verification of quarterly table fix
Simulates what a real user would see
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from core.models import Teacher, School
from primepath_routinetest.models import TeacherClassAssignment
from bs4 import BeautifulSoup

User = get_user_model()

def verify_quarterly_fix():
    """Manually verify the quarterly table fix"""
    print("\n" + "="*70)
    print("MANUAL VERIFICATION: Quarterly Table Fix")
    print("="*70)
    
    # Setup test client
    client = Client()
    
    # Create test user and teacher with class assignments
    user = User.objects.filter(username="testteacher").first()
    if not user:
        user = User.objects.create_user(
            username="testteacher",
            email="teacher@test.com", 
            password="testpass123"
        )
    
    teacher = Teacher.objects.filter(user=user).first()
    if not teacher:
        teacher = Teacher.objects.create(
            user=user,
            name="Test Teacher",
            email="teacher@test.com"
        )
    
    # Create class assignment so we don't get redirected
    assignment = TeacherClassAssignment.objects.filter(
        teacher=teacher,
        class_code='8A'
    ).first()
    
    if not assignment:
        assignment = TeacherClassAssignment.objects.create(
            teacher=teacher,
            class_code='8A',
            access_level='FULL',
            is_active=True
        )
        print("✓ Created test class assignment for teacher")
    
    # Login
    client.login(username="testteacher", password="testpass123")
    print("✓ Logged in as testteacher")
    
    # Get the page
    response = client.get('/RoutineTest/schedule-matrix/')
    print(f"✓ Got response: Status {response.status_code}")
    
    if response.status_code == 302:
        print(f"  Redirected to: {response.url}")
        # Follow redirect
        response = client.get(response.url)
        print(f"  After redirect: Status {response.status_code}")
    
    if response.status_code == 200:
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("\n" + "-"*50)
        print("CHECKING TAB STRUCTURE:")
        print("-"*50)
        
        # Check for tab panels
        monthly_panel = soup.find('div', id='monthly-panel')
        quarterly_panel = soup.find('div', id='quarterly-panel')
        
        if monthly_panel:
            print("✅ Monthly panel found")
            print(f"   Classes: {' '.join(monthly_panel.get('class', []))}")
            print(f"   Display: {'block' if 'active' in monthly_panel.get('class', []) else 'none'}")
        else:
            print("❌ Monthly panel NOT found")
        
        if quarterly_panel:
            print("✅ Quarterly panel found")
            print(f"   Classes: {' '.join(quarterly_panel.get('class', []))}")
            print(f"   Display: {'block' if 'active' in quarterly_panel.get('class', []) else 'none'}")
        else:
            print("❌ Quarterly panel NOT found")
        
        print("\n" + "-"*50)
        print("CHECKING FOR DUPLICATE TABLES:")
        print("-"*50)
        
        # Find all tables
        all_tables = soup.find_all('table', class_='matrix-table')
        print(f"Total tables found: {len(all_tables)}")
        
        # Check each table's location
        for i, table in enumerate(all_tables):
            # Find parent containers
            parent = table.parent
            container_path = []
            
            while parent:
                if parent.get('id'):
                    container_path.append(f"#{parent.get('id')}")
                elif parent.get('class'):
                    container_path.append(f".{parent.get('class')[0] if parent.get('class') else 'unknown'}")
                
                if parent.get('id') in ['monthly-panel', 'quarterly-panel']:
                    break
                    
                parent = parent.parent
            
            print(f"\nTable {i+1}:")
            print(f"  Location: {' > '.join(reversed(container_path[-5:]))}")
            
            # Check if it's a quarterly table
            headers = table.find_all('th')
            header_text = ' '.join([th.get_text() for th in headers])
            if 'Q1' in header_text or 'Quarter' in header_text:
                print(f"  Type: QUARTERLY TABLE")
                if 'quarterly-panel' in str(container_path):
                    print(f"  ✅ Correctly inside quarterly panel")
                else:
                    print(f"  ❌ ERROR: Outside quarterly panel!")
            else:
                print(f"  Type: Monthly table")
        
        # Check for tables outside tab container
        tab_container = soup.find('div', class_='tab-container')
        if tab_container:
            # Check siblings
            siblings_after = tab_container.find_next_siblings()
            tables_after = []
            
            for sibling in siblings_after:
                if sibling.name == 'table':
                    tables_after.append(sibling)
                elif sibling.name == 'div' and sibling.find('table'):
                    tables_after.append(sibling)
            
            if tables_after:
                print(f"\n❌ ISSUE: Found {len(tables_after)} table(s) AFTER tab container!")
                print("   This is the quarterly table bug!")
            else:
                print("\n✅ No tables found after tab container")
        
        print("\n" + "-"*50)
        print("CHECKING RESOURCES:")
        print("-"*50)
        
        # Check CSS
        css_links = soup.find_all('link', rel='stylesheet')
        css_found = False
        for link in css_links:
            if 'schedule-matrix.css' in link.get('href', ''):
                css_found = True
                print(f"✅ CSS loaded: {link.get('href')}")
                break
        if not css_found:
            print("❌ schedule-matrix.css NOT loaded")
        
        # Check JS
        js_scripts = soup.find_all('script', src=True)
        js_found = False
        for script in js_scripts:
            if 'schedule-matrix.js' in script.get('src', ''):
                js_found = True
                print(f"✅ JS loaded: {script.get('src')}")
                break
        if not js_found:
            print("❌ schedule-matrix.js NOT loaded")
        
        print("\n" + "="*70)
        print("VERIFICATION COMPLETE")
        print("="*70)
        
        # Final verdict
        issues = []
        if not monthly_panel:
            issues.append("Monthly panel missing")
        if not quarterly_panel:
            issues.append("Quarterly panel missing")
        if tables_after:
            issues.append("Tables found outside tab container")
        if not css_found:
            issues.append("CSS not loaded")
        if not js_found:
            issues.append("JS not loaded")
        
        if issues:
            print(f"❌ ISSUES FOUND: {', '.join(issues)}")
        else:
            print("✅ ALL CHECKS PASSED - Quarterly table issue appears FIXED!")
            
    else:
        print(f"❌ Could not load page - Status {response.status_code}")
    
    # Cleanup
    if assignment:
        assignment.delete()
        print("\n✓ Cleaned up test data")

if __name__ == "__main__":
    verify_quarterly_fix()
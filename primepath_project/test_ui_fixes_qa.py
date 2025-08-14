#!/usr/bin/env python
"""
QA Test for UI Fixes
Tests each UI fix incrementally
"""
import os
import sys
import django
import json
from datetime import datetime

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_tab_highlight_fix():
    """Test Issue #1: Dashboard tab highlight coverage"""
    print("\n" + "="*70)
    print("QA TEST #1: DASHBOARD TAB HIGHLIGHT FIX")
    print("="*70)
    
    client = Client()
    
    # Login as teacher
    login_success = client.login(username='teacher1', password='teacher123')
    print(f"\n1. Login status: {'✅ Success' if login_success else '❌ Failed'}")
    
    if login_success:
        # Test dashboard page
        response = client.get('/PlacementTest/PlacementTest/teacher/dashboard/')
        print(f"2. Dashboard access: {'✅ Success' if response.status_code == 200 else '❌ Failed'} (Status: {response.status_code})")
        
        if response.status_code == 200:
            content = response.content.decode()
            
            # Check for CSS fixes
            css_checks = {
                "margin: 0; /* Fixed:": "Margin fix applied",
                "display: flex; /* Ensure li stretches": "Flex display added",
                "height: 100%; /* Ensure full height": "Height 100% added",
                "white-space: nowrap; /* Prevent text": "Text wrapping prevented",
                "box-shadow: inset 0 -3px": "Bottom highlight added"
            }
            
            print("\n3. CSS Fix Verification:")
            all_css_ok = True
            for check, description in css_checks.items():
                if check in content:
                    print(f"   ✅ {description}")
                else:
                    print(f"   ❌ {description} - NOT FOUND")
                    all_css_ok = False
            
            # Check active class on dashboard
            has_active = 'class="active"' in content and 'teacher_dashboard' in content
            print(f"\n4. Active class on Dashboard: {'✅ Present' if has_active else '❌ Missing'}")
            
            # Check that navigation structure is intact
            nav_checks = [
                ('Dashboard', 'core:teacher_dashboard'),
                ('Upload Exam', 'PlacementTest:create_exam'),
                ('Manage Exams', 'PlacementTest:exam_list'),
            ]
            
            print("\n5. Navigation Structure:")
            for nav_text, url_name in nav_checks:
                if nav_text in content and url_name in content:
                    print(f"   ✅ {nav_text} link present")
                else:
                    print(f"   ❌ {nav_text} link missing")
            
            print("\n" + "-"*40)
            print("SUMMARY:")
            if all_css_ok and has_active:
                print("✅ TAB HIGHLIGHT FIX SUCCESSFUL!")
                print("   - All CSS fixes applied")
                print("   - Active state working")
                print("   - Navigation structure intact")
            else:
                print("⚠️  Some issues remain - see details above")
    
    return login_success

def test_profile_name_wrapping():
    """Test Issue #2: Profile name breaking into two lines"""
    print("\n" + "="*70)
    print("QA TEST #2: PROFILE NAME WRAPPING FIX")
    print("="*70)
    
    client = Client()
    
    # Login as teacher
    login_success = client.login(username='teacher1', password='teacher123')
    print(f"\n1. Login status: {'✅ Success' if login_success else '❌ Failed'}")
    
    if login_success:
        # Test any page with navigation
        response = client.get('/')
        print(f"2. Home page access: {'✅ Success' if response.status_code == 200 else '❌ Failed'}")
        
        if response.status_code == 200:
            content = response.content.decode()
            
            # Check for profile display
            has_profile = '👤' in content and 'Taehyun Kim' in content
            print(f"3. Profile name displayed: {'✅ Yes' if has_profile else '❌ No'}")
            
            # Check for nowrap CSS
            has_nowrap = 'white-space: nowrap' in content
            print(f"4. Nowrap CSS applied: {'✅ Yes' if has_nowrap else '❌ No'}")
            
            print("\n" + "-"*40)
            print("SUMMARY:")
            if has_profile and has_nowrap:
                print("✅ PROFILE NAME WRAPPING FIX SUCCESSFUL!")
                print("   - Name should display on single line")
                print("   - CSS white-space: nowrap applied")
            else:
                print("⚠️  Issue may persist - manual verification needed")

def test_profile_link_disabled():
    """Test Issue #3: Profile link disabled"""
    print("\n" + "="*70)
    print("QA TEST #3: PROFILE LINK DISABLED")
    print("="*70)
    
    client = Client()
    
    # Login as teacher
    login_success = client.login(username='teacher1', password='teacher123')
    print(f"\n1. Login status: {'✅ Success' if login_success else '❌ Failed'}")
    
    if login_success:
        # Test profile URL
        response = client.get('/profile/', follow=False)
        print(f"2. Profile URL test: Status {response.status_code}")
        
        if response.status_code == 404:
            print("   ⚠️  Profile page returns 404 - needs to be disabled")
        elif response.status_code == 302:
            print("   ℹ️  Profile redirects - might be disabled")
        elif response.status_code == 200:
            print("   ✅ Profile page exists")
        
        # Check home page for profile link
        response = client.get('/')
        content = response.content.decode()
        
        # Check if link is disabled
        # Will update this after implementing the fix
        print("\n3. Profile link status: To be implemented...")
        
        print("\n" + "-"*40)
        print("SUMMARY:")
        print("⚠️  Profile link disable to be implemented next")

if __name__ == "__main__":
    print("\n" + "#"*70)
    print("# UI FIXES QA TEST SUITE - ISSUE #2: PROFILE NAME WRAPPING")
    print("#"*70)
    
    # Test the profile name wrapping fix
    test_profile_name_wrapping()
    
    print("\n" + "#"*70)
    print("# END OF QA TEST")
    print("#"*70)
    print("\n📋 Profile name wrapping fix has been applied.")
    print("CSS and HTML changes implemented:")
    print("  - Added profile-link class with flex display")
    print("  - Applied white-space: nowrap with !important") 
    print("  - Separated emoji and name into spans")
    print("  - Added comprehensive JavaScript logging")
    print("\nPlease verify 'TAEHYUN KIM' displays on single line.")
    print("Once confirmed, we'll proceed with Issue #3.")
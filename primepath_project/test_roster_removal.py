#!/usr/bin/env python
"""
Test script to verify complete removal of Roster functionality from RoutineTest
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Teacher
from primepath_routinetest.models import Exam
from bs4 import BeautifulSoup
import json

def run_tests():
    """Run comprehensive Roster removal tests"""
    print("\n" + "="*70)
    print("ROSTER REMOVAL VERIFICATION TEST")
    print("="*70)
    
    # Initialize client
    client = Client()
    
    # Create admin user and login
    admin_user = User.objects.filter(username='admin').first()
    if not admin_user:
        admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
    
    # Ensure Teacher profile exists
    teacher, _ = Teacher.objects.get_or_create(
        user=admin_user,
        defaults={
            'name': admin_user.username,
            'email': admin_user.email,
            'is_head_teacher': True
        }
    )
    
    client.login(username='admin', password='admin123')
    
    print("\n✅ Admin user logged in")
    
    # Test 1: Check exam list template
    print("\n📋 TEST 1: Checking exam list page...")
    response = client.get(reverse('RoutineTest:exam_list'))
    
    if response.status_code == 200:
        print("   ✅ Exam list page loaded successfully")
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check for Roster button
        roster_found = False
        all_buttons = soup.find_all(['button', 'a'])
        
        for button in all_buttons:
            if 'Roster' in button.get_text():
                roster_found = True
                print(f"   ❌ FOUND ROSTER BUTTON: {button.get_text().strip()}")
                print(f"      HTML: {str(button)[:100]}...")
        
        if not roster_found:
            print("   ✅ No Roster buttons found in HTML")
        
        # Check for roster URLs
        roster_links = soup.find_all(href=lambda x: x and 'roster' in x.lower())
        if roster_links:
            print(f"   ❌ Found {len(roster_links)} roster-related links")
            for link in roster_links[:3]:
                print(f"      - {link.get('href')}")
        else:
            print("   ✅ No roster-related URLs found")
        
        # Check for template version marker
        version_marker = soup.find(attrs={'data-template-version': True})
        if version_marker:
            version = version_marker.get('data-template-version')
            if '2.0-no-roster' in version:
                print(f"   ✅ Template version marker found: {version}")
            else:
                print(f"   ⚠️ Template version marker found but unexpected: {version}")
        else:
            print("   ⚠️ No template version marker found")
        
        # Check for warning banner
        warning_banner = soup.find(string=lambda text: 'ROSTER BUTTON REMOVED' in text if text else False)
        if warning_banner:
            print("   ✅ Template warning banner present")
        else:
            print("   ⚠️ Template warning banner not found")
            
    else:
        print(f"   ❌ Failed to load exam list page: {response.status_code}")
    
    # Test 2: Check URL patterns
    print("\n📋 TEST 2: Checking URL patterns...")
    from django.urls import get_resolver
    from primepath_routinetest import urls as rt_urls
    
    url_patterns = []
    for pattern in rt_urls.urlpatterns:
        if hasattr(pattern, 'name'):
            url_patterns.append(pattern.name)
    
    roster_urls = [name for name in url_patterns if name and 'roster' in name.lower()]
    if roster_urls:
        print(f"   ❌ Found {len(roster_urls)} roster-related URL patterns:")
        for url in roster_urls:
            print(f"      - {url}")
    else:
        print("   ✅ No roster-related URL patterns found")
    
    # Test 3: Check exam model for roster references
    print("\n📋 TEST 3: Checking Exam model...")
    exam_attrs = dir(Exam)
    roster_attrs = [attr for attr in exam_attrs if 'roster' in attr.lower()]
    
    if roster_attrs:
        print(f"   ⚠️ Found {len(roster_attrs)} roster-related attributes/methods in Exam model:")
        for attr in roster_attrs:
            print(f"      - {attr}")
        print("   Note: Model methods still exist but should not be used in views/templates")
    else:
        print("   ✅ No roster-related attributes in Exam model")
    
    # Test 4: Check view for roster references
    print("\n📋 TEST 4: Checking exam_list view...")
    import primepath_routinetest.views.exam as exam_views
    import inspect
    
    exam_list_source = inspect.getsource(exam_views.exam_list)
    
    if 'roster' in exam_list_source.lower():
        # Count occurrences
        roster_count = exam_list_source.lower().count('roster')
        print(f"   ⚠️ Found {roster_count} references to 'roster' in exam_list view")
        
        # Check if it's just in comments
        lines = exam_list_source.split('\n')
        code_refs = 0
        for line in lines:
            if 'roster' in line.lower() and not line.strip().startswith('#'):
                code_refs += 1
        
        if code_refs == 0:
            print("   ✅ All roster references are in comments only")
        else:
            print(f"   ❌ Found {code_refs} roster references in actual code")
    else:
        print("   ✅ No roster references in exam_list view")
    
    # Test 5: Check for prefetch_related references
    if 'student_roster' in exam_list_source:
        print("   ❌ View still prefetches 'student_roster'")
    else:
        print("   ✅ View does not prefetch 'student_roster'")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    issues = []
    if roster_found:
        issues.append("Roster button still visible in HTML")
    if roster_links:
        issues.append("Roster URLs still present in HTML")
    if roster_urls:
        issues.append("Roster URL patterns still registered")
    if 'student_roster' in exam_list_source:
        issues.append("View still prefetches student_roster")
    
    if issues:
        print("❌ ISSUES FOUND:")
        for issue in issues:
            print(f"   - {issue}")
        print("\nACTION REQUIRED:")
        print("1. Clear browser cache completely")
        print("2. Restart Django development server")
        print("3. Check for template caching or overrides")
        print("4. Verify no custom JavaScript is adding buttons")
    else:
        print("✅ ALL CHECKS PASSED - Roster completely removed!")
        print("\nIf you still see the Roster button:")
        print("1. Clear browser cache (Ctrl+Shift+Delete)")
        print("2. Try incognito/private browsing mode")
        print("3. Restart the Django server")
        print("4. Check browser console for the diagnostic messages")
    
    print("\n" + "="*70)

if __name__ == '__main__':
    try:
        run_tests()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
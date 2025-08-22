#!/usr/bin/env python
"""
Debug script to check the actual HTTP response from the server
to see if the issue is with browser caching or server-side.
"""
import os
import sys
import django

# Add the project path to sys.path
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
import re

def test_actual_browser_response():
    """Simulate an actual browser request to see what HTML is returned"""
    print("="*80)
    print("BROWSER RESPONSE DEBUG - SIMULATING ACTUAL HTTP REQUEST")
    print("="*80)
    
    # Get teacher1 user
    try:
        user = User.objects.get(username='teacher1')
        print(f"✅ Testing with user: {user.username}")
    except User.DoesNotExist:
        print("❌ Teacher1 user not found!")
        return
    
    # Create test client
    client = Client()
    
    # Log in as teacher1
    client.force_login(user)
    print("✅ Logged in as teacher1")
    print()
    
    # Test 1: Filter OFF (show all)
    print("🔍 TEST 1: Filter OFF (Show All Exams)")
    print("-" * 50)
    
    response_all = client.get('/RoutineTest/exams/', follow=True)
    print(f"Status Code: {response_all.status_code}")
    print(f"Cache-Control: {response_all.get('Cache-Control', 'Not Set')}")
    print(f"Pragma: {response_all.get('Pragma', 'Not Set')}")
    print(f"Expires: {response_all.get('Expires', 'Not Set')}")
    
    # Count VIEW ONLY badges in HTML
    html_all = response_all.content.decode('utf-8')
    view_only_count_all = html_all.count('VIEW ONLY')
    owner_count_all = html_all.count('>OWNER<')
    full_access_count_all = html_all.count('FULL ACCESS')
    edit_count_all = html_all.count('>EDIT<')
    
    print(f"VIEW ONLY badges in HTML: {view_only_count_all}")
    print(f"OWNER badges in HTML: {owner_count_all}")
    print(f"FULL ACCESS badges in HTML: {full_access_count_all}")
    print(f"EDIT badges in HTML: {edit_count_all}")
    print()
    
    # Test 2: Filter ON (assigned only)
    print("🔍 TEST 2: Filter ON (Show Assigned Classes Only)")
    print("-" * 50)
    
    response_filtered = client.get('/RoutineTest/exams/?assigned_only=true', follow=True)
    print(f"Status Code: {response_filtered.status_code}")
    print(f"Cache-Control: {response_filtered.get('Cache-Control', 'Not Set')}")
    print(f"Pragma: {response_filtered.get('Pragma', 'Not Set')}")
    print(f"Expires: {response_filtered.get('Expires', 'Not Set')}")
    
    # Count VIEW ONLY badges in HTML
    html_filtered = response_filtered.content.decode('utf-8')
    view_only_count_filtered = html_filtered.count('VIEW ONLY')
    owner_count_filtered = html_filtered.count('>OWNER<')
    full_access_count_filtered = html_filtered.count('FULL ACCESS')
    edit_count_filtered = html_filtered.count('>EDIT<')
    
    print(f"VIEW ONLY badges in HTML: {view_only_count_filtered}")
    print(f"OWNER badges in HTML: {owner_count_filtered}")
    print(f"FULL ACCESS badges in HTML: {full_access_count_filtered}")
    print(f"EDIT badges in HTML: {edit_count_filtered}")
    print()
    
    # Analysis
    print("="*80)
    print("ANALYSIS")
    print("="*80)
    
    if view_only_count_filtered > 0:
        print("❌ PROBLEM CONFIRMED!")
        print(f"   Server is returning HTML with {view_only_count_filtered} VIEW ONLY badges")
        print("   when filter is ON. This should be 0.")
        print()
        
        # Find the actual exam names with VIEW ONLY
        view_only_pattern = r'<span class="exam-title"[^>]*>([^<]+)</span>.*?<span class="access-badge[^"]*"[^>]*>VIEW ONLY</span>'
        matches = re.findall(view_only_pattern, html_filtered, re.DOTALL)
        if matches:
            print("VIEW ONLY exams found in filtered response:")
            for exam_name in matches:
                print(f"   - {exam_name.strip()}")
        print()
        print("This indicates the problem is in the backend filtering logic,")
        print("not browser caching or client-side JavaScript.")
        
    elif view_only_count_filtered == 0 and view_only_count_all > 0:
        print("✅ SERVER RESPONSE IS CORRECT!")
        print(f"   Filter OFF: {view_only_count_all} VIEW ONLY badges")
        print(f"   Filter ON: {view_only_count_filtered} VIEW ONLY badges")
        print()
        print("The server is correctly filtering. The issue must be:")
        print("1. Browser cache (try incognito/hard refresh)")
        print("2. JavaScript modifying the DOM after page load")
        print("3. Browser showing cached version instead of fresh response")
        print("4. Network issues (proxy, CDN, etc.)")
        
    else:
        print("⚠️ UNEXPECTED RESULT")
        print(f"   Filter OFF VIEW ONLY count: {view_only_count_all}")
        print(f"   Filter ON VIEW ONLY count: {view_only_count_filtered}")
        print()
    
    # Check checkbox state in HTML
    print("CHECKBOX STATE CHECK:")
    print("-" * 30)
    checkbox_checked_all = 'id="assignedOnlyFilter" checked' in html_all
    checkbox_checked_filtered = 'id="assignedOnlyFilter" checked' in html_filtered
    print(f"Filter OFF - Checkbox checked: {checkbox_checked_all}")
    print(f"Filter ON - Checkbox checked: {checkbox_checked_filtered}")
    print()
    
    # Check URL parameters being processed
    print("TEMPLATE CONTEXT CHECK:")
    print("-" * 30)
    show_assigned_only_all = 'show_assigned_only: false' in html_all or 'show_assigned_only: False' in html_all
    show_assigned_only_filtered = 'show_assigned_only: true' in html_filtered or 'show_assigned_only: True' in html_filtered
    print(f"Filter OFF - show_assigned_only: {not show_assigned_only_all}")  # Inverted because we're checking for false
    print(f"Filter ON - show_assigned_only: {show_assigned_only_filtered}")
    print()
    
    # Check if there are any JavaScript errors or console logs
    print("JAVASCRIPT DEBUG CHECK:")
    print("-" * 30)
    js_filter_debug_all = html_all.count('[FILTER_DEBUG]')
    js_filter_debug_filtered = html_filtered.count('[FILTER_DEBUG]')
    print(f"Filter OFF - JS debug statements: {js_filter_debug_all}")
    print(f"Filter ON - JS debug statements: {js_filter_debug_filtered}")
    print()
    
    print("RECOMMENDATIONS:")
    print("1. Open browser developer tools and check console for [FILTER_DEBUG] messages")
    print("2. Test in incognito mode to bypass all browser cache")
    print("3. Check if there are any AJAX requests overriding the page content")
    print("4. Verify the URL in browser address bar matches expected pattern")
    print("5. Use 'View Page Source' to see raw HTML vs rendered DOM")

if __name__ == '__main__':
    test_actual_browser_response()
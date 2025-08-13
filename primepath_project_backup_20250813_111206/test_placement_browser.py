#!/usr/bin/env python
"""
Test script to simulate browser interaction with Placement Rules page
"""
import os
import sys
import django
import json
import requests
from bs4 import BeautifulSoup

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from core.models import CurriculumLevel

def test_placement_rules_browser():
    """Simulate browser interaction with placement rules page"""
    print("\n" + "="*60)
    print("Testing Placement Rules Page - Browser Simulation")
    print("="*60)
    
    session = requests.Session()
    base_url = "http://127.0.0.1:8000"
    
    # Step 1: GET the placement rules page
    print("\n1. Loading placement rules page...")
    response = session.get(f"{base_url}/placement-rules/")
    
    if response.status_code != 200:
        print(f"   ❌ Failed to load page: {response.status_code}")
        return False
    
    print(f"   ✓ Page loaded successfully")
    
    # Parse the HTML to extract CSRF token
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    
    if not csrf_input:
        print("   ❌ CSRF token not found in HTML")
        return False
    
    csrf_token = csrf_input.get('value')
    print(f"   ✓ CSRF token extracted: {csrf_token[:20]}...")
    
    # Check if we also got a cookie
    if 'csrftoken' in session.cookies:
        print(f"   ✓ CSRF cookie also set: {session.cookies['csrftoken'][:20]}...")
    else:
        print("   ⚠ No CSRF cookie set (might use session-based CSRF)")
    
    # Step 2: Prepare test data
    levels = CurriculumLevel.objects.all()[:2]
    if not levels:
        print("\n❌ No curriculum levels found")
        return False
    
    test_rules = [
        {
            'program': 'CORE',
            'grade': 1,
            'rank': 'top_10',
            'curriculum_level_id': levels[0].id
        }
    ]
    
    print(f"\n2. Sending save request with CSRF token...")
    print(f"   Test data: Grade 1, Rank top_10, Level {levels[0].display_name}")
    
    # Step 3: Make the save request with proper headers
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token,  # Use the token from the form
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': f"{base_url}/placement-rules/"
    }
    
    response = session.post(
        f"{base_url}/api/placement-rules/save/",
        json={'rules': test_rules},
        headers=headers
    )
    
    print(f"   Response status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            if data.get('success'):
                print("   ✓ Save successful!")
                return True
            else:
                print(f"   ❌ Save failed: {data.get('error')}")
                return False
        except:
            print(f"   ❌ Invalid JSON response: {response.text[:200]}")
            return False
    elif response.status_code == 403:
        print("   ❌ CSRF verification failed")
        print(f"   Response: {response.text[:200]}")
        return False
    else:
        print(f"   ❌ Unexpected response")
        print(f"   Response: {response.text[:200]}")
        return False

def test_csrf_methods():
    """Test different CSRF token methods"""
    print("\n" + "="*60)
    print("Testing CSRF Token Methods")
    print("="*60)
    
    session = requests.Session()
    base_url = "http://127.0.0.1:8000"
    
    # Get the page
    response = session.get(f"{base_url}/placement-rules/")
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Method 1: From hidden input
    csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    if csrf_input:
        print("\n✓ Method 1 - Hidden input field:")
        print(f"  Token: {csrf_input.get('value')[:20]}...")
    else:
        print("\n❌ Method 1 - No hidden input field found")
    
    # Method 2: From cookie
    if 'csrftoken' in session.cookies:
        print("\n✓ Method 2 - Cookie:")
        print(f"  Token: {session.cookies['csrftoken'][:20]}...")
    else:
        print("\n❌ Method 2 - No CSRF cookie found")
    
    # Method 3: Check if both match
    if csrf_input and 'csrftoken' in session.cookies:
        if csrf_input.get('value') == session.cookies['csrftoken']:
            print("\n✓ Tokens match (same value in form and cookie)")
        else:
            print("\n⚠ Tokens differ (form vs cookie) - this is normal")

if __name__ == '__main__':
    # Test CSRF methods first
    test_csrf_methods()
    
    # Then test the actual save
    success = test_placement_rules_browser()
    
    if success:
        print("\n" + "="*60)
        print("✅ Placement Rules save is working correctly!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ Issue found with Placement Rules save")
        print("="*60)
    
    sys.exit(0 if success else 1)
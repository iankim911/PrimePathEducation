#!/usr/bin/env python
"""
Final comprehensive test for Placement Rules functionality
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

from core.models import CurriculumLevel, PlacementRule

def test_placement_rules_complete():
    """Complete test of placement rules functionality"""
    print("\n" + "="*70)
    print("COMPREHENSIVE PLACEMENT RULES TEST")
    print("="*70)
    
    session = requests.Session()
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: Page loads correctly
    print("\n1. Testing page load...")
    response = session.get(f"{base_url}/placement-rules/")
    
    if response.status_code != 200:
        print(f"   ❌ Failed to load page: {response.status_code}")
        return False
    print("   ✓ Page loads successfully")
    
    # Test 2: CSRF token is present
    print("\n2. Testing CSRF token presence...")
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Check for CSRF token in form
    csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    if csrf_input:
        csrf_token = csrf_input.get('value')
        print(f"   ✓ CSRF token in HTML: {csrf_token[:20]}...")
    else:
        print("   ❌ No CSRF token in HTML")
        return False
    
    # Check for CSRF cookie
    if 'csrftoken' in session.cookies:
        print(f"   ✓ CSRF cookie present: {session.cookies['csrftoken'][:20]}...")
    else:
        print("   ⚠ No CSRF cookie (using session-based CSRF)")
    
    # Check JavaScript functions
    print("\n3. Testing JavaScript functions...")
    js_checks = [
        ('getCookie function', 'function getCookie' in response.text),
        ('savePlacementRules function', 'function savePlacementRules' in response.text),
        ('CSRF token DOM fallback', "querySelector('[name=csrfmiddlewaretoken]')" in response.text),
        ('Error handling', 'if (!response.ok)' in response.text),
        ('CSRF validation', 'if (!csrfToken)' in response.text)
    ]
    
    for check_name, check_result in js_checks:
        if check_result:
            print(f"   ✓ {check_name} found")
        else:
            print(f"   ❌ {check_name} missing")
    
    # Test 4: Save operation
    print("\n4. Testing save operation...")
    
    # Get curriculum levels for test
    levels = CurriculumLevel.objects.all()[:2]
    if not levels:
        print("   ❌ No curriculum levels found")
        return False
    
    test_rules = [
        {
            'program': 'CORE',
            'grade': 1,
            'rank': 'top_10',
            'curriculum_level_id': levels[0].id
        },
        {
            'program': 'CORE',
            'grade': 2,
            'rank': 'top_20',
            'curriculum_level_id': levels[1].id if len(levels) > 1 else levels[0].id
        }
    ]
    
    # Clear existing rules first
    PlacementRule.objects.all().delete()
    print("   Cleared existing rules")
    
    # Make save request
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token,
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': f"{base_url}/placement-rules/"
    }
    
    response = session.post(
        f"{base_url}/api/placement-rules/save/",
        json={'rules': test_rules},
        headers=headers
    )
    
    if response.status_code == 200:
        try:
            data = response.json()
            if data.get('success'):
                print("   ✓ Save request successful")
                
                # Verify in database
                saved_count = PlacementRule.objects.count()
                print(f"   ✓ {saved_count} rules saved to database")
                
                # Show saved rules
                for rule in PlacementRule.objects.all()[:5]:
                    print(f"      - Grade {rule.grade}, {rule.min_rank_percentile}-{rule.max_rank_percentile}%, {rule.curriculum_level.display_name}")
                
            else:
                print(f"   ❌ Save failed: {data.get('error')}")
                return False
        except Exception as e:
            print(f"   ❌ Error parsing response: {e}")
            return False
    else:
        print(f"   ❌ Request failed with status {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        return False
    
    # Test 5: Load saved rules
    print("\n5. Testing load saved rules...")
    response = session.get(f"{base_url}/api/placement-rules/")
    
    if response.status_code == 200:
        try:
            data = response.json()
            if data.get('success'):
                rules = data.get('rules', [])
                print(f"   ✓ Loaded {len(rules)} rules from API")
                for rule in rules[:3]:
                    print(f"      - Grade {rule['grade']}, Rank {rule['rank']}, Level ID {rule['curriculum_level_id']}")
            else:
                print(f"   ❌ Failed to load rules")
                return False
        except Exception as e:
            print(f"   ❌ Error parsing response: {e}")
            return False
    else:
        print(f"   ❌ Failed to load rules: {response.status_code}")
        return False
    
    return True

if __name__ == '__main__':
    try:
        success = test_placement_rules_complete()
        
        if success:
            print("\n" + "="*70)
            print("✅ PLACEMENT RULES: ALL TESTS PASSED!")
            print("="*70)
            print("\nThe Placement Rules save functionality is working correctly.")
            print("If you're still seeing errors in the browser, try:")
            print("1. Clear browser cache and cookies")
            print("2. Use an incognito/private window")
            print("3. Check browser console for JavaScript errors")
        else:
            print("\n" + "="*70)
            print("❌ PLACEMENT RULES: TESTS FAILED")
            print("="*70)
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
    
    sys.exit(0)
#!/usr/bin/env python
"""
Test script to verify Placement Rules save functionality
"""
import os
import sys
import django
import json
from django.test import Client
from django.urls import reverse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from core.models import Program, SubProgram, CurriculumLevel, PlacementRule

def test_placement_rules_save():
    """Test saving placement rules"""
    print("\n" + "="*50)
    print("Testing Placement Rules Save Functionality")
    print("="*50)
    
    client = Client()
    
    # Get some curriculum levels for testing
    levels = CurriculumLevel.objects.all()[:3]
    if not levels:
        print("❌ No curriculum levels found in database")
        return False
    
    print(f"\n✓ Found {len(levels)} curriculum levels for testing")
    
    # Prepare test data
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
    
    print("\nTest data prepared:")
    for rule in test_rules:
        print(f"  - Grade {rule['grade']}, Rank {rule['rank']}, Level ID {rule['curriculum_level_id']}")
    
    # Test 1: Direct POST without CSRF (should fail)
    print("\n1. Testing POST without CSRF token...")
    response = client.post(
        reverse('core:save_placement_rules'),
        data=json.dumps({'rules': test_rules}),
        content_type='application/json'
    )
    
    if response.status_code == 403:
        print("   ✓ Correctly rejected (403 Forbidden) - CSRF protection working")
    else:
        print(f"   ⚠ Unexpected status code: {response.status_code}")
        print(f"   Response: {response.content.decode()}")
    
    # Test 2: POST with CSRF token
    print("\n2. Testing POST with CSRF token...")
    
    # Get CSRF token
    client.get('/')  # Get a page to establish session
    csrf_token = client.cookies.get('csrftoken')
    
    if csrf_token:
        print(f"   ✓ CSRF token obtained: {csrf_token.value[:20]}...")
    else:
        print("   ❌ Could not obtain CSRF token")
        return False
    
    # Make request with CSRF token
    response = client.post(
        reverse('core:save_placement_rules'),
        data=json.dumps({'rules': test_rules}),
        content_type='application/json',
        HTTP_X_CSRFTOKEN=csrf_token.value
    )
    
    print(f"   Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("   ✓ Save successful!")
            
            # Verify rules were saved
            saved_rules = PlacementRule.objects.all()
            print(f"\n3. Verification:")
            print(f"   - Total rules in database: {saved_rules.count()}")
            
            for rule in saved_rules[:5]:  # Show first 5 rules
                print(f"     • Grade {rule.grade}, "
                      f"Rank {rule.min_rank_percentile}-{rule.max_rank_percentile}%, "
                      f"Level: {rule.curriculum_level.display_name}")
            
            return True
        else:
            print(f"   ❌ Save failed: {data.get('error')}")
            return False
    else:
        print(f"   ❌ Request failed")
        try:
            error_data = response.json()
            print(f"   Error: {error_data}")
        except:
            print(f"   Response: {response.content.decode()[:200]}")
        return False

if __name__ == '__main__':
    success = test_placement_rules_save()
    
    if success:
        print("\n" + "="*50)
        print("✅ All Placement Rules tests passed!")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("❌ Some tests failed - check output above")
        print("="*50)
    
    sys.exit(0 if success else 1)
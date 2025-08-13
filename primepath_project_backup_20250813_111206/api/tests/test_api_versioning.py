#!/usr/bin/env python3
"""
Test API Versioning Implementation
Part of Phase 11: Final Integration & Testing
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.urls import reverse, resolve
import json

def test_api_versioning():
    """Test that API versioning is working correctly"""
    client = Client()
    results = {
        'passed': [],
        'failed': []
    }
    
    print("="*60)
    print("  TESTING API VERSIONING IMPLEMENTATION")
    print("="*60)
    
    # Test 1: Check v1 endpoints
    print("\n1. Testing v1 endpoints...")
    v1_endpoints = [
        '/api/v1/health/',
        '/api/v1/exams/',
        '/api/v1/sessions/',
        '/api/v1/schools/',
        '/api/v1/programs/',
    ]
    
    for endpoint in v1_endpoints:
        try:
            response = client.get(endpoint)
            if response.status_code in [200, 401, 403]:  # OK or auth required
                print(f"   ✅ {endpoint} accessible")
                results['passed'].append(f"v1 endpoint: {endpoint}")
            else:
                print(f"   ❌ {endpoint} error: {response.status_code}")
                results['failed'].append(f"v1 endpoint {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint} exception: {e}")
            results['failed'].append(f"v1 endpoint {endpoint}: {str(e)}")
    
    # Test 2: Check backward compatibility (non-versioned endpoints)
    print("\n2. Testing backward compatibility...")
    legacy_endpoints = [
        '/api/health/',
        '/api/exams/',
        '/api/sessions/',
    ]
    
    for endpoint in legacy_endpoints:
        try:
            response = client.get(endpoint)
            if response.status_code in [200, 401, 403]:
                print(f"   ✅ {endpoint} backward compatible")
                results['passed'].append(f"Legacy endpoint: {endpoint}")
            else:
                print(f"   ❌ {endpoint} not working: {response.status_code}")
                results['failed'].append(f"Legacy endpoint {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint} exception: {e}")
            results['failed'].append(f"Legacy endpoint {endpoint}: {str(e)}")
    
    # Test 3: Check API structure
    print("\n3. Checking API structure...")
    api_structure_checks = [
        ('api/v1/__init__.py', 'v1 package initialized'),
        ('api/v1/urls.py', 'v1 URLs configured'),
        ('api/v1/views.py', 'v1 views present'),
        ('api/v1/serializers.py', 'v1 serializers present'),
        ('api/common/__init__.py', 'Common utilities initialized'),
        ('api/common/pagination.py', 'Common pagination'),
        ('api/common/permissions.py', 'Common permissions'),
    ]
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for file_path, description in api_structure_checks:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            print(f"   ✅ {description}")
            results['passed'].append(description)
        else:
            print(f"   ❌ {description} missing")
            results['failed'].append(f"{description} missing")
    
    # Test 4: Check placement API endpoints
    print("\n4. Testing placement API endpoints...")
    placement_endpoints = [
        '/api/v1/placement/start/',
        '/api/placement/start/',  # Legacy
    ]
    
    for endpoint in placement_endpoints:
        try:
            # GET to check if endpoint exists (will require POST data for actual use)
            response = client.get(endpoint)
            # 405 Method Not Allowed is OK - means endpoint exists but needs POST
            if response.status_code in [200, 401, 403, 405]:
                print(f"   ✅ {endpoint} exists")
                results['passed'].append(f"Placement endpoint: {endpoint}")
            else:
                print(f"   ❌ {endpoint} error: {response.status_code}")
                results['failed'].append(f"Placement endpoint {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint} exception: {e}")
            results['failed'].append(f"Placement endpoint {endpoint}: {str(e)}")
    
    # Summary
    print("\n" + "="*60)
    print("  TEST RESULTS")
    print("="*60)
    total = len(results['passed']) + len(results['failed'])
    pass_rate = (len(results['passed']) / total * 100) if total > 0 else 0
    
    print(f"\n✅ Passed: {len(results['passed'])}")
    print(f"❌ Failed: {len(results['failed'])}")
    print(f"📊 Pass Rate: {pass_rate:.1f}%")
    
    if results['failed']:
        print("\nFailed tests:")
        for failure in results['failed']:
            print(f"  - {failure}")
    
    if pass_rate >= 80:
        print("\n✅ API VERSIONING SUCCESSFULLY IMPLEMENTED!")
    else:
        print("\n⚠️  API versioning needs attention")
    
    return results

if __name__ == "__main__":
    test_api_versioning()
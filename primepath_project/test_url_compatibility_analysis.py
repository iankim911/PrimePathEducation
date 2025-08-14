#!/usr/bin/env python
"""
Pre-implementation analysis of URL compatibility 
Tests current URL structure before making changes
"""

import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.urls import reverse, resolve
from placement_test.models import StudentSession, Exam
from django.urls import NoReverseMatch

def test_current_url_structure():
    """Analyze current URL structure and dependencies"""
    print("🔍 URL COMPATIBILITY ANALYSIS - PRE-IMPLEMENTATION")
    print("=" * 60)
    
    client = Client()
    results = {'working': [], 'broken': [], 'analysis': []}
    
    # Test current working URLs
    print("\n1. Testing Current URL Structure:")
    
    # Create test session for URL testing
    exam = Exam.objects.filter(is_active=True).first()
    if exam:
        session = StudentSession.objects.create(
            student_name="URL Test",
            parent_phone="010-0000-0000", 
            school_id=1,
            grade=7,
            academic_rank="TOP_30",
            exam=exam
        )
        
        # Test current URLs
        current_urls = [
            f'/api/PlacementTest/session/{session.id}/',
            f'/api/PlacementTest/session/{session.id}/submit/',
            f'/api/PlacementTest/session/{session.id}/complete/',
            f'/api/PlacementTest/session/{session.id}/result/',
            '/api/PlacementTest/start/',
            '/api/PlacementTest/sessions/',
            '/api/PlacementTest/exams/',
        ]
        
        print("Testing current URL patterns:")
        for url in current_urls:
            try:
                response = client.get(url)
                status = "✅ WORKING" if response.status_code < 500 else "⚠️ ERROR"
                print(f"  {url} → {status} ({response.status_code})")
                if response.status_code < 500:
                    results['working'].append(url)
                else:
                    results['broken'].append(url)
            except Exception as e:
                print(f"  {url} → ❌ EXCEPTION ({str(e)})")
                results['broken'].append(url)
        
        # Test legacy URLs (should be 404 currently)
        print(f"\nTesting legacy URL patterns (should be 404):")
        legacy_urls = [
            f'/PlacementTest/test/{session.id}/',
            f'/PlacementTest/session/{session.id}/',
        ]
        
        for url in legacy_urls:
            try:
                response = client.get(url)
                status = "404 NOT FOUND" if response.status_code == 404 else f"UNEXPECTED {response.status_code}"
                print(f"  {url} → {status}")
                results['analysis'].append(f"{url}: {status}")
            except Exception as e:
                print(f"  {url} → EXCEPTION ({str(e)})")
                results['analysis'].append(f"{url}: EXCEPTION")
    
    # Test URL name resolution
    print(f"\n2. Testing URL Name Resolution:")
    url_names = [
        'PlacementTest:start_test',
        'PlacementTest:take_test',
        'PlacementTest:submit_answer',
        'PlacementTest:complete_test',
        'PlacementTest:test_result',
        'PlacementTest:post_submit_difficulty_choice',
        'core:teacher_dashboard',
        'core:exam_mapping',
    ]
    
    for name in url_names:
        try:
            if 'session_id' in name or 'uuid' in name:
                # Skip URLs that need parameters for this test
                print(f"  {name} → REQUIRES PARAMETERS (skipped)")
                continue
            url = reverse(name)
            print(f"  {name} → ✅ RESOLVES ({url})")
            results['working'].append(f"URL_NAME:{name}")
        except NoReverseMatch as e:
            print(f"  {name} → ❌ FAILED ({str(e)})")
            results['broken'].append(f"URL_NAME:{name}")
        except Exception as e:
            print(f"  {name} → ❌ EXCEPTION ({str(e)})")
            results['broken'].append(f"URL_NAME:{name}")
    
    # Summary
    print(f"\n3. Analysis Summary:")
    print(f"✅ Working URLs/Names: {len(results['working'])}")
    print(f"❌ Broken URLs/Names: {len(results['broken'])}")
    print(f"📊 Analysis Notes: {len(results['analysis'])}")
    
    if results['broken']:
        print(f"\n⚠️ Issues Found:")
        for issue in results['broken']:
            print(f"  - {issue}")
    
    # Save results
    with open('url_compatibility_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: url_compatibility_analysis.json")
    return len(results['broken']) == 0

if __name__ == '__main__':
    success = test_current_url_structure()
    sys.exit(0 if success else 1)
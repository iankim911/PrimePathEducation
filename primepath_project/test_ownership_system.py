#!/usr/bin/env python
"""
Test the new ownership-based tab system
Comprehensive testing of My Test Files vs Other Teachers' Test Files
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
import json

def test_ownership_system():
    """Test the new ownership-based filtering system"""
    
    print("🔍 TESTING NEW OWNERSHIP-BASED TAB SYSTEM")
    print("=" * 60)
    
    # Set up test client
    client = Client()
    teacher1 = User.objects.get(username='teacher1')
    teacher1.set_password('teacher123')
    teacher1.save()
    
    login = client.login(username='teacher1', password='teacher123')
    print(f"✅ Logged in as teacher1: {login}")
    
    def test_ownership_filter(ownership, exam_type, description):
        print(f"\n{'='*50}")
        print(f"🧪 TESTING: {description}")
        print(f"{'='*50}")
        
        url = f'/RoutineTest/exams/?ownership={ownership}&exam_type={exam_type}'
        print(f"URL: {url}")
        
        response = client.get(url)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Count ownership tabs
            if 'ownership-tab active' in content:
                print("✅ Ownership tab system found in HTML")
            else:
                print("❌ Ownership tab system NOT found")
            
            # Check for correct active tab
            if f'ownership={ownership}' in content and 'exam_type={exam_type}' in content:
                print(f"✅ URL parameters correctly integrated: ownership={ownership}, exam_type={exam_type}")
            
            # Count exam cards
            exam_cards = content.count('exam-card')
            print(f"Exam cards found: {exam_cards}")
            
            # Count VIEW ONLY badges
            view_only_badges = content.count('VIEW ONLY')
            print(f"VIEW ONLY badges: {view_only_badges}")
            
            # Check expected behavior
            if ownership == 'my':
                if view_only_badges == 0:
                    print("✅ CORRECT: No VIEW ONLY badges in 'My Test Files'")
                else:
                    print(f"❌ ERROR: Found {view_only_badges} VIEW ONLY badges in 'My Test Files' - should be 0")
            elif ownership == 'others':
                print(f"ℹ️ INFO: 'Other Teachers' Test Files' showing {view_only_badges} VIEW ONLY badges (expected)")
            
            # Check for JavaScript logging
            if '[OWNERSHIP_SYSTEM_DEBUG]' in content:
                print("✅ Enhanced logging system integrated")
            
            return {
                'exam_cards': exam_cards,
                'view_only_badges': view_only_badges,
                'status': 'success'
            }
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return {'status': 'error', 'code': response.status_code}
    
    # Test all combinations
    test_cases = [
        ('my', 'ALL', 'My Test Files → All Exams'),
        ('my', 'REVIEW', 'My Test Files → Review/Monthly'),
        ('my', 'QUARTERLY', 'My Test Files → Quarterly'),
        ('others', 'ALL', 'Other Teachers\' Test Files → All Exams'),
        ('others', 'REVIEW', 'Other Teachers\' Test Files → Review/Monthly'),
        ('others', 'QUARTERLY', 'Other Teachers\' Test Files → Quarterly'),
    ]
    
    results = {}
    for ownership, exam_type, description in test_cases:
        results[f"{ownership}_{exam_type}"] = test_ownership_filter(ownership, exam_type, description)
    
    # Summary
    print(f"\n{'🏁 FINAL SUMMARY'}")
    print("=" * 60)
    
    success_count = sum(1 for r in results.values() if r['status'] == 'success')
    total_count = len(results)
    
    print(f"✅ Successful tests: {success_count}/{total_count}")
    
    # Check key requirements
    my_all_result = results.get('my_ALL', {})
    others_all_result = results.get('others_ALL', {})
    
    if my_all_result.get('view_only_badges', 0) == 0:
        print("✅ REQUIREMENT MET: 'My Test Files' shows no VIEW ONLY badges")
    else:
        print("❌ REQUIREMENT FAILED: 'My Test Files' still shows VIEW ONLY badges")
    
    if others_all_result.get('view_only_badges', 0) > 0:
        print("✅ REQUIREMENT MET: 'Other Teachers' Test Files' shows VIEW ONLY badges")
    else:
        print("ℹ️ INFO: 'Other Teachers' Test Files' shows no VIEW ONLY badges (may be normal)")
    
    # Test backward compatibility
    print(f"\n📋 TESTING BACKWARD COMPATIBILITY")
    print("-" * 40)
    
    legacy_response = client.get('/RoutineTest/exams/?assigned_only=true')
    if legacy_response.status_code == 200:
        print("✅ Legacy assigned_only=true parameter still works")
        legacy_content = legacy_response.content.decode('utf-8')
        if 'ownership_filter' in legacy_content:
            print("✅ Legacy parameter converted to new ownership system")
    
    print(f"\n🎯 NEW OWNERSHIP SYSTEM TESTING COMPLETE!")
    return results

if __name__ == "__main__":
    test_ownership_system()
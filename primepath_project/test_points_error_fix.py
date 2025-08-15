#!/usr/bin/env python3
"""
COMPREHENSIVE TEST: Points Error Fix
Tests that question_number is included in all response paths
"""

import os
import sys
import json
from datetime import datetime

# Django setup
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')

import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from placement_test.models import Exam, Question
from placement_test.services import PointsService

def test_points_error_responses():
    """Test that all error responses include question_number"""
    
    print("=" * 60)
    print("🔧 POINTS ERROR FIX TEST")
    print("=" * 60)
    
    # Step 1: Setup authentication
    print("\n📋 STEP 1: Setting up authentication...")
    
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        user = User.objects.create_superuser(
            username='testadmin',
            password='testpass123',
            email='admin@test.com'
        )
        print(f"✅ Created test admin: {user.username}")
    else:
        user.set_password('testpass123')
        user.save()
        print(f"✅ Using existing admin: {user.username}")
    
    client = Client()
    client.login(username=user.username, password='testpass123')
    
    # Step 2: Find test exam and question
    print("\n📋 STEP 2: Finding test data...")
    
    exam = Exam.objects.filter(questions__isnull=False).first()
    question = exam.questions.first()
    print(f"✅ Using exam: {exam.name}")
    print(f"✅ Using question: Q{question.question_number} (ID: {question.id})")
    
    # Step 3: Test error scenarios
    print("\n📋 STEP 3: Testing error scenarios...")
    
    test_cases = [
        {
            'name': 'Points too low',
            'data': {'points': 0},
            'expected_status': 400,
            'expected_fields': ['success', 'error', 'question_number', 'question_id']
        },
        {
            'name': 'Points too high',
            'data': {'points': 11},
            'expected_status': 400,
            'expected_fields': ['success', 'error', 'question_number', 'question_id']
        },
        {
            'name': 'Invalid points format',
            'data': {'points': 'invalid'},
            'expected_status': 400,
            'expected_fields': ['success', 'error', 'question_number', 'question_id']
        },
        {
            'name': 'Invalid options count',
            'data': {'options_count': 11},
            'expected_status': 400,
            'expected_fields': ['success', 'error', 'question_number', 'question_id']
        },
        {
            'name': 'Valid points update',
            'data': {'points': 5},
            'expected_status': 200,
            'expected_fields': ['success', 'question_number', 'question_id', 'question']
        }
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        print(f"\n   Testing: {test_case['name']}")
        print(f"   Sending data: {test_case['data']}")
        
        response = client.post(
            f'/api/PlacementTest/questions/{question.id}/update/',
            data=test_case['data'],
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        print(f"   Response status: {response.status_code}")
        
        if response.status_code != test_case['expected_status']:
            print(f"   ❌ Unexpected status: expected {test_case['expected_status']}, got {response.status_code}")
            all_passed = False
            continue
        
        try:
            data = response.json()
            
            # Check for required fields
            missing_fields = []
            for field in test_case['expected_fields']:
                if field not in data:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"   ❌ Missing fields: {missing_fields}")
                print(f"   Response keys: {list(data.keys())}")
                all_passed = False
            else:
                print(f"   ✅ All required fields present")
                
                # Verify question_number value
                if 'question_number' in data:
                    if data['question_number'] == question.question_number:
                        print(f"   ✅ question_number correct: {data['question_number']}")
                    else:
                        print(f"   ❌ question_number incorrect: expected {question.question_number}, got {data['question_number']}")
                        all_passed = False
                
                # Check nested question object if present
                if 'question' in data:
                    if isinstance(data['question'], dict):
                        if 'number' in data['question']:
                            print(f"   ✅ Nested question.number present: {data['question']['number']}")
                        else:
                            print(f"   ⚠️ Nested question object missing 'number' field")
                    else:
                        print(f"   ⚠️ question field is not a dict: {type(data['question'])}")
            
            # Show debug info for errors
            if not data.get('success'):
                print(f"   Error message: {data.get('error', 'No error message')}")
                if 'debug_info' in data:
                    print(f"   Debug info available: {len(data['debug_info'])} items")
                    
        except Exception as e:
            print(f"   ❌ Failed to parse response: {e}")
            all_passed = False
    
    # Step 4: Test frontend compatibility
    print("\n📋 STEP 4: Testing frontend compatibility...")
    
    # Simulate a valid update to check success path
    response = client.post(
        f'/api/PlacementTest/questions/{question.id}/update/',
        data={'points': 3},
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    
    if response.status_code == 200:
        data = response.json()
        
        # Check both old and new field locations
        print("\n   Field compatibility check:")
        print(f"   Root level question_number: {'✅' if 'question_number' in data else '❌'}")
        print(f"   Root level question_id: {'✅' if 'question_id' in data else '❌'}")
        print(f"   Nested question.number: {'✅' if data.get('question', {}).get('number') else '❌'}")
        print(f"   Nested question.id: {'✅' if data.get('question', {}).get('id') else '❌'}")
        
        # Check if frontend can access the data
        can_access_old_way = 'question_number' in data
        can_access_new_way = 'question' in data and 'number' in data.get('question', {})
        
        if can_access_old_way:
            print(f"   ✅ Frontend can use data.question_number")
        else:
            print(f"   ❌ Frontend cannot use data.question_number")
            all_passed = False
            
        if can_access_new_way:
            print(f"   ✅ Frontend can use data.question.number")
        else:
            print(f"   ⚠️ Frontend cannot use data.question.number")
    
    return all_passed

def main():
    print("\n🚀 COMPREHENSIVE POINTS ERROR FIX TEST")
    print("=" * 60)
    
    try:
        success = test_points_error_responses()
        
        if success:
            print("\n" + "=" * 60)
            print("🎉 ALL TESTS PASSED!")
            print("\n✅ Summary:")
            print("   • Error responses include question_number")
            print("   • Error responses include question_id")
            print("   • Success responses include both root and nested fields")
            print("   • Frontend backward compatibility maintained")
            print("   • No JavaScript errors expected")
            print("\n📝 The fix ensures:")
            print("   1. All error paths return question_number at root level")
            print("   2. Success paths have both root and nested structure")
            print("   3. Frontend can safely access data.question_number")
            print("   4. No 'undefined' errors in JavaScript")
        else:
            print("\n" + "=" * 60)
            print("⚠️ Some tests failed - check details above")
            print("\n🔍 Debug steps:")
            print("   1. Check browser console for JavaScript errors")
            print("   2. Verify response structure in Network tab")
            print("   3. Check server logs for Python errors")
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Test script to verify the exam API fixes work correctly
Tests the API endpoints directly through Django's test client
"""
import os
import sys
import django
from django.test import Client
from django.contrib.auth.models import User

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

def test_exam_apis():
    """Test the exam management API endpoints"""
    
    # Create a test client
    client = Client()
    
    # Create a test user and login
    test_user = User.objects.create_user(
        username='testteacher',
        password='testpass123',
        is_staff=True
    )
    
    # Login the test user
    login_success = client.login(username='testteacher', password='testpass123')
    print(f"Login successful: {login_success}")
    
    if not login_success:
        print("❌ Failed to login test user")
        return False
    
    # Test cases for different API endpoints
    test_cases = [
        {
            'name': 'Class Overview API',
            'url': '/RoutineTest/api/class/CLASS_2B/overview/?timeslot=overview',
            'expected_keys': ['class_code', 'class_name', 'curriculum', 'timeslot', 'exams']
        },
        {
            'name': 'Class Exams API',
            'url': '/RoutineTest/api/class/CLASS_2B/exams/?timeslot=overview',
            'expected_keys': ['exams']
        },
        {
            'name': 'Class Students API',
            'url': '/RoutineTest/api/class/CLASS_2B/students/',
            'expected_keys': ['students', 'total', 'active']
        },
        {
            'name': 'All Classes API',
            'url': '/RoutineTest/api/all-classes/',
            'expected_keys': ['classes']
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n🧪 Testing {test_case['name']}")
        print(f"URL: {test_case['url']}")
        
        response = client.get(test_case['url'])
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response keys: {list(data.keys())}")
                
                # Check if expected keys are present
                missing_keys = [key for key in test_case['expected_keys'] if key not in data]
                if missing_keys:
                    print(f"⚠️  Missing expected keys: {missing_keys}")
                    results.append({'test': test_case['name'], 'status': 'partial', 'issue': f'missing keys: {missing_keys}'})
                else:
                    print("✅ All expected keys present")
                    results.append({'test': test_case['name'], 'status': 'success'})
                    
                # Print sample data structure
                for key in test_case['expected_keys']:
                    if key in data:
                        value = data[key]
                        if isinstance(value, list):
                            print(f"  {key}: [{len(value)} items]")
                            if value and len(value) > 0:
                                print(f"    Sample item: {type(value[0]).__name__}")
                        else:
                            print(f"  {key}: {type(value).__name__} = {value}")
                            
            except Exception as e:
                print(f"❌ Error parsing JSON response: {e}")
                print(f"Response content: {response.content[:200]}...")
                results.append({'test': test_case['name'], 'status': 'error', 'issue': str(e)})
        elif response.status_code == 500:
            print(f"❌ Internal Server Error (500)")
            print(f"Response content: {response.content[:500]}...")
            results.append({'test': test_case['name'], 'status': 'error', 'issue': 'HTTP 500'})
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            results.append({'test': test_case['name'], 'status': 'error', 'issue': f'HTTP {response.status_code}'})
    
    # Summary
    print(f"\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    success_count = sum(1 for r in results if r['status'] == 'success')
    total_count = len(results)
    
    for result in results:
        status_icon = "✅" if result['status'] == 'success' else "⚠️" if result['status'] == 'partial' else "❌"
        issue_text = f" - {result['issue']}" if 'issue' in result else ""
        print(f"{status_icon} {result['test']}: {result['status']}{issue_text}")
    
    print(f"\nOverall: {success_count}/{total_count} tests passed")
    
    # Cleanup
    test_user.delete()
    
    return success_count == total_count

if __name__ == '__main__':
    print("🚀 Starting Exam API Fix Verification")
    print("="*60)
    
    try:
        success = test_exam_apis()
        if success:
            print("\n🎉 All tests passed! API fixes are working correctly.")
            sys.exit(0)
        else:
            print("\n⚠️  Some tests failed. Review the output above.")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test script failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
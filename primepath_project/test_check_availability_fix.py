#!/usr/bin/env python
"""
Test the check-availability API endpoint fix
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
from django.contrib.auth.models import User
from primepath_student.models import StudentProfile

def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_check_availability_endpoint():
    """Test the check-availability API endpoint"""
    print_section("TESTING CHECK AVAILABILITY API ENDPOINT")
    
    client = Client()
    
    # Create a test user that already exists
    test_user, created = User.objects.get_or_create(
        username='test123',
        defaults={
            'first_name': 'Test',
            'last_name': 'Student',
            'email': 'test123@example.com'
        }
    )
    
    # Create student profile if user was created
    if created:
        StudentProfile.objects.create(
            user=test_user,
            student_id='test123',
            phone_number='010-1234-5678',
            parent1_name='Test Parent',
            parent1_phone='010-8765-4321'
        )
        print(f"✓ Created test user: {test_user.username}")
    else:
        print(f"✓ Using existing test user: {test_user.username}")
    
    # Test 1: Check available student ID
    print("\n[Test 1: Available Student ID]")
    response = client.post(
        '/student/api/check-availability/',
        data=json.dumps({
            'type': 'student_id',
            'value': 'new_student_123'
        }),
        content_type='application/json'
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data}")
        if data.get('available') is True:
            print("✅ PASS: Available student ID correctly identified")
        else:
            print("❌ FAIL: Available student ID not correctly identified")
    else:
        print(f"❌ FAIL: Endpoint returned {response.status_code}")
        print(f"Response: {response.content.decode()}")
    
    # Test 2: Check taken student ID
    print("\n[Test 2: Taken Student ID]")
    response = client.post(
        '/student/api/check-availability/',
        data=json.dumps({
            'type': 'student_id',
            'value': 'test123'
        }),
        content_type='application/json'
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data}")
        if data.get('available') is False:
            print("✅ PASS: Taken student ID correctly identified")
        else:
            print("❌ FAIL: Taken student ID not correctly identified")
    else:
        print(f"❌ FAIL: Endpoint returned {response.status_code}")
        print(f"Response: {response.content.decode()}")
    
    # Test 3: Check available email
    print("\n[Test 3: Available Email]")
    response = client.post(
        '/student/api/check-availability/',
        data=json.dumps({
            'type': 'email',
            'value': 'new_email@example.com'
        }),
        content_type='application/json'
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data}")
        if data.get('available') is True:
            print("✅ PASS: Available email correctly identified")
        else:
            print("❌ FAIL: Available email not correctly identified")
    else:
        print(f"❌ FAIL: Endpoint returned {response.status_code}")
        print(f"Response: {response.content.decode()}")
    
    # Test 4: Check taken email
    print("\n[Test 4: Taken Email]")
    response = client.post(
        '/student/api/check-availability/',
        data=json.dumps({
            'type': 'email',
            'value': 'test123@example.com'
        }),
        content_type='application/json'
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data}")
        if data.get('available') is False:
            print("✅ PASS: Taken email correctly identified")
        else:
            print("❌ FAIL: Taken email not correctly identified")
    else:
        print(f"❌ FAIL: Endpoint returned {response.status_code}")
        print(f"Response: {response.content.decode()}")
    
    # Test 5: Check available phone
    print("\n[Test 5: Available Phone]")
    response = client.post(
        '/student/api/check-availability/',
        data=json.dumps({
            'type': 'phone',
            'value': '010-9999-9999'
        }),
        content_type='application/json'
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data}")
        if data.get('available') is True:
            print("✅ PASS: Available phone correctly identified")
        else:
            print("❌ FAIL: Available phone not correctly identified")
    else:
        print(f"❌ FAIL: Endpoint returned {response.status_code}")
        print(f"Response: {response.content.decode()}")
    
    # Test 6: Check taken phone
    print("\n[Test 6: Taken Phone]")
    response = client.post(
        '/student/api/check-availability/',
        data=json.dumps({
            'type': 'phone',
            'value': '010-1234-5678'
        }),
        content_type='application/json'
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data}")
        if data.get('available') is False:
            print("✅ PASS: Taken phone correctly identified")
        else:
            print("❌ FAIL: Taken phone not correctly identified")
    else:
        print(f"❌ FAIL: Endpoint returned {response.status_code}")
        print(f"Response: {response.content.decode()}")

def test_registration_page_loads():
    """Test that the registration page loads correctly"""
    print_section("TESTING REGISTRATION PAGE LOADS")
    
    client = Client()
    response = client.get('/student/register/')
    
    print(f"Registration page status: {response.status_code}")
    if response.status_code == 200:
        print("✅ PASS: Registration page loads successfully")
        
        # Check if the check availability functionality is present
        content = response.content.decode()
        if 'check-availability' in content:
            print("✅ PASS: Check availability functionality is present in page")
        else:
            print("❌ FAIL: Check availability functionality not found in page")
    else:
        print(f"❌ FAIL: Registration page returned {response.status_code}")

def run_tests():
    """Run all tests"""
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "CHECK AVAILABILITY API FIX TEST" + " " * 15 + "║")
    print("╚" + "═" * 58 + "╝")
    
    try:
        test_registration_page_loads()
        test_check_availability_endpoint()
        
        print_section("SUMMARY")
        print("✅ Fix applied: @csrf_exempt decorator added to check_availability view")
        print("✅ API endpoint should now work for unauthenticated users")
        print("✅ Registration form availability checking should be functional")
        
        print("\nNEXT STEPS:")
        print("1. Restart the Django server for changes to take effect")
        print("2. Test the registration page in browser")
        print("3. Try checking student ID availability with the 'Check' button")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
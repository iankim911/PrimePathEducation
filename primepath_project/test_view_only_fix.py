#!/usr/bin/env python3
"""
Test script to verify that VIEW ONLY badges are removed from Classes and Exams page
"""
import os
import sys
import django
import requests
from bs4 import BeautifulSoup

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, '.')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_view_only_fix():
    """Test that VIEW ONLY badges are no longer shown on Classes and Exams page"""
    print("=" * 80)
    print("TESTING VIEW ONLY BADGE FIX")
    print("=" * 80)
    
    # Create a test client
    client = Client()
    
    # Login as admin user
    try:
        user = User.objects.get(username='admin')
        user.set_password('test123')
        user.save()
        login_success = client.login(username='admin', password='test123')
        
        if not login_success:
            print("❌ Failed to login as admin")
            return False
        
        print("✅ Successfully logged in as admin")
        
    except User.DoesNotExist:
        print("❌ Admin user not found")
        return False
    
    # Test the Classes and Exams page
    response = client.get('/RoutineTest/classes-exams/')
    
    if response.status_code != 200:
        print(f"❌ Failed to load Classes and Exams page: {response.status_code}")
        return False
    
    print("✅ Classes and Exams page loaded successfully")
    
    # Parse HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Check for VIEW ONLY badges
    view_only_badges = soup.find_all(string="VIEW ONLY")
    view_access_badges = soup.find_all(string="VIEW Access")
    
    print(f"\n📊 RESULTS:")
    print(f"   'VIEW ONLY' text found: {len(view_only_badges)} times")
    print(f"   'VIEW Access' text found: {len(view_access_badges)} times")
    
    # Check for FULL ACCESS badges (these should be present)
    full_access_badges = soup.find_all(string="FULL ACCESS")
    full_access_text = soup.find_all(string="FULL Access")
    
    print(f"   'FULL ACCESS' text found: {full_access_badges.__len__()} times")
    print(f"   'FULL Access' text found: {full_access_text.__len__()} times")
    
    # Test passed if no VIEW ONLY badges are found
    if len(view_only_badges) == 0 and len(view_access_badges) == 0:
        print(f"\n✅ SUCCESS: No VIEW ONLY badges found on Classes and Exams page!")
        print(f"   Classes now correctly show only FULL ACCESS badges")
        return True
    else:
        print(f"\n❌ FAILURE: Still found VIEW ONLY badges on Classes and Exams page")
        print(f"   This indicates the fix did not work as expected")
        
        # Show where VIEW ONLY badges were found
        if view_only_badges:
            print(f"\n   'VIEW ONLY' badges found in these contexts:")
            for i, badge in enumerate(view_only_badges[:5]):  # Show first 5
                parent = badge.parent
                if parent:
                    print(f"   {i+1}. {parent.get_text().strip()[:100]}...")
        
        return False

def test_with_different_server_ports():
    """Test via HTTP requests to running server on different ports"""
    print("\n" + "=" * 80)
    print("TESTING WITH HTTP REQUESTS")
    print("=" * 80)
    
    ports_to_try = [8000, 8001, 8080]
    
    for port in ports_to_try:
        try:
            print(f"\n🔍 Testing server on port {port}...")
            
            # Try to access the login page first
            login_url = f"http://127.0.0.1:{port}/RoutineTest/auth/login/"
            response = requests.get(login_url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ Server responding on port {port}")
                
                # Create a session and login
                session = requests.Session()
                
                # Get CSRF token
                soup = BeautifulSoup(response.content, 'html.parser')
                csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
                
                if csrf_token:
                    token = csrf_token.get('value')
                    
                    # Login
                    login_data = {
                        'username': 'admin',
                        'password': 'test123',
                        'csrfmiddlewaretoken': token
                    }
                    
                    login_response = session.post(login_url, data=login_data)
                    
                    if login_response.status_code == 200 or login_response.status_code == 302:
                        print(f"✅ Login successful on port {port}")
                        
                        # Now test the Classes and Exams page
                        classes_url = f"http://127.0.0.1:{port}/RoutineTest/classes-exams/"
                        classes_response = session.get(classes_url)
                        
                        if classes_response.status_code == 200:
                            content = classes_response.text
                            view_only_count = content.count('VIEW ONLY')
                            full_access_count = content.count('FULL ACCESS')
                            
                            print(f"📊 Classes and Exams page results:")
                            print(f"   VIEW ONLY badges: {view_only_count}")
                            print(f"   FULL ACCESS badges: {full_access_count}")
                            
                            if view_only_count == 0:
                                print(f"✅ SUCCESS: No VIEW ONLY badges found via HTTP on port {port}!")
                                return True
                            else:
                                print(f"❌ FAILURE: Still found {view_only_count} VIEW ONLY badges via HTTP")
                                return False
                        else:
                            print(f"❌ Could not access Classes and Exams page: {classes_response.status_code}")
                    else:
                        print(f"❌ Login failed on port {port}")
                else:
                    print(f"❌ Could not find CSRF token on port {port}")
            else:
                print(f"⚠️  Server not responding on port {port}: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️  No server running on port {port}: {e}")
    
    return False

if __name__ == '__main__':
    print("Starting VIEW ONLY badge fix test...")
    
    # Test via Django test client first
    django_test_result = test_view_only_fix()
    
    # Test via HTTP requests if Django test passed
    if django_test_result:
        http_test_result = test_with_different_server_ports()
        
        if http_test_result:
            print(f"\n🎉 BOTH TESTS PASSED!")
            print(f"✅ Django Test Client: PASS")
            print(f"✅ HTTP Request Test: PASS")
            print(f"\nThe fix is working correctly - VIEW ONLY badges removed from Classes and Exams page!")
        else:
            print(f"\n⚠️  MIXED RESULTS:")
            print(f"✅ Django Test Client: PASS")
            print(f"❌ HTTP Request Test: FAIL")
            print(f"\nThe fix works in testing but may need server restart to take effect.")
    else:
        print(f"\n❌ DJANGO TEST FAILED")
        print(f"The fix did not work as expected. Check the view logic.")
        
        # Try HTTP test anyway for comparison
        http_test_result = test_with_different_server_ports()
    
    print("\n" + "=" * 80)
    print("TEST COMPLETED")
    print("=" * 80)
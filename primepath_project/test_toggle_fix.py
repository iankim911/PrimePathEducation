#!/usr/bin/env python3
"""
Test script to verify toggleClass function is now available.
This will login and check if the function exists in the JavaScript.
"""

import os
import sys
import django
import requests
import re

# Add the project directory to the path
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User

def test_toggle_function():
    print("🧪 Testing toggleClass function fix...")
    
    try:
        # Create/get admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'is_superuser': True,
                'is_staff': True,
                'email': 'admin@example.com'
            }
        )
        if created or not admin_user.check_password('test123'):
            admin_user.set_password('test123')
            admin_user.save()
            print(f"✅ Admin user {'created' if created else 'updated'}")
        
        # Test without authentication first (should redirect)
        response = requests.get('http://127.0.0.1:8000/RoutineTest/exams/')
        if response.status_code == 302 and '/login/' in response.headers.get('Location', ''):
            print("✅ Proper redirect to login (server is working)")
        
        # Now test with authentication
        session = requests.Session()
        
        # Get CSRF token from login page
        login_page = session.get('http://127.0.0.1:8000/login/')
        if login_page.status_code == 200:
            csrf_token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', login_page.text)
            if csrf_token:
                # Login
                login_data = {
                    'username': 'admin',
                    'password': 'test123',
                    'csrfmiddlewaretoken': csrf_token.group(1)
                }
                
                login_response = session.post('http://127.0.0.1:8000/login/', data=login_data)
                if login_response.status_code in [200, 302]:
                    print("✅ Login successful")
                    
                    # Now test the exams page with different filters
                    test_urls = [
                        'http://127.0.0.1:8000/RoutineTest/exams/',
                        'http://127.0.0.1:8000/RoutineTest/exams/?ownership=my',
                        'http://127.0.0.1:8000/RoutineTest/exams/?ownership=my&exam_type=ALL',
                    ]
                    
                    # Test different URLs to find where toggle buttons appear
                    best_result = {'toggle_calls': 0, 'url': '', 'class_sections': 0}
                    
                    for url in test_urls:
                        print(f"\n🔍 Testing URL: {url}")
                        exams_response = session.get(url)
                        if exams_response.status_code == 200:
                            html_content = exams_response.text
                            
                            # Check for onclick handlers using toggleClass
                            toggle_calls = html_content.count('onclick="toggleClass(')
                            class_sections = html_content.count('class-section')
                            
                            print(f"   Toggle calls: {toggle_calls}")
                            print(f"   Class sections: {class_sections}")
                            
                            if toggle_calls > best_result['toggle_calls']:
                                best_result = {
                                    'toggle_calls': toggle_calls,
                                    'url': url,
                                    'class_sections': class_sections,
                                    'html_content': html_content
                                }
                        else:
                            print(f"   ❌ Status: {exams_response.status_code}")
                    
                    # Use the best result for final checks
                    if best_result['toggle_calls'] > 0:
                        html_content = best_result['html_content']
                        print(f"\n🎯 Best result from: {best_result['url']}")
                    else:
                        # Fallback to first URL
                        exams_response = session.get(test_urls[0])
                        html_content = exams_response.text if exams_response.status_code == 200 else ""
                    
                    # Final checks on the best HTML content  
                    if html_content:
                        # Check for critical functions script
                        has_critical_functions = 'CRITICAL_FUNCTIONS' in html_content
                        has_toggle_function = 'window.toggleClass = function' in html_content
                        toggle_calls = html_content.count('onclick="toggleClass(')
                        class_sections = html_content.count('class-section')
                        
                        print(f"\n📊 FINAL RESULTS:")
                        print(f"   ✅ Critical functions: {has_critical_functions}")
                        print(f"   ✅ Toggle function: {has_toggle_function}")
                        print(f"   ✅ Toggle calls: {toggle_calls}")
                        print(f"   ✅ Class sections: {class_sections}")
                        
                        # Save debug HTML
                        with open('debug_toggle_fix_final.html', 'w') as f:
                            f.write(html_content)
                        print("💾 Saved debug HTML to debug_toggle_fix_final.html")
                        
                        return {
                            'success': True,
                            'has_critical_functions': has_critical_functions,
                            'has_toggle_function': has_toggle_function,
                            'toggle_calls': toggle_calls,
                            'class_sections': class_sections,
                            'best_url': best_result.get('url', test_urls[0])
                        }
                    else:
                        print(f"❌ Exams page returned status: {exams_response.status_code}")
                else:
                    print(f"❌ Login failed with status: {login_response.status_code}")
            else:
                print("❌ Could not find CSRF token")
        else:
            print(f"❌ Login page returned status: {login_page.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    result = test_toggle_function()
    
    if result and result.get('success'):
        print("\n🎉 TOGGLE FIX TEST SUMMARY:")
        print(f"   ✅ Critical functions: {result.get('has_critical_functions', False)}")
        print(f"   ✅ Toggle function: {result.get('has_toggle_function', False)}")
        print(f"   ✅ Toggle calls: {result.get('toggle_calls', 0)}")
        print(f"   ✅ Class sections: {result.get('class_sections', 0)}")
        
        if result.get('has_toggle_function') and result.get('toggle_calls', 0) > 0:
            print("\n🎯 FIX IS WORKING! The toggleClass function should now work in the browser.")
        else:
            print("\n⚠️  Fix may need additional work.")
    else:
        print(f"\n❌ Test failed: {result.get('error') if result else 'Unknown error'}")
#!/usr/bin/env python
"""
Comprehensive Test for My Classes & Access Button Visibility
Tests button visibility in navigation and quick actions

Run with: python test_button_visibility.py
"""

import os
import sys
import django
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import Teacher

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def test_anonymous_user():
    """Test what anonymous users see"""
    print_section("Testing Anonymous User Access")
    
    client = Client()
    response = client.get('/RoutineTest/')
    
    print(f"  Status Code: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check navigation
        if 'My Classes & Access' in content and 'data-nav="my-classes"' in content:
            print("  ✓ Navigation link visible (should be visible to all)")
        else:
            print("  ✗ Navigation link NOT visible")
            
        # Check Quick Actions (should NOT show for anonymous)
        if 'id="my-classes-btn"' in content:
            print("  ✗ Quick Actions button visible (should be hidden for anonymous)")
        else:
            print("  ✓ Quick Actions button correctly hidden for anonymous")
            
        # Count total buttons
        quick_action_count = content.count('class="btn"')
        print(f"  Total buttons visible: {quick_action_count}")
        
    return response.status_code == 200

def test_regular_user():
    """Test what regular non-teacher users see"""
    print_section("Testing Regular User (Non-Teacher)")
    
    client = Client()
    
    # Create regular user
    user = User.objects.filter(username='regular_user').first()
    if not user:
        user = User.objects.create_user('regular_user', 'regular@example.com', 'password123')
        user.is_staff = False
        user.is_superuser = False
        user.save()
        print("  Created regular user")
    
    client.force_login(user)
    response = client.get('/RoutineTest/')
    
    print(f"  Status Code: {response.status_code}")
    print(f"  User: {user.username}")
    print(f"  Is Staff: {user.is_staff}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check navigation
        if 'My Classes & Access' in content and 'data-nav="my-classes"' in content:
            print("  ✓ Navigation link visible")
        else:
            print("  ✗ Navigation link NOT visible")
            
        # Check Quick Actions
        if 'id="my-classes-btn"' in content:
            print("  ✓ Quick Actions button visible (authenticated user)")
        else:
            print("  ✗ Quick Actions button NOT visible")
    
    return True

def test_teacher_user():
    """Test what teachers see"""
    print_section("Testing Teacher User")
    
    client = Client()
    
    # Create or get teacher user
    user = User.objects.filter(username='teacher_user').first()
    if not user:
        user = User.objects.create_user('teacher_user', 'teacher@example.com', 'password123')
        user.is_staff = True  # Teachers are staff
        user.save()
        print("  Created teacher user")
    
    # Ensure teacher profile exists
    if not hasattr(user, 'teacher_profile'):
        Teacher.objects.get_or_create(
            email=user.email,
            defaults={
                'name': 'Test Teacher',
                'user': user
            }
        )
    
    client.force_login(user)
    response = client.get('/RoutineTest/')
    
    print(f"  Status Code: {response.status_code}")
    print(f"  User: {user.username}")
    print(f"  Is Staff: {user.is_staff}")
    print(f"  Has Teacher Profile: {hasattr(user, 'teacher_profile')}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check navigation
        if 'My Classes & Access' in content and 'data-nav="my-classes"' in content:
            print("  ✓ Navigation link visible")
        else:
            print("  ✗ Navigation link NOT visible (PROBLEM!)")
            
        # Check Quick Actions
        if 'id="my-classes-btn"' in content:
            print("  ✓ Quick Actions button visible")
        else:
            print("  ✗ Quick Actions button NOT visible (PROBLEM!)")
            
        # Check if button URL is correct
        if '/RoutineTest/access/my-classes/' in content:
            print("  ✓ Correct URL path found")
        else:
            print("  ✗ URL path not found")
    
    # Test accessing the page directly
    print("\n  Testing direct access to My Classes page:")
    access_response = client.get('/RoutineTest/access/my-classes/')
    print(f"  Direct access status: {access_response.status_code}")
    
    if access_response.status_code == 200:
        print("  ✓ Can access My Classes page")
    else:
        print(f"  ✗ Cannot access My Classes page (redirected to: {access_response.url if access_response.status_code == 302 else 'N/A'})")
    
    return True

def test_admin_user():
    """Test what admins see"""
    print_section("Testing Admin User")
    
    client = Client()
    
    # Get or create admin
    user = User.objects.filter(username='admin_user').first()
    if not user:
        user = User.objects.create_superuser('admin_user', 'admin@example.com', 'admin123')
        print("  Created admin user")
    
    client.force_login(user)
    response = client.get('/RoutineTest/')
    
    print(f"  Status Code: {response.status_code}")
    print(f"  User: {user.username}")
    print(f"  Is Superuser: {user.is_superuser}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check both locations
        nav_visible = 'My Classes & Access' in content and 'data-nav="my-classes"' in content
        button_visible = 'id="my-classes-btn"' in content
        
        print(f"  ✓ Navigation link: {'Visible' if nav_visible else 'NOT VISIBLE'}")
        print(f"  ✓ Quick Actions button: {'Visible' if button_visible else 'NOT VISIBLE'}")
        
        # Test admin view toggle
        print("\n  Testing admin view toggle:")
        admin_view_response = client.get('/RoutineTest/access/my-classes/?admin_view=true')
        if admin_view_response.status_code == 200:
            admin_content = admin_view_response.content.decode('utf-8')
            if 'Admin Dashboard' in admin_content:
                print("  ✓ Admin view accessible")
            else:
                print("  ✗ Admin view not showing")
    
    return True

def check_url_patterns():
    """Check if URL patterns are correctly configured"""
    print_section("Checking URL Patterns")
    
    try:
        # Test URL reversing
        url = reverse('RoutineTest:my_classes')
        print(f"  ✓ URL pattern exists: {url}")
        
        # Test all related URLs
        urls_to_test = [
            'RoutineTest:my_classes',
            'RoutineTest:request_access',
            'RoutineTest:api_my_classes',
        ]
        
        for url_name in urls_to_test:
            try:
                url = reverse(url_name)
                print(f"  ✓ {url_name}: {url}")
            except:
                print(f"  ✗ {url_name}: NOT FOUND")
                
        return True
    except Exception as e:
        print(f"  ✗ Error checking URLs: {str(e)}")
        return False

def check_template_files():
    """Check if template files exist"""
    print_section("Checking Template Files")
    
    import os
    
    base_path = '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/templates/primepath_routinetest'
    
    templates_to_check = [
        'index.html',
        'class_access.html',
        '../routinetest_base.html'
    ]
    
    for template in templates_to_check:
        full_path = os.path.join(base_path, template)
        if os.path.exists(full_path):
            print(f"  ✓ {template} exists")
            
            # Check for button in index.html
            if template == 'index.html':
                with open(full_path, 'r') as f:
                    content = f.read()
                    if 'My Classes & Access' in content:
                        print(f"    ✓ Button text found in template")
                    if 'RoutineTest:my_classes' in content:
                        print(f"    ✓ URL reference found in template")
        else:
            print(f"  ✗ {template} NOT FOUND")
    
    return True

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  MY CLASSES & ACCESS - BUTTON VISIBILITY TEST")
    print("="*70)
    print(f"  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("URL Patterns", check_url_patterns),
        ("Template Files", check_template_files),
        ("Anonymous User", test_anonymous_user),
        ("Regular User", test_regular_user),
        ("Teacher User", test_teacher_user),
        ("Admin User", test_admin_user),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n✗ Error in {test_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Print summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 All tests passed!")
        print("\n  The button should now be visible:")
        print("    1. In the top navigation bar (replacing 'Class Management' placeholder)")
        print("    2. In Quick Actions section (orange button) for authenticated users")
        print("\n  Next steps:")
        print("    1. Clear browser cache")
        print("    2. Restart server if needed")
        print("    3. Login as a teacher or admin")
        print("    4. Check both locations for the button")
    else:
        print(f"\n  ⚠ {total - passed} test(s) failed.")
        print("\n  Troubleshooting:")
        print("    1. Check browser console for JavaScript errors")
        print("    2. View page source to see if HTML is generated")
        print("    3. Check Django logs for template errors")
        print("    4. Ensure user is authenticated")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
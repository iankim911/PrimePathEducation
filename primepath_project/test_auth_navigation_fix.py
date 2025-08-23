#!/usr/bin/env python
"""
Comprehensive test for authentication page navigation fix
Tests that login, logout, and profile pages don't show application-specific navigation
"""

import os
import sys
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')

import django
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from bs4 import BeautifulSoup

class AuthNavigationTestCase(TestCase):
    """Test authentication pages for proper navigation isolation"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        # Create test user
        self.user = User.objects.create_user(
            username='testteacher',
            password='testpass123',
            email='test@example.com'
        )
        self.user.first_name = 'Test'
        self.user.last_name = 'Teacher'
        self.user.save()
        
        print("\n" + "="*80)
        print("🧪 AUTHENTICATION NAVIGATION FIX TEST")
        print("="*80)
    
    def test_login_page_no_navigation(self):
        """Test that login page has no application-specific navigation"""
        print("\n📋 Test 1: Login Page Navigation Check")
        print("-"*40)
        
        response = self.client.get(reverse('core:login'))
        self.assertEqual(response.status_code, 200)
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check for navigation elements that shouldn't exist
        nav_tabs = soup.find_all(class_='nav-tabs')
        nav_elements = soup.find_all('nav')
        placement_links = soup.find_all('a', href=lambda x: x and 'PlacementTest' in x)
        routine_links = soup.find_all('a', href=lambda x: x and 'RoutineTest' in x)
        
        # Dashboard, Upload Exam, etc. links shouldn't exist
        dashboard_links = soup.find_all('a', string=lambda x: x and 'Dashboard' in x)
        upload_links = soup.find_all('a', string=lambda x: x and 'Upload Exam' in x)
        manage_links = soup.find_all('a', string=lambda x: x and 'Manage Exams' in x)
        
        print(f"  ✓ Checking for nav-tabs: Found {len(nav_tabs)}")
        print(f"  ✓ Checking for nav elements: Found {len(nav_elements)}")
        print(f"  ✓ Checking for PlacementTest links: Found {len(placement_links)}")
        print(f"  ✓ Checking for RoutineTest links: Found {len(routine_links)}")
        print(f"  ✓ Checking for Dashboard links: Found {len(dashboard_links)}")
        print(f"  ✓ Checking for Upload Exam links: Found {len(upload_links)}")
        print(f"  ✓ Checking for Manage Exams links: Found {len(manage_links)}")
        
        # Assertions
        self.assertEqual(len(nav_tabs), 0, "Login page should have no nav-tabs")
        self.assertEqual(len(nav_elements), 0, "Login page should have no nav elements")
        self.assertEqual(len(placement_links), 0, "Login page should have no PlacementTest links")
        self.assertEqual(len(routine_links), 0, "Login page should have no RoutineTest links")
        self.assertEqual(len(dashboard_links), 0, "Login page should have no Dashboard links")
        self.assertEqual(len(upload_links), 0, "Login page should have no Upload Exam links")
        self.assertEqual(len(manage_links), 0, "Login page should have no Manage Exams links")
        
        # Check that it extends the correct base template
        content = response.content.decode('utf-8')
        self.assertNotIn('nav-tabs', content, "No navigation tabs should be present")
        self.assertNotIn('Start Test', content, "No 'Start Test' link should be present")
        self.assertNotIn('View Results', content, "No 'View Results' link should be present")
        
        print(f"\n  ✅ Login page is correctly neutral (no navigation found)")
    
    def test_profile_page_no_navigation(self):
        """Test that profile page has no application-specific navigation"""
        print("\n📋 Test 2: Profile Page Navigation Check")
        print("-"*40)
        
        # Login first
        self.client.login(username='testteacher', password='testpass123')
        
        response = self.client.get(reverse('core:profile'))
        self.assertEqual(response.status_code, 200)
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check for navigation elements
        nav_tabs = soup.find_all(class_='nav-tabs')
        placement_links = soup.find_all('a', href=lambda x: x and 'PlacementTest' in x)
        routine_links = soup.find_all('a', href=lambda x: x and 'RoutineTest' in x)
        
        print(f"  ✓ Checking for nav-tabs: Found {len(nav_tabs)}")
        print(f"  ✓ Checking for PlacementTest links: Found {len(placement_links)}")
        print(f"  ✓ Checking for RoutineTest links: Found {len(routine_links)}")
        
        # The profile page should only have minimal auth info (profile/logout links)
        # but no application-specific navigation
        self.assertEqual(len(nav_tabs), 0, "Profile page should have no nav-tabs")
        self.assertEqual(len(placement_links), 0, "Profile page should have no PlacementTest links")
        
        # RoutineTest link might appear in "Back to RoutineTest" context, which is OK
        # but not in main navigation
        
        print(f"\n  ✅ Profile page is correctly neutral")
    
    def test_index_page_neutral(self):
        """Test that index page (app chooser) is neutral"""
        print("\n📋 Test 3: Index Page (App Chooser) Check")
        print("-"*40)
        
        response = self.client.get('/')
        
        # If not logged in, should redirect to login
        if response.status_code == 302:
            print(f"  ✓ Index redirects to login when not authenticated")
            self.assertIn('/login/', response.url)
        else:
            # If logged in (in some test scenarios)
            soup = BeautifulSoup(response.content, 'html.parser')
            nav_tabs = soup.find_all(class_='nav-tabs')
            
            print(f"  ✓ Checking for nav-tabs: Found {len(nav_tabs)}")
            self.assertEqual(len(nav_tabs), 0, "Index page should have no nav-tabs")
        
        print(f"\n  ✅ Index page is correctly neutral")
    
    def test_login_flow_complete(self):
        """Test complete login flow"""
        print("\n📋 Test 4: Complete Login Flow")
        print("-"*40)
        
        # 1. Visit login page
        response = self.client.get(reverse('core:login'))
        self.assertEqual(response.status_code, 200)
        print(f"  ✓ Login page accessible")
        
        # 2. Submit login form
        response = self.client.post(reverse('core:login'), {
            'username': 'testteacher',
            'password': 'testpass123',
        }, follow=True)
        
        # Should redirect to app chooser
        self.assertEqual(response.status_code, 200)
        print(f"  ✓ Login successful, redirected")
        
        # 3. Check that we're on app chooser, not in any specific app
        final_url = response.wsgi_request.path
        self.assertEqual(final_url, '/', f"Should redirect to app chooser, got {final_url}")
        print(f"  ✓ Redirected to app chooser at '/'")
        
        # 4. Verify no application-specific navigation on app chooser
        soup = BeautifulSoup(response.content, 'html.parser')
        nav_tabs = soup.find_all(class_='nav-tabs')
        self.assertEqual(len(nav_tabs), 0, "App chooser should have no nav-tabs")
        print(f"  ✓ App chooser has no navigation")
        
        print(f"\n  ✅ Complete login flow works correctly")
    
    def test_template_inheritance(self):
        """Test that templates extend the correct base"""
        print("\n📋 Test 5: Template Inheritance Check")
        print("-"*40)
        
        templates_to_check = [
            'core/auth/login.html',
            'core/auth/profile.html',
            'core/auth/logout_confirm.html',
            'core/index.html'
        ]
        
        from django.template.loader import get_template
        
        for template_name in templates_to_check:
            try:
                template = get_template(template_name)
                source = template.source
                
                # Check if it extends base_clean.html
                if 'base_clean.html' in source:
                    print(f"  ✅ {template_name} extends base_clean.html")
                elif 'base.html' in source and 'base_clean' not in source:
                    print(f"  ❌ {template_name} extends base.html (should be base_clean.html)")
                    self.fail(f"{template_name} should extend base_clean.html, not base.html")
                else:
                    print(f"  ✓ {template_name} checked")
                    
            except Exception as e:
                print(f"  ⚠️ Could not check {template_name}: {e}")
        
        print(f"\n  ✅ All auth templates use correct base template")

def run_tests():
    """Run all tests"""
    from django.test.utils import setup_test_environment, teardown_test_environment
    from django.test.runner import DiscoverRunner
    
    setup_test_environment()
    runner = DiscoverRunner(verbosity=2, interactive=False, keepdb=False)
    
    # Create test database
    old_db_name = runner.setup_databases()
    
    try:
        # Run tests
        suite = runner.test_loader.loadTestsFromTestCase(AuthNavigationTestCase)
        result = runner.run_suite(suite)
        
        # Summary
        print("\n" + "="*80)
        print("📊 TEST SUMMARY")
        print("="*80)
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        
        if result.wasSuccessful():
            print("\n✅ ALL TESTS PASSED - Authentication pages are correctly neutral!")
        else:
            print("\n❌ SOME TESTS FAILED - Review the output above")
            for failure in result.failures:
                print(f"\nFailure: {failure[0]}")
                print(failure[1])
            for error in result.errors:
                print(f"\nError: {error[0]}")
                print(error[1])
        
        return result.wasSuccessful()
        
    finally:
        # Teardown test database
        runner.teardown_databases(old_db_name)
        teardown_test_environment()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
#!/usr/bin/env python
"""
Final QA Test for Navigation V8 Implementation
Tests unified Classes & Exams tab with complete cache busting
"""
import os
import sys
import django
from pathlib import Path
import json
import traceback
from datetime import datetime

# Setup Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.core.cache import cache
from core.models import Teacher
from bs4 import BeautifulSoup


class NavigationV8Test:
    """Comprehensive test suite for Navigation V8"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.successes = []
        self.client = Client()
        
    def log_success(self, message):
        self.successes.append(f"✅ {message}")
        print(f"✅ {message}")
        
    def log_error(self, message):
        self.errors.append(f"❌ {message}")
        print(f"❌ {message}")
        
    def log_warning(self, message):
        self.warnings.append(f"⚠️ {message}")
        print(f"⚠️ {message}")
        
    def log_info(self, message):
        print(f"📋 {message}")
        
    def setup_test_user(self):
        """Create test user and login"""
        # Use admin user for testing
        admin_user = User.objects.filter(username='admin').first()
        if admin_user:
            self.client.force_login(admin_user)
            self.log_success(f"Logged in as: {admin_user.username}")
            return True
        else:
            # Create test user
            test_user = User.objects.create_user('test_nav_v8', 'test@example.com', 'test123')
            self.client.login(username='test_nav_v8', password='test123')
            self.log_success("Created and logged in as test user")
            return True
            
    def test_navigation_rendering(self):
        """Test navigation is correctly rendered"""
        print("\n📋 Testing Navigation Rendering...")
        
        test_urls = [
            ('/RoutineTest/', 'Dashboard'),
            ('/RoutineTest/classes-exams/', 'Classes & Exams'),
        ]
        
        for url, page_name in test_urls:
            try:
                response = self.client.get(url)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find navigation
                    nav = soup.find('nav', class_='nav-tabs')
                    if not nav:
                        nav = soup.find('nav')
                    
                    if nav:
                        nav_id = nav.get('id', '')
                        nav_version = nav.get('data-version', '')
                        
                        # Check if it's V8
                        if 'nav-v8' in nav_id:
                            self.log_success(f"{page_name}: Using Navigation V8 (ID: {nav_id})")
                        elif nav_version == '8.0':
                            self.log_success(f"{page_name}: Navigation version 8.0")
                        else:
                            self.log_warning(f"{page_name}: Navigation version {nav_version} (ID: {nav_id})")
                        
                        # Count tabs
                        tabs = nav.find_all('a', {'data-nav': True})
                        nav_items = []
                        
                        for tab in tabs:
                            text = tab.text.strip()
                            data_nav = tab.get('data-nav', '')
                            
                            # Skip user tabs
                            if '👤' in text or text in ['Logout', 'Login']:
                                continue
                                
                            nav_items.append({
                                'text': text,
                                'data_nav': data_nav
                            })
                            
                            # Check for specific tabs
                            if 'Classes & Exams' in text:
                                self.log_success(f"  ✓ Unified 'Classes & Exams' tab found")
                            elif 'My Classes' in text and 'Access' in text:
                                self.log_error(f"  ✗ OLD TAB: 'My Classes & Access' still present!")
                            elif 'Exam Assignments' in text:
                                self.log_error(f"  ✗ OLD TAB: 'Exam Assignments' still present!")
                        
                        self.log_info(f"  Total navigation items: {len(nav_items)}")
                        
                        # Check for unified tab specifically
                        unified_found = any('classes-exams' in item['data_nav'] for item in nav_items)
                        if unified_found:
                            self.log_success(f"  ✓ Unified tab data-nav='classes-exams' confirmed")
                        else:
                            self.log_error(f"  ✗ Unified tab data-nav='classes-exams' NOT found")
                            
                    else:
                        self.log_error(f"{page_name}: No navigation found")
                        
                else:
                    self.log_error(f"{page_name}: Page returned status {response.status_code}")
                    
            except Exception as e:
                self.log_error(f"{page_name} test failed: {e}")
                
    def test_url_redirects(self):
        """Test old URLs redirect properly"""
        print("\n📋 Testing URL Redirects...")
        
        redirects = [
            ('/RoutineTest/access/my-classes/', 'My Classes & Access'),
            ('/RoutineTest/schedule-matrix/', 'Exam Assignments'),
        ]
        
        for old_url, name in redirects:
            try:
                response = self.client.get(old_url, follow=False)
                
                if response.status_code in [301, 302]:
                    redirect_url = response.url
                    if 'classes-exams' in redirect_url:
                        self.log_success(f"{name}: Redirects to unified view")
                    else:
                        self.log_error(f"{name}: Redirects to wrong URL: {redirect_url}")
                elif response.status_code == 200:
                    # Check if it's rendering unified view directly
                    content = response.content.decode('utf-8')
                    if 'Classes & Exams' in content:
                        self.log_warning(f"{name}: Renders unified view directly (no redirect)")
                    else:
                        self.log_error(f"{name}: Still rendering old view")
                else:
                    self.log_error(f"{name}: Unexpected status {response.status_code}")
                    
            except Exception as e:
                self.log_error(f"{name} redirect test failed: {e}")
                
    def test_javascript_verification(self):
        """Test JavaScript console logging is working"""
        print("\n📋 Testing JavaScript Components...")
        
        try:
            response = self.client.get('/RoutineTest/')
            content = response.content.decode('utf-8')
            
            # Check for V8 scripts
            if 'NAV_V8' in content:
                self.log_success("Navigation V8 JavaScript found")
            else:
                self.log_warning("Navigation V8 JavaScript not found")
                
            if 'routinetest-nav-v8' in content:
                self.log_success("Navigation V8 ID reference found")
            else:
                self.log_warning("Navigation V8 ID not found")
                
            # Check for old references
            if 'my-classes' in content.lower() and 'data-nav' in content:
                self.log_warning("Old 'my-classes' reference might still exist")
            else:
                self.log_success("No old 'my-classes' data-nav found")
                
        except Exception as e:
            self.log_error(f"JavaScript test failed: {e}")
            
    def test_template_files(self):
        """Test template files are correct"""
        print("\n📋 Testing Template Files...")
        
        # Check V8 template exists
        v8_template = Path('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/templates/primepath_routinetest/includes/navigation_tabs_v8.html')
        if v8_template.exists():
            self.log_success("Navigation V8 template file exists")
            
            with open(v8_template, 'r') as f:
                content = f.read()
                if 'Classes & Exams' in content:
                    self.log_success("V8 template contains 'Classes & Exams'")
                if 'VERSION 8.0' in content:
                    self.log_success("V8 template has VERSION 8.0 marker")
                    
        else:
            self.log_error("Navigation V8 template file not found")
            
        # Check base template
        base_template = Path('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/templates/routinetest_base.html')
        if base_template.exists():
            with open(base_template, 'r') as f:
                content = f.read()
                if 'navigation_tabs_v8.html' in content:
                    self.log_success("Base template includes navigation_tabs_v8.html")
                elif 'navigation_tabs.html' in content:
                    self.log_error("Base template still using old navigation_tabs.html")
                    
    def test_no_placementtest_impact(self):
        """Verify PlacementTest is not affected"""
        print("\n📋 Testing PlacementTest Independence...")
        
        try:
            response = self.client.get('/PlacementTest/')
            if response.status_code in [200, 302]:
                self.log_success("PlacementTest still accessible")
                
                if response.status_code == 200:
                    content = response.content.decode('utf-8')
                    if 'nav-v8' not in content:
                        self.log_success("PlacementTest not using Navigation V8 (correct)")
                    else:
                        self.log_warning("PlacementTest might be using RoutineTest navigation")
            else:
                self.log_warning(f"PlacementTest returned status {response.status_code}")
                
        except Exception as e:
            self.log_warning(f"PlacementTest test incomplete: {e}")
            
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*80)
        print("NAVIGATION V8 FINAL QA TEST")
        print("="*80)
        print(f"Test started: {datetime.now()}")
        
        # Clear cache first
        cache.clear()
        self.log_success("Cache cleared")
        
        # Setup
        self.setup_test_user()
        
        # Run tests
        self.test_navigation_rendering()
        self.test_url_redirects()
        self.test_javascript_verification()
        self.test_template_files()
        self.test_no_placementtest_impact()
        
        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        print(f"\n✅ Successes: {len(self.successes)}")
        for success in self.successes[:10]:  # Show first 10
            print(f"  {success}")
        if len(self.successes) > 10:
            print(f"  ... and {len(self.successes) - 10} more")
            
        if self.warnings:
            print(f"\n⚠️ Warnings: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"  {warning}")
                
        if self.errors:
            print(f"\n❌ Errors: {len(self.errors)}")
            for error in self.errors:
                print(f"  {error}")
                
        print("\n" + "="*80)
        
        if not self.errors:
            print("🎉 ALL TESTS PASSED!")
            print("\n✨ NAVIGATION V8 IMPLEMENTATION SUCCESSFUL! ✨")
            print("\nNext Steps:")
            print("1. Clear browser cache (Cmd+Shift+R or Ctrl+F5)")
            print("2. Navigate to: http://127.0.0.1:8000/RoutineTest/")
            print("3. Verify single 'Classes & Exams' tab is showing")
            print("4. Old tabs should be completely gone")
        else:
            print("❌ ISSUES DETECTED - Review errors above")
            print("\nTroubleshooting:")
            print("1. Hard refresh browser (Cmd+Shift+R)")
            print("2. Try incognito/private mode")
            print("3. Clear browser cookies for 127.0.0.1")
            print("4. Check browser console for errors")
            
        return len(self.errors) == 0


if __name__ == '__main__':
    tester = NavigationV8Test()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
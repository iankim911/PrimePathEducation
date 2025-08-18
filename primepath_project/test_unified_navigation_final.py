#!/usr/bin/env python
"""
FINAL TEST - Unified Classes & Exams Navigation
Tests the complete merger of My Classes & Access with Exam Assignments
Version 7.0
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
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.management import call_command
from core.models import Teacher
from primepath_routinetest.models import TeacherClassAssignment
from bs4 import BeautifulSoup


class UnifiedNavigationFinalTest:
    """Final test suite for unified navigation implementation"""
    
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
        
    def clear_caches(self):
        """Clear all caches"""
        print("\n🔄 Clearing all caches...")
        
        # Clear Django cache
        cache.clear()
        self.log_success("Django cache cleared")
        
        # Force template recompilation by touching files
        template_dir = Path('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/templates/primepath_routinetest')
        if template_dir.exists():
            for template in template_dir.glob('**/*.html'):
                template.touch()
            self.log_success(f"Touched {len(list(template_dir.glob('**/*.html')))} template files")
        
        # Clear Python cache
        try:
            cache_dirs = Path('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project').glob('**/__pycache__')
            count = 0
            for cache_dir in cache_dirs:
                if cache_dir.exists():
                    for pyc in cache_dir.glob('*.pyc'):
                        pyc.unlink()
                        count += 1
            self.log_success(f"Removed {count} .pyc files")
        except Exception as e:
            self.log_warning(f"Could not clear all Python cache: {e}")
            
    def setup_test_user(self):
        """Create test user and login"""
        # Create or get test user
        self.user = User.objects.filter(username='nav_test_v7').first()
        if not self.user:
            self.user = User.objects.create_user('nav_test_v7', 'nav_test_v7@example.com', 'test123')
            
        # Create teacher profile
        try:
            self.teacher = Teacher.objects.get(user=self.user)
        except Teacher.DoesNotExist:
            self.teacher = Teacher.objects.create(
                user=self.user,
                name='Nav Test Teacher V7',
                email=f'nav_test_v7_{self.user.id}@example.com',
                is_head_teacher=False
            )
        
        # Login
        self.client.login(username='nav_test_v7', password='test123')
        self.log_success("Test user created and logged in")
        
    def test_url_redirects(self):
        """Test that old URLs redirect to unified view"""
        print("\n📋 Testing URL Redirects...")
        
        test_urls = [
            ('/RoutineTest/access/my-classes/', 'My Classes & Access'),
            ('/RoutineTest/schedule-matrix/', 'Exam Assignments'),
        ]
        
        for url, name in test_urls:
            try:
                response = self.client.get(url, follow=False)
                
                if response.status_code in [301, 302]:
                    redirect_url = response.url
                    self.log_success(f"{name} URL redirects (status: {response.status_code})")
                    self.log_info(f"  Redirects to: {redirect_url}")
                    
                    # Check if it redirects to unified view
                    if 'classes-exams' in redirect_url:
                        self.log_success(f"  ✓ Redirects to unified view correctly")
                    else:
                        self.log_error(f"  ✗ Redirects to wrong URL: {redirect_url}")
                        
                elif response.status_code == 200:
                    # Check if it's rendering the unified view directly
                    content = response.content.decode('utf-8')
                    if 'Classes & Exams' in content and 'classes-exams' in content:
                        self.log_warning(f"{name} renders unified view directly (no redirect)")
                    else:
                        self.log_error(f"{name} still rendering old view!")
                        
                        # Check what navigation it's showing
                        soup = BeautifulSoup(content, 'html.parser')
                        nav_tabs = soup.find_all('a', {'data-nav': True})
                        self.log_info(f"  Navigation tabs found: {[tab.text.strip() for tab in nav_tabs]}")
                        
                else:
                    self.log_error(f"{name} returned unexpected status: {response.status_code}")
                    
            except Exception as e:
                self.log_error(f"{name} test failed: {e}")
                traceback.print_exc()
                
    def test_unified_url(self):
        """Test that unified URL works"""
        print("\n📋 Testing Unified URL...")
        
        try:
            url = '/RoutineTest/classes-exams/'
            response = self.client.get(url)
            
            if response.status_code == 200:
                self.log_success(f"Unified URL accessible (status: 200)")
                
                content = response.content.decode('utf-8')
                
                # Check for key elements
                checks = [
                    ('Classes & Exams', 'Unified title'),
                    ('overview-section', 'Overview section'),
                    ('classes-section', 'Classes section'),
                    ('exam_stats', 'Exam statistics'),
                ]
                
                for check_text, description in checks:
                    if check_text in content:
                        self.log_success(f"  ✓ {description} found")
                    else:
                        self.log_warning(f"  ⚠ {description} not found")
                        
            else:
                self.log_error(f"Unified URL returned status {response.status_code}")
                
        except Exception as e:
            self.log_error(f"Unified URL test failed: {e}")
            
    def test_navigation_structure(self):
        """Test navigation has correct tabs"""
        print("\n📋 Testing Navigation Structure...")
        
        try:
            # Test on unified URL
            response = self.client.get('/RoutineTest/classes-exams/')
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find navigation
                nav = soup.find('nav', class_='nav-tabs')
                if not nav:
                    nav = soup.find('nav', id=lambda x: x and 'nav' in x)
                    
                if nav:
                    self.log_success("Navigation found")
                    
                    # Get all tabs
                    tabs = nav.find_all('a')
                    tab_info = []
                    
                    for tab in tabs:
                        text = tab.text.strip()
                        href = tab.get('href', '')
                        data_nav = tab.get('data-nav', '')
                        
                        if text and text not in ['👤 nav_test_v7', 'Logout']:
                            tab_info.append({
                                'text': text,
                                'href': href,
                                'data_nav': data_nav
                            })
                    
                    # Log found tabs
                    self.log_info("Found navigation tabs:")
                    for i, tab in enumerate(tab_info, 1):
                        self.log_info(f"  {i}. {tab['text']} → {tab['data_nav']} ({tab['href']})")
                    
                    # Check for unified tab
                    unified_found = False
                    old_tabs_found = []
                    
                    for tab in tab_info:
                        if 'Classes & Exams' in tab['text'] or tab['data_nav'] == 'classes-exams':
                            unified_found = True
                            self.log_success("✓ Unified 'Classes & Exams' tab found")
                            
                        if 'My Classes & Access' in tab['text'] or tab['data_nav'] == 'my-classes':
                            old_tabs_found.append('My Classes & Access')
                            
                        if 'Exam Assignments' in tab['text'] or tab['data_nav'] == 'exam-assignments':
                            old_tabs_found.append('Exam Assignments')
                    
                    if not unified_found:
                        self.log_error("✗ Unified 'Classes & Exams' tab NOT found!")
                        
                    if old_tabs_found:
                        self.log_error(f"✗ Old tabs still present: {old_tabs_found}")
                    else:
                        self.log_success("✓ Old tabs successfully removed")
                        
                else:
                    self.log_error("Navigation element not found in HTML")
                    
            else:
                self.log_error(f"Page returned status {response.status_code}")
                
        except Exception as e:
            self.log_error(f"Navigation test failed: {e}")
            traceback.print_exc()
            
    def test_url_patterns(self):
        """Test URL pattern registration"""
        print("\n📋 Testing URL Pattern Registration...")
        
        try:
            # Test new unified URL
            url = reverse('RoutineTest:classes_exams_unified')
            self.log_success(f"Unified URL resolves: {url}")
            
            # Test URL resolution
            resolver = resolve('/RoutineTest/classes-exams/')
            self.log_info(f"  View name: {resolver.view_name}")
            self.log_info(f"  View function: {resolver.func.__name__ if hasattr(resolver.func, '__name__') else resolver.func}")
            
            # Try to resolve old URLs
            old_urls = [
                '/RoutineTest/access/my-classes/',
                '/RoutineTest/schedule-matrix/'
            ]
            
            for old_url in old_urls:
                try:
                    resolver = resolve(old_url)
                    view_name = resolver.func.__name__ if hasattr(resolver.func, '__name__') else str(resolver.func)
                    
                    if 'redirect' in view_name.lower():
                        self.log_success(f"Old URL {old_url} → redirect function")
                    else:
                        self.log_warning(f"Old URL {old_url} → {view_name} (should be redirect)")
                        
                except Exception as e:
                    self.log_error(f"Could not resolve {old_url}: {e}")
                    
        except Exception as e:
            self.log_error(f"URL pattern test failed: {e}")
            
    def test_template_rendering(self):
        """Test which templates are being used"""
        print("\n📋 Testing Template Rendering...")
        
        try:
            # Force template debug mode
            from django.conf import settings
            old_debug = settings.TEMPLATES[0].get('OPTIONS', {}).get('debug', False)
            settings.TEMPLATES[0]['OPTIONS']['debug'] = True
            
            response = self.client.get('/RoutineTest/classes-exams/')
            
            if hasattr(response, 'templates') and response.templates:
                self.log_info("Templates used:")
                for template in response.templates:
                    if hasattr(template, 'name'):
                        self.log_info(f"  - {template.name}")
                        
                # Check for expected template
                template_names = [t.name for t in response.templates if hasattr(t, 'name')]
                if 'primepath_routinetest/classes_exams_unified.html' in template_names:
                    self.log_success("✓ Unified template being used")
                else:
                    self.log_warning("⚠ Unified template not in template list")
                    
            # Restore debug setting
            settings.TEMPLATES[0]['OPTIONS']['debug'] = old_debug
            
        except Exception as e:
            self.log_warning(f"Template test incomplete: {e}")
            
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*80)
        print("UNIFIED NAVIGATION FINAL TEST - VERSION 7.0")
        print("="*80)
        print(f"Test started: {datetime.now()}")
        
        # Clear caches first
        self.clear_caches()
        
        # Setup
        self.setup_test_user()
        
        # Run tests
        self.test_url_patterns()
        self.test_url_redirects()
        self.test_unified_url()
        self.test_navigation_structure()
        self.test_template_rendering()
        
        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        print(f"\n✅ Successes: {len(self.successes)}")
        for success in self.successes:
            print(f"  {success}")
            
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
            print("🎉 ALL CRITICAL TESTS PASSED!")
            print("\n✨ UNIFIED NAVIGATION IMPLEMENTATION SUCCESSFUL! ✨")
            print("\nNext Steps:")
            print("1. Restart Django server to ensure all changes take effect")
            print("2. Clear browser cache completely")
            print("3. Navigate to: /RoutineTest/classes-exams/")
            print("4. Verify single unified tab showing 'Classes & Exams'")
            print("5. Test old URLs redirect properly")
        else:
            print("❌ ISSUES DETECTED - Review errors above")
            print("\nTroubleshooting:")
            print("1. Restart Django server")
            print("2. Clear browser cache and cookies")
            print("3. Check server console for redirect logs")
            print("4. Try incognito/private browsing mode")
            
        return len(self.errors) == 0


if __name__ == '__main__':
    tester = UnifiedNavigationFinalTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
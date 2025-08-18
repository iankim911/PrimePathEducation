#!/usr/bin/env python
"""
Comprehensive QA Test for Unified Classes & Exams
Tests the merger of My Classes & Access with Exam Assignments
"""
import os
import sys
import django
from pathlib import Path
import json
import traceback

# Setup Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from django.core.cache import cache
from core.models import Teacher
from primepath_routinetest.models import Exam, TeacherClassAssignment
from bs4 import BeautifulSoup


class UnifiedClassesExamsTest:
    """Test suite for unified Classes & Exams functionality"""
    
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
        
    def setup_test_user(self):
        """Create test user and teacher profile"""
        # Create or get test user
        self.user = User.objects.filter(username='unified_test').first()
        if not self.user:
            self.user = User.objects.create_user('unified_test', 'unified_test@example.com', 'test123')
            
        # Create teacher profile
        try:
            self.teacher = Teacher.objects.get(user=self.user)
        except Teacher.DoesNotExist:
            # Use unique email for this test
            self.teacher = Teacher.objects.create(
                user=self.user,
                name='Unified Test Teacher',
                email=f'unified_{self.user.id}@example.com',
                is_head_teacher=False
            )
        
        # Login
        self.client.login(username='unified_test', password='test123')
        self.log_success("Test user created and logged in")
        
    def test_url_patterns(self):
        """Test that new URLs are registered"""
        print("\n📋 Testing URL Patterns...")
        
        try:
            # Test new unified URL
            url = reverse('RoutineTest:classes_exams_unified')
            self.log_success(f"Unified URL resolved: {url}")
            
            # Check URL pattern
            resolver = resolve('/RoutineTest/classes-exams/')
            if resolver.view_name == 'RoutineTest:classes_exams_unified':
                self.log_success("URL pattern correctly mapped to unified view")
            else:
                self.log_error(f"URL mapped to wrong view: {resolver.view_name}")
                
        except Exception as e:
            self.log_error(f"URL pattern test failed: {e}")
            
    def test_unified_view_loads(self):
        """Test that unified view loads successfully"""
        print("\n📋 Testing Unified View...")
        
        try:
            response = self.client.get(reverse('RoutineTest:classes_exams_unified'))
            
            if response.status_code == 200:
                self.log_success(f"Unified view loaded successfully (status: {response.status_code})")
                
                # Check template used
                if 'classes_exams_unified.html' in [t.name for t in response.templates]:
                    self.log_success("Correct template used")
                else:
                    self.log_warning(f"Different template used: {response.templates}")
                    
                # Check context data
                if 'exam_stats' in response.context:
                    self.log_success("Exam statistics present in context")
                    stats = response.context['exam_stats']
                    self.log_success(f"  - Total exams: {stats.get('total_exams', 0)}")
                    self.log_success(f"  - Active exams: {stats.get('active_exams', 0)}")
                else:
                    self.log_warning("Exam statistics not in context")
                    
                if 'classes_info' in response.context:
                    self.log_success(f"Classes info present ({len(response.context['classes_info'])} classes)")
                else:
                    self.log_warning("Classes info not in context")
                    
            else:
                self.log_error(f"View returned status {response.status_code}")
                
        except Exception as e:
            self.log_error(f"View test failed: {e}")
            traceback.print_exc()
            
    def test_overview_dashboard(self):
        """Test that overview dashboard is present"""
        print("\n📋 Testing Overview Dashboard...")
        
        try:
            response = self.client.get(reverse('RoutineTest:classes_exams_unified'))
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Check for overview section
                overview = soup.find(class_='overview-section')
                if overview:
                    self.log_success("Overview section found")
                    
                    # Check for stats grid
                    stats_grid = soup.find(class_='stats-grid')
                    if stats_grid:
                        stat_cards = stats_grid.find_all(class_='stat-card')
                        self.log_success(f"Stats grid with {len(stat_cards)} stat cards")
                    else:
                        self.log_warning("Stats grid not found")
                        
                    # Check for recent activity
                    activity = soup.find(class_='recent-activity')
                    if activity:
                        self.log_success("Recent activity section found")
                    else:
                        self.log_warning("Recent activity section not found")
                        
                else:
                    self.log_error("Overview section not found in HTML")
                    
                # Check for classes section
                classes_section = soup.find(class_='classes-section')
                if classes_section:
                    self.log_success("Classes section found (scrollable below)")
                else:
                    self.log_error("Classes section not found")
                    
                # Check for matrix preview
                matrix_preview = soup.find(class_='matrix-preview')
                if matrix_preview:
                    self.log_success("Matrix preview section found")
                else:
                    self.log_warning("Matrix preview not found")
                    
            else:
                self.log_error(f"Page returned status {response.status_code}")
                
        except Exception as e:
            self.log_error(f"Dashboard test failed: {e}")
            
    def test_navigation_tabs(self):
        """Test that navigation shows unified tab"""
        print("\n📋 Testing Navigation Tabs...")
        
        try:
            response = self.client.get(reverse('RoutineTest:classes_exams_unified'))
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Check for nav tabs
                nav = soup.find(id='routinetest-nav-v6')
                if nav:
                    self.log_success("Navigation v6 found")
                    
                    # Check for unified tab
                    unified_tab = nav.find(id='unified-tab-v6')
                    if unified_tab:
                        self.log_success("Unified Classes & Exams tab found")
                        
                        # Check tab text
                        tab_link = unified_tab.find('a')
                        if tab_link and 'Classes & Exams' in tab_link.text:
                            self.log_success("Tab has correct text: Classes & Exams")
                        else:
                            self.log_warning(f"Tab text: {tab_link.text if tab_link else 'Not found'}")
                            
                    else:
                        self.log_error("Unified tab not found in navigation")
                        
                    # Check that old tabs are gone
                    old_classes = nav.find(attrs={'data-nav': 'classes'})
                    old_matrix = nav.find(attrs={'data-nav': 'matrix'})
                    
                    if not old_classes and not old_matrix:
                        self.log_success("Old separate tabs removed successfully")
                    else:
                        if old_classes:
                            self.log_error("Old 'My Classes & Access' tab still present")
                        if old_matrix:
                            self.log_error("Old 'Exam Assignments' tab still present")
                            
                else:
                    self.log_error("Navigation not found")
                    
        except Exception as e:
            self.log_error(f"Navigation test failed: {e}")
            
    def test_backward_compatibility(self):
        """Test that old URLs redirect properly"""
        print("\n📋 Testing Backward Compatibility...")
        
        # Note: Since we kept the old views, they should still work
        # but we can add redirects if needed
        
        try:
            # Test old my-classes URL
            old_url = '/RoutineTest/access/my-classes/'
            response = self.client.get(old_url, follow=False)
            
            # It should still work (we kept the old view)
            if response.status_code == 200:
                self.log_success(f"Old my-classes URL still works (compatibility maintained)")
            elif response.status_code in [301, 302]:
                self.log_success(f"Old my-classes URL redirects to unified view")
            else:
                self.log_warning(f"Old my-classes URL status: {response.status_code}")
                
            # Test old schedule-matrix URL
            old_matrix_url = '/RoutineTest/schedule-matrix/'
            response = self.client.get(old_matrix_url, follow=False)
            
            if response.status_code == 200:
                self.log_success(f"Old schedule-matrix URL still works (compatibility maintained)")
            elif response.status_code in [301, 302]:
                self.log_success(f"Old schedule-matrix URL redirects to unified view")
            else:
                self.log_warning(f"Old schedule-matrix URL status: {response.status_code}")
                
        except Exception as e:
            self.log_error(f"Backward compatibility test failed: {e}")
            
    def test_admin_access(self):
        """Test admin user access to unified view"""
        print("\n📋 Testing Admin Access...")
        
        # Create admin user
        admin = User.objects.filter(username='admin_unified').first()
        if not admin:
            admin = User.objects.create_superuser('admin_unified', 'admin@test.com', 'admin123')
            
        # Create teacher profile for admin
        admin_teacher, _ = Teacher.objects.get_or_create(
            user=admin,
            defaults={
                'name': 'Admin Teacher',
                'email': 'admin@test.com',
                'is_head_teacher': True
            }
        )
        
        # Login as admin
        self.client.login(username='admin_unified', password='admin123')
        
        try:
            response = self.client.get(reverse('RoutineTest:classes_exams_unified'))
            
            if response.status_code == 200:
                self.log_success("Admin can access unified view")
                
                # Check for admin indicator
                if response.context.get('is_admin'):
                    self.log_success("Admin status recognized")
                    
                if response.context.get('admin_all_access'):
                    self.log_success("Admin has all access flag")
                    
                # Check HTML for admin badge
                soup = BeautifulSoup(response.content, 'html.parser')
                admin_badge = soup.find(text=lambda t: 'ADMIN' in t if t else False)
                if admin_badge:
                    self.log_success("Admin badge displayed in UI")
                    
            else:
                self.log_error(f"Admin access returned status {response.status_code}")
                
        except Exception as e:
            self.log_error(f"Admin access test failed: {e}")
            
    def test_performance(self):
        """Test view performance"""
        print("\n📋 Testing Performance...")
        
        import time
        
        try:
            start_time = time.time()
            response = self.client.get(reverse('RoutineTest:classes_exams_unified'))
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.log_success(f"View loaded in {duration:.2f} seconds")
                
                if duration < 2:
                    self.log_success("Performance: Excellent (< 2s)")
                elif duration < 5:
                    self.log_warning(f"Performance: Acceptable ({duration:.2f}s)")
                else:
                    self.log_error(f"Performance: Poor ({duration:.2f}s)")
                    
                # Check if caching is used
                if 'render_time' in response.context:
                    self.log_success(f"Server render time: {response.context['render_time']}")
                    
        except Exception as e:
            self.log_error(f"Performance test failed: {e}")
            
    def test_console_logging(self):
        """Test that console logging is present"""
        print("\n📋 Testing Console Logging...")
        
        try:
            response = self.client.get(reverse('RoutineTest:classes_exams_unified'))
            
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                
                # Check for console.log statements
                if 'console.log' in content:
                    self.log_success("Console logging present")
                    
                    # Count console.log occurrences
                    log_count = content.count('console.log')
                    self.log_success(f"Found {log_count} console.log statements")
                    
                if 'console.group' in content:
                    self.log_success("Console grouping used for organization")
                    
                if '[UNIFIED_VIEW]' in content:
                    self.log_success("Unified view specific logging tags found")
                    
                if 'console.table' in content:
                    self.log_success("Console table used for structured data")
                    
            else:
                self.log_error(f"Page returned status {response.status_code}")
                
        except Exception as e:
            self.log_error(f"Console logging test failed: {e}")
            
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*70)
        print("UNIFIED CLASSES & EXAMS - COMPREHENSIVE QA TEST")
        print("="*70)
        
        # Clear cache before testing
        cache.clear()
        print("✅ Cache cleared")
        
        # Setup
        self.setup_test_user()
        
        # Run tests
        self.test_url_patterns()
        self.test_unified_view_loads()
        self.test_overview_dashboard()
        self.test_navigation_tabs()
        self.test_backward_compatibility()
        self.test_admin_access()
        self.test_performance()
        self.test_console_logging()
        
        # Summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
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
                
        print("\n" + "="*70)
        
        if not self.errors:
            print("🎉 ALL CRITICAL TESTS PASSED!")
            print("\n✨ UNIFIED CLASSES & EXAMS IMPLEMENTATION SUCCESSFUL! ✨")
            print("\nNext Steps:")
            print("1. Start Django server")
            print("2. Navigate to: /RoutineTest/classes-exams/")
            print("3. Verify:")
            print("   - Overview dashboard at top")
            print("   - Classes section below (scrollable)")
            print("   - Single unified tab in navigation")
            print("   - No separate 'My Classes' or 'Exam Assignments' tabs")
        else:
            print("❌ ISSUES DETECTED - Review errors above")
            
        return len(self.errors) == 0


if __name__ == '__main__':
    tester = UnifiedClassesExamsTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
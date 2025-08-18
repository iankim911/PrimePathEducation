#!/usr/bin/env python
"""
Comprehensive QA Test for Complete Roster Removal - Version 3.0
Tests all aspects of the Roster removal to ensure it's completely eliminated
"""
import os
import sys
import django
from pathlib import Path
import json
import importlib
import ast

# Setup Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from django.core.cache import cache
from core.models import Teacher
from primepath_routinetest.models import Exam
from bs4 import BeautifulSoup
import traceback

class RosterCompleteRemovalTestV3:
    """Comprehensive test suite for Roster removal verification"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.successes = []
        
    def log_success(self, message):
        self.successes.append(f"✅ {message}")
        print(f"✅ {message}")
        
    def log_error(self, message):
        self.errors.append(f"❌ {message}")
        print(f"❌ {message}")
        
    def log_warning(self, message):
        self.warnings.append(f"⚠️ {message}")
        print(f"⚠️ {message}")
        
    def test_model_exports(self):
        """Test that StudentRoster is not exported from models"""
        print("\n📋 Testing Model Exports...")
        
        try:
            from primepath_routinetest import models
            
            # Check __all__ exports
            if hasattr(models, '__all__'):
                if 'StudentRoster' in models.__all__:
                    self.log_error("StudentRoster still in models.__all__")
                else:
                    self.log_success("StudentRoster not in models.__all__")
            
            # Try to import StudentRoster
            try:
                from primepath_routinetest.models import StudentRoster
                self.log_warning("StudentRoster can still be imported (model exists but should not be used)")
            except ImportError:
                self.log_success("StudentRoster cannot be imported")
                
        except Exception as e:
            self.log_error(f"Model export test failed: {e}")
            
    def test_view_exports(self):
        """Test that roster views are not exported"""
        print("\n📋 Testing View Exports...")
        
        try:
            from primepath_routinetest import views
            
            # Check __all__ exports
            if hasattr(views, '__all__'):
                roster_exports = [v for v in views.__all__ if 'roster' in v.lower()]
                if roster_exports:
                    self.log_error(f"Roster views still exported: {roster_exports}")
                else:
                    self.log_success("No roster views in exports")
                    
            # Check if roster functions exist
            roster_funcs = ['manage_roster', 'import_roster_csv', 'roster_report']
            for func in roster_funcs:
                if hasattr(views, func):
                    self.log_error(f"View function '{func}' still accessible")
                else:
                    self.log_success(f"View function '{func}' not accessible")
                    
        except Exception as e:
            self.log_error(f"View export test failed: {e}")
            
    def test_url_patterns(self):
        """Test that no roster URLs are registered"""
        print("\n📋 Testing URL Patterns...")
        
        try:
            from primepath_routinetest import urls
            
            roster_patterns = []
            for pattern in urls.urlpatterns:
                if hasattr(pattern, 'name') and pattern.name:
                    if 'roster' in pattern.name.lower():
                        roster_patterns.append(pattern.name)
                        
            if roster_patterns:
                self.log_error(f"Roster URL patterns found: {roster_patterns}")
            else:
                self.log_success("No roster URL patterns registered")
                
            # Test if roster URLs resolve
            test_urls = [
                '/RoutineTest/exams/test-id/roster/',
                '/RoutineTest/roster/test-id/status/',
            ]
            
            for url in test_urls:
                try:
                    resolve(url)
                    self.log_error(f"Roster URL still resolves: {url}")
                except:
                    self.log_success(f"Roster URL does not resolve: {url}")
                    
        except Exception as e:
            self.log_error(f"URL pattern test failed: {e}")
            
    def test_template_content(self):
        """Test template for Roster references"""
        print("\n📋 Testing Template Content...")
        
        template_path = Path('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/templates/primepath_routinetest/exam_list.html')
        
        if template_path.exists():
            content = template_path.read_text()
            
            # Check for template version
            if 'Version 3.0' in content or 'VERSION 3.0' in content:
                self.log_success("Template has Version 3.0 marker")
            else:
                self.log_warning("Template missing Version 3.0 marker")
                
            # Check for Roster button in template
            if '<button' in content and 'Roster' in content:
                # More precise check
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'Roster' in line and not line.strip().startswith('{#') and not line.strip().startswith('<!--'):
                        if '<button' in line or '<a' in line:
                            self.log_error(f"Found Roster button at line {i+1}: {line.strip()[:80]}")
                            break
                else:
                    self.log_success("No active Roster buttons in template (only in comments)")
            else:
                self.log_success("No Roster buttons in template")
                
            # Check for roster URLs in template
            if 'manage_roster' in content or 'roster_report' in content:
                self.log_error("Template contains roster URL references")
            else:
                self.log_success("Template has no roster URL references")
                
        else:
            self.log_error(f"Template not found at {template_path}")
            
    def test_view_response(self):
        """Test the actual view response"""
        print("\n📋 Testing View Response...")
        
        client = Client()
        
        # Create test user
        user = User.objects.filter(username='qa_test').first()
        if not user:
            user = User.objects.create_user('qa_test', 'qa@test.com', 'test123')
            
        # Create teacher profile
        teacher, _ = Teacher.objects.get_or_create(
            user=user,
            defaults={'name': 'QA Test', 'email': 'qa@test.com'}
        )
        
        client.login(username='qa_test', password='test123')
        
        try:
            response = client.get(reverse('RoutineTest:exam_list'))
            
            # Check response headers
            if response.status_code == 200:
                self.log_success("Exam list page loads successfully")
                
                # Check cache headers
                if 'Cache-Control' in response:
                    if 'no-cache' in response['Cache-Control']:
                        self.log_success("Cache-Control header set to no-cache")
                    else:
                        self.log_warning(f"Cache-Control: {response['Cache-Control']}")
                        
                # Check custom headers
                if 'X-Template-Version' in response:
                    if '3.0' in response['X-Template-Version']:
                        self.log_success(f"X-Template-Version: {response['X-Template-Version']}")
                    else:
                        self.log_error(f"Wrong template version: {response['X-Template-Version']}")
                        
                if 'X-Roster-Status' in response:
                    self.log_success(f"X-Roster-Status: {response['X-Roster-Status']}")
                    
                # Parse HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Check for Roster buttons
                roster_elements = soup.find_all(text=lambda t: 'Roster' in t if t else False)
                roster_buttons = [elem for elem in roster_elements if elem.parent.name in ['button', 'a']]
                
                if roster_buttons:
                    self.log_error(f"Found {len(roster_buttons)} Roster buttons in response HTML")
                    for btn in roster_buttons[:2]:
                        self.log_error(f"  Button: {btn.strip()}")
                else:
                    self.log_success("No Roster buttons in response HTML")
                    
                # Check version banner
                version_banner = soup.find(id='template-version-banner')
                if version_banner:
                    if 'VERSION 3.0' in version_banner.text:
                        self.log_success("Version 3.0 banner present")
                    else:
                        self.log_warning("Version banner exists but wrong version")
                else:
                    self.log_warning("Version banner not found")
                    
            else:
                self.log_error(f"Page returned status {response.status_code}")
                
        except Exception as e:
            self.log_error(f"View response test failed: {e}")
            traceback.print_exc()
            
    def test_file_system(self):
        """Test that roster files are properly renamed/removed"""
        print("\n📋 Testing File System...")
        
        base_dir = Path('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/primepath_routinetest')
        
        # Check for roster view file
        roster_view = base_dir / 'views' / 'roster.py'
        if roster_view.exists():
            self.log_error(f"Roster view file still exists: {roster_view}")
        else:
            self.log_success("Roster view file removed/renamed")
            
        # Check for backup
        roster_backup = base_dir / 'views' / 'roster.py.removed_backup'
        if roster_backup.exists():
            self.log_success("Roster view backed up as .removed_backup")
            
        # Check for roster URLs file
        roster_urls = base_dir / 'roster_urls.py'
        if roster_urls.exists():
            self.log_error(f"Roster URLs file still exists: {roster_urls}")
        else:
            self.log_success("Roster URLs file removed/renamed")
            
    def test_cache_state(self):
        """Test cache is cleared"""
        print("\n📋 Testing Cache State...")
        
        try:
            # Clear Django cache
            cache.clear()
            self.log_success("Django cache cleared")
            
            # Check for __pycache__ directories
            import subprocess
            result = subprocess.run(
                ['find', '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project', 
                 '-type', 'd', '-name', '__pycache__'],
                capture_output=True, text=True
            )
            
            if result.stdout.strip():
                cache_dirs = result.stdout.strip().split('\n')
                self.log_warning(f"Found {len(cache_dirs)} __pycache__ directories")
            else:
                self.log_success("No __pycache__ directories found")
                
        except Exception as e:
            self.log_error(f"Cache test failed: {e}")
            
    def run_all_tests(self):
        """Run all tests and generate report"""
        print("\n" + "="*70)
        print("ROSTER COMPLETE REMOVAL TEST - VERSION 3.0")
        print("="*70)
        
        self.test_model_exports()
        self.test_view_exports()
        self.test_url_patterns()
        self.test_template_content()
        self.test_view_response()
        self.test_file_system()
        self.test_cache_state()
        
        # Generate report
        print("\n" + "="*70)
        print("TEST SUMMARY REPORT")
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
            print("🎉 ALL CRITICAL TESTS PASSED! ROSTER COMPLETELY REMOVED!")
            print("\nNEXT STEPS:")
            print("1. Start the Django server:")
            print("   cd primepath_project")
            print("   ../venv/bin/python manage.py runserver --settings=primepath_project.settings_sqlite")
            print("\n2. Clear browser cache completely:")
            print("   - Chrome: Cmd+Shift+Delete → Clear browsing data")
            print("   - Safari: Develop → Empty Caches")
            print("\n3. Visit: http://127.0.0.1:8000/RoutineTest/exams/")
            print("\n4. Check browser console for Version 3.0 confirmation")
        else:
            print("❌ ISSUES DETECTED - Review errors above")
            print("\nTROUBLESHOOTING:")
            print("1. Ensure all changes are saved")
            print("2. Clear all caches")
            print("3. Restart Django server")
            print("4. Use incognito/private browsing")
            
        return len(self.errors) == 0

if __name__ == '__main__':
    tester = RosterCompleteRemovalTestV3()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
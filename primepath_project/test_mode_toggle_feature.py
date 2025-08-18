#!/usr/bin/env python
"""
Test Mode Toggle Feature - Admin/Teacher Mode Switching
Tests the new mode toggle functionality and curriculum mapping visibility
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import Teacher

class ModeToggleTest:
    """Test the Admin/Teacher mode toggle feature"""
    
    def __init__(self):
        self.client = Client()
        self.test_results = []
        self.setup_test_user()
    
    def setup_test_user(self):
        """Setup test user and teacher"""
        print("\n" + "="*80)
        print("🔧 Setting up test user for mode toggle testing...")
        print("="*80)
        
        # Create or get test admin user
        self.admin_user, created = User.objects.get_or_create(
            username='mode_test_admin',
            defaults={
                'email': 'mode_test@test.com',
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Mode',
                'last_name': 'Test'
            }
        )
        if created:
            self.admin_user.set_password('test123')
            self.admin_user.save()
        
        # Create teacher profile
        self.teacher, created = Teacher.objects.get_or_create(
            user=self.admin_user,
            defaults={
                'name': 'Mode Test Teacher',
                'is_head_teacher': True
            }
        )
        
        print(f"✅ Test user created: {self.admin_user.username} (Staff: {self.admin_user.is_staff})")
    
    def test_mode_toggle_api(self):
        """Test the mode toggle API endpoint"""
        print("\n🧪 Testing Mode Toggle API...")
        
        # Login
        self.client.login(username='mode_test_admin', password='test123')
        
        # Test switching to Admin mode
        response = self.client.post(
            '/routinetest/api/toggle-mode/',
            data=json.dumps({'mode': 'Admin'}),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('mode') == 'Admin':
                print("✅ Successfully switched to Admin mode")
                print(f"   Features enabled: {data.get('features', {})}")
                self.test_results.append(('Mode Toggle to Admin', True))
            else:
                print(f"❌ Failed to switch to Admin mode: {data.get('message')}")
                self.test_results.append(('Mode Toggle to Admin', False))
        else:
            print(f"❌ API returned status {response.status_code}")
            self.test_results.append(('Mode Toggle to Admin', False))
        
        # Test switching back to Teacher mode
        response = self.client.post(
            '/routinetest/api/toggle-mode/',
            data=json.dumps({'mode': 'Teacher'}),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('mode') == 'Teacher':
                print("✅ Successfully switched to Teacher mode")
                self.test_results.append(('Mode Toggle to Teacher', True))
            else:
                print(f"❌ Failed to switch to Teacher mode: {data.get('message')}")
                self.test_results.append(('Mode Toggle to Teacher', False))
        else:
            print(f"❌ API returned status {response.status_code}")
            self.test_results.append(('Mode Toggle to Teacher', False))
    
    def test_get_current_mode(self):
        """Test getting current mode"""
        print("\n🧪 Testing Get Current Mode API...")
        
        self.client.login(username='mode_test_admin', password='test123')
        
        response = self.client.get('/routinetest/api/current-mode/')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Current mode: {data.get('mode')}")
                print(f"   User info: {data.get('user', {})}")
                self.test_results.append(('Get Current Mode', True))
            else:
                print(f"❌ Failed to get current mode: {data.get('message')}")
                self.test_results.append(('Get Current Mode', False))
        else:
            print(f"❌ API returned status {response.status_code}")
            self.test_results.append(('Get Current Mode', False))
    
    def test_curriculum_mapping_access(self):
        """Test curriculum mapping tab visibility based on mode"""
        print("\n🧪 Testing Curriculum Mapping Access Control...")
        
        self.client.login(username='mode_test_admin', password='test123')
        
        # Test access in Teacher mode (should be denied or hidden)
        self.client.post(
            '/routinetest/api/toggle-mode/',
            data=json.dumps({'mode': 'Teacher'}),
            content_type='application/json'
        )
        
        response = self.client.get('/routinetest/curriculum-mapping/')
        if response.status_code in [302, 403]:  # Redirect or forbidden
            print("✅ Curriculum mapping correctly blocked in Teacher mode")
            self.test_results.append(('Curriculum Mapping Block in Teacher Mode', True))
        elif response.status_code == 200:
            print("⚠️ Curriculum mapping accessible in Teacher mode (check if redirected)")
            self.test_results.append(('Curriculum Mapping Block in Teacher Mode', False))
        
        # Test access in Admin mode (should be allowed)
        self.client.post(
            '/routinetest/api/toggle-mode/',
            data=json.dumps({'mode': 'Admin'}),
            content_type='application/json'
        )
        
        response = self.client.get('/routinetest/curriculum-mapping/')
        if response.status_code == 200:
            print("✅ Curriculum mapping accessible in Admin mode")
            self.test_results.append(('Curriculum Mapping Access in Admin Mode', True))
        else:
            print(f"❌ Curriculum mapping not accessible in Admin mode (status: {response.status_code})")
            self.test_results.append(('Curriculum Mapping Access in Admin Mode', False))
    
    def test_mode_persistence(self):
        """Test that mode persists across requests"""
        print("\n🧪 Testing Mode Persistence...")
        
        self.client.login(username='mode_test_admin', password='test123')
        
        # Set to Admin mode
        self.client.post(
            '/routinetest/api/toggle-mode/',
            data=json.dumps({'mode': 'Admin'}),
            content_type='application/json'
        )
        
        # Make several requests and check mode persists
        for i in range(3):
            response = self.client.get('/routinetest/api/current-mode/')
            data = response.json()
            if data.get('mode') != 'Admin':
                print(f"❌ Mode not persisted on request {i+1}")
                self.test_results.append(('Mode Persistence', False))
                break
        else:
            print("✅ Mode persisted across multiple requests")
            self.test_results.append(('Mode Persistence', True))
    
    def test_non_staff_access(self):
        """Test that non-staff users cannot toggle modes"""
        print("\n🧪 Testing Non-Staff Access Control...")
        
        # Create regular user
        regular_user, created = User.objects.get_or_create(
            username='regular_teacher',
            defaults={
                'email': 'regular@test.com',
                'is_staff': False,
                'is_superuser': False
            }
        )
        if created:
            regular_user.set_password('test123')
            regular_user.save()
        
        self.client.login(username='regular_teacher', password='test123')
        
        response = self.client.post(
            '/routinetest/api/toggle-mode/',
            data=json.dumps({'mode': 'Admin'}),
            content_type='application/json'
        )
        
        if response.status_code == 403:
            print("✅ Non-staff users correctly denied mode toggle")
            self.test_results.append(('Non-Staff Access Denial', True))
        else:
            print(f"❌ Non-staff user was not denied (status: {response.status_code})")
            self.test_results.append(('Non-Staff Access Denial', False))
    
    def run_all_tests(self):
        """Run all mode toggle tests"""
        print("\n" + "="*80)
        print("🚀 STARTING MODE TOGGLE FEATURE TESTS")
        print("="*80)
        
        self.test_mode_toggle_api()
        self.test_get_current_mode()
        self.test_curriculum_mapping_access()
        self.test_mode_persistence()
        self.test_non_staff_access()
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "="*80)
        print("📊 MODE TOGGLE FEATURE TEST RESULTS")
        print("="*80)
        
        passed = sum(1 for _, result in self.test_results if result)
        failed = sum(1 for _, result in self.test_results if not result)
        total = len(self.test_results)
        
        print(f"\n📈 SUMMARY:")
        print(f"   Total Tests: {total}")
        print(f"   Passed: {passed} ✅")
        print(f"   Failed: {failed} ❌")
        print(f"   Success Rate: {(passed/total*100) if total > 0 else 0:.1f}%")
        
        print(f"\n📋 DETAILED RESULTS:")
        for test_name, result in self.test_results:
            status = "✅" if result else "❌"
            print(f"   {status} {test_name}")
        
        print("\n" + "="*80)
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Mode toggle feature is working correctly!")
        elif passed >= total * 0.8:
            print("✅ Most tests passed. Minor issues may need attention.")
        else:
            print("⚠️ Several tests failed. Review implementation.")
        
        print("="*80)


if __name__ == '__main__':
    test = ModeToggleTest()
    test.run_all_tests()
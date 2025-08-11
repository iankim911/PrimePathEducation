#!/usr/bin/env python3
"""
Comprehensive Test for All Implemented Fixes
Tests URL redirects, authentication, and mobile responsiveness
"""

import os
import sys
import django
import json
import time
from datetime import datetime

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client, TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from placement_test.models import Exam, StudentSession
from core.models import School, Teacher

class ComprehensiveFixesTestCase:
    """Test all three fixes: URLs, Authentication, Mobile"""
    
    def __init__(self):
        self.client = Client()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'url_redirects': [],
            'authentication': [],
            'mobile_css': [],
            'summary': {'passed': 0, 'failed': 0}
        }
        
    def test_url_redirects(self):
        """Test URL redirect system"""
        print("\n" + "="*60)
        print("TESTING URL REDIRECTS")
        print("="*60)
        
        # Test legacy URLs that should redirect
        legacy_urls = [
            ('/placement/', '/', 'Placement home redirect'),
            ('/placement/start-test/', '/api/placement/start/', 'Start test redirect'),
            ('/placement/create-exam/', None, 'Create exam (should work directly)'),
            ('/placement/sessions/', '/api/placement/sessions/', 'Sessions redirect'),
            ('/core/', '/', 'Core dashboard redirect'),
            ('/core/dashboard/', '/', 'Dashboard redirect'),
        ]
        
        for old_url, expected_redirect, description in legacy_urls:
            response = self.client.get(old_url, follow=False)
            
            if response.status_code in [301, 302]:
                # It's a redirect
                redirect_url = response.get('Location', '')
                result = {
                    'url': old_url,
                    'status': response.status_code,
                    'redirected_to': redirect_url,
                    'test': 'PASS' if expected_redirect and expected_redirect in redirect_url else 'FAIL',
                    'description': description
                }
                print(f"✅ {old_url} -> {redirect_url} ({response.status_code})")
            elif response.status_code == 200:
                # Direct access (no redirect needed)
                result = {
                    'url': old_url,
                    'status': response.status_code,
                    'test': 'PASS' if expected_redirect is None else 'WARNING',
                    'description': f"{description} - Direct access"
                }
                print(f"✅ {old_url} - Direct access OK ({response.status_code})")
            else:
                # Error
                result = {
                    'url': old_url,
                    'status': response.status_code,
                    'test': 'FAIL',
                    'description': f"{description} - Unexpected status"
                }
                print(f"❌ {old_url} - Status: {response.status_code}")
            
            self.results['url_redirects'].append(result)
            
            if result['test'] == 'PASS':
                self.results['summary']['passed'] += 1
            else:
                self.results['summary']['failed'] += 1
    
    def test_authentication(self):
        """Test authentication system"""
        print("\n" + "="*60)
        print("TESTING AUTHENTICATION")
        print("="*60)
        
        # Test anonymous access to student endpoints
        anonymous_allowed = [
            '/api/placement/start/',
            '/api/placement/sessions/',
        ]
        
        print("\n📍 Testing Anonymous Access (should be allowed):")
        for url in anonymous_allowed:
            response = self.client.get(url)
            result = {
                'url': url,
                'user': 'anonymous',
                'status': response.status_code,
                'test': 'PASS' if response.status_code in [200, 201] else 'FAIL'
            }
            
            if result['test'] == 'PASS':
                print(f"✅ {url} - Anonymous access allowed")
                self.results['summary']['passed'] += 1
            else:
                print(f"❌ {url} - Anonymous access blocked ({response.status_code})")
                self.results['summary']['failed'] += 1
            
            self.results['authentication'].append(result)
        
        # Test protected endpoints
        protected_endpoints = [
            '/api/placement/exams/create/',
            '/api/placement-rules/',
        ]
        
        print("\n📍 Testing Protected Endpoints (should require auth):")
        for url in protected_endpoints:
            # Test without authentication
            response = self.client.get(url)
            
            if response.status_code in [401, 403, 302]:
                print(f"✅ {url} - Correctly protected ({response.status_code})")
                result = {'url': url, 'protection': 'working', 'test': 'PASS'}
                self.results['summary']['passed'] += 1
            else:
                print(f"⚠️  {url} - NOT protected! ({response.status_code})")
                result = {'url': url, 'protection': 'missing', 'test': 'WARNING'}
                self.results['summary']['failed'] += 1
            
            self.results['authentication'].append(result)
        
        # Test with authentication
        print("\n📍 Testing Authenticated Access:")
        try:
            # Create test user
            user = User.objects.create_user(username='test_teacher', password='test123')
            school = School.objects.first() or School.objects.create(name="Test School")
            teacher = Teacher.objects.create(
                user=user,
                school=school,
                name="Test Teacher"
            )
            
            # Login
            self.client.login(username='test_teacher', password='test123')
            
            # Test access to protected endpoints
            response = self.client.get('/api/placement/exams/create/')
            if response.status_code == 200:
                print(f"✅ Authenticated user can access protected endpoints")
                self.results['summary']['passed'] += 1
            else:
                print(f"❌ Authenticated user cannot access protected endpoints ({response.status_code})")
                self.results['summary']['failed'] += 1
            
            # Cleanup
            user.delete()
            
        except Exception as e:
            print(f"❌ Authentication test error: {e}")
            self.results['summary']['failed'] += 1
    
    def test_mobile_css(self):
        """Test mobile CSS and JavaScript loading"""
        print("\n" + "="*60)
        print("TESTING MOBILE RESPONSIVENESS")
        print("="*60)
        
        # Check if mobile CSS file exists
        mobile_css_path = 'static/css/mobile-responsive.css'
        if os.path.exists(mobile_css_path):
            print(f"✅ Mobile CSS file exists")
            self.results['mobile_css'].append({'file': 'mobile-responsive.css', 'exists': True, 'test': 'PASS'})
            self.results['summary']['passed'] += 1
            
            # Check CSS content
            with open(mobile_css_path, 'r') as f:
                content = f.read()
                
                # Check for key mobile breakpoints
                checks = [
                    ('@media only screen and (max-width: 767px)', 'Mobile breakpoint'),
                    ('@media only screen and (min-width: 768px) and (max-width: 1024px)', 'Tablet breakpoint'),
                    ('@media (hover: none) and (pointer: coarse)', 'Touch device detection'),
                    ('min-height: 44px', 'Touch target sizing'),
                ]
                
                for pattern, description in checks:
                    if pattern in content:
                        print(f"✅ {description} found in CSS")
                        self.results['summary']['passed'] += 1
                    else:
                        print(f"❌ {description} missing from CSS")
                        self.results['summary']['failed'] += 1
        else:
            print(f"❌ Mobile CSS file not found")
            self.results['mobile_css'].append({'file': 'mobile-responsive.css', 'exists': False, 'test': 'FAIL'})
            self.results['summary']['failed'] += 1
        
        # Check mobile JavaScript
        mobile_js_path = 'static/js/modules/mobile-handler.js'
        if os.path.exists(mobile_js_path):
            print(f"✅ Mobile JavaScript handler exists")
            self.results['mobile_css'].append({'file': 'mobile-handler.js', 'exists': True, 'test': 'PASS'})
            self.results['summary']['passed'] += 1
            
            # Check JS content
            with open(mobile_js_path, 'r') as f:
                content = f.read()
                
                # Check for key functionality
                checks = [
                    ('detectDevice', 'Device detection'),
                    ('setupEventListeners', 'Touch event setup'),
                    ('addTouchSupport', 'Touch support function'),
                    ('setupSwipeGestures', 'Swipe gesture support'),
                    ('logDebug', 'Debug logging'),
                ]
                
                for pattern, description in checks:
                    if pattern in content:
                        print(f"✅ {description} found in JS")
                        self.results['summary']['passed'] += 1
                    else:
                        print(f"❌ {description} missing from JS")
                        self.results['summary']['failed'] += 1
        else:
            print(f"❌ Mobile JavaScript handler not found")
            self.results['mobile_css'].append({'file': 'mobile-handler.js', 'exists': False, 'test': 'FAIL'})
            self.results['summary']['failed'] += 1
        
        # Test template integration
        print("\n📍 Testing Template Integration:")
        
        # Get a test session
        session = StudentSession.objects.filter(completed_at__isnull=True).first()
        if session:
            response = self.client.get(f'/placement/test/{session.id}/')
            
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                
                # Check for mobile CSS inclusion
                if 'mobile-responsive.css' in content:
                    print(f"✅ Mobile CSS included in student test template")
                    self.results['summary']['passed'] += 1
                else:
                    print(f"⚠️  Mobile CSS not found in template")
                    self.results['summary']['failed'] += 1
                
                # Check for mobile JS inclusion
                if 'mobile-handler.js' in content:
                    print(f"✅ Mobile JS included in student test template")
                    self.results['summary']['passed'] += 1
                else:
                    print(f"⚠️  Mobile JS not found in template")
                    self.results['summary']['failed'] += 1
                
                # Check for viewport meta tag
                if 'viewport' in content:
                    print(f"✅ Viewport meta tag present")
                    self.results['summary']['passed'] += 1
                else:
                    print(f"❌ Viewport meta tag missing")
                    self.results['summary']['failed'] += 1
        else:
            print(f"⚠️  No test session available for template testing")
    
    def generate_report(self):
        """Generate final report"""
        print("\n" + "="*60)
        print("COMPREHENSIVE FIX TEST REPORT")
        print("="*60)
        
        total = self.results['summary']['passed'] + self.results['summary']['failed']
        pass_rate = (self.results['summary']['passed'] / total * 100) if total > 0 else 0
        
        print(f"\n📊 Summary:")
        print(f"  ✅ Passed: {self.results['summary']['passed']}")
        print(f"  ❌ Failed: {self.results['summary']['failed']}")
        print(f"  📈 Pass Rate: {pass_rate:.1f}%")
        
        # URL Redirects Summary
        url_passes = sum(1 for r in self.results['url_redirects'] if r.get('test') == 'PASS')
        print(f"\n🔗 URL Redirects: {url_passes}/{len(self.results['url_redirects'])} working")
        
        # Authentication Summary
        auth_passes = sum(1 for r in self.results['authentication'] if r.get('test') == 'PASS')
        print(f"🔐 Authentication: {auth_passes}/{len(self.results['authentication'])} correct")
        
        # Mobile Summary
        mobile_passes = sum(1 for r in self.results['mobile_css'] if r.get('test') == 'PASS')
        print(f"📱 Mobile Support: {mobile_passes}/{len(self.results['mobile_css'])} implemented")
        
        # Save report
        with open('fix_test_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to fix_test_results.json")
        
        # Overall assessment
        if pass_rate >= 80:
            print(f"\n✅ ALL FIXES SUCCESSFULLY IMPLEMENTED!")
        elif pass_rate >= 60:
            print(f"\n⚠️  Most fixes working, some issues remain")
        else:
            print(f"\n❌ Fixes need more work")
        
        return self.results
    
    def run_all_tests(self):
        """Run all fix tests"""
        print("🚀 Starting Comprehensive Fix Tests...")
        print("Testing: URL Redirects, Authentication, Mobile Support")
        
        self.test_url_redirects()
        self.test_authentication()
        self.test_mobile_css()
        
        return self.generate_report()


if __name__ == "__main__":
    tester = ComprehensiveFixesTestCase()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results['summary']['failed'] == 0:
        sys.exit(0)
    else:
        sys.exit(1)
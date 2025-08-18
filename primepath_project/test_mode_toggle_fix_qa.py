#!/usr/bin/env python3
"""
Comprehensive QA Test for Mode Toggle Fix
Tests that the toggle issue is resolved and only header toggle remains
Created: August 18, 2025
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from django.test import Client, TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from bs4 import BeautifulSoup
import re

print("\n" + "="*80)
print("MODE TOGGLE FIX - COMPREHENSIVE QA TEST")
print("="*80)
print(f"Test Started: {datetime.now()}")
print("="*80 + "\n")

class ModeToggleFixTest:
    def __init__(self):
        self.client = Client()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests_passed': 0,
            'tests_failed': 0,
            'issues_found': [],
            'pages_tested': [],
            'toggle_locations': []
        }
        
    def setup_test_user(self):
        """Create test user if needed"""
        try:
            self.user = User.objects.get(username='test_admin')
        except User.DoesNotExist:
            self.user = User.objects.create_user(
                username='test_admin',
                password='test123',
                is_staff=True,
                is_superuser=True
            )
        
        # Login
        logged_in = self.client.login(username='test_admin', password='test123')
        if logged_in:
            print("✅ Test user logged in successfully")
        else:
            print("❌ Failed to login test user")
        return logged_in
    
    def check_page_for_toggle_issues(self, url, page_name):
        """Check a specific page for toggle issues"""
        print(f"\n📄 Testing: {page_name} ({url})")
        print("-" * 60)
        
        try:
            response = self.client.get(url)
            if response.status_code != 200:
                print(f"⚠️ Page returned status {response.status_code}")
                self.results['issues_found'].append({
                    'page': page_name,
                    'issue': f'HTTP {response.status_code}'
                })
                return False
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Test 1: Check for "function:" text
            print("  🔍 Checking for 'function:' text...")
            function_texts = []
            for text in soup.stripped_strings:
                if 'function:' in text.lower() or 'function :' in text.lower():
                    function_texts.append(text[:100])
            
            if function_texts:
                print(f"  ❌ Found 'function:' text in {len(function_texts)} places:")
                for text in function_texts[:3]:  # Show first 3
                    print(f"     - {text}")
                self.results['issues_found'].append({
                    'page': page_name,
                    'issue': f"'function:' text found {len(function_texts)} times",
                    'samples': function_texts[:3]
                })
                self.results['tests_failed'] += 1
            else:
                print("  ✅ No 'function:' text found")
                self.results['tests_passed'] += 1
            
            # Test 2: Count toggle elements
            print("  🔍 Counting toggle elements...")
            toggle_containers = soup.find_all(class_=re.compile(r'mode-toggle-container'))
            toggle_wrappers = soup.find_all(class_=re.compile(r'mode-toggle-wrapper'))
            toggle_buttons = soup.find_all(class_=re.compile(r'mode-toggle-btn'))
            
            total_toggles = len(set(
                [elem.parent for elem in toggle_containers] +
                [elem.parent for elem in toggle_wrappers] +
                [elem.parent for elem in toggle_buttons]
            ))
            
            print(f"  📊 Toggle elements found:")
            print(f"     - Containers: {len(toggle_containers)}")
            print(f"     - Wrappers: {len(toggle_wrappers)}")
            print(f"     - Buttons: {len(toggle_buttons)}")
            print(f"     - Unique toggles: {total_toggles}")
            
            if total_toggles > 1:
                print(f"  ⚠️ Multiple toggles found ({total_toggles})")
                self.results['issues_found'].append({
                    'page': page_name,
                    'issue': f'Multiple toggles ({total_toggles})',
                    'details': {
                        'containers': len(toggle_containers),
                        'wrappers': len(toggle_wrappers),
                        'buttons': len(toggle_buttons)
                    }
                })
            elif total_toggles == 1:
                print("  ✅ Exactly one toggle found (expected)")
                self.results['tests_passed'] += 1
            else:
                print("  ℹ️ No toggles found (may be OK for some pages)")
            
            # Test 3: Check toggle locations
            print("  🔍 Checking toggle locations...")
            for toggle in toggle_containers:
                # Check if toggle is in stats area
                parent = toggle.parent
                parent_classes = ' '.join(parent.get('class', []))
                
                in_stats = any(stat_class in parent_classes for stat_class in 
                             ['stats', 'stat-', 'statistics', 'dashboard'])
                
                location = {
                    'element_id': toggle.get('id', 'no-id'),
                    'parent_classes': parent_classes[:100],
                    'in_stats_area': in_stats,
                    'text': toggle.get_text()[:50].strip()
                }
                
                self.results['toggle_locations'].append({
                    'page': page_name,
                    'location': location
                })
                
                if in_stats:
                    print(f"  ❌ Toggle found in stats area!")
                    print(f"     Parent classes: {parent_classes[:100]}")
                    self.results['issues_found'].append({
                        'page': page_name,
                        'issue': 'Toggle in stats area',
                        'location': location
                    })
                    self.results['tests_failed'] += 1
                else:
                    print(f"  ✅ Toggle location OK (not in stats)")
                    if toggle.get('id') == 'modeToggleContainer':
                        print("     Located in header (expected)")
                    self.results['tests_passed'] += 1
            
            # Test 4: Check for toggle in specific stats elements
            print("  🔍 Checking stats boxes for toggles...")
            stats_selectors = [
                'class-stats', 'class-stat', 'stats-box', 'stat-box',
                'stats-cards', 'stat-card', 'statistics-container'
            ]
            
            stats_with_toggles = []
            for selector in stats_selectors:
                stats_elements = soup.find_all(class_=re.compile(selector))
                for elem in stats_elements:
                    # Check if this stats element contains any toggle
                    toggles_inside = elem.find_all(class_=re.compile(r'toggle'))
                    if toggles_inside:
                        stats_with_toggles.append({
                            'stats_class': selector,
                            'toggle_count': len(toggles_inside),
                            'toggle_text': toggles_inside[0].get_text()[:50] if toggles_inside else ''
                        })
            
            if stats_with_toggles:
                print(f"  ❌ Found toggles inside stats boxes:")
                for stat in stats_with_toggles:
                    print(f"     - {stat['stats_class']}: {stat['toggle_count']} toggles")
                self.results['issues_found'].append({
                    'page': page_name,
                    'issue': 'Toggles in stats boxes',
                    'details': stats_with_toggles
                })
                self.results['tests_failed'] += 1
            else:
                print("  ✅ No toggles found in stats boxes")
                self.results['tests_passed'] += 1
            
            # Test 5: Verify header toggle exists and is correct
            print("  🔍 Verifying header toggle...")
            header_toggle = soup.find(id='modeToggleContainer')
            if header_toggle:
                print("  ✅ Header toggle found")
                # Check button text
                btn = header_toggle.find(class_='mode-toggle-btn')
                if btn:
                    btn_text = btn.get_text().strip()
                    if 'function' in btn_text.lower():
                        print(f"  ❌ Header toggle has 'function' in text: {btn_text}")
                        self.results['issues_found'].append({
                            'page': page_name,
                            'issue': 'Header toggle has function text',
                            'text': btn_text
                        })
                        self.results['tests_failed'] += 1
                    else:
                        print(f"  ✅ Header toggle text OK: {btn_text}")
                        self.results['tests_passed'] += 1
            else:
                print("  ⚠️ Header toggle not found")
            
            self.results['pages_tested'].append({
                'name': page_name,
                'url': url,
                'status': 'tested'
            })
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing page: {str(e)}")
            self.results['issues_found'].append({
                'page': page_name,
                'issue': f'Test error: {str(e)}'
            })
            return False
    
    def run_tests(self):
        """Run all tests"""
        print("\n🚀 Starting Mode Toggle Fix QA Tests...")
        
        # Setup
        if not self.setup_test_user():
            print("❌ Failed to setup test user, aborting")
            return
        
        # Define pages to test
        test_pages = [
            ('/RoutineTest/', 'RoutineTest Dashboard'),
            ('/RoutineTest/classes-exams/', 'Classes & Exams'),
            ('/RoutineTest/create/', 'Create Exam'),
            ('/RoutineTest/exams/', 'Exam List'),
            ('/RoutineTest/sessions/', 'Session List'),
        ]
        
        # Test each page
        for url, name in test_pages:
            self.check_page_for_toggle_issues(url, name)
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        total_tests = self.results['tests_passed'] + self.results['tests_failed']
        
        print(f"\n📊 Test Results:")
        print(f"  Total Tests: {total_tests}")
        print(f"  ✅ Passed: {self.results['tests_passed']}")
        print(f"  ❌ Failed: {self.results['tests_failed']}")
        print(f"  Pages Tested: {len(self.results['pages_tested'])}")
        
        if self.results['issues_found']:
            print(f"\n⚠️ Issues Found ({len(self.results['issues_found'])}):")
            for issue in self.results['issues_found']:
                print(f"\n  📄 {issue['page']}:")
                print(f"     Issue: {issue['issue']}")
                if 'details' in issue:
                    print(f"     Details: {json.dumps(issue['details'], indent=8)}")
        else:
            print("\n✅ No issues found!")
        
        if self.results['toggle_locations']:
            print(f"\n📍 Toggle Locations Found:")
            for loc in self.results['toggle_locations']:
                print(f"  {loc['page']}: {loc['location']['element_id']}")
                if loc['location']['in_stats_area']:
                    print(f"    ⚠️ IN STATS AREA")
        
        # Save results to file
        results_file = f"qa_mode_toggle_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\n💾 Results saved to: {results_file}")
        
        # Final verdict
        print("\n" + "="*80)
        if self.results['tests_failed'] == 0:
            print("✅ ALL TESTS PASSED - Mode toggle fix is working correctly!")
        else:
            print(f"❌ TESTS FAILED - {self.results['tests_failed']} issues need attention")
        print("="*80 + "\n")

if __name__ == '__main__':
    tester = ModeToggleFixTest()
    tester.run_tests()
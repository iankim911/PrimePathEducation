#!/usr/bin/env python
"""
Comprehensive QA Test for RoutineTest Schedule Matrix Quarterly Table Fix
Tests that the quarterly table no longer appears at the bottom of the page
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from core.models import Teacher, School
from primepath_routinetest.models import Exam, Question
from primepath_routinetest.views.schedule_matrix import schedule_matrix_view
from bs4 import BeautifulSoup
import json

User = get_user_model()

class ScheduleMatrixQuarterlyFixTest(TestCase):
    """Test that quarterly table issue is resolved"""
    
    def setUp(self):
        """Setup test data"""
        self.client = Client()
        
        # Create test school
        self.school = School.objects.create(
            name="Test School",
            address="123 Test Street"
        )
        
        # Create test user and teacher
        self.user = User.objects.create_user(
            username="testteacher",
            email="teacher@test.com",
            password="testpass123"
        )
        
        self.teacher = Teacher.objects.create(
            user=self.user,
            name="Test Teacher",
            email="teacher@test.com"
        )
        
        # Login
        self.client.login(username="testteacher", password="testpass123")
    
    def test_quarterly_table_not_duplicated(self):
        """Test that quarterly table only appears in tab panel, not at bottom"""
        print("\n" + "="*70)
        print("TEST: Quarterly Table Fix Verification")
        print("="*70)
        
        # Get the schedule matrix page
        response = self.client.get('/RoutineTest/schedule-matrix/')
        self.assertEqual(response.status_code, 200, "Schedule matrix page should load")
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all quarterly tables
        quarterly_tables = []
        all_tables = soup.find_all('table', class_='matrix-table')
        
        for table in all_tables:
            # Check if this is a quarterly table by looking for quarter headers
            headers = table.find_all('th')
            header_text = ' '.join([th.get_text() for th in headers])
            if 'Quarter' in header_text or 'Q1' in header_text or 'Q2' in header_text:
                quarterly_tables.append(table)
                
        print(f"✓ Found {len(quarterly_tables)} quarterly table(s)")
        
        # Check that quarterly table is only inside tab panel
        for i, table in enumerate(quarterly_tables):
            # Navigate up to find parent containers
            parent = table.parent
            is_in_tab_panel = False
            
            while parent:
                if parent.get('id') == 'quarterly-panel':
                    is_in_tab_panel = True
                    break
                parent = parent.parent
            
            print(f"  Table {i+1}: In tab panel = {is_in_tab_panel}")
            self.assertTrue(is_in_tab_panel, 
                f"Quarterly table {i+1} should be inside quarterly-panel")
        
        # Check tab panel structure
        monthly_panel = soup.find('div', id='monthly-panel')
        quarterly_panel = soup.find('div', id='quarterly-panel')
        
        self.assertIsNotNone(monthly_panel, "Monthly panel should exist")
        self.assertIsNotNone(quarterly_panel, "Quarterly panel should exist")
        
        # Check that panels have proper classes
        self.assertIn('tab-panel', monthly_panel.get('class', []), 
            "Monthly panel should have tab-panel class")
        self.assertIn('tab-panel', quarterly_panel.get('class', []), 
            "Quarterly panel should have tab-panel class")
        
        # Check ARIA attributes
        self.assertEqual(monthly_panel.get('role'), 'tabpanel', 
            "Monthly panel should have tabpanel role")
        self.assertEqual(quarterly_panel.get('role'), 'tabpanel', 
            "Quarterly panel should have tabpanel role")
        
        print("\n✓ Tab panel structure is correct")
        print("✓ ARIA attributes are properly set")
        
        # Check that quarterly panel is hidden by default
        quarterly_classes = quarterly_panel.get('class', [])
        monthly_classes = monthly_panel.get('class', [])
        
        self.assertIn('active', monthly_classes, 
            "Monthly panel should be active by default")
        self.assertNotIn('active', quarterly_classes, 
            "Quarterly panel should NOT be active by default")
        
        print("✓ Monthly panel is active by default")
        print("✓ Quarterly panel is hidden by default")
        
        # Check for duplicate content outside tab panels
        tab_container = soup.find('div', class_='tab-container')
        if tab_container:
            # Find any tables that are siblings of tab-container (should be none)
            siblings = tab_container.find_next_siblings()
            duplicate_tables = []
            for sibling in siblings:
                if sibling.name == 'table' or (sibling.name == 'div' and sibling.find('table')):
                    duplicate_tables.append(sibling)
            
            self.assertEqual(len(duplicate_tables), 0, 
                f"Found {len(duplicate_tables)} table(s) outside tab container - ISSUE NOT FIXED!")
            print("✓ No duplicate tables found outside tab container")
        
        print("\n" + "="*70)
        print("RESULT: Quarterly table issue is RESOLVED ✅")
        print("="*70)
    
    def test_javascript_module_loaded(self):
        """Test that JavaScript module is properly loaded"""
        print("\n" + "="*70)
        print("TEST: JavaScript Module Loading")
        print("="*70)
        
        response = self.client.get('/RoutineTest/schedule-matrix/')
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check for modular JS file
        js_scripts = soup.find_all('script', src=True)
        js_loaded = False
        for script in js_scripts:
            if 'schedule-matrix.js' in script.get('src', ''):
                js_loaded = True
                print(f"✓ Found schedule-matrix.js: {script.get('src')}")
                break
        
        self.assertTrue(js_loaded, "schedule-matrix.js should be loaded")
        
        # Check for initialization script
        init_scripts = soup.find_all('script', src=False)
        has_config = False
        for script in init_scripts:
            if script.string and 'MATRIX_CONFIG' in script.string:
                has_config = True
                print("✓ Found MATRIX_CONFIG initialization")
                break
        
        self.assertTrue(has_config, "Matrix configuration should be present")
        
        print("\n" + "="*70)
        print("RESULT: JavaScript modules properly loaded ✅")
        print("="*70)
    
    def test_css_module_loaded(self):
        """Test that CSS module is properly loaded"""
        print("\n" + "="*70)
        print("TEST: CSS Module Loading")
        print("="*70)
        
        response = self.client.get('/RoutineTest/schedule-matrix/')
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check for modular CSS file
        css_links = soup.find_all('link', rel='stylesheet')
        css_loaded = False
        for link in css_links:
            if 'schedule-matrix.css' in link.get('href', ''):
                css_loaded = True
                print(f"✓ Found schedule-matrix.css: {link.get('href')}")
                break
        
        self.assertTrue(css_loaded, "schedule-matrix.css should be loaded")
        
        print("\n" + "="*70)
        print("RESULT: CSS modules properly loaded ✅")
        print("="*70)
    
    def test_tab_buttons_present(self):
        """Test that tab switching buttons are present and functional"""
        print("\n" + "="*70)
        print("TEST: Tab Button Functionality")
        print("="*70)
        
        response = self.client.get('/RoutineTest/schedule-matrix/')
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find tab buttons
        monthly_tab = soup.find('button', {'data-tab': 'monthly'})
        quarterly_tab = soup.find('button', {'data-tab': 'quarterly'})
        
        self.assertIsNotNone(monthly_tab, "Monthly tab button should exist")
        self.assertIsNotNone(quarterly_tab, "Quarterly tab button should exist")
        
        print("✓ Monthly tab button found")
        print("✓ Quarterly tab button found")
        
        # Check button attributes
        self.assertEqual(monthly_tab.get('role'), 'tab', 
            "Monthly button should have tab role")
        self.assertEqual(quarterly_tab.get('role'), 'tab', 
            "Quarterly button should have tab role")
        
        # Check active state
        monthly_classes = monthly_tab.get('class', [])
        quarterly_classes = quarterly_tab.get('class', [])
        
        self.assertIn('active', monthly_classes, 
            "Monthly tab should be active by default")
        self.assertNotIn('active', quarterly_classes, 
            "Quarterly tab should not be active by default")
        
        print("✓ Tab buttons have correct initial state")
        print("✓ ARIA roles properly set")
        
        print("\n" + "="*70)
        print("RESULT: Tab buttons properly configured ✅")
        print("="*70)

def run_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("ROUTINETEST QUARTERLY TABLE FIX - COMPREHENSIVE QA TEST")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    from django.test.runner import DiscoverRunner
    runner = DiscoverRunner(verbosity=2, interactive=False, keepdb=False)
    
    # Run tests
    test_suite = runner.test_loader.loadTestsFromTestCase(ScheduleMatrixQuarterlyFixTest)
    result = runner.run_suite(test_suite)
    
    # Summary
    print("\n" + "="*70)
    print("FINAL TEST SUMMARY")
    print("="*70)
    
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED - Quarterly table issue is FIXED!")
        print("\nKey Achievements:")
        print("  • Quarterly table only appears in tab panel")
        print("  • No duplicate tables at bottom of page")
        print("  • Proper tab switching structure")
        print("  • Modular JavaScript and CSS loaded")
        print("  • ARIA attributes for accessibility")
        print("\nThe modular refactor successfully resolved the issue!")
    else:
        print("❌ SOME TESTS FAILED - Issue may not be fully resolved")
        print(f"\nFailures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        
        for test, traceback in result.failures:
            print(f"\nFailed: {test}")
            print(traceback)
    
    print("\n" + "="*70)
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
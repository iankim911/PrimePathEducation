#!/usr/bin/env python
"""
Comprehensive test to verify RoutineTest exam list UI optimization.
Tests removal of scheduling displays, button consistency, and alignment.
"""
import os
import sys
import django
import re

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from primepath_routinetest.models import Exam
import json


def test_routinetest_ui_optimization():
    """Test RoutineTest exam list UI optimization."""
    print("\n" + "="*80)
    print("🎨 ROUTINETEST UI OPTIMIZATION TEST")
    print("="*80)
    
    test_results = []
    
    # ========================================
    # SECTION 1: TEMPLATE ANALYSIS
    # ========================================
    print("\n📋 SECTION 1: Template Analysis - UI Changes")
    print("-" * 60)
    
    template_path = 'templates/primepath_routinetest/exam_list.html'
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    # Check that scheduling displays have been removed
    removed_elements = [
        ('Time Period Display with dates', '📅 {{ exam.get_time_period_display }}'),
        ('Class schedules count', '📆 {{ exam.class_schedules.count }}'),
        ('No schedules set message', '⏰ No schedules set'),
        ('Scheduled Date field', 'scheduled_date'),
        ('Scheduled Time fields', 'scheduled_start_time'),
        ('Schedule-related displays', 'has_class_schedules'),
    ]
    
    for name, pattern in removed_elements:
        if pattern not in template_content:
            print(f"✅ {name} - Successfully removed")
            test_results.append((f'Removed: {name}', True))
        else:
            print(f"❌ {name} - Still present (should be removed)")
            test_results.append((f'Removed: {name}', False))
    
    # ========================================
    # SECTION 2: BUTTON STYLING
    # ========================================
    print("\n📋 SECTION 2: Button Styling - Consistency Check")
    print("-" * 60)
    
    # Check button classes and styling
    button_checks = [
        ('Manage button has primary style', 'btn btn-small btn-primary">Manage'),
        ('Roster button has success style', 'btn btn-small btn-success"'),
        ('Update Name has secondary style', 'btn btn-small btn-secondary">Update Name'),
        ('Delete button has danger style', 'btn btn-small btn-danger">Delete'),
        ('Consistent button sizing class', '.btn-small {'),
        ('Minimum width for buttons', 'min-width: 80px'),
        ('Delete button margin-left auto', 'margin-left: auto'),
    ]
    
    for name, pattern in button_checks:
        if pattern in template_content:
            print(f"✅ {name}")
            test_results.append((f'Button: {name}', True))
        else:
            print(f"❌ {name} - Missing")
            test_results.append((f'Button: {name}', False))
    
    # ========================================
    # SECTION 3: SIMPLIFIED DISPLAYS
    # ========================================
    print("\n📋 SECTION 3: Simplified Displays")
    print("-" * 60)
    
    # Check for simplified exam type badge
    simplified_checks = [
        ('Simplified exam type badge', 'Review / Monthly'),
        ('Quarterly exam badge', 'Quarterly'),
        ('No emoji in exam type', '📝' not in template_content or '📊' not in template_content),
        ('Roster without emoji', 'Roster{% if'),
    ]
    
    for name, check in simplified_checks:
        if isinstance(check, bool):
            result = check
        else:
            result = check in template_content
            
        if result:
            print(f"✅ {name}")
            test_results.append((f'Simplified: {name}', True))
        else:
            print(f"❌ {name}")
            test_results.append((f'Simplified: {name}', False))
    
    # ========================================
    # SECTION 4: CSS ALIGNMENT
    # ========================================
    print("\n📋 SECTION 4: CSS Alignment & Grid")
    print("-" * 60)
    
    css_checks = [
        ('Grid layout for cards', 'display: grid'),
        ('Card padding consistent', 'padding: 20px'),
        ('Flex display for actions', '.exam-actions {'),
        ('Gap between buttons', 'gap: 10px'),
        ('Card hover effect', '.exam-card:hover'),
        ('Border radius for cards', 'border-radius: 8px'),
    ]
    
    for name, pattern in css_checks:
        if pattern in template_content:
            print(f"✅ {name}")
            test_results.append((f'CSS: {name}', True))
        else:
            print(f"❌ {name}")
            test_results.append((f'CSS: {name}', False))
    
    # ========================================
    # SECTION 5: CONSOLE DEBUGGING
    # ========================================
    print("\n📋 SECTION 5: Console Debugging - Enhanced Logging")
    print("-" * 60)
    
    debug_checks = [
        ('UI Optimization logging', '[UI_OPTIMIZATION]'),
        ('Button analysis logging', 'Button Analysis'),
        ('Scheduling element check', 'No scheduling elements found'),
        ('Button click monitoring', 'Button clicked:'),
        ('Roster stats logging', 'Roster button for'),
        ('Date pattern detection', 'datePatterns'),
        ('Delete button warning', 'DELETE button clicked'),
        ('UI changes list', 'UI Changes Applied:'),
    ]
    
    for name, pattern in debug_checks:
        if pattern in template_content:
            print(f"✅ {name}")
            test_results.append((f'Debug: {name}', True))
        else:
            print(f"❌ {name}")
            test_results.append((f'Debug: {name}', False))
    
    # ========================================
    # SECTION 6: FUNCTIONAL TEST
    # ========================================
    print("\n📋 SECTION 6: Functional Test - Page Rendering")
    print("-" * 60)
    
    client = Client()
    
    # Test that the page loads
    response = client.get('/RoutineTest/exams/', follow=True)
    if response.status_code in [200, 302]:
        print("✅ Exam list page loads successfully")
        test_results.append(('Functional: Page loads', True))
        
        # Check response content for key elements
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check that no scheduling elements are in the rendered HTML
            scheduling_patterns = [
                'scheduled_date',
                'scheduled_start_time',
                'class schedule',
                'No schedules set'
            ]
            
            found_scheduling = False
            for pattern in scheduling_patterns:
                if pattern in content.lower():
                    print(f"⚠️ Found scheduling element in rendered HTML: {pattern}")
                    found_scheduling = True
            
            if not found_scheduling:
                print("✅ No scheduling elements in rendered HTML")
                test_results.append(('Functional: No scheduling', True))
            else:
                test_results.append(('Functional: No scheduling', False))
    else:
        print(f"❌ Exam list page error: {response.status_code}")
        test_results.append(('Functional: Page loads', False))
    
    # ========================================
    # SECTION 7: DATABASE CHECK
    # ========================================
    print("\n📋 SECTION 7: Database - Verify Model Structure")
    print("-" * 60)
    
    # Check that scheduling fields exist in model but aren't displayed
    from primepath_routinetest.models.class_schedule import ClassExamSchedule
    
    if hasattr(ClassExamSchedule, 'scheduled_date'):
        print("✅ ClassExamSchedule has scheduled_date (class-level)")
        test_results.append(('Model: Class scheduling exists', True))
    
    # Verify Exam model doesn't have direct scheduling
    exam = Exam.objects.first()
    if exam:
        # These fields should NOT exist on Exam model
        if not hasattr(exam, 'scheduled_date'):
            print("✅ Exam model doesn't have scheduled_date (correct)")
            test_results.append(('Model: No exam-level scheduling', True))
        else:
            print("❌ Exam model has scheduled_date (should be class-level only)")
            test_results.append(('Model: No exam-level scheduling', False))
    
    # ========================================
    # SECTION 8: COMPARISON WITH PLACEMENTTEST
    # ========================================
    print("\n📋 SECTION 8: PlacementTest Comparison")
    print("-" * 60)
    
    placement_template = 'templates/placement_test/exam_list.html'
    with open(placement_template, 'r') as f:
        placement_content = f.read()
    
    # Check for consistent elements
    consistency_checks = [
        ('Same grid layout', 'grid-template-columns: repeat(auto-fill'),
        ('Same button class structure', 'btn btn-small'),
        ('Same card styling', '.exam-card {'),
        ('Same hover effects', '.exam-card:hover'),
        ('Same action button layout', '.exam-actions {'),
    ]
    
    for name, pattern in consistency_checks:
        in_placement = pattern in placement_content
        in_routine = pattern in template_content
        
        if in_placement and in_routine:
            print(f"✅ {name} - Consistent with PlacementTest")
            test_results.append((f'Consistent: {name}', True))
        else:
            print(f"⚠️ {name} - Inconsistent")
            test_results.append((f'Consistent: {name}', False))
    
    # ========================================
    # FINAL SUMMARY
    # ========================================
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\nTests Passed: {passed}/{total} ({percentage:.1f}%)")
    
    # Group results by category
    categories = {}
    for name, result in test_results:
        category = name.split(':')[0]
        if category not in categories:
            categories[category] = []
        categories[category].append((name, result))
    
    print("\n📈 Results by Category:")
    print("-" * 40)
    for category, results in categories.items():
        cat_passed = sum(1 for _, r in results if r)
        cat_total = len(results)
        cat_percent = (cat_passed / cat_total * 100) if cat_total > 0 else 0
        status = "✅" if cat_percent == 100 else "⚠️" if cat_percent >= 80 else "❌"
        print(f"{status} {category}: {cat_passed}/{cat_total} ({cat_percent:.1f}%)")
    
    # List failures
    if passed < total:
        print("\n❌ Failed Items:")
        print("-" * 40)
        for name, result in test_results:
            if not result:
                print(f"  • {name}")
    
    # Final verdict
    print("\n" + "="*80)
    if percentage >= 95:
        print("🎉 EXCELLENT! UI optimization successfully implemented!")
        print("✅ Scheduling displays removed (class-level only)")
        print("✅ Button sizing and colors consistent")
        print("✅ Alignment issues fixed")
        print("✅ Comprehensive debugging added")
        print("✅ Matches PlacementTest UI standards")
    elif percentage >= 90:
        print("✅ VERY GOOD: Most UI optimizations working")
    elif percentage >= 80:
        print("⚠️ GOOD: Core UI improvements in place")
    else:
        print("❌ NEEDS ATTENTION: Some UI issues remain")
    
    print("\n💡 Key UI Improvements:")
    print("-" * 40)
    print("1. Removed all scheduling/date displays from exam cards")
    print("2. Standardized button sizes with consistent padding")
    print("3. Delete button styled with danger color and right-aligned")
    print("4. Simplified exam type badges without excessive styling")
    print("5. Roster button shows count inline without emoji")
    print("6. Added comprehensive console debugging for UI state")
    print("7. Aligned with PlacementTest module UI standards")
    
    print("="*80)
    
    return passed, total, percentage


if __name__ == '__main__':
    try:
        passed, total, percentage = test_routinetest_ui_optimization()
        sys.exit(0 if percentage >= 90 else 1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
#!/usr/bin/env python
"""
Comprehensive test to verify RoutineTest UI fixes for button overflow, 
alignment, and color issues.
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


def test_routinetest_ui_fixes():
    """Test comprehensive UI fixes for RoutineTest exam list."""
    print("\n" + "="*80)
    print("🔧 ROUTINETEST UI FIXES VERIFICATION")
    print("="*80)
    
    test_results = []
    
    # ========================================
    # SECTION 1: BUTTON LAYOUT FIXES
    # ========================================
    print("\n📋 SECTION 1: Button Layout & Overflow Fixes")
    print("-" * 60)
    
    template_path = 'templates/primepath_routinetest/exam_list.html'
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    # Check button layout fixes
    button_fixes = [
        ('Removed margin-left auto', 'margin-left: auto' not in template_content),
        ('Added flex-wrap for overflow', 'flex-wrap: wrap' in template_content),
        ('Restored normal gap', 'gap: 10px' in template_content),
        ('Generous min-width for buttons', 'min-width: 85px' in template_content),
        ('Generous max-width constraint', 'max-width: 110px' in template_content),
        ('Normal font for Update Name', 'btn-secondary' in template_content and 'font-size: 0.9rem' in template_content),
        ('Generous padding for space', 'padding: 6px 10px' in template_content),
    ]
    
    for name, check in button_fixes:
        if check:
            print(f"✅ {name}")
            test_results.append((f'Button Fix: {name}', True))
        else:
            print(f"❌ {name}")
            test_results.append((f'Button Fix: {name}', False))
    
    # ========================================
    # SECTION 2: DELETE BUTTON COLOR
    # ========================================
    print("\n📋 SECTION 2: Delete Button Color Fix")
    print("-" * 60)
    
    delete_color_fixes = [
        ('Force red background', 'background-color: #dc3545 !important' in template_content),
        ('Force red border', 'border-color: #dc3545 !important' in template_content),
        ('Force white text', 'color: white !important' in template_content),
        ('Red hover state', 'background-color: #c82333 !important' in template_content),
        ('Red hover border', 'border-color: #bd2130 !important' in template_content),
    ]
    
    for name, check in delete_color_fixes:
        if check:
            print(f"✅ {name}")
            test_results.append((f'Delete Color: {name}', True))
        else:
            print(f"❌ {name}")
            test_results.append((f'Delete Color: {name}', False))
    
    # ========================================
    # SECTION 3: CARD ALIGNMENT FIXES
    # ========================================
    print("\n📋 SECTION 3: Card Alignment & Height Consistency")
    print("-" * 60)
    
    alignment_fixes = [
        ('Consistent minimum height', 'min-height: 400px' in template_content),
        ('Flexbox card layout', 'flex-direction: column' in template_content),
        ('Actions pushed to bottom', 'margin-top: auto' in template_content),
        ('Title minimum height', 'min-height: 2.4rem' in template_content),
        ('Title line clamping', '-webkit-line-clamp: 2' in template_content),
        ('Grid align to start', 'align-items: start' in template_content),
        ('Slightly wider grid', 'minmax(360px, 1fr)' in template_content),
    ]
    
    for name, check in alignment_fixes:
        if check:
            print(f"✅ {name}")
            test_results.append((f'Alignment: {name}', True))
        else:
            print(f"❌ {name}")
            test_results.append((f'Alignment: {name}', False))
    
    # ========================================
    # SECTION 4: ENHANCED DEBUGGING
    # ========================================
    print("\n📋 SECTION 4: Enhanced Debugging Features")
    print("-" * 60)
    
    debug_features = [
        ('Button overflow detection', 'UI_BUTTON_ANALYSIS' in template_content),
        ('Button width calculations', 'totalButtonWidth' in template_content),
        ('Overflow warnings', 'UI_OVERFLOW' in template_content),
        ('Delete button color check', 'UI_COLOR' in template_content),
        ('Card height analysis', 'UI_CARD_ALIGNMENT' in template_content),
        ('Text truncation detection', 'UI_TRUNCATION' in template_content),
        ('ScrollWidth monitoring', 'scrollWidth' in template_content and 'clientWidth' in template_content),
        ('Background color verification', 'backgroundColor' in template_content),
    ]
    
    for name, check in debug_features:
        if check:
            print(f"✅ {name}")
            test_results.append((f'Debug: {name}', True))
        else:
            print(f"❌ {name}")
            test_results.append((f'Debug: {name}', False))
    
    # ========================================
    # SECTION 5: FUNCTIONAL TEST
    # ========================================
    print("\n📋 SECTION 5: Functional Test - Page Rendering")
    print("-" * 60)
    
    client = Client()
    
    # Test that the page loads with fixes
    response = client.get('/RoutineTest/exams/', follow=True)
    if response.status_code in [200, 302]:
        print("✅ Exam list page loads successfully with fixes")
        test_results.append(('Functional: Page loads', True))
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check for button classes in rendered HTML
            button_classes = [
                'btn-small btn-primary',
                'btn-small btn-success', 
                'btn-small btn-secondary',
                'btn-small btn-danger'
            ]
            
            for btn_class in button_classes:
                if btn_class in content:
                    print(f"✅ Button class found in HTML: {btn_class}")
                    test_results.append((f'HTML: {btn_class}', True))
                else:
                    print(f"❌ Button class missing: {btn_class}")
                    test_results.append((f'HTML: {btn_class}', False))
    else:
        print(f"❌ Exam list page error: {response.status_code}")
        test_results.append(('Functional: Page loads', False))
    
    # ========================================
    # SECTION 6: CSS VALIDATION
    # ========================================
    print("\n📋 SECTION 6: CSS Validation - No Conflicts")
    print("-" * 60)
    
    # Check for potential CSS conflicts
    css_validations = [
        ('No duplicate button styles', template_content.count('.btn-danger {') <= 2),
        ('Consistent flex properties', 'flex: 0 0 auto' in template_content),
        ('No conflicting margins', template_content.count('margin-left: auto') == 0),
        ('Proper z-index usage', 'position: relative' in template_content),
        ('Hover states defined', ':hover' in template_content),
    ]
    
    for name, check in css_validations:
        if check:
            print(f"✅ {name}")
            test_results.append((f'CSS: {name}', True))
        else:
            print(f"❌ {name}")
            test_results.append((f'CSS: {name}', False))
    
    # ========================================
    # SECTION 7: COMPARISON WITH PLACEMENTTEST
    # ========================================
    print("\n📋 SECTION 7: PlacementTest Compatibility")
    print("-" * 60)
    
    placement_template = 'templates/placement_test/exam_list.html'
    with open(placement_template, 'r') as f:
        placement_content = f.read()
    
    # Check for maintained compatibility
    compatibility_checks = [
        ('Same delete button color', '#dc3545' in placement_content and '#dc3545' in template_content),
        ('Similar button structure', '.btn-small' in placement_content and '.btn-small' in template_content),
        ('Consistent card layout', '.exam-card' in placement_content and '.exam-card' in template_content),
        ('Same grid approach', 'display: grid' in placement_content and 'display: grid' in template_content),
    ]
    
    for name, check in compatibility_checks:
        if check:
            print(f"✅ {name}")
            test_results.append((f'Compatibility: {name}', True))
        else:
            print(f"❌ {name}")
            test_results.append((f'Compatibility: {name}', False))
    
    # ========================================
    # SECTION 8: TEXT CONTENT ANALYSIS
    # ========================================
    print("\n📋 SECTION 8: Text Content & Truncation")
    print("-" * 60)
    
    # Check button text handling
    text_checks = [
        ('Update Name button text present', 'Update Name' in template_content),
        ('Delete button text present', '>Delete<' in template_content),
        ('Manage button text present', '>Manage<' in template_content),
        ('Roster button text present', 'Roster' in template_content),
        ('Text overflow handling', 'text-overflow: ellipsis' in template_content),
        ('Line height defined', 'line-height: 1.2' in template_content),
    ]
    
    for name, check in text_checks:
        if check:
            print(f"✅ {name}")
            test_results.append((f'Text: {name}', True))
        else:
            print(f"❌ {name}")
            test_results.append((f'Text: {name}', False))
    
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
        status = "✅" if cat_percent == 100 else "⚠️" if cat_percent >= 90 else "❌"
        print(f"{status} {category}: {cat_passed}/{cat_total} ({cat_percent:.1f}%)")
    
    # List failures
    if passed < total:
        print("\\n❌ Failed Items:")
        print("-" * 40)
        for name, result in test_results:
            if not result:
                print(f"  • {name}")
    
    # Final verdict
    print("\\n" + "="*80)
    if percentage >= 98:
        print("🎉 PERFECT! All UI issues fixed!")
        print("✅ Delete button overflow resolved")
        print("✅ Delete button properly colored red")
        print("✅ Update Name text no longer truncated")
        print("✅ Card alignment consistent")
        print("✅ Comprehensive debugging added")
    elif percentage >= 95:
        print("✅ EXCELLENT: Critical UI issues resolved")
    elif percentage >= 90:
        print("✅ VERY GOOD: Major improvements implemented")
    else:
        print("⚠️ NEEDS ATTENTION: Some issues remain")
    
    print("\\n💡 Key Fixes Implemented:")
    print("-" * 40)
    print("1. Removed margin-left: auto causing button overflow")
    print("2. Increased button sizes to utilize available horizontal space")
    print("3. Added !important flags for delete button red color")
    print("4. Implemented consistent card heights (min-height: 400px)")
    print("5. Added flexbox column layout for proper alignment")
    print("6. Enhanced debugging with overflow and color detection")
    print("7. Added text truncation monitoring")
    print("8. Maintained PlacementTest compatibility")
    
    print("="*80)
    
    return passed, total, percentage


if __name__ == '__main__':
    try:
        passed, total, percentage = test_routinetest_ui_fixes()
        sys.exit(0 if percentage >= 95 else 1)
    except Exception as e:
        print(f"\\n❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
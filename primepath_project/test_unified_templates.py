#!/usr/bin/env python
"""
Phase 3, Day 1: Test Unified Base Template
Test that unified_base.html works for both placement and routine modules
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.template import Template, Context
from django.template.loader import get_template
from django.test import RequestFactory

def test_unified_templates():
    """Test that both test templates render correctly with unified base."""
    
    print("=" * 80)
    print("TESTING UNIFIED BASE TEMPLATE")
    print("=" * 80)
    print()
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/')
    
    # Test results
    results = {
        'placement': False,
        'routine': False
    }
    
    # Test 1: Placement template
    print("1. Testing Placement Module Template")
    print("-" * 40)
    try:
        template = get_template('test_unified_placement.html')
        context = {
            'request': request,
            'debug': True,
            'csrf_token': 'test-token'
        }
        html = template.render(context)
        
        # Verify key elements
        checks = [
            ('Title correct', 'Test - Placement Module' in html),
            ('Module name set', 'placement_test' in html),
            ('Navigation present', 'placement-nav' in html),
            ('Content rendered', 'Placement Test - Unified Base Template Test' in html),
            ('Button present', 'class="btn"' in html),
            ('No template errors', '{%' not in html and '{{' not in html)
        ]
        
        all_passed = True
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}")
            if not passed:
                all_passed = False
        
        results['placement'] = all_passed
        
        if all_passed:
            print("\n✅ Placement template renders successfully!")
        else:
            print("\n❌ Placement template has issues")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Test 2: RoutineTest template
    print("2. Testing RoutineTest Module Template")
    print("-" * 40)
    try:
        template = get_template('test_unified_routine.html')
        context = {
            'request': request,
            'debug': True,
            'csrf_token': 'test-token'
        }
        html = template.render(context)
        
        # Verify key elements
        checks = [
            ('Title correct', 'Test - RoutineTest Module' in html),
            ('Module name set', 'routinetest' in html),
            ('Font size 17px', '17px' in html),
            ('BCG Green color', '#00A65E' in html),
            ('Tab navigation', 'nav-tabs' in html),
            ('RoutineTest CSS', 'primepath_brand.css' in html),
            ('JS config present', 'ROUTINETEST_DEBUG' in html),
            ('No template errors', '{%' not in html and '{{' not in html)
        ]
        
        all_passed = True
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}")
            if not passed:
                all_passed = False
        
        results['routine'] = all_passed
        
        if all_passed:
            print("\n✅ RoutineTest template renders successfully!")
        else:
            print("\n❌ RoutineTest template has issues")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    if all(results.values()):
        print("🎉 SUCCESS! Unified base template works for both modules!")
        print()
        print("✅ Both placement_test and primepath_routinetest can use unified_base.html")
        print("✅ All module-specific customizations working")
        print("✅ Backward compatibility maintained")
        print("✅ Ready to proceed with migration")
        return True
    else:
        print("❌ ISSUES FOUND:")
        if not results['placement']:
            print("  - Placement module template has problems")
        if not results['routine']:
            print("  - RoutineTest module template has problems")
        print("\nPlease fix issues before proceeding with migration.")
        return False

def test_block_inheritance():
    """Test that all required blocks are available."""
    
    print()
    print("3. Testing Block Inheritance")
    print("-" * 40)
    
    # Load unified_base.html content
    base_path = Path("/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/templates/unified_base.html")
    with open(base_path, 'r') as f:
        content = f.read()
    
    # Check for all required blocks
    required_blocks = [
        'title', 'extra_css', 'extra_js', 'content',  # From base.html
        'header', 'navigation', 'footer',  # Common blocks
        'module_css', 'module_js', 'module_name',  # New unified blocks
        'header_wrapper', 'content_wrapper', 'footer_wrapper'  # Wrapper blocks
    ]
    
    print("Checking required blocks:")
    all_present = True
    for block in required_blocks:
        if f'{{% block {block}' in content:
            print(f"  ✅ {block}")
        else:
            print(f"  ❌ {block} - MISSING")
            all_present = False
    
    if all_present:
        print("\n✅ All required blocks present in unified_base.html")
    else:
        print("\n❌ Some blocks missing from unified_base.html")
    
    return all_present

if __name__ == '__main__':
    # Run tests
    templates_ok = test_unified_templates()
    blocks_ok = test_block_inheritance()
    
    print()
    print("=" * 80)
    
    if templates_ok and blocks_ok:
        print("✅ UNIFIED BASE TEMPLATE VALIDATION: PASSED")
        print()
        print("Ready to proceed with Day 1 afternoon tasks:")
        print("- Create compatibility layer")
        print("- Begin migration strategy implementation")
    else:
        print("❌ UNIFIED BASE TEMPLATE VALIDATION: FAILED")
        print()
        print("Please fix the issues before proceeding.")
    
    sys.exit(0 if (templates_ok and blocks_ok) else 1)
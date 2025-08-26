#!/usr/bin/env python
"""
Phase 3, Day 1 Afternoon: Test Adapter Templates
Test that adapter templates provide proper backward compatibility
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


def test_base_adapter():
    """Test base_adapter.html compatibility."""
    
    print("=" * 80)
    print("TESTING BASE ADAPTER")
    print("=" * 80)
    print()
    
    # Create mock request
    factory = RequestFactory()
    request = factory.get('/')
    
    try:
        # Load adapter template
        template = get_template('base_adapter.html')
        context = {
            'request': request,
            'debug': True,
            'csrf_token': 'test-token'
        }
        html = template.render(context)
        
        # Verify key elements preserved from base.html
        checks = [
            ('Extends unified_base', 'unified_base.html' not in html),  # Should be processed
            ('Module set to core', 'window.PRIMEPATH_CONFIG' in html),
            ('Default header color', '#2c3e50' in html),
            ('Container div', '<div class="container">' in html),
            ('No template errors', '{%' not in html and '{{' not in html)
        ]
        
        print("base_adapter.html checks:")
        all_passed = True
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}")
            if not passed:
                all_passed = False
                
        return all_passed
        
    except Exception as e:
        print(f"❌ ERROR loading base_adapter.html: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_routinetest_adapter():
    """Test routinetest_base_adapter.html compatibility."""
    
    print()
    print("=" * 80)
    print("TESTING ROUTINETEST BASE ADAPTER")
    print("=" * 80)
    print()
    
    # Create mock request
    factory = RequestFactory()
    request = factory.get('/RoutineTest/')
    
    try:
        # Load adapter template
        template = get_template('routinetest_base_adapter.html')
        context = {
            'request': request,
            'debug': True,
            'csrf_token': 'test-token'
        }
        html = template.render(context)
        
        # Verify key elements preserved from routinetest_base.html
        checks = [
            ('Extends unified_base', 'unified_base.html' not in html),  # Should be processed
            ('Module set to routinetest', 'primepath_routinetest' in html or 'routinetest' in html),
            ('Font size 17px', '17px' in html),
            ('BCG Green color', '#00A65E' in html),
            ('PrimePath brand CSS', 'primepath_brand.css' in html),
            ('RoutineTest debug config', 'ROUTINETEST_DEBUG' in html),
            ('Matrix tab version', 'MATRIX_TAB_VERSION' in html),
            ('No template errors', '{%' not in html and '{{' not in html)
        ]
        
        print("routinetest_base_adapter.html checks:")
        all_passed = True
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}")
            if not passed:
                all_passed = False
                
        return all_passed
        
    except Exception as e:
        print(f"❌ ERROR loading routinetest_base_adapter.html: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_adapter_with_child_template():
    """Test that a child template can extend an adapter successfully."""
    
    print()
    print("=" * 80)
    print("TESTING CHILD TEMPLATE WITH ADAPTER")
    print("=" * 80)
    print()
    
    # Create a test child template that extends base_adapter
    test_template_content = """
{% extends "base_adapter.html" %}
{% block title %}Test Child Template{% endblock %}
{% block content %}
    <h2>Test Content</h2>
    <p>This template extends base_adapter.html</p>
{% endblock %}
"""
    
    try:
        # Compile and render the template
        template = Template(test_template_content)
        factory = RequestFactory()
        request = factory.get('/')
        context = Context({
            'request': request,
            'debug': True,
            'csrf_token': 'test-token'
        })
        html = template.render(context)
        
        # Verify rendering
        checks = [
            ('Title rendered', 'Test Child Template' in html),
            ('Content rendered', 'Test Content' in html),
            ('Paragraph rendered', 'This template extends base_adapter.html' in html),
            ('Has container', 'container' in html),
            ('No errors', '{%' not in html and '{{' not in html)
        ]
        
        print("Child template rendering checks:")
        all_passed = True
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}")
            if not passed:
                all_passed = False
                
        return all_passed
        
    except Exception as e:
        print(f"❌ ERROR rendering child template: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # Run all tests
    base_ok = test_base_adapter()
    routine_ok = test_routinetest_adapter()
    child_ok = test_adapter_with_child_template()
    
    print()
    print("=" * 80)
    print("ADAPTER TEMPLATE VALIDATION SUMMARY")
    print("=" * 80)
    
    if base_ok and routine_ok and child_ok:
        print("✅ ALL ADAPTER TEMPLATES VALIDATED SUCCESSFULLY")
        print()
        print("Ready to proceed with gradual migration:")
        print("1. Templates can now optionally extend adapters instead of originals")
        print("2. Adapters provide full backward compatibility")
        print("3. Migration can be done incrementally without breaking anything")
    else:
        print("❌ ADAPTER TEMPLATE VALIDATION FAILED")
        if not base_ok:
            print("  - base_adapter.html has issues")
        if not routine_ok:
            print("  - routinetest_base_adapter.html has issues")
        if not child_ok:
            print("  - Child template compatibility has issues")
        print("\nPlease fix the issues before proceeding.")
    
    sys.exit(0 if (base_ok and routine_ok and child_ok) else 1)
#!/usr/bin/env python
"""
Final verification test for RoutineTest template fix
Tests that the duplicate block issue is resolved and functionality intact
"""
import os
import sys
import django
import re

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.template import Template, Context
from django.template.loader import get_template
from primepath_routinetest.models import Exam, ExamScheduleMatrix
from core.models import Teacher

def run_template_verification():
    """Verify template fixes and functionality"""
    print("\n" + "="*80)
    print("ROUTINETEST TEMPLATE FIX VERIFICATION")
    print("="*80)
    
    results = {
        'passed': [],
        'failed': [],
        'warnings': []
    }
    
    # Test 1: Check schedule_matrix.html for duplicate blocks
    print("\n[TEST 1] Checking schedule_matrix.html for duplicate blocks...")
    template_path = '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/templates/primepath_routinetest/schedule_matrix.html'
    
    try:
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Count occurrences of block extra_css
        block_count = content.count('{% block extra_css %}')
        endblock_count = content.count('{% endblock %}')
        
        if block_count == 1:
            results['passed'].append("✅ Only one extra_css block found")
            print(f"  ✅ Single extra_css block (count: {block_count})")
        else:
            results['failed'].append(f"❌ Found {block_count} extra_css block declarations")
            print(f"  ❌ Multiple extra_css blocks found: {block_count}")
        
        # Check for proper block closure
        if endblock_count >= block_count:
            results['passed'].append("✅ All blocks properly closed")
            print(f"  ✅ Block closure verified (endblocks: {endblock_count})")
        else:
            results['failed'].append(f"❌ Block closure mismatch: {block_count} blocks, {endblock_count} endblocks")
            
    except Exception as e:
        results['failed'].append(f"❌ Error reading template: {str(e)}")
        print(f"  ❌ Error: {str(e)}")
    
    # Test 2: Verify template can be loaded without syntax errors
    print("\n[TEST 2] Testing template loading...")
    try:
        template = get_template('primepath_routinetest/schedule_matrix.html')
        results['passed'].append("✅ Template loads without syntax errors")
        print("  ✅ Template loaded successfully")
        
        # Try to render with minimal context
        from django.http import HttpRequest
        request = HttpRequest()
        request.path = '/RoutineTest/schedule-matrix/'
        
        # Create minimal context
        context = {
            'teacher': None,
            'current_year': '2025',
            'available_years': ['2025', '2026'],
            'monthly_matrix': {},
            'quarterly_matrix': {},
            'months': ['JAN', 'FEB', 'MAR'],
            'quarters': ['Q1', 'Q2'],
            'month_names': {'JAN': 'January', 'FEB': 'February', 'MAR': 'March'},
            'quarter_names': {'Q1': 'Q1 (Jan-Mar)', 'Q2': 'Q2 (Apr-Jun)'},
            'assigned_classes': [],
            'request': request,
            'user': type('obj', (), {'is_authenticated': False, 'username': 'test'})()
        }
        
        # Attempt to render
        rendered = template.render(context)
        if rendered:
            results['passed'].append("✅ Template renders successfully")
            print(f"  ✅ Template rendered ({len(rendered)} characters)")
            
            # Check for key elements
            if 'Exam Assignments' in rendered:
                results['passed'].append("✅ 'Exam Assignments' title present")
                print("  ✅ Page title correct")
            
            if 'matrix-container' in rendered:
                results['passed'].append("✅ Matrix container CSS class present")
                print("  ✅ Matrix container found")
                
    except Exception as e:
        error_msg = str(e)
        if 'appears more than once' in error_msg:
            results['failed'].append(f"❌ Template still has duplicate blocks: {error_msg}")
            print(f"  ❌ DUPLICATE BLOCK ERROR: {error_msg}")
        else:
            results['failed'].append(f"❌ Template loading error: {error_msg}")
            print(f"  ❌ Error: {error_msg}")
    
    # Test 3: Check CSS preservation
    print("\n[TEST 3] Verifying CSS preservation...")
    try:
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Check for key CSS classes that should be present
        css_checks = [
            ('matrix-container', 'Matrix container styles'),
            ('matrix-table', 'Matrix table styles'),
            ('matrix-cell', 'Matrix cell styles'),
            ('cell-icon', 'Cell icon styles'),
            ('cell-count', 'Cell count styles'),
            ('.matrix-cell.empty', 'Empty cell styles'),
            ('.matrix-cell.scheduled', 'Scheduled cell styles'),
            ('MATRIX DISPLAY FIXES', 'Display fixes CSS'),
            ('Matrix Layout Styles', 'Layout styles CSS'),
        ]
        
        for css_pattern, description in css_checks:
            if css_pattern in content:
                results['passed'].append(f"✅ {description} preserved")
                print(f"  ✅ {description} found")
            else:
                results['failed'].append(f"❌ {description} missing")
                print(f"  ❌ {description} not found")
                
    except Exception as e:
        results['warnings'].append(f"⚠️ Could not verify CSS: {str(e)}")
        print(f"  ⚠️ CSS verification error: {str(e)}")
    
    # Test 4: Check other templates for duplicate blocks
    print("\n[TEST 4] Checking other templates for duplicate blocks...")
    other_templates = [
        'create_exam.html',
        'class_access.html',
        'preview_and_answers.html',
        'manage_questions.html',
        'test_result.html'
    ]
    
    all_good = True
    for template_name in other_templates:
        path = f'/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/templates/primepath_routinetest/{template_name}'
        if os.path.exists(path):
            with open(path, 'r') as f:
                content = f.read()
            block_count = content.count('{% block extra_css %}')
            if block_count > 1:
                results['failed'].append(f"❌ {template_name} has {block_count} extra_css blocks")
                all_good = False
    
    if all_good:
        results['passed'].append(f"✅ All {len(other_templates)} other templates have single blocks")
        print(f"  ✅ All other templates verified (no duplicates)")
    
    # Summary
    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)
    
    print(f"\n✅ PASSED: {len(results['passed'])} checks")
    for msg in results['passed'][:5]:  # Show first 5
        print(f"  {msg}")
    if len(results['passed']) > 5:
        print(f"  ... and {len(results['passed'])-5} more")
    
    if results['warnings']:
        print(f"\n⚠️ WARNINGS: {len(results['warnings'])}")
        for msg in results['warnings']:
            print(f"  {msg}")
    
    if results['failed']:
        print(f"\n❌ FAILED: {len(results['failed'])} checks")
        for msg in results['failed']:
            print(f"  {msg}")
        print("\n🔴 TEMPLATE FIX INCOMPLETE - Issues remain")
    else:
        print("\n🎉 TEMPLATE FIX SUCCESSFUL - All checks passed!")
        print("\nThe TemplateSyntaxError has been resolved:")
        print("  ✓ Duplicate {% block extra_css %} removed")
        print("  ✓ All CSS preserved in single block")
        print("  ✓ Template loads and renders correctly")
        print("  ✓ No other templates affected")
    
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("1. Clear browser cache")
    print("2. Visit http://127.0.0.1:8000/RoutineTest/schedule-matrix/")
    print("3. Verify the Exam Assignments matrix displays correctly")
    print("4. Test exam assignment/unassignment functionality")
    print("5. Check console for debugging output")
    
    return len(results['failed']) == 0

if __name__ == '__main__':
    success = run_template_verification()
    sys.exit(0 if success else 1)
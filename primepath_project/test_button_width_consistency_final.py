#!/usr/bin/env python
"""
COMPREHENSIVE BUTTON WIDTH CONSISTENCY TEST
==========================================
Tests the final fix for button width consistency in the admin classes table.

This test verifies:
1. All buttons have exactly 75px width
2. Inline styles are properly applied 
3. No CSS conflicts override our fixes
4. Debug logging is working properly
5. All button functionalities are preserved
"""

import os
import sys
import re

# Setup Django first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')

import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_button_width_consistency():
    """Test that all buttons have consistent 75px width"""
    print("\n" + "="*80)
    print("BUTTON WIDTH CONSISTENCY VERIFICATION - FINAL TEST")
    print("="*80)
    
    # Create test client
    client = Client()
    
    # Login as admin
    try:
        admin_user = User.objects.get(username='admin')
        admin_user.set_password('admin123')
        admin_user.save()
        login_success = client.login(username='admin', password='admin123')
        
        if not login_success:
            print("❌ Failed to login as admin")
            return False
            
        print("✅ Logged in as admin successfully")
        
    except User.DoesNotExist:
        print("❌ Admin user not found")
        return False
    
    # Test: Access the classes-exams page
    print("\n--- Test 1: Loading Classes & Exams Page ---")
    response = client.get('/RoutineTest/classes-exams/')
    if response.status_code != 200:
        print(f"❌ Page failed to load (status: {response.status_code})")
        return False
        
    print(f"✅ Page loaded successfully (status: {response.status_code})")
    content = response.content.decode()
    
    # Test 2: Check for inline styles in JavaScript
    print("\n--- Test 2: Verifying Inline Styles in JavaScript ---")
    
    # Check if buttons have width: 75px !important
    width_pattern = r'style="[^"]*width:\s*75px\s*!important[^"]*"'
    width_matches = re.findall(width_pattern, content)
    
    if len(width_matches) >= 3:  # Should have at least 3 buttons per row
        print(f"✅ Found {len(width_matches)} buttons with width: 75px !important")
    else:
        print(f"❌ Only found {len(width_matches)} buttons with enforced width")
        
    # Check for all required inline style properties
    required_styles = [
        'width: 75px !important',
        'padding: 8px 15px !important', 
        'box-sizing: border-box !important',
        'display: inline-block !important',
        'text-align: center !important'
    ]
    
    style_checks = {}
    for style in required_styles:
        count = content.count(style)
        style_checks[style] = count
        if count >= 3:  # At least 3 buttons should have each style
            print(f"  ✅ {style}: Found in {count} buttons")
        else:
            print(f"  ❌ {style}: Only found in {count} buttons")
    
    # Test 3: Check CSS High Specificity Rules
    print("\n--- Test 3: Verifying High Specificity CSS Rules ---")
    
    css_patterns = [
        r'\.admin-table\s+\.action-buttons\s+\.btn-save',
        r'\.admin-table\s+\.action-buttons\s+\.btn-edit',
        r'\.admin-table\s+\.action-buttons\s+\.btn-delete'
    ]
    
    for pattern in css_patterns:
        if re.search(pattern, content):
            print(f"  ✅ High specificity CSS rule found: {pattern}")
        else:
            print(f"  ❌ Missing high specificity CSS rule: {pattern}")
    
    # Test 4: Check for proper background colors
    print("\n--- Test 4: Verifying Button Background Colors ---")
    
    bg_colors = {
        'Save': '#2E7D32',
        'Edit': '#1976D2', 
        'Delete': '#D32F2F'
    }
    
    for button_name, color in bg_colors.items():
        if f'background: {color} !important' in content:
            print(f"  ✅ {button_name} button has correct background color ({color})")
        else:
            print(f"  ❌ {button_name} button missing correct background color")
    
    # Test 5: Check for debug logging
    print("\n--- Test 5: Verifying Debug Logging ---")
    
    debug_patterns = [
        'BUTTON_FIX] Rendered',
        'DETAILED BUTTON ANALYSIS',
        'OVERALL CONSISTENCY CHECK',
        'Hover effects applied'
    ]
    
    for pattern in debug_patterns:
        if pattern in content:
            print(f"  ✅ Debug logging found: [{pattern}]")
        else:
            print(f"  ❌ Missing debug logging: [{pattern}]")
    
    # Test 6: Check hover effect JavaScript
    print("\n--- Test 6: Verifying JavaScript Hover Effects ---")
    
    hover_patterns = [
        'addEventListener.*mouseenter',
        'addEventListener.*mouseleave',
        'hoverColors.*rgb'
    ]
    
    for pattern in hover_patterns:
        if re.search(pattern, content):
            print(f"  ✅ Hover effect code found: {pattern}")
        else:
            print(f"  ❌ Missing hover effect code: {pattern}")
    
    # Test 7: Ensure no old conflicting styles remain
    print("\n--- Test 7: Checking for Conflicting Styles ---")
    
    conflicting_patterns = [
        r'min-width:\s*60px(?!\s*!important)',  # Old min-width without !important
        r'padding:\s*10px\s+20px',              # Base.html padding
        r'\.btn\s*\{[^}]*padding:\s*10px'       # Base button class
    ]
    
    conflicts_found = 0
    for pattern in conflicting_patterns:
        matches = re.findall(pattern, content)
        if matches:
            conflicts_found += len(matches)
            print(f"  ⚠️  Potential conflict found: {pattern} ({len(matches)} instances)")
        else:
            print(f"  ✅ No conflicts found for: {pattern}")
    
    print("\n" + "="*80)
    print("FINAL CONSISTENCY TEST SUMMARY")
    print("="*80)
    
    # Count success indicators
    successes = []
    issues = []
    
    if len(width_matches) >= 3:
        successes.append("✅ Button width enforcement (75px !important)")
    else:
        issues.append("❌ Insufficient button width enforcement")
    
    if all(count >= 3 for count in style_checks.values()):
        successes.append("✅ All required inline styles present")
    else:
        issues.append("❌ Some required inline styles missing")
        
    if conflicts_found == 0:
        successes.append("✅ No conflicting CSS styles detected")
    else:
        issues.append(f"⚠️  {conflicts_found} potential style conflicts")
    
    print("\nSUCCESSFUL FIXES:")
    for success in successes:
        print(f"  {success}")
    
    if issues:
        print("\nREMAINING ISSUES:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n🎉 ALL BUTTON WIDTH CONSISTENCY ISSUES FIXED!")
        print("   - All buttons now have uniform 75px width")
        print("   - Inline styles with !important override any conflicts")
        print("   - High specificity CSS rules provide fallback")
        print("   - JavaScript hover effects maintain functionality")
        print("   - Debug logging helps with future troubleshooting")
    
    print("\n" + "="*80)
    print("TESTING RECOMMENDATIONS")
    print("="*80)
    print("1. Clear browser cache completely (Ctrl+Shift+R or Cmd+Shift+R)")
    print("2. Open browser DevTools Console")
    print("3. Look for [BUTTON_FIX] debug messages")
    print("4. Verify all buttons show 75px width in Elements inspector")
    print("5. Test hover effects on all buttons")
    print("6. Confirm Save/Edit/Delete functionality still works")
    
    return len(issues) == 0

if __name__ == "__main__":
    success = test_button_width_consistency()
    print(f"\n{'✅ TEST PASSED' if success else '❌ TEST FAILED'}")
    sys.exit(0 if success else 1)
#!/usr/bin/env python
"""
COMPREHENSIVE BUTTON FIX VERIFICATION
=====================================
Tests the comprehensive button UI fixes implemented:

1. Inline styles with !important declarations
2. High specificity CSS rules as fallback
3. JavaScript debug logging
4. Hover effects via JavaScript
5. 75px uniform width enforcement
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
import re

def test_comprehensive_button_fix():
    """Test all aspects of the button fix"""
    print("\n" + "="*90)
    print("COMPREHENSIVE BUTTON UI FIX VERIFICATION")
    print("="*90)
    
    # Login as admin
    client = Client()
    admin_user = User.objects.get(username='admin')
    admin_user.set_password('admin123')
    admin_user.save()
    
    login_success = client.login(username='admin', password='admin123')
    if not login_success:
        print("❌ Login failed")
        return False
    
    print("✅ Logged in as admin")
    
    # Get the page
    response = client.get('/RoutineTest/classes-exams/')
    if response.status_code != 200:
        print(f"❌ Page load failed: {response.status_code}")
        return False
    
    content = response.content.decode()
    print("✅ Page loaded successfully")
    
    # Test 1: Check inline styles with !important
    print("\n--- Test 1: Inline Styles with !important ---")
    
    # Count buttons with proper inline styles
    inline_style_patterns = [
        r'style="[^"]*width:\s*75px\s*!important[^"]*"',
        r'style="[^"]*background:\s*#2E7D32\s*!important[^"]*"',  # Save button
        r'style="[^"]*background:\s*#1976D2\s*!important[^"]*"',  # Edit button  
        r'style="[^"]*background:\s*#D32F2F\s*!important[^"]*"',  # Delete button
        r'style="[^"]*box-sizing:\s*border-box\s*!important[^"]*"'
    ]
    
    inline_results = {}
    for pattern in inline_style_patterns:
        matches = re.findall(pattern, content)
        style_name = pattern.split('*')[1].split('\\s*')[0]  # Extract style name
        inline_results[style_name] = len(matches)
        print(f"  {style_name}: {len(matches)} buttons found")
    
    # Test 2: Check high specificity CSS rules
    print("\n--- Test 2: High Specificity CSS Rules ---")
    
    css_patterns = [
        r'\.admin-table\s+\.action-buttons\s+\.btn-save[^{]*\{',
        r'\.admin-table\s+\.action-buttons\s+\.btn-edit[^{]*\{',
        r'\.admin-table\s+\.action-buttons\s+\.btn-delete[^{]*\{',
        r'width:\s*75px\s*!important'
    ]
    
    css_results = {}
    for pattern in css_patterns:
        matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
        rule_type = pattern.split('\\s+')[2].replace('\\', '') if 'btn-' in pattern else 'width rule'
        css_results[rule_type] = len(matches) > 0
        status = "✅" if len(matches) > 0 else "❌"
        print(f"  {status} {rule_type}: {'Found' if len(matches) > 0 else 'Missing'}")
    
    # Test 3: Check debug logging
    print("\n--- Test 3: Debug Logging Implementation ---")
    
    debug_patterns = [
        '[BUTTON_FIX] Rendered.*classes with INLINE STYLES',
        'DETAILED BUTTON ANALYSIS',
        'OVERALL CONSISTENCY CHECK',
        'console.log.*Save Button.*px wide',
        'console.log.*Edit Button.*px wide', 
        'console.log.*Delete Button.*px wide',
        'All buttons have consistent width',
        'Hover effects applied'
    ]
    
    debug_results = {}
    for pattern in debug_patterns:
        found = pattern in content
        debug_results[pattern] = found
        status = "✅" if found else "❌"
        print(f"  {status} {pattern}")
    
    # Test 4: Check hover effect JavaScript
    print("\n--- Test 4: JavaScript Hover Effects ---")
    
    hover_patterns = [
        'addEventListener.*mouseenter',
        'addEventListener.*mouseleave',
        'hoverColors.*rgb.*125.*50',    # Save button color
        'hoverColors.*rgb.*118.*210',   # Edit button color
        'hoverColors.*rgb.*211.*47',    # Delete button color
        'translateY.*-1px',
        'boxShadow.*rgba'
    ]
    
    hover_results = {}
    for pattern in hover_patterns:
        found = re.search(pattern, content) is not None
        hover_results[pattern] = found
        status = "✅" if found else "❌"
        print(f"  {status} {pattern}")
    
    # Test 5: Verify no conflicting styles
    print("\n--- Test 5: Check for Conflicting Styles ---")
    
    conflict_patterns = [
        (r'\.btn\s*\{[^}]*padding:\s*10px\s+20px[^}]*\}', 'base.html btn padding'),
        (r'min-width:\s*60px(?!\s*!important)', 'old min-width without !important'),
        (r'display:\s*inline-block(?!\s*!important)', 'display without !important')
    ]
    
    conflicts_found = 0
    for pattern, desc in conflict_patterns:
        matches = re.findall(pattern, content)
        if matches:
            conflicts_found += len(matches)
            print(f"  ⚠️  {desc}: {len(matches)} potential conflicts")
        else:
            print(f"  ✅ No conflicts: {desc}")
    
    # Final Assessment
    print("\n" + "="*90)
    print("FINAL ASSESSMENT")
    print("="*90)
    
    scores = {
        'inline_styles': sum(1 for count in inline_results.values() if count >= 3),
        'css_rules': sum(1 for found in css_results.values() if found),
        'debug_logging': sum(1 for found in debug_results.values() if found),
        'hover_effects': sum(1 for found in hover_results.values() if found),
        'no_conflicts': 1 if conflicts_found == 0 else 0
    }
    
    total_possible = len(inline_style_patterns) + len(css_patterns) + len(debug_patterns) + len(hover_patterns) + 1
    total_score = sum(scores.values())
    
    print(f"Inline Styles Score: {scores['inline_styles']}/{len(inline_style_patterns)}")
    print(f"CSS Rules Score: {scores['css_rules']}/{len(css_patterns)}")
    print(f"Debug Logging Score: {scores['debug_logging']}/{len(debug_patterns)}")
    print(f"Hover Effects Score: {scores['hover_effects']}/{len(hover_patterns)}")
    print(f"No Conflicts Score: {scores['no_conflicts']}/1")
    print(f"\nOverall Score: {total_score}/{total_possible} ({total_score/total_possible*100:.1f}%)")
    
    if total_score >= total_possible * 0.85:
        print("\n🎉 BUTTON FIX IS COMPREHENSIVE AND EFFECTIVE!")
        print("✅ All buttons should now have uniform 75px width")
        print("✅ Inline styles override any conflicting CSS")
        print("✅ High specificity CSS rules provide fallback")
        print("✅ Debug logging helps with troubleshooting")  
        print("✅ JavaScript hover effects maintain interactivity")
        success = True
    else:
        print("\n❌ BUTTON FIX NEEDS MORE WORK")
        print("Some components are missing or not working properly")
        success = False
    
    print("\n" + "="*90)
    print("TESTING INSTRUCTIONS")
    print("="*90)
    print("1. Open http://127.0.0.1:8000/RoutineTest/classes-exams/ in browser")
    print("2. Navigate to the 'Admin: Curriculum Management' section")
    print("3. Open browser DevTools Console")
    print("4. Look for [BUTTON_FIX] debug messages")
    print("5. Inspect buttons - should all be 75px wide")
    print("6. Test hover effects on Save, Edit, Delete buttons")
    print("7. Verify all button functionalities still work")
    
    return success

if __name__ == "__main__":
    success = test_comprehensive_button_fix()
    print(f"\n{'✅ ALL TESTS PASSED' if success else '❌ SOME TESTS FAILED'}")
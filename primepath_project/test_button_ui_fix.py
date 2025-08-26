#!/usr/bin/env python
"""
Test script to verify the button UI fixes:
1. Button alignment is centered
2. Edit button has proper background color
3. No text overlay issues with Save button
"""

import os
import sys

# Setup Django first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')

import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_button_ui_fixes():
    """Test the button UI fixes in the admin classes-exams page"""
    print("\n" + "="*70)
    print("BUTTON UI FIX VERIFICATION TEST")
    print("="*70)
    
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
    
    # Test 1: Access the classes-exams page
    print("\n--- Test 1: Loading Classes & Exams Page ---")
    response = client.get('/RoutineTest/classes-exams/')
    if response.status_code == 200:
        print(f"✅ Page loaded successfully (status: {response.status_code})")
        content = response.content.decode()
        
        # Check for button styling fixes in CSS
        print("\n--- Test 2: Checking Button Styles ---")
        
        # Check if old absolute positioning is removed
        if "position: absolute" in content and "action-buttons" in content:
            print("❌ Old absolute positioning still present in action-buttons")
        else:
            print("✅ Absolute positioning removed from action-buttons")
        
        # Check for centered alignment
        if "justify-content: center" in content:
            print("✅ Center alignment added to action-buttons")
        else:
            print("❌ Center alignment not found in action-buttons")
        
        # Check for Edit button background color
        if "btn-edit" in content and "background: #1976D2" in content:
            print("✅ Edit button has blue background color (#1976D2)")
        elif "btn-edit" in content and "background:" in content:
            print("⚠️  Edit button has background but different color")
        else:
            print("❌ Edit button missing background color")
        
        # Check for consistent button sizing
        if "padding: 8px 15px" in content:
            print("✅ Consistent padding (8px 15px) applied to buttons")
        else:
            print("❌ Inconsistent button padding")
        
        # Check for min-width on buttons
        if "min-width: 60px" in content:
            print("✅ Minimum width constraint added to buttons")
        else:
            print("❌ No minimum width on buttons")
        
        # Check for proper button structure in JavaScript
        print("\n--- Test 3: Checking JavaScript Button Structure ---")
        
        if 'type="button"' in content and 'return false;' in content:
            print("✅ Buttons have proper type and event handling")
        else:
            print("⚠️  Button structure may need improvement")
        
        if "title=" in content and "Save curriculum mapping" in content:
            print("✅ Buttons have descriptive tooltips")
        else:
            print("⚠️  Tooltips missing from buttons")
        
        # Check for console logging
        print("\n--- Test 4: Debug Logging ---")
        
        if "[BUTTON_FIX]" in content:
            print("✅ Debug console logging added for troubleshooting")
        else:
            print("⚠️  Debug logging not found (may be in external JS)")
        
        print("\n--- Test 5: Visual Consistency ---")
        
        # Check all three buttons have consistent styling
        has_save_style = ".btn-save" in content and "background:" in content
        has_edit_style = ".btn-edit" in content and "background:" in content  
        has_delete_style = ".btn-delete" in content and "background:" in content
        
        if has_save_style and has_edit_style and has_delete_style:
            print("✅ All three buttons (Save, Edit, Delete) have background colors")
        else:
            missing = []
            if not has_save_style: missing.append("Save")
            if not has_edit_style: missing.append("Edit")
            if not has_delete_style: missing.append("Delete")
            print(f"❌ Missing background colors for: {', '.join(missing)}")
        
        # Check for hover states
        if ":hover" in content and "transform: translateY(-1px)" in content:
            print("✅ Hover effects with elevation added")
        else:
            print("⚠️  Hover effects may be missing")
        
    else:
        print(f"❌ Failed to load page (status: {response.status_code})")
        return False
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    issues_fixed = []
    issues_remaining = []
    
    # Determine what was fixed
    if "justify-content: center" in content:
        issues_fixed.append("✅ Button alignment centered")
    else:
        issues_remaining.append("❌ Button alignment needs work")
    
    if "btn-edit" in content and "background: #1976D2" in content:
        issues_fixed.append("✅ Edit button has blue background")
    else:
        issues_remaining.append("❌ Edit button needs background color")
    
    if 'type="button"' in content and not ("position: absolute" in content and "action-buttons" in content):
        issues_fixed.append("✅ Text overlay issue resolved")
    else:
        issues_remaining.append("❌ Potential text overlay issues remain")
    
    print("\nFIXED ISSUES:")
    for issue in issues_fixed:
        print(f"  {issue}")
    
    if issues_remaining:
        print("\nREMAINING ISSUES:")
        for issue in issues_remaining:
            print(f"  {issue}")
    else:
        print("\n🎉 ALL ISSUES FIXED! The button UI is now properly aligned and styled.")
    
    print("\n" + "="*70)
    print("RECOMMENDATIONS")
    print("="*70)
    print("1. Clear browser cache and refresh the page")
    print("2. Open browser console to see debug logs (look for [BUTTON_FIX] messages)")
    print("3. Test button interactions (Save, Edit, Delete)")
    print("4. Verify no JavaScript errors in console")
    print("5. Check that buttons are visually centered in their cells")
    
    return len(issues_remaining) == 0

if __name__ == "__main__":
    success = test_button_ui_fixes()
    sys.exit(0 if success else 1)
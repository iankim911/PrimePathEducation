#!/usr/bin/env python
"""
Test to verify the button width fixes for RoutineTest UI.
Checks that "Update Name" button has sufficient width to display without truncation.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()


def test_button_width_fixes():
    """Test that button widths have been increased to fix truncation."""
    print("\n" + "="*70)
    print("🔧 BUTTON WIDTH FIX VERIFICATION")
    print("="*70)
    
    template_path = 'templates/primepath_routinetest/exam_list.html'
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    print("\n📋 SECTION: Button Width Analysis")
    print("-" * 50)
    
    # Check base button sizing
    checks = [
        ('Base min-width increased', 'min-width: 85px' in template_content),
        ('Base max-width increased', 'max-width: 110px' in template_content),
        ('Update Name min-width increased', 'min-width: 100px' in template_content),
        ('Update Name max-width increased', 'max-width: 120px' in template_content),
        ('Normal gap restored', 'gap: 10px' in template_content),
        ('Normal font size restored', 'font-size: 0.9rem' in template_content),
        ('Generous padding', 'padding: 6px 10px' in template_content),
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check in checks:
        if check:
            print(f"✅ {name}")
            passed += 1
        else:
            print(f"❌ {name}")
    
    print(f"\n📊 Results: {passed}/{total} ({passed/total*100:.1f}%)")
    
    print("\n💡 Button Layout Summary:")
    print("-" * 50)
    print("OLD LAYOUT (causing truncation):")
    print("  • Base buttons: 68px-80px width")
    print("  • Update Name: 75px-85px width") 
    print("  • Gap: 8px")
    print("  • Font: 0.85rem/0.8rem")
    print("")
    print("NEW LAYOUT (generous sizing):")
    print("  • Base buttons: 85px-110px width (+17px-30px)")
    print("  • Update Name: 100px-120px width (+25px-35px)")
    print("  • Gap: 10px (+2px)")
    print("  • Font: 0.9rem (restored to normal)")
    
    print("\n🎯 Expected Result:")
    print("With 100px-120px width, 'Update Name' (11 characters)")
    print("should display completely without truncation!")
    
    if passed == total:
        print("\n🎉 ALL BUTTON WIDTH FIXES APPLIED!")
        print("✅ Update Name should no longer be cut off")
        print("✅ All buttons have generous sizing")
        print("✅ Utilizing available horizontal space")
        return True
    else:
        print(f"\n⚠️ {total-passed} fixes still needed")
        return False


if __name__ == '__main__':
    success = test_button_width_fixes()
    sys.exit(0 if success else 1)
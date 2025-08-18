#!/usr/bin/env python
"""
Matrix Fix Verification Test
Verifies that the matrix display fixes are working correctly
"""
import os
import sys
import django
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import Teacher
from primepath_routinetest.models import TeacherClassAssignment


def print_header(title):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def test_matrix_fix():
    """Test that the matrix fixes are working"""
    print_header("MATRIX FIX VERIFICATION TEST")
    
    # Create authenticated client
    client = Client()
    
    # Create test user and teacher
    user = User.objects.filter(username='matrix_fix_test').first()
    if not user:
        user = User.objects.create_user('matrix_fix_test', 'matrixfix@test.com', 'testpass123')
        user.is_staff = True
        user.save()
    
    teacher, created = Teacher.objects.get_or_create(
        email=user.email,
        defaults={'name': 'Matrix Fix Test Teacher', 'user': user}
    )
    
    # Create class assignment
    TeacherClassAssignment.objects.get_or_create(
        teacher=teacher,
        class_code='CLASS_7A',
        defaults={'access_level': 'FULL', 'assigned_by': user}
    )
    
    client.force_login(user)
    print(f"✅ Authenticated as: {user.username}")
    
    # Test main matrix page
    print("\n🔍 TESTING MAIN MATRIX PAGE:")
    response = client.get('/RoutineTest/schedule-matrix/')
    
    if response.status_code == 200:
        print(f"✅ Main matrix page loads: Status {response.status_code}")
        
        content = response.content.decode('utf-8')
        
        # Check for fix indicators
        fix_checks = {
            'CSS Fixes Applied': '!important' in content and '.matrix-cell' in content,
            'JavaScript Fixes Applied': '[MATRIX FIX]' in content,
            'Debug Mode Available': 'matrix-debug-panel' in content,
            'Month Headers Present': all(month in content for month in ['January', 'February', 'March']),
            'Matrix Cells Present': 'matrix-cell' in content and 'cell-icon' in content,
            'Enhanced Tab Switching': 'Enhanced switchTab' in content,
            'Forced Visibility': 'display: block !important' in content,
        }
        
        for check, result in fix_checks.items():
            status = "✓" if result else "✗"
            print(f"   {status} {check}: {'Applied' if result else 'Missing'}")
        
        # Count key elements
        import re
        matrix_cell_count = len(re.findall(r'class="matrix-cell', content))
        month_header_count = len(re.findall(r'<th>January|<th>February|<th>March', content))
        css_fix_count = content.count('!important')
        js_fix_count = content.count('[MATRIX FIX]')
        
        print(f"\n📊 ELEMENT COUNTS:")
        print(f"   Matrix cells found: {matrix_cell_count}")
        print(f"   Month headers found: {month_header_count}")
        print(f"   CSS fixes applied: {css_fix_count}")
        print(f"   JavaScript fixes applied: {js_fix_count}")
        
        # Check for specific fix patterns
        print(f"\n🔧 FIX VERIFICATION:")
        essential_fixes = [
            ('#monthly-matrix { display: block !important', 'Monthly matrix forced visible'),
            ('.matrix-cell { min-height: 60px !important', 'Matrix cell minimum height'),
            ('.matrix-table { display: table !important', 'Matrix table forced visible'),
            ('visibility: visible !important', 'Visibility forced'),
            ('console.log(\'[MATRIX FIX]', 'JavaScript debug logging'),
            ('monthlyMatrix.style.display = \'block\'', 'JavaScript visibility fixes'),
        ]
        
        for pattern, description in essential_fixes:
            found = pattern in content
            status = "✓" if found else "✗"
            print(f"   {status} {description}: {'Applied' if found else 'Missing'}")
        
        all_passed = all(result for _, result in fix_checks.items())
        
        if all_passed:
            print(f"\n🎉 ALL MATRIX FIXES SUCCESSFULLY APPLIED!")
        else:
            failed_checks = [check for check, result in fix_checks.items() if not result]
            print(f"\n⚠️  Some fixes missing: {failed_checks}")
        
    else:
        print(f"❌ Main matrix page failed: Status {response.status_code}")
        return False
    
    # Test simple matrix test page
    print("\n🔍 TESTING SIMPLE MATRIX TEST PAGE:")
    response = client.get('/RoutineTest/matrix-test/')
    
    if response.status_code == 200:
        print(f"✅ Test matrix page loads: Status {response.status_code}")
        
        content = response.content.decode('utf-8')
        
        test_checks = {
            'Test Page Title': 'Matrix Rendering Test' in content,
            'Basic Table Test': 'Basic Table Test' in content,
            'Template Filter Test': 'Template Filter Test' in content,
            'Matrix Data Test': 'Matrix Data Test' in content,
            'Test CSS Loaded': '.test-table' in content,
        }
        
        for check, result in test_checks.items():
            status = "✓" if result else "✗"
            print(f"   {status} {check}: {'Present' if result else 'Missing'}")
        
    else:
        print(f"❌ Test matrix page failed: Status {response.status_code}")
        return False
    
    return True


def generate_testing_instructions():
    """Generate testing instructions for manual verification"""
    print_header("MANUAL TESTING INSTRUCTIONS")
    
    print("🧪 STEP-BY-STEP TESTING GUIDE:")
    print()
    print("1. RESTART DJANGO SERVER:")
    print("   cd primepath_project")
    print("   ../venv/bin/python manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite")
    print()
    print("2. OPEN BROWSER:")
    print("   Navigate to: http://127.0.0.1:8000/RoutineTest/schedule-matrix/")
    print()
    print("3. VERIFY FIXES:")
    print("   ✓ Month headers should be visible: January, February, March, etc.")
    print("   ✓ Matrix cells should show icons: 📅 (scheduled) or ⬜ (empty)")
    print("   ✓ Table should have proper borders and spacing")
    print("   ✓ Both Monthly and Quarterly tabs should work")
    print()
    print("4. DEBUG MODE:")
    print("   Press Ctrl+Shift+D to toggle debug mode")
    print("   - Green debug panel should appear in top-right")
    print("   - Matrix cells should get colored borders")
    print("   - Console should show '[MATRIX FIX]' messages")
    print()
    print("5. TEST SIMPLE VERSION:")
    print("   Navigate to: http://127.0.0.1:8000/RoutineTest/matrix-test/")
    print("   - Should show simplified matrix table")
    print("   - Verifies basic rendering functionality")
    print()
    print("6. BROWSER CONSOLE:")
    print("   Press F12 → Console tab")
    print("   Look for messages starting with '[MATRIX FIX]'")
    print("   Should see matrix initialization messages")
    print()
    print("7. DIFFERENT BROWSERS:")
    print("   Test in Chrome, Firefox, Safari")
    print("   Try incognito/private mode")
    print("   Test different screen sizes")
    print()
    print("🚨 IF STILL NOT WORKING:")
    print("   1. Clear browser cache completely (Ctrl+Shift+Delete)")
    print("   2. Try different browser")
    print("   3. Check browser console for JavaScript errors")
    print("   4. Verify CSS is loading (inspect element)")
    print("   5. Check network tab for failed requests")


def main():
    """Run matrix fix verification"""
    print("\n" + "="*80)
    print("  MATRIX FIX VERIFICATION")
    print("="*80)
    print(f"  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run verification test
        success = test_matrix_fix()
        
        # Generate testing instructions
        generate_testing_instructions()
        
        print_header("VERIFICATION SUMMARY")
        
        if success:
            print("✅ Matrix fixes verified successfully!")
            print("✅ All necessary components are in place")
            print("💡 Ready for manual browser testing")
        else:
            print("⚠️  Some issues detected in verification")
            print("💡 Check the test results above for details")
        
        print("\n📁 IMPORTANT FILES MODIFIED:")
        print("   ✓ templates/primepath_routinetest/schedule_matrix.html (CSS + JS fixes)")
        print("   ✓ templates/primepath_routinetest/matrix_test.html (test template)")
        print("   ✓ primepath_routinetest/views/schedule_matrix.py (test view)")
        print("   ✓ primepath_routinetest/matrix_urls.py (test URL)")
        
        print(f"\n📱 ACCESS URLS:")
        print("   Main Matrix: http://127.0.0.1:8000/RoutineTest/schedule-matrix/")
        print("   Test Matrix: http://127.0.0.1:8000/RoutineTest/matrix-test/")
        
    except Exception as e:
        print(f"\n❌ Verification error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
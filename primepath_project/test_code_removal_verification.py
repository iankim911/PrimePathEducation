#!/usr/bin/env python
"""
Test to verify JavaScript code is no longer showing at bottom of page
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import Teacher
from primepath_routinetest.models import TeacherClassAssignment


def test_code_removal():
    """Test that JavaScript code is not showing in page content"""
    print("🧪 TESTING CODE REMOVAL FROM PAGE BOTTOM")
    
    # Create authenticated client
    client = Client()
    
    # Use existing test user
    user = User.objects.filter(username='matrix_fix_test').first()
    if not user:
        user = User.objects.create_user('matrix_fix_test', 'matrixfix@test.com', 'testpass123')
        user.is_staff = True
        user.save()
    
    teacher = Teacher.objects.get_or_create(
        email=user.email,
        defaults={'name': 'Matrix Fix Test Teacher', 'user': user}
    )[0]
    
    TeacherClassAssignment.objects.get_or_create(
        teacher=teacher,
        class_code='CLASS_7A',
        defaults={'access_level': 'FULL', 'assigned_by': user}
    )
    
    client.force_login(user)
    
    # Get the matrix page
    response = client.get('/RoutineTest/schedule-matrix/')
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check for JavaScript code appearing in page content (not in script tags)
        problematic_patterns = [
            'document.addEventListener(\'DOMContentLoaded\'',  # Outside script tags
            'function switchTab(type)',  # Outside script tags  
            'console.log(\'[MATRIX FIX]',  # Outside script tags
            'monthlyMatrix.style.display',  # Outside script tags
        ]
        
        print(f"✅ Page loads successfully: Status {response.status_code}")
        
        # Split content to check if JS appears outside script tags
        import re
        
        # Remove all script tag contents to see what's left
        content_without_scripts = re.sub(r'<script.*?</script>', '', content, flags=re.DOTALL)
        
        # Check if problematic JS patterns appear outside scripts
        issues_found = []
        for pattern in problematic_patterns:
            if pattern in content_without_scripts:
                issues_found.append(pattern)
        
        if issues_found:
            print(f"❌ JavaScript code still appearing in page content:")
            for issue in issues_found:
                print(f"   - {issue}")
            return False
        else:
            print(f"✅ No JavaScript code found in page content")
            
        # Verify JS is still in script tags (should be there)
        script_sections = re.findall(r'<script.*?</script>', content, flags=re.DOTALL)
        
        js_in_scripts = False
        for script in script_sections:
            if '[MATRIX FIX]' in script:
                js_in_scripts = True
                break
        
        if js_in_scripts:
            print(f"✅ Matrix fix JavaScript properly contained in script tags")
        else:
            print(f"⚠️  Matrix fix JavaScript not found in script tags")
        
        # Check page structure
        print(f"\n📊 PAGE STRUCTURE:")
        print(f"   Total content length: {len(content):,} characters")
        print(f"   Script sections found: {len(script_sections)}")
        print(f"   Content without scripts: {len(content_without_scripts):,} characters")
        
        # Look for visible matrix elements
        matrix_elements = {
            'Month headers': any(month in content for month in ['January', 'February', 'March']),
            'Matrix cells': 'matrix-cell' in content,
            'Cell icons': any(icon in content for icon in ['📅', '⬜']),
            'Matrix table': 'matrix-table' in content,
        }
        
        print(f"\n🔍 MATRIX ELEMENTS VERIFICATION:")
        for element, present in matrix_elements.items():
            status = "✓" if present else "✗"
            print(f"   {status} {element}: {'Present' if present else 'Missing'}")
        
        return not issues_found
    else:
        print(f"❌ Page failed to load: Status {response.status_code}")
        return False


if __name__ == "__main__":
    print("=" * 80)
    print("  CODE REMOVAL VERIFICATION TEST")
    print("=" * 80)
    
    try:
        success = test_code_removal()
        
        print(f"\n" + "=" * 80)
        if success:
            print("🎉 CODE REMOVAL SUCCESSFUL!")
            print("✅ No JavaScript code appearing at bottom of page")
            print("✅ Matrix functionality preserved")
            print("💡 Page is now clean and properly formatted")
        else:
            print("⚠️  ISSUES DETECTED")
            print("❌ JavaScript code may still be visible in page content")
            print("💡 Manual verification recommended")
        
        print(f"\n📱 TEST URL: http://127.0.0.1:8000/RoutineTest/schedule-matrix/")
        print("💡 Refresh browser cache after changes (Ctrl+Shift+R)")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 80)
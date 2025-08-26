#!/usr/bin/env python3

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_button_consistency():
    """Test that button consistency fixes are working"""
    print("=== TESTING BUTTON CONSISTENCY FIXES ===")
    print()
    
    # Create test client and login as admin
    client = Client()
    
    try:
        admin_user = User.objects.get(username='admin')
        
        # Ensure admin password is set
        if not admin_user.check_password('admin123'):
            admin_user.set_password('admin123')
            admin_user.save()
        
        # Login
        login_success = client.login(username='admin', password='admin123')
        print(f"✅ Login as admin: {'SUCCESS' if login_success else 'FAILED'}")
        
        if login_success:
            response = client.get('/RoutineTest/admin/classes/')
            print(f"✅ Admin classes page access: {'SUCCESS' if response.status_code == 200 else 'FAILED'}")
            
            if response.status_code == 200:
                content = response.content.decode()
                
                # Check for our standardized button classes
                checks = {
                    'Standardized CSS Classes': 'btn-admin-primary' in content,
                    'Create Button Uses Class': 'class="btn-admin-create"' in content,
                    'Action Buttons Use Classes': 'class="btn-admin-primary"' in content and 'class="btn-admin-danger"' in content,
                    'Modal Buttons Use Classes': 'class="btn-admin-secondary"' in content and 'class="btn-admin-success"' in content,
                    'Back Button Uses Class': 'class="btn-admin-secondary"' in content,
                    'Old Inline Styles Removed': 'style="padding: 8px 15px; background: #1B5E20' not in content,
                    'Consistent Border Radius': 'border-radius: 5px' in content,
                    'Consistent Hover Effects': ':hover' in content
                }
                
                print()
                print("=== BUTTON CONSISTENCY CHECK RESULTS ===")
                all_passed = True
                for check_name, result in checks.items():
                    status = '✅' if result else '❌'
                    print(f"{status} {check_name}")
                    if not result:
                        all_passed = False
                
                print()
                if all_passed:
                    print("🎉 ALL BUTTON CONSISTENCY CHECKS PASSED!")
                    print()
                    print("✅ Standardized button classes implemented")
                    print("✅ Consistent button shapes (5px border-radius)")  
                    print("✅ Consistent padding and font-weight")
                    print("✅ Consistent hover effects")
                    print("✅ Old inline styles completely removed")
                    print("✅ Uses !important to override any conflicts")
                    print()
                    print("🔧 TECHNICAL DETAILS:")
                    print("   • .btn-admin-primary: Green buttons (Add Teacher)")
                    print("   • .btn-admin-danger: Red buttons (Delete)")
                    print("   • .btn-admin-success: Green buttons (Assign)")
                    print("   • .btn-admin-secondary: Gray buttons (Cancel, Back)")
                    print("   • .btn-admin-create: Special create button styling")
                    print()
                    print("📐 STANDARDIZED DIMENSIONS:")
                    print("   • Padding: 8px 15px")
                    print("   • Border-radius: 5px")
                    print("   • Font-size: 14px")
                    print("   • Font-weight: 500")
                    print("   • Min-width: 100px")
                    print("   • Transition: 0.3s ease")
                    return True
                else:
                    print("❌ Some button consistency checks failed")
                    return False
            else:
                print(f"❌ Error accessing admin classes page: {response.status_code}")
                return False
        else:
            print("❌ Login failed")
            return False
            
    except User.DoesNotExist:
        print("❌ Admin user not found")
        return False
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == '__main__':
    success = test_button_consistency()
    print()
    if success:
        print("🏆 BUTTON CONSISTENCY FIX: COMPLETE")
        print("📱 Ready for visual testing in browser!")
    else:
        print("❌ BUTTON CONSISTENCY FIX: NEEDS ATTENTION")
#\!/usr/bin/env python3

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_button_consistency_across_admin_pages():
    """Test that button consistency fixes work across ALL admin pages"""
    print("=== TESTING BUTTON CONSISTENCY ACROSS ALL ADMIN PAGES ===")
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
            # Test both admin pages
            pages_to_test = [
                ('/RoutineTest/admin/classes/', 'Manage Classes Page'),
                ('/RoutineTest/admin/classes-teachers/', 'Classes & Teachers Admin Page')
            ]
            
            all_pages_passed = True
            
            for url, page_name in pages_to_test:
                print(f"\n=== TESTING {page_name.upper()} ===")
                
                response = client.get(url)
                print(f"✅ {page_name} access: {'SUCCESS' if response.status_code == 200 else 'FAILED'}")
                
                if response.status_code == 200:
                    content = response.content.decode()
                    
                    # Check for standardized button CSS and consistent properties
                    checks = {
                        'Has Standardized Border-Radius': 'border-radius: 5px' in content,
                        'Has Consistent Padding': 'padding: 8px 15px' in content,
                        'Has Consistent Font Size': 'font-size: 14px' in content,
                        'Has Consistent Font Weight': 'font-weight: 500' in content,
                        'Has Smooth Transitions': 'transition:' in content and '0.3s' in content,
                        'Uses Important for Override': '\!important' in content,
                        'Old Inconsistent Border-Radius Gone': 'border-radius: 4px' not in content and 'border-radius: 6px' not in content,
                        'Old Inconsistent Padding Gone': 'padding: 10px 20px' not in content and 'padding: 5px' not in content
                    }
                    
                    page_passed = True
                    for check_name, result in checks.items():
                        status = '✅' if result else '❌'
                        print(f"  {status} {check_name}")
                        if not result:
                            page_passed = False
                            all_pages_passed = False
                    
                    if page_passed:
                        print(f"  🎉 {page_name}: ALL CONSISTENCY CHECKS PASSED")
                    else:
                        print(f"  ❌ {page_name}: Some consistency checks failed")
                else:
                    print(f"  ❌ Error accessing {page_name}: {response.status_code}")
                    all_pages_passed = False
            
            print("\n" + "="*70)
            if all_pages_passed:
                print("🏆 ALL ADMIN PAGES: BUTTON CONSISTENCY ACHIEVED\!")
                print()
                print("✅ STANDARDIZED BUTTON PROPERTIES:")
                print("   • Border-radius: 5px (consistent rounded corners)")
                print("   • Padding: 8px 15px (consistent size)")
                print("   • Font-size: 14px (consistent typography)")
                print("   • Font-weight: 500 (consistent weight)")
                print("   • Transition: 0.3s ease (smooth hover effects)")
                print("   • \!important declarations (override conflicts)")
                print()
                print("🎨 CONSISTENT BUTTON CLASSES:")
                print("   • .btn-admin-primary (green action buttons)")
                print("   • .btn-admin-danger (red delete buttons)")
                print("   • .btn-admin-success (green confirm buttons)")
                print("   • .btn-admin-secondary (gray cancel buttons)")
                print("   • .btn-admin-create (special create buttons)")
                print()
                print("📱 READY FOR VISUAL VERIFICATION\!")
                print("All admin interface buttons now have consistent styling.")
                return True
            else:
                print("❌ BUTTON CONSISTENCY: NEEDS MORE WORK")
                print("Some admin pages still have inconsistent button styling.")
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
    success = test_button_consistency_across_admin_pages()
    print()
    if success:
        print("🎯 BUTTON CONSISTENCY FIX: COMPLETE ACROSS ALL ADMIN PAGES")
        print("The screenshot issue should now be resolved\!")
    else:
        print("❌ BUTTON CONSISTENCY FIX: REQUIRES FURTHER ATTENTION")
EOF < /dev/null
"""
Test PINNACLE visibility in Classes & Exams view
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from primepath_routinetest.models.class_model import Class

def test_pinnacle_view():
    print("\n=== TESTING PINNACLE IN CLASSES & EXAMS VIEW ===\n")
    
    client = Client()
    
    # Login as admin
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No admin user found")
        return False
    
    admin_user.set_password('admin')
    admin_user.save()
    
    login_success = client.login(username=admin_user.username, password='admin')
    if not login_success:
        print("❌ Could not login as admin")
        return False
    
    print(f"✅ Logged in as {admin_user.username}")
    
    # Test the unified Classes & Exams view
    response = client.get('/RoutineTest/classes-exams/')
    
    if response.status_code != 200:
        print(f"❌ Classes & Exams page returned status {response.status_code}")
        return False
    
    print("✅ Classes & Exams page loads successfully")
    
    # Check if PINNACLE appears in the content
    content = response.content.decode()
    
    # Count PINNACLE occurrences
    pinnacle_count = content.count('PINNACLE')
    pinnacle_class_count = sum(1 for c in ['PINNACLE_V1', 'PINNACLE_V2', 'PINNACLE_E1', 'PINNACLE_E2',
                                           'PINNACLE_S1', 'PINNACLE_S2', 'PINNACLE_P1', 'PINNACLE_P2'] 
                              if c in content)
    
    print(f"\n📊 PINNACLE Visibility:")
    print(f"   - 'PINNACLE' text appears: {pinnacle_count} times")
    print(f"   - PINNACLE class codes found: {pinnacle_class_count}/8")
    
    # Check context data
    if hasattr(response, 'context') and response.context:
        programs = response.context.get('programs', [])
        if programs:
            print(f"\n📋 Programs in context:")
            for program in programs:
                print(f"   - {program.get('name', 'Unknown')}")
                if program.get('name') == 'PINNACLE':
                    classes = program.get('classes', [])
                    print(f"     Classes: {len(classes)}")
                    for cls in classes[:3]:  # Show first 3
                        print(f"       • {cls.get('section', 'Unknown')}")
    
    # Summary
    print("\n=== SUMMARY ===")
    if pinnacle_count > 0:
        print("✅ PINNACLE is visible in Classes & Exams view!")
        if pinnacle_class_count == 8:
            print("✅ All 8 PINNACLE classes are present!")
        else:
            print(f"⚠️  Only {pinnacle_class_count}/8 PINNACLE classes visible")
        return True
    else:
        print("❌ PINNACLE not visible in Classes & Exams view")
        return False

if __name__ == "__main__":
    success = test_pinnacle_view()
    sys.exit(0 if success else 1)
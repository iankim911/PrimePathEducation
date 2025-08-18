#!/usr/bin/env python
"""
Test script for Admin Curriculum Management feature
Tests all the new functionality added for admin-only curriculum management
"""

import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from primepath_routinetest.models import ClassCurriculumMapping
from primepath_routinetest.models.class_constants import CLASS_CODE_CHOICES
from core.models import Teacher

def test_admin_curriculum_management():
    """Test the admin curriculum management functionality"""
    
    print("\n" + "="*70)
    print("ADMIN CURRICULUM MANAGEMENT TEST")
    print("="*70)
    
    client = Client()
    results = []
    
    # Step 1: Create admin user if not exists
    print("\n1. Setting up admin user...")
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'is_staff': True,
            'is_superuser': True,
            'email': 'admin@example.com'
        }
    )
    if created:
        admin_user.set_password('admin')
        admin_user.save()
        print("   ✅ Admin user created")
    else:
        print("   ✅ Admin user exists")
    
    # Ensure teacher profile exists
    teacher, _ = Teacher.objects.get_or_create(
        user=admin_user,
        defaults={
            'name': 'Admin Teacher',
            'is_head_teacher': True
        }
    )
    
    # Step 2: Login as admin
    print("\n2. Logging in as admin...")
    login_success = client.login(username='admin', password='admin')
    if login_success:
        print("   ✅ Login successful")
        results.append(("Admin Login", "PASS"))
    else:
        print("   ❌ Login failed")
        results.append(("Admin Login", "FAIL"))
        return results
    
    # Step 3: Test access to classes-exams page
    print("\n3. Testing access to Classes & Exams page...")
    response = client.get('/RoutineTest/classes-exams/')
    if response.status_code == 200:
        print("   ✅ Classes & Exams page accessible")
        results.append(("Classes & Exams Access", "PASS"))
        
        # Check if admin section is in the HTML
        content = response.content.decode('utf-8')
        if 'admin-section' in content or 'Curriculum Management' in content:
            print("   ✅ Admin section found in page")
            results.append(("Admin Section Visible", "PASS"))
        else:
            print("   ⚠️  Admin section not found in page HTML")
            results.append(("Admin Section Visible", "WARN"))
    else:
        print(f"   ❌ Page returned status {response.status_code}")
        results.append(("Classes & Exams Access", "FAIL"))
    
    # Step 4: Test API endpoint for getting all classes
    print("\n4. Testing admin API endpoints...")
    response = client.get('/RoutineTest/api/admin/classes/')
    if response.status_code == 200:
        print("   ✅ Admin classes API accessible")
        data = json.loads(response.content)
        print(f"   Found {len(data.get('classes', []))} classes")
        results.append(("Admin Classes API", "PASS"))
        
        # Show sample of classes
        if data.get('classes'):
            for cls in data['classes'][:3]:
                print(f"      - {cls['code']}: {cls['name']}")
                if cls.get('curriculum'):
                    print(f"        Curriculum: {cls['curriculum']}")
    else:
        print(f"   ❌ API returned status {response.status_code}")
        results.append(("Admin Classes API", "FAIL"))
    
    # Step 5: Test curriculum mapping creation
    print("\n5. Testing curriculum mapping creation...")
    test_class_code = 'PRIMARY_1A'  # Use a valid class code from constants
    
    mapping_data = {
        'class_code': test_class_code,
        'program': 'CORE',
        'subprogram': 'Phonics',
        'level': 1
    }
    
    response = client.post(
        '/RoutineTest/api/admin/curriculum-mapping/',
        data=json.dumps(mapping_data),
        content_type='application/json'
    )
    
    if response.status_code == 200:
        print(f"   ✅ Curriculum mapping created for {test_class_code}")
        results.append(("Create Curriculum Mapping", "PASS"))
        
        # Verify mapping was created
        mapping = ClassCurriculumMapping.objects.filter(
            class_code=test_class_code
        ).first()
        if mapping:
            print(f"      Verified in DB: {mapping}")
    else:
        print(f"   ❌ Mapping creation returned status {response.status_code}")
        if response.content:
            print(f"      Error: {response.content.decode('utf-8')}")
        results.append(("Create Curriculum Mapping", "FAIL"))
    
    # Step 6: Test that non-admin users cannot access
    print("\n6. Testing access control...")
    
    # Create regular teacher user
    teacher_user, created = User.objects.get_or_create(
        username='teacher1',
        defaults={
            'is_staff': False,
            'is_superuser': False,
            'email': 'teacher1@example.com'
        }
    )
    # Ensure teacher1 is not staff (in case it was already created as staff)
    teacher_user.is_staff = False
    teacher_user.is_superuser = False
    teacher_user.set_password('teacher123')
    teacher_user.save()
    
    # Login as regular teacher
    client.logout()
    client.login(username='teacher1', password='teacher123')
    
    response = client.get('/RoutineTest/api/admin/classes/')
    if response.status_code in [403, 302]:  # Forbidden or redirect to login
        print("   ✅ Non-admin access properly restricted")
        results.append(("Access Control", "PASS"))
    else:
        print(f"   ❌ Non-admin got status {response.status_code} (should be 403)")
        results.append(("Access Control", "FAIL"))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    pass_count = sum(1 for _, status in results if status == "PASS")
    total_count = len(results)
    
    for test_name, status in results:
        symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{symbol} {test_name}: {status}")
    
    print(f"\nTotal: {pass_count}/{total_count} tests passed")
    
    if pass_count == total_count:
        print("\n🎉 All tests passed! Admin curriculum management is working correctly.")
    elif pass_count > 0:
        print("\n⚠️  Some tests passed. Check the failures above.")
    else:
        print("\n❌ Tests failed. Please review the implementation.")
    
    return results

if __name__ == "__main__":
    test_admin_curriculum_management()
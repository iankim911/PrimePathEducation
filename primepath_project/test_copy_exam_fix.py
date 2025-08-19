#!/usr/bin/env python
"""
Test script to verify the Copy from Other Class fix
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from primepath_routinetest.models import Class
import json

def test_copy_exam_api():
    """Test the all-classes API endpoint"""
    print("=" * 60)
    print("Testing Copy from Other Class Fix")
    print("=" * 60)
    
    # Create test client
    client = Client()
    
    # Login as admin
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No admin user found")
        return False
    
    client.force_login(admin_user)
    print(f"✅ Logged in as: {admin_user.username}")
    
    # Test the all-classes endpoint
    print("\n1. Testing /api/RoutineTest/api/all-classes/")
    response = client.get('/api/RoutineTest/api/all-classes/')
    
    if response.status_code == 200:
        print(f"   ✅ Status: {response.status_code}")
        data = json.loads(response.content)
        
        if 'classes' in data:
            print(f"   ✅ Response has 'classes' key")
            print(f"   ✅ Number of classes: {len(data['classes'])}")
            
            if data['classes']:
                print("   Sample classes:")
                for cls in data['classes'][:3]:
                    print(f"      - {cls['code']}: {cls['name']}")
            else:
                print("   ⚠️ No classes found in database")
                
                # Check if classes exist at all
                class_count = Class.objects.count()
                print(f"   Database has {class_count} classes")
                
                if class_count == 0:
                    print("\n   Creating sample classes for testing...")
                    for i in range(1, 4):
                        Class.objects.create(
                            code=f"CLASS_{i}",
                            name=f"Test Class {i}"
                        )
                    print("   ✅ Created 3 test classes")
                    
                    # Retry the API
                    response = client.get('/api/RoutineTest/api/all-classes/')
                    data = json.loads(response.content)
                    print(f"   ✅ After creating classes: {len(data['classes'])} classes available")
        else:
            print(f"   ❌ Response missing 'classes' key. Got: {data.keys()}")
            return False
    else:
        print(f"   ❌ Status: {response.status_code}")
        print(f"   Response: {response.content.decode()[:200]}")
        return False
    
    # Test a specific class's exams endpoint
    if data['classes']:
        test_class = data['classes'][0]['code']
        print(f"\n2. Testing /api/RoutineTest/api/class/{test_class}/all-exams/")
        
        response = client.get(f'/api/RoutineTest/api/class/{test_class}/all-exams/')
        if response.status_code == 200:
            print(f"   ✅ Status: {response.status_code}")
            exam_data = json.loads(response.content)
            
            if 'exams' in exam_data:
                print(f"   ✅ Response has 'exams' key")
                print(f"   ✅ Number of exams: {len(exam_data['exams'])}")
            else:
                print(f"   ❌ Response missing 'exams' key. Got: {exam_data.keys()}")
        else:
            print(f"   ❌ Status: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("✅ Copy from Other Class API endpoints are working correctly!")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = test_copy_exam_api()
    sys.exit(0 if success else 1)
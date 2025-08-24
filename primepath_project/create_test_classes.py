#!/usr/bin/env python3
"""
Create test classes and assign them to the admin user for testing toggleClass functionality.
"""

import os
import sys
import django

# Add the project directory to the path
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from core.models import Teacher
from primepath_routinetest.models import TeacherClassAssignment, Exam

def create_test_data():
    print("🔧 Setting up test data for toggleClass functionality...")
    
    try:
        # Get admin user and teacher profile
        admin_user = User.objects.get(username='admin')
        teacher = Teacher.objects.get(user=admin_user)
        
        print(f"✅ Found admin user: {admin_user.username}")
        print(f"✅ Found teacher profile: {teacher.name}")
        
        # Create test class assignments
        test_classes = ['B2', 'B3', 'B5']  # From the screenshot
        
        for class_code in test_classes:
            # Create class assignment
            assignment, created = TeacherClassAssignment.objects.get_or_create(
                teacher=teacher,
                class_code=class_code,
                defaults={
                    'access_level': 'FULL',
                    'is_active': True
                }
            )
            
            if created:
                print(f"✅ Created class assignment: {class_code} (FULL access)")
            else:
                print(f"ℹ️  Class assignment exists: {class_code}")
            
            # Create a test exam for each class (simplified)
            exam, exam_created = Exam.objects.get_or_create(
                name=f"[QTR] - Q2 2025 - PINNACLE Vision Lv1_123 - {class_code}",
                class_code=class_code,
                defaults={
                    'created_by': teacher,
                    'exam_type': 'QUARTERLY'
                }
            )
            
            if exam_created:
                print(f"✅ Created test exam: {exam.name}")
            else:
                print(f"ℹ️  Test exam exists: {exam.name}")
        
        print(f"\n🎯 Test data created successfully!")
        print(f"   - Admin user has {len(test_classes)} class assignments")
        print(f"   - Each class has a test exam")
        print(f"   - Green triangle buttons should now appear for toggleClass functionality")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    if create_test_data():
        print("\n🚀 Ready to test! Reload http://127.0.0.1:8000/RoutineTest/exams/ to see the toggle buttons.")
    else:
        print("\n❌ Test data creation failed.")
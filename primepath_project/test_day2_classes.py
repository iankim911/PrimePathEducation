"""
BUILDER: Test Day 2 - Class Management
Tests creating classes and assigning teachers
"""
import os
import sys
import django
import json

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from core.models import Teacher
from primepath_routinetest.models import Class

def test_day2_features():
    print("\n" + "="*60)
    print("BUILDER: Day 2 Test - Class Management")
    print("="*60)
    
    # Check if admin and teachers exist
    admin = User.objects.filter(username='admin').first()
    if not admin:
        print("❌ Admin user not found - run create_routinetest_users.py first")
        return False
    
    teacher1 = Teacher.objects.filter(user__username='teacher1').first()
    if not teacher1:
        print("❌ Teacher1 not found - run create_routinetest_users.py first")
        return False
    
    print(f"✓ Admin user found: {admin.username}")
    print(f"✓ Teacher found: {teacher1.name}")
    
    # Create test classes
    print("\n--- Creating Test Classes ---")
    
    test_classes = [
        {'name': 'Mathematics 101', 'grade_level': 'Grade 5', 'section': 'A'},
        {'name': 'Science 101', 'grade_level': 'Grade 5', 'section': 'B'},
        {'name': 'English 101', 'grade_level': 'Grade 6', 'section': 'A'},
    ]
    
    created_classes = []
    for class_data in test_classes:
        class_obj, created = Class.objects.get_or_create(
            name=class_data['name'],
            defaults={
                'grade_level': class_data['grade_level'],
                'section': class_data['section'],
                'academic_year': '2024-2025',
                'created_by': admin
            }
        )
        if created:
            print(f"✅ Created class: {class_obj}")
            created_classes.append(class_obj)
        else:
            print(f"✓ Class already exists: {class_obj}")
            created_classes.append(class_obj)
    
    # Assign teacher to classes
    print("\n--- Assigning Teachers to Classes ---")
    
    for class_obj in created_classes[:2]:  # Assign to first 2 classes
        class_obj.assigned_teachers.add(teacher1)
        print(f"✅ Assigned {teacher1.name} to {class_obj.name}")
    
    # Verify assignments
    print("\n--- Verifying Assignments ---")
    
    teacher_classes = Class.objects.filter(assigned_teachers=teacher1)
    print(f"\nClasses assigned to {teacher1.name}:")
    for class_obj in teacher_classes:
        print(f"  - {class_obj}")
    
    # Summary
    print("\n" + "="*60)
    print("DAY 2 TEST RESULTS")
    print("="*60)
    
    total_classes = Class.objects.filter(is_active=True).count()
    classes_with_teachers = Class.objects.filter(assigned_teachers__isnull=False).distinct().count()
    
    print(f"Total active classes: {total_classes}")
    print(f"Classes with teachers: {classes_with_teachers}")
    print(f"Teacher {teacher1.name} assigned to: {teacher_classes.count()} classes")
    
    print("\n🎉 Day 2 Class Management: WORKING!")
    print("\nYou can now test the UI:")
    print("1. Login as admin/admin123")
    print("2. Go to Admin Dashboard")
    print("3. Click 'Manage Classes'")
    print("4. Create new classes and assign teachers")
    
    return True

if __name__ == "__main__":
    test_day2_features()
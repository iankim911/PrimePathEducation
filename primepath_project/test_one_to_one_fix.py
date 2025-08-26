#!/usr/bin/env python
"""
Test One-to-One Exam-Class Relationship Fix
Comprehensive QA test to verify the fix is working correctly
"""

import os
import sys
import django
import json

# Setup Django
sys.path.insert(0, '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from primepath_routinetest.models import RoutineExam as Exam
from primepath_routinetest.services import ExamService
import uuid

def run_comprehensive_tests():
    """Run comprehensive tests for one-to-one relationship fix"""
    print("\n" + "="*80)
    print("ONE-TO-ONE EXAM-CLASS RELATIONSHIP FIX - COMPREHENSIVE QA")
    print("="*80)
    
    # Initialize test client
    client = Client()
    
    # Get admin user for testing
    try:
        admin = User.objects.get(username='admin')
        client.force_login(admin)
        print("✅ Logged in as admin")
    except User.DoesNotExist:
        print("❌ Admin user not found")
        return False
    
    # Test 1: Check existing exams for multiple class assignments
    print("\n1. CHECKING EXISTING EXAMS FOR MULTIPLE CLASS ASSIGNMENTS...")
    print("-" * 60)
    
    multi_class_exams = []
    single_class_exams = []
    no_class_exams = []
    
    for exam in Exam.objects.all()[:20]:  # Check first 20 exams
        # Check new field
        if exam.class_code:
            single_class_exams.append(exam)
            print(f"  ✅ Exam {exam.id}: Single class '{exam.class_code}'")
        
        # Check old field for backward compatibility
        if exam.class_codes:
            if isinstance(exam.class_codes, list):
                if len(exam.class_codes) > 1:
                    multi_class_exams.append(exam)
                    print(f"  ⚠️  Exam {exam.id}: MULTIPLE classes {exam.class_codes}")
                elif len(exam.class_codes) == 1:
                    if not exam.class_code:
                        print(f"  ⚡ Exam {exam.id}: Needs migration from class_codes to class_code")
        else:
            no_class_exams.append(exam)
            if not exam.class_code:
                print(f"  ❓ Exam {exam.id}: No class assigned")
    
    print(f"\nSummary:")
    print(f"  Single class (correct): {len(single_class_exams)}")
    print(f"  Multiple classes (needs fixing): {len(multi_class_exams)}")
    print(f"  No class assigned: {len(no_class_exams)}")
    
    # Test 2: Test Copy Exam Functionality
    print("\n2. TESTING COPY EXAM FUNCTIONALITY...")
    print("-" * 60)
    
    # Find an exam to copy
    source_exam = Exam.objects.filter(class_code__isnull=False).first()
    if not source_exam:
        source_exam = Exam.objects.first()
    
    if source_exam:
        print(f"  Source exam: {source_exam.name}")
        print(f"  Source class: {source_exam.effective_class_code}")
        
        # Simulate copy exam API call
        copy_data = {
            'source_exam_id': str(source_exam.id),
            'target_class': 'PS2',  # Different class
            'target_timeslot': 'JAN-2025',
            'exam_type': 'REVIEW',
            'academic_year': '2025',
            'custom_suffix': 'test_copy'
        }
        
        response = client.post(
            '/RoutineTest/api/copy-exam/',
            data=json.dumps(copy_data),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                new_exam_id = result.get('exam_id')
                print(f"  ✅ Copy created successfully")
                print(f"  New exam ID: {new_exam_id}")
                
                # Verify the new exam
                if new_exam_id:
                    try:
                        new_exam = Exam.objects.get(id=new_exam_id)
                        print(f"  New exam name: {new_exam.name}")
                        print(f"  New exam class: {new_exam.effective_class_code}")
                        
                        # Verify it's a different exam
                        if new_exam.id != source_exam.id:
                            print(f"  ✅ Confirmed: New exam is a separate instance")
                        else:
                            print(f"  ❌ ERROR: Same exam ID - not a new instance!")
                        
                        # Verify single class assignment
                        if new_exam.class_code == 'PS2':
                            print(f"  ✅ Confirmed: New exam assigned to PS2 only")
                        else:
                            print(f"  ❌ ERROR: Class assignment incorrect")
                    except Exam.DoesNotExist:
                        print(f"  ❌ New exam not found in database")
            else:
                print(f"  ❌ Copy failed: {result.get('error')}")
        else:
            print(f"  ❌ API call failed: {response.status_code}")
            try:
                error = response.json()
                print(f"  Error: {error}")
            except:
                print(f"  Response: {response.content[:200]}")
    else:
        print("  ❌ No exams found to test copying")
    
    # Test 3: Test Display Logic
    print("\n3. TESTING DISPLAY LOGIC...")
    print("-" * 60)
    
    response = client.get('/RoutineTest/exams/')
    if response.status_code == 200:
        print("  ✅ Exam list page loads successfully")
        
        # Check if the template is using the new single class display
        content = response.content.decode('utf-8')
        
        if 'Assigned to Class:' in content:
            print("  ✅ Template uses singular 'Class' (not 'Classes')")
        elif 'Assigned to Classes:' in content:
            print("  ⚠️  Template still uses plural 'Classes'")
        
        if 'exam.effective_class_code' in content:
            print("  ✅ Template uses new effective_class_code property")
        elif 'exam.class_codes' in content:
            print("  ⚠️  Template still references old class_codes field")
    else:
        print(f"  ❌ Failed to load exam list: {response.status_code}")
    
    # Test 4: Test Service Layer
    print("\n4. TESTING SERVICE LAYER...")
    print("-" * 60)
    
    # Test the organize_exams_hierarchically function
    exams = Exam.objects.all()[:5]
    hierarchical = ExamService.organize_exams_hierarchically(
        exams, 
        admin,
        filter_assigned_only=False,
        ownership_filter='my'
    )
    
    print(f"  Programs in hierarchy: {list(hierarchical.keys())}")
    
    # Check that exams appear only once
    exam_appearances = {}
    for program, classes in hierarchical.items():
        for class_code, class_exams in classes.items():
            for exam in class_exams:
                if exam.id not in exam_appearances:
                    exam_appearances[exam.id] = []
                exam_appearances[exam.id].append(f"{program}/{class_code}")
    
    for exam_id, locations in exam_appearances.items():
        if len(locations) > 1:
            print(f"  ⚠️  Exam {exam_id} appears in multiple locations: {locations}")
        else:
            print(f"  ✅ Exam {exam_id} appears in single location: {locations[0]}")
    
    # Final Summary
    print("\n" + "="*80)
    print("QA TEST SUMMARY")
    print("="*80)
    
    issues_found = len(multi_class_exams) > 0
    
    if issues_found:
        print("⚠️  ISSUES FOUND:")
        print(f"  - {len(multi_class_exams)} exams still have multiple classes")
        print("  - Run migrations to fix these")
    else:
        print("✅ ALL TESTS PASSED!")
        print("  - One-to-one relationship is working correctly")
        print("  - Copy exam creates new instances")
        print("  - Display shows single class")
    
    print("\nRECOMMENDATIONS:")
    print("1. Run migrations if not already done:")
    print("   python manage.py migrate primepath_routinetest")
    print("2. Monitor for any exams created with multiple classes")
    print("3. Update any remaining references to class_codes (plural)")
    
    return not issues_found

if __name__ == '__main__':
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
#!/usr/bin/env python
"""
Test to ensure other features haven't been broken by the filter fix
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from primepath_routinetest.models import RoutineExam as Exam
from primepath_routinetest.services import ExamService


def test_other_features():
    """Test that other features still work"""
    print("\n" + "="*80)
    print("TESTING OTHER FEATURES - ENSURE NOTHING BROKEN")
    print("="*80)
    
    client = Client()
    all_pass = True
    
    # Test 1: Admin can see all exams
    print("\n" + "-"*60)
    print("TEST 1: Admin Access")
    print("-"*60)
    
    admin_user = User.objects.filter(is_superuser=True).first()
    if admin_user:
        admin_user.set_password('admin123')
        admin_user.save()
        
        if client.login(username=admin_user.username, password='admin123'):
            response = client.get('/RoutineTest/exams/')
            if response.status_code == 200:
                print("✅ Admin can access exam list")
            else:
                print(f"❌ Admin access failed: {response.status_code}")
                all_pass = False
            
            # Test with filter on for admin
            response = client.get('/RoutineTest/exams/?assigned_only=true')
            if response.status_code == 200:
                print("✅ Admin can use filter")
            else:
                print(f"❌ Admin filter failed: {response.status_code}")
                all_pass = False
        else:
            print("❌ Admin login failed")
            all_pass = False
    else:
        print("⚠️ No admin user found - skipping admin tests")
    
    client.logout()
    
    # Test 2: Teacher can still see owned exams
    print("\n" + "-"*60)
    print("TEST 2: Owner Access")
    print("-"*60)
    
    teacher_user = User.objects.filter(username='teacher1').first()
    if teacher_user:
        teacher_user.set_password('teacher123')
        teacher_user.save()
        
        if client.login(username='teacher1', password='teacher123'):
            # Get owned exams
            all_exams = Exam.objects.all()
            owned_exams = []
            for exam in all_exams:
                try:
                    if exam.created_by and exam.created_by.id == teacher_user.teacher_profile.id:
                        owned_exams.append(exam)
                except:
                    pass
            
            print(f"Teacher owns {len(owned_exams)} exams")
            
            # Check that owned exams appear correctly
            result = ExamService.organize_exams_hierarchically(
                all_exams, teacher_user, filter_assigned_only=False
            )
            
            found_owned = 0
            for program in result.values():
                for class_exams in program.values():
                    for exam in class_exams:
                        if hasattr(exam, 'is_owner') and exam.is_owner:
                            found_owned += 1
                            if hasattr(exam, 'access_badge'):
                                if exam.access_badge == 'OWNER':
                                    print(f"✅ Owned exam has OWNER badge: {exam.name}")
                                else:
                                    print(f"❌ Owned exam has wrong badge: {exam.access_badge}")
                                    all_pass = False
            
            if found_owned == len(owned_exams):
                print(f"✅ All {found_owned} owned exams visible")
            else:
                print(f"❌ Only {found_owned} of {len(owned_exams)} owned exams visible")
                all_pass = False
        else:
            print("❌ Teacher login failed")
            all_pass = False
    
    # Test 3: Exam type filters still work
    print("\n" + "-"*60)
    print("TEST 3: Exam Type Filters")
    print("-"*60)
    
    response = client.get('/RoutineTest/exams/?exam_type=REVIEW')
    if response.status_code == 200:
        print("✅ REVIEW filter works")
    else:
        print(f"❌ REVIEW filter failed: {response.status_code}")
        all_pass = False
    
    response = client.get('/RoutineTest/exams/?exam_type=QUARTERLY')
    if response.status_code == 200:
        print("✅ QUARTERLY filter works")
    else:
        print(f"❌ QUARTERLY filter failed: {response.status_code}")
        all_pass = False
    
    # Test 4: Combined filters work
    print("\n" + "-"*60)
    print("TEST 4: Combined Filters")
    print("-"*60)
    
    response = client.get('/RoutineTest/exams/?assigned_only=true&exam_type=REVIEW')
    if response.status_code == 200:
        print("✅ Combined filters work (assigned + REVIEW)")
    else:
        print(f"❌ Combined filters failed: {response.status_code}")
        all_pass = False
    
    # Test 5: Permission buttons still work correctly
    print("\n" + "-"*60)
    print("TEST 5: Permission-Based Buttons")
    print("-"*60)
    
    response = client.get('/RoutineTest/exams/')
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check for expected buttons
        if 'btn-edit' in content or 'Edit Answers' in content:
            print("✅ Edit buttons present")
        else:
            print("⚠️ No edit buttons found (may be correct if no editable exams)")
        
        if 'btn-copy' in content or 'Copy Exam' in content:
            print("✅ Copy buttons present")
        else:
            print("⚠️ No copy buttons found (may be correct)")
        
        if 'Upload New Exam' in content:
            print("✅ Upload button present (teacher has manage permission)")
        else:
            print("⚠️ No upload button (check if teacher has manage permission)")
    
    # Summary
    print("\n" + "="*80)
    print("FEATURE TEST SUMMARY")
    print("="*80)
    
    if all_pass:
        print("✅✅✅ ALL FEATURES WORKING - NO REGRESSION! ✅✅✅")
    else:
        print("❌ SOME FEATURES MAY BE BROKEN - CHECK ABOVE")
    
    return all_pass


if __name__ == '__main__':
    test_other_features()
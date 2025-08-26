#!/usr/bin/env python
"""
Debug the service layer filtering logic specifically
Focus on why VIEW ONLY exams are not being filtered out
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from primepath_routinetest.models import RoutineExam as Exam
from primepath_routinetest.services import ExamService

def debug_service_filtering():
    """Debug the service layer filtering for 'My Test Files'"""
    
    print("🔍 DEBUG: SERVICE LAYER FILTERING LOGIC")
    print("=" * 60)
    
    # Get teacher1 user
    user = User.objects.get(username='teacher1')
    print(f"✅ Testing with user: {user.username}")
    
    # Get all exams
    exams = Exam.objects.select_related(
        'curriculum_level__subprogram__program'
    ).prefetch_related(
        'routine_questions',
        'routine_audio_files'
    ).all()
    
    print(f"📊 Total exams in database: {exams.count()}")
    
    # Get teacher assignments for context
    assignments = ExamService.get_teacher_assignments(user)
    print(f"👤 Teacher assignments: {assignments}")
    print(f"📝 Assignment access levels:")
    for class_code, access in assignments.items():
        print(f"  {class_code}: {access}")
    
    # Test 1: Call service with ownership='my' (should filter VIEW ONLY)
    test1_title = "🧪 TEST 1: ownership='my' (My Test Files)"
    print(f"\n{test1_title}")
    print("-" * 50)
    
    hierarchical_my = ExamService.organize_exams_hierarchically(
        exams,
        user,
        filter_assigned_only=True,  # This should be True when ownership='my'
        ownership_filter='my'
    )
    
    # Count exams and badges in "My Test Files" result
    my_total = 0
    my_view_only = 0
    my_owner = 0
    my_full = 0
    my_edit = 0
    
    for program, classes in hierarchical_my.items():
        for class_code, exam_list in classes.items():
            for exam in exam_list:
                my_total += 1
                if hasattr(exam, 'access_badge'):
                    badge = exam.access_badge
                    if badge == 'VIEW ONLY':
                        my_view_only += 1
                        print(f"❌ VIEW ONLY found: {exam.name} (ID: {exam.id}) - Classes: {exam.class_codes}")
                    elif badge == 'OWNER':
                        my_owner += 1
                    elif badge == 'FULL ACCESS':
                        my_full += 1
                    elif badge == 'EDIT':
                        my_edit += 1
    
    print(f"📊 My Test Files Results:")
    print(f"  Total exams: {my_total}")
    print(f"  VIEW ONLY badges: {my_view_only} ❌")
    print(f"  OWNER badges: {my_owner}")
    print(f"  FULL ACCESS badges: {my_full}")
    print(f"  EDIT badges: {my_edit}")
    
    # Test 2: Call service with ownership='others' (should show VIEW ONLY)
    test2_title = "🧪 TEST 2: ownership='others' (Other Teachers' Test Files)"
    print(f"\n{test2_title}")
    print("-" * 50)
    
    hierarchical_others = ExamService.organize_exams_hierarchically(
        exams,
        user,
        filter_assigned_only=False,  # This should be False when ownership='others'
        ownership_filter='others'
    )
    
    # Count exams and badges in "Other Teachers' Test Files" result
    others_total = 0
    others_view_only = 0
    
    for program, classes in hierarchical_others.items():
        for class_code, exam_list in classes.items():
            for exam in exam_list:
                others_total += 1
                if hasattr(exam, 'access_badge') and exam.access_badge == 'VIEW ONLY':
                    others_view_only += 1
    
    print(f"📊 Other Teachers' Test Files Results:")
    print(f"  Total exams: {others_total}")
    print(f"  VIEW ONLY badges: {others_view_only} (expected)")
    
    # Analysis
    print(f"\n{'🎯 ANALYSIS'}")
    print("-" * 30)
    
    if my_view_only == 0:
        print("✅ SUCCESS: My Test Files correctly shows no VIEW ONLY badges")
    else:
        print(f"❌ FAILURE: My Test Files shows {my_view_only} VIEW ONLY badges (should be 0)")
        print("🔍 This indicates the service layer filtering is NOT working")
    
    if others_view_only > 0:
        print("✅ SUCCESS: Other Teachers' Test Files shows VIEW ONLY badges as expected")
    else:
        print("⚠️  INFO: Other Teachers' Test Files shows no VIEW ONLY badges")
    
    # Detailed analysis of first few VIEW ONLY exams in "My Test Files"
    if my_view_only > 0:
        analysis_title = "🔬 DETAILED ANALYSIS OF VIEW ONLY EXAMS IN 'MY TEST FILES'"
        print(f"\n{analysis_title}")
        print("-" * 60)
        
        count = 0
        for program, classes in hierarchical_my.items():
            for class_code, exam_list in classes.items():
                for exam in exam_list:
                    if hasattr(exam, 'access_badge') and exam.access_badge == 'VIEW ONLY':
                        count += 1
                        if count <= 3:  # Analyze first 3 VIEW ONLY exams
                            print(f"\n📋 Exam #{count}: {exam.name}")
                            print(f"   ID: {exam.id}")
                            print(f"   Class codes: {exam.class_codes}")
                            print(f"   Created by: {exam.created_by}")
                            
                            # Check teacher access to exam classes
                            for cls in (exam.class_codes or []):
                                access = assignments.get(cls, 'NO ACCESS')
                                print(f"   Class {cls}: Teacher has {access} access")
                            
                            # Check ownership
                            is_owner = False
                            if exam.created_by and hasattr(user, 'teacher_profile'):
                                try:
                                    is_owner = exam.created_by.id == user.teacher_profile.id
                                except:
                                    pass
                            print(f"   Is owner: {is_owner}")
                            
                            # This exam SHOULD have been filtered out by the service layer
                            print(f"   ❌ WHY NOT FILTERED: This exam should have been excluded!")
    
    return {
        'my_total': my_total,
        'my_view_only': my_view_only,
        'others_total': others_total,
        'others_view_only': others_view_only
    }

if __name__ == "__main__":
    debug_service_filtering()
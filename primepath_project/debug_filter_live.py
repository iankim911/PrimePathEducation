#!/usr/bin/env python
"""
Live debugging script to test the "Show Assigned Classes Only" filter
in the exam library for teacher1 account.
"""
import os
import sys
import django

# Add the project path to sys.path
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from primepath_routinetest.services.exam_service import ExamService, ExamPermissionService
from primepath_routinetest.models import RoutineExam as Exam
import logging
import json

def debug_live_filter():
    """Test the actual filter behavior as it would work in the browser"""
    
    print("="*80)
    print("LIVE FILTER DEBUG - SIMULATING BROWSER REQUEST")
    print("="*80)
    
    # Get teacher1 user (the one having issues)
    try:
        user = User.objects.get(username='teacher1')
        print(f"✅ Found user: {user.username}")
        print(f"   - ID: {user.id}")
        print(f"   - Is staff: {user.is_staff}")
        print(f"   - Is superuser: {user.is_superuser}")
        
        # Get teacher profile
        teacher_profile = getattr(user, 'teacher_profile', None)
        if teacher_profile:
            print(f"   - Teacher ID: {teacher_profile.id}")
            print(f"   - Teacher name: {teacher_profile.name}")
            print(f"   - Is head teacher: {teacher_profile.is_head_teacher}")
        else:
            print("   - ❌ NO TEACHER PROFILE FOUND!")
            return
            
    except User.DoesNotExist:
        print("❌ Teacher1 user not found!")
        return
    
    print()
    
    # Get teacher assignments
    assignments = ExamPermissionService.get_teacher_assignments(user)
    print(f"Teacher assignments: {len(assignments)} classes")
    for class_code, access_level in assignments.items():
        print(f"  - {class_code}: {access_level} access")
        if access_level == 'VIEW':
            print(f"    ⚠️  VIEW ONLY - should be filtered out when toggle is ON")
        else:
            print(f"    ✅ {access_level} - should remain when toggle is ON")
    
    print()
    
    # Get all exams
    base_query = Exam.objects.select_related(
        'curriculum_level__subprogram__program'
    ).prefetch_related('routine_questions', 'routine_audio_files')
    all_exams = base_query.all()
    
    print(f"Total exams in database: {all_exams.count()}")
    print()
    
    # Test FILTER OFF (show all)
    print("🔍 TESTING: Filter OFF (Show All Exams)")
    print("-" * 50)
    
    hierarchical_all = ExamService.organize_exams_hierarchically(
        all_exams, user, filter_assigned_only=False
    )
    
    all_count = 0
    view_only_count = 0
    exam_details = []
    
    for program, program_data in hierarchical_all.items():
        for class_code, class_exams in program_data.items():
            for exam in class_exams:
                all_count += 1
                badge = getattr(exam, 'access_badge', 'UNKNOWN')
                exam_details.append({
                    'name': exam.name,
                    'badge': badge,
                    'class_codes': getattr(exam, 'class_codes', []),
                    'program': program,
                    'class_code': class_code
                })
                
                if badge == 'VIEW ONLY':
                    view_only_count += 1
                    print(f"  📋 {exam.name} - {badge} ({class_code})")
    
    print(f"Filter OFF Results:")
    print(f"  - Total exams: {all_count}")
    print(f"  - VIEW ONLY exams: {view_only_count}")
    print()
    
    # Test FILTER ON (assigned only)
    print("🔍 TESTING: Filter ON (Show Assigned Classes Only)")
    print("-" * 50)
    
    # Enable logging to capture filter decisions
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('primepath_routinetest.services.exam_service')
    logger.setLevel(logging.INFO)
    
    hierarchical_filtered = ExamService.organize_exams_hierarchically(
        all_exams, user, filter_assigned_only=True
    )
    
    filtered_count = 0
    filtered_view_only_count = 0
    filtered_exam_details = []
    
    for program, program_data in hierarchical_filtered.items():
        for class_code, class_exams in program_data.items():
            for exam in class_exams:
                filtered_count += 1
                badge = getattr(exam, 'access_badge', 'UNKNOWN')
                filtered_exam_details.append({
                    'name': exam.name,
                    'badge': badge,
                    'class_codes': getattr(exam, 'class_codes', []),
                    'program': program,
                    'class_code': class_code
                })
                
                if badge == 'VIEW ONLY':
                    filtered_view_only_count += 1
                    print(f"  ❌ PROBLEM: {exam.name} - {badge} ({class_code}) - SHOULD BE FILTERED OUT!")
                else:
                    print(f"  ✅ {exam.name} - {badge} ({class_code})")
    
    print(f"Filter ON Results:")
    print(f"  - Total exams: {filtered_count}")
    print(f"  - VIEW ONLY exams: {filtered_view_only_count} (should be 0)")
    print()
    
    # Analysis
    print("="*80)
    print("ANALYSIS")
    print("="*80)
    
    if filtered_view_only_count > 0:
        print("❌ PROBLEM DETECTED!")
        print(f"   When filter is ON, {filtered_view_only_count} VIEW ONLY exams are still showing")
        print("   These should be filtered out.")
        print()
        print("VIEW ONLY exams that shouldn't be visible:")
        for exam in filtered_exam_details:
            if exam['badge'] == 'VIEW ONLY':
                print(f"   - {exam['name']} (Class: {exam['class_code']}, Badge: {exam['badge']})")
                # Check if this class is in teacher assignments with VIEW access
                class_codes = exam.get('class_codes', [exam['class_code']])
                for cc in class_codes:
                    if cc in assignments:
                        print(f"     Teacher has {assignments[cc]} access to {cc}")
                    else:
                        print(f"     Teacher has NO access to {cc}")
        print()
    else:
        print("✅ FILTER WORKING CORRECTLY!")
        print("   No VIEW ONLY exams are showing when filter is ON")
        print()
    
    print("Summary:")
    print(f"  - Filter OFF: {all_count} exams ({view_only_count} VIEW ONLY)")
    print(f"  - Filter ON: {filtered_count} exams ({filtered_view_only_count} VIEW ONLY)")
    print(f"  - Filtered out: {all_count - filtered_count} exams")
    
    if filtered_view_only_count == 0:
        print("  - ✅ Filter is working as expected")
    else:
        print("  - ❌ Filter has issues - VIEW ONLY exams are not being filtered out")
    
    print()
    print("Next steps:")
    print("1. Check browser console logs for client-side issues")
    print("2. Check cache headers are being sent correctly")
    print("3. Verify URL parameters are being processed correctly")
    print("4. Test in incognito browser to bypass cache")

if __name__ == '__main__':
    debug_live_filter()
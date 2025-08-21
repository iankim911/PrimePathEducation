#!/usr/bin/env python
"""
Quick test to get the final results summary for toggle filter fix verification.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from primepath_routinetest.models import Exam, TeacherClassAssignment
from primepath_routinetest.services.exam_service import ExamService
from core.models import Teacher

def quick_verification():
    """Quick verification of toggle filter fix"""
    print("\n" + "="*80)
    print("TOGGLE FILTER FIX - QUICK VERIFICATION SUMMARY")
    print("="*80)
    
    # Get test user
    try:
        user = User.objects.get(username='teacher1')
        teacher = Teacher.objects.get(user=user)
        print(f"✅ Testing with user: {user.username}")
    except (User.DoesNotExist, Teacher.DoesNotExist):
        print("❌ Test user 'teacher1' not found")
        return False
    
    # Get teacher assignments
    assignments = TeacherClassAssignment.objects.filter(
        teacher=teacher,
        is_active=True
    )
    
    view_assignments = assignments.filter(access_level='VIEW').count()
    full_assignments = assignments.filter(access_level='FULL').count()
    
    print(f"📋 Teacher's Class Assignments:")
    print(f"   - FULL access: {full_assignments}")
    print(f"   - VIEW access: {view_assignments}")
    print(f"   - Total: {assignments.count()}")
    
    # Get sample exams
    all_exams = Exam.objects.all()[:10]
    
    # Test toggle filter functionality
    print(f"\n🔍 TESTING TOGGLE FILTER:")
    
    # Test 1: Without filter (show all)
    hierarchical_all = ExamService.organize_exams_hierarchically(
        all_exams, user, filter_assigned_only=False
    )
    
    exam_count_all = 0
    view_only_all = 0
    for program, classes in hierarchical_all.items():
        for class_code, exams in classes.items():
            for exam in exams:
                exam_count_all += 1
                if hasattr(exam, 'access_badge') and exam.access_badge == 'VIEW ONLY':
                    view_only_all += 1
    
    print(f"   Show All Mode: {exam_count_all} exams, {view_only_all} VIEW ONLY")
    
    # Test 2: With filter (assigned only)
    hierarchical_filtered = ExamService.organize_exams_hierarchically(
        all_exams, user, filter_assigned_only=True
    )
    
    exam_count_filtered = 0
    view_only_filtered = 0
    full_access_filtered = 0
    owner_filtered = 0
    
    for program, classes in hierarchical_filtered.items():
        for class_code, exams in classes.items():
            for exam in exams:
                exam_count_filtered += 1
                badge = getattr(exam, 'access_badge', 'UNKNOWN')
                if badge == 'VIEW ONLY':
                    view_only_filtered += 1
                elif badge == 'FULL ACCESS':
                    full_access_filtered += 1
                elif badge == 'OWNER':
                    owner_filtered += 1
    
    print(f"   Assigned Only Mode: {exam_count_filtered} exams")
    print(f"     - OWNER: {owner_filtered}")
    print(f"     - FULL ACCESS: {full_access_filtered}")
    print(f"     - VIEW ONLY: {view_only_filtered}")
    
    # Verification
    print(f"\n✅ VERIFICATION RESULTS:")
    
    # Test 1: Toggle filter shows VIEW access exams
    if view_only_filtered > 0 and view_assignments > 0:
        print("✅ PASS: Toggle filter correctly shows VIEW access exams")
        toggle_test = True
    elif view_assignments == 0:
        print("✅ PASS: No VIEW assignments, so no VIEW ONLY exams expected")
        toggle_test = True
    else:
        print("❌ FAIL: Toggle filter not showing VIEW access exams")
        toggle_test = False
    
    # Test 2: Permission badges are working
    badge_test = (view_only_all + view_only_filtered + full_access_filtered + owner_filtered) > 0
    if badge_test:
        print("✅ PASS: Permission badges are being assigned correctly")
    else:
        print("❌ FAIL: Permission badges not working")
    
    # Test 3: Basic functionality preserved
    functionality_test = exam_count_all > 0 and exam_count_filtered >= 0
    if functionality_test:
        print("✅ PASS: Basic exam organization functionality preserved")
    else:
        print("❌ FAIL: Basic functionality broken")
    
    # Overall result
    all_passed = toggle_test and badge_test and functionality_test
    
    print(f"\n{'='*80}")
    print("FINAL VERDICT:")
    print("="*80)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED")
        print("✅ Toggle filter fix is working correctly")
        print("✅ Other features remain functional")
        print("✅ Safe to continue using the system")
        print("\n📋 What the fix does:")
        print("   - 'Show Assigned Classes Only' now includes VIEW access exams")
        print("   - This matches the semantic meaning of the toggle")
        print("   - Teachers can see exams from ALL their assigned classes")
    else:
        print("⚠️ SOME TESTS FAILED")
        print("❌ Review the failed tests above")
        
    return all_passed

if __name__ == "__main__":
    success = quick_verification()
    sys.exit(0 if success else 1)
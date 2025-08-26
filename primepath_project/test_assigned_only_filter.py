#!/usr/bin/env python3
"""
Test script to analyze the "Show Assigned Classes Only" filtering issue
in the RoutineTest Exam Library.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')

django.setup()

from primepath_routinetest.services.exam_service import ExamService
from primepath_routinetest.models import RoutineExam as Exam
from django.contrib.auth import get_user_model

User = get_user_model()

def test_assigned_only_filter():
    """Test the filtering logic to identify the bug"""
    
    print("=" * 80)
    print("TESTING ASSIGNED ONLY FILTER BUG")
    print("=" * 80)
    
    # Get a teacher user (not admin)
    try:
        teacher_users = User.objects.filter(is_superuser=False, is_staff=False)
        if not teacher_users.exists():
            print("❌ No non-admin users found. Creating test user...")
            test_user = User.objects.create_user(
                username='test_teacher',
                password='password',
                email='test@example.com'
            )
        else:
            test_user = teacher_users.first()
            
        print(f"✅ Using test user: {test_user.username}")
        
        # Get teacher assignments
        assignments = ExamService.get_teacher_assignments(test_user)
        print(f"✅ Teacher assignments: {assignments}")
        
        # Get all exams
        exams = Exam.objects.all()[:5]  # Test with first 5 exams
        print(f"✅ Testing with {exams.count()} exams")
        
        print("\n" + "=" * 60)
        print("TESTING WITH filter_assigned_only=True (Show Assigned Classes Only)")
        print("=" * 60)
        
        # Test with assigned only = True
        hierarchical_assigned = ExamService.organize_exams_hierarchically(
            exams, test_user, filter_assigned_only=True
        )
        
        assigned_total = 0
        view_only_count = 0
        
        for program, classes in hierarchical_assigned.items():
            if classes:
                print(f"\n📚 {program} Program:")
                for class_code, class_exams in classes.items():
                    if class_exams:
                        print(f"  📂 {class_code}: {len(class_exams)} exams")
                        for exam in class_exams:
                            assigned_total += 1
                            badge = getattr(exam, 'access_badge', 'NO BADGE')
                            print(f"    📄 {exam.name[:50]}... - Badge: {badge}")
                            if badge == 'VIEW ONLY':
                                view_only_count += 1
                                print(f"      ⚠️  VIEW ONLY exam found in ASSIGNED ONLY mode!")
        
        print("\n" + "=" * 60)
        print("TESTING WITH filter_assigned_only=False (Show All Exams)")
        print("=" * 60)
        
        # Test with assigned only = False
        hierarchical_all = ExamService.organize_exams_hierarchically(
            exams, test_user, filter_assigned_only=False
        )
        
        all_total = 0
        all_view_only_count = 0
        
        for program, classes in hierarchical_all.items():
            if classes:
                for class_code, class_exams in classes.items():
                    if class_exams:
                        for exam in class_exams:
                            all_total += 1
                            badge = getattr(exam, 'access_badge', 'NO BADGE')
                            if badge == 'VIEW ONLY':
                                all_view_only_count += 1
        
        print("\n" + "=" * 60)
        print("ANALYSIS RESULTS")
        print("=" * 60)
        print(f"📊 Assigned Only Mode:")
        print(f"   - Total exams: {assigned_total}")
        print(f"   - VIEW ONLY badges: {view_only_count}")
        print(f"   - BUG FOUND: {'YES' if view_only_count > 0 else 'NO'}")
        
        print(f"\n📊 Show All Mode:")
        print(f"   - Total exams: {all_total}")
        print(f"   - VIEW ONLY badges: {all_view_only_count}")
        
        if view_only_count > 0:
            print("\n🐛 BUG CONFIRMED:")
            print("   When 'Show Assigned Classes Only' is checked, exams with")
            print("   'VIEW ONLY' badges should NOT appear, but they do!")
            print("\n💡 SEMANTIC MEANING:")
            print("   'Show Assigned Classes Only' should mean:")
            print("   Show exams from classes where teacher is assigned")
            print("   (regardless of permission level: FULL, CO_TEACHER, or VIEW)")
        else:
            print("\n✅ NO BUG FOUND:")
            print("   Filtering appears to be working correctly")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_assigned_only_filter()
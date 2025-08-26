#!/usr/bin/env python
"""
Test Other Teachers' Test Files filter fix
Quick test to verify ownership filtering works correctly
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from primepath_routinetest.models import RoutineExam as Exam
from primepath_routinetest.services.exam_service import ExamService

def test_ownership_filter():
    print("="*80)
    print("🧪 TESTING OTHER TEACHERS' FILTER FIX")
    print("="*80)
    
    # Get admin user (should have exams)
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No admin user found")
        return
    
    print(f"📋 Testing with user: {admin_user.username}")
    
    # Get all exams
    all_exams = Exam.objects.select_related('created_by').all()
    print(f"📊 Total exams in database: {all_exams.count()}")
    
    if all_exams.count() == 0:
        print("❌ No exams found for testing")
        return
    
    # Check ownership (created_by is Teacher, not User)
    admin_teacher = None
    if hasattr(admin_user, 'teacher_profile'):
        admin_teacher = admin_user.teacher_profile
        owned_exams = all_exams.filter(created_by=admin_teacher)
        other_exams = all_exams.exclude(created_by=admin_teacher)
    else:
        print(f"❌ User {admin_user.username} has no teacher profile")
        owned_exams = all_exams.none()  # Empty queryset
        other_exams = all_exams
    
    print(f"📋 Exams owned by {admin_user.username}: {owned_exams.count()}")
    print(f"📋 Exams owned by others: {other_exams.count()}")
    
    # Test "My Test Files" filter (ownership_filter='my')
    print(f"\n{'='*50}")
    print("🔍 Testing 'My Test Files' filter...")
    my_exams = ExamService.organize_exams_hierarchically(
        all_exams,
        admin_user,
        filter_assigned_only=True,
        ownership_filter='my',
        filter_intent='SHOW_EDITABLE'
    )
    
    my_exam_count = sum(len(exam_list) for program in my_exams.values() for exam_list in program.values())
    print(f"📊 'My Test Files' returned: {my_exam_count} exams")
    
    # Test "Other Teachers' Test Files" filter (ownership_filter='others')
    print(f"\n{'='*50}")
    print("🔍 Testing 'Other Teachers' Test Files' filter...")
    others_exams = ExamService.organize_exams_hierarchically(
        all_exams,
        admin_user,
        filter_assigned_only=True,
        ownership_filter='others',
        filter_intent='SHOW_VIEW_ONLY'
    )
    
    others_exam_count = sum(len(exam_list) for program in others_exams.values() for exam_list in program.values())
    print(f"📊 'Other Teachers' Test Files' returned: {others_exam_count} exams")
    
    # Verify the fix worked
    print(f"\n{'='*80}")
    print("✅ VERIFICATION RESULTS:")
    print("="*80)
    
    if admin_user.is_superuser:
        print("ℹ️  User is superuser - may see all exams regardless of ownership")
        print("⚠️  For proper testing, use a regular teacher account")
    
    print(f"📋 Database totals:")
    print(f"  - Owned by {admin_user.username}: {owned_exams.count()}")
    print(f"  - Owned by others: {other_exams.count()}")
    print(f"📋 Filter results:")
    print(f"  - 'My Test Files': {my_exam_count}")
    print(f"  - 'Other Teachers': {others_exam_count}")
    
    # Show some example exams from each filter
    if my_exam_count > 0:
        print(f"\n📋 Sample from 'My Test Files':")
        for program, program_data in my_exams.items():
            for class_code, exams in program_data.items():
                for exam in exams[:3]:  # Show first 3
                    badge = getattr(exam, 'access_badge', 'Unknown')
                    owner_info = f"(created_by: {exam.created_by.username if exam.created_by else 'None'})"
                    print(f"  - {exam.name} | Badge: {badge} | {owner_info}")
                    break
                break
            break
    
    if others_exam_count > 0:
        print(f"\n📋 Sample from 'Other Teachers' Test Files':")
        for program, program_data in others_exams.items():
            for class_code, exams in program_data.items():
                for exam in exams[:3]:  # Show first 3
                    badge = getattr(exam, 'access_badge', 'Unknown')
                    owner_info = f"(created_by: {exam.created_by.username if exam.created_by else 'None'})"
                    print(f"  - {exam.name} | Badge: {badge} | {owner_info}")
                    break
                break
            break
    
    # Final assessment
    if others_exam_count == 0 and other_exams.count() > 0:
        print(f"\n✅ POSSIBLE SUCCESS: No exams shown in 'Other Teachers' despite {other_exams.count()} other-owned exams")
        print("   This could be correct if user has no VIEW access to other exams")
    elif others_exam_count > 0:
        print(f"\n🔍 CHECK NEEDED: {others_exam_count} exams shown in 'Other Teachers'")
        print("   Verify these are actually VIEW-ONLY access exams, not owned by current user")
    
    print("="*80)

if __name__ == "__main__":
    test_ownership_filter()
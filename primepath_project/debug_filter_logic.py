#!/usr/bin/env python
"""
Debug the exact filter logic to see why VIEW ONLY exams are not being filtered out
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from primepath_routinetest.services.exam_service import ExamService
import logging

def debug_filter_logic():
    """Debug exactly what happens in the filter logic"""
    
    # Set up logging to capture the service logs
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('primepath_routinetest.services.exam_service')
    logger.setLevel(logging.DEBUG)
    
    # Create a simple handler to see the logs
    import sys
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    print("🔍 DEBUGGING FILTER LOGIC")
    print("="*60)
    
    teacher1 = User.objects.get(username='teacher1')
    
    print("\n1️⃣ TESTING WITH FILTER OFF")
    print("-"*30)
    
    # Get all exams first
    from primepath_routinetest.models import RoutineExam as Exam
    all_exams = Exam.objects.all()
    
    result_off = ExamService.organize_exams_hierarchically(
        exams=all_exams,
        user=teacher1,
        filter_assigned_only=False
    )
    
    # Count exams and badges
    exam_count_off = 0
    view_only_count_off = 0
    for program, classes in result_off.items():
        for class_code, exams in classes.items():
            for exam in exams:
                exam_count_off += 1
                if hasattr(exam, 'access_badge') and 'VIEW' in exam.access_badge:
                    view_only_count_off += 1
    
    print(f"📊 Filter OFF Results:")
    print(f"   Total exams: {exam_count_off}")
    print(f"   VIEW ONLY badges: {view_only_count_off}")
    
    print("\n2️⃣ TESTING WITH FILTER ON")
    print("-"*30)
    result_on = ExamService.organize_exams_hierarchically(
        exams=all_exams,
        user=teacher1,
        filter_assigned_only=True  # ← This should filter out VIEW ONLY
    )
    
    # Count exams and badges
    exam_count_on = 0
    view_only_count_on = 0
    badge_types = {}
    for program, classes in result_on.items():
        for class_code, exams in classes.items():
            for exam in exams:
                exam_count_on += 1
                if hasattr(exam, 'access_badge'):
                    badge = exam.access_badge
                    badge_types[badge] = badge_types.get(badge, 0) + 1
                    if 'VIEW' in badge:
                        view_only_count_on += 1
                        print(f"🚨 FOUND VIEW ONLY EXAM: {exam.name} (Class: {class_code}, Badge: {badge})")
    
    print(f"📊 Filter ON Results:")
    print(f"   Total exams: {exam_count_on}")
    print(f"   VIEW ONLY badges: {view_only_count_on}")
    print(f"   All badge types: {badge_types}")
    
    print("\n" + "="*60)
    print("📈 COMPARISON")
    print("="*60)
    print(f"Filter OFF: {exam_count_off} exams, {view_only_count_off} VIEW ONLY")
    print(f"Filter ON:  {exam_count_on} exams, {view_only_count_on} VIEW ONLY")
    
    if view_only_count_on > 0:
        print("❌ FILTER IS NOT WORKING - VIEW ONLY EXAMS STILL PRESENT!")
        print("🔧 The 'continue' statement in the filter logic is not working")
    else:
        print("✅ FILTER IS WORKING - NO VIEW ONLY EXAMS")

if __name__ == "__main__":
    debug_filter_logic()
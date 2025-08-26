#!/usr/bin/env python
"""
Final comprehensive test for the filter fix
Tests all layers: service, view, and template
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
from primepath_routinetest.models import RoutineExam as Exam, TeacherClassAssignment
from core.models import Teacher
from bs4 import BeautifulSoup

def test_filter():
    print("=" * 80)
    print("FINAL FILTER FIX VERIFICATION TEST")
    print("=" * 80)
    
    # Setup
    client = Client()
    teacher1 = User.objects.get(username='teacher1')
    teacher1.set_password('teacher123')
    teacher1.save()
    
    # Get teacher profile
    teacher_profile = Teacher.objects.get(user=teacher1)
    
    # Show current assignments
    print("\n1. TEACHER ASSIGNMENTS:")
    print("-" * 40)
    assignments = TeacherClassAssignment.objects.filter(teacher=teacher_profile, is_active=True)
    for assignment in assignments:
        print(f"   {assignment.get_class_code_display()}: {assignment.access_level}")
    
    # Check what exams exist for VIEW ONLY classes
    view_only_classes = assignments.filter(access_level='VIEW').values_list('class_code', flat=True)
    print(f"\n   VIEW ONLY classes: {list(view_only_classes)}")
    
    # Count exams in VIEW ONLY classes
    view_only_exam_count = 0
    for class_code in view_only_classes:
        # Use a different approach for SQLite compatibility
        all_exams = Exam.objects.all()
        matching_exams = []
        for exam in all_exams:
            if exam.class_codes and class_code in exam.class_codes:
                matching_exams.append(exam)
                view_only_exam_count += 1
        
        if matching_exams:
            print(f"\n   Exams in {class_code} (VIEW ONLY):")
            for exam in matching_exams[:3]:  # Show first 3
                print(f"      - {exam.name}")
    
    print(f"\n   Total exams in VIEW ONLY classes: {view_only_exam_count}")
    
    # Test with filter OFF (should show VIEW ONLY)
    print("\n2. TEST WITH FILTER OFF (Show All Exams):")
    print("-" * 40)
    
    login_success = client.login(username='teacher1', password='teacher123')
    print(f"   Login successful: {login_success}")
    
    response = client.get('/RoutineTest/exams/')
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Count badges
    all_badges = soup.find_all('span', class_='badge')
    view_only_badges_off = [b for b in all_badges if 'VIEW' in b.get_text()]
    
    print(f"   Response status: {response.status_code}")
    print(f"   Total badges found: {len(all_badges)}")
    print(f"   VIEW ONLY badges: {len(view_only_badges_off)}")
    
    # Test with filter ON (should NOT show VIEW ONLY)
    print("\n3. TEST WITH FILTER ON (Show Assigned Classes Only):")
    print("-" * 40)
    
    response = client.get('/RoutineTest/exams/?assigned_only=true')
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Check filter checkbox
    checkbox = soup.find('input', {'id': 'assignedOnlyFilter'})
    print(f"   Filter checkbox found: {checkbox is not None}")
    if checkbox:
        print(f"   Checkbox checked: {checkbox.get('checked') is not None}")
    
    # Count badges
    all_badges = soup.find_all('span', class_='badge')
    view_only_badges_on = []
    
    for badge in all_badges:
        badge_text = badge.get_text().strip()
        if 'VIEW' in badge_text:
            view_only_badges_on.append(badge_text)
            # Find the exam card
            exam_card = badge.find_parent('div', class_='exam-card')
            if exam_card:
                exam_title = exam_card.find('div', class_='exam-title')
                if exam_title:
                    print(f"   ❌ FOUND VIEW ONLY BADGE: {exam_title.get_text().strip()}")
    
    print(f"\n   Response status: {response.status_code}")
    print(f"   Total badges found: {len(all_badges)}")
    print(f"   VIEW ONLY badges: {len(view_only_badges_on)}")
    
    # Count total exam cards
    exam_cards = soup.find_all('div', class_='exam-card')
    print(f"   Total exam cards displayed: {len(exam_cards)}")
    
    # Check context variable
    if hasattr(response, 'context') and response.context:
        show_assigned = response.context.get('show_assigned_only', False)
        print(f"\n   Context show_assigned_only: {show_assigned}")
    
    # Final verdict
    print("\n" + "=" * 80)
    print("FINAL VERDICT:")
    print("=" * 80)
    
    if len(view_only_badges_on) == 0:
        print("✅ SUCCESS: No VIEW ONLY badges shown with filter enabled!")
        print("   The filter is working correctly.")
    else:
        print("❌ FAILURE: VIEW ONLY badges still visible with filter enabled!")
        print(f"   Found {len(view_only_badges_on)} VIEW ONLY badges that should be hidden.")
        print("\nDEBUGGING INFO:")
        print(f"   - URL had assigned_only=true: {response.request['QUERY_STRING'] == b'assigned_only=true'}")
        print(f"   - Template received show_assigned_only: Check context above")
        print(f"   - Browser cache may need clearing")
        print(f"   - Check JavaScript console for errors")
    
    print("\n" + "=" * 80)
    
    return len(view_only_badges_on) == 0

if __name__ == "__main__":
    success = test_filter()
    sys.exit(0 if success else 1)
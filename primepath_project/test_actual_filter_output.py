#!/usr/bin/env python
"""
Test what's actually being rendered when the filter is applied
This simulates what the browser sees
"""
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from primepath_routinetest.models import RoutineExam as Exam
from primepath_routinetest.services import ExamService
from primepath_routinetest.services.exam_service import ExamPermissionService
from bs4 import BeautifulSoup


def test_actual_filter_rendering():
    """Test what's actually rendered in the HTML when filter is applied"""
    print("\n" + "="*80)
    print("TESTING ACTUAL FILTER RENDERING")
    print("="*80)
    
    # Create test client
    client = Client()
    
    # Get teacher1 user and set password
    teacher_user = User.objects.filter(username='teacher1').first()
    if not teacher_user:
        print("❌ teacher1 user not found")
        return
    
    # Set a known password
    teacher_user.set_password('test1234')
    teacher_user.save()
    
    # Login
    login_success = client.login(username='teacher1', password='test1234')
    if not login_success:
        print("❌ Failed to login")
        return
    
    print("✅ Logged in as teacher1")
    
    # Test 1: Filter OFF
    print("\n" + "-"*60)
    print("TEST 1: Filter OFF (assigned_only not set)")
    print("-"*60)
    
    response = client.get('/RoutineTest/exams/')
    if response.status_code == 200:
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all exam badges
        badges = soup.find_all('span', class_='badge')
        badge_texts = [badge.get_text(strip=True) for badge in badges]
        
        # Count VIEW ONLY badges
        view_only_count = sum(1 for text in badge_texts if 'VIEW' in text or 'View' in text)
        
        print(f"Total badges found: {len(badges)}")
        print(f"VIEW ONLY badges: {view_only_count}")
        print(f"Badge texts: {badge_texts[:10]}")  # First 10
        
        # Check context data
        if hasattr(response, 'context') and response.context:
            show_assigned_only = response.context.get('show_assigned_only', False)
            print(f"Context show_assigned_only: {show_assigned_only}")
    
    # Test 2: Filter ON
    print("\n" + "-"*60)
    print("TEST 2: Filter ON (assigned_only=true)")
    print("-"*60)
    
    response = client.get('/RoutineTest/exams/?assigned_only=true')
    if response.status_code == 200:
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all exam badges
        badges = soup.find_all('span', class_='badge')
        badge_texts = [badge.get_text(strip=True) for badge in badges]
        
        # Count VIEW ONLY badges
        view_only_count = sum(1 for text in badge_texts if 'VIEW' in text or 'View' in text)
        
        print(f"Total badges found: {len(badges)}")
        print(f"VIEW ONLY badges: {view_only_count}")
        print(f"Badge texts: {badge_texts[:10]}")  # First 10
        
        if view_only_count > 0:
            print("\n❌❌❌ BUG CONFIRMED: VIEW ONLY badges still showing when filter is ON!")
            
            # Find the exam cards with VIEW ONLY badges
            exam_cards = soup.find_all('div', class_='exam-card')
            for card in exam_cards:
                badge = card.find('span', class_='badge')
                if badge and ('VIEW' in badge.get_text() or 'View' in badge.get_text()):
                    exam_title = card.find('div', class_='exam-title')
                    if exam_title:
                        print(f"  - Exam with VIEW ONLY: {exam_title.get_text(strip=True)}")
        else:
            print("✅ No VIEW ONLY badges found - filter working correctly!")
        
        # Check context data
        if hasattr(response, 'context') and response.context:
            show_assigned_only = response.context.get('show_assigned_only', False)
            hierarchical_exams = response.context.get('hierarchical_exams', {})
            
            print(f"\nContext show_assigned_only: {show_assigned_only}")
            
            # Count exams in context
            total_in_context = 0
            for program in hierarchical_exams.values():
                for class_exams in program.values():
                    total_in_context += len(class_exams)
                    # Check badges in context
                    for exam in class_exams:
                        if hasattr(exam, 'access_badge'):
                            if exam.access_badge == 'VIEW ONLY':
                                print(f"❌ Context has VIEW ONLY exam: {exam.name}")
            
            print(f"Total exams in context: {total_in_context}")
    
    # Test 3: Direct backend call
    print("\n" + "-"*60)
    print("TEST 3: Direct Backend Service Call")
    print("-"*60)
    
    all_exams = Exam.objects.all()
    filtered = ExamService.organize_exams_hierarchically(
        all_exams, teacher_user, filter_assigned_only=True
    )
    
    backend_count = sum(len(exams) for program in filtered.values() for exams in program.values())
    view_only_in_backend = 0
    
    for program in filtered.values():
        for class_exams in program.values():
            for exam in class_exams:
                if hasattr(exam, 'access_badge') and exam.access_badge == 'VIEW ONLY':
                    view_only_in_backend += 1
                    print(f"❌ Backend has VIEW ONLY: {exam.name}")
    
    print(f"Backend filtered count: {backend_count}")
    print(f"Backend VIEW ONLY count: {view_only_in_backend}")
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    if view_only_count > 0:
        print("❌ FILTER IS NOT WORKING - VIEW ONLY badges still showing in HTML")
        print("The issue is between backend and template rendering")
    else:
        print("✅ Filter appears to be working correctly")


if __name__ == '__main__':
    # Install BeautifulSoup if needed
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("Installing BeautifulSoup4...")
        os.system("../venv/bin/pip install beautifulsoup4")
        from bs4 import BeautifulSoup
    
    test_actual_filter_rendering()
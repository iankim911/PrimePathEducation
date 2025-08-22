#!/usr/bin/env python
"""
Debug the Django view directly to see what it returns
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import User
from primepath_routinetest.views.exam import exam_list
import re

def debug_django_view():
    """Debug what the Django view actually returns"""
    
    print("🔍 DEBUGGING DJANGO VIEW DIRECTLY")
    print("="*60)
    
    # Set up test client
    client = Client()
    teacher1 = User.objects.get(username='teacher1')
    teacher1.set_password('teacher123')
    teacher1.save()
    
    login = client.login(username='teacher1', password='teacher123')
    print(f"✅ Logged in as teacher1: {login}")
    
    print("\n1️⃣ TESTING VIEW WITH FILTER OFF")
    print("-"*40)
    response_off = client.get('/RoutineTest/exams/')
    print(f"Status: {response_off.status_code}")
    
    if response_off.status_code == 200:
        content_off = response_off.content.decode('utf-8')
        view_only_badges_off = len(re.findall(r'VIEW\s*ONLY', content_off))
        print(f"VIEW ONLY badges in HTML: {view_only_badges_off}")
        
        # Check what data was passed to template
        if hasattr(response_off, 'context') and response_off.context:
            context = response_off.context[0]  # First context
            hierarchical_exams = context.get('hierarchical_exams', {})
            
            # Count exams in context
            exam_count = 0
            badge_count = 0
            for program, classes in hierarchical_exams.items():
                for class_code, exams in classes.items():
                    for exam in exams:
                        exam_count += 1
                        if hasattr(exam, 'access_badge') and 'VIEW' in exam.access_badge:
                            badge_count += 1
                            print(f"   Context: {exam.name} has badge: {exam.access_badge}")
            
            print(f"Context data: {exam_count} exams, {badge_count} with VIEW badges")
    
    print("\n2️⃣ TESTING VIEW WITH FILTER ON")
    print("-"*40)
    response_on = client.get('/RoutineTest/exams/?assigned_only=true')
    print(f"Status: {response_on.status_code}")
    
    if response_on.status_code == 200:
        content_on = response_on.content.decode('utf-8')
        view_only_badges_on = len(re.findall(r'VIEW\s*ONLY', content_on))
        print(f"VIEW ONLY badges in HTML: {view_only_badges_on}")
        
        # Check what data was passed to template
        if hasattr(response_on, 'context') and response_on.context:
            context = response_on.context[0]  # First context
            hierarchical_exams = context.get('hierarchical_exams', {})
            
            # Count exams in context
            exam_count = 0
            badge_count = 0
            all_badges = {}
            for program, classes in hierarchical_exams.items():
                for class_code, exams in classes.items():
                    for exam in exams:
                        exam_count += 1
                        if hasattr(exam, 'access_badge'):
                            badge = exam.access_badge
                            all_badges[badge] = all_badges.get(badge, 0) + 1
                            if 'VIEW' in badge:
                                badge_count += 1
                                print(f"🚨 Context: {exam.name} has VIEW badge: {badge}")
            
            print(f"Context data: {exam_count} exams, {badge_count} with VIEW badges")
            print(f"All badge types in context: {all_badges}")
    
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print(f"Filter OFF: {view_only_badges_off} VIEW ONLY badges in HTML")
    print(f"Filter ON:  {view_only_badges_on} VIEW ONLY badges in HTML")
    
    if view_only_badges_on > 0:
        print("❌ FILTER NOT WORKING - VIEW ONLY badges still in HTML")
        print("🔧 Issue is in Django view or template rendering")
    else:
        print("✅ FILTER WORKING - No VIEW ONLY badges in HTML")

if __name__ == "__main__":
    debug_django_view()
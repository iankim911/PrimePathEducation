#!/usr/bin/env python
"""
Debug the actual filter issue - trace the full data flow
"""
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth.models import User
from primepath_routinetest.models import Exam
from primepath_routinetest.views.exam import exam_list
from primepath_routinetest.services import ExamService


def debug_live_filter():
    """Debug the live filter issue"""
    print("\n" + "="*80)
    print("LIVE FILTER DEBUG - TRACING FULL DATA FLOW")
    print("="*80)
    
    # Get teacher1 user
    teacher_user = User.objects.filter(username='teacher1').first()
    if not teacher_user:
        print("❌ teacher1 user not found")
        return
    
    # Create a request factory
    factory = RequestFactory()
    
    # Create request with filter ON
    request = factory.get('/RoutineTest/exams/?assigned_only=true')
    request.user = teacher_user
    
    # Add session and messages middleware attributes (required by view)
    from django.contrib.sessions.middleware import SessionMiddleware
    from django.contrib.messages.middleware import MessageMiddleware
    from django.contrib.auth.middleware import AuthenticationMiddleware
    
    # Process request through minimal middleware
    session_middleware = SessionMiddleware(lambda x: x)
    session_middleware.process_request(request)
    request.session.save()
    
    auth_middleware = AuthenticationMiddleware(lambda x: x)
    auth_middleware.process_request(request)
    
    message_middleware = MessageMiddleware(lambda x: x)
    message_middleware.process_request(request)
    
    print(f"Request URL: {request.get_full_path()}")
    print(f"Request user: {request.user.username}")
    print(f"GET params: {dict(request.GET)}")
    
    # Call the view directly
    print("\n" + "-"*60)
    print("CALLING VIEW DIRECTLY")
    print("-"*60)
    
    response = exam_list(request)
    
    print(f"Response status: {response.status_code}")
    
    # Check the context
    if hasattr(response, 'context_data'):
        context = response.context_data
    elif hasattr(response, '_context_data'):
        context = response._context_data
    else:
        # Try to extract context from the response
        try:
            # Parse the rendered content to find debug info
            content = response.content.decode('utf-8')
            
            # Look for our debug markers
            if '[SERVER_DATA_DEBUG]' in content:
                print("\n✅ Found SERVER_DATA_DEBUG in response")
                # Extract the debug section
                import re
                matches = re.findall(r'serverTotalExams\+\+;.*?serverViewOnlyCount\+\+;', content, re.DOTALL)
                if matches:
                    view_only_count = len(re.findall(r'serverViewOnlyCount\+\+;', matches[0]))
                    total_count = len(re.findall(r'serverTotalExams\+\+;', matches[0]))
                    print(f"Server data shows: {total_count} total exams, {view_only_count} VIEW ONLY")
                    
                    if view_only_count > 0:
                        print("❌❌❌ VIEW ONLY EXAMS FOUND IN TEMPLATE DATA!")
                        # Extract exam names
                        view_only_logs = re.findall(r"console\.log\('\[SERVER_DATA_DEBUG\] ❌ VIEW ONLY exam in server data: (.*?)'\)", content)
                        for exam_name in view_only_logs:
                            print(f"  - {exam_name}")
            
            # Check for VIEW ONLY badges in HTML
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            badges = soup.find_all('span', class_='badge')
            
            view_only_badges = [b for b in badges if 'VIEW ONLY' in b.get_text()]
            print(f"\nHTML Analysis:")
            print(f"Total badges in HTML: {len(badges)}")
            print(f"VIEW ONLY badges: {len(view_only_badges)}")
            
            if view_only_badges:
                print("\n❌ VIEW ONLY badges found in HTML:")
                # Find the exam names
                for badge in view_only_badges[:3]:  # Show first 3
                    parent = badge.find_parent('div', class_='exam-card')
                    if parent:
                        exam_title = parent.find('div', class_='exam-title')
                        if exam_title:
                            print(f"  - {exam_title.get_text(strip=True)}")
            
        except Exception as e:
            print(f"Error analyzing response: {e}")
    
    # Now test the service directly with same parameters
    print("\n" + "-"*60)
    print("TESTING SERVICE DIRECTLY")
    print("-"*60)
    
    all_exams = Exam.objects.all()
    result = ExamService.organize_exams_hierarchically(
        all_exams, teacher_user, filter_assigned_only=True
    )
    
    service_total = 0
    service_view_only = 0
    
    for program in result.values():
        for class_exams in program.values():
            for exam in class_exams:
                service_total += 1
                if hasattr(exam, 'access_badge') and exam.access_badge == 'VIEW ONLY':
                    service_view_only += 1
                    print(f"❌ Service returned VIEW ONLY: {exam.name}")
    
    print(f"\nService results: {service_total} total, {service_view_only} VIEW ONLY")
    
    # Summary
    print("\n" + "="*80)
    print("DIAGNOSIS")
    print("="*80)
    
    if service_view_only == 0:
        print("✅ Service is filtering correctly (0 VIEW ONLY)")
        print("❌ But template is showing VIEW ONLY badges")
        print("\nPOSSIBLE CAUSES:")
        print("1. Template is using wrong data variable")
        print("2. Template has hardcoded test data")
        print("3. View is modifying data after service call")
        print("4. Multiple service calls with different parameters")
    else:
        print("❌ Service itself is NOT filtering correctly!")
        print(f"❌ Service returned {service_view_only} VIEW ONLY exams")
        print("\nTHE BUG IS IN THE SERVICE LAYER")


if __name__ == '__main__':
    # Install BeautifulSoup if needed
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("Installing BeautifulSoup4...")
        os.system("../venv/bin/pip install beautifulsoup4")
    
    debug_live_filter()
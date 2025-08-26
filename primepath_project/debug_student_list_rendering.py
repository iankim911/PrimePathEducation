#!/usr/bin/env python
"""
Debug script to test the student_list view rendering issue
"""

import os
import sys
import django

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from core.models import Teacher
from primepath_routinetest.views.student_management_v2 import student_list

print("=== DIRECT VIEW TESTING FOR STUDENT_LIST ===")
print()

def test_view_directly():
    """Test the view function directly with proper request setup"""
    
    # Create request factory
    factory = RequestFactory()
    
    # Test with admin user
    print("--- TESTING WITH ADMIN USER ---")
    admin_user = User.objects.get(username='admin')
    request = factory.get('/RoutineTest/students/')
    request.user = admin_user
    
    # Add required middleware attributes
    setattr(request, 'session', {})
    setattr(request, '_messages', [])
    
    try:
        response = student_list(request)
        print(f"✅ View executed successfully")
        print(f"Status code: {response.status_code}")
        print(f"Template name: {response.template_name}")
        
        # Check context
        if hasattr(response, 'context_data'):
            context = response.context_data
            print(f"Context keys: {list(context.keys())}")
            
            students = context.get('students')
            if students:
                print(f"Students count: {students.count()}")
                for student in students:
                    if student.student_id == 'student1':
                        print(f"  ⭐ FOUND student1: {student.user.get_full_name()}")
            else:
                print("❌ No students in context")
        else:
            print("❌ No context_data available")
            
    except Exception as e:
        print(f"❌ View execution failed: {e}")
        import traceback
        traceback.print_exc()

def test_with_client():
    """Test with Django test client"""
    
    print("\n--- TESTING WITH CLIENT ---")
    client = Client()
    
    # Login admin
    admin_user = User.objects.get(username='admin')
    admin_user.set_password('admin123')
    admin_user.save()
    
    login_success = client.login(username='admin', password='admin123')
    print(f"Login successful: {login_success}")
    
    if login_success:
        response = client.get('/RoutineTest/students/')
        print(f"Response status: {response.status_code}")
        print(f"Response type: {type(response)}")
        
        # Try to get content length
        try:
            content = response.content.decode()
            print(f"Content length: {len(content)} characters")
            
            # Check if student1 appears in rendered content
            if 'student1' in content:
                print("✅ student1 found in rendered HTML content!")
            else:
                print("❌ student1 NOT found in rendered HTML content")
                
            # Check for specific markers
            if 'Total Students:' in content:
                # Extract student count from content
                import re
                match = re.search(r'Total Students:</strong>\s*(\d+)', content)
                if match:
                    student_count = match.group(1)
                    print(f"Template shows student count: {student_count}")
            
        except Exception as e:
            print(f"Error reading content: {e}")

if __name__ == "__main__":
    test_view_directly()
    test_with_client()
#!/usr/bin/env python
"""
Test the view directly to see what's happening with the filter
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from primepath_routinetest.views.exam import exam_list

User = get_user_model()

def test_view():
    print("\n" + "="*80)
    print("TESTING VIEW DIRECTLY")
    print("="*80)
    
    factory = RequestFactory()
    teacher1 = User.objects.filter(username='teacher1').first()
    
    if not teacher1:
        print("ERROR: teacher1 not found")
        return
    
    print(f"Testing with user: {teacher1.username}")
    
    # Test with filter OFF
    print("\n" + "-"*40)
    print("Test 1: Filter OFF (assigned_only not set)")
    print("-"*40)
    request = factory.get('/routinetest/exams/')
    request.user = teacher1
    
    try:
        response = exam_list(request)
        print(f"Response status: {response.status_code if hasattr(response, 'status_code') else 'N/A'}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test with filter ON
    print("\n" + "-"*40)
    print("Test 2: Filter ON (assigned_only=true)")
    print("-"*40)
    request = factory.get('/routinetest/exams/', {'assigned_only': 'true'})
    request.user = teacher1
    
    try:
        response = exam_list(request)
        print(f"Response status: {response.status_code if hasattr(response, 'status_code') else 'N/A'}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test with filter ON (uppercase)
    print("\n" + "-"*40)
    print("Test 3: Filter ON (assigned_only=True)")
    print("-"*40)
    request = factory.get('/routinetest/exams/', {'assigned_only': 'True'})
    request.user = teacher1
    
    try:
        response = exam_list(request)
        print(f"Response status: {response.status_code if hasattr(response, 'status_code') else 'N/A'}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_view()
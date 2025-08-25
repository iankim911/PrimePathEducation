#!/usr/bin/env python
"""
Test the template fix
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_template_fix():
    print("=== TESTING TEMPLATE FIX ===\n")
    
    # Login as admin and test the page
    client = Client()
    admin_user = User.objects.get(username='admin')
    
    # Ensure password is set
    if not admin_user.check_password('admin'):
        admin_user.set_password('admin')
        admin_user.save()
    
    login_success = client.login(username='admin', password='admin')
    print(f"Login successful: {login_success}")
    
    if login_success:
        response = client.get('/RoutineTest/students/')
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode()
            
            # Check what the template is showing now
            if 'Total Students:</strong> 4' in content:
                print("✅ Student count still shows 4")
            
            if '<table style="width: 100%; border-collapse: collapse;">' in content:
                print("✅ Table is now being rendered!")
            else:
                print("❌ Table still not rendered")
                
            if 'No students found' in content:
                print("❌ Still shows 'No students found'")
            else:
                print("✅ 'No students found' message is gone!")
                
            # Look for actual student names in the HTML
            student_names = ['Emily Davis', 'Sarah Johnson', 'John Smith', 'Michael Williams']
            found_students = []
            for name in student_names:
                if name in content:
                    found_students.append(name)
                    
            if found_students:
                print(f"✅ Found student names in HTML: {found_students}")
            else:
                print("❌ No student names found in HTML")
                
            # Debug: Show a snippet of the relevant HTML
            print("\n=== HTML SNIPPET ===")
            start = content.find('<div class="card">')
            if start > -1:
                end = content.find('</div>', start + 200)
                if end > -1:
                    snippet = content[start:end + 6]
                    print(snippet[:500] + "..." if len(snippet) > 500 else snippet)
        else:
            print(f"❌ Error response: {response.status_code}")

if __name__ == "__main__":
    test_template_fix()
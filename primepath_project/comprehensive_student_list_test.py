#!/usr/bin/env python
"""
Comprehensive test to determine why student1 doesn't appear in browser
"""

import os
import sys
import django

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse, resolve
from django.http import HttpRequest
from primepath_routinetest.views.student_management_v2 import student_list
from core.models import Teacher
import re

def test_url_resolution():
    """Test URL resolution"""
    print("=== URL RESOLUTION TEST ===")
    
    try:
        url = reverse('RoutineTest:student_list')
        print(f"✅ URL resolves to: {url}")
        
        # Test what view this URL actually calls
        resolver_match = resolve(url)
        print(f"✅ Resolved view: {resolver_match.func.__name__}")
        print(f"✅ View module: {resolver_match.func.__module__}")
        
        return url
    except Exception as e:
        print(f"❌ URL resolution failed: {e}")
        return None

def test_browser_simulation():
    """Simulate exact browser request"""
    print("\n=== BROWSER SIMULATION TEST ===")
    
    client = Client()
    
    # Login as admin
    admin_user = User.objects.get(username='admin')
    admin_user.set_password('admin123')
    admin_user.save()
    
    login_success = client.login(username='admin', password='admin123')
    print(f"Login success: {login_success}")
    
    if not login_success:
        return False
    
    url = '/RoutineTest/students/'
    print(f"Testing URL: {url}")
    
    response = client.get(url)
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode()
        
        # Check for student1 in various formats
        checks = {
            'student1 ID': 'student1' in content,
            'John Smith name': 'John Smith' in content,
            'smith (lowercase)': 'smith' in content.lower(),
            'Total students text': 'Total Students' in content,
            'Student table': '<table' in content,
            'Student rows': '<tr>' in content
        }
        
        print("Content checks:")
        for check_name, result in checks.items():
            status = "✅" if result else "❌"
            print(f"  {status} {check_name}")
        
        # Extract student count from HTML
        count_match = re.search(r'Total Students:</strong>\s*(\d+)', content)
        if count_match:
            displayed_count = count_match.group(1)
            print(f"  📊 Displayed count: {displayed_count} students")
        
        # Find all student IDs in the content
        student_id_matches = re.findall(r'<strong>([^<]+)</strong>', content)
        print(f"  📋 Student IDs found in HTML: {student_id_matches}")
        
        # Check if there are empty table rows or JavaScript hiding
        table_rows = content.count('<tr>')
        print(f"  📋 Table rows count: {table_rows}")
        
        return 'student1' in content or 'John Smith' in content
    else:
        print(f"❌ Response error: {response.status_code}")
        return False

def test_view_execution():
    """Test direct view execution"""
    print("\n=== DIRECT VIEW EXECUTION TEST ===")
    
    from django.test import RequestFactory
    
    factory = RequestFactory()
    request = factory.get('/RoutineTest/students/')
    
    # Set up request with admin user
    admin_user = User.objects.get(username='admin')
    request.user = admin_user
    
    # Add required attributes
    setattr(request, 'session', {})
    setattr(request, '_messages', [])
    
    try:
        response = student_list(request)
        print(f"✅ Direct view execution successful")
        print(f"Response status: {response.status_code}")
        
        if hasattr(response, 'context_data'):
            context = response.context_data
            students = context.get('students')
            if students:
                print(f"Context students count: {students.count()}")
                student1_in_context = students.filter(student_id='student1').exists()
                print(f"student1 in context: {student1_in_context}")
            else:
                print("❌ No students in context")
        
        return True
    except Exception as e:
        print(f"❌ Direct view execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_rendering():
    """Test if the issue is in template rendering"""
    print("\n=== TEMPLATE RENDERING TEST ===")
    
    from django.template.loader import get_template
    from django.template import Context
    from primepath_student.models import StudentProfile
    from django.db.models import Q, Count
    
    try:
        template = get_template('primepath_routinetest/student_management/student_list.html')
        print(f"✅ Template loaded: {template.origin.name if hasattr(template, 'origin') else 'Unknown'}")
        
        # Create context identical to view
        admin_user = User.objects.get(username='admin')
        admin_teacher = Teacher.objects.get(user=admin_user)
        
        students = StudentProfile.objects.all().select_related('user').annotate(
            class_count=Count('class_assignments', filter=Q(class_assignments__is_active=True))
        ).order_by('user__last_name')
        
        context = {
            'students': students,
            'is_head_teacher': admin_teacher.is_head_teacher,
            'user': admin_user
        }
        
        # Create request for template context
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/RoutineTest/students/')
        request.user = admin_user
        
        rendered = template.render(context, request=request)
        
        print(f"✅ Template rendered successfully")
        print(f"Rendered length: {len(rendered)} characters")
        
        # Check for student1 in rendered output
        if 'student1' in rendered:
            print("✅ student1 found in rendered template!")
            
            # Find the specific lines containing student1
            lines = rendered.split('\n')
            student1_lines = [line.strip() for line in lines if 'student1' in line]
            print("student1 template lines:")
            for i, line in enumerate(student1_lines[:5]):  # First 5 matches
                print(f"  {i+1}: {line[:100]}...")
                
        else:
            print("❌ student1 NOT found in rendered template!")
            
            # Debug: show what students are in the template
            student_matches = re.findall(r'<strong>([^<]+)</strong>', rendered)
            print(f"Student IDs found in rendered template: {student_matches}")
        
        return 'student1' in rendered
        
    except Exception as e:
        print(f"❌ Template rendering failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run comprehensive test"""
    print("🔍 COMPREHENSIVE STUDENT LIST TEST")
    print("="*50)
    
    url_ok = test_url_resolution()
    browser_ok = test_browser_simulation() 
    view_ok = test_view_execution()
    template_ok = test_template_rendering()
    
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    results = {
        "URL Resolution": url_ok,
        "Browser Simulation": browser_ok,
        "Direct View Execution": view_ok, 
        "Template Rendering": template_ok
    }
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print("\n🎯 CONCLUSION:")
    if all(results.values()):
        print("✅ All tests pass - student1 should be visible in browser")
        print("   If still not visible, check browser cache or JavaScript issues")
    else:
        failed_tests = [name for name, result in results.items() if not result]
        print(f"❌ Issues found in: {', '.join(failed_tests)}")
        print("   These are the root causes of the problem")

if __name__ == "__main__":
    main()
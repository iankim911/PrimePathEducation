#!/usr/bin/env python3
"""
Debug script to check why the Curriculum column is missing from the matrix display
"""
import os
import sys
import django

# Add the Django project path
sys.path.insert(0, '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')

# Initialize Django
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import User
from django.template.loader import get_template
from django.template import Context
from django.http import HttpRequest
from primepath_routinetest.views.schedule_matrix_optimized import schedule_matrix_view
from core.models import Teacher
import json

def check_template_structure():
    """Check if the template has the curriculum column in its source code"""
    print("=" * 60)
    print("STEP 1: CHECKING TEMPLATE STRUCTURE")
    print("=" * 60)
    
    template_path = '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/templates/primepath_routinetest/schedule_matrix.html'
    
    with open(template_path, 'r') as f:
        content = f.read()
    
    # Check for curriculum headers
    curriculum_headers = []
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        if 'Curriculum' in line and ('<th>' in line or '</th>' in line):
            curriculum_headers.append(f"Line {i}: {line.strip()}")
    
    print(f"Found {len(curriculum_headers)} Curriculum header(s):")
    for header in curriculum_headers:
        print(f"  ✓ {header}")
    
    # Check for curriculum cell content
    curriculum_cells = []
    for i, line in enumerate(lines, 1):
        if 'curriculum-mapping' in line or 'curriculum-badge' in line:
            curriculum_cells.append(f"Line {i}: {line.strip()}")
    
    print(f"\nFound {len(curriculum_cells)} curriculum content reference(s):")
    for cell in curriculum_cells[:5]:  # Show first 5
        print(f"  ✓ {cell}")
    
    return len(curriculum_headers) > 0 and len(curriculum_cells) > 0

def check_view_data():
    """Try to get data from the view to see what's being passed to template"""
    print("\n" + "=" * 60)
    print("STEP 2: CHECKING VIEW DATA")
    print("=" * 60)
    
    try:
        # Create a test user and teacher
        user, created = User.objects.get_or_create(
            username='test_teacher_debug',
            defaults={'password': 'test123', 'is_staff': True}
        )
        
        # Create teacher record if needed
        teacher, created = Teacher.objects.get_or_create(
            user=user,
            defaults={'full_name': 'Test Debug Teacher'}
        )
        
        # Create request
        factory = RequestFactory()
        request = factory.get('/RoutineTest/schedule-matrix/')
        request.user = user
        
        print(f"✓ Created test user: {user.username}")
        print(f"✓ Created test teacher: {teacher.full_name}")
        
        # Try to call the view
        response = schedule_matrix_view(request)
        
        if hasattr(response, 'context_data'):
            context = response.context_data
            print(f"✓ View executed successfully")
            print(f"✓ Context keys: {list(context.keys())}")
            
            # Check for matrix data
            if 'monthly_matrix' in context:
                monthly_matrix = context['monthly_matrix']
                print(f"✓ Monthly matrix has {len(monthly_matrix)} classes")
                
                # Check a sample class for curriculum mapping
                for class_code, class_data in list(monthly_matrix.items())[:2]:
                    print(f"\n  Class: {class_code}")
                    print(f"  Display name: {class_data.get('display_name', 'N/A')}")
                    
                    if 'curriculum_mapping' in class_data:
                        curr_mapping = class_data['curriculum_mapping']
                        print(f"  Curriculum mapping:")
                        print(f"    - Combined: {curr_mapping.get('combined', 'N/A')}")
                        print(f"    - Review: {curr_mapping.get('review', 'N/A')}")
                        print(f"    - Quarterly: {curr_mapping.get('quarterly', 'N/A')}")
                    else:
                        print(f"  ❌ NO curriculum_mapping in class_data!")
            
            return True
        else:
            print(f"❌ View response has no context_data")
            return False
            
    except Exception as e:
        print(f"❌ Error calling view: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_browser_simulation():
    """Simulate what the browser would receive"""
    print("\n" + "=" * 60)
    print("STEP 3: BROWSER SIMULATION")
    print("=" * 60)
    
    try:
        client = Client()
        
        # Create admin user for authentication
        user, created = User.objects.get_or_create(
            username='admin_debug',
            defaults={'password': 'admin123', 'is_staff': True, 'is_superuser': True}
        )
        if created:
            user.set_password('admin123')
            user.save()
        
        # Create teacher record
        teacher, created = Teacher.objects.get_or_create(
            user=user,
            defaults={'full_name': 'Admin Debug Teacher'}
        )
        
        # Login
        client.force_login(user)
        print(f"✓ Logged in as: {user.username}")
        
        # Make request
        response = client.get('/RoutineTest/schedule-matrix/')
        print(f"✓ Response status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check for curriculum header in HTML
            curriculum_headers = content.count('<th>Curriculum</th>')
            print(f"✓ Found {curriculum_headers} '<th>Curriculum</th>' in HTML")
            
            # Check for curriculum-mapping class
            curriculum_cells = content.count('class="curriculum-mapping"')
            print(f"✓ Found {curriculum_cells} 'class=\"curriculum-mapping\"' in HTML")
            
            # Check for curriculum-badge
            curriculum_badges = content.count('curriculum-badge')
            print(f"✓ Found {curriculum_badges} 'curriculum-badge' in HTML")
            
            # Check for specific CSS file
            matrix_css = 'schedule-matrix.css' in content
            print(f"✓ Matrix CSS loaded: {matrix_css}")
            
            # Show first few lines of matrix table
            if '<table class="matrix-table">' in content:
                table_start = content.find('<table class="matrix-table">')
                table_part = content[table_start:table_start+1000]
                print(f"\n✓ First part of matrix table:")
                print("    " + table_part.replace('\n', '\n    ')[:500] + "...")
            
            return curriculum_headers > 0
        else:
            print(f"❌ HTTP {response.status_code}: {response.reason_phrase}")
            return False
            
    except Exception as e:
        print(f"❌ Error in browser simulation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔍 DEBUGGING: Missing Curriculum Column in Matrix Display")
    print("=" * 60)
    
    # Run all checks
    template_ok = check_template_structure()
    view_ok = check_view_data()
    browser_ok = check_browser_simulation()
    
    print("\n" + "=" * 60)
    print("FINAL DIAGNOSIS")
    print("=" * 60)
    
    print(f"Template structure: {'✓ PASS' if template_ok else '❌ FAIL'}")
    print(f"View data: {'✓ PASS' if view_ok else '❌ FAIL'}")
    print(f"Browser simulation: {'✓ PASS' if browser_ok else '❌ FAIL'}")
    
    if template_ok and view_ok and browser_ok:
        print("\n🎉 ALL CHECKS PASSED!")
        print("The curriculum column SHOULD be visible in the browser.")
        print("If it's not visible, the issue is likely:")
        print("  1. Browser cache needs clearing")
        print("  2. User is not properly authenticated")
        print("  3. CSS is being overridden by other styles")
        print("  4. JavaScript is hiding the column")
    else:
        print("\n❌ ISSUES FOUND!")
        if not template_ok:
            print("  - Template structure is missing curriculum column")
        if not view_ok:
            print("  - View is not providing curriculum data")
        if not browser_ok:
            print("  - Browser simulation failed")

if __name__ == "__main__":
    main()
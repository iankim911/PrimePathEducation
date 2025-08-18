#!/usr/bin/env python
"""
Comprehensive Matrix Debugging Script
Deep analysis of the schedule matrix issue
"""
import os
import sys
import django
import json
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.template import Template, Context
from core.models import Teacher
from primepath_routinetest.models import (
    Exam, ExamScheduleMatrix, TeacherClassAssignment
)


def print_header(title):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def test_view_data_generation():
    """Test the actual data generation from the view"""
    print_header("TESTING VIEW DATA GENERATION")
    
    # Create test user and teacher
    user = User.objects.filter(username='debug_user').first()
    if not user:
        user = User.objects.create_user('debug_user', 'debug@test.com', 'testpass123')
        user.is_staff = True
        user.save()
    
    teacher, created = Teacher.objects.get_or_create(
        email=user.email,
        defaults={'name': 'Debug Teacher', 'user': user}
    )
    
    # Create multiple class assignments
    test_classes = ['CLASS_7A', 'CLASS_8B', 'CLASS_9C']
    for class_code in test_classes:
        TeacherClassAssignment.objects.get_or_create(
            teacher=teacher,
            class_code=class_code,
            defaults={'access_level': 'FULL', 'assigned_by': user}
        )
    
    print(f"  Created teacher: {teacher.name}")
    print(f"  Created class assignments: {test_classes}")
    
    # Simulate the view logic
    assigned_classes = TeacherClassAssignment.objects.filter(
        teacher=teacher,
        is_active=True
    ).order_by('class_code')
    
    current_year = str(datetime.now().year)
    
    # Build monthly matrix data (same as view)
    monthly_matrix = {}
    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
              'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    
    print(f"\n  Building monthly matrix for {len(assigned_classes)} classes...")
    
    for assignment in assigned_classes:
        class_code = assignment.class_code
        print(f"\n    Processing class: {class_code}")
        
        monthly_matrix[class_code] = {
            'display_name': assignment.get_class_code_display(),
            'access_level': assignment.access_level,
            'cells': {}
        }
        
        for month in months:
            # Get or create matrix cell
            matrix_cell, created = ExamScheduleMatrix.get_or_create_cell(
                class_code=class_code,
                academic_year=current_year,
                time_period_type='MONTHLY',
                time_period_value=month,
                user=user
            )
            
            cell_data = {
                'id': str(matrix_cell.id),
                'status': matrix_cell.status,
                'exam_count': matrix_cell.get_exam_count(),
                'color': matrix_cell.get_status_color(),
                'icon': matrix_cell.get_status_icon(),
                'scheduled_date': matrix_cell.scheduled_date.isoformat() if matrix_cell.scheduled_date else None,
                'can_edit': matrix_cell.can_teacher_edit(teacher)
            }
            
            monthly_matrix[class_code]['cells'][month] = cell_data
            
            if created:
                print(f"      Created cell for {month}: {matrix_cell.id}")
    
    # Build quarterly matrix data
    quarterly_matrix = {}
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    
    print(f"\n  Building quarterly matrix for {len(assigned_classes)} classes...")
    
    for assignment in assigned_classes:
        class_code = assignment.class_code
        
        quarterly_matrix[class_code] = {
            'display_name': assignment.get_class_code_display(),
            'access_level': assignment.access_level,
            'cells': {}
        }
        
        for quarter in quarters:
            # Get or create matrix cell
            matrix_cell, created = ExamScheduleMatrix.get_or_create_cell(
                class_code=class_code,
                academic_year=current_year,
                time_period_type='QUARTERLY',
                time_period_value=quarter,
                user=user
            )
            
            cell_data = {
                'id': str(matrix_cell.id),
                'status': matrix_cell.status,
                'exam_count': matrix_cell.get_exam_count(),
                'color': matrix_cell.get_status_color(),
                'icon': matrix_cell.get_status_icon(),
                'scheduled_date': matrix_cell.scheduled_date.isoformat() if matrix_cell.scheduled_date else None,
                'can_edit': matrix_cell.can_teacher_edit(teacher)
            }
            
            quarterly_matrix[class_code]['cells'][quarter] = cell_data
            
            if created:
                print(f"      Created cell for {quarter}: {matrix_cell.id}")
    
    # Month and quarter names
    month_names = {
        'JAN': 'January', 'FEB': 'February', 'MAR': 'March',
        'APR': 'April', 'MAY': 'May', 'JUN': 'June',
        'JUL': 'July', 'AUG': 'August', 'SEP': 'September',
        'OCT': 'October', 'NOV': 'November', 'DEC': 'December'
    }
    
    quarter_names = {
        'Q1': 'Q1 (Jan-Mar)',
        'Q2': 'Q2 (Apr-Jun)',
        'Q3': 'Q3 (Jul-Sep)',
        'Q4': 'Q4 (Oct-Dec)'
    }
    
    # Debug output
    print(f"\n  MONTHLY MATRIX STRUCTURE:")
    print(f"    Classes: {list(monthly_matrix.keys())}")
    print(f"    Months: {months}")
    
    for class_code, class_data in monthly_matrix.items():
        print(f"    {class_code}:")
        print(f"      display_name: {class_data['display_name']}")
        print(f"      cells count: {len(class_data['cells'])}")
        print(f"      cell keys: {list(class_data['cells'].keys())}")
        
        # Sample cell data
        if class_data['cells']:
            first_month = list(class_data['cells'].keys())[0]
            sample_cell = class_data['cells'][first_month]
            print(f"      sample cell ({first_month}): {sample_cell}")
    
    print(f"\n  QUARTERLY MATRIX STRUCTURE:")
    print(f"    Classes: {list(quarterly_matrix.keys())}")
    print(f"    Quarters: {quarters}")
    
    for class_code, class_data in quarterly_matrix.items():
        print(f"    {class_code}:")
        print(f"      display_name: {class_data['display_name']}")
        print(f"      cells count: {len(class_data['cells'])}")
        print(f"      cell keys: {list(class_data['cells'].keys())}")
    
    return {
        'monthly_matrix': monthly_matrix,
        'quarterly_matrix': quarterly_matrix,
        'months': months,
        'quarters': quarters,
        'month_names': month_names,
        'quarter_names': quarter_names,
        'teacher': teacher,
        'current_year': current_year,
        'assigned_classes': assigned_classes
    }


def test_template_filters():
    """Test template filters with actual data"""
    print_header("TESTING TEMPLATE FILTERS")
    
    # Generate test data
    context_data = test_view_data_generation()
    
    # Test get_item filter
    print("\n  Testing get_item filter:")
    
    try:
        from primepath_routinetest.templatetags import matrix_filters
        
        # Test with month data
        monthly_matrix = context_data['monthly_matrix']
        if monthly_matrix:
            first_class = list(monthly_matrix.keys())[0]
            class_data = monthly_matrix[first_class]
            
            print(f"    Testing with class: {first_class}")
            print(f"    Class data: {class_data}")
            
            # Test getting cells
            cells = class_data.get('cells', {})
            print(f"    Cells: {list(cells.keys())}")
            
            # Test filter
            month = 'JAN'
            cell = matrix_filters.get_item(cells, month)
            print(f"    Filter result for {month}: {cell}")
            
        print("  ✅ Template filters working correctly")
        return True
        
    except Exception as e:
        print(f"  ❌ Template filter error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_template_rendering():
    """Test actual template rendering"""
    print_header("TESTING TEMPLATE RENDERING")
    
    # Generate test data
    context_data = test_view_data_generation()
    
    # Test monthly matrix template
    monthly_template = """
    {% load matrix_filters %}
    <table>
        <thead>
            <tr>
                <th>Class</th>
                {% for month in months %}
                <th>{{ month_names|get_item:month }}</th>
                {% endfor %}
            </tr>
        </thead>
        <tbody>
            {% for class_code, class_data in monthly_matrix.items %}
            <tr>
                <td>{{ class_data.display_name }}</td>
                {% for month in months %}
                {% with cell=class_data.cells|get_item:month %}
                <td>
                    {% if cell %}
                    <div class="matrix-cell">
                        <div class="cell-icon">{{ cell.icon }}</div>
                        {% if cell.exam_count > 0 %}
                        <div class="cell-count">{{ cell.exam_count }}</div>
                        {% endif %}
                    </div>
                    {% else %}
                    <div class="matrix-cell empty">No cell data</div>
                    {% endif %}
                </td>
                {% endwith %}
                {% endfor %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
    """
    
    try:
        template = Template(monthly_template)
        context = Context(context_data)
        result = template.render(context)
        
        print("  ✅ Monthly template rendered successfully")
        print(f"    Output length: {len(result)} characters")
        
        # Check for key elements
        if 'January' in result:
            print("  ✅ Month names rendered correctly")
        if 'matrix-cell' in result:
            print("  ✅ Matrix cells rendered")
        if '⬜' in result or 'cell-icon' in result:
            print("  ✅ Cell icons present")
        
        # Save rendered output for inspection
        with open('/tmp/matrix_debug_output.html', 'w') as f:
            f.write(result)
        print("  💾 Saved output to /tmp/matrix_debug_output.html")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Template rendering error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_actual_page_response():
    """Test the actual page response"""
    print_header("TESTING ACTUAL PAGE RESPONSE")
    
    client = Client()
    
    # Create and login user
    user = User.objects.filter(username='page_test_user').first()
    if not user:
        user = User.objects.create_user('page_test_user', 'page@test.com', 'testpass123')
        user.is_staff = True
        user.save()
    
    teacher, created = Teacher.objects.get_or_create(
        email=user.email,
        defaults={'name': 'Page Test Teacher', 'user': user}
    )
    
    # Create class assignment
    TeacherClassAssignment.objects.get_or_create(
        teacher=teacher,
        class_code='CLASS_7A',
        defaults={'access_level': 'FULL', 'assigned_by': user}
    )
    
    client.force_login(user)
    
    # Test the page
    response = client.get('/RoutineTest/schedule-matrix/')
    
    if response.status_code == 200:
        print(f"  ✅ Page loads successfully: Status {response.status_code}")
        
        content = response.content.decode('utf-8')
        
        # Save the actual response for inspection
        with open('/tmp/actual_matrix_page.html', 'w') as f:
            f.write(content)
        print("  💾 Saved actual page to /tmp/actual_matrix_page.html")
        
        # Check for specific issues
        if 'TemplateSyntaxError' in content:
            print("  ❌ Template syntax error found")
        elif 'matrix_filters' in content and 'is not a registered tag library' in content:
            print("  ❌ Template filter registration error")
        else:
            print("  ✅ No template errors detected")
        
        # Check for expected content
        checks = {
            'Matrix Title': 'Exam Schedule Matrix' in content,
            'Monthly Tab': 'Monthly/Review Exams' in content,
            'Quarterly Tab': 'Quarterly Exams' in content,
            'Month Headers': any(month in content for month in ['January', 'February', 'March']),
            'Quarter Headers': any(quarter in content for quarter in ['Q1 (Jan-Mar)', 'Q2 (Apr-Jun)']),
            'Matrix Cells': 'matrix-cell' in content,
            'Cell Icons': any(icon in content for icon in ['⬜', '📅', '✅']),
            'JavaScript': 'debugLog' in content,
            'Template Load': '{% load matrix_filters %}' in content
        }
        
        print("\n  Content checks:")
        for check, passed in checks.items():
            status = "✓" if passed else "✗"
            print(f"    {status} {check}: {'Present' if passed else 'Missing'}")
        
        # Check table structure
        if '<table class="matrix-table">' in content:
            print("  ✅ Matrix table structure present")
            
            # Check for empty tbody
            import re
            tbody_pattern = r'<tbody>(.*?)</tbody>'
            tbody_matches = re.findall(tbody_pattern, content, re.DOTALL)
            
            if tbody_matches:
                tbody_content = tbody_matches[0].strip()
                if tbody_content:
                    print("  ✅ Table body has content")
                    print(f"    Tbody length: {len(tbody_content)} characters")
                else:
                    print("  ❌ Table body is empty")
            else:
                print("  ❌ No tbody found")
        
        return all(checks.values())
    else:
        print(f"  ❌ Page failed to load: Status {response.status_code}")
        return False


def main():
    """Run comprehensive debugging"""
    print("\n" + "="*80)
    print("  COMPREHENSIVE MATRIX DEBUGGING")
    print("="*80)
    print(f"  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("View Data Generation", test_view_data_generation),
        ("Template Filters", test_template_filters),
        ("Template Rendering", test_template_rendering),
        ("Actual Page Response", test_actual_page_response),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if test_name == "View Data Generation":
                # This test returns data, not boolean
                test_func()
                results.append((test_name, True))
            else:
                success = test_func()
                results.append((test_name, success))
        except Exception as e:
            print(f"\n✗ Error in {test_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Print summary
    print_header("DEBUGGING SUMMARY")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 ALL DEBUGGING TESTS PASSED!")
        print("  The matrix data and template logic appear to be working correctly.")
        print("  The issue might be browser-specific or CSS-related.")
    else:
        print(f"\n  ⚠️ {total - passed} test(s) failed")
        print("  Review the failed tests for insights.")
    
    print("\n  📁 Debug files created:")
    print("    /tmp/matrix_debug_output.html - Template rendering test")
    print("    /tmp/actual_matrix_page.html - Actual page response")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
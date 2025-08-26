#!/usr/bin/env python
"""
Live debugging script to monitor student_list view execution in real-time
"""
import os
import sys
import django

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from core.models import Teacher
from primepath_student.models import StudentProfile, StudentClassAssignment
from primepath_routinetest.models.class_access import TeacherClassAssignment
from django.db.models import Q, Count
import logging

# Set up console logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_current_browser_user():
    """
    Debug what the current browser user should see
    """
    print("=== DEBUGGING CURRENT BROWSER SESSION ===")
    print()
    
    # Check what happens for admin user (most likely browser user)
    try:
        admin_user = User.objects.get(username='admin')
        admin_teacher = Teacher.objects.get(user=admin_user)
        
        print(f"Browser User: {admin_user.username}")
        print(f"Teacher Profile: {admin_teacher.name}")
        print(f"is_head_teacher: {admin_teacher.is_head_teacher}")
        print(f"is_staff: {admin_user.is_staff}")
        print(f"is_superuser: {admin_user.is_superuser}")
        print()
        
        # Execute exact same logic as student_list view
        if admin_teacher.is_head_teacher:
            print("--- HEAD TEACHER LOGIC BRANCH ---")
            students = StudentProfile.objects.all().select_related('user').annotate(
                class_count=Count('class_assignments', filter=Q(class_assignments__is_active=True))
            ).order_by('user__last_name')
            
            print(f"Query executed: StudentProfile.objects.all() (head teacher)")
            print(f"Students found: {students.count()}")
            print()
            
            print("Students that SHOULD appear in browser:")
            student_found = False
            for student in students:
                display_name = student.user.get_full_name() or student.user.username
                print(f"  - {display_name} (ID: {student.student_id}, Classes: {student.class_count})")
                if student.student_id == 'student1':
                    student_found = True
                    print(f"    ⭐ STUDENT1 FOUND - Should appear in browser!")
                    
                    # Get detailed info about student1
                    print(f"    User active: {student.user.is_active}")
                    print(f"    User staff: {student.user.is_staff}")
                    print(f"    Profile created: {student.created_at}")
                    
                    # Check class assignments
                    assignments = student.class_assignments.filter(is_active=True)
                    print(f"    Active assignments: {assignments.count()}")
                    for assignment in assignments:
                        print(f"      -> {assignment.class_code}")
            
            if not student_found:
                print("    ❌ STUDENT1 NOT FOUND in head teacher query!")
        else:
            print("--- REGULAR TEACHER LOGIC BRANCH ---")
            teacher_classes = TeacherClassAssignment.objects.filter(
                teacher=admin_teacher,
                is_active=True
            ).values_list('class_code', flat=True)
            
            students = StudentProfile.objects.filter(
                class_assignments__class_code__in=teacher_classes,
                class_assignments__is_active=True
            ).distinct().select_related('user').annotate(
                class_count=Count('class_assignments', filter=Q(class_assignments__is_active=True))
            ).order_by('user__last_name')
            
            print(f"Teacher classes: {list(teacher_classes)}")
            print(f"Students found: {students.count()}")
            
    except Exception as e:
        print(f"❌ Error getting admin user: {e}")

def check_template_context():
    """
    Check what gets passed to the template
    """
    print("\n=== TEMPLATE CONTEXT CHECK ===")
    
    admin_user = User.objects.get(username='admin') 
    admin_teacher = Teacher.objects.get(user=admin_user)
    
    # Simulate exact context creation
    if admin_teacher.is_head_teacher:
        students = StudentProfile.objects.all().select_related('user').annotate(
            class_count=Count('class_assignments', filter=Q(class_assignments__is_active=True))
        ).order_by('user__last_name')
    else:
        teacher_classes = TeacherClassAssignment.objects.filter(
            teacher=admin_teacher,
            is_active=True
        ).values_list('class_code', flat=True)
        
        students = StudentProfile.objects.filter(
            class_assignments__class_code__in=teacher_classes,
            class_assignments__is_active=True
        ).distinct().select_related('user').annotate(
            class_count=Count('class_assignments', filter=Q(class_assignments__is_active=True))
        ).order_by('user__last_name')
    
    context = {
        'students': students,
        'is_head_teacher': admin_teacher.is_head_teacher
    }
    
    print(f"Context students count: {context['students'].count()}")
    print(f"Context is_head_teacher: {context['is_head_teacher']}")
    
    # Check if student1 would be in template context
    for student in context['students']:
        if student.student_id == 'student1':
            print(f"✅ student1 IS in template context!")
            print(f"   Name: {student.user.get_full_name()}")
            print(f"   Student ID: {student.student_id}")
            print(f"   Class count: {student.class_count}")
            return True
    
    print("❌ student1 NOT in template context!")
    return False

def verify_template_rendering():
    """
    Test template rendering directly
    """
    print("\n=== TEMPLATE RENDERING TEST ===")
    
    from django.template.loader import render_to_string
    from django.contrib.auth.models import AnonymousUser
    from django.test import RequestFactory
    
    factory = RequestFactory()
    request = factory.get('/RoutineTest/students/')
    request.user = User.objects.get(username='admin')
    
    admin_teacher = Teacher.objects.get(user=request.user)
    students = StudentProfile.objects.all().select_related('user').annotate(
        class_count=Count('class_assignments', filter=Q(class_assignments__is_active=True))
    ).order_by('user__last_name')
    
    context = {
        'students': students,
        'is_head_teacher': admin_teacher.is_head_teacher,
        'request': request
    }
    
    try:
        rendered = render_to_string('primepath_routinetest/student_management/student_list.html', context, request=request)
        
        if 'student1' in rendered:
            print("✅ student1 FOUND in rendered template!")
            
            # Extract the table row for student1
            lines = rendered.split('\n')
            student1_lines = [line for line in lines if 'student1' in line]
            for line in student1_lines[:3]:  # First 3 matches
                print(f"   Template line: {line.strip()}")
        else:
            print("❌ student1 NOT FOUND in rendered template!")
            
        print(f"\nTemplate size: {len(rendered)} characters")
        
        # Check total student count in template
        if 'Total Students:' in rendered:
            import re
            match = re.search(r'Total Students:</strong>\s*(\d+)', rendered)
            if match:
                count = match.group(1)
                print(f"Template shows: {count} total students")
        
    except Exception as e:
        print(f"❌ Template rendering failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_current_browser_user()
    student1_in_context = check_template_context() 
    verify_template_rendering()
    
    print("\n" + "="*50)
    if student1_in_context:
        print("🔍 CONCLUSION: student1 should be visible in browser")
        print("   If not visible, this is a frontend/caching issue")
    else:
        print("🔍 CONCLUSION: student1 missing from backend data")
        print("   This is a data/query issue")
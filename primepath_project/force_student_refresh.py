#!/usr/bin/env python
"""
Force refresh student1 data to ensure it appears in browser
"""

import os
import sys
import django

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.contrib.auth.models import User
from primepath_student.models import StudentProfile, StudentClassAssignment
from primepath_routinetest.models.class_access import TeacherClassAssignment
from django.core.cache import cache

def force_refresh_student1():
    """Force refresh student1 data and clear any caches"""
    
    print("=== FORCE REFRESHING STUDENT1 DATA ===")
    print()
    
    # Clear Django cache
    cache.clear()
    print("✅ Cleared Django cache")
    
    # Get student1 and touch the record to update timestamps
    try:
        user = User.objects.get(username='student1')
        profile = StudentProfile.objects.get(user=user)
        
        # Touch the user record
        user.save()
        print(f"✅ Touched user record: {user.username}")
        
        # Touch the profile record
        profile.save()
        print(f"✅ Touched profile record: {profile.student_id}")
        
        # Touch class assignments
        assignments = StudentClassAssignment.objects.filter(student=profile)
        for assignment in assignments:
            assignment.save()
            print(f"✅ Touched assignment: {assignment.class_code}")
        
        print()
        print("=== STUDENT1 FINAL STATUS ===")
        print(f"User: {user.username} ({user.get_full_name()})")
        print(f"Profile: {profile.student_id}")
        print(f"Phone: {profile.phone_number}")
        print(f"Active: {user.is_active}")
        print(f"Classes: {list(assignments.filter(is_active=True).values_list('class_code', flat=True))}")
        
    except Exception as e:
        print(f"❌ Error refreshing student1: {e}")

def add_debug_info_to_template():
    """Add debugging info to the student list template"""
    
    template_path = "/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/templates/primepath_routinetest/student_management/student_list.html"
    
    try:
        # Read current template
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Check if debug info already exists
        if 'DEBUG INFO' not in content:
            # Add debug section after the total students display
            debug_section = """
        
        <!-- DEBUG INFO - Remove after testing -->
        <div style="background-color: #fff3cd; padding: 10px; border-radius: 4px; margin-bottom: 20px; border-left: 4px solid #ffc107;">
            <h4 style="margin: 0 0 10px 0; color: #856404;">🔧 DEBUG INFO (Remove after testing)</h4>
            <p style="margin: 0; font-size: 12px; color: #856404;">
                <strong>Template rendered at:</strong> {% now "Y-m-d H:i:s" %}<br>
                <strong>Total students in context:</strong> {{ students.count }}<br>
                <strong>Current user:</strong> {{ user.username }} ({% if is_head_teacher %}Head Teacher{% else %}Regular Teacher{% endif %})<br>
                <strong>Students in queryset:</strong><br>
                {% for student in students %}
                    &nbsp;&nbsp;- {{ student.user.get_full_name }} ({{ student.student_id }}){% if student.student_id == 'student1' %} <strong>← STUDENT1 HERE!</strong>{% endif %}<br>
                {% empty %}
                    &nbsp;&nbsp;No students found in queryset!<br>
                {% endfor %}
            </p>
        </div>"""
            
            # Insert debug section after the total students info div
            content = content.replace(
                '<div class="card">',
                debug_section + '\n    <div class="card">',
                1
            )
            
            # Write back to template
            with open(template_path, 'w') as f:
                f.write(content)
            
            print("✅ Added debug info to student list template")
            print("   This will show exactly what data the template receives")
            print("   Refresh your browser to see the debug info")
            
        else:
            print("✅ Debug info already exists in template")
            
    except Exception as e:
        print(f"❌ Error adding debug info: {e}")

if __name__ == "__main__":
    force_refresh_student1()
    add_debug_info_to_template()
    
    print()
    print("=" * 50)
    print("🔄 NEXT STEPS:")
    print("1. Refresh your browser (hard refresh: Cmd+Shift+R)")
    print("2. Look for the yellow DEBUG INFO box on the student list page")
    print("3. Check if 'STUDENT1 HERE!' appears in the debug info")
    print("4. If debug shows student1 but table doesn't, it's a template issue")
    print("5. If debug doesn't show student1, it's a query issue")
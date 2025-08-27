#!/usr/bin/env python
"""
Fix RoutineTest navigation by updating all templates to use routinetest_unified_base.html
"""

import os
import re

template_dir = "/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/templates/primepath_routinetest"

# Templates that should use the new base
templates_to_update = [
    "admin_classes_teachers.html",
    "admin_pending_requests.html",
    "admin_teacher_management.html",
    "class_access_admin.html",
    "class_access.html",
    "class_code_overview.html",
    "class_details.html",
    "classes_exams_unified.html",
    "create_exam.html",
    "create_exam_fixed.html",
    "curriculum_mapping.html",
    "edit_exam.html",
    "exam_details.html",
    "exam_launch.html",
    "exam_launch_completed.html",
    "exam_results.html",
    "exam_session.html",
    "grade_distribution.html",
    "launch_history.html",
    "my_classes.html",
    "session_list.html",
    "student_exam.html",
    "student_list.html",
    "student_management.html",
    "student_session.html",
    "take_test.html",
    "test_filter.html"
]

# Dashboard templates
dashboard_templates = [
    "dashboards/admin_dashboard.html",
    "dashboards/head_teacher_dashboard.html",
    "dashboards/super_teacher_dashboard.html"
]

all_templates = templates_to_update + dashboard_templates

updates_made = 0

for template_name in all_templates:
    template_path = os.path.join(template_dir, template_name)
    
    if not os.path.exists(template_path):
        print(f"⚠️  Template not found: {template_name}")
        continue
    
    with open(template_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Replace extends directive
    if 'extends "unified_base.html"' in content:
        content = content.replace(
            'extends "unified_base.html"',
            'extends "primepath_routinetest/routinetest_unified_base.html"'
        )
        
        # Remove module_name block since it's in the base template
        content = re.sub(
            r'{% block module_name %}primepath_routinetest{% endblock %}\n?',
            '',
            content
        )
        
        # Update comment
        content = re.sub(
            r'Migrated to unified_base\.html on .*',
            'Updated 2025-08-27: Using routinetest_unified_base.html for navigation',
            content
        )
        
        # Replace content block with page_content
        content = content.replace('{% block content %}', '{% block page_content %}')
        
        if content != original_content:
            with open(template_path, 'w') as f:
                f.write(content)
            print(f"✅ Updated: {template_name}")
            updates_made += 1
        else:
            print(f"⏭️  Already updated: {template_name}")
    else:
        print(f"⏭️  Different base template: {template_name}")

print(f"\n✅ Total templates updated: {updates_made}")
print("🔄 Please restart the server or reload the page to see changes")
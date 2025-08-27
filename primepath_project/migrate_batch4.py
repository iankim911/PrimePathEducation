#!/usr/bin/env python3
"""
Phase 3, Batch 4: Migrate RoutineTest student management and Student portal auth templates
Date: August 27, 2025
"""

import os
import re
from datetime import datetime

def migrate_template(template_path, module_name):
    """Migrate a single template to unified_base.html"""
    
    if not os.path.exists(template_path):
        print(f"❌ File not found: {template_path}")
        return False
        
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if already migrated
        if 'unified_base.html' in content:
            print(f"✅ Already migrated: {os.path.basename(template_path)}")
            return True
        
        # Detect which base template is being used
        old_base = None
        if 'routinetest_base.html' in content:
            old_base = 'routinetest_base.html'
        elif 'student_base.html' in content:
            old_base = 'student_base.html'
        elif 'base.html' in content:
            old_base = 'base.html'
        
        # Replace extends statement
        content = re.sub(
            r'{%\s*extends\s+[\'"][^\'"]+[\'"]\s*%}',
            '{% extends "unified_base.html" %}',
            content,
            count=1
        )
        
        # Add migration comment after extends
        migration_comment = f"""
{{% comment %}}
Phase 3: Template Migration
Migrated from {old_base or 'base.html'} to unified_base.html
Date: {datetime.now().strftime('%B %d, %Y')}
{{% endcomment %}}"""
        
        # Insert comment after extends statement
        extends_pattern = r'({% extends "unified_base.html" %})'
        content = re.sub(extends_pattern, r'\1' + migration_comment, content, count=1)
        
        # Add module blocks after comment if not present
        if '{% block module_name %}' not in content:
            module_blocks = f"""
{{% block module_name %}}{module_name}{{% endblock %}}
{{% block data_module %}}{module_name}{{% endblock %}}
{{% block header_bg_color %}}#1B5E20{{% endblock %}}"""
            
            # Insert after the migration comment
            comment_end = '{% endcomment %}'
            if comment_end in content:
                content = content.replace(comment_end, comment_end + module_blocks, 1)
        
        # Replace {% block content %} with {% block main %}
        content = content.replace('{% block content %}', '{% block main %}')
        content = content.replace('{% endblock content %}', '{% endblock %}')
        
        # Write back
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"✅ Migrated: {os.path.basename(template_path)}")
        return True
        
    except Exception as e:
        print(f"❌ Error migrating {template_path}: {str(e)}")
        return False

def main():
    """Run Batch 4 migration"""
    
    print("=" * 60)
    print("Phase 3, Batch 4: Template Migration")
    print("=" * 60)
    
    # Batch 4 templates
    batch4_templates = [
        # RoutineTest student management templates
        ('templates/primepath_routinetest/student_exam_take.html', 'primepath_routinetest'),
        ('templates/primepath_routinetest/curriculum_mapping.html', 'primepath_routinetest'),
        ('templates/primepath_routinetest/student_management/class_students.html', 'primepath_routinetest'),
        ('templates/primepath_routinetest/student_management/student_list.html', 'primepath_routinetest'),
        ('templates/primepath_routinetest/student_management/create_student.html', 'primepath_routinetest'),
        
        # Student portal auth/admin templates
        ('templates/primepath_student/auth/register_simple.html', 'primepath_student'),
        ('templates/primepath_student/auth/password_reset.html', 'primepath_student'),
        ('templates/primepath_student/auth/password_reset_confirm.html', 'primepath_student'),
        ('templates/primepath_student/admin/dashboard.html', 'primepath_student'),
    ]
    
    success_count = 0
    
    for template_path, module_name in batch4_templates:
        if migrate_template(template_path, module_name):
            success_count += 1
    
    print()
    print("=" * 60)
    print(f"✅ Successfully migrated: {success_count}/{len(batch4_templates)} templates")
    
    if success_count == len(batch4_templates):
        print("🎉 Batch 4 migration complete!")
    else:
        print(f"⚠️  {len(batch4_templates) - success_count} templates failed to migrate")

if __name__ == "__main__":
    main()
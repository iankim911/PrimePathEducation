#!/usr/bin/env python
"""
Phase 3, Batch 3: Migrate Placement Test Templates
Date: August 27, 2025
"""

import os
import re
from pathlib import Path

# Templates to migrate
templates = [
    'templates/placement_test/create_exam.html',
    'templates/placement_test/edit_exam.html',
    'templates/placement_test/error.html',
    'templates/placement_test/exam_detail.html',
    'templates/placement_test/grade_session.html',
    'templates/placement_test/manage_questions.html',
    'templates/placement_test/preview_and_answers.html',
    'templates/placement_test/session_detail.html',
    'templates/placement_test/session_list.html',
    'templates/placement_test/start_test.html',
    'templates/placement_test/test_result.html',
]

migration_comment = """{% comment %}
Phase 3: Template Migration
Migrated from base.html to unified_base.html
Date: August 27, 2025
{% endcomment %}"""

module_blocks = """
{% block module_name %}placement_test{% endblock %}
{% block data_module %}placement_test{% endblock %}
{% block header_bg_color %}#1B5E20{% endblock %}"""

def migrate_template(filepath):
    """Migrate a single template to unified_base.html"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Check if already migrated
        if 'unified_base.html' in content:
            print(f"⏭️  {filepath} - Already migrated")
            return False
        
        # Replace extends statement
        content = re.sub(
            r'{%\s*extends\s+[\'"][^\'"]+[\'"]\s*%}',
            '{% extends "unified_base.html" %}',
            content,
            count=1
        )
        
        # Add migration comment and module blocks after extends
        lines = content.split('\n')
        new_lines = []
        extends_found = False
        
        for line in lines:
            new_lines.append(line)
            if not extends_found and 'extends' in line:
                extends_found = True
                new_lines.append(migration_comment)
                # Add module blocks if there's a title block nearby
                
        # Replace {% block content %} with {% block main %}
        content = '\n'.join(new_lines)
        content = content.replace('{% block content %}', '{% block main %}')
        
        # Add module blocks after title block if found
        if '{% block title %}' in content:
            title_end = content.find('{% endblock %}', content.find('{% block title %}'))
            if title_end != -1:
                insert_pos = content.find('\n', title_end) + 1
                content = content[:insert_pos] + module_blocks + '\n' + content[insert_pos:]
        
        # Save migrated template
        with open(filepath, 'w') as f:
            f.write(content)
        
        print(f"✅ {filepath} - Migrated successfully")
        return True
        
    except Exception as e:
        print(f"❌ {filepath} - Error: {e}")
        return False

def main():
    print("=== Phase 3, Batch 3: Placement Test Template Migration ===\n")
    
    successful = 0
    failed = 0
    
    for template in templates:
        if migrate_template(template):
            successful += 1
        else:
            failed += 1
    
    print(f"\n=== Migration Summary ===")
    print(f"✅ Successfully migrated: {successful}")
    if failed > 0:
        print(f"❌ Failed or skipped: {failed}")
    print(f"Total templates processed: {len(templates)}")

if __name__ == "__main__":
    main()
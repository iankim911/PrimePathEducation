#!/usr/bin/env python
"""
Find all unmigrated templates
"""

import os
from pathlib import Path

# All migrated templates from the middleware
MIGRATED_TEMPLATES = set([
    'test_unified_placement.html',
    'test_unified_routine.html',
    
    # Core module (10 templates)
    'core/exam_mapping.html',
    'core/login_with_kakao.html',
    'core/placement_configuration.html',
    'core/placement_rules_matrix.html',
    'core/placement_rules.html',
    'core/teacher_dashboard.html',
    'core/teacher_exams.html',
    'core/teacher_login.html',
    'core/teacher_sessions.html',
    'core/teacher_settings.html',
    
    # Registration (8 templates)
    'registration/choice.html',
    'registration/complete.html',
    'registration/step1_basic.html',
    'registration/step2_personal.html',
    'registration/step3_contact.html',
    'registration/step4_academic.html',
    'registration/step5_parent.html',
    'registration/step6_additional.html',
    
    # PlacementTest (2 templates)
    'placement_test/index.html',
    'placement_test/auth/login.html',
    
    # RoutineTest (37 templates)
    'primepath_routinetest/admin_classes_teachers.html',
    'primepath_routinetest/admin_pending_requests.html',
    'primepath_routinetest/admin_teacher_management.html',
    'primepath_routinetest/admin/manage_classes.html',
    'primepath_routinetest/analytics/dashboard.html',
    'primepath_routinetest/auth/login.html',
    'primepath_routinetest/class_access_admin.html',
    'primepath_routinetest/class_access.html',
    'primepath_routinetest/class_code_overview.html',
    'primepath_routinetest/class_details.html',
    'primepath_routinetest/classes_exams_unified_backup.html',
    'primepath_routinetest/classes_exams_unified.html',
    'primepath_routinetest/create_exam_fixed.html',
    'primepath_routinetest/create_exam.html',
    'primepath_routinetest/dashboards/admin_dashboard.html',
    'primepath_routinetest/dashboards/student_dashboard.html',
    'primepath_routinetest/dashboards/teacher_dashboard.html',
    'primepath_routinetest/edit_exam.html',
    'primepath_routinetest/error.html',
    'primepath_routinetest/exam_detail.html',
    'primepath_routinetest/exam_list_hierarchical_backup.html',
    'primepath_routinetest/exam_list_hierarchical_fixed.html',
    'primepath_routinetest/exam_list_hierarchical.html',
    'primepath_routinetest/exam_list.html',
    'primepath_routinetest/exam_results.html',
    'primepath_routinetest/grade_session.html',
    'primepath_routinetest/index.html',
    'primepath_routinetest/manage_questions.html',
    'primepath_routinetest/manage_roster.html',
    'primepath_routinetest/preview_and_answers.html',
    'primepath_routinetest/session_detail.html',
    'primepath_routinetest/session_list.html',
    'primepath_routinetest/start_test.html',
    'primepath_routinetest/teacher_assessment.html',
    'primepath_routinetest/test_result.html',
])

def find_all_templates():
    """Find all HTML templates in the templates directory"""
    templates_dir = Path('templates')
    all_templates = []
    
    for template_path in templates_dir.rglob('*.html'):
        # Get relative path from templates directory
        rel_path = template_path.relative_to(templates_dir)
        all_templates.append(str(rel_path))
    
    return sorted(all_templates)

def categorize_templates(all_templates):
    """Categorize templates by module"""
    categories = {
        'core': [],
        'registration': [],
        'placement_test': [],
        'primepath_routinetest': [],
        'primepath_student': [],
        'admin': [],
        'other': []
    }
    
    for template in all_templates:
        if template.startswith('core/'):
            categories['core'].append(template)
        elif template.startswith('registration/'):
            categories['registration'].append(template)
        elif template.startswith('placement_test/'):
            categories['placement_test'].append(template)
        elif template.startswith('primepath_routinetest/'):
            categories['primepath_routinetest'].append(template)
        elif template.startswith('primepath_student/'):
            categories['primepath_student'].append(template)
        elif template.startswith('admin/'):
            categories['admin'].append(template)
        else:
            categories['other'].append(template)
    
    return categories

def main():
    print("="*80)
    print("TEMPLATE MIGRATION STATUS ANALYSIS")
    print("="*80)
    
    # Find all templates
    all_templates = find_all_templates()
    total_count = len(all_templates)
    migrated_count = len(MIGRATED_TEMPLATES & set(all_templates))
    unmigrated_templates = set(all_templates) - MIGRATED_TEMPLATES
    unmigrated_count = len(unmigrated_templates)
    
    print(f"Total templates: {total_count}")
    print(f"Migrated templates: {migrated_count}")
    print(f"Unmigrated templates: {unmigrated_count}")
    print(f"Migration progress: {migrated_count/total_count*100:.1f}%")
    
    # Categorize all templates
    all_categorized = categorize_templates(all_templates)
    unmigrated_categorized = categorize_templates(list(unmigrated_templates))
    
    print("\n" + "="*80)
    print("MIGRATION STATUS BY MODULE")
    print("="*80)
    
    for module, templates in all_categorized.items():
        if not templates:
            continue
        migrated_in_module = len(templates) - len(unmigrated_categorized.get(module, []))
        total_in_module = len(templates)
        pct = (migrated_in_module / total_in_module * 100) if total_in_module > 0 else 0
        print(f"{module:20} {migrated_in_module:3d}/{total_in_module:3d} ({pct:5.1f}%)")
    
    print("\n" + "="*80)
    print("UNMIGRATED TEMPLATES BY MODULE")
    print("="*80)
    
    priority_order = ['primepath_student', 'placement_test', 'core', 'admin', 'other']
    
    for module in priority_order:
        templates = unmigrated_categorized.get(module, [])
        if not templates:
            continue
        
        print(f"\n{module.upper()} ({len(templates)} templates):")
        print("-" * 40)
        for template in sorted(templates):
            print(f"  {template}")
    
    return unmigrated_templates

if __name__ == '__main__':
    unmigrated = main()
    
    # Save results for use by other scripts
    with open('unmigrated_templates.txt', 'w') as f:
        for template in sorted(unmigrated):
            f.write(f"{template}\n")
    
    print(f"\nUnmigrated templates saved to unmigrated_templates.txt")
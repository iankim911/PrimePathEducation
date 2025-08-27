#!/usr/bin/env python
"""
Phase 3: Template Migration Completion Plan
Date: August 27, 2025
Purpose: Prioritized migration strategy for remaining 76 templates
"""

MIGRATION_BATCHES = {
    'batch_1_critical': {
        'priority': 'CRITICAL',
        'templates': [
            # Core authentication and base templates (5 templates)
            'core/auth/login.html',
            'core/index.html',
            'core/auth/profile.html',
            'core/auth/logout_confirm.html',
            'core/base_clean.html',
        ],
        'rationale': 'Core authentication and entry points - high visibility, low complexity'
    },
    
    'batch_2_student_portal': {
        'priority': 'HIGH',
        'templates': [
            # Student portal core functionality (8 templates)
            'primepath_student/auth/login.html',
            'primepath_student/auth/register.html',
            'primepath_student/dashboard.html',
            'primepath_student/profile.html',
            'primepath_student/class_detail.html',
            'primepath_student/exam/take_exam.html',
            'primepath_student/exam/exam_result.html',
            'primepath_student/exam/exam_history.html',
        ],
        'rationale': 'Student portal main functionality - high impact, moderate complexity'
    },
    
    'batch_3_placement_core': {
        'priority': 'HIGH', 
        'templates': [
            # Placement test core functionality (8 templates)
            'placement_test/student_test.html',
            'placement_test/student_test_v2.html',
            'placement_test/exam_list.html',
            'placement_test/exam_detail.html',
            'placement_test/test_result.html',
            'placement_test/start_test.html',
            'placement_test/session_detail.html',
            'placement_test/session_list.html',
        ],
        'rationale': 'Placement test user-facing functionality - high impact, high complexity'
    },
    
    'batch_4_admin_tools': {
        'priority': 'MEDIUM',
        'templates': [
            # Admin/teacher tools (7 templates) 
            'placement_test/create_exam.html',
            'placement_test/edit_exam.html',
            'placement_test/manage_questions.html',
            'placement_test/grade_session.html',
            'placement_test/preview_and_answers.html',
            'primepath_student/admin/dashboard.html',
            'placement_test/error.html',
        ],
        'rationale': 'Administrative functionality - medium impact, low-medium complexity'
    },
    
    'batch_5_routinetest_remaining': {
        'priority': 'MEDIUM',
        'templates': [
            # Remaining routinetest templates (19 templates)
            'primepath_routinetest/classes_exams_unified.html',
            'primepath_routinetest/exam_list_hierarchical.html', 
            'primepath_routinetest/exam_detail.html',
            'primepath_routinetest/create_exam.html',
            'primepath_routinetest/edit_exam.html',
            'primepath_routinetest/manage_questions.html',
            'primepath_routinetest/preview_and_answers.html',
            'primepath_routinetest/grade_session.html',
            'primepath_routinetest/start_test.html',
            'primepath_routinetest/test_result.html',
            'primepath_routinetest/session_list.html',
            'primepath_routinetest/session_detail.html',
            'primepath_routinetest/exam_results.html',
            'primepath_routinetest/teacher_assessment.html',
            'primepath_routinetest/class_access.html',
            'primepath_routinetest/class_details.html',
            'primepath_routinetest/admin_classes_teachers.html',
            'primepath_routinetest/admin_pending_requests.html',
            'primepath_routinetest/admin_teacher_management.html',
        ],
        'rationale': 'Complete routinetest module - medium impact, varied complexity'
    },
    
    'batch_6_supporting': {
        'priority': 'LOW',
        'templates': [
            # Supporting templates and components (29 templates)
            'primepath_student/auth/login_register_modern.html',
            'primepath_student/auth/password_reset.html',
            'primepath_student/auth/password_reset_confirm.html',
            'primepath_student/auth/register_simple.html',
            'primepath_student/emails/password_reset.html',
            'primepath_student/exam_history.html',
            'placement_test/preview_and_answers_fixed.html',
            'components/audio/player.html',
            'components/exam/question_checkbox.html',
            'components/exam/question_long.html',
            'components/exam/question_mcq.html',
            'components/exam/question_mixed.html',
            'components/exam/question_short.html',
            'components/exam/timer.html',
            'components/pdf/viewer.html',
            'components/placement_test/audio_player.html',
            'components/placement_test/difficulty_choice_modal.html',
            'components/placement_test/pdf_viewer.html',
            'components/placement_test/question_nav.html',
            'components/placement_test/question_panel.html',
            'components/placement_test/timer.html',
            'emails/analytics_report.html',
            'base.html',
            'base_adapter.html', 
            'routinetest_base.html',
            'routinetest_base_adapter.html',
            'student_base.html',
            'student_base_adapter.html',
            'unified_base.html',
        ],
        'rationale': 'Supporting components and legacy base templates - low impact but completion needed'
    }
}

def print_migration_plan():
    """Print the complete migration plan"""
    print("="*80)
    print("PHASE 3: TEMPLATE MIGRATION COMPLETION PLAN")
    print("="*80)
    
    total_templates = sum(len(batch['templates']) for batch in MIGRATION_BATCHES.values())
    print(f"Total templates to migrate: {total_templates}")
    
    batch_num = 1
    for batch_key, batch_info in MIGRATION_BATCHES.items():
        print(f"\n{batch_num}. {batch_key.upper().replace('_', ' ')}")
        print("-" * 60)
        print(f"Priority: {batch_info['priority']}")
        print(f"Templates: {len(batch_info['templates'])}")
        print(f"Rationale: {batch_info['rationale']}")
        print("\nTemplates:")
        for template in batch_info['templates']:
            print(f"  • {template}")
        batch_num += 1
    
    print("\n" + "="*80)
    print("RECOMMENDED EXECUTION STRATEGY")
    print("="*80)
    print("1. Execute batches 1-3 in day 1 (21 templates - core functionality)")
    print("2. Execute batches 4-5 in day 2 (26 templates - admin and remaining)")
    print("3. Execute batch 6 in day 3 (29 templates - components and cleanup)")
    print("4. Test after each batch to catch issues early")
    print("5. Update middleware after each successful batch")
    
    return MIGRATION_BATCHES

if __name__ == '__main__':
    batches = print_migration_plan()
    
    # Calculate progress milestones
    current_migrated = 57
    total_templates = 133
    
    print(f"\n" + "="*80)
    print("PROGRESS MILESTONES")
    print("="*80)
    
    running_total = current_migrated
    for batch_key, batch_info in batches.items():
        running_total += len(batch_info['templates'])
        percentage = (running_total / total_templates) * 100
        print(f"After {batch_key:25}: {running_total:3d}/{total_templates} ({percentage:5.1f}%)")
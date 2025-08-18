"""
Placement Test Views Module

This file maintains 100% backward compatibility.
All existing code that imports from primepath_routinetest.views will continue to work.

The views have been organized into logical modules:
- student.py: Student test-taking views
- exam.py: Exam management views  
- session.py: Session management views
- ajax.py: AJAX endpoint views

All views are re-exported here to maintain compatibility.
"""

# Import all views from the modular files
from .student import (
    start_test,
    take_test,
    submit_answer,
    adjust_difficulty,
    manual_adjust_difficulty,
    complete_test,
    test_result
)

from .exam import (
    exam_list,
    check_exam_version,
    create_exam,
    exam_detail,
    edit_exam,
    preview_exam,
    manage_questions,
    delete_exam
)

from .session import (
    session_list,
    session_detail,
    grade_session,
    export_result
)

from .ajax import (
    add_audio,
    update_question,
    create_questions,
    save_exam_answers,
    get_audio,
    update_audio_names,
    delete_audio_from_exam,
    get_curriculum_hierarchy
)

# Phase 5: Roster management views REMOVED - not needed for Answer Keys functionality
# Roster functionality has been completely removed from RoutineTest
# as it is not needed in the Answer Keys section where the prime goal is to assign answers

# Teacher Class Access Management views
from .class_access import (
    my_classes_view,
    request_access,
    withdraw_request,
    admin_pending_requests,
    approve_request,
    deny_request,
    bulk_approve_requests,
    api_my_classes,
    api_available_classes,
    api_my_requests,
    api_class_current_teachers,
    admin_teacher_assignments,
    admin_direct_assign,
    admin_revoke_access
)

# Schedule Matrix views
from .schedule_matrix import (
    schedule_matrix_view,
    matrix_cell_detail,
    bulk_assign_exams,
    get_matrix_data,
    clone_schedule
)

# Export all views for backward compatibility
__all__ = [
    # Student views
    'start_test',
    'take_test',
    'submit_answer',
    'adjust_difficulty',
    'manual_adjust_difficulty',
    'complete_test',
    'test_result',
    
    # Exam views
    'exam_list',
    'check_exam_version',
    'create_exam',
    'exam_detail',
    'edit_exam',
    'preview_exam',
    'manage_questions',
    'delete_exam',
    
    # Session views
    'session_list',
    'session_detail',
    'grade_session',
    'export_result',
    
    # AJAX views
    'add_audio',
    'update_question',
    'create_questions',
    'save_exam_answers',
    'get_audio',
    'update_audio_names',
    'delete_audio_from_exam',
    'get_curriculum_hierarchy',
    
    # Phase 5: Roster management views REMOVED - not needed
    
    # Teacher Class Access Management views
    'my_classes_view',
    'request_access',
    'withdraw_request',
    'admin_pending_requests',
    'approve_request',
    'deny_request',
    'bulk_approve_requests',
    'api_my_classes',
    'api_available_classes',
    'api_my_requests',
    'api_class_current_teachers',
    'admin_teacher_assignments',
    'admin_direct_assign',
    'admin_revoke_access',
    
    # Schedule Matrix views
    'schedule_matrix_view',
    'matrix_cell_detail',
    'bulk_assign_exams',
    'get_matrix_data',
    'clone_schedule'
]

# This ensures that the following imports continue to work:
# from primepath_routinetest import views
# from primepath_routinetest.views import start_test
# import primepath_routinetest.views as views

# No changes are required in:
# - URLs (primepath_routinetest/urls.py)
# - Templates (they use URL names, not direct imports)
# - JavaScript (uses URLs, not Python imports)
# - Other apps (if they import views)
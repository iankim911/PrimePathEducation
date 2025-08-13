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
    update_exam_name,
    get_audio,
    update_audio_names,
    delete_audio_from_exam
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
    'update_exam_name',
    'get_audio',
    'update_audio_names',
    'delete_audio_from_exam'
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
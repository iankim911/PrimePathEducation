"""
Placement Test Models Package
Part of Phase 9: Model Modularization

This file re-exports all models for backward compatibility.
All existing imports will continue to work:
- from primepath_routinetest.models import Exam
- from primepath_routinetest.models import Question, AudioFile
- etc.
"""

# Import all models from their respective modules
from .exam import Exam, AudioFile
# StudentRoster removed - not needed for Answer Keys functionality
from .question import Question
from .session import StudentSession, StudentAnswer, DifficultyAdjustment
from .class_schedule import ClassExamSchedule  # Class-specific scheduling
from .class_access import TeacherClassAssignment, ClassAccessRequest, AccessAuditLog  # Teacher class access management
from .exam_schedule_matrix import ExamScheduleMatrix  # Class × Timeslot Matrix
from .exam_abstraction import ExamAbstraction  # Unified exam interface
from .curriculum_mapping import ClassCurriculumMapping  # Admin curriculum mapping
from .class_model import Class, StudentEnrollment  # BUILDER: Day 2 - Class management
from .exam_management import RoutineExam, ExamAssignment, StudentExamAssignment, ExamAttempt, ExamLaunchSession  # BUILDER: Day 4 - Exam management

# Re-export all models for backward compatibility
__all__ = [
    'Exam',
    'AudioFile',
    # 'StudentRoster' removed - not needed for Answer Keys functionality
    'ClassExamSchedule',  # Class-specific scheduling
    'Question',
    'StudentSession',
    'StudentAnswer',
    'DifficultyAdjustment',
    'TeacherClassAssignment',  # Teacher class access management
    'ClassAccessRequest',  # Teacher access requests
    'AccessAuditLog',  # Access audit logging
    'ExamScheduleMatrix',  # Class × Timeslot Matrix
    'ClassCurriculumMapping',  # Admin curriculum mapping
    'Class',  # BUILDER: Day 2
    'StudentEnrollment',  # BUILDER: Day 2
    'RoutineExam',  # BUILDER: Day 4
    'ExamAssignment',  # BUILDER: Day 4
    'StudentExamAssignment',  # BUILDER: Day 4
    'ExamAttempt',  # BUILDER: Day 4
    'ExamLaunchSession',  # Exam launch bridge for student access
]
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
from .exam import RoutineExam, RoutineAudioFile, StudentRoster  # Main exam models
from .question import Question
from .session import StudentSession, StudentAnswer, DifficultyAdjustment
from .class_schedule import ClassExamSchedule  # Class-specific scheduling
from .class_access import TeacherClassAssignment, ClassAccessRequest, AccessAuditLog  # Teacher class access management
from .exam_schedule_matrix import ExamScheduleMatrix  # Class × Timeslot Matrix
from .exam_abstraction import ExamAbstraction  # Unified exam interface
from .curriculum_mapping import ClassCurriculumMapping  # Admin curriculum mapping
from .class_model import Class, StudentEnrollment  # BUILDER: Day 2 - Class management
from .exam_management import ManagedExam, ExamAssignment, StudentExamAssignment, ExamAttempt, ExamLaunchSession  # BUILDER: Day 4 - Exam management

# Backward compatibility aliases
Exam = RoutineExam  # Legacy import compatibility
AudioFile = RoutineAudioFile  # Legacy import compatibility

# Re-export all models for backward compatibility
__all__ = [
    'RoutineExam',  # Main exam model
    'RoutineAudioFile',  # Main audio file model
    'StudentRoster',  # Student roster management
    'Exam',  # Legacy compatibility
    'AudioFile',  # Legacy compatibility
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
    'ManagedExam',  # BUILDER: Day 4 (renamed from RoutineExam to avoid conflict)
    'ExamAssignment',  # BUILDER: Day 4
    'StudentExamAssignment',  # BUILDER: Day 4
    'ExamAttempt',  # BUILDER: Day 4
    'ExamLaunchSession',  # Exam launch bridge for student access
]
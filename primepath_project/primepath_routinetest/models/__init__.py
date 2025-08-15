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
from .exam import Exam, AudioFile, StudentRoster
from .question import Question
from .session import StudentSession, StudentAnswer, DifficultyAdjustment
from .class_schedule import ClassExamSchedule  # Class-specific scheduling

# Re-export all models for backward compatibility
__all__ = [
    'Exam',
    'AudioFile',
    'StudentRoster',  # Phase 5: Student Roster & Assignment
    'ClassExamSchedule',  # Class-specific scheduling
    'Question',
    'StudentSession',
    'StudentAnswer',
    'DifficultyAdjustment',
]
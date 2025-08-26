"""
Placement Test Models Package
Part of Phase 9: Model Modularization

This file re-exports all models for backward compatibility.
All existing imports will continue to work:
- from placement_test.models import PlacementExam as Exam
- from placement_test.models import Question, AudioFile
- etc.
"""

# Import all models from their respective modules
from .exam import PlacementExam, PlacementAudioFile
from .question import Question
from .session import StudentSession, StudentAnswer, DifficultyAdjustment

# Backward compatibility aliases
Exam = PlacementExam  # Legacy import compatibility
AudioFile = PlacementAudioFile  # Legacy import compatibility

# Re-export all models for backward compatibility
__all__ = [
    'PlacementExam',
    'PlacementAudioFile', 
    'Exam',  # Legacy compatibility
    'AudioFile',  # Legacy compatibility
    'Question',
    'StudentSession',
    'StudentAnswer',
    'DifficultyAdjustment',
]
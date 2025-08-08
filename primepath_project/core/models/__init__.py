"""
Core Models Package
Part of Phase 9: Model Modularization

This file re-exports all models for backward compatibility.
All existing imports will continue to work:
- from core.models import School
- from core.models import Program, CurriculumLevel
- etc.
"""

# Import all models from their respective modules
from .user import School, Teacher
from .curriculum import Program, SubProgram, CurriculumLevel
from .placement import PlacementRule, ExamLevelMapping

# Re-export all models for backward compatibility
__all__ = [
    'School',
    'Teacher',
    'Program',
    'SubProgram',
    'CurriculumLevel',
    'PlacementRule',
    'ExamLevelMapping',
]
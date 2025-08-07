"""
Service layer for core business logic.
"""
from .curriculum_service import CurriculumService
from .school_service import SchoolService
from .teacher_service import TeacherService

__all__ = [
    'CurriculumService',
    'SchoolService',
    'TeacherService',
]
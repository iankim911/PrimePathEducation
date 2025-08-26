"""
Service layer for core business logic.
"""
from .curriculum_service import CurriculumService
from .school_service import SchoolService
from .teacher_service import TeacherService
from .dashboard_service import DashboardService
from .file_service import FileService
from .config_service import ConfigurationService
from .security_service import SecurityService

__all__ = [
    'CurriculumService',
    'SchoolService',
    'TeacherService',
    'DashboardService',
    'FileService',
    'ConfigurationService',
    'SecurityService',
]
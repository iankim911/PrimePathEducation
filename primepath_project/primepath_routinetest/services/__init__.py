"""
Service layer for routine test business logic.
"""
from .exam_service import RoutineExamService, ExamService, ExamPermissionService  # New name + backward compatibility
from .placement_service import PlacementService
from .session_service import RoutineSessionService, SessionService  # New name + backward compatibility
from .grading_service import RoutineGradingService, GradingService  # New name + backward compatibility

__all__ = [
    # New namespace-clear names
    'RoutineExamService',
    'ExamPermissionService',  # This one is unique, no conflict
    'RoutineSessionService',
    'RoutineGradingService',
    # No conflict, keep original
    'PlacementService',
    # Backward compatibility aliases
    'ExamService',
    'SessionService',
    'GradingService',
]
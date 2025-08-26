"""
Service layer for placement test business logic.
"""
from .exam_service import PlacementExamService, ExamService  # New name + backward compatibility
from .placement_service import PlacementService
from .session_service import PlacementSessionService, SessionService  # New name + backward compatibility
from .grading_service import PlacementGradingService, GradingService  # New name + backward compatibility
from .points_service import PointsService

__all__ = [
    # New namespace-clear names
    'PlacementExamService',
    'PlacementSessionService',
    'PlacementGradingService',
    'PointsService',
    # No conflict, keep original
    'PlacementService',
    # Backward compatibility aliases
    'ExamService',
    'SessionService',
    'GradingService',
]
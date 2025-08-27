"""
Phase 4: Unified Service Registry
Date: August 26, 2025
Purpose: Central registry for all services to prevent duplicates and namespace conflicts
"""

from typing import Dict, Type, Any
import logging

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """
    Central registry for all application services.
    Prevents duplicate services and provides unified access.
    """
    
    _services: Dict[str, Any] = {}
    _interfaces: Dict[str, Type] = {}
    
    @classmethod
    def register(cls, name: str, service: Any, interface: Type = None):
        """Register a service with optional interface verification."""
        if name in cls._services:
            logger.warning(f"Service '{name}' already registered, overwriting")
        
        if interface:
            if not isinstance(service, interface):
                raise TypeError(f"Service {service} does not implement interface {interface}")
            cls._interfaces[name] = interface
        
        cls._services[name] = service
        logger.info(f"Registered service: {name}")
    
    @classmethod
    def get(cls, name: str) -> Any:
        """Get a registered service by name."""
        if name not in cls._services:
            raise KeyError(f"Service '{name}' not registered")
        return cls._services[name]
    
    @classmethod
    def has(cls, name: str) -> bool:
        """Check if a service is registered."""
        return name in cls._services
    
    @classmethod
    def list_services(cls) -> list:
        """List all registered services."""
        return list(cls._services.keys())
    
    @classmethod
    def clear(cls):
        """Clear all registered services (mainly for testing)."""
        cls._services.clear()
        cls._interfaces.clear()


# Initialize and register all services
def initialize_services():
    """Initialize all application services in the registry."""
    
    # Core services
    from core.services import (
        CurriculumService, 
        SchoolService, 
        TeacherService,
        DashboardService,
        ConfigurationService,
        FileService,
        SecurityService,
        DataService
    )
    
    ServiceRegistry.register('curriculum', CurriculumService)
    ServiceRegistry.register('school', SchoolService)
    ServiceRegistry.register('teacher', TeacherService)
    ServiceRegistry.register('dashboard', DashboardService)
    ServiceRegistry.register('config', ConfigurationService)
    ServiceRegistry.register('file', FileService)
    ServiceRegistry.register('security', SecurityService)
    ServiceRegistry.register('data', DataService)
    
    # Placement Test services
    from placement_test.services import (
        PlacementExamService,
        PlacementSessionService,
        PlacementGradingService,
        PlacementService,
        PointsService
    )
    
    ServiceRegistry.register('placement.exam', PlacementExamService)
    ServiceRegistry.register('placement.session', PlacementSessionService)
    ServiceRegistry.register('placement.grading', PlacementGradingService)
    ServiceRegistry.register('placement.rules', PlacementService)
    ServiceRegistry.register('placement.points', PointsService)
    
    # Routine Test services
    from primepath_routinetest.services import (
        RoutineExamService,
        RoutineSessionService,
        RoutineGradingService,
        ExamPermissionService
    )
    
    ServiceRegistry.register('routine.exam', RoutineExamService)
    ServiceRegistry.register('routine.session', RoutineSessionService)
    ServiceRegistry.register('routine.grading', RoutineGradingService)
    ServiceRegistry.register('routine.permissions', ExamPermissionService)
    
    # Student services (if available)
    try:
        from primepath_student.services.notification_service import NotificationService
        ServiceRegistry.register('student.notifications', NotificationService)
    except ImportError:
        logger.warning("NotificationService not available, skipping registration")
    
    logger.info(f"Initialized {len(ServiceRegistry.list_services())} services")


# Convenience functions for common services
def get_exam_service(module: str):
    """Get the appropriate exam service for a module."""
    if module == 'placement':
        return ServiceRegistry.get('placement.exam')
    elif module == 'routine':
        return ServiceRegistry.get('routine.exam')
    else:
        raise ValueError(f"Unknown module: {module}")


def get_grading_service(module: str):
    """Get the appropriate grading service for a module."""
    if module == 'placement':
        return ServiceRegistry.get('placement.grading')
    elif module == 'routine':
        return ServiceRegistry.get('routine.grading')
    else:
        raise ValueError(f"Unknown module: {module}")


def get_session_service(module: str):
    """Get the appropriate session service for a module."""
    if module == 'placement':
        return ServiceRegistry.get('placement.session')
    elif module == 'routine':
        return ServiceRegistry.get('routine.session')
    else:
        raise ValueError(f"Unknown module: {module}")
"""
Phase 4: Unified Service Interfaces
Date: August 26, 2025
Purpose: Define common interfaces that services must implement
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from django.db.models import QuerySet


class IExamService(ABC):
    """Interface for exam services across all modules."""
    
    @abstractmethod
    def get_exam(self, exam_id: str) -> Any:
        """Get an exam by ID."""
        pass
    
    @abstractmethod
    def list_exams(self, **filters) -> QuerySet:
        """List exams with optional filters."""
        pass
    
    @abstractmethod
    def create_exam(self, data: Dict) -> Any:
        """Create a new exam."""
        pass
    
    @abstractmethod
    def update_exam(self, exam_id: str, data: Dict) -> Any:
        """Update an existing exam."""
        pass
    
    @abstractmethod
    def delete_exam(self, exam_id: str) -> bool:
        """Delete an exam."""
        pass
    
    @abstractmethod
    def get_exam_questions(self, exam_id: str) -> QuerySet:
        """Get questions for an exam."""
        pass


class IGradingService(ABC):
    """Interface for grading services across all modules."""
    
    @abstractmethod
    def grade_answer(self, question, answer: str) -> Tuple[bool, int]:
        """Grade a single answer."""
        pass
    
    @abstractmethod
    def calculate_score(self, session) -> Dict:
        """Calculate total score for a session."""
        pass
    
    @abstractmethod
    def get_grading_criteria(self, question_type: str) -> Dict:
        """Get grading criteria for a question type."""
        pass


class ISessionService(ABC):
    """Interface for session services across all modules."""
    
    @abstractmethod
    def create_session(self, **kwargs) -> Any:
        """Create a new test session."""
        pass
    
    @abstractmethod
    def get_session(self, session_id: str) -> Any:
        """Get a session by ID."""
        pass
    
    @abstractmethod
    def save_answer(self, session_id: str, question_id: str, answer: str) -> bool:
        """Save an answer for a session."""
        pass
    
    @abstractmethod
    def complete_session(self, session_id: str) -> Dict:
        """Complete a test session and calculate results."""
        pass
    
    @abstractmethod
    def get_session_progress(self, session_id: str) -> Dict:
        """Get progress for a session."""
        pass


class IPlacementService(ABC):
    """Interface for placement/curriculum services."""
    
    @abstractmethod
    def get_placement_level(self, grade: int, rank: str) -> Any:
        """Get placement level based on grade and rank."""
        pass
    
    @abstractmethod
    def calculate_difficulty_adjustment(self, score: float) -> int:
        """Calculate difficulty adjustment based on score."""
        pass
    
    @abstractmethod
    def get_curriculum_hierarchy(self) -> Dict:
        """Get the curriculum hierarchy."""
        pass


class INotificationService(ABC):
    """Interface for notification services."""
    
    @abstractmethod
    def send_notification(self, recipient, message: str, **kwargs) -> bool:
        """Send a notification."""
        pass
    
    @abstractmethod
    def get_notifications(self, user, unread_only: bool = False) -> QuerySet:
        """Get notifications for a user."""
        pass
    
    @abstractmethod
    def mark_as_read(self, notification_id: str) -> bool:
        """Mark a notification as read."""
        pass


# Service implementation checker
def validate_service_implementation(service: Any, interface: Type[ABC]) -> bool:
    """
    Validate that a service implements all required interface methods.
    """
    interface_methods = [
        method for method in dir(interface)
        if not method.startswith('_') and callable(getattr(interface, method))
    ]
    
    for method in interface_methods:
        if not hasattr(service, method):
            return False
        if not callable(getattr(service, method)):
            return False
    
    return True
"""
Service for school management and operations.
"""
from typing import List, Dict, Any, Optional
from django.db import transaction
from ..models import School
import logging

logger = logging.getLogger(__name__)


class SchoolService:
    """Handles school-related operations."""
    
    @staticmethod
    def get_all_schools(active_only: bool = False) -> List[School]:
        """
        Get all schools.
        
        Args:
            active_only: Not used (School model doesn't have is_active field)
            
        Returns:
            List of School instances
        """
        queryset = School.objects.all()
        # Note: School model doesn't have is_active field
        return queryset.order_by('name')
    
    @staticmethod
    def get_school_by_id(school_id: int) -> Optional[School]:
        """
        Get a specific school by ID.
        
        Args:
            school_id: School ID
            
        Returns:
            School instance or None
        """
        try:
            return School.objects.get(id=school_id)
        except School.DoesNotExist:
            logger.warning(f"School with id {school_id} not found")
            return None
    
    @staticmethod
    def get_school_by_name(name: str) -> Optional[School]:
        """
        Get a school by exact name match.
        
        Args:
            name: School name
            
        Returns:
            School instance or None
        """
        try:
            return School.objects.get(name=name)
        except School.DoesNotExist:
            return None
        except School.MultipleObjectsReturned:
            logger.warning(f"Multiple schools found with name: {name}")
            return School.objects.filter(name=name).first()
    
    @staticmethod
    @transaction.atomic
    def create_school(school_data: Dict[str, Any]) -> School:
        """
        Create a new school.
        
        Args:
            school_data: Dictionary containing school information
            
        Returns:
            Created School instance
        """
        return School.objects.create(**school_data)
    
    @staticmethod
    @transaction.atomic
    def update_school(school_id: int, school_data: Dict[str, Any]) -> School:
        """
        Update an existing school.
        
        Args:
            school_id: School ID
            school_data: Dictionary containing updated school information
            
        Returns:
            Updated School instance
        """
        School.objects.filter(id=school_id).update(**school_data)
        return School.objects.get(id=school_id)
    
    @staticmethod
    def get_or_create_school(name: str) -> School:
        """
        Get an existing school or create a new one.
        
        Args:
            name: School name
            
        Returns:
            School instance
        """
        school, created = School.objects.get_or_create(
            name=name,
            defaults={}  # School model doesn't have is_active field
        )
        if created:
            logger.info(f"Created new school: {name}")
        return school
    
    @staticmethod
    def get_session_count_for_school(school_id: int) -> int:
        """
        Get the number of test sessions for a school.
        
        Args:
            school_id: School ID
            
        Returns:
            Number of sessions
        """
        from placement_test.models import StudentSession
        return StudentSession.objects.filter(school_id=school_id).count()
    
    @staticmethod
    def serialize_schools(schools: List[School]) -> List[Dict[str, Any]]:
        """
        Serialize schools for API responses.
        
        Args:
            schools: List of School instances
            
        Returns:
            List of dictionaries with school data
        """
        return [
            {
                'id': school.id,
                'name': school.name,
                'created_at': school.created_at.isoformat() if hasattr(school, 'created_at') else None
            }
            for school in schools
        ]
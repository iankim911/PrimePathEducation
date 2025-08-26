"""
Service for teacher management and operations.
"""
from typing import List, Dict, Any, Optional
from django.db import transaction
from django.contrib.auth.models import User
from ..models import Teacher
import logging

logger = logging.getLogger(__name__)


class TeacherService:
    """Handles teacher-related operations."""
    
    @staticmethod
    def get_all_teachers(active_only: bool = True) -> List[Teacher]:
        """
        Get all teachers, optionally filtered by active status.
        
        Args:
            active_only: Whether to return only active teachers
            
        Returns:
            List of Teacher instances
        """
        queryset = Teacher.objects.select_related('user', 'school')
        if active_only:
            queryset = queryset.filter(is_active=True)
        return queryset.order_by('user__first_name', 'user__last_name')
    
    @staticmethod
    def get_teacher_by_id(teacher_id: int) -> Optional[Teacher]:
        """
        Get a specific teacher by ID.
        
        Args:
            teacher_id: Teacher ID
            
        Returns:
            Teacher instance or None
        """
        try:
            return Teacher.objects.select_related('user', 'school').get(id=teacher_id)
        except Teacher.DoesNotExist:
            logger.warning(f"Teacher with id {teacher_id} not found")
            return None
    
    @staticmethod
    def get_teacher_by_user(user: User) -> Optional[Teacher]:
        """
        Get a teacher by their user account.
        
        Args:
            user: User instance
            
        Returns:
            Teacher instance or None
        """
        try:
            return Teacher.objects.select_related('school').get(user=user)
        except Teacher.DoesNotExist:
            logger.warning(f"No teacher found for user: {user.username}")
            return None
    
    @staticmethod
    @transaction.atomic
    def create_teacher(teacher_data: Dict[str, Any]) -> Teacher:
        """
        Create a new teacher.
        
        Args:
            teacher_data: Dictionary containing teacher information
            
        Returns:
            Created Teacher instance
        """
        return Teacher.objects.create(**teacher_data)
    
    @staticmethod
    @transaction.atomic
    def update_teacher(teacher_id: int, teacher_data: Dict[str, Any]) -> Teacher:
        """
        Update an existing teacher.
        
        Args:
            teacher_id: Teacher ID
            teacher_data: Dictionary containing updated teacher information
            
        Returns:
            Updated Teacher instance
        """
        Teacher.objects.filter(id=teacher_id).update(**teacher_data)
        return Teacher.objects.get(id=teacher_id)
    
    @staticmethod
    def get_teacher_statistics(teacher_id: int) -> Dict[str, Any]:
        """
        Get statistics for a teacher.
        
        Args:
            teacher_id: Teacher ID
            
        Returns:
            Dictionary with teacher statistics
        """
        from placement_test.models import PlacementExam as Exam, StudentSession
        
        teacher = Teacher.objects.get(id=teacher_id)
        
        # Get exam statistics
        exams = Exam.objects.filter(created_by=teacher.user)
        active_exams = exams.filter(is_active=True).count()
        total_exams = exams.count()
        
        # Get session statistics through exams
        sessions = StudentSession.objects.filter(exam__in=exams)
        total_sessions = sessions.count()
        completed_sessions = sessions.filter(is_completed=True).count()
        
        return {
            'teacher_name': f"{teacher.user.first_name} {teacher.user.last_name}",
            'school': teacher.school.name if teacher.school else None,
            'total_exams': total_exams,
            'active_exams': active_exams,
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'completion_rate': (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
        }
    
    @staticmethod
    def get_teachers_for_school(school_id: int) -> List[Teacher]:
        """
        Get all teachers for a specific school.
        
        Args:
            school_id: School ID
            
        Returns:
            List of Teacher instances
        """
        return Teacher.objects.filter(
            school_id=school_id,
            is_active=True
        ).select_related('user').order_by('user__first_name', 'user__last_name')
    
    @staticmethod
    def serialize_teachers(teachers: List[Teacher]) -> List[Dict[str, Any]]:
        """
        Serialize teachers for API responses.
        
        Args:
            teachers: List of Teacher instances
            
        Returns:
            List of dictionaries with teacher data
        """
        return [
            {
                'id': teacher.id,
                'username': teacher.user.username,
                'first_name': teacher.user.first_name,
                'last_name': teacher.user.last_name,
                'email': teacher.user.email,
                'school': teacher.school.name if teacher.school else None,
                'school_id': teacher.school_id,
                'is_active': teacher.is_active
            }
            for teacher in teachers
        ]
"""
Service for curriculum management and operations.
"""
from typing import List, Dict, Any, Optional
from django.db import transaction
from django.db.models import Prefetch, Q
from ..models import Program, SubProgram, CurriculumLevel, PlacementRule
import logging

logger = logging.getLogger(__name__)


class CurriculumService:
    """Handles curriculum levels, programs, and placement rules."""
    
    @staticmethod
    def get_programs_with_hierarchy() -> List[Program]:
        """
        Get all programs with their subprograms and levels prefetched.
        
        Returns:
            List of Program instances with related data
        """
        return Program.objects.prefetch_related(
            'subprograms__levels'
        ).all()
    
    @staticmethod
    def get_curriculum_level(level_id: int) -> Optional[CurriculumLevel]:
        """
        Get a specific curriculum level by ID.
        
        Args:
            level_id: CurriculumLevel ID
            
        Returns:
            CurriculumLevel instance or None
        """
        try:
            return CurriculumLevel.objects.select_related(
                'subprogram__program'
            ).get(id=level_id)
        except CurriculumLevel.DoesNotExist:
            logger.warning(f"CurriculumLevel with id {level_id} not found")
            return None
    
    @staticmethod
    def get_levels_for_program(program_id: int) -> List[CurriculumLevel]:
        """
        Get all curriculum levels for a specific program.
        
        Args:
            program_id: Program ID
            
        Returns:
            List of CurriculumLevel instances
        """
        return CurriculumLevel.objects.filter(
            subprogram__program_id=program_id
        ).select_related('subprogram').order_by('level_number')
    
    @staticmethod
    def get_placement_rules_for_level(level_id: int) -> List[PlacementRule]:
        """
        Get all placement rules for a curriculum level.
        
        Args:
            level_id: CurriculumLevel ID
            
        Returns:
            List of PlacementRule instances
        """
        return PlacementRule.objects.filter(
            curriculum_level_id=level_id
        ).order_by('min_percentage')
    
    @staticmethod
    @transaction.atomic
    def create_placement_rule(rule_data: Dict[str, Any]) -> PlacementRule:
        """
        Create a new placement rule.
        
        Args:
            rule_data: Dictionary containing rule information
            
        Returns:
            Created PlacementRule instance
        """
        return PlacementRule.objects.create(**rule_data)
    
    @staticmethod
    @transaction.atomic
    def update_placement_rule(rule_id: int, rule_data: Dict[str, Any]) -> PlacementRule:
        """
        Update an existing placement rule.
        
        Args:
            rule_id: PlacementRule ID
            rule_data: Dictionary containing updated rule information
            
        Returns:
            Updated PlacementRule instance
        """
        PlacementRule.objects.filter(id=rule_id).update(**rule_data)
        return PlacementRule.objects.get(id=rule_id)
    
    @staticmethod
    def get_programs_for_grade(grade: int) -> List[Program]:
        """
        Get programs available for a specific grade.
        
        Args:
            grade: Student's grade level
            
        Returns:
            List of Program instances
        """
        return Program.objects.filter(
            grade_range_start__lte=grade,
            grade_range_end__gte=grade
        ).prefetch_related('subprograms__levels')
    
    @staticmethod
    def serialize_program_hierarchy(programs: List[Program]) -> List[Dict[str, Any]]:
        """
        Serialize program hierarchy for API responses.
        
        Args:
            programs: List of Program instances
            
        Returns:
            List of dictionaries with program data
        """
        data = []
        for program in programs:
            program_data = {
                'id': program.id,
                'name': program.get_name_display(),
                'grade_range': f"{program.grade_range_start}-{program.grade_range_end}",
                'subprograms': []
            }
            for subprogram in program.subprograms.all():
                subprogram_data = {
                    'id': subprogram.id,
                    'name': subprogram.name,
                    'levels': [
                        {
                            'id': level.id,
                            'number': level.level_number,
                            'full_name': level.full_name
                        }
                        for level in subprogram.levels.all()
                    ]
                }
                program_data['subprograms'].append(subprogram_data)
            data.append(program_data)
        return data
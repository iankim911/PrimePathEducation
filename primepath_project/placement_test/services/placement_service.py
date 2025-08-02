"""
Service for handling placement logic and exam matching.
"""
from typing import Optional, Tuple
from django.db import transaction
from core.models import PlacementRule, CurriculumLevel
from core.constants import ACADEMIC_RANK_PERCENTILES
from core.exceptions import PlacementRuleException, ExamNotFoundException, ValidationException
from ..models import Exam
import logging

logger = logging.getLogger(__name__)


class PlacementService:
    """Handles placement rule matching and exam assignment logic."""
    
    @staticmethod
    def get_percentile_for_rank(academic_rank: str) -> int:
        """
        Convert academic rank to percentile.
        
        Args:
            academic_rank: Student's academic rank
            
        Returns:
            Percentile value
            
        Raises:
            ValidationException: If rank is invalid
        """
        percentile = ACADEMIC_RANK_PERCENTILES.get(academic_rank)
        if percentile is None:
            raise ValidationException(
                f"Invalid academic rank: {academic_rank}",
                code="INVALID_RANK",
                details={'academic_rank': academic_rank}
            )
        return percentile
    
    @staticmethod
    def find_matching_rule(grade: int, academic_rank: str) -> PlacementRule:
        """
        Find the matching placement rule for given grade and rank.
        
        Args:
            grade: Student's grade (1-12)
            academic_rank: Student's academic rank
            
        Returns:
            Matching PlacementRule
            
        Raises:
            PlacementRuleException: If no matching rule found
        """
        percentile = PlacementService.get_percentile_for_rank(academic_rank)
        
        matching_rule = PlacementRule.objects.filter(
            grade=grade,
            min_rank_percentile__lte=percentile,
            max_rank_percentile__gte=percentile
        ).order_by('priority').first()
        
        if not matching_rule:
            logger.warning(
                f"No placement rule found for grade={grade}, rank={academic_rank}",
                extra={'grade': grade, 'academic_rank': academic_rank, 'percentile': percentile}
            )
            raise PlacementRuleException(
                f"No matching exam found for grade {grade} with rank {academic_rank}",
                code="NO_MATCHING_RULE",
                details={'grade': grade, 'academic_rank': academic_rank}
            )
            
        logger.info(
            f"Found placement rule {matching_rule.id} for grade={grade}, rank={academic_rank}"
        )
        return matching_rule
    
    @staticmethod
    def find_exam_for_level(curriculum_level: CurriculumLevel) -> Exam:
        """
        Find an active exam for the given curriculum level using exam mappings.
        
        Args:
            curriculum_level: Target curriculum level
            
        Returns:
            Active Exam instance
            
        Raises:
            ExamNotFoundException: If no active exam exists
        """
        from core.models import ExamLevelMapping
        import random
        
        # Get all exam mappings for this curriculum level
        mappings = ExamLevelMapping.objects.filter(
            curriculum_level=curriculum_level
        ).select_related('exam')
        
        # Filter for active exams only
        active_exams = []
        for mapping in mappings:
            if mapping.exam and mapping.exam.is_active:
                active_exams.append(mapping.exam)
        
        if not active_exams:
            raise ExamNotFoundException(
                f"No active exam available for curriculum level {curriculum_level.full_name}",
                code="NO_ACTIVE_EXAM",
                details={'curriculum_level_id': curriculum_level.id}
            )
        
        # Randomly select one of the available exams
        exam = random.choice(active_exams)
        logger.info(f"Selected exam {exam.id} for curriculum level {curriculum_level.id}")
        
        return exam
    
    @staticmethod
    def match_student_to_exam(grade: int, academic_rank: str) -> Tuple[Exam, CurriculumLevel]:
        """
        Match a student to an appropriate exam based on grade and rank.
        
        Args:
            grade: Student's grade
            academic_rank: Student's academic rank
            
        Returns:
            Tuple of (Exam, CurriculumLevel)
            
        Raises:
            PlacementRuleException: If no matching rule
            ExamNotFoundException: If no active exam
        """
        # Find matching placement rule
        matching_rule = PlacementService.find_matching_rule(grade, academic_rank)
        curriculum_level = matching_rule.curriculum_level
        
        # Find active exam for the level
        exam = PlacementService.find_exam_for_level(curriculum_level)
        
        return exam, curriculum_level
    
    @staticmethod
    def adjust_difficulty(
        current_level: CurriculumLevel,
        adjustment: int
    ) -> Optional[Tuple[CurriculumLevel, Exam]]:
        """
        Adjust difficulty level up or down.
        
        Args:
            current_level: Current curriculum level
            adjustment: +1 for harder, -1 for easier
            
        Returns:
            Tuple of (new_level, new_exam) or None if adjustment not possible
        """
        if adjustment not in [-1, 1]:
            raise ValidationException(
                "Invalid adjustment value. Must be -1 or 1",
                code="INVALID_ADJUSTMENT"
            )
            
        # Get all curriculum levels in order
        all_levels = CurriculumLevel.objects.order_by(
            'subprogram__program__order',
            'subprogram__order',
            'level_number'
        )
        
        level_list = list(all_levels)
        try:
            current_index = level_list.index(current_level)
        except ValueError:
            logger.error(f"Current level {current_level.id} not found in level list")
            return None
            
        new_index = current_index + adjustment
        
        # Check bounds
        if not 0 <= new_index < len(level_list):
            logger.info(
                f"Cannot adjust difficulty: new_index={new_index} out of bounds"
            )
            return None
            
        new_level = level_list[new_index]
        
        # Try to find exam for new level
        try:
            new_exam = PlacementService.find_exam_for_level(new_level)
            return new_level, new_exam
        except ExamNotFoundException:
            logger.warning(f"No exam available for adjusted level {new_level.id}")
            return None
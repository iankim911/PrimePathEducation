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
    def find_alternate_difficulty_exam(current_level: CurriculumLevel, adjustment: int) -> Optional[Tuple[CurriculumLevel, Exam]]:
        """
        Enhanced version: Find an exam from a different difficulty tier.
        Now with smart gap handling and comprehensive logging.
        
        Args:
            current_level: Current curriculum level
            adjustment: +1 for harder, -1 for easier
            
        Returns:
            Tuple of (new_level, exam) or None if no alternate found
        """
        from core.models import ExamLevelMapping
        import json
        
        # Console logging for debugging
        console_log = {
            'action': 'find_alternate_difficulty',
            'current_level': str(current_level),
            'current_level_id': current_level.id,
            'adjustment': adjustment,
            'direction': 'harder' if adjustment > 0 else 'easier'
        }
        
        # Get current difficulty tier
        current_difficulty = current_level.internal_difficulty if hasattr(current_level, 'internal_difficulty') else None
        console_log['current_difficulty'] = current_difficulty
        
        if current_difficulty is None:
            # If no difficulty set, fall back to level-based logic
            logger.warning(
                f"No internal difficulty set for level {current_level.id}, using level-based logic"
            )
            console_log['fallback'] = 'using_level_based_logic'
            print(f"[DIFFICULTY_ADJUSTMENT] {json.dumps(console_log)}")
            return PlacementService._find_alternate_by_level(current_level, adjustment)
        
        # Smart gap handling: Find next available difficulty
        max_attempts = 10  # Prevent infinite loops
        attempts = 0
        
        while attempts < max_attempts:
            attempts += 1
            
            # Calculate target difficulty
            target_difficulty = current_difficulty + (adjustment * attempts)
            console_log['attempt'] = attempts
            console_log['target_difficulty'] = target_difficulty
            
            # Check boundaries
            if adjustment > 0 and target_difficulty > 44:  # Max difficulty
                logger.info(f"Reached maximum difficulty tier (44)")
                console_log['result'] = 'max_difficulty_reached'
                print(f"[DIFFICULTY_ADJUSTMENT] {json.dumps(console_log)}")
                return None
            elif adjustment < 0 and target_difficulty < 1:  # Min difficulty
                logger.info(f"Reached minimum difficulty tier (1)")
                console_log['result'] = 'min_difficulty_reached'
                print(f"[DIFFICULTY_ADJUSTMENT] {json.dumps(console_log)}")
                return None
            
            # Find levels with target difficulty
            alternate_levels = CurriculumLevel.objects.filter(
                internal_difficulty=target_difficulty
            ).exclude(id=current_level.id).select_related('subprogram__program')
            
            if not alternate_levels.exists():
                # No levels at this difficulty, try next
                logger.debug(f"No levels found at difficulty {target_difficulty}, trying next...")
                console_log[f'attempt_{attempts}_result'] = 'no_levels_found'
                continue
            
            # Try to find a level with an exam
            for level in alternate_levels:
                mappings = ExamLevelMapping.objects.filter(
                    curriculum_level=level
                ).select_related('exam')
                
                # Get active exams
                active_exams = [m.exam for m in mappings if m.exam.is_active]
                
                if active_exams:
                    # Success! Found an exam
                    import random
                    selected_exam = random.choice(active_exams)
                    
                    console_log['result'] = 'success'
                    console_log['new_level'] = str(level)
                    console_log['new_level_id'] = level.id
                    console_log['new_difficulty'] = target_difficulty
                    console_log['new_exam'] = selected_exam.name
                    console_log['difficulty_jump'] = target_difficulty - current_difficulty
                    
                    logger.info(
                        f"Found alternate difficulty exam: {selected_exam.name} "
                        f"at level {level} (difficulty {target_difficulty}, "
                        f"jump of {target_difficulty - current_difficulty})"
                    )
                    
                    print(f"[DIFFICULTY_ADJUSTMENT_SUCCESS] {json.dumps(console_log)}")
                    return (level, selected_exam)
            
            # No exams found at this difficulty level
            logger.debug(f"No exams found for difficulty tier {target_difficulty}, trying next...")
            console_log[f'attempt_{attempts}_result'] = 'no_exams_found'
        
        # Exhausted attempts
        logger.info(f"Could not find alternate exam after {max_attempts} attempts")
        console_log['result'] = 'no_alternate_found'
        console_log['attempts_exhausted'] = True
        print(f"[DIFFICULTY_ADJUSTMENT_FAILED] {json.dumps(console_log)}")
        return None
    
    @staticmethod
    def _find_alternate_by_level(current_level: CurriculumLevel, adjustment: int) -> Optional[Tuple[CurriculumLevel, Exam]]:
        """
        Fallback method to find alternate exam by curriculum level order.
        Used when difficulty tiers are not configured.
        """
        from core.models import ExamLevelMapping
        
        # Get all levels ordered by program hierarchy
        all_levels = list(CurriculumLevel.objects.select_related(
            'subprogram__program'
        ).order_by('subprogram__program__order', 'subprogram__order', 'level_number'))
        
        # Find current position
        try:
            current_index = all_levels.index(current_level)
        except ValueError:
            return None
        
        # Calculate target index
        target_index = current_index + adjustment
        
        if target_index < 0 or target_index >= len(all_levels):
            return None
        
        target_level = all_levels[target_index]
        
        # Try to find an exam for the target level
        mappings = ExamLevelMapping.objects.filter(
            curriculum_level=target_level
        ).select_related('exam')
        
        active_exams = [m.exam for m in mappings if m.exam.is_active]
        
        if active_exams:
            import random
            selected_exam = random.choice(active_exams)
            return (target_level, selected_exam)
        
        return None
    
    @staticmethod
    def get_difficulty_info(curriculum_level: CurriculumLevel) -> dict:
        """
        Get detailed difficulty information for a curriculum level.
        Useful for frontend display and debugging.
        """
        from core.models import ExamLevelMapping
        
        difficulty = curriculum_level.internal_difficulty
        
        # Find adjacent difficulties
        easier_exists = False
        harder_exists = False
        
        if difficulty:
            # Check for easier levels with exams
            easier_levels = CurriculumLevel.objects.filter(
                internal_difficulty__lt=difficulty
            ).order_by('-internal_difficulty')
            
            for level in easier_levels[:3]:  # Check top 3 easier
                mappings = ExamLevelMapping.objects.filter(
                    curriculum_level=level,
                    exam__is_active=True
                ).exists()
                if mappings:
                    easier_exists = True
                    break
            
            # Check for harder levels with exams
            harder_levels = CurriculumLevel.objects.filter(
                internal_difficulty__gt=difficulty
            ).order_by('internal_difficulty')
            
            for level in harder_levels[:3]:  # Check top 3 harder
                mappings = ExamLevelMapping.objects.filter(
                    curriculum_level=level,
                    exam__is_active=True
                ).exists()
                if mappings:
                    harder_exists = True
                    break
        
        return {
            'current_difficulty': difficulty,
            'current_level': str(curriculum_level),
            'can_go_easier': easier_exists,
            'can_go_harder': harder_exists,
            'difficulty_range': {
                'min': 1,
                'max': 44,
                'current': difficulty
            }
        }
    
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
# No backward compatibility alias needed - PlacementService is the original name

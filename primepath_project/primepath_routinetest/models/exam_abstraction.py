"""
Exam Abstraction Layer
Provides unified interface for accessing exam properties regardless of exam model type
Part of comprehensive fix for RoutineExam/Exam model mismatch
"""
import logging
from django.db import models

logger = logging.getLogger(__name__)


class ExamAbstraction:
    """
    Unified interface for accessing exam properties
    Handles both Exam and RoutineExam models transparently
    """
    
    @staticmethod
    def get_questions(exam_obj):
        """
        Get questions for any exam object type
        Returns QuerySet or empty list
        """
        logger.debug(f"[EXAM_ABSTRACTION] Getting questions for exam type: {type(exam_obj).__name__}")
        
        # Check if it's the main Exam model with routine_questions
        if hasattr(exam_obj, 'routine_questions'):
            logger.debug(f"[EXAM_ABSTRACTION] Found routine_questions relationship")
            return exam_obj.routine_questions.all()
        
        # Check if it's RoutineExam - try to find related Exam
        if exam_obj.__class__.__name__ == 'RoutineExam':
            logger.debug(f"[EXAM_ABSTRACTION] Handling RoutineExam object")
            
            # Try to find corresponding Exam by matching criteria
            from primepath_routinetest.models import Exam
            try:
                # Match by name and time period
                matching_exam = Exam.objects.filter(
                    name=exam_obj.name,
                    exam_type=exam_obj.exam_type if hasattr(exam_obj, 'exam_type') else 'REVIEW',
                    academic_year=exam_obj.academic_year if hasattr(exam_obj, 'academic_year') else None
                ).first()
                
                if matching_exam:
                    logger.info(f"[EXAM_ABSTRACTION] Found matching Exam for RoutineExam: {matching_exam.name}")
                    return matching_exam.routine_questions.all()
                else:
                    logger.warning(f"[EXAM_ABSTRACTION] No matching Exam found for RoutineExam: {exam_obj.name}")
            except Exception as e:
                logger.error(f"[EXAM_ABSTRACTION] Error finding matching Exam: {str(e)}")
        
        # Return empty queryset if no questions found
        from primepath_routinetest.models import Question
        return Question.objects.none()
    
    @staticmethod
    def get_audio_files(exam_obj):
        """
        Get audio files for any exam object type
        Returns QuerySet or empty list
        """
        logger.debug(f"[EXAM_ABSTRACTION] Getting audio files for exam type: {type(exam_obj).__name__}")
        
        # Check if it's the main Exam model with routine_audio_files
        if hasattr(exam_obj, 'routine_audio_files'):
            logger.debug(f"[EXAM_ABSTRACTION] Found routine_audio_files relationship")
            return exam_obj.routine_audio_files.all()
        
        # Check if it's RoutineExam - try to find related Exam
        if exam_obj.__class__.__name__ == 'RoutineExam':
            logger.debug(f"[EXAM_ABSTRACTION] Handling RoutineExam object for audio files")
            
            # Try to find corresponding Exam
            from primepath_routinetest.models import Exam
            try:
                matching_exam = Exam.objects.filter(
                    name=exam_obj.name,
                    exam_type=exam_obj.exam_type if hasattr(exam_obj, 'exam_type') else 'REVIEW',
                    academic_year=exam_obj.academic_year if hasattr(exam_obj, 'academic_year') else None
                ).first()
                
                if matching_exam:
                    logger.info(f"[EXAM_ABSTRACTION] Found matching Exam for audio files: {matching_exam.name}")
                    return matching_exam.routine_audio_files.all()
                else:
                    logger.warning(f"[EXAM_ABSTRACTION] No matching Exam found for audio files: {exam_obj.name}")
            except Exception as e:
                logger.error(f"[EXAM_ABSTRACTION] Error finding matching Exam for audio: {str(e)}")
        
        # Return empty queryset if no audio files found
        from primepath_routinetest.models import AudioFile
        return AudioFile.objects.none()
    
    @staticmethod
    def get_total_questions(exam_obj):
        """
        Get total number of questions for any exam object type
        """
        logger.debug(f"[EXAM_ABSTRACTION] Getting total questions for exam type: {type(exam_obj).__name__}")
        
        # Check direct attribute
        if hasattr(exam_obj, 'total_questions'):
            return exam_obj.total_questions
        
        # Count from questions relationship
        questions = ExamAbstraction.get_questions(exam_obj)
        return questions.count()
    
    @staticmethod
    def get_timer_minutes(exam_obj):
        """
        Get timer minutes for any exam object type
        """
        if hasattr(exam_obj, 'timer_minutes'):
            return exam_obj.timer_minutes
        
        # Default timer if not specified
        return 60
    
    @staticmethod
    def get_answer_mapping_status(exam_obj):
        """
        Get answer mapping status for any exam object type
        """
        logger.debug(f"[EXAM_ABSTRACTION] Getting answer mapping status for: {exam_obj.name}")
        
        # For RoutineExam with answer_key
        if hasattr(exam_obj, 'answer_key') and exam_obj.answer_key:
            return {
                'all_mapped': bool(exam_obj.answer_key),
                'partially_mapped': False,
                'percentage': 100.0 if exam_obj.answer_key else 0.0
            }
        
        # For Exam with routine_questions
        if hasattr(exam_obj, 'get_answer_mapping_status'):
            return exam_obj.get_answer_mapping_status()
        
        # Calculate from questions
        questions = ExamAbstraction.get_questions(exam_obj)
        total = questions.count()
        mapped = questions.filter(correct_answer__isnull=False).count() if total > 0 else 0
        
        percentage = (mapped / total * 100) if total > 0 else 0
        
        return {
            'all_mapped': percentage >= 100,
            'partially_mapped': 0 < percentage < 100,
            'percentage': round(percentage, 1)
        }
    
    @staticmethod
    def get_curriculum_level(exam_obj):
        """
        Get curriculum level for any exam object type
        """
        # Direct curriculum_level attribute (could be object or string)
        if hasattr(exam_obj, 'curriculum_level'):
            curriculum = exam_obj.curriculum_level
            
            # If it's a model object with full_name
            if hasattr(curriculum, 'full_name'):
                return curriculum.full_name
            
            # If it's a string
            if isinstance(curriculum, str):
                return curriculum
        
        return 'N/A'
    
    @staticmethod
    def get_exam_type_display(exam_obj):
        """
        Get exam type display for any exam object type
        """
        if hasattr(exam_obj, 'get_exam_type_display'):
            return exam_obj.get_exam_type_display()
        
        if hasattr(exam_obj, 'exam_type'):
            return exam_obj.exam_type
        
        return 'Unknown'
    
    @staticmethod
    def get_exam_type_short(exam_obj):
        """
        Get short exam type display
        """
        if hasattr(exam_obj, 'get_exam_type_display_short'):
            return exam_obj.get_exam_type_display_short()
        
        if hasattr(exam_obj, 'get_exam_type_display'):
            full_display = exam_obj.get_exam_type_display()
            # Extract first word
            return full_display.split()[0] if full_display else 'Unknown'
        
        if hasattr(exam_obj, 'exam_type'):
            exam_type = exam_obj.exam_type
            if exam_type == 'REVIEW':
                return 'Review'
            elif exam_type == 'QUARTERLY':
                return 'Quarterly'
        
        return 'Unknown'
    
    @staticmethod
    def safely_get_attribute(exam_obj, attribute_name, default=None):
        """
        Safely get any attribute from exam object with fallback
        """
        try:
            if hasattr(exam_obj, attribute_name):
                value = getattr(exam_obj, attribute_name)
                
                # If it's a callable (method), call it
                if callable(value):
                    return value()
                
                return value
        except Exception as e:
            logger.warning(f"[EXAM_ABSTRACTION] Error getting attribute {attribute_name}: {str(e)}")
        
        return default
"""
Exam and AudioFile models
Part of Phase 9: Model Modularization
"""
from django.db import models
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
import uuid


class PlacementExam(models.Model):
    """Main exam model containing test information and configuration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    curriculum_level = models.ForeignKey(
        'core.CurriculumLevel', 
        on_delete=models.CASCADE, 
        related_name='exams', 
        null=True, 
        blank=True
    )
    pdf_file = models.FileField(
        upload_to='exams/pdfs/',
        validators=[FileExtensionValidator(['pdf'])],
        help_text="Maximum file size: 10MB"
    )
    timer_minutes = models.IntegerField(default=60, validators=[MinValueValidator(1)])
    total_questions = models.IntegerField(validators=[MinValueValidator(1)])
    default_options_count = models.IntegerField(
        default=5, 
        validators=[MinValueValidator(2), MaxValueValidator(10)]
    )
    passing_score = models.IntegerField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    pdf_rotation = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(270)],
        help_text="PDF rotation angle in degrees (0, 90, 180, 270)"
    )
    created_by = models.ForeignKey('core.Teacher', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['curriculum_level', 'is_active']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        if self.curriculum_level:
            return f"{self.name} - {self.curriculum_level.full_name}"
        return self.name
    
    def get_answer_mapping_status(self):
        """
        Check the answer mapping status for this exam.
        Returns a dict with detailed status information.
        
        Returns:
            dict: {
                'is_complete': bool - True if all questions have answers
                'total_questions': int - Total number of questions
                'mapped_questions': int - Questions with answers
                'unmapped_questions': int - Questions without answers
                'unmapped_question_numbers': list - Question numbers without answers
                'percentage_complete': float - Percentage of questions with answers
                'status_label': str - 'Complete', 'Partial', or 'Not Started'
                'status_color': str - CSS color class for status display
            }
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Get all questions for this exam
            questions = self.questions.all()
            total_questions = questions.count()
            
            if total_questions == 0:
                # No questions created yet
                logger.warning(f"[ANSWER_MAPPING] Exam {self.id} has no questions")
                return {
                    'is_complete': False,
                    'total_questions': 0,
                    'mapped_questions': 0,
                    'unmapped_questions': 0,
                    'unmapped_question_numbers': [],
                    'percentage_complete': 0,
                    'status_label': 'No Questions',
                    'status_color': 'warning'
                }
            
            # Check which questions have answers
            unmapped = []
            mapped_count = 0
            
            for question in questions:
                has_answer = False
                
                # Check if question has an answer based on its type
                if question.question_type in ['MCQ', 'CHECKBOX']:
                    # For MCQ and CHECKBOX, check if correct_answer is not empty
                    has_answer = bool(question.correct_answer and question.correct_answer.strip())
                elif question.question_type in ['SHORT', 'LONG', 'MIXED']:
                    # For text-based answers, check if correct_answer has content
                    has_answer = bool(question.correct_answer and question.correct_answer.strip())
                
                if has_answer:
                    mapped_count += 1
                else:
                    unmapped.append(question.question_number)
            
            unmapped_count = len(unmapped)
            percentage_complete = (mapped_count / total_questions * 100) if total_questions > 0 else 0
            
            # Determine status label and color
            if unmapped_count == 0:
                status_label = 'Complete'
                status_color = 'success'
                is_complete = True
            elif mapped_count == 0:
                status_label = 'Not Started'
                status_color = 'danger'
                is_complete = False
            else:
                status_label = 'Partial'
                status_color = 'warning'
                is_complete = False
            
            # Log the status check
            logger.info(f"[ANSWER_MAPPING] Exam {self.id} ({self.name}): "
                       f"{mapped_count}/{total_questions} questions mapped. "
                       f"Status: {status_label}")
            
            return {
                'is_complete': is_complete,
                'total_questions': total_questions,
                'mapped_questions': mapped_count,
                'unmapped_questions': unmapped_count,
                'unmapped_question_numbers': unmapped[:10],  # Limit to first 10 for display
                'percentage_complete': round(percentage_complete, 1),
                'status_label': status_label,
                'status_color': status_color
            }
            
        except Exception as e:
            logger.error(f"[ANSWER_MAPPING_ERROR] Error checking answer mapping for exam {self.id}: {str(e)}")
            return {
                'is_complete': False,
                'total_questions': 0,
                'mapped_questions': 0,
                'unmapped_questions': 0,
                'unmapped_question_numbers': [],
                'percentage_complete': 0,
                'status_label': 'Error',
                'status_color': 'danger'
            }
    
    def has_all_answers_mapped(self):
        """
        Quick check if all questions have answers mapped.
        Returns True only if ALL questions have answers.
        """
        status = self.get_answer_mapping_status()
        return status['is_complete']


class PlacementAudioFile(models.Model):
    """Audio file model for listening comprehension questions"""
    exam = models.ForeignKey(PlacementExam, on_delete=models.CASCADE, related_name='audio_files')
    name = models.CharField(
        max_length=200, 
        help_text="Descriptive name for this audio file", 
        default="Audio File"
    )
    audio_file = models.FileField(
        upload_to='exams/audio/',
        validators=[FileExtensionValidator(['mp3', 'wav', 'm4a'])]
    )
    start_question = models.IntegerField(validators=[MinValueValidator(1)])
    end_question = models.IntegerField(validators=[MinValueValidator(1)])
    order = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'start_question']
        indexes = [
            models.Index(fields=['exam', 'order']),
        ]

    def __str__(self):
        if hasattr(self, 'name') and self.name:
            return f"{self.name} (Q{self.start_question}-{self.end_question})"
        return f"Audio for Q{self.start_question}-{self.end_question}"
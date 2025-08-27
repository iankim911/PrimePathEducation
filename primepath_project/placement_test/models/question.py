"""
Question model
Part of Phase 9: Model Modularization
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Question(models.Model):
    """Individual question model with various question types"""
    QUESTION_TYPES = [
        ('MCQ', 'Multiple Choice'),
        ('CHECKBOX', 'Select All'),
        ('SHORT', 'Short Answer'),
        ('LONG', 'Long Answer'),
        ('MIXED', 'Mixed'),
    ]

    exam = models.ForeignKey(
        'placement_test.PlacementExam', 
        on_delete=models.CASCADE, 
        related_name='questions'
    )
    question_number = models.IntegerField(validators=[MinValueValidator(1)])
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    correct_answer = models.TextField(
        help_text="For MCQ: single letter, For CHECKBOX: comma-separated letters"
    )
    points = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    options_count = models.IntegerField(
        default=5, 
        validators=[MinValueValidator(2), MaxValueValidator(10)]
    )
    audio_file = models.ForeignKey(
        'placement_test.PlacementAudioFile', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_question'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['question_number']
        unique_together = ['exam', 'question_number']
        indexes = [
            models.Index(fields=['exam', 'question_number']),
        ]

    def clean(self):
        """
        Validate and ensure options_count matches actual answer data for SHORT/LONG questions.
        For MIXED questions, preserve manual options_count for MCQ components.
        """
        from django.core.exceptions import ValidationError
        
        # Auto-calculate options_count for SHORT and LONG questions only
        # MIXED questions can have custom options_count for MCQ components
        if self.question_type in ['SHORT', 'LONG']:
            calculated_count = self._calculate_actual_options_count()
            if self.options_count != calculated_count:
                self.options_count = calculated_count
        elif self.question_type == 'MIXED':
            # For MIXED questions, validate that options_count is reasonable but don't auto-calculate
            # This allows teachers to customize MCQ options within MIXED questions
            if not (2 <= self.options_count <= 10):
                # Only auto-calculate if options_count is clearly invalid
                calculated_count = self._calculate_actual_options_count()
                self.options_count = max(min(calculated_count, 10), 2)
    
    def _calculate_actual_options_count(self):
        """
        Calculate the actual number of options based on correct_answer field.
        """
        if not self.correct_answer:
            return 1
        
        answer = str(self.correct_answer).strip()
        
        # For MIXED questions with JSON structure
        if self.question_type == 'MIXED':
            try:
                import json
                parsed = json.loads(answer)
                if isinstance(parsed, list):
                    return max(len(parsed), 1)
            except:
                pass
        
        # For LONG questions
        if self.question_type == 'LONG':
            # Check for multiple parts separated by triple pipe
            if '|||' in answer:
                parts = [p.strip() for p in answer.split('|||') if p.strip()]
                return max(len(parts), 1)
        
        # For SHORT questions
        if self.question_type == 'SHORT':
            # Check for multiple parts separated by pipe
            if '|' in answer:
                parts = [p.strip() for p in answer.split('|') if p.strip()]
                return max(len(parts), 1)
            elif ',' in answer:
                # Check if it's letter format or actual answers
                parts = [p.strip() for p in answer.split(',') if p.strip()]
                # If all parts are single letters, it's MCQ format
                if all(len(p) == 1 and p.isalpha() for p in parts):
                    return len(parts)
                return max(len(parts), 1)
        
        return 1
    
    def save(self, *args, **kwargs):
        """
        Override save to ensure data consistency.
        """
        # Only auto-calculate options_count for SHORT and LONG questions
        # MIXED questions can have custom options_count for MCQ components
        if self.question_type in ['SHORT', 'LONG']:
            self.options_count = self._calculate_actual_options_count()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Q{self.question_number} ({self.get_question_type_display()})"
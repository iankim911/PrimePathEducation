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
        'placement_test.Exam', 
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
        'placement_test.AudioFile', 
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

    def __str__(self):
        return f"Q{self.question_number} ({self.get_question_type_display()})"
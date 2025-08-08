"""
Exam and AudioFile models
Part of Phase 9: Model Modularization
"""
from django.db import models
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
import uuid


class Exam(models.Model):
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


class AudioFile(models.Model):
    """Audio file model for listening comprehension questions"""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='audio_files')
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
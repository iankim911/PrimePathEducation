from django.db import models
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from core.models import Teacher, School, CurriculumLevel
import uuid


class Exam(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    curriculum_level = models.ForeignKey(CurriculumLevel, on_delete=models.CASCADE, related_name='exams', null=True, blank=True)
    pdf_file = models.FileField(
        upload_to='exams/pdfs/',
        validators=[FileExtensionValidator(['pdf'])],
        help_text="Maximum file size: 10MB"
    )
    timer_minutes = models.IntegerField(default=60, validators=[MinValueValidator(1)])
    total_questions = models.IntegerField(validators=[MinValueValidator(1)])
    default_options_count = models.IntegerField(default=5, validators=[MinValueValidator(2), MaxValueValidator(10)])
    passing_score = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
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
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='audio_files')
    name = models.CharField(max_length=200, help_text="Descriptive name for this audio file", default="Audio File")
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


class Question(models.Model):
    QUESTION_TYPES = [
        ('MCQ', 'Multiple Choice'),
        ('CHECKBOX', 'Select All'),
        ('SHORT', 'Short Answer'),
        ('LONG', 'Long Answer'),
        ('MIXED', 'Mixed'),
    ]

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    question_number = models.IntegerField(validators=[MinValueValidator(1)])
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    correct_answer = models.TextField(help_text="For MCQ: single letter, For CHECKBOX: comma-separated letters")
    points = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    options_count = models.IntegerField(default=5, validators=[MinValueValidator(2), MaxValueValidator(10)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['question_number']
        unique_together = ['exam', 'question_number']
        indexes = [
            models.Index(fields=['exam', 'question_number']),
        ]

    def __str__(self):
        return f"Q{self.question_number} ({self.get_question_type_display()})"


class StudentSession(models.Model):
    ACADEMIC_RANKS = [
        ('TOP_10', 'Top 10% (English class rank)'),
        ('TOP_20', 'Top 20% (English class rank)'),
        ('TOP_30', 'Top 30% (English class rank)'),
        ('TOP_40', 'Top 40% (English class rank)'),
        ('TOP_50', 'Top 50% (English class rank)'),
        ('BELOW_50', 'Below 50% (English class rank)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student_name = models.CharField(max_length=100)
    parent_phone = models.CharField(max_length=20, default='', help_text="Contact number for admission interview")
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True)
    school_name_manual = models.CharField(max_length=200, blank=True)
    grade = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    academic_rank = models.CharField(max_length=20, choices=ACADEMIC_RANKS)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='sessions')
    original_curriculum_level = models.ForeignKey(
        CurriculumLevel, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='original_sessions'
    )
    final_curriculum_level = models.ForeignKey(
        CurriculumLevel, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='final_sessions'
    )
    difficulty_adjustments = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent_seconds = models.IntegerField(null=True, blank=True)
    
    score = models.IntegerField(null=True, blank=True)
    percentage_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['started_at']),
            models.Index(fields=['grade', 'academic_rank']),
            models.Index(fields=['exam', 'completed_at']),
        ]

    def __str__(self):
        return f"{self.student_name} - {self.exam.name} ({self.started_at.date()})"

    @property
    def is_completed(self):
        return self.completed_at is not None


class StudentAnswer(models.Model):
    session = models.ForeignKey(StudentSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField(blank=True)
    is_correct = models.BooleanField(null=True)
    points_earned = models.IntegerField(default=0)
    answered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['question__question_number']
        unique_together = ['session', 'question']
        indexes = [
            models.Index(fields=['session', 'question']),
        ]

    def __str__(self):
        return f"{self.session.student_name} - Q{self.question.question_number}"

    def auto_grade(self):
        """Automatically grade this answer using GradingService."""
        from placement_test.services import GradingService
        
        result = GradingService.auto_grade_answer(self)
        self.is_correct = result['is_correct']
        self.points_earned = result['points_earned']


class DifficultyAdjustment(models.Model):
    session = models.ForeignKey(StudentSession, on_delete=models.CASCADE, related_name='adjustments')
    from_level = models.ForeignKey(CurriculumLevel, on_delete=models.CASCADE, related_name='adjustments_from')
    to_level = models.ForeignKey(CurriculumLevel, on_delete=models.CASCADE, related_name='adjustments_to')
    adjustment = models.IntegerField()
    adjusted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.session.student_name}: {self.from_level} → {self.to_level}"
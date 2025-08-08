"""
Session-related models: StudentSession, StudentAnswer, DifficultyAdjustment
Part of Phase 9: Model Modularization
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class StudentSession(models.Model):
    """Student test session tracking"""
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
    parent_phone = models.CharField(
        max_length=20, 
        default='', 
        help_text="Contact number for admission interview"
    )
    school = models.ForeignKey('core.School', on_delete=models.SET_NULL, null=True, blank=True)
    school_name_manual = models.CharField(max_length=200, blank=True)
    grade = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    academic_rank = models.CharField(max_length=20, choices=ACADEMIC_RANKS)
    exam = models.ForeignKey('placement_test.Exam', on_delete=models.CASCADE, related_name='sessions')
    original_curriculum_level = models.ForeignKey(
        'core.CurriculumLevel', 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='original_sessions'
    )
    final_curriculum_level = models.ForeignKey(
        'core.CurriculumLevel', 
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
    """Individual answer submitted by a student"""
    session = models.ForeignKey(StudentSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('placement_test.Question', on_delete=models.CASCADE)
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
    """Track difficulty adjustments during adaptive testing"""
    session = models.ForeignKey(StudentSession, on_delete=models.CASCADE, related_name='adjustments')
    from_level = models.ForeignKey(
        'core.CurriculumLevel', 
        on_delete=models.CASCADE, 
        related_name='adjustments_from'
    )
    to_level = models.ForeignKey(
        'core.CurriculumLevel', 
        on_delete=models.CASCADE, 
        related_name='adjustments_to'
    )
    adjustment = models.IntegerField()
    adjusted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.session.student_name}: {self.from_level} → {self.to_level}"
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
    exam = models.ForeignKey('placement_test.PlacementExam', on_delete=models.CASCADE, related_name='sessions')
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
    
    @property
    def correct_answers(self):
        """Return count of correct answers for this session."""
        return self.answers.filter(is_correct=True).count()
    
    @property
    def total_questions(self):
        """Return total questions from the associated exam."""
        return self.exam.total_questions
    
    def get_timer_expiry_time(self):
        """
        Calculate when the timer should expire based on exam duration.
        
        Returns:
            datetime: The theoretical timer expiry time, or None if no timer
        """
        if not self.exam.timer_minutes:
            return None
            
        from django.utils import timezone
        import datetime
        
        return self.started_at + datetime.timedelta(minutes=self.exam.timer_minutes)
    
    def is_timer_expired(self):
        """
        Check if the timer has expired based on exam duration.
        
        Returns:
            bool: True if timer has expired, False if no timer or still active
        """
        expiry_time = self.get_timer_expiry_time()
        if not expiry_time:
            return False
            
        from django.utils import timezone
        return timezone.now() > expiry_time
    
    def is_in_grace_period(self, grace_period_seconds=300):
        """
        Check if the session is in grace period for answer submissions.
        
        CRITICAL FIX: Uses timer expiry time as reference, not completed_at.
        This prevents race conditions where completed_at is set before saves finish.
        
        Args:
            grace_period_seconds: Grace period duration in seconds (default: 300 = 5 minutes)
            
        Returns:
            bool: True if timer expired but within grace period for saves
        """
        # For non-timed exams, no grace period concept applies
        if not self.exam.timer_minutes:
            return False
            
        # If timer hasn't expired yet, not in grace period
        if not self.is_timer_expired():
            return False
            
        from django.utils import timezone
        import datetime
        
        # Calculate time since timer expiry (not completion detection)
        timer_expiry_time = self.get_timer_expiry_time()
        time_since_expiry = timezone.now() - timer_expiry_time
        grace_period = datetime.timedelta(seconds=grace_period_seconds)
        
        # Allow submissions for 5 minutes after timer expires
        return time_since_expiry <= grace_period
    
    def can_accept_answers(self):
        """
        Check if the session can accept new answer submissions.
        
        ENHANCED LOGIC FOR TIMER-BASED GRACE PERIOD:
        
        For timed exams:
        1. Timer not expired: Always allow submissions
        2. Timer expired but in grace period: Allow submissions  
        3. Timer expired and grace period over: Block submissions
        
        For non-timed exams:
        1. Not completed: Allow submissions
        2. Completed: Block submissions (no grace period concept)
        
        Returns:
            bool: True if answers can be submitted
        """
        # For timed exams, use timer-based logic
        if self.exam.timer_minutes:
            # If timer hasn't expired yet, always allow
            if not self.is_timer_expired():
                return True
            
            # Timer expired - check if in grace period
            return self.is_in_grace_period()
        
        # For non-timed exams, use completion-based logic  
        return not self.is_completed


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
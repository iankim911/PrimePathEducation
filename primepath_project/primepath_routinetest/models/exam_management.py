"""
BUILDER: Day 4 - Exam Management Models
Core models for RoutineTest exam management system
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid
import json

from core.models import Teacher, Student
from .class_model import Class


class ManagedExam(models.Model):
    """Represents a routine test exam (monthly review or quarterly) - BUILDER Day 4 version"""
    
    EXAM_TYPES = [
        ('REVIEW', 'Monthly Review'),
        ('QUARTERLY', 'Quarterly Exam')
    ]
    
    QUARTERS = [
        ('Q1', 'Quarter 1'),
        ('Q2', 'Quarter 2'),
        ('Q3', 'Quarter 3'),
        ('Q4', 'Quarter 4')
    ]
    
    MONTHS = [
        ('JAN', 'January'),
        ('FEB', 'February'),
        ('MAR', 'March'),
        ('APR', 'April'),
        ('MAY', 'May'),
        ('JUN', 'June'),
        ('JUL', 'July'),
        ('AUG', 'August'),
        ('SEP', 'September'),
        ('OCT', 'October'),
        ('NOV', 'November'),
        ('DEC', 'December')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES)
    curriculum_level = models.CharField(max_length=100)  # From 44 levels
    academic_year = models.CharField(max_length=10)  # e.g., "2025"
    
    # Time period fields - use quarter for QUARTERLY exams, month for REVIEW exams
    time_period_quarter = models.CharField(max_length=2, choices=QUARTERS, null=True, blank=True)
    time_period_month = models.CharField(max_length=3, choices=MONTHS, null=True, blank=True)
    
    # Keep quarter field for backward compatibility
    quarter = models.CharField(max_length=2, choices=QUARTERS, null=True, blank=True)
    
    # Content
    pdf_file = models.FileField(upload_to='routine_exams/', null=True, blank=True)
    answer_key = models.JSONField(default=dict, blank=True)
    duration = models.IntegerField(default=60, help_text="Exam duration in minutes")
    instructions = models.TextField(blank=True, help_text="Exam instructions for students")
    
    # Metadata
    version = models.IntegerField(default=1)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_routine_exams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'routinetest_exam'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['curriculum_level', 'time_period_quarter', 'exam_type']),
            models.Index(fields=['curriculum_level', 'time_period_month', 'exam_type']),
            models.Index(fields=['academic_year', 'time_period_quarter']),
            models.Index(fields=['academic_year', 'time_period_month']),
            models.Index(fields=['is_active']),
            models.Index(fields=['exam_type']),
        ]
        unique_together = [['name', 'academic_year', 'time_period_quarter', 'time_period_month']]
    
    def __str__(self):
        time_period = self.get_time_period_display()
        return f"{self.name} - {self.get_exam_type_display()} ({time_period} {self.academic_year})"
    
    def get_time_period_display(self):
        """Get the time period display based on exam type"""
        if self.exam_type == 'QUARTERLY' and self.time_period_quarter:
            return self.get_time_period_quarter_display()
        elif self.exam_type == 'REVIEW' and self.time_period_month:
            return self.get_time_period_month_display()
        elif self.quarter:  # Backward compatibility
            return self.get_quarter_display()
        return 'Unknown Period'
    
    def get_questions(self):
        """Get questions from answer key"""
        return list(self.answer_key.keys()) if self.answer_key else []
    
    def validate_answer_key(self):
        """Validate answer key format"""
        if not isinstance(self.answer_key, dict):
            return False
        return all(isinstance(k, str) and v for k, v in self.answer_key.items())
    
    def clone_exam(self, new_name=None):
        """Create a copy of this exam"""
        cloned = ManagedExam.objects.create(
            name=new_name or f"{self.name} (Copy)",
            exam_type=self.exam_type,
            curriculum_level=self.curriculum_level,
            academic_year=self.academic_year,
            quarter=self.quarter,
            pdf_file=self.pdf_file,
            answer_key=self.answer_key.copy() if self.answer_key else {},
            created_by=self.created_by,
            version=self.version + 1
        )
        return cloned
    
    def get_statistics(self):
        """Get exam statistics"""
        attempts = ExamAttempt.objects.filter(exam=self, is_submitted=True)
        if not attempts.exists():
            return {
                'total_attempts': 0,
                'average_score': 0,
                'highest_score': 0,
                'lowest_score': 0
            }
        
        scores = [attempt.score for attempt in attempts]
        return {
            'total_attempts': len(scores),
            'average_score': sum(scores) / len(scores),
            'highest_score': max(scores),
            'lowest_score': min(scores)
        }


class ExamAssignment(models.Model):
    """Represents assignment of an exam to a class or students"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(ManagedExam, on_delete=models.CASCADE, related_name='assignments')
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='exam_assignments')
    assigned_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='exam_assignments')
    
    # Assignment details
    deadline = models.DateTimeField()
    allow_multiple_attempts = models.BooleanField(default=True)
    is_bulk_assignment = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'routinetest_exam_assignment'
        ordering = ['-deadline']
        unique_together = [['exam', 'class_assigned', 'deadline']]
    
    def __str__(self):
        return f"{self.exam.name} -> {self.class_assigned.name} (Due: {self.deadline})"
    
    def is_past_deadline(self):
        """Check if deadline has passed"""
        return timezone.now() > self.deadline
    
    def get_completion_rate(self):
        """Get percentage of students who completed the exam"""
        total = self.student_assignments.count()
        if total == 0:
            return 0
        completed = self.student_assignments.filter(status='completed').count()
        return (completed / total) * 100
    
    def extend_deadline(self, new_deadline):
        """Extend the assignment deadline"""
        if new_deadline > self.deadline:
            self.deadline = new_deadline
            self.save()
            return True
        return False
    
    def get_student_progress(self):
        """Get progress for all students"""
        return {
            'total': self.student_assignments.count(),
            'assigned': self.student_assignments.filter(status='assigned').count(),
            'in_progress': self.student_assignments.filter(status='in_progress').count(),
            'completed': self.student_assignments.filter(status='completed').count(),
            'missed': self.student_assignments.filter(status='missed').count()
        }


class StudentExamAssignment(models.Model):
    """Represents individual student's exam assignment"""
    
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('missed', 'Missed')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_assignments')
    exam_assignment = models.ForeignKey(ExamAssignment, on_delete=models.CASCADE, related_name='student_assignments')
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    assigned_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'routinetest_student_exam_assignment'
        unique_together = [['student', 'exam_assignment']]
    
    def __str__(self):
        return f"{self.student.name} - {self.exam_assignment.exam.name}"
    
    def can_take_exam(self):
        """Check if student can still take the exam"""
        if self.status == 'completed':
            return False
        if self.exam_assignment.is_past_deadline():
            if self.status != 'in_progress':  # Allow continuing if already started
                return False
        return True
    
    def mark_as_started(self):
        """Mark assignment as started"""
        if self.status == 'assigned':
            self.status = 'in_progress'
            self.started_at = timezone.now()
            self.save()
    
    def mark_as_completed(self):
        """Mark assignment as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()


class ExamAttempt(models.Model):
    """Represents a student's attempt at an exam"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_attempts')
    exam = models.ForeignKey(ManagedExam, on_delete=models.CASCADE, related_name='attempts')
    assignment = models.ForeignKey(StudentExamAssignment, on_delete=models.CASCADE, related_name='attempts')
    
    # Attempt details
    attempt_number = models.IntegerField(default=1)
    answers = models.JSONField(default=dict)
    score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    time_spent = models.DurationField(null=True, blank=True)
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    is_submitted = models.BooleanField(default=False)
    
    # Auto-save and security
    auto_saved_data = models.JSONField(default=dict, blank=True)
    violation_flags = models.JSONField(default=list, blank=True)
    
    class Meta:
        db_table = 'routinetest_exam_attempt'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['student', 'exam', 'attempt_number']),
            models.Index(fields=['is_submitted', 'submitted_at']),
        ]
        unique_together = [['student', 'exam', 'attempt_number']]
    
    def __str__(self):
        return f"{self.student.name} - {self.exam.name} (Attempt {self.attempt_number})"
    
    def calculate_score(self):
        """Calculate score based on answers and answer key"""
        if not self.exam.answer_key or not self.answers:
            return Decimal('0.00')
        
        correct = 0
        total = len(self.exam.answer_key)
        
        for question, correct_answer in self.exam.answer_key.items():
            if self.answers.get(question) == correct_answer:
                correct += 1
        
        if total > 0:
            score = (Decimal(correct) / Decimal(total)) * 100
            return score.quantize(Decimal('0.01'))
        return Decimal('0.00')
    
    def auto_save(self, answers):
        """Auto-save current answers"""
        self.auto_saved_data = answers
        self.save()
    
    def submit(self):
        """Submit the exam attempt"""
        if not self.is_submitted:
            self.is_submitted = True
            self.submitted_at = timezone.now()
            self.score = self.calculate_score()
            
            # Calculate time spent
            if self.started_at:
                self.time_spent = self.submitted_at - self.started_at
            
            self.save()
            
            # Update assignment status
            self.assignment.mark_as_completed()
            
            return True
        return False
    
    def flag_violation(self, violation_type):
        """Flag a potential cheating violation"""
        if not isinstance(self.violation_flags, list):
            self.violation_flags = []
        
        self.violation_flags.append({
            'type': violation_type,
            'timestamp': timezone.now().isoformat()
        })
        self.save()


class ExamLaunchSession(models.Model):
    """
    Represents an exam launch by a teacher for a specific class.
    Students can access the exam through this launch session.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Exam being launched
    exam = models.ForeignKey(
        ManagedExam,
        on_delete=models.CASCADE,
        related_name='launch_sessions'
    )
    
    # Class this exam is launched for
    class_code = models.CharField(
        max_length=10,
        help_text="Class code this exam is launched for"
    )
    
    # Launch metadata
    launched_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='exam_launches'
    )
    launched_at = models.DateTimeField(default=timezone.now)
    
    # Duration and expiry
    duration_minutes = models.IntegerField(
        help_text="Custom duration for this launch (overrides exam default)"
    )
    expires_at = models.DateTimeField(
        help_text="When this exam launch expires and is no longer accessible"
    )
    
    # Launch configuration
    selected_student_ids = models.JSONField(
        default=list,
        blank=True,
        help_text="List of student IDs allowed to take this exam. Empty = all students"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'routinetest_exam_launch_session'
        ordering = ['-launched_at']
        indexes = [
            models.Index(fields=['class_code', 'is_active']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.exam.name} - {self.class_code} ({self.launched_at.date()})"
    
    def save(self, *args, **kwargs):
        """Auto-calculate expiry if not set"""
        from datetime import timedelta
        
        if not self.expires_at:
            # Set expiry to 24 hours from launch by default
            self.expires_at = self.launched_at + timedelta(hours=24)
        
        # If duration not set, use exam's default (60 minutes)
        if not self.duration_minutes and self.exam:
            self.duration_minutes = getattr(self.exam, 'timer_minutes', 60)
        
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if this launch session has expired"""
        return timezone.now() > self.expires_at
    
    def can_student_access(self, student_id):
        """Check if a specific student can access this exam"""
        if not self.is_active or self.is_expired():
            return False
        
        # If no specific students selected, all can access
        if not self.selected_student_ids:
            return True
        
        # Check if student is in the selected list
        return str(student_id) in [str(sid) for sid in self.selected_student_ids]
    
    def get_remaining_time(self):
        """Get remaining time before expiry"""
        from datetime import timedelta
        
        if self.is_expired():
            return timedelta(0)
        return self.expires_at - timezone.now()
    
    def deactivate(self):
        """Deactivate this launch session"""
        self.is_active = False
        self.save()
    
    @classmethod
    def get_active_for_class(cls, class_code):
        """Get all active launch sessions for a class"""
        return cls.objects.filter(
            class_code=class_code,
            is_active=True,
            expires_at__gt=timezone.now()
        )
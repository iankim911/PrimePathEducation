from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from primepath_routinetest.models.class_constants import CLASS_CODE_CHOICES
from core.models import Teacher
from django.utils import timezone
import random
import string
import uuid
import json


class StudentProfile(models.Model):
    """Student profile extending Django User model"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    ]
    
    GRADE_CHOICES = [
        ('K', 'Kindergarten'),
        ('1', 'Grade 1'),
        ('2', 'Grade 2'),
        ('3', 'Grade 3'),
        ('4', 'Grade 4'),
        ('5', 'Grade 5'),
        ('6', 'Grade 6'),
        ('7', 'Grade 7'),
        ('8', 'Grade 8'),
        ('9', 'Grade 9'),
        ('10', 'Grade 10'),
        ('11', 'Grade 11'),
        ('12', 'Grade 12'),
        ('UNI', 'University'),
        ('ADULT', 'Adult Student'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='primepath_student_profile')
    student_id = models.CharField(
        max_length=20, 
        unique=True,
        help_text="Unique student identifier created by student"
    )
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be valid")],
        help_text="Student's phone number for authentication"
    )
    
    # Personal Information
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    grade = models.CharField(max_length=5, choices=GRADE_CHOICES, blank=True)
    
    # Contact Information
    address = models.TextField(blank=True, help_text="Student's home address")
    emergency_contact_phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be valid")],
        help_text="Emergency contact phone number"
    )
    
    # School Information
    school_name = models.CharField(max_length=200, blank=True, help_text="Name of school student attends")
    school_address = models.TextField(blank=True, help_text="School address")
    
    # Parent/Guardian Information
    parent1_name = models.CharField(max_length=100, blank=True, help_text="First parent/guardian name")
    parent1_phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be valid")],
        help_text="First parent/guardian phone"
    )
    parent1_email = models.EmailField(blank=True, help_text="First parent/guardian email")
    
    parent2_name = models.CharField(max_length=100, blank=True, help_text="Second parent/guardian name")
    parent2_phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be valid")],
        help_text="Second parent/guardian phone"
    )
    parent2_email = models.EmailField(blank=True, help_text="Second parent/guardian email")
    
    # Account Recovery
    recovery_email = models.EmailField(
        blank=True,
        help_text="Alternative email for password recovery (can be parent's email)"
    )
    
    # System fields
    kakao_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_profile'
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'
    
    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name() or self.user.username}"
    
    @staticmethod
    def generate_student_id():
        """Generate a unique student ID if student doesn't provide one"""
        while True:
            # Format: STU + 6 random alphanumeric characters
            student_id = 'STU' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not StudentProfile.objects.filter(student_id=student_id).exists():
                return student_id
    
    @property
    def active_classes(self):
        """Get all active class assignments for this student"""
        return self.class_assignments.filter(is_active=True)
    
    @property
    def all_classes(self):
        """Get all class assignments (active and inactive) for this student"""
        return self.class_assignments.all().order_by('-is_active', '-assigned_at')


class StudentClassAssignment(models.Model):
    """Tracks student assignment to classes"""
    student = models.ForeignKey(
        StudentProfile, 
        on_delete=models.CASCADE, 
        related_name='class_assignments'
    )
    class_code = models.CharField(
        max_length=20,
        choices=CLASS_CODE_CHOICES,
        help_text="Class code the student is assigned to"
    )
    assigned_by = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        related_name='student_assignments_made'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    removed_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'student_class_assignment'
        verbose_name = 'Student Class Assignment'
        verbose_name_plural = 'Student Class Assignments'
        unique_together = ['student', 'class_code']
        indexes = [
            models.Index(fields=['student', 'is_active']),
            models.Index(fields=['class_code', 'is_active']),
        ]
    
    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        class_display = dict(CLASS_CODE_CHOICES).get(self.class_code, self.class_code)
        return f"{self.student.student_id} in {class_display} ({status})"
    
    def deactivate(self):
        """Deactivate this class assignment"""
        from django.utils import timezone
        self.is_active = False
        self.removed_at = timezone.now()
        self.save()
    
    def reactivate(self):
        """Reactivate this class assignment"""
        self.is_active = True
        self.removed_at = None
        self.save()


class StudentExamSession(models.Model):
    """
    Tracks a student's exam attempt/session
    Similar to placement test StudentSession but for routine tests
    """
    EXAM_STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
        ('abandoned', 'Abandoned'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='exam_sessions'
    )
    exam = models.ForeignKey(
        'primepath_routinetest.RoutineExam',
        on_delete=models.CASCADE,
        related_name='student_exam_sessions'
    )
    class_assignment = models.ForeignKey(
        StudentClassAssignment,
        on_delete=models.SET_NULL,
        null=True,
        help_text="The class context in which this exam was taken"
    )
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(help_text="Exam duration in minutes")
    
    # Status and Progress
    status = models.CharField(
        max_length=20,
        choices=EXAM_STATUS_CHOICES,
        default='not_started'
    )
    current_question = models.IntegerField(default=1)
    
    # Answers and Scoring
    answers = models.JSONField(
        default=dict,
        help_text="Student's answers stored as JSON"
    )
    auto_saved_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Last auto-save timestamp"
    )
    
    # Results
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Final score as percentage"
    )
    correct_answers = models.IntegerField(null=True, blank=True)
    total_questions = models.IntegerField(null=True, blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        db_table = 'student_exam_session'
        verbose_name = 'Student Exam Session'
        verbose_name_plural = 'Student Exam Sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'status', 'created_at']),
            models.Index(fields=['exam', 'status']),
            models.Index(fields=['class_assignment', 'created_at']),
            models.Index(fields=['status', 'expires_at']),  # For cleanup queries
            models.Index(fields=['student', 'exam']),  # For duplicate session checks
        ]
    
    def __str__(self):
        return f"{self.student.student_id} - {self.exam.name} ({self.status})"
    
    def start(self):
        """Start the exam session"""
        if self.status != 'not_started':
            raise ValueError("Exam has already been started")
        
        now = timezone.now()
        self.started_at = now
        self.status = 'in_progress'
        self.expires_at = now + timezone.timedelta(minutes=self.duration_minutes)
        self.save()
    
    def save_answer(self, question_number, answer):
        """Save a student's answer"""
        if self.status != 'in_progress':
            raise ValueError("Cannot save answers - exam is not in progress")
        
        if self.is_expired():
            self.expire()
            raise ValueError("Exam has expired")
        
        self.answers[str(question_number)] = answer
        self.auto_saved_at = timezone.now()
        self.current_question = question_number
        self.save()
    
    def save_answers_batch(self, answers_dict):
        """Save multiple answers at once (for auto-save)"""
        if self.status != 'in_progress':
            return False
        
        if self.is_expired():
            self.expire()
            return False
        
        self.answers.update(answers_dict)
        self.auto_saved_at = timezone.now()
        self.save()
        return True
    
    def complete(self):
        """Mark the exam as completed and calculate score"""
        if self.status not in ['in_progress', 'not_started']:
            raise ValueError("Cannot complete exam in current status")
        
        self.completed_at = timezone.now()
        self.status = 'completed'
        self.calculate_score()
        self.save()
    
    def expire(self):
        """Mark the exam as expired (time ran out)"""
        self.status = 'expired'
        self.completed_at = timezone.now()
        self.calculate_score()
        self.save()
    
    def is_expired(self):
        """Check if the exam time has expired"""
        if self.expires_at and timezone.now() > self.expires_at:
            return True
        return False
    
    def calculate_score(self):
        """Calculate the exam score based on answers"""
        if not self.exam:
            return
        
        answer_key = self.exam.answer_key if self.exam.answer_key else {}
        self.total_questions = len(answer_key)
        correct_count = 0
        
        for question_num, correct_answer in answer_key.items():
            student_answer = self.answers.get(str(question_num))
            if student_answer and student_answer == correct_answer:
                correct_count += 1
        
        self.correct_answers = correct_count
        if self.total_questions > 0:
            self.score = (correct_count / self.total_questions) * 100
        else:
            self.score = 0
        
        self.graded_at = timezone.now()
    
    def get_time_remaining(self):
        """Get time remaining in seconds"""
        if not self.expires_at or self.status != 'in_progress':
            return 0
        
        remaining = (self.expires_at - timezone.now()).total_seconds()
        return max(0, int(remaining))
    
    def get_progress_percentage(self):
        """Get exam completion progress as percentage"""
        if not self.total_questions:
            return 0
        
        answered = len([v for v in self.answers.values() if v])
        return (answered / self.total_questions) * 100
    
    @classmethod
    def get_or_create_session(cls, student, exam, class_assignment=None):
        """Get existing session or create new one"""
        # Check for existing incomplete session
        existing = cls.objects.filter(
            student=student,
            exam=exam,
            status__in=['not_started', 'in_progress']
        ).first()
        
        if existing:
            return existing, False
        
        # Create new session
        answer_key = exam.answer_key if exam.answer_key else {}
        session = cls.objects.create(
            student=student,
            exam=exam,
            class_assignment=class_assignment,
            duration_minutes=getattr(exam, 'duration', 60),  # Default 60 minutes
            total_questions=len(answer_key)
        )
        return session, True


# Import notification models so they are registered with Django
try:
    from primepath_student.models.notifications import (
        NotificationPreference,
        Notification,
        NotificationTemplate,
        NotificationQueue,
        NotificationLog
    )
except ImportError:
    pass  # Models will be imported when migrations are created

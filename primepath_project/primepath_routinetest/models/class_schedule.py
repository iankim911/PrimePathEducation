"""
Class-specific exam scheduling model
Allows different schedules for the same exam across different classes
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import logging
import json

logger = logging.getLogger(__name__)


class ClassExamSchedule(models.Model):
    """
    Represents a schedule for a specific class taking an exam.
    One exam can have multiple schedules - one for each class.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Link to exam and class
    exam = models.ForeignKey(
        'primepath_routinetest.Exam',
        on_delete=models.CASCADE,
        related_name='class_schedules'
    )
    class_code = models.CharField(
        max_length=20,
        help_text="The specific class this schedule applies to"
    )
    
    # Schedule information
    scheduled_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when this class will take the exam"
    )
    
    scheduled_start_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Start time for this class"
    )
    
    scheduled_end_time = models.TimeField(
        null=True,
        blank=True,
        help_text="End time for this class"
    )
    
    # Room/Location (optional)
    location = models.CharField(
        max_length=100,
        blank=True,
        help_text="Room or location for this class's exam"
    )
    
    # Class-specific instructions (optional, in addition to exam instructions)
    additional_instructions = models.TextField(
        blank=True,
        help_text="Additional instructions specific to this class"
    )
    
    # Late submission policy (per class)
    allow_late_submission = models.BooleanField(
        default=False,
        help_text="Whether this class can submit late"
    )
    
    late_submission_penalty = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage penalty for late submission (0-100)"
    )
    
    # Tracking
    created_by = models.ForeignKey(
        'core.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        related_name='class_schedules_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this schedule is active"
    )
    
    class Meta:
        ordering = ['scheduled_date', 'scheduled_start_time', 'class_code']
        unique_together = ['exam', 'class_code']
        indexes = [
            models.Index(fields=['exam', 'class_code']),
            models.Index(fields=['scheduled_date']),
        ]
    
    def __str__(self):
        if self.scheduled_date:
            return f"{self.exam.name} - {self.get_class_display()} on {self.scheduled_date}"
        return f"{self.exam.name} - {self.get_class_display()} (Unscheduled)"
    
    def get_class_display(self):
        """Get display name for the class code"""
        # Import here to avoid circular dependency
        from .exam import Exam
        class_dict = dict(Exam.CLASS_CODE_CHOICES)
        return class_dict.get(self.class_code, self.class_code)
    
    def get_schedule_display(self):
        """Get formatted schedule display for this class"""
        if not self.scheduled_date:
            return "Not scheduled"
        
        from django.utils import formats
        date_str = formats.date_format(self.scheduled_date, "M d, Y")
        
        if self.scheduled_start_time and self.scheduled_end_time:
            start_time = self.scheduled_start_time.strftime("%I:%M %p")
            end_time = self.scheduled_end_time.strftime("%I:%M %p")
            schedule = f"{date_str} • {start_time} - {end_time}"
        elif self.scheduled_start_time:
            start_time = self.scheduled_start_time.strftime("%I:%M %p")
            schedule = f"{date_str} • {start_time}"
        else:
            schedule = date_str
        
        if self.location:
            schedule += f" • {self.location}"
        
        return schedule
    
    def get_schedule_short(self):
        """Get short schedule display for compact views"""
        if not self.scheduled_date:
            return ""
        
        from django.utils import formats
        date_str = formats.date_format(self.scheduled_date, "M d")
        
        if self.scheduled_start_time:
            time_str = self.scheduled_start_time.strftime("%I:%M%p").lower()
            return f"{date_str} @ {time_str}"
        return date_str
    
    def is_scheduled(self):
        """Check if this class has scheduling information"""
        return bool(self.scheduled_date)
    
    def get_late_policy_display(self):
        """Get formatted late submission policy for this class"""
        if not self.allow_late_submission:
            return "No late submissions"
        
        if self.late_submission_penalty > 0:
            return f"Late: -{self.late_submission_penalty}%"
        else:
            return "Late allowed"
    
    def can_student_access(self, current_time=None):
        """
        Check if students in this class can access the exam based on schedule.
        
        Args:
            current_time: DateTime to check against (defaults to now)
            
        Returns:
            tuple: (can_access: bool, message: str)
        """
        from django.utils import timezone
        import datetime
        
        if current_time is None:
            current_time = timezone.now()
        
        # If no schedule set, always allow access
        if not self.scheduled_date:
            return True, "Exam available"
        
        # Combine date and time for comparison
        if self.scheduled_start_time:
            scheduled_datetime = timezone.make_aware(
                datetime.datetime.combine(
                    self.scheduled_date,
                    self.scheduled_start_time
                )
            )
            
            if current_time < scheduled_datetime:
                time_until = scheduled_datetime - current_time
                hours = int(time_until.total_seconds() // 3600)
                minutes = int((time_until.total_seconds() % 3600) // 60)
                return False, f"Exam starts in {hours}h {minutes}m"
        
        # Check if exam has ended (with grace period for late submission)
        if self.scheduled_end_time:
            scheduled_end = timezone.make_aware(
                datetime.datetime.combine(
                    self.scheduled_date,
                    self.scheduled_end_time
                )
            )
            
            if self.allow_late_submission:
                # Add 24 hour grace period for late submissions
                grace_period = datetime.timedelta(hours=24)
                final_deadline = scheduled_end + grace_period
                
                if current_time > final_deadline:
                    return False, "Exam period has ended"
                elif current_time > scheduled_end:
                    return True, f"Late submission (-{self.late_submission_penalty}%)"
            else:
                if current_time > scheduled_end:
                    return False, "Exam period has ended"
        
        return True, "Exam in progress"
    
    def save(self, *args, **kwargs):
        """Override save to add logging"""
        is_new = self.pk is None
        
        console_log = {
            "model": "ClassExamSchedule",
            "action": "create" if is_new else "update",
            "exam_id": str(self.exam_id),
            "exam_name": self.exam.name if self.exam else None,
            "class_code": self.class_code,
            "scheduled_date": str(self.scheduled_date) if self.scheduled_date else None,
            "scheduled_time": (
                f"{self.scheduled_start_time} - {self.scheduled_end_time}" 
                if self.scheduled_start_time else None
            ),
            "location": self.location,
            "allow_late": self.allow_late_submission
        }
        
        logger.info(f"[CLASS_SCHEDULE_SAVE] {json.dumps(console_log)}")
        print(f"[CLASS_SCHEDULE_SAVE] {json.dumps(console_log)}")
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Override delete to add logging"""
        console_log = {
            "model": "ClassExamSchedule",
            "action": "delete",
            "exam_id": str(self.exam_id),
            "class_code": self.class_code,
            "was_scheduled": self.is_scheduled()
        }
        
        logger.info(f"[CLASS_SCHEDULE_DELETE] {json.dumps(console_log)}")
        print(f"[CLASS_SCHEDULE_DELETE] {json.dumps(console_log)}")
        
        super().delete(*args, **kwargs)
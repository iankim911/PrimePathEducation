"""
Notification System Models for Student Portal
Handles email, SMS, and in-app notifications
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
import uuid
import json
from datetime import timedelta


class NotificationPreference(models.Model):
    """Student notification preferences"""
    student = models.OneToOneField(
        'StudentProfile',
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # Notification channels
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    
    # Notification types
    exam_launch = models.BooleanField(default=True, help_text="Notify when new exam is available")
    exam_reminder = models.BooleanField(default=True, help_text="Remind before exam expires")
    exam_results = models.BooleanField(default=True, help_text="Notify when results are available")
    class_updates = models.BooleanField(default=True, help_text="Updates about class activities")
    
    # Timing preferences
    reminder_hours_before = models.IntegerField(
        default=2,
        help_text="Hours before exam expiry to send reminder"
    )
    quiet_hours_start = models.TimeField(
        null=True, blank=True,
        help_text="Don't send notifications after this time"
    )
    quiet_hours_end = models.TimeField(
        null=True, blank=True,
        help_text="Resume notifications after this time"
    )
    
    # Contact preferences
    preferred_email = models.EmailField(blank=True, null=True)
    preferred_phone = models.CharField(max_length=20, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_notification_preferences'
    
    def __str__(self):
        return f"Notification preferences for {self.student.student_id}"
    
    def should_send_notification(self, notification_type, channel):
        """Check if notification should be sent based on preferences"""
        # Check channel preference
        channel_enabled = getattr(self, f"{channel}_enabled", False)
        if not channel_enabled:
            return False
        
        # Check notification type preference
        type_enabled = getattr(self, notification_type, True)
        if not type_enabled:
            return False
        
        # Check quiet hours
        if self.quiet_hours_start and self.quiet_hours_end:
            current_time = timezone.now().time()
            if self.quiet_hours_start <= current_time <= self.quiet_hours_end:
                return False
        
        return True


class Notification(models.Model):
    """Individual notification record"""
    NOTIFICATION_TYPES = [
        ('exam_launch', 'Exam Launch'),
        ('exam_reminder', 'Exam Reminder'),
        ('exam_results', 'Exam Results'),
        ('class_update', 'Class Update'),
        ('system', 'System Message'),
    ]
    
    CHANNELS = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('in_app', 'In-App'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('read', 'Read'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        'StudentProfile',
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    # Notification details
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    channel = models.CharField(max_length=10, choices=CHANNELS)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    # Content
    subject = models.CharField(max_length=200)
    message = models.TextField()
    html_message = models.TextField(blank=True, null=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    related_exam_id = models.UUIDField(null=True, blank=True)
    related_class_code = models.CharField(max_length=10, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Delivery info
    delivery_attempts = models.IntegerField(default=0)
    last_error = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'student_notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['scheduled_for']),
            models.Index(fields=['channel', 'status']),
        ]
    
    def __str__(self):
        return f"{self.notification_type} for {self.student.student_id}"
    
    def mark_as_sent(self):
        """Mark notification as sent"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save()
    
    def mark_as_read(self):
        """Mark notification as read"""
        if self.status == 'sent':
            self.status = 'read'
            self.read_at = timezone.now()
            self.save()
    
    def mark_as_failed(self, error=None):
        """Mark notification as failed"""
        self.status = 'failed'
        self.delivery_attempts += 1
        if error:
            self.last_error = str(error)
        self.save()


class NotificationTemplate(models.Model):
    """Reusable notification templates"""
    TEMPLATE_TYPES = [
        ('exam_launch', 'Exam Launch'),
        ('exam_reminder_2h', '2 Hour Exam Reminder'),
        ('exam_reminder_30m', '30 Minute Exam Reminder'),
        ('exam_completed', 'Exam Completed'),
        ('exam_results', 'Exam Results Available'),
        ('welcome', 'Welcome Message'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPES, unique=True)
    
    # Email templates
    email_subject = models.CharField(max_length=200)
    email_body = models.TextField(help_text="Plain text email body with {variables}")
    email_html_body = models.TextField(
        blank=True, null=True,
        help_text="HTML email body with {variables}"
    )
    
    # SMS template
    sms_message = models.TextField(
        max_length=160,
        help_text="SMS message with {variables}, max 160 chars"
    )
    
    # In-app notification
    in_app_title = models.CharField(max_length=100)
    in_app_message = models.TextField(max_length=500)
    
    # Template variables (for documentation)
    available_variables = models.JSONField(
        default=dict,
        help_text="Document available template variables"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_templates'
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"
    
    def render_email(self, context):
        """Render email content with context"""
        subject = self.email_subject.format(**context)
        body = self.email_body.format(**context)
        html_body = self.email_html_body.format(**context) if self.email_html_body else None
        return subject, body, html_body
    
    def render_sms(self, context):
        """Render SMS message with context"""
        return self.sms_message.format(**context)
    
    def render_in_app(self, context):
        """Render in-app notification with context"""
        title = self.in_app_title.format(**context)
        message = self.in_app_message.format(**context)
        return title, message


class NotificationQueue(models.Model):
    """Queue for batch notification processing"""
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('normal', 'Normal'),
        ('low', 'Low'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='queue_entries'
    )
    
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    scheduled_time = models.DateTimeField(default=timezone.now)
    
    # Processing info
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notification_queue'
        ordering = ['priority', 'scheduled_time']
        indexes = [
            models.Index(fields=['is_processed', 'scheduled_time']),
            models.Index(fields=['priority', 'is_processed']),
        ]
    
    def __str__(self):
        return f"Queue entry for {self.notification.id}"
    
    def can_retry(self):
        """Check if notification can be retried"""
        return self.retry_count < self.max_retries
    
    def increment_retry(self):
        """Increment retry count and reschedule"""
        self.retry_count += 1
        # Exponential backoff: 5 min, 15 min, 45 min
        delay_minutes = 5 * (3 ** (self.retry_count - 1))
        self.scheduled_time = timezone.now() + timedelta(minutes=delay_minutes)
        self.save()


class NotificationLog(models.Model):
    """Log of all notification activities"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    
    action = models.CharField(max_length=50)
    details = models.JSONField(default=dict, blank=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notification_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Log: {self.action} for {self.notification.id}"
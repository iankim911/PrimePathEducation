"""
Teacher Class Access Management Models
Part of RoutineTest module - Teacher access control system

This module provides models for managing teacher access to classes,
including assignment tracking, access requests, and audit logging.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import json
import logging
from ..class_code_mapping import CLASS_CODE_CURRICULUM_MAPPING

logger = logging.getLogger(__name__)

# Generate class code choices from the curriculum mapping
CLASS_CODE_CHOICES = [(code, code) for code, curriculum in CLASS_CODE_CURRICULUM_MAPPING.items()]


class TeacherClassAssignment(models.Model):
    """
    Tracks which classes each teacher has access to.
    This is the actual assignment that grants access.
    """
    ACCESS_LEVEL_CHOICES = [
        ('FULL', 'Full Access'),  # Can create/edit exams, grade, manage everything
        ('VIEW', 'View Only'),    # Can only view class data, no modifications
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(
        'core.Teacher',
        on_delete=models.CASCADE,
        related_name='class_assignments'
    )
    class_code = models.CharField(
        max_length=30,
        choices=CLASS_CODE_CHOICES
    )
    access_level = models.CharField(
        max_length=20,
        choices=ACCESS_LEVEL_CHOICES,
        default='FULL'
    )
    
    # Assignment metadata
    assigned_date = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assignments_made'
    )
    expires_on = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Leave blank for permanent assignment"
    )
    is_active = models.BooleanField(default=True)
    
    # Additional information
    notes = models.TextField(
        blank=True,
        help_text="Admin notes about this assignment"
    )
    
    # Link to the request that led to this assignment (if applicable)
    from_request = models.ForeignKey(
        'ClassAccessRequest',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resulting_assignment'
    )
    
    class Meta:
        unique_together = ['teacher', 'class_code', 'is_active']
        ordering = ['class_code', 'teacher__name']
        indexes = [
            models.Index(fields=['teacher', 'is_active']),
            models.Index(fields=['class_code', 'is_active']),
            models.Index(fields=['expires_on']),
        ]
    
    def __str__(self):
        return f"{self.teacher.name} - {self.get_class_code_display()} ({self.get_access_level_display()})"
    
    def is_expired(self):
        """Check if this assignment has expired"""
        if self.expires_on:
            return timezone.now() > self.expires_on
        return False
    
    def get_student_count(self):
        """Get the number of students in this class"""
        # StudentRoster removed - not needed for Answer Keys functionality
        # This feature is no longer available
        return 0  # Return 0 as roster functionality has been removed
    
    def save(self, *args, **kwargs):
        """Override save to log assignment changes"""
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        # Log the assignment
        action = "created" if is_new else "updated"
        console_log = {
            "model": "TeacherClassAssignment",
            "action": action,
            "assignment_id": str(self.id),
            "teacher": self.teacher.name,
            "class_code": self.class_code,
            "access_level": self.access_level,
            "assigned_by": self.assigned_by.username if self.assigned_by else "System",
            "expires_on": self.expires_on.isoformat() if self.expires_on else None,
            "is_active": self.is_active
        }
        logger.info(f"[CLASS_ASSIGNMENT] {json.dumps(console_log)}")
        print(f"[CLASS_ASSIGNMENT] {json.dumps(console_log)}")


class ClassAccessRequest(models.Model):
    """
    Tracks teacher requests for access to classes.
    These are requests that need admin approval.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('DENIED', 'Denied'),
        ('WITHDRAWN', 'Withdrawn'),
        ('MORE_INFO', 'More Information Needed'),
    ]
    
    REQUEST_TYPE_CHOICES = [
        ('PERMANENT', 'Permanent Assignment'),
        ('TEMPORARY', 'Temporary Coverage'),
        ('SUBSTITUTE', 'Substitute Teacher'),
        ('CO_TEACHING', 'Co-Teaching Arrangement'),
    ]
    
    REASON_CHOICES = [
        ('NEW_ASSIGNMENT', 'New class assignment'),
        ('SUBSTITUTE', 'Substituting for another teacher'),
        ('CO_TEACHING', 'Co-teaching arrangement'),
        ('CURRICULUM_EXPERTISE', 'Have expertise in curriculum'),
        ('SCHEDULE_OPTIMIZATION', 'Better schedule alignment'),
        ('TEACHER_ABSENCE', 'Covering for absent teacher'),
        ('OTHER', 'Other reason'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(
        'core.Teacher',
        on_delete=models.CASCADE,
        related_name='access_requests'
    )
    class_code = models.CharField(
        max_length=30,
        choices=CLASS_CODE_CHOICES
    )
    
    # Request details
    request_type = models.CharField(
        max_length=20,
        choices=REQUEST_TYPE_CHOICES,
        default='PERMANENT'
    )
    reason_code = models.CharField(
        max_length=30,
        choices=REASON_CHOICES,
        default='NEW_ASSIGNMENT'
    )
    reason_text = models.TextField(
        help_text="Detailed explanation for the request"
    )
    
    # Duration for temporary requests
    duration_start = models.DateField(
        null=True,
        blank=True,
        help_text="Start date for temporary access"
    )
    duration_end = models.DateField(
        null=True,
        blank=True,
        help_text="End date for temporary access"
    )
    
    # Request status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    # Timestamps
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Review information
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requests_reviewed'
    )
    admin_notes = models.TextField(
        blank=True,
        help_text="Admin notes/reason for approval or denial"
    )
    
    # Requested access level
    requested_access_level = models.CharField(
        max_length=20,
        choices=TeacherClassAssignment.ACCESS_LEVEL_CHOICES,
        default='FULL'
    )
    
    class Meta:
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['teacher', 'status']),
            models.Index(fields=['status', 'requested_at']),
            models.Index(fields=['class_code', 'status']),
        ]
    
    def __str__(self):
        return f"{self.teacher.name} requesting {self.get_class_code_display()} - {self.get_status_display()}"
    
    def approve(self, user, notes=''):
        """Approve this request and create the assignment"""
        self.status = 'APPROVED'
        self.reviewed_at = timezone.now()
        self.reviewed_by = user
        if notes:
            self.admin_notes = notes
        self.save()
        
        # Create the actual assignment
        assignment = TeacherClassAssignment.objects.create(
            teacher=self.teacher,
            class_code=self.class_code,
            access_level=self.requested_access_level,
            assigned_by=user,
            expires_on=self.duration_end if self.request_type == 'TEMPORARY' else None,
            notes=f"Approved from request: {self.reason_text}",
            from_request=self
        )
        
        # Log the approval
        console_log = {
            "model": "ClassAccessRequest",
            "action": "approved",
            "request_id": str(self.id),
            "teacher": self.teacher.name,
            "class_code": self.class_code,
            "approved_by": user.username,
            "assignment_id": str(assignment.id)
        }
        logger.info(f"[ACCESS_REQUEST_APPROVED] {json.dumps(console_log)}")
        print(f"[ACCESS_REQUEST_APPROVED] {json.dumps(console_log)}")
        
        return assignment
    
    def deny(self, user, reason):
        """Deny this request"""
        self.status = 'DENIED'
        self.reviewed_at = timezone.now()
        self.reviewed_by = user
        self.admin_notes = reason
        self.save()
        
        # Log the denial
        console_log = {
            "model": "ClassAccessRequest",
            "action": "denied",
            "request_id": str(self.id),
            "teacher": self.teacher.name,
            "class_code": self.class_code,
            "denied_by": user.username,
            "reason": reason
        }
        logger.info(f"[ACCESS_REQUEST_DENIED] {json.dumps(console_log)}")
        print(f"[ACCESS_REQUEST_DENIED] {json.dumps(console_log)}")
    
    def withdraw(self):
        """Teacher withdraws their own request"""
        self.status = 'WITHDRAWN'
        self.save()
        
        # Log the withdrawal
        console_log = {
            "model": "ClassAccessRequest",
            "action": "withdrawn",
            "request_id": str(self.id),
            "teacher": self.teacher.name,
            "class_code": self.class_code
        }
        logger.info(f"[ACCESS_REQUEST_WITHDRAWN] {json.dumps(console_log)}")
        print(f"[ACCESS_REQUEST_WITHDRAWN] {json.dumps(console_log)}")
    
    def get_current_teachers(self):
        """Get list of teachers currently assigned to this class"""
        return TeacherClassAssignment.objects.filter(
            class_code=self.class_code,
            is_active=True
        ).select_related('teacher')
    
    def save(self, *args, **kwargs):
        """Override save to log request creation/updates"""
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        if is_new:
            # Log new request
            console_log = {
                "model": "ClassAccessRequest",
                "action": "created",
                "request_id": str(self.id),
                "teacher": self.teacher.name,
                "class_code": self.class_code,
                "request_type": self.request_type,
                "reason": self.reason_code
            }
            logger.info(f"[ACCESS_REQUEST_CREATED] {json.dumps(console_log)}")
            print(f"[ACCESS_REQUEST_CREATED] {json.dumps(console_log)}")


class AccessAuditLog(models.Model):
    """
    Immutable audit log for all access-related actions.
    This provides a complete history of who did what and when.
    """
    ACTION_CHOICES = [
        ('REQUEST_CREATED', 'Access Request Created'),
        ('REQUEST_APPROVED', 'Request Approved'),
        ('REQUEST_DENIED', 'Request Denied'),
        ('REQUEST_WITHDRAWN', 'Request Withdrawn'),
        ('ASSIGNMENT_CREATED', 'Direct Assignment Created'),
        ('ASSIGNMENT_MODIFIED', 'Assignment Modified'),
        ('ASSIGNMENT_REVOKED', 'Assignment Revoked'),
        ('ASSIGNMENT_EXPIRED', 'Assignment Expired'),
        ('BULK_APPROVAL', 'Bulk Approval'),
        ('BULK_DENIAL', 'Bulk Denial'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # What happened
    action = models.CharField(
        max_length=30,
        choices=ACTION_CHOICES
    )
    
    # Who was affected
    teacher = models.ForeignKey(
        'core.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        related_name='access_audit_logs'
    )
    class_code = models.CharField(max_length=20)
    
    # Who did it
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='access_actions_performed'
    )
    
    # Additional context
    details = models.JSONField(
        default=dict,
        help_text="Additional details about the action"
    )
    
    # Related objects (optional)
    related_request = models.ForeignKey(
        ClassAccessRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    related_assignment = models.ForeignKey(
        TeacherClassAssignment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['teacher', 'timestamp']),
            models.Index(fields=['class_code', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.timestamp}: {self.get_action_display()} - {self.teacher.name if self.teacher else 'Unknown'}"
    
    @classmethod
    def log_action(cls, action, teacher, class_code, user, details=None, request=None, assignment=None):
        """Helper method to create audit log entries"""
        log_entry = cls.objects.create(
            action=action,
            teacher=teacher,
            class_code=class_code,
            performed_by=user,
            details=details or {},
            related_request=request,
            related_assignment=assignment
        )
        
        # Also log to console for debugging
        console_log = {
            "model": "AccessAuditLog",
            "action": action,
            "teacher": teacher.name if teacher else None,
            "class_code": class_code,
            "performed_by": user.username if user else "System",
            "timestamp": log_entry.timestamp.isoformat(),
            "details": details
        }
        logger.info(f"[ACCESS_AUDIT] {json.dumps(console_log)}")
        print(f"[ACCESS_AUDIT] {json.dumps(console_log)}")
        
        return log_entry
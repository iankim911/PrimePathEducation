from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from primepath_routinetest.models.class_constants import CLASS_CODE_CHOICES
from core.models import Teacher
import random
import string


class StudentProfile(models.Model):
    """Student profile extending Django User model"""
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
    kakao_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
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
        return self.class_assignments.filter(is_active=True).select_related('class_code')
    
    @property
    def all_classes(self):
        """Get all class assignments (active and inactive) for this student"""
        return self.class_assignments.all().select_related('class_code').order_by('-is_active', '-assigned_at')


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

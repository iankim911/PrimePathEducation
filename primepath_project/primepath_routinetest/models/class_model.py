"""
BUILDER: Day 2 & 3 - Class Model and Student Enrollment for RoutineTest
Represents a class that teachers can be assigned to and students can enroll in
"""
from django.db import models
from django.contrib.auth.models import User
from core.models import Teacher, Student
import uuid

class Class(models.Model):
    """A class in the RoutineTest system"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    grade_level = models.CharField(max_length=50)
    section = models.CharField(max_length=50, blank=True)
    academic_year = models.CharField(max_length=20, default='2024-2025')
    
    # Program assignment field (Direct mapping to CORE, ASCENT, EDGE, PINNACLE)
    program = models.CharField(
        max_length=20,
        choices=[
            ('CORE', 'CORE'),
            ('ASCENT', 'ASCENT'),
            ('EDGE', 'EDGE'),
            ('PINNACLE', 'PINNACLE')
        ],
        blank=True,
        null=True,
        db_index=True,
        help_text="Program this class belongs to"
    )
    
    # SubProgram field for more specific curriculum mapping
    subprogram = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Specific subprogram within the program"
    )
    
    # Teacher assignment (ManyToMany doesn't cascade delete by default)
    assigned_teachers = models.ManyToManyField(
        Teacher,
        related_name='routinetest_classes',
        blank=True,
        help_text="Teachers assigned to this class"
    )
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_routinetest_classes'
    )
    
    class Meta:
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'
        ordering = ['grade_level', 'section', 'name']
        db_table = 'routinetest_class'
        unique_together = [['name', 'grade_level', 'section', 'academic_year']]
        indexes = [
            models.Index(fields=['is_active', 'academic_year']),
            models.Index(fields=['grade_level', 'section']),
            models.Index(fields=['program', 'is_active']),  # New index for program queries
        ]
    
    def __str__(self):
        if self.section:
            return f"{self.grade_level} - {self.section} ({self.name})"
        return f"{self.grade_level} - {self.name}"
    
    @property
    def student_count(self):
        """Get count of students in this class"""
        return self.enrollments.filter(status='active').count()
    
    @property
    def teacher_names(self):
        """Get comma-separated list of teacher names"""
        return ', '.join([t.name for t in self.assigned_teachers.all()])


class StudentEnrollment(models.Model):
    """Represents a student's enrollment in a class with enhanced tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Core relationships
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    class_assigned = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    
    # Enrollment details
    enrollment_date = models.DateTimeField(auto_now_add=True)
    academic_year = models.CharField(max_length=20, default='2024-2025')
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('transferred', 'Transferred'),
            ('graduated', 'Graduated')
        ],
        default='active'
    )
    
    # Audit fields
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_enrollments'
    )
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['student', 'class_assigned', 'academic_year']]
        indexes = [
            models.Index(fields=['class_assigned', 'status']),
            models.Index(fields=['student', 'academic_year']),
        ]
        db_table = 'routinetest_student_enrollment'
        ordering = ['-enrollment_date']
    
    def __str__(self):
        return f"{self.student.name} - {self.class_assigned.name} ({self.academic_year})"
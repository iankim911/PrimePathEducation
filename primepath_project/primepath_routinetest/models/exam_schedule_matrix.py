"""
Exam Schedule Matrix Model
Manages the Class × Timeslot matrix for exam assignments
Supports both monthly (Review) and quarterly exam scheduling
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.auth.models import User
import uuid
import json
import logging

logger = logging.getLogger(__name__)


class ExamScheduleMatrix(models.Model):
    """
    Represents an exam assignment in the Class × Timeslot matrix.
    Each record represents one or more exams assigned to a specific class-timeslot combination.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Class and timeslot identification
    class_code = models.CharField(
        max_length=20,
        help_text="The class this schedule applies to"
    )
    
    # Academic year
    academic_year = models.CharField(
        max_length=4,
        help_text="Academic year (e.g., 2025)"
    )
    
    # Timeslot - either month or quarter
    time_period_type = models.CharField(
        max_length=10,
        choices=[
            ('MONTHLY', 'Monthly/Review'),
            ('QUARTERLY', 'Quarterly'),
        ]
    )
    
    time_period_value = models.CharField(
        max_length=3,
        help_text="Month code (JAN-DEC) or Quarter code (Q1-Q4)"
    )
    
    # Multiple exams can be assigned to one matrix cell
    exams = models.ManyToManyField(
        'primepath_routinetest.RoutineExam',
        related_name='matrix_schedules',
        blank=True
    )
    
    # Scheduling details
    scheduled_date = models.DateField(
        null=True,
        blank=True,
        help_text="Primary scheduled date for exams in this cell"
    )
    
    scheduled_start_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Default start time for exams"
    )
    
    scheduled_end_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Default end time for exams"
    )
    
    # Status and configuration
    status = models.CharField(
        max_length=20,
        choices=[
            ('EMPTY', 'No Exams'),
            ('SCHEDULED', 'Exams Scheduled'),
            ('IN_PROGRESS', 'Currently Running'),
            ('COMPLETED', 'Completed'),
            ('DRAFT', 'Draft/Planning'),
        ],
        default='EMPTY'
    )
    
    # Visual indicators for the matrix
    color_code = models.CharField(
        max_length=7,
        default='#FFFFFF',
        help_text="Hex color code for visual display"
    )
    
    icon = models.CharField(
        max_length=20,
        blank=True,
        help_text="Icon identifier for status display"
    )
    
    # Assignment tracking
    created_by = models.ForeignKey(
        'core.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        related_name='matrix_schedules_created'
    )
    
    modified_by = models.ForeignKey(
        'core.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        related_name='matrix_schedules_modified'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Sharing configuration
    shared_with_classes = models.JSONField(
        default=list,
        blank=True,
        help_text="List of other class codes this schedule is shared with"
    )
    
    is_template = models.BooleanField(
        default=False,
        help_text="If true, this can be used as a template for other classes"
    )
    
    # Notes and metadata
    notes = models.TextField(
        blank=True,
        help_text="Administrative notes about this schedule"
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata for this matrix cell"
    )
    
    class Meta:
        ordering = ['class_code', 'academic_year', 'time_period_type', 'time_period_value']
        unique_together = ['class_code', 'academic_year', 'time_period_type', 'time_period_value']
        indexes = [
            models.Index(fields=['class_code', 'academic_year']),
            models.Index(fields=['time_period_type', 'time_period_value']),
            models.Index(fields=['status']),
            models.Index(fields=['created_by']),
        ]
    
    def __str__(self):
        return f"{self.get_class_display()} - {self.get_time_period_display()} ({self.academic_year})"
    
    def get_class_display(self):
        """Get display name for the class code"""
        from .class_constants import CLASS_CODE_CHOICES
        class_dict = dict(CLASS_CODE_CHOICES)
        return class_dict.get(self.class_code, self.class_code)
    
    def get_time_period_display(self):
        """Get formatted time period display"""
        if self.time_period_type == 'MONTHLY':
            from .exam_management import RoutineExam
            month_dict = dict(RoutineExam.MONTHS)
            return month_dict.get(self.time_period_value, self.time_period_value)
        else:  # QUARTERLY
            from .exam_management import RoutineExam
            quarter_dict = dict(RoutineExam.QUARTERS)
            return quarter_dict.get(self.time_period_value, self.time_period_value)
    
    def get_exam_count(self):
        """Get the number of exams assigned to this cell"""
        return self.exams.count()
    
    def get_exam_list(self):
        """Get list of exams with their details"""
        exam_list = []
        for exam in self.exams.all():
            exam_list.append({
                'id': str(exam.id),
                'name': exam.name,
                'type': exam.get_exam_type_display_short(),
                'curriculum': exam.curriculum_level.full_name if exam.curriculum_level else 'N/A',
                'questions': exam.total_questions,
                'timer': exam.timer_minutes,
                'status': exam.get_answer_mapping_status()
            })
        return exam_list
    
    def get_detailed_exam_list(self):
        """Get comprehensive exam details for modular exam card display"""
        detailed_exams = []
        for exam in self.exams.prefetch_related('routine_questions', 'routine_audio_files').all():
            # Get answer mapping status
            answer_status = exam.get_answer_mapping_status()
            
            # Calculate completion percentage
            total_questions = exam.total_questions
            mapped_questions = exam.routine_questions.filter(correct_answer__isnull=False).count()
            mapping_percentage = round((mapped_questions / total_questions * 100), 1) if total_questions > 0 else 0.0
            
            # Get audio file count
            audio_count = exam.routine_audio_files.count()
            
            # Determine status color and label
            if mapping_percentage >= 100:
                status_color = 'success'
                status_label = 'All mapped'
                status_icon = '✓'
            elif mapping_percentage >= 50:
                status_color = 'warning'
                status_label = 'Partially mapped'
                status_icon = '⚠'
            else:
                status_color = 'danger'
                status_label = 'Not mapped'
                status_icon = '✗'
            
            detailed_exam = {
                'id': str(exam.id),
                'name': exam.name,
                'exam_type': exam.exam_type,
                'exam_type_display': exam.get_exam_type_display(),
                'exam_type_short': exam.get_exam_type_display_short(),
                
                # Curriculum information
                'curriculum': {
                    'level': exam.curriculum_level.full_name if exam.curriculum_level else None,
                    'program': exam.curriculum_level.subprogram.program.name if exam.curriculum_level and exam.curriculum_level.subprogram and exam.curriculum_level.subprogram.program else None,
                    'subprogram': exam.curriculum_level.subprogram.name if exam.curriculum_level and exam.curriculum_level.subprogram else None,
                    'level_number': exam.curriculum_level.level_number if exam.curriculum_level else None,
                },
                
                # Question and content details
                'questions': {
                    'total': total_questions,
                    'mapped': mapped_questions,
                    'unmapped': total_questions - mapped_questions
                },
                
                # Timing information
                'timer': {
                    'minutes': exam.timer_minutes,
                    'display': f"{exam.timer_minutes} minutes" if exam.timer_minutes else "No timer"
                },
                
                # Audio files
                'audio': {
                    'count': audio_count,
                    'display': f"{audio_count} file{'s' if audio_count != 1 else ''}" if audio_count > 0 else "No audio"
                },
                
                # Answer mapping status
                'answer_status': {
                    'percentage': mapping_percentage,
                    'color': status_color,
                    'label': status_label,
                    'icon': status_icon,
                    'complete': mapping_percentage >= 100
                },
                
                # Activity status
                'is_active': exam.is_active,
                'activity_status': 'Active' if exam.is_active else 'Inactive',
                'activity_color': 'success' if exam.is_active else 'secondary',
                
                # Metadata
                'created_at': exam.created_at.isoformat() if exam.created_at else None,
                'updated_at': exam.updated_at.isoformat() if exam.updated_at else None,
                
                # Actions available
                'actions': {
                    'can_manage': True,  # Based on permissions
                    'can_update_name': True,
                    'can_delete': True,
                    'can_preview': True
                }
            }
            
            detailed_exams.append(detailed_exam)
        
        # Sort by exam name for consistent display
        detailed_exams.sort(key=lambda x: x['name'])
        
        return detailed_exams
    
    def add_exam(self, exam, user=None):
        """Add an exam to this matrix cell"""
        self.exams.add(exam)
        
        # Update status if needed
        if self.status == 'EMPTY':
            self.status = 'SCHEDULED'
            self.save()
        
        # Log the action
        console_log = {
            "model": "ExamScheduleMatrix",
            "action": "add_exam",
            "matrix_id": str(self.id),
            "exam_id": str(exam.id),
            "exam_name": exam.name,
            "class_code": self.class_code,
            "time_period": f"{self.time_period_type}:{self.time_period_value}",
            "user": user.username if user else "System"
        }
        logger.info(f"[MATRIX_ADD_EXAM] {json.dumps(console_log)}")
        print(f"[MATRIX_ADD_EXAM] {json.dumps(console_log)}")
        
        return True
    
    def remove_exam(self, exam, user=None):
        """Remove an exam from this matrix cell"""
        self.exams.remove(exam)
        
        # Update status if no exams left
        if self.get_exam_count() == 0:
            self.status = 'EMPTY'
            self.save()
        
        # Log the action
        console_log = {
            "model": "ExamScheduleMatrix",
            "action": "remove_exam",
            "matrix_id": str(self.id),
            "exam_id": str(exam.id),
            "exam_name": exam.name,
            "class_code": self.class_code,
            "time_period": f"{self.time_period_type}:{self.time_period_value}",
            "user": user.username if user else "System"
        }
        logger.info(f"[MATRIX_REMOVE_EXAM] {json.dumps(console_log)}")
        print(f"[MATRIX_REMOVE_EXAM] {json.dumps(console_log)}")
        
        return True
    
    def share_with_class(self, target_class_code, user=None):
        """Share this schedule with another class"""
        if target_class_code not in self.shared_with_classes:
            self.shared_with_classes.append(target_class_code)
            self.save()
            
            # Create a copy for the target class
            target_matrix, created = ExamScheduleMatrix.objects.get_or_create(
                class_code=target_class_code,
                academic_year=self.academic_year,
                time_period_type=self.time_period_type,
                time_period_value=self.time_period_value,
                defaults={
                    'status': self.status,
                    'scheduled_date': self.scheduled_date,
                    'scheduled_start_time': self.scheduled_start_time,
                    'scheduled_end_time': self.scheduled_end_time,
                    'created_by': user if hasattr(user, 'teacher') else None,
                    'notes': f"Shared from {self.get_class_display()}"
                }
            )
            
            # Copy exams to target
            for exam in self.exams.all():
                target_matrix.exams.add(exam)
            
            # Log the sharing
            console_log = {
                "model": "ExamScheduleMatrix",
                "action": "share_schedule",
                "source_class": self.class_code,
                "target_class": target_class_code,
                "time_period": f"{self.time_period_type}:{self.time_period_value}",
                "exam_count": self.get_exam_count(),
                "user": user.username if user else "System"
            }
            logger.info(f"[MATRIX_SHARE] {json.dumps(console_log)}")
            print(f"[MATRIX_SHARE] {json.dumps(console_log)}")
            
            return target_matrix
        
        return None
    
    def update_schedule(self, date=None, start_time=None, end_time=None, user=None):
        """Update the scheduling details for this matrix cell"""
        changes = {}
        
        if date:
            self.scheduled_date = date
            changes['date'] = str(date)
        
        if start_time:
            self.scheduled_start_time = start_time
            changes['start_time'] = str(start_time)
        
        if end_time:
            self.scheduled_end_time = end_time
            changes['end_time'] = str(end_time)
        
        if changes:
            self.modified_by = user if hasattr(user, 'teacher') else None
            self.save()
            
            # Log the update
            console_log = {
                "model": "ExamScheduleMatrix",
                "action": "update_schedule",
                "matrix_id": str(self.id),
                "class_code": self.class_code,
                "time_period": f"{self.time_period_type}:{self.time_period_value}",
                "changes": changes,
                "user": user.username if user else "System"
            }
            logger.info(f"[MATRIX_UPDATE_SCHEDULE] {json.dumps(console_log)}")
            print(f"[MATRIX_UPDATE_SCHEDULE] {json.dumps(console_log)}")
        
        return True
    
    def get_status_color(self):
        """Get the appropriate color for the current status"""
        status_colors = {
            'EMPTY': '#F5F5F5',
            'SCHEDULED': '#E3F2FD',
            'IN_PROGRESS': '#FFF3E0',
            'COMPLETED': '#E8F5E9',
            'DRAFT': '#F3E5F5',
        }
        return status_colors.get(self.status, '#FFFFFF')
    
    def get_status_icon(self):
        """Get the appropriate icon for the current status"""
        status_icons = {
            'EMPTY': '⬜',
            'SCHEDULED': '📅',
            'IN_PROGRESS': '⏳',
            'COMPLETED': '✅',
            'DRAFT': '📝',
        }
        return status_icons.get(self.status, '❓')
    
    def can_teacher_edit(self, teacher):
        """Check if a teacher can edit this matrix cell"""
        from .class_access import TeacherClassAssignment
        
        # Check if teacher has access to this class
        has_access = TeacherClassAssignment.objects.filter(
            teacher=teacher,
            class_code=self.class_code,
            is_active=True,
            access_level__in=['FULL', 'CO_TEACHER']
        ).exists()
        
        return has_access
    
    def get_completion_stats(self):
        """Get completion statistics for exams in this cell"""
        from primepath_routinetest.models import StudentSession
        
        stats = {
            'total_exams': self.get_exam_count(),
            'total_students': 0,
            'completed': 0,
            'in_progress': 0,
            'not_started': 0,
            'completion_rate': 0
        }
        
        if stats['total_exams'] == 0:
            return stats
        
        # Calculate stats across all exams
        for exam in self.exams.all():
            sessions = StudentSession.objects.filter(
                exam=exam
            )
            
            total = sessions.count()
            completed = sessions.filter(completed_at__isnull=False).count()
            in_progress = sessions.filter(
                completed_at__isnull=True,
                started_at__isnull=False
            ).count()
            
            stats['total_students'] += total
            stats['completed'] += completed
            stats['in_progress'] += in_progress
        
        stats['not_started'] = stats['total_students'] - stats['completed'] - stats['in_progress']
        
        if stats['total_students'] > 0:
            stats['completion_rate'] = round(
                (stats['completed'] / stats['total_students']) * 100, 1
            )
        
        return stats
    
    @classmethod
    def get_matrix_for_class(cls, class_code, academic_year, time_period_type='MONTHLY'):
        """Get all matrix cells for a class and year"""
        return cls.objects.filter(
            class_code=class_code,
            academic_year=academic_year,
            time_period_type=time_period_type
        ).prefetch_related('exams').order_by('time_period_value')
    
    @classmethod
    def get_or_create_cell(cls, class_code, academic_year, time_period_type, time_period_value, user=None):
        """Get or create a matrix cell"""
        matrix_cell, created = cls.objects.get_or_create(
            class_code=class_code,
            academic_year=academic_year,
            time_period_type=time_period_type,
            time_period_value=time_period_value,
            defaults={
                'status': 'EMPTY',
                'created_by': user if hasattr(user, 'teacher') else None
            }
        )
        
        if created:
            console_log = {
                "model": "ExamScheduleMatrix",
                "action": "create_cell",
                "class_code": class_code,
                "academic_year": academic_year,
                "time_period": f"{time_period_type}:{time_period_value}",
                "user": user.username if user else "System"
            }
            logger.info(f"[MATRIX_CREATE_CELL] {json.dumps(console_log)}")
            print(f"[MATRIX_CREATE_CELL] {json.dumps(console_log)}")
        
        return matrix_cell, created
    
    def save(self, *args, **kwargs):
        """Override save to update color and icon based on status"""
        self.color_code = self.get_status_color()
        self.icon = self.get_status_icon()
        super().save(*args, **kwargs)
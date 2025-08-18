"""
Class Curriculum Mapping Model
Maps class codes to curriculum levels (Program × SubProgram × Level)
Admin-only feature for direct curriculum assignment instead of inference
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.models import CurriculumLevel
import uuid
import json
import logging

logger = logging.getLogger(__name__)


class ClassCurriculumMapping(models.Model):
    """
    Maps a class code to curriculum levels
    One-to-many relationship: One class can have multiple curriculum levels
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Class information
    class_code = models.CharField(
        max_length=10,
        db_index=True,
        help_text="Class code (e.g., 8A, 9B, 10C)"
    )
    
    # Curriculum mapping
    curriculum_level = models.ForeignKey(
        CurriculumLevel,
        on_delete=models.CASCADE,
        related_name='class_mappings',
        help_text="The curriculum level assigned to this class"
    )
    
    # Academic year for historical tracking
    academic_year = models.CharField(
        max_length=4,
        db_index=True,
        help_text="Academic year (e.g., 2025)"
    )
    
    # Priority for ordering when multiple curricula per class
    priority = models.IntegerField(
        default=1,
        help_text="Priority order when class has multiple curricula (1 = primary)"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this mapping is currently active"
    )
    
    # Metadata
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='curriculum_mappings_created'
    )
    modified_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='curriculum_mappings_modified'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optional notes
    notes = models.TextField(
        blank=True,
        help_text="Optional notes about this mapping"
    )
    
    class Meta:
        unique_together = [
            ['class_code', 'curriculum_level', 'academic_year']
        ]
        ordering = ['class_code', 'priority', '-created_at']
        indexes = [
            models.Index(fields=['class_code', 'academic_year', 'is_active']),
            models.Index(fields=['curriculum_level', 'academic_year']),
        ]
        verbose_name = "Class Curriculum Mapping"
        verbose_name_plural = "Class Curriculum Mappings"
    
    def __str__(self):
        return f"{self.class_code} → {self.curriculum_level.display_name} ({self.academic_year})"
    
    def clean(self):
        """Validate the mapping"""
        # Ensure class code is uppercase
        if self.class_code:
            self.class_code = self.class_code.upper().strip()
        
        # Validate priority uniqueness for same class and year
        if self.priority:
            existing = ClassCurriculumMapping.objects.filter(
                class_code=self.class_code,
                academic_year=self.academic_year,
                priority=self.priority,
                is_active=True
            ).exclude(pk=self.pk)
            
            if existing.exists():
                raise ValidationError(
                    f"Priority {self.priority} already assigned to another curriculum for {self.class_code}"
                )
    
    def save(self, *args, **kwargs):
        """Override save to add logging"""
        self.clean()
        
        is_new = self.pk is None
        action = "created" if is_new else "updated"
        
        # Log the action
        console_log = {
            "model": "ClassCurriculumMapping",
            "action": action,
            "mapping_id": str(self.id),
            "class_code": self.class_code,
            "curriculum": str(self.curriculum_level),
            "academic_year": self.academic_year,
            "priority": self.priority,
            "is_active": self.is_active,
            "user": str(self.modified_by or self.created_by) if not is_new else str(self.created_by)
        }
        logger.info(f"[CURRICULUM_MAPPING] {json.dumps(console_log)}")
        print(f"[CURRICULUM_MAPPING] {json.dumps(console_log)}")
        
        super().save(*args, **kwargs)
    
    @classmethod
    def get_curricula_for_class(cls, class_code, academic_year=None):
        """
        Get all active curriculum mappings for a class
        Returns them ordered by priority
        """
        if not academic_year:
            academic_year = str(timezone.now().year)
        
        mappings = cls.objects.filter(
            class_code=class_code.upper(),
            academic_year=academic_year,
            is_active=True
        ).select_related(
            'curriculum_level__subprogram__program'
        ).order_by('priority')
        
        console_log = {
            "method": "get_curricula_for_class",
            "class_code": class_code,
            "academic_year": academic_year,
            "found_count": mappings.count()
        }
        logger.info(f"[CURRICULUM_LOOKUP] {json.dumps(console_log)}")
        
        return mappings
    
    @classmethod
    def get_primary_curriculum(cls, class_code, academic_year=None):
        """
        Get the primary (priority=1) curriculum for a class
        Returns None if no mapping exists
        """
        if not academic_year:
            academic_year = str(timezone.now().year)
        
        mapping = cls.objects.filter(
            class_code=class_code.upper(),
            academic_year=academic_year,
            priority=1,
            is_active=True
        ).select_related(
            'curriculum_level__subprogram__program'
        ).first()
        
        return mapping.curriculum_level if mapping else None
    
    @classmethod
    def bulk_create_mappings(cls, mappings_data, user):
        """
        Bulk create multiple mappings
        mappings_data: List of dicts with class_code, curriculum_level_id, academic_year
        """
        mappings_to_create = []
        
        for data in mappings_data:
            mapping = cls(
                class_code=data['class_code'].upper(),
                curriculum_level_id=data['curriculum_level_id'],
                academic_year=data.get('academic_year', str(timezone.now().year)),
                priority=data.get('priority', 1),
                created_by=user,
                modified_by=user
            )
            mappings_to_create.append(mapping)
        
        created = cls.objects.bulk_create(mappings_to_create, ignore_conflicts=True)
        
        console_log = {
            "method": "bulk_create_mappings",
            "created_count": len(created),
            "user": str(user)
        }
        logger.info(f"[CURRICULUM_BULK_CREATE] {json.dumps(console_log)}")
        
        return created
    
    def get_display_info(self):
        """Get formatted display information"""
        return {
            'class_code': self.class_code,
            'curriculum': {
                'program': self.curriculum_level.subprogram.program.name,
                'subprogram': self.curriculum_level.subprogram.name,
                'level': self.curriculum_level.level_number,
                'display': self.curriculum_level.display_name
            },
            'academic_year': self.academic_year,
            'priority': self.priority,
            'is_active': self.is_active,
            'notes': self.notes
        }
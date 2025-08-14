"""
Placement-related models: PlacementRule, ExamLevelMapping
Part of Phase 9: Model Modularization
"""
from django.db import models


class PlacementRule(models.Model):
    """Rules for placing students into curriculum levels based on performance"""
    grade = models.IntegerField()
    min_rank_percentile = models.IntegerField(help_text="Minimum percentile (0-100)")
    max_rank_percentile = models.IntegerField(help_text="Maximum percentile (0-100)")
    curriculum_level = models.ForeignKey(
        'core.CurriculumLevel', 
        on_delete=models.CASCADE
    )
    priority = models.IntegerField(default=1, help_text="Lower number = higher priority")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey('core.Teacher', on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['priority', 'grade', 'min_rank_percentile']

    def __str__(self):
        return f"Grade {self.grade}, Top {self.max_rank_percentile}% → {self.curriculum_level.full_name}"


class ExamLevelMapping(models.Model):
    """Maps exams to curriculum levels with slot positions"""
    curriculum_level = models.ForeignKey(
        'core.CurriculumLevel', 
        on_delete=models.CASCADE, 
        related_name='exam_mappings'
    )
    exam = models.ForeignKey(
        'placement_test.Exam', 
        on_delete=models.CASCADE, 
        related_name='level_mappings'
    )
    slot = models.IntegerField(default=1, help_text="Slot position (1-5)")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def clean(self):
        """Validate that exam is not already mapped to another level"""
        from django.core.exceptions import ValidationError
        
        # Check if this exam is already mapped to another curriculum level
        existing = ExamLevelMapping.objects.filter(exam=self.exam).exclude(pk=self.pk).first()
        if existing:
            raise ValidationError(
                f'This exam "{self.exam.name}" is already mapped to '
                f'"{existing.curriculum_level.full_name}". '
                f'Each exam can only be mapped to one curriculum level.'
            )
    
    def save(self, *args, **kwargs):
        """Override save to validate before saving"""
        self.clean()
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['curriculum_level', 'slot']
        unique_together = [
            ('curriculum_level', 'exam'),  # Same exam can't be mapped twice to same level
            ('curriculum_level', 'slot'),  # Each slot can only have one exam
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['exam'],
                name='unique_exam_per_mapping',
                condition=None
            )
        ]
    
    def __str__(self):
        return f"{self.curriculum_level} - Slot {self.slot}: {self.exam.name}"
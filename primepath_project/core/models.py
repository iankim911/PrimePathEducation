from django.db import models
from django.contrib.auth.models import AbstractUser


class School(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name


class Teacher(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    is_head_teacher = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({'Head' if self.is_head_teacher else 'Teacher'})"


class Program(models.Model):
    PROGRAM_TYPES = [
        ('CORE', 'PRIME CORE'),
        ('ASCENT', 'PRIME ASCENT'),
        ('EDGE', 'PRIME EDGE'),
        ('PINNACLE', 'PRIME PINNACLE'),
    ]
    
    name = models.CharField(max_length=50, choices=PROGRAM_TYPES, unique=True)
    grade_range_start = models.IntegerField()
    grade_range_end = models.IntegerField()
    order = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.get_name_display()} (Grades {self.grade_range_start}-{self.grade_range_end})"


class SubProgram(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='subprograms')
    name = models.CharField(max_length=100)
    order = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ['order']
        unique_together = ['program', 'name']

    def __str__(self):
        return f"{self.program.get_name_display()} - {self.name}"


class CurriculumLevel(models.Model):
    subprogram = models.ForeignKey(SubProgram, on_delete=models.CASCADE, related_name='levels')
    level_number = models.IntegerField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ['subprogram__program__order', 'subprogram__order', 'level_number']
        unique_together = ['subprogram', 'level_number']

    def __str__(self):
        return f"{self.subprogram} - Level {self.level_number}"

    @property
    def full_name(self):
        program_name = self.subprogram.program.get_name_display()
        subprogram_name = self.subprogram.name
        
        # Check if subprogram name already contains the program name
        if subprogram_name.startswith(self.subprogram.program.name):
            # If it does, just use PRIME + subprogram name
            return f"PRIME {subprogram_name} - Level {self.level_number}"
        else:
            # Otherwise, use the full format
            return f"{program_name} {subprogram_name} - Level {self.level_number}"


class PlacementRule(models.Model):
    grade = models.IntegerField()
    min_rank_percentile = models.IntegerField(help_text="Minimum percentile (0-100)")
    max_rank_percentile = models.IntegerField(help_text="Maximum percentile (0-100)")
    curriculum_level = models.ForeignKey(CurriculumLevel, on_delete=models.CASCADE)
    priority = models.IntegerField(default=1, help_text="Lower number = higher priority")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['priority', 'grade', 'min_rank_percentile']

    def __str__(self):
        return f"Grade {self.grade}, Top {self.max_rank_percentile}% → {self.curriculum_level.full_name}"
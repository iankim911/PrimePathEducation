"""
Curriculum-related models: Program, SubProgram, CurriculumLevel
Part of Phase 9: Model Modularization
"""
from django.db import models


class Program(models.Model):
    """Main program categories (CORE, ASCENT, EDGE, PINNACLE)"""
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
    """Sub-programs within main programs"""
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
    """Individual curriculum levels within sub-programs"""
    subprogram = models.ForeignKey(SubProgram, on_delete=models.CASCADE, related_name='levels')
    level_number = models.IntegerField()
    description = models.TextField(blank=True)
    internal_difficulty = models.IntegerField(
        null=True, 
        blank=True,
        help_text="Internal difficulty tier (1=easiest, higher=harder). Multiple levels can share the same difficulty."
    )
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
    
    @property
    def display_name(self):
        """Abbreviated display name using 'Lv' instead of 'Level'"""
        program_name = self.subprogram.program.get_name_display()
        subprogram_name = self.subprogram.name
        
        # Remove "PRIME" from the beginning
        if program_name.startswith("PRIME "):
            program_name = program_name[6:]
        
        # Check if subprogram name already contains the program name
        if subprogram_name.startswith(self.subprogram.program.name):
            # If it does, just use subprogram name  
            return f"{subprogram_name} - Lv {self.level_number}"
        else:
            # Otherwise, use the program + subprogram format
            return f"{program_name} {subprogram_name} - Lv {self.level_number}"
    
    @property
    def exam_base_name(self):
        """Base name for exam files - simplified format without PRIME and spaces replaced with underscores"""
        program_name = self.subprogram.program.get_name_display()
        subprogram_name = self.subprogram.name
        
        # Remove "PRIME" from the beginning
        if program_name.startswith("PRIME "):
            program_name = program_name[6:]
        
        # Replace spaces with underscores for cleaner file names
        program_name = program_name.replace(" ", "_")
        subprogram_name = subprogram_name.replace(" ", "_")
        
        # Check if subprogram name already contains the program name
        if subprogram_name.startswith(self.subprogram.program.name):
            # If it does, just use subprogram name  
            return f"{subprogram_name}_Lv{self.level_number}"
        else:
            # Otherwise, use the program + subprogram format
            return f"{program_name}_{subprogram_name}_Lv{self.level_number}"
    
    def get_display_name(self):
        """For compatibility - returns abbreviated name"""
        return self.display_name
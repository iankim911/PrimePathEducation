from django.contrib import admin
from .models import School, Teacher, Program, SubProgram, CurriculumLevel, PlacementRule, ExamLevelMapping


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'is_head_teacher', 'created_at']
    list_filter = ['is_head_teacher']
    search_fields = ['name', 'email']


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'grade_range_start', 'grade_range_end', 'order']
    ordering = ['order']


@admin.register(SubProgram)
class SubProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'program', 'order']
    list_filter = ['program']
    ordering = ['program__order', 'order']


@admin.register(CurriculumLevel)
class CurriculumLevelAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'subprogram', 'level_number']
    list_filter = ['subprogram__program', 'subprogram']
    search_fields = ['subprogram__name', 'description']


@admin.register(PlacementRule)
class PlacementRuleAdmin(admin.ModelAdmin):
    list_display = ['grade', 'min_rank_percentile', 'max_rank_percentile', 'curriculum_level', 'priority']
    list_filter = ['grade', 'curriculum_level__subprogram__program']
    ordering = ['priority', 'grade']


@admin.register(ExamLevelMapping)
class ExamLevelMappingAdmin(admin.ModelAdmin):
    list_display = ['curriculum_level', 'exam', 'slot', 'created_at']
    list_filter = ['curriculum_level__subprogram__program', 'slot']
    search_fields = ['curriculum_level__subprogram__name', 'exam__name']
    ordering = ['curriculum_level', 'slot']
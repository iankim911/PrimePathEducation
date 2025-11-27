from django.contrib import admin
from .models import Exam, AudioFile, Question, StudentSession, StudentAnswer, DifficultyAdjustment


class AudioFileInline(admin.TabularInline):
    model = AudioFile
    extra = 1
    fields = ['audio_file', 'start_question', 'end_question', 'order']  # Removed 'name' until migration is run


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 5


@admin.register(AudioFile)
class AudioFileAdmin(admin.ModelAdmin):
    list_display = ['exam', 'start_question', 'end_question', 'order', 'created_at']  # Removed 'name' until migration is run
    list_filter = ['exam']
    search_fields = ['exam__name']  # Removed 'name' from search
    ordering = ['exam', 'order']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'curriculum_level', 'timer_minutes', 'total_questions', 'is_active', 'created_at']
    list_filter = ['is_active', 'curriculum_level__subprogram__program']
    search_fields = ['name']
    inlines = [AudioFileInline, QuestionInline]


@admin.register(StudentSession)
class StudentSessionAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'grade', 'academic_rank', 'exam', 'score', 'percentage_score', 'is_completed', 'started_at']
    list_filter = ['grade', 'academic_rank', 'completed_at']
    search_fields = ['student_name', 'school__name', 'school_name_manual']
    readonly_fields = ['id', 'started_at', 'completed_at', 'time_spent_seconds', 'ip_address', 'user_agent']
    
    def is_completed(self, obj):
        return obj.is_completed
    is_completed.boolean = True


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ['session', 'question', 'is_correct', 'points_earned']
    list_filter = ['is_correct', 'question__question_type']
    search_fields = ['session__student_name']


@admin.register(DifficultyAdjustment)
class DifficultyAdjustmentAdmin(admin.ModelAdmin):
    list_display = ['session', 'from_level', 'to_level', 'adjustment', 'adjusted_at']
    list_filter = ['adjustment']
    search_fields = ['session__student_name']
"""
API Serializers - Phase 8
Django REST Framework serializers for all models
"""
from rest_framework import serializers
from placement_test.models import (
    Exam, Question, AudioFile, StudentSession, 
    StudentAnswer, DifficultyAdjustment
)
from core.models import (
    School, Program, SubProgram, CurriculumLevel
)
from django.contrib.auth.models import User


# Core Model Serializers

class SchoolSerializer(serializers.ModelSerializer):
    """Serializer for School model."""
    
    class Meta:
        model = School
        fields = ['id', 'name', 'address', 'created_at']
        read_only_fields = ['created_at']


class CurriculumLevelSerializer(serializers.ModelSerializer):
    """Serializer for CurriculumLevel model."""
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = CurriculumLevel
        fields = ['id', 'description', 'full_name', 'subprogram', 'level_number']


class SubProgramSerializer(serializers.ModelSerializer):
    """Serializer for SubProgram model."""
    levels = CurriculumLevelSerializer(many=True, read_only=True)
    
    class Meta:
        model = SubProgram
        fields = ['id', 'name', 'program', 'order', 'levels']


class ProgramSerializer(serializers.ModelSerializer):
    """Serializer for Program model."""
    subprograms = SubProgramSerializer(many=True, read_only=True)
    
    class Meta:
        model = Program
        fields = ['id', 'name', 'order', 'subprograms']


# PlacementRule model doesn't exist in current models - removed serializer


# Placement Test Model Serializers

class AudioFileSerializer(serializers.ModelSerializer):
    """Serializer for AudioFile model."""
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = AudioFile
        fields = [
            'id', 'name', 'audio_file', 'file_url',
            'start_question', 'end_question'
        ]
    
    def get_file_url(self, obj):
        """Get full URL for audio file."""
        request = self.context.get('request')
        if obj.audio_file and request:
            return request.build_absolute_uri(obj.audio_file.url)
        return None


# QuestionOption model doesn't exist - removed serializer


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Question model."""
    audio_file = AudioFileSerializer(read_only=True)
    
    class Meta:
        model = Question
        fields = [
            'id', 'exam', 'question_number',
            'question_type', 'points', 'correct_answer',
            'options_count', 'audio_file'
        ]


class ExamSerializer(serializers.ModelSerializer):
    """Serializer for Exam model."""
    curriculum_level_name = serializers.CharField(
        source='curriculum_level.full_name',
        read_only=True
    )
    question_count = serializers.IntegerField(
        source='questions.count',
        read_only=True
    )
    pdf_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Exam
        fields = [
            'id', 'name', 'curriculum_level', 'curriculum_level_name',
            'total_questions', 'question_count', 'timer_minutes',
            'passing_score', 'default_options_count',
            'is_active', 'pdf_file', 'pdf_url'
        ]
        read_only_fields = ['id']
    
    def get_pdf_url(self, obj):
        """Get full URL for PDF file."""
        request = self.context.get('request')
        if obj.pdf_file and request:
            return request.build_absolute_uri(obj.pdf_file.url)
        return None


class ExamDetailSerializer(ExamSerializer):
    """Detailed serializer for Exam with nested data."""
    questions = QuestionSerializer(many=True, read_only=True)
    audio_files = AudioFileSerializer(many=True, read_only=True)
    
    class Meta(ExamSerializer.Meta):
        fields = ExamSerializer.Meta.fields + ['questions', 'audio_files']


class StudentAnswerSerializer(serializers.ModelSerializer):
    """Serializer for StudentAnswer model."""
    question_number = serializers.IntegerField(
        source='question.question_number',
        read_only=True
    )
    
    class Meta:
        model = StudentAnswer
        fields = [
            'id', 'question', 'question_number',
            'answer', 'is_correct', 'created_at'
        ]
        read_only_fields = ['is_correct', 'created_at']


class StudentSessionSerializer(serializers.ModelSerializer):
    """Serializer for StudentSession model."""
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    school_name = serializers.CharField(source='school.name', read_only=True)
    final_curriculum_level_name = serializers.CharField(
        source='final_curriculum_level.full_name',
        read_only=True
    )
    is_completed = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = StudentSession
        fields = [
            'id', 'student_name', 'parent_phone', 'grade',
            'school', 'school_name', 'exam', 'exam_name',
            'academic_rank', 'started_at', 'completed_at',
            'is_completed', 'percentage_score', 'correct_answers',
            'total_questions', 'final_curriculum_level',
            'final_curriculum_level_name'
        ]
        read_only_fields = [
            'started_at', 'completed_at', 'percentage_score',
            'correct_answers', 'total_questions'
        ]


class StudentSessionDetailSerializer(StudentSessionSerializer):
    """Detailed serializer for StudentSession with answers."""
    answers = StudentAnswerSerializer(many=True, read_only=True)
    exam = ExamSerializer(read_only=True)
    
    class Meta(StudentSessionSerializer.Meta):
        fields = StudentSessionSerializer.Meta.fields + ['answers', 'exam']


# Request/Response Serializers

class StartTestSerializer(serializers.Serializer):
    """Serializer for starting a test session."""
    student_name = serializers.CharField(max_length=200)
    parent_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    grade = serializers.IntegerField(min_value=1, max_value=12)
    school_id = serializers.UUIDField(required=False, allow_null=True)
    school_name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    academic_rank = serializers.ChoiceField(
        choices=['top_10', 'top_20', 'top_30', 'average', 'below_average']
    )


class SubmitAnswerSerializer(serializers.Serializer):
    """Serializer for submitting an answer."""
    session_id = serializers.UUIDField()
    question_id = serializers.UUIDField()
    answer = serializers.CharField(allow_blank=True)


class BatchAnswerSerializer(serializers.Serializer):
    """Serializer for batch answer submission."""
    session_id = serializers.UUIDField()
    answers = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )


class SessionStatusSerializer(serializers.Serializer):
    """Serializer for session status response."""
    session_id = serializers.UUIDField()
    status = serializers.CharField()
    progress = serializers.IntegerField()
    time_remaining = serializers.IntegerField()
    answered_questions = serializers.ListField(
        child=serializers.IntegerField()
    )
    current_question = serializers.IntegerField()


class TestResultSerializer(serializers.Serializer):
    """Serializer for test completion results."""
    session_id = serializers.UUIDField()
    total_questions = serializers.IntegerField()
    answered = serializers.IntegerField()
    correct = serializers.IntegerField()
    score = serializers.FloatField()
    percentage = serializers.FloatField()
    placement_level = serializers.CharField()
    certificate_url = serializers.CharField(required=False)


# Bulk Operation Serializers

class BulkCreateQuestionSerializer(serializers.Serializer):
    """Serializer for bulk question creation."""
    exam_id = serializers.UUIDField()
    questions = serializers.ListField(
        child=serializers.DictField()
    )


class ExamStatisticsSerializer(serializers.Serializer):
    """Serializer for exam statistics."""
    exam_id = serializers.UUIDField()
    total_sessions = serializers.IntegerField()
    completed_sessions = serializers.IntegerField()
    average_score = serializers.FloatField()
    pass_rate = serializers.FloatField()
    average_completion_time = serializers.IntegerField()
    difficulty_distribution = serializers.DictField()


# File Upload Serializers

class FileUploadSerializer(serializers.Serializer):
    """Generic file upload serializer."""
    file = serializers.FileField()
    file_type = serializers.ChoiceField(choices=['pdf', 'audio', 'image'])
    related_id = serializers.UUIDField(required=False)
    metadata = serializers.JSONField(required=False)


# WebSocket Message Serializers

class WebSocketMessageSerializer(serializers.Serializer):
    """Serializer for WebSocket messages."""
    type = serializers.CharField()
    data = serializers.JSONField()
    timestamp = serializers.DateTimeField()


# Dashboard Serializers

class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics."""
    total_sessions = serializers.IntegerField()
    active_exams = serializers.IntegerField()
    completed_today = serializers.IntegerField()
    average_score = serializers.FloatField()
    recent_sessions = StudentSessionSerializer(many=True)
    exam_statistics = ExamStatisticsSerializer(many=True)
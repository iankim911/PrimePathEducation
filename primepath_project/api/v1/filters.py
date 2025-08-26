"""
API Filters - Phase 8
Filter classes for API endpoints
"""
from django_filters import rest_framework as filters
from placement_test.models import PlacementExam as Exam, StudentSession
from core.models import PlacementRule


class ExamFilter(filters.FilterSet):
    """Filter for Exam queryset."""
    name = filters.CharFilter(lookup_expr='icontains')
    is_active = filters.BooleanFilter()
    curriculum_level = filters.UUIDFilter()
    min_questions = filters.NumberFilter(field_name='total_questions', lookup_expr='gte')
    max_questions = filters.NumberFilter(field_name='total_questions', lookup_expr='lte')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Exam
        fields = [
            'name', 'is_active', 'curriculum_level',
            'total_questions', 'timer_minutes', 'passing_score'
        ]


class SessionFilter(filters.FilterSet):
    """Filter for StudentSession queryset."""
    student_name = filters.CharFilter(lookup_expr='icontains')
    school = filters.UUIDFilter()
    exam = filters.UUIDFilter()
    grade = filters.NumberFilter()
    academic_rank = filters.CharFilter()
    completed = filters.BooleanFilter(field_name='completed_at', lookup_expr='isnull', exclude=True)
    started_after = filters.DateTimeFilter(field_name='start_time', lookup_expr='gte')
    started_before = filters.DateTimeFilter(field_name='start_time', lookup_expr='lte')
    min_score = filters.NumberFilter(field_name='percentage_score', lookup_expr='gte')
    max_score = filters.NumberFilter(field_name='percentage_score', lookup_expr='lte')
    
    class Meta:
        model = StudentSession
        fields = [
            'student_name', 'school', 'exam', 'grade',
            'academic_rank', 'final_curriculum_level'
        ]


class PlacementRuleFilter(filters.FilterSet):
    """Filter for PlacementRule queryset."""
    grade = filters.NumberFilter()
    curriculum_level = filters.UUIDFilter()
    min_rank = filters.NumberFilter(field_name='min_rank_percentile', lookup_expr='gte')
    max_rank = filters.NumberFilter(field_name='max_rank_percentile', lookup_expr='lte')
    
    class Meta:
        model = PlacementRule
        fields = ['grade', 'curriculum_level', 'priority']
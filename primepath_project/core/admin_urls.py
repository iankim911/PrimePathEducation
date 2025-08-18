"""
Administrative URLs
URLs for administrative functions and configuration
"""
from django.urls import path
from .views import (
    placement_rules, create_placement_rule,
    delete_placement_rule, exam_mapping
)

urlpatterns = [
    # Administrative functions
    path('placement-rules/', placement_rules, name='placement_rules'),
    path('placement-rules/create/', create_placement_rule, name='create_placement_rule'),
    path('placement-rules/<int:pk>/delete/', delete_placement_rule, name='delete_placement_rule'),
    path('exam-mapping/', exam_mapping, name='exam_mapping'),
]
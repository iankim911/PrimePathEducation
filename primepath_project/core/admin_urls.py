"""
Administrative URLs
URLs for administrative functions and configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    # Administrative functions
    path('placement-rules/', views.placement_rules, name='placement_rules'),
    path('placement-rules/create/', views.create_placement_rule, name='create_placement_rule'),
    path('placement-rules/<int:pk>/delete/', views.delete_placement_rule, name='delete_placement_rule'),
    path('exam-mapping/', views.exam_mapping, name='exam_mapping'),
]
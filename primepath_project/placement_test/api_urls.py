"""
API URL patterns for placement test.
"""
from django.urls import path
from . import api_views

app_name = 'placement_api'

urlpatterns = [
    # Exam endpoints
    path('exams/', api_views.api_exam_list, name='exam_list'),
    path('exams/<uuid:exam_id>/', api_views.api_exam_detail, name='exam_detail'),
    
    # Session endpoints
    path('sessions/<uuid:session_id>/status/', api_views.api_session_status, name='session_status'),
    path('sessions/complete/', api_views.api_complete_session, name='complete_session'),
    
    # Answer endpoints
    path('answers/submit/', api_views.api_submit_answer, name='submit_answer'),
    
    # Rules
    path('rules/', api_views.api_placement_rules, name='placement_rules'),
]
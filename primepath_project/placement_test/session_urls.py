"""
Session Management URLs
URLs for session administration and grading
"""
from django.urls import path
from . import views

urlpatterns = [
    # Session management
    path('sessions/', views.session_list, name='session_list'),
    path('sessions/<uuid:session_id>/', views.session_detail, name='session_detail'),
    path('sessions/<uuid:session_id>/grade/', views.grade_session, name='grade_session'),
    path('sessions/<uuid:session_id>/export/', views.export_result, name='export_result'),
]
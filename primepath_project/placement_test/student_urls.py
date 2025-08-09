"""
Student Test-Taking URLs
URLs for student test workflow and test session management
"""
from django.urls import path
from . import views

urlpatterns = [
    # Student test workflow
    path('start/', views.start_test, name='start_test'),
    path('session/<uuid:session_id>/', views.take_test, name='take_test'),
    path('session/<uuid:session_id>/submit/', views.submit_answer, name='submit_answer'),
    path('session/<uuid:session_id>/adjust-difficulty/', views.adjust_difficulty, name='adjust_difficulty'),
    path('session/<uuid:session_id>/manual-adjust/', views.manual_adjust_difficulty, name='manual_adjust_difficulty'),
    path('session/<uuid:session_id>/complete/', views.complete_test, name='complete_test'),
    path('session/<uuid:session_id>/result/', views.test_result, name='test_result'),
]
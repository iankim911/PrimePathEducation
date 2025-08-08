"""
AJAX/API URLs
URLs for AJAX endpoints and API functionality
"""
from django.urls import path
from . import views

urlpatterns = [
    # AJAX/API endpoints
    path('audio/<int:audio_id>/', views.get_audio, name='get_audio'),
    path('questions/<int:question_id>/update/', views.update_question, name='update_question'),
    path('exams/<uuid:exam_id>/create-questions/', views.create_questions, name='create_questions'),
    path('exams/<uuid:exam_id>/save-answers/', views.save_exam_answers, name='save_exam_answers'),
    path('exams/<uuid:exam_id>/update-audio-names/', views.update_audio_names, name='update_audio_names'),
    path('exams/<uuid:exam_id>/audio/<int:audio_id>/delete/', views.delete_audio_from_exam, name='delete_audio_from_exam'),
    path('exams/<uuid:exam_id>/update-name/', views.update_exam_name, name='update_exam_name'),
]
"""
AJAX/API URLs
URLs for AJAX endpoints and API functionality
"""
from django.urls import path
from . import views
from .views.mode_toggle import toggle_view_mode, get_current_mode, authenticate_admin

urlpatterns = [
    # AJAX/API endpoints
    path('audio/<int:audio_id>/', views.get_audio, name='get_audio'),
    path('questions/<int:question_id>/update/', views.update_question, name='update_question'),
    path('exams/<uuid:exam_id>/create-questions/', views.create_questions, name='create_questions'),
    path('exams/<uuid:exam_id>/save-answers/', views.save_exam_answers, name='save_exam_answers'),
    path('exams/<uuid:exam_id>/update-audio-names/', views.update_audio_names, name='update_audio_names'),
    path('exams/<uuid:exam_id>/audio/<int:audio_id>/delete/', views.delete_audio_from_exam, name='delete_audio_from_exam'),
    path('exams/<uuid:exam_id>/update-name/', views.update_exam_name, name='update_exam_name'),
    # Cascading curriculum hierarchy endpoint
    path('api/curriculum-hierarchy/', views.get_curriculum_hierarchy, name='get_curriculum_hierarchy'),
    
    # Mode toggle endpoints
    path('api/toggle-mode/', toggle_view_mode, name='toggle_mode'),
    path('api/current-mode/', get_current_mode, name='get_current_mode'),
    path('api/authenticate-admin/', authenticate_admin, name='authenticate_admin'),
]
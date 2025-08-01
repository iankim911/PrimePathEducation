from django.urls import path
from . import views

app_name = 'placement_test'

urlpatterns = [
    path('start/', views.start_test, name='start_test'),
    path('session/<uuid:session_id>/', views.take_test, name='take_test'),
    path('session/<uuid:session_id>/submit/', views.submit_answer, name='submit_answer'),
    path('session/<uuid:session_id>/adjust-difficulty/', views.adjust_difficulty, name='adjust_difficulty'),
    path('session/<uuid:session_id>/complete/', views.complete_test, name='complete_test'),
    path('session/<uuid:session_id>/result/', views.test_result, name='test_result'),
    
    path('exams/', views.exam_list, name='exam_list'),
    path('exams/create/', views.create_exam, name='create_exam'),
    path('exams/check-version/', views.check_exam_version, name='check_exam_version'),
    path('exams/<uuid:exam_id>/', views.exam_detail, name='exam_detail'),
    path('exams/<uuid:exam_id>/edit/', views.edit_exam, name='edit_exam'),
    path('exams/<uuid:exam_id>/preview/', views.preview_exam, name='preview_exam'),
    path('exams/<uuid:exam_id>/audio/add/', views.add_audio, name='add_audio'),
    path('exams/<uuid:exam_id>/questions/', views.manage_questions, name='manage_questions'),
    path('exams/<uuid:exam_id>/delete/', views.delete_exam, name='delete_exam'),
    
    path('sessions/', views.session_list, name='session_list'),
    path('sessions/<uuid:session_id>/grade/', views.grade_session, name='grade_session'),
    
    path('audio/<int:audio_id>/', views.get_audio, name='get_audio'),
    path('questions/<int:question_id>/update/', views.update_question, name='update_question'),
    path('exams/<uuid:exam_id>/create-questions/', views.create_questions, name='create_questions'),
    path('exams/<uuid:exam_id>/save-answers/', views.save_exam_answers, name='save_exam_answers'),
    path('exams/<uuid:exam_id>/update-audio-names/', views.update_audio_names, name='update_audio_names'),
    path('exams/<uuid:exam_id>/audio/<int:audio_id>/delete/', views.delete_audio_from_exam, name='delete_audio_from_exam'),
    path('exams/<uuid:exam_id>/update-name/', views.update_exam_name, name='update_exam_name'),
]
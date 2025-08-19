"""
AJAX/API URLs
URLs for AJAX endpoints and API functionality
"""
from django.urls import path
from . import views
from .views.mode_toggle import toggle_view_mode, get_current_mode, authenticate_admin
from .views import exam_management  # BUILDER: Day 4
from .views import exam_api  # Exam Management Modal APIs
from .views import curriculum_admin  # Admin Curriculum Management APIs

urlpatterns = [
    # AJAX/API endpoints
    path('audio/<int:audio_id>/', views.get_audio, name='get_audio'),
    path('questions/<int:question_id>/update/', views.update_question, name='update_question'),
    path('exams/<uuid:exam_id>/create-questions/', views.create_questions, name='create_questions'),
    path('exams/<uuid:exam_id>/save-answers/', views.save_exam_answers, name='save_exam_answers'),
    path('exams/<uuid:exam_id>/update-audio-names/', views.update_audio_names, name='update_audio_names'),
    path('exams/<uuid:exam_id>/audio/<int:audio_id>/delete/', views.delete_audio_from_exam, name='delete_audio_from_exam'),
    # UPDATE NAME REMOVED: Names are systematically generated from exam type and curriculum
    # path('exams/<uuid:exam_id>/update-name/', views.update_exam_name, name='update_exam_name'),
    # Cascading curriculum hierarchy endpoint
    path('api/curriculum-hierarchy/', views.get_curriculum_hierarchy, name='get_curriculum_hierarchy'),
    
    # Mode toggle endpoints
    path('api/toggle-mode/', toggle_view_mode, name='toggle_mode'),
    path('api/current-mode/', get_current_mode, name='get_current_mode'),
    path('api/authenticate-admin/', authenticate_admin, name='authenticate_admin'),
    
    # Day 4: Exam Management APIs
    # Admin URLs
    path('admin/exams/upload/', exam_management.upload_exam, name='upload_exam'),
    path('admin/exams/<uuid:exam_id>/answer-key/', exam_management.set_answer_key, name='set_answer_key'),
    
    # Teacher URLs
    path('teacher/exams/', exam_management.list_available_exams, name='list_available_exams'),
    path('teacher/exams/assign/', exam_management.assign_exam_to_class, name='assign_exam_to_class'),
    path('teacher/exams/assign-individual/', exam_management.assign_exam_to_students, name='assign_exam_to_students'),
    path('teacher/assignments/<uuid:assignment_id>/extend/', exam_management.extend_deadline, name='extend_deadline'),
    
    # Student URLs
    path('student/exams/', exam_management.view_assigned_exams, name='view_assigned_exams'),
    path('student/exams/<uuid:exam_id>/start/', exam_management.start_exam, name='start_exam'),
    path('student/exams/<uuid:exam_id>/auto-save/', exam_management.auto_save_progress, name='auto_save_progress'),
    path('student/exams/<uuid:exam_id>/submit/', exam_management.submit_exam, name='submit_exam'),
    
    # Exam Management Modal APIs
    path('api/class/<str:class_code>/overview/', exam_api.get_class_overview, name='class_overview'),
    path('api/class/<str:class_code>/exams/', exam_api.get_class_exams, name='class_exams'),
    path('api/class/<str:class_code>/students/', exam_api.get_class_students, name='class_students'),
    path('api/class/<str:class_code>/all-exams/', exam_api.get_class_all_exams, name='class_all_exams'),
    path('api/class/<str:class_code>/filtered-exams/', exam_api.get_class_filtered_exams, name='class_filtered_exams'),
    path('api/all-classes/', exam_api.get_all_classes, name='all_classes'),
    path('api/copy-exam/', exam_api.copy_exam, name='copy_exam'),
    path('api/exam/<uuid:exam_id>/delete/', exam_api.delete_exam, name='delete_exam'),
    path('api/exam/<uuid:exam_id>/duration/', exam_api.update_exam_duration, name='update_exam_duration'),
    path('api/schedule-exam/', exam_api.schedule_exam, name='schedule_exam'),
    
    # Admin Curriculum Management APIs
    path('api/admin/classes/', curriculum_admin.get_all_classes_admin, name='admin_classes'),
    path('api/admin/class/', curriculum_admin.create_class, name='create_class'),
    path('api/admin/class/<str:class_code>/', curriculum_admin.get_class_details, name='get_class_details'),
    path('api/admin/class/<str:class_code>/update/', curriculum_admin.update_class, name='update_class'),
    path('api/admin/class/<str:class_code>/delete/', curriculum_admin.delete_class, name='delete_class'),
    path('api/admin/curriculum-mapping/', curriculum_admin.save_curriculum_mapping, name='save_curriculum'),
]
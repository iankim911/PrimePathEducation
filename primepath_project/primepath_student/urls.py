from django.urls import path
from . import views

app_name = 'primepath_student'

urlpatterns = [
    # Authentication
    path('register/', views.student_register, name='register'),
    path('login/', views.student_login, name='login'),
    path('logout/', views.student_logout, name='logout'),
    path('kakao-login/', views.kakao_login, name='kakao_login'),
    
    # Dashboard
    path('', views.student_dashboard, name='dashboard'),
    path('dashboard/', views.student_dashboard, name='dashboard_alias'),
    
    # Class views
    path('class/<str:class_code>/', views.class_detail, name='class_detail'),
    
    # Exam taking
    path('exam/start/<uuid:launch_id>/', views.start_exam, name='start_exam'),
    path('exam/<uuid:session_id>/', views.take_exam, name='take_exam'),
    path('exam/<uuid:session_id>/save-answer/', views.save_answer, name='save_answer'),
    path('exam/<uuid:session_id>/auto-save/', views.auto_save, name='auto_save'),
    path('exam/<uuid:session_id>/submit/', views.submit_exam, name='submit_exam'),
    path('exam/<uuid:session_id>/result/', views.exam_result, name='exam_result'),
    path('exam-history/', views.exam_history, name='exam_history'),
    
    # Admin Dashboard
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/monitor/<uuid:session_id>/', views.monitor_session, name='admin_monitor_session'),
    path('admin/terminate/<uuid:session_id>/', views.terminate_session, name='admin_terminate_session'),
    path('admin/export/', views.export_data, name='admin_export'),
    path('admin/analytics/', views.analytics_view, name='admin_analytics'),
]
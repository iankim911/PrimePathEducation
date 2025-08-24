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
]
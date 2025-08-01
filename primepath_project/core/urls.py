from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('curriculum/levels/', views.curriculum_levels, name='curriculum_levels'),
    path('placement-rules/', views.placement_rules, name='placement_rules'),
    path('placement-rules/create/', views.create_placement_rule, name='create_placement_rule'),
    path('placement-rules/<int:pk>/delete/', views.delete_placement_rule, name='delete_placement_rule'),
    path('api/placement-rules/', views.get_placement_rules, name='get_placement_rules'),
    path('api/placement-rules/save/', views.save_placement_rules, name='save_placement_rules'),
    path('exam-mapping/', views.exam_mapping, name='exam_mapping'),
    path('api/exam-mappings/save/', views.save_exam_mappings, name='save_exam_mappings'),
]
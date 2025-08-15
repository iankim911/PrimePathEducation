"""
Phase 5: Student Roster & Assignment URLs
Handles roster management, assignment tracking, and completion monitoring
"""
from django.urls import path
from .views import roster

urlpatterns = [
    # Roster management
    path('exams/<uuid:exam_id>/roster/', roster.manage_roster, name='manage_roster'),
    path('exams/<uuid:exam_id>/roster/import/', roster.import_roster_csv, name='import_roster_csv'),
    path('exams/<uuid:exam_id>/roster/report/', roster.roster_report, name='roster_report'),
    path('exams/<uuid:exam_id>/roster/export/', roster.export_roster, name='export_roster'),
    
    # Individual roster entry management
    path('roster/<uuid:roster_id>/status/', roster.update_roster_status, name='update_roster_status'),
    path('roster/<uuid:roster_id>/remove/', roster.remove_roster_entry, name='remove_roster_entry'),
]
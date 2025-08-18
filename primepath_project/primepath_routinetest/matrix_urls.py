"""
Schedule Matrix URL patterns
"""
from django.urls import path
from .views import schedule_matrix_optimized as matrix_views

urlpatterns = [
    # Main matrix view
    path('schedule-matrix/', 
         matrix_views.schedule_matrix_view, 
         name='schedule_matrix'),
    
    # Matrix cell detail/management
    path('schedule-matrix/cell/<uuid:matrix_id>/', 
         matrix_views.matrix_cell_detail, 
         name='matrix_cell_detail'),
    
    # API endpoints
    path('api/schedule-matrix/bulk-assign/', 
         matrix_views.bulk_assign_exams, 
         name='api_bulk_assign_exams'),
    
    path('api/schedule-matrix/data/', 
         matrix_views.get_matrix_data, 
         name='api_get_matrix_data'),
    
    path('api/schedule-matrix/clone/', 
         matrix_views.clone_schedule, 
         name='api_clone_schedule'),
    
    # Test/Debug views
    path('matrix-test/', 
         matrix_views.matrix_test_view, 
         name='matrix_test'),
]
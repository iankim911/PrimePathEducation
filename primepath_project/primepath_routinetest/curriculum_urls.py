"""
Curriculum Mapping URL patterns
Admin-only URLs for managing class-curriculum mappings
"""
from django.urls import path
from .views import curriculum_mapping as cm_views

urlpatterns = [
    # Main curriculum mapping interface
    path('curriculum-mapping/', 
         cm_views.curriculum_mapping_view, 
         name='curriculum_mapping'),
    
    # AJAX endpoints
    path('api/curriculum-mapping/add/', 
         cm_views.add_curriculum_mapping, 
         name='api_add_curriculum_mapping'),
    
    path('api/curriculum-mapping/remove/', 
         cm_views.remove_curriculum_mapping, 
         name='api_remove_curriculum_mapping'),
    
    path('api/curriculum-mapping/update-priority/', 
         cm_views.update_mapping_priority, 
         name='api_update_mapping_priority'),
    
    path('api/curriculum-mapping/bulk-add/', 
         cm_views.bulk_add_mappings, 
         name='api_bulk_add_mappings'),
    
    path('api/curriculum-mapping/class/<str:class_code>/', 
         cm_views.get_class_mappings, 
         name='api_get_class_mappings'),
]
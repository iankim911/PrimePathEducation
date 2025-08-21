"""
URLs for Class Code Management
"""
from django.urls import path
from .views import class_code_admin

urlpatterns = [
    # Class Code Management
    path('admin/class-codes/', class_code_admin.class_code_overview, name='class_code_overview'),
    path('admin/class-codes/sync/', class_code_admin.sync_class_codes, name='sync_class_codes'),
    path('admin/class-codes/matrix/', class_code_admin.class_code_matrix, name='class_code_matrix'),
    path('api/class-codes/mapping/', class_code_admin.get_class_code_mapping, name='get_class_code_mapping'),
]
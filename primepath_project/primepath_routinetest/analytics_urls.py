"""
Analytics and Reporting URLs
Provides comprehensive analytics and reporting for teachers
"""
from django.urls import path
from .views import analytics

urlpatterns = [
    # Main analytics dashboard
    path('analytics/', analytics.analytics_dashboard, name='analytics_dashboard'),
    
    # Export endpoints
    path('analytics/export/', analytics.export_analytics_report, name='export_analytics'),
    
    # Chart data API
    path('analytics/chart-data/', analytics.get_chart_data, name='chart_data'),
]
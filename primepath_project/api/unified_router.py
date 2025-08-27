"""
Phase 7: Unified API Router
Date: August 26, 2025
Purpose: Central API routing for all modules
"""

from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from core.service_registry import ServiceRegistry
import json


class UnifiedAPIRouter:
    """Unified API router using the service registry."""
    
    @staticmethod
    @csrf_exempt
    def route_exam_api(request, module, action):
        """Route exam API calls to appropriate service."""
        
        try:
            # Get the appropriate service
            service = ServiceRegistry.get(f'{module}.exam')
            
            # Parse request data
            if request.method == 'POST':
                data = json.loads(request.body)
            else:
                data = request.GET.dict()
            
            # Route to action
            if hasattr(service, action):
                result = getattr(service, action)(**data)
                return JsonResponse({'success': True, 'data': result})
            else:
                return JsonResponse({'success': False, 'error': f'Action {action} not found'}, status=404)
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    @staticmethod
    @csrf_exempt
    def route_grading_api(request, module, action):
        """Route grading API calls to appropriate service."""
        
        try:
            service = ServiceRegistry.get(f'{module}.grading')
            
            if request.method == 'POST':
                data = json.loads(request.body)
            else:
                data = request.GET.dict()
            
            if hasattr(service, action):
                result = getattr(service, action)(**data)
                return JsonResponse({'success': True, 'data': result})
            else:
                return JsonResponse({'success': False, 'error': f'Action {action} not found'}, status=404)
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    @staticmethod
    def get_service_info(request, service_name):
        """Get information about a registered service."""
        
        try:
            if ServiceRegistry.has(service_name):
                service = ServiceRegistry.get(service_name)
                methods = [m for m in dir(service) if not m.startswith('_')]
                
                return JsonResponse({
                    'success': True,
                    'service': service_name,
                    'type': type(service).__name__,
                    'methods': methods
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Service {service_name} not found'
                }, status=404)
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    @staticmethod
    def list_services(request):
        """List all registered services."""
        
        services = ServiceRegistry.list_services()
        grouped = {
            'core': [],
            'placement': [],
            'routine': [],
            'student': [],
            'other': []
        }
        
        for service in services:
            if service.startswith('placement.'):
                grouped['placement'].append(service)
            elif service.startswith('routine.'):
                grouped['routine'].append(service)
            elif service.startswith('student.'):
                grouped['student'].append(service)
            elif '.' not in service:
                grouped['core'].append(service)
            else:
                grouped['other'].append(service)
        
        return JsonResponse({
            'success': True,
            'total': len(services),
            'services': grouped
        })


# URL patterns for the unified API
urlpatterns = [
    # Service discovery
    path('services/', UnifiedAPIRouter.list_services, name='api_list_services'),
    path('services/<str:service_name>/', UnifiedAPIRouter.get_service_info, name='api_service_info'),
    
    # Module APIs
    path('<str:module>/exam/<str:action>/', UnifiedAPIRouter.route_exam_api, name='api_exam'),
    path('<str:module>/grading/<str:action>/', UnifiedAPIRouter.route_grading_api, name='api_grading'),
]
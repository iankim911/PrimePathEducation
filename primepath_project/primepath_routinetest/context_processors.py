"""
RoutineTest Context Processors

Provides module-specific context to all RoutineTest templates
Includes theme information and debugging data
"""
import logging

logger = logging.getLogger(__name__)

def routinetest_context(request):
    """
    Add RoutineTest-specific context to templates
    
    This context processor ensures all RoutineTest templates
    have access to module and theme information
    """
    
    # Check if this is a RoutineTest URL
    is_routinetest = 'routinetest' in request.path.lower() or 'routine' in request.path.lower()
    
    # Log the context being added
    if is_routinetest:
        logger.info(f"[RoutineTest Context] Processing request for: {request.path}")
        logger.info("[RoutineTest Context] Adding BCG Green theme context")
    
    context = {
        'module_name': 'RoutineTest',
        'theme_name': 'BCG Green',
        'theme_primary_color': '#00A65E',
        'theme_primary_dark': '#007C3F',
        'theme_primary_light': '#E8F5E9',
        'is_routinetest': is_routinetest,
        'module_version': '2.0.0',
        'module_description': 'Continuous Assessment Platform',
        'debug_mode': request.GET.get('debug', 'false') == 'true',
    }
    
    # Add console debugging information
    if is_routinetest:
        context['console_debug'] = {
            'module': 'RoutineTest',
            'theme': 'BCG Green',
            'user': str(request.user) if hasattr(request, 'user') and request.user and request.user.is_authenticated else 'Anonymous',
            'path': request.path,
            'method': request.method,
        }
        
        # Log to server console
        logger.debug(f"[RoutineTest] Context added for {request.path}")
        logger.debug(f"[RoutineTest] Theme: BCG Green (#00A65E)")
        logger.debug(f"[RoutineTest] User: {context['console_debug']['user']}")
    
    return context
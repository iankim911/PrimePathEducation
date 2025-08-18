"""
RoutineTest Context Processors

Provides module-specific context to all RoutineTest templates
Includes theme information and debugging data
"""
import logging
from core.models import Teacher

logger = logging.getLogger(__name__)

def routinetest_context(request):
    """
    Add RoutineTest-specific context to templates
    
    This context processor ensures all RoutineTest templates
    have access to module and theme information
    """
    
    # Check if this is a RoutineTest URL
    is_routinetest = 'routinetest' in request.path.lower() or 'routine' in request.path.lower()
    
    # Check if user is head teacher/admin
    is_head_teacher = False
    if hasattr(request, 'user') and request.user and request.user.is_authenticated:
        try:
            teacher = Teacher.objects.get(user=request.user)
            is_head_teacher = teacher.is_head_teacher
        except Teacher.DoesNotExist:
            is_head_teacher = False
    
    # Log the context being added
    if is_routinetest:
        logger.info(f"[RoutineTest Context] Processing request for: {request.path}")
        logger.info("[RoutineTest Context] Adding BCG Green theme context")
        if is_head_teacher:
            logger.info("[RoutineTest Context] User is HEAD TEACHER/ADMIN")
    
    # Get current view mode from session with robust error handling
    current_view_mode = 'Teacher'  # Default
    if hasattr(request, 'session'):
        try:
            view_mode_value = request.session.get('view_mode', 'Teacher')
            
            # CRITICAL FIX: Handle edge cases where session contains invalid data
            if callable(view_mode_value):
                # If it's a function/callable, call it to get the value
                logger.warning(f"[CONTEXT_PROCESSOR_FIX] Found callable in session view_mode: {view_mode_value}")
                try:
                    current_view_mode = str(view_mode_value())
                except:
                    current_view_mode = 'Teacher'
            elif view_mode_value is None:
                current_view_mode = 'Teacher'
            elif not isinstance(view_mode_value, str):
                # Convert non-string values to string
                logger.warning(f"[CONTEXT_PROCESSOR_FIX] Non-string view_mode in session: {type(view_mode_value)}")
                current_view_mode = str(view_mode_value)
            else:
                # Valid string value
                current_view_mode = view_mode_value
                
            # Additional validation: ensure it's a valid mode
            if current_view_mode not in ['Teacher', 'Admin']:
                logger.warning(f"[CONTEXT_PROCESSOR_FIX] Invalid view_mode '{current_view_mode}', defaulting to Teacher")
                current_view_mode = 'Teacher'
                # Clean up the session
                request.session['view_mode'] = 'Teacher'
                
        except Exception as e:
            logger.error(f"[CONTEXT_PROCESSOR_FIX] Error processing view_mode: {e}")
            current_view_mode = 'Teacher'
    
    context = {
        'module_name': 'RoutineTest',
        'theme_name': 'BCG Green',
        'theme_primary_color': '#00A65E',
        'theme_primary_dark': '#007C3F',
        'theme_primary_light': '#E8F5E9',
        'is_routinetest': is_routinetest,
        'module_version': '2.1.0',
        'module_description': 'Exam Management System',
        'debug_mode': request.GET.get('debug', 'false') == 'true',
        'is_head_teacher': is_head_teacher,  # Add head teacher status
        'current_view_mode': current_view_mode,  # Add current view mode
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
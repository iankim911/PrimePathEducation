"""
Mode Toggle View - Admin/Teacher Mode Switching with Authentication
Handles switching between Admin and Teacher modes for RoutineTest
Enhanced with authentication for Admin mode access
"""
import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from primepath_routinetest.error_handlers import ConsoleLogger
from datetime import datetime

logger = logging.getLogger(__name__)

@login_required
@require_POST
def toggle_view_mode(request):
    """
    Toggle between Admin and Teacher view modes
    Only available to staff users
    """
    try:
        # Check if user is staff
        if not request.user.is_staff:
            return JsonResponse({
                'success': False,
                'message': 'Permission denied. Only staff members can toggle modes.'
            }, status=403)
        
        # Parse request body
        try:
            data = json.loads(request.body)
            new_mode = data.get('mode', 'Teacher')
        except json.JSONDecodeError:
            new_mode = request.POST.get('mode', 'Teacher')
        
        # Validate mode with extra type checking
        if not isinstance(new_mode, str):
            logger.error(f"[MODE_TOGGLE_FIX] Received non-string mode: {type(new_mode)} - {new_mode}")
            new_mode = str(new_mode) if new_mode else 'Teacher'
            
        if new_mode not in ['Admin', 'Teacher']:
            return JsonResponse({
                'success': False,
                'message': f'Invalid mode: {new_mode}. Must be Admin or Teacher.'
            }, status=400)
        
        # Store in session with validation
        old_mode = request.session.get('view_mode', 'Teacher')
        
        # Extra validation to ensure we never store non-string values
        if not isinstance(old_mode, str):
            logger.warning(f"[MODE_TOGGLE_FIX] Found non-string in session: {type(old_mode)}")
            old_mode = 'Teacher'
            
        request.session['view_mode'] = str(new_mode)  # Ensure it's a string
        request.session.save()
        
        # Log mode change
        ConsoleLogger.log_view_start(
            f'MODE_TOGGLE_{new_mode}',
            request.user,
            {
                'old_mode': old_mode,
                'new_mode': new_mode,
                'user_is_superuser': request.user.is_superuser
            }
        )
        
        logger.info(f"[MODE_TOGGLE] User {request.user.username} switched from {old_mode} to {new_mode} mode")
        
        # Determine available features based on mode
        features = {
            'curriculum_mapping': new_mode == 'Admin',
            'bulk_operations': new_mode == 'Admin',
            'advanced_analytics': new_mode == 'Admin',
            'class_management': True,  # Available in both modes
            'exam_management': True,   # Available in both modes
        }
        
        return JsonResponse({
            'success': True,
            'mode': new_mode,
            'previous_mode': old_mode,
            'features': features,
            'message': f'Successfully switched to {new_mode} mode'
        })
        
    except Exception as e:
        logger.error(f"[MODE_TOGGLE_ERROR] Error toggling mode: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error switching modes: {str(e)}'
        }, status=500)


@login_required
def get_current_mode(request):
    """
    Get the current view mode for the user
    """
    try:
        current_mode = request.session.get('view_mode', 'Teacher')
        
        return JsonResponse({
            'success': True,
            'mode': current_mode,
            'is_admin': current_mode == 'Admin',
            'user': {
                'username': request.user.username,
                'is_staff': request.user.is_staff,
                'is_superuser': request.user.is_superuser
            }
        })
        
    except Exception as e:
        logger.error(f"[GET_MODE_ERROR] Error getting current mode: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error getting current mode: {str(e)}'
        }, status=500)


@login_required
@require_POST
def authenticate_admin(request):
    """
    Authenticate user for Admin mode access
    Requires valid admin credentials
    """
    try:
        # Parse request body
        try:
            data = json.loads(request.body)
            username = data.get('username', '')
            password = data.get('password', '')
        except json.JSONDecodeError:
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
        
        # Enhanced logging
        console_log = {
            'action': 'ADMIN_AUTH_ATTEMPT',
            'username': username,
            'timestamp': datetime.now().isoformat(),
            'ip_address': request.META.get('REMOTE_ADDR', 'unknown'),
            'user_agent': request.META.get('HTTP_USER_AGENT', 'unknown')
        }
        logger.info(f"[ADMIN_AUTH] Authentication attempt: {json.dumps(console_log)}")
        print(f"\n{'='*60}")
        print(f"[ADMIN_AUTH] Authentication Attempt")
        print(f"  Username: {username}")
        print(f"  Timestamp: {datetime.now()}")
        print(f"  Current User: {request.user.username}")
        print(f"{'='*60}\n")
        
        # Validate inputs
        if not username or not password:
            logger.warning(f"[ADMIN_AUTH] Missing credentials from {request.user.username}")
            return JsonResponse({
                'success': False,
                'message': 'Username and password are required'
            }, status=400)
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user has admin privileges
            if user.is_staff or user.is_superuser:
                logger.info(f"[ADMIN_AUTH] ✅ Successful authentication for {username}")
                print(f"[ADMIN_AUTH] ✅ Authentication successful for {username}")
                print(f"  is_staff: {user.is_staff}")
                print(f"  is_superuser: {user.is_superuser}")
                
                # Log successful authentication
                ConsoleLogger.log_view_start(
                    'ADMIN_AUTH_SUCCESS',
                    user,
                    {
                        'authenticated_user': username,
                        'is_staff': user.is_staff,
                        'is_superuser': user.is_superuser,
                        'authentication_time': datetime.now().isoformat()
                    }
                )
                
                # Set admin mode in session
                request.session['view_mode'] = 'Admin'
                request.session['admin_authenticated'] = True
                request.session['admin_auth_time'] = datetime.now().isoformat()
                request.session.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Authentication successful',
                    'user': {
                        'username': user.username,
                        'is_staff': user.is_staff,
                        'is_superuser': user.is_superuser
                    }
                })
            else:
                logger.warning(f"[ADMIN_AUTH] User {username} lacks admin privileges")
                print(f"[ADMIN_AUTH] ❌ User {username} is not an admin")
                
                return JsonResponse({
                    'success': False,
                    'message': 'You do not have admin privileges. Only staff members can access Admin Mode.'
                }, status=403)
        else:
            logger.warning(f"[ADMIN_AUTH] Failed authentication for {username}")
            print(f"[ADMIN_AUTH] ❌ Authentication failed for {username}")
            
            # Log failed attempt
            ConsoleLogger.log_view_start(
                'ADMIN_AUTH_FAILED',
                request.user,
                {
                    'attempted_username': username,
                    'failure_time': datetime.now().isoformat(),
                    'ip_address': request.META.get('REMOTE_ADDR', 'unknown')
                }
            )
            
            return JsonResponse({
                'success': False,
                'message': 'Invalid credentials. Please check your username and password.'
            }, status=401)
            
    except Exception as e:
        logger.error(f"[ADMIN_AUTH_ERROR] Error during authentication: {str(e)}")
        print(f"[ADMIN_AUTH_ERROR] Exception: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'An error occurred during authentication: {str(e)}'
        }, status=500)
"""
Error handling utilities for PrimePath Routine Test app
Provides robust error handling and logging for all operations
"""
import logging
import traceback
from functools import wraps
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import IntegrityError, DatabaseError

# Configure logger
logger = logging.getLogger('primepath_routinetest')

class RoutineTestError(Exception):
    """Base exception for routine test app"""
    pass

class SessionError(RoutineTestError):
    """Exception for session-related errors"""
    pass

class ExamError(RoutineTestError):
    """Exception for exam-related errors"""
    pass

class GradingError(RoutineTestError):
    """Exception for grading-related errors"""
    pass

def handle_view_errors(view_func):
    """
    Decorator to handle errors in view functions
    Returns appropriate error responses based on exception type
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except ObjectDoesNotExist as e:
            logger.warning(f"Object not found in {view_func.__name__}: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Requested resource not found',
                    'details': str(e)
                }, status=404)
            return render(request, 'primepath_routinetest/error.html', {
                'error_title': 'Not Found',
                'error_message': 'The requested resource was not found.',
                'error_code': 404
            }, status=404)
            
        except ValidationError as e:
            logger.warning(f"Validation error in {view_func.__name__}: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Validation failed',
                    'details': e.message_dict if hasattr(e, 'message_dict') else str(e)
                }, status=400)
            return render(request, 'primepath_routinetest/error.html', {
                'error_title': 'Invalid Data',
                'error_message': 'The submitted data is invalid.',
                'error_details': str(e),
                'error_code': 400
            }, status=400)
            
        except IntegrityError as e:
            logger.error(f"Database integrity error in {view_func.__name__}: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Data integrity error',
                    'details': 'This operation would violate data constraints'
                }, status=409)
            return render(request, 'primepath_routinetest/error.html', {
                'error_title': 'Data Conflict',
                'error_message': 'This operation conflicts with existing data.',
                'error_code': 409
            }, status=409)
            
        except DatabaseError as e:
            logger.error(f"Database error in {view_func.__name__}: {str(e)}\n{traceback.format_exc()}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Database error occurred',
                    'details': 'Please try again later'
                }, status=500)
            return render(request, 'primepath_routinetest/error.html', {
                'error_title': 'Database Error',
                'error_message': 'A database error occurred. Please try again later.',
                'error_code': 500
            }, status=500)
            
        except RoutineTestError as e:
            logger.error(f"Application error in {view_func.__name__}: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': str(e),
                    'error_type': e.__class__.__name__
                }, status=400)
            return render(request, 'primepath_routinetest/error.html', {
                'error_title': 'Application Error',
                'error_message': str(e),
                'error_code': 400
            }, status=400)
            
        except Exception as e:
            logger.error(f"Unexpected error in {view_func.__name__}: {str(e)}\n{traceback.format_exc()}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'An unexpected error occurred',
                    'details': str(e) if logger.isEnabledFor(logging.DEBUG) else 'Please contact support'
                }, status=500)
            return render(request, 'primepath_routinetest/error.html', {
                'error_title': 'Unexpected Error',
                'error_message': 'An unexpected error occurred. Please try again.',
                'error_code': 500
            }, status=500)
    
    return wrapped_view

def handle_api_errors(api_func):
    """
    Decorator specifically for API endpoints
    Always returns JSON responses
    """
    @wraps(api_func)
    def wrapped_api(request, *args, **kwargs):
        try:
            return api_func(request, *args, **kwargs)
        except ObjectDoesNotExist as e:
            logger.warning(f"API: Object not found in {api_func.__name__}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Resource not found',
                'error_code': 'NOT_FOUND'
            }, status=404)
            
        except ValidationError as e:
            logger.warning(f"API: Validation error in {api_func.__name__}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Validation failed',
                'error_code': 'VALIDATION_ERROR',
                'details': e.message_dict if hasattr(e, 'message_dict') else str(e)
            }, status=400)
            
        except IntegrityError as e:
            logger.error(f"API: Integrity error in {api_func.__name__}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Data integrity violation',
                'error_code': 'INTEGRITY_ERROR'
            }, status=409)
            
        except DatabaseError as e:
            logger.error(f"API: Database error in {api_func.__name__}: {str(e)}\n{traceback.format_exc()}")
            return JsonResponse({
                'success': False,
                'error': 'Database error',
                'error_code': 'DATABASE_ERROR'
            }, status=500)
            
        except RoutineTestError as e:
            logger.error(f"API: Application error in {api_func.__name__}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e),
                'error_code': e.__class__.__name__.upper()
            }, status=400)
            
        except Exception as e:
            logger.error(f"API: Unexpected error in {api_func.__name__}: {str(e)}\n{traceback.format_exc()}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error',
                'error_code': 'INTERNAL_ERROR',
                'details': str(e) if logger.isEnabledFor(logging.DEBUG) else None
            }, status=500)
    
    return wrapped_api

def safe_get_or_404(model, **kwargs):
    """
    Safely get an object or raise a proper 404 error
    """
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        raise ObjectDoesNotExist(f"{model.__name__} not found with criteria: {kwargs}")
    except Exception as e:
        logger.error(f"Error retrieving {model.__name__}: {str(e)}")
        raise DatabaseError(f"Failed to retrieve {model.__name__}")

def safe_bulk_create(model, objects, **kwargs):
    """
    Safely bulk create objects with error handling
    """
    try:
        return model.objects.bulk_create(objects, **kwargs)
    except IntegrityError as e:
        logger.error(f"Integrity error during bulk create for {model.__name__}: {str(e)}")
        raise IntegrityError(f"Failed to create {model.__name__} objects: Data integrity violation")
    except Exception as e:
        logger.error(f"Error during bulk create for {model.__name__}: {str(e)}")
        raise DatabaseError(f"Failed to create {model.__name__} objects")

def log_activity(user, action, details=None):
    """
    Log user activity for audit purposes
    """
    try:
        logger.info(f"USER_ACTIVITY: User={user.username if user else 'Anonymous'}, "
                   f"Action={action}, Details={details}")
    except Exception as e:
        logger.error(f"Failed to log activity: {str(e)}")

def validate_session_access(session, user):
    """
    Validate that a user has access to a session
    """
    if not session:
        raise SessionError("Session not found")
    
    # Add your access control logic here
    # For example, check if user is the student or a teacher
    if hasattr(session, 'student') and session.student != user:
        if not user.is_staff and not user.groups.filter(name='Teachers').exists():
            raise SessionError("You don't have permission to access this session")
    
    return True

def validate_exam_access(exam, user):
    """
    Validate that a user has access to an exam
    """
    if not exam:
        raise ExamError("Exam not found")
    
    # Add your access control logic here
    if not exam.is_active and not user.is_staff:
        raise ExamError("This exam is not currently available")
    
    return True
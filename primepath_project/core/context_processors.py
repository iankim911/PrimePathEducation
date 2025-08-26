"""
Context Processors for PrimePath
Makes configuration and common data available to all templates
Created: August 26, 2025

Phase 3 Enhancement: Data Configuration Context
Provides dynamic data constraints and validation rules to templates
"""

from .services.config_service import ConfigurationService, get_config_for_frontend
import json
import logging

logger = logging.getLogger(__name__)


def config_context(request):
    """
    Make configuration service available to all templates
    Provides dynamic configuration without hardcoding
    """
    try:
        context = {
            'config': {
                'current_year': ConfigurationService.get_current_year(),
                'academic_year': ConfigurationService.get_current_academic_year(),
                'base_url': ConfigurationService.get_base_url(request),
                'api_base_url': ConfigurationService.get_api_base_url(request),
                'media_url': ConfigurationService.get_media_url(request),
                'static_url': ConfigurationService.get_static_url(request),
                'environment': ConfigurationService.get_environment(),
                'debug_mode': ConfigurationService.get_feature_flag('DEBUG'),
            },
            # For JavaScript use
            'config_json': get_config_for_frontend(request),
        }
        
        logger.debug(f"[CONTEXT_PROCESSOR] Configuration context provided for {request.path}")
        return context
        
    except Exception as e:
        logger.error(f"[CONTEXT_PROCESSOR] Error providing configuration context: {e}")
        # Return empty context on error to prevent template failures
        return {
            'config': {
                'current_year': 2025,  # Fallback
                'academic_year': '2025-2026',  # Fallback
                'base_url': 'http://127.0.0.1:8000',  # Fallback
                'api_base_url': 'http://127.0.0.1:8000/api',  # Fallback
                'environment': 'development',
                'debug_mode': True,
            },
            'config_json': {},
        }


def user_context(request):
    """
    Add user-specific context to templates
    Provides user role information and permissions
    """
    if not request.user.is_authenticated:
        return {
            'user_role': 'anonymous',
            'is_teacher': False,
            'is_student': False,
            'is_admin': False,
            'can_manage_curriculum': False,
            'can_create_exams': False,
        }
    
    try:
        user = request.user
        
        # Determine user role
        user_role = 'user'
        is_teacher = False
        is_student = False
        is_admin = user.is_staff or user.is_superuser
        
        # Check for teacher profile
        if hasattr(user, 'teacher'):
            is_teacher = True
            user_role = 'teacher'
            if user.teacher.is_head_teacher:
                user_role = 'head_teacher'
        
        # Check for student profile
        if hasattr(user, 'primepath_student_profile'):
            is_student = True
            user_role = 'student'
        
        # Permissions based on role
        can_manage_curriculum = is_admin or (is_teacher and hasattr(user, 'teacher') and user.teacher.is_head_teacher)
        can_create_exams = is_admin or is_teacher
        
        context = {
            'user_role': user_role,
            'is_teacher': is_teacher,
            'is_student': is_student,
            'is_admin': is_admin,
            'can_manage_curriculum': can_manage_curriculum,
            'can_create_exams': can_create_exams,
            'user_display_name': user.get_full_name() or user.username,
        }
        
        logger.debug(f"[CONTEXT_PROCESSOR] User context provided: {user_role} for {user.username}")
        return context
        
    except Exception as e:
        logger.error(f"[CONTEXT_PROCESSOR] Error providing user context: {e}")
        # Return safe defaults on error
        return {
            'user_role': 'user',
            'is_teacher': False,
            'is_student': False,
            'is_admin': False,
            'can_manage_curriculum': False,
            'can_create_exams': False,
            'user_display_name': 'User',
        }


def feature_flags_context(request):
    """
    Add feature flags to templates
    Allows conditional rendering based on features
    """
    try:
        context = {
            'features': {
                'use_v2_templates': ConfigurationService.get_feature_flag('USE_V2_TEMPLATES', False),
                'allow_audio': ConfigurationService.get_feature_flag('ALLOW_AUDIO', True),
                'allow_pdf': ConfigurationService.get_feature_flag('ALLOW_PDF', True),
                'show_debug_info': ConfigurationService.get_feature_flag('SHOW_DEBUG_INFO', False),
                'enable_social_login': ConfigurationService.get_feature_flag('ENABLE_SOCIAL_LOGIN', False),
                'maintenance_mode': ConfigurationService.get_feature_flag('MAINTENANCE_MODE', False),
            }
        }
        
        return context
        
    except Exception as e:
        logger.error(f"[CONTEXT_PROCESSOR] Error providing feature flags context: {e}")
        return {
            'features': {
                'use_v2_templates': False,
                'allow_audio': True,
                'allow_pdf': True,
                'show_debug_info': False,
                'enable_social_login': False,
                'maintenance_mode': False,
            }
        }


def app_info_context(request):
    """
    Add application information to templates
    Provides app name, version, etc.
    """
    try:
        context = {
            'app_info': {
                'name': 'PrimePath',
                'version': '2.0',
                'description': 'Comprehensive Education Assessment Platform',
                'copyright_year': ConfigurationService.get_current_year(),
                'support_email': 'support@primepath.education',
                'build_date': '2025-08-26',
            }
        }
        
        return context
        
    except Exception as e:
        logger.error(f"[CONTEXT_PROCESSOR] Error providing app info context: {e}")
        return {
            'app_info': {
                'name': 'PrimePath',
                'version': '2.0',
                'description': 'Education Assessment Platform',
                'copyright_year': 2025,
                'support_email': 'support@example.com',
                'build_date': '2025-08-26',
            }
        }


def data_config_context(request):
    """
    Add data configuration to templates - Phase 3 Enhancement
    Provides dynamic field constraints, validation rules, and business logic
    """
    try:
        from .services.data_service import DataService
        
        # Get all data configurations
        data_config = {
            'user_fields': DataService.get_user_field_lengths(),
            'student_profile': DataService.get_student_profile_constraints(),
            'teacher_profile': DataService.get_teacher_profile_constraints(),
            'exam_constraints': DataService.get_exam_constraints(),
            'question_constraints': DataService.get_question_constraints(),
            'pagination': DataService.get_pagination_settings(),
            'validation': DataService.get_validation_rules(),
            'business_rules': DataService.get_business_rules(),
            'file_upload': DataService.get_file_upload_constraints(),
        }
        
        # Make available as both template variable and JavaScript
        context = {
            'data_config': data_config,
            'data_config_json': json.dumps(data_config, default=str),
        }
        
        logger.debug(f"[DATA_CONFIG_PROCESSOR] Data configuration provided for {request.path}")
        return context
        
    except Exception as e:
        logger.error(f"[DATA_CONFIG_PROCESSOR] Error providing data configuration: {e}")
        # Return safe fallbacks on error
        fallback_config = {
            'user_fields': {'username_max_length': 150, 'email_max_length': 254},
            'student_profile': {'name_max_length': 100, 'student_id_max_length': 20},
            'pagination': {'default_page_size': 25, 'max_page_size': 100},
            'validation': {'password_min_length': 8, 'phone_number_formats': []},
            'business_rules': {'max_concurrent_sessions': 3, 'session_timeout_minutes': 120},
            'file_upload': {'pdf_max_size_mb': 10, 'audio_max_size_mb': 50},
        }
        
        return {
            'data_config': fallback_config,
            'data_config_json': json.dumps(fallback_config),
        }
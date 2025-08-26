"""
Data Configuration Service
Centralized data layer configuration and constraint management
Created: August 26, 2025

This service provides:
- Dynamic field length constraints
- Configurable pagination settings
- Business rule constraints
- Data validation rules
- Environment-based data settings
"""

import os
from django.conf import settings
from django.core.cache import cache
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class DataService:
    """
    Central data configuration service for managing constraints and business rules
    Eliminates hardcoded values throughout the data layer
    """
    
    # Cache configuration
    CACHE_PREFIX = 'data_config:'
    CACHE_TIMEOUT = 3600  # 1 hour
    
    # Environment detection
    ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development' if settings.DEBUG else 'production')
    
    @classmethod
    def _get_cached_config(cls, config_key, default_value, cache_timeout=None):
        """Get configuration value with caching"""
        cache_key = f"{cls.CACHE_PREFIX}{config_key}"
        cached_value = cache.get(cache_key)
        
        if cached_value is not None:
            return cached_value
        
        # Get from environment or use default
        env_key = config_key.upper().replace('.', '_')
        env_value = os.environ.get(env_key)
        
        if env_value is not None:
            # Try to convert to appropriate type
            try:
                if isinstance(default_value, int):
                    value = int(env_value)
                elif isinstance(default_value, float):
                    value = float(env_value)
                elif isinstance(default_value, bool):
                    value = env_value.lower() in ('true', '1', 'yes', 'on')
                elif isinstance(default_value, Decimal):
                    value = Decimal(env_value)
                else:
                    value = env_value
            except (ValueError, TypeError):
                logger.warning(f"[DATA_CONFIG] Invalid value for {env_key}: {env_value}, using default: {default_value}")
                value = default_value
        else:
            value = default_value
        
        # Cache the result
        cache_timeout = cache_timeout or cls.CACHE_TIMEOUT
        cache.set(cache_key, value, timeout=cache_timeout)
        
        logger.debug(f"[DATA_CONFIG] {config_key} = {value} (cached)")
        return value
    
    # =========================================================================
    # USER AND PROFILE CONSTRAINTS
    # =========================================================================
    
    @classmethod
    def get_user_field_lengths(cls):
        """Get user model field length constraints"""
        return {
            'username_max_length': cls._get_cached_config('user.username_max_length', 150),
            'email_max_length': cls._get_cached_config('user.email_max_length', 254),
            'first_name_max_length': cls._get_cached_config('user.first_name_max_length', 30),
            'last_name_max_length': cls._get_cached_config('user.last_name_max_length', 150),
            'full_name_max_length': cls._get_cached_config('user.full_name_max_length', 200),
        }
    
    @classmethod
    def get_student_profile_constraints(cls):
        """Get student profile constraints"""
        return {
            'name_max_length': cls._get_cached_config('student.name_max_length', 100),
            'student_id_max_length': cls._get_cached_config('student.student_id_max_length', 20),
            'phone_max_length': cls._get_cached_config('student.phone_max_length', 20),
            'grade_max_length': cls._get_cached_config('student.grade_max_length', 10),
            'program_max_length': cls._get_cached_config('student.program_max_length', 100),
            'class_code_max_length': cls._get_cached_config('student.class_code_max_length', 50),
        }
    
    @classmethod
    def get_teacher_profile_constraints(cls):
        """Get teacher profile constraints"""
        return {
            'name_max_length': cls._get_cached_config('teacher.name_max_length', 100),
            'department_max_length': cls._get_cached_config('teacher.department_max_length', 100),
            'title_max_length': cls._get_cached_config('teacher.title_max_length', 50),
        }
    
    # =========================================================================
    # EXAM AND QUESTION CONSTRAINTS
    # =========================================================================
    
    @classmethod
    def get_exam_constraints(cls):
        """Get exam model constraints"""
        return {
            'name_max_length': cls._get_cached_config('exam.name_max_length', 200),
            'description_max_length': cls._get_cached_config('exam.description_max_length', 1000),
            'max_questions_per_exam': cls._get_cached_config('exam.max_questions_per_exam', 200),
            'min_questions_per_exam': cls._get_cached_config('exam.min_questions_per_exam', 1),
            'default_points_per_question': cls._get_cached_config('exam.default_points_per_question', 1),
            'max_points_per_question': cls._get_cached_config('exam.max_points_per_question', 10),
            'default_time_limit_minutes': cls._get_cached_config('exam.default_time_limit_minutes', 60),
            'max_time_limit_minutes': cls._get_cached_config('exam.max_time_limit_minutes', 300),  # 5 hours
        }
    
    @classmethod
    def get_question_constraints(cls):
        """Get question model constraints"""
        return {
            'question_text_max_length': cls._get_cached_config('question.text_max_length', 2000),
            'answer_choice_max_length': cls._get_cached_config('question.answer_choice_max_length', 500),
            'short_answer_max_length': cls._get_cached_config('question.short_answer_max_length', 1000),
            'explanation_max_length': cls._get_cached_config('question.explanation_max_length', 2000),
            'max_answer_choices': cls._get_cached_config('question.max_answer_choices', 6),
            'min_answer_choices': cls._get_cached_config('question.min_answer_choices', 2),
        }
    
    @classmethod
    def get_audio_file_constraints(cls):
        """Get audio file constraints"""
        return {
            'name_max_length': cls._get_cached_config('audio.name_max_length', 200),
            'file_path_max_length': cls._get_cached_config('audio.file_path_max_length', 500),
            'max_file_size_mb': cls._get_cached_config('audio.max_file_size_mb', 50),
            'allowed_extensions': cls._get_cached_config('audio.allowed_extensions', ['mp3', 'wav', 'm4a', 'ogg']),
        }
    
    # =========================================================================
    # PAGINATION AND QUERY LIMITS
    # =========================================================================
    
    @classmethod
    def get_pagination_settings(cls):
        """Get pagination settings for different contexts"""
        base_settings = {
            'default_page_size': cls._get_cached_config('pagination.default_page_size', 25),
            'max_page_size': cls._get_cached_config('pagination.max_page_size', 100),
            'min_page_size': cls._get_cached_config('pagination.min_page_size', 5),
        }
        
        # Context-specific pagination
        context_settings = {
            'students_per_page': cls._get_cached_config('pagination.students_per_page', base_settings['default_page_size']),
            'teachers_per_page': cls._get_cached_config('pagination.teachers_per_page', base_settings['default_page_size']),
            'exams_per_page': cls._get_cached_config('pagination.exams_per_page', 20),
            'questions_per_page': cls._get_cached_config('pagination.questions_per_page', 15),
            'sessions_per_page': cls._get_cached_config('pagination.sessions_per_page', 30),
            'classes_per_page': cls._get_cached_config('pagination.classes_per_page', 20),
        }
        
        return {**base_settings, **context_settings}
    
    @classmethod
    def get_query_limits(cls):
        """Get query limits for performance optimization"""
        return {
            'dashboard_recent_limit': cls._get_cached_config('query.dashboard_recent_limit', 10),
            'analytics_batch_size': cls._get_cached_config('query.analytics_batch_size', 1000),
            'search_results_limit': cls._get_cached_config('query.search_results_limit', 50),
            'autocomplete_limit': cls._get_cached_config('query.autocomplete_limit', 10),
            'export_batch_size': cls._get_cached_config('query.export_batch_size', 500),
            'bulk_operation_batch_size': cls._get_cached_config('query.bulk_operation_batch_size', 100),
        }
    
    # =========================================================================
    # VALIDATION RULES
    # =========================================================================
    
    @classmethod
    def get_validation_rules(cls):
        """Get validation rules and constraints"""
        return {
            'password_min_length': cls._get_cached_config('validation.password_min_length', 8),
            'password_max_length': cls._get_cached_config('validation.password_max_length', 128),
            'username_min_length': cls._get_cached_config('validation.username_min_length', 3),
            'phone_number_formats': cls._get_cached_config('validation.phone_number_formats', [
                r'^\d{3}-\d{3,4}-\d{4}$',  # Korean format
                r'^\+\d{1,3}-\d{3,4}-\d{4}$',  # International
                r'^\d{10,11}$'  # Simple numeric
            ]),
            'email_max_length': cls._get_cached_config('validation.email_max_length', 254),
            'student_id_pattern': cls._get_cached_config('validation.student_id_pattern', r'^[A-Za-z0-9_-]+$'),
            'grade_choices': cls._get_cached_config('validation.grade_choices', [
                '1', '2', '3', '4', '5', '6',  # Elementary
                '7', '8', '9',  # Middle School
                '10', '11', '12'  # High School
            ]),
        }
    
    # =========================================================================
    # BUSINESS RULES
    # =========================================================================
    
    @classmethod
    def get_business_rules(cls):
        """Get business logic constraints"""
        return {
            'max_concurrent_sessions': cls._get_cached_config('business.max_concurrent_sessions', 3),
            'session_timeout_minutes': cls._get_cached_config('business.session_timeout_minutes', 120),
            'exam_attempt_limit': cls._get_cached_config('business.exam_attempt_limit', 3),
            'grade_pass_threshold': cls._get_cached_config('business.grade_pass_threshold', 0.7),
            'placement_score_ranges': {
                'beginner': cls._get_cached_config('business.beginner_max_score', 60),
                'intermediate': cls._get_cached_config('business.intermediate_max_score', 80),
                'advanced': cls._get_cached_config('business.advanced_min_score', 81),
            },
            'auto_save_interval_seconds': cls._get_cached_config('business.auto_save_interval_seconds', 30),
        }
    
    # =========================================================================
    # FILE UPLOAD CONSTRAINTS
    # =========================================================================
    
    @classmethod
    def get_file_upload_constraints(cls):
        """Get file upload constraints"""
        return {
            'pdf_max_size_mb': cls._get_cached_config('upload.pdf_max_size_mb', 10),
            'audio_max_size_mb': cls._get_cached_config('upload.audio_max_size_mb', 50),
            'image_max_size_mb': cls._get_cached_config('upload.image_max_size_mb', 5),
            'allowed_pdf_extensions': cls._get_cached_config('upload.allowed_pdf_extensions', ['pdf']),
            'allowed_audio_extensions': cls._get_cached_config('upload.allowed_audio_extensions', ['mp3', 'wav', 'm4a', 'ogg']),
            'allowed_image_extensions': cls._get_cached_config('upload.allowed_image_extensions', ['jpg', 'jpeg', 'png', 'gif']),
            'max_files_per_upload': cls._get_cached_config('upload.max_files_per_upload', 10),
        }
    
    # =========================================================================
    # PERFORMANCE SETTINGS
    # =========================================================================
    
    @classmethod
    def get_performance_settings(cls):
        """Get performance-related configuration"""
        return {
            'database_connection_timeout': cls._get_cached_config('performance.db_connection_timeout', 30),
            'cache_timeout_seconds': cls._get_cached_config('performance.cache_timeout_seconds', 300),
            'static_file_cache_seconds': cls._get_cached_config('performance.static_file_cache_seconds', 86400),  # 1 day
            'api_request_timeout': cls._get_cached_config('performance.api_request_timeout', 30),
            'batch_processing_size': cls._get_cached_config('performance.batch_processing_size', 1000),
            'concurrent_request_limit': cls._get_cached_config('performance.concurrent_request_limit', 100),
        }
    
    # =========================================================================
    # ENVIRONMENT-SPECIFIC OVERRIDES
    # =========================================================================
    
    @classmethod
    def get_environment_overrides(cls):
        """Get environment-specific overrides"""
        if cls.ENVIRONMENT == 'production':
            return {
                'debug_enabled': False,
                'verbose_logging': False,
                'cache_timeout_multiplier': 2.0,
                'strict_validation': True,
            }
        elif cls.ENVIRONMENT == 'staging':
            return {
                'debug_enabled': True,
                'verbose_logging': True,
                'cache_timeout_multiplier': 1.0,
                'strict_validation': True,
            }
        else:  # development
            return {
                'debug_enabled': True,
                'verbose_logging': True,
                'cache_timeout_multiplier': 0.5,
                'strict_validation': False,
            }
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    @classmethod
    def get_all_configurations(cls):
        """Get all data configurations as a single dictionary"""
        all_config = {
            'user_fields': cls.get_user_field_lengths(),
            'student_profile': cls.get_student_profile_constraints(),
            'teacher_profile': cls.get_teacher_profile_constraints(),
            'exam_constraints': cls.get_exam_constraints(),
            'question_constraints': cls.get_question_constraints(),
            'audio_constraints': cls.get_audio_file_constraints(),
            'pagination': cls.get_pagination_settings(),
            'query_limits': cls.get_query_limits(),
            'validation': cls.get_validation_rules(),
            'business_rules': cls.get_business_rules(),
            'file_uploads': cls.get_file_upload_constraints(),
            'performance': cls.get_performance_settings(),
            'environment': cls.get_environment_overrides(),
        }
        
        logger.info(f"[DATA_CONFIG] All configurations loaded for environment: {cls.ENVIRONMENT}")
        return all_config
    
    @classmethod
    def clear_cache(cls):
        """Clear all cached configuration values"""
        # Get all cache keys with our prefix
        cache_pattern = f"{cls.CACHE_PREFIX}*"
        
        # Note: This is a simplified cache clear
        # In production, you might want a more sophisticated cache invalidation
        try:
            cache.clear()
            logger.info("[DATA_CONFIG] Cache cleared successfully")
            return True
        except Exception as e:
            logger.error(f"[DATA_CONFIG] Error clearing cache: {e}")
            return False
    
    @classmethod
    def validate_configuration(cls):
        """Validate all configuration values"""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Test all configuration loading
            all_config = cls.get_all_configurations()
            
            # Validate pagination settings
            pagination = all_config['pagination']
            if pagination['min_page_size'] >= pagination['max_page_size']:
                validation_results['errors'].append("min_page_size must be less than max_page_size")
            
            # Validate exam constraints
            exam = all_config['exam_constraints']
            if exam['min_questions_per_exam'] >= exam['max_questions_per_exam']:
                validation_results['errors'].append("min_questions_per_exam must be less than max_questions_per_exam")
            
            # Validate business rules
            business = all_config['business_rules']
            if business['grade_pass_threshold'] < 0 or business['grade_pass_threshold'] > 1:
                validation_results['errors'].append("grade_pass_threshold must be between 0 and 1")
            
            if validation_results['errors']:
                validation_results['valid'] = False
            
            logger.info(f"[DATA_CONFIG] Configuration validation: {'PASSED' if validation_results['valid'] else 'FAILED'}")
            
        except Exception as e:
            validation_results['valid'] = False
            validation_results['errors'].append(f"Configuration validation error: {str(e)}")
            logger.error(f"[DATA_CONFIG] Validation failed: {e}")
        
        return validation_results


# Utility functions for easy access
def get_pagination_size(context='default'):
    """Get pagination size for a specific context"""
    pagination_settings = DataService.get_pagination_settings()
    context_key = f"{context}_per_page"
    return pagination_settings.get(context_key, pagination_settings['default_page_size'])

def get_field_max_length(model, field):
    """Get maximum length for a specific model field"""
    if model.lower() == 'user':
        constraints = DataService.get_user_field_lengths()
        return constraints.get(f"{field}_max_length")
    elif model.lower() == 'student':
        constraints = DataService.get_student_profile_constraints()
        return constraints.get(f"{field}_max_length")
    elif model.lower() == 'teacher':
        constraints = DataService.get_teacher_profile_constraints()
        return constraints.get(f"{field}_max_length")
    elif model.lower() == 'exam':
        constraints = DataService.get_exam_constraints()
        return constraints.get(f"{field}_max_length")
    elif model.lower() == 'question':
        constraints = DataService.get_question_constraints()
        return constraints.get(f"{field}_max_length")
    elif model.lower() == 'audio':
        constraints = DataService.get_audio_file_constraints()
        return constraints.get(f"{field}_max_length")
    return None

def get_query_limit(context):
    """Get query limit for a specific context"""
    limits = DataService.get_query_limits()
    return limits.get(f"{context}_limit", limits.get('search_results_limit', 50))

def get_business_rule(rule_name):
    """Get a specific business rule value"""
    rules = DataService.get_business_rules()
    return rules.get(rule_name)

def validate_all_data_config():
    """Validate all data configuration"""
    return DataService.validate_configuration()

# Export service for registration
__all__ = ['DataService', 'get_pagination_size', 'get_field_max_length', 'get_query_limit', 'get_business_rule', 'validate_all_data_config']
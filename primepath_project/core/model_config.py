"""
Dynamic Model Configuration Utility
Phase 3: Data Layer Flexibility

This module provides dynamic field constraints and validation rules
for Django models using DataService configuration.
"""

from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


def get_dynamic_max_length(model_name, field_name, default_length=None):
    """
    Get dynamic max_length for model fields using DataService
    
    Args:
        model_name (str): Model name (e.g., 'student', 'teacher', 'exam')
        field_name (str): Field name (e.g., 'name', 'student_id')
        default_length (int): Fallback length if DataService unavailable
        
    Returns:
        int: Maximum length for the field
    """
    try:
        from .services.data_service import get_field_max_length
        dynamic_length = get_field_max_length(model_name, field_name)
        if dynamic_length:
            logger.debug(f"[MODEL_CONFIG] {model_name}.{field_name} max_length: {dynamic_length}")
            return dynamic_length
    except (ImportError, AttributeError):
        logger.debug(f"[MODEL_CONFIG] DataService unavailable, using default for {model_name}.{field_name}")
    
    # Fallback to provided default or calculate sensible default
    if default_length:
        return default_length
        
    # Sensible defaults based on field type
    field_defaults = {
        # Student fields
        'student_id': 20,
        'phone_number': 15,
        'emergency_contact_phone': 15,
        'parent1_phone': 15,
        'parent2_phone': 15,
        'school_name': 200,
        'parent1_name': 100,
        'parent2_name': 100,
        'grade': 5,
        'gender': 1,
        
        # Teacher fields
        'name': 100,
        'department': 100,
        'title': 50,
        
        # Exam fields
        'exam_name': 200,
        'description': 1000,
        
        # Question fields
        'question_text': 2000,
        'answer_choice': 500,
        'short_answer': 1000,
        'explanation': 2000,
        
        # Audio fields
        'audio_name': 200,
        'file_path': 500,
        
        # Default fallback
        'default': 255
    }
    
    return field_defaults.get(field_name, field_defaults['default'])


def get_dynamic_choices(model_name, field_name, default_choices=None):
    """
    Get dynamic choices for model fields using DataService
    
    Args:
        model_name (str): Model name
        field_name (str): Field name
        default_choices (list): Fallback choices if DataService unavailable
        
    Returns:
        list: Choices for the field
    """
    try:
        from .services.data_service import DataService
        validation_rules = DataService.get_validation_rules()
        
        if field_name == 'grade' and model_name == 'student':
            grades = validation_rules['grade_choices']
            # Convert to Django choices format
            grade_choices = []
            for grade in grades:
                if grade == 'K':
                    grade_choices.append(('K', 'Kindergarten'))
                elif grade.isdigit():
                    grade_choices.append((grade, f'Grade {grade}'))
                else:
                    grade_choices.append((grade, grade))
            
            # Add special grades
            grade_choices.extend([
                ('UNI', 'University'),
                ('ADULT', 'Adult Student')
            ])
            
            logger.debug(f"[MODEL_CONFIG] Dynamic grade choices: {len(grade_choices)} options")
            return grade_choices
            
    except (ImportError, AttributeError) as e:
        logger.debug(f"[MODEL_CONFIG] DataService unavailable for choices: {e}")
    
    # Return provided defaults or sensible defaults
    if default_choices:
        return default_choices
    
    # Default choices for common fields
    if field_name == 'grade':
        return [
            ('K', 'Kindergarten'),
            ('1', 'Grade 1'), ('2', 'Grade 2'), ('3', 'Grade 3'),
            ('4', 'Grade 4'), ('5', 'Grade 5'), ('6', 'Grade 6'),
            ('7', 'Grade 7'), ('8', 'Grade 8'), ('9', 'Grade 9'),
            ('10', 'Grade 10'), ('11', 'Grade 11'), ('12', 'Grade 12'),
            ('UNI', 'University'), ('ADULT', 'Adult Student')
        ]
    elif field_name == 'gender':
        return [
            ('M', 'Male'), ('F', 'Female'), ('O', 'Other'), ('P', 'Prefer not to say')
        ]
    
    return []


def get_dynamic_validators(model_name, field_name, default_validators=None):
    """
    Get dynamic validators for model fields using DataService
    
    Args:
        model_name (str): Model name
        field_name (str): Field name
        default_validators (list): Fallback validators if DataService unavailable
        
    Returns:
        list: Validators for the field
    """
    try:
        from .services.data_service import DataService
        validation_rules = DataService.get_validation_rules()
        
        validators = []
        
        # Phone number validation
        if 'phone' in field_name.lower():
            phone_patterns = validation_rules.get('phone_number_formats', [])
            if phone_patterns:
                # Use first pattern as primary validator
                primary_pattern = phone_patterns[0]
                validators.append(RegexValidator(
                    regex=primary_pattern,
                    message="Phone number must be in valid format"
                ))
                logger.debug(f"[MODEL_CONFIG] Dynamic phone validator for {field_name}")
        
        # Student ID validation
        elif field_name == 'student_id':
            student_pattern = validation_rules.get('student_id_pattern')
            if student_pattern:
                validators.append(RegexValidator(
                    regex=student_pattern,
                    message="Student ID must contain only letters, numbers, underscores, and dashes"
                ))
                logger.debug(f"[MODEL_CONFIG] Dynamic student ID validator")
        
        if validators:
            return validators
            
    except (ImportError, AttributeError) as e:
        logger.debug(f"[MODEL_CONFIG] DataService unavailable for validators: {e}")
    
    # Return provided defaults or sensible defaults
    if default_validators:
        return default_validators
    
    # Default validators for common fields
    if 'phone' in field_name.lower():
        return [RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be valid")]
    elif field_name == 'student_id':
        return [RegexValidator(regex=r'^[A-Za-z0-9_-]+$', message="Student ID must be alphanumeric")]
    
    return []


def get_dynamic_business_constraints():
    """
    Get dynamic business rule constraints using DataService
    
    Returns:
        dict: Business rule constraints
    """
    try:
        from .services.data_service import DataService
        business_rules = DataService.get_business_rules()
        exam_constraints = DataService.get_exam_constraints()
        query_limits = DataService.get_query_limits()
        
        constraints = {
            # Session constraints
            'max_concurrent_sessions': business_rules['max_concurrent_sessions'],
            'session_timeout_minutes': business_rules['session_timeout_minutes'],
            'exam_attempt_limit': business_rules['exam_attempt_limit'],
            
            # Exam constraints
            'max_questions_per_exam': exam_constraints['max_questions_per_exam'],
            'min_questions_per_exam': exam_constraints['min_questions_per_exam'],
            'max_points_per_question': exam_constraints['max_points_per_question'],
            'max_time_limit_minutes': exam_constraints['max_time_limit_minutes'],
            
            # Scoring constraints
            'grade_pass_threshold': business_rules['grade_pass_threshold'],
            'placement_score_ranges': business_rules['placement_score_ranges'],
            
            # Query limits
            'search_results_limit': query_limits['search_results_limit'],
            'dashboard_recent_limit': query_limits['dashboard_recent_limit'],
            'export_batch_size': query_limits['export_batch_size'],
        }
        
        logger.debug(f"[MODEL_CONFIG] Loaded {len(constraints)} business constraints")
        return constraints
        
    except (ImportError, AttributeError):
        logger.debug("[MODEL_CONFIG] DataService unavailable, using default business constraints")
        return {
            'max_concurrent_sessions': 3,
            'session_timeout_minutes': 120,
            'exam_attempt_limit': 3,
            'max_questions_per_exam': 200,
            'min_questions_per_exam': 1,
            'max_points_per_question': 10,
            'max_time_limit_minutes': 300,
            'grade_pass_threshold': 0.7,
            'placement_score_ranges': {
                'beginner': 60,
                'intermediate': 80,
                'advanced': 81
            },
            'search_results_limit': 50,
            'dashboard_recent_limit': 10,
            'export_batch_size': 500,
        }


def get_file_upload_constraints():
    """
    Get dynamic file upload constraints using DataService
    
    Returns:
        dict: File upload constraints
    """
    try:
        from .services.data_service import DataService
        file_constraints = DataService.get_file_upload_constraints()
        
        logger.debug("[MODEL_CONFIG] Loaded dynamic file upload constraints")
        return file_constraints
        
    except (ImportError, AttributeError):
        logger.debug("[MODEL_CONFIG] DataService unavailable, using default file constraints")
        return {
            'pdf_max_size_mb': 10,
            'audio_max_size_mb': 50,
            'image_max_size_mb': 5,
            'allowed_pdf_extensions': ['pdf'],
            'allowed_audio_extensions': ['mp3', 'wav', 'm4a', 'ogg'],
            'allowed_image_extensions': ['jpg', 'jpeg', 'png', 'gif'],
            'max_files_per_upload': 10,
        }


# Convenience functions for common use cases
def student_field_length(field_name):
    """Get max_length for student profile fields"""
    return get_dynamic_max_length('student', field_name)


def teacher_field_length(field_name):
    """Get max_length for teacher profile fields"""
    return get_dynamic_max_length('teacher', field_name)


def exam_field_length(field_name):
    """Get max_length for exam fields"""
    return get_dynamic_max_length('exam', field_name)


def question_field_length(field_name):
    """Get max_length for question fields"""
    return get_dynamic_max_length('question', field_name)


def audio_field_length(field_name):
    """Get max_length for audio file fields"""
    return get_dynamic_max_length('audio', field_name)


# Export functions for easy access
__all__ = [
    'get_dynamic_max_length',
    'get_dynamic_choices',
    'get_dynamic_validators',
    'get_dynamic_business_constraints',
    'get_file_upload_constraints',
    'student_field_length',
    'teacher_field_length',
    'exam_field_length',
    'question_field_length',
    'audio_field_length'
]
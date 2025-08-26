"""
Centralized constants for the PrimePath application.
This eliminates code duplication and provides a single source of truth.

Phase 3 Enhancement: Dynamic configuration using DataService
Many previously hardcoded values now use DataService for environment flexibility
"""

# Academic rank to percentile mapping
ACADEMIC_RANK_PERCENTILES = {
    'TOP_10': 10,
    'TOP_20': 20,
    'TOP_30': 30,
    'TOP_40': 40,
    'TOP_50': 50,
    'BELOW_50': 100,
}

# Reverse mapping for display purposes
PERCENTILE_TO_RANK = {v: k for k, v in ACADEMIC_RANK_PERCENTILES.items()}

# Question type constants
QUESTION_TYPES = {
    'MCQ': 'Multiple Choice',
    'CHECKBOX': 'Select All',
    'SHORT': 'Short Answer',
    'LONG': 'Long Answer',
    'MIXED': 'Mixed',
}

# Dynamic configuration functions using DataService
def get_default_exam_timer():
    """Get default exam timer from DataService"""
    try:
        from .services.data_service import DataService
        return DataService.get_exam_constraints()['default_time_limit_minutes']
    except ImportError:
        return 60  # Fallback for early initialization

def get_default_question_points():
    """Get default question points from DataService"""
    try:
        from .services.data_service import DataService
        return DataService.get_exam_constraints()['default_points_per_question']
    except ImportError:
        return 1  # Fallback for early initialization

def get_max_file_sizes():
    """Get file size limits from DataService"""
    try:
        from .services.data_service import DataService
        constraints = DataService.get_file_upload_constraints()
        return {
            'pdf_mb': constraints['pdf_max_size_mb'],
            'audio_mb': constraints['audio_max_size_mb'],
            'image_mb': constraints['image_max_size_mb'],
            'pdf_bytes': constraints['pdf_max_size_mb'] * 1024 * 1024,
            'audio_bytes': constraints['audio_max_size_mb'] * 1024 * 1024,
            'image_bytes': constraints['image_max_size_mb'] * 1024 * 1024,
        }
    except ImportError:
        return {
            'pdf_mb': 10,
            'audio_mb': 50,
            'image_mb': 5,
            'pdf_bytes': 10 * 1024 * 1024,
            'audio_bytes': 50 * 1024 * 1024,
            'image_bytes': 5 * 1024 * 1024,
        }

def get_allowed_file_extensions():
    """Get allowed file extensions from DataService"""
    try:
        from .services.data_service import DataService
        constraints = DataService.get_file_upload_constraints()
        return {
            'pdf': constraints['allowed_pdf_extensions'],
            'audio': constraints['allowed_audio_extensions'],
            'image': constraints['allowed_image_extensions'],
        }
    except ImportError:
        return {
            'pdf': ['pdf'],
            'audio': ['mp3', 'wav', 'm4a'],
            'image': ['jpg', 'jpeg', 'png', 'gif'],
        }

def get_pagination_settings():
    """Get pagination settings from DataService"""
    try:
        from .services.data_service import DataService
        settings = DataService.get_pagination_settings()
        return {
            'default_page_size': settings['default_page_size'],
            'max_page_size': settings['max_page_size'],
        }
    except ImportError:
        return {
            'default_page_size': 20,
            'max_page_size': 100,
        }

def get_business_rules():
    """Get business rules from DataService"""
    try:
        from .services.data_service import DataService
        rules = DataService.get_business_rules()
        return {
            'session_timeout_hours': rules['session_timeout_minutes'] / 60,
            'min_passing_percentage': rules['grade_pass_threshold'] * 100,
        }
    except ImportError:
        return {
            'session_timeout_hours': 24,
            'min_passing_percentage': 70,
        }

def get_validation_rules():
    """Get validation rules from DataService"""
    try:
        from .services.data_service import DataService
        rules = DataService.get_validation_rules()
        grade_choices = rules['grade_choices']
        return {
            'min_grade': int(min(grade_choices)),
            'max_grade': int(max(grade_choices)),
        }
    except ImportError:
        return {
            'min_grade': 1,
            'max_grade': 12,
        }

# Backward compatibility - these will use DataService when available
try:
    from .services.data_service import DataService
    
    # Dynamic values
    _exam_constraints = DataService.get_exam_constraints()
    _file_constraints = DataService.get_file_upload_constraints()
    _pagination = DataService.get_pagination_settings()
    _business_rules = DataService.get_business_rules()
    _validation_rules = DataService.get_validation_rules()
    
    # Override with dynamic values
    DEFAULT_EXAM_TIMER_MINUTES = _exam_constraints['default_time_limit_minutes']
    DEFAULT_OPTIONS_COUNT = _exam_constraints.get('default_answer_choices', 5)  # Keep as fallback
    DEFAULT_QUESTION_POINTS = _exam_constraints['default_points_per_question']
    
    # File settings from DataService
    MAX_FILE_SIZE_MB = _file_constraints['pdf_max_size_mb']  # Default to PDF size
    ALLOWED_PDF_EXTENSIONS = _file_constraints['allowed_pdf_extensions']
    ALLOWED_AUDIO_EXTENSIONS = _file_constraints['allowed_audio_extensions']
    ALLOWED_IMAGE_EXTENSIONS = _file_constraints['allowed_image_extensions']
    
    # File size limits in bytes
    MAX_PDF_SIZE = _file_constraints['pdf_max_size_mb'] * 1024 * 1024
    MAX_AUDIO_SIZE = _file_constraints['audio_max_size_mb'] * 1024 * 1024
    MAX_IMAGE_SIZE = _file_constraints['image_max_size_mb'] * 1024 * 1024
    
    # Session and business rules
    SESSION_TIMEOUT_HOURS = _business_rules['session_timeout_minutes'] / 60
    MIN_PASSING_PERCENTAGE = _business_rules['grade_pass_threshold'] * 100
    
    # Validation rules
    grade_choices = _validation_rules['grade_choices']
    MIN_GRADE = int(min(grade_choices))
    MAX_GRADE = int(max(grade_choices))
    
    # Pagination from DataService
    DEFAULT_PAGE_SIZE = _pagination['default_page_size']
    MAX_PAGE_SIZE = _pagination['max_page_size']
    
    # Performance settings
    _performance = DataService.get_performance_settings()
    CACHE_TTL_SECONDS = _performance['cache_timeout_seconds']
    API_RATE_LIMIT_PER_MINUTE = _performance.get('api_requests_per_minute', 60)
    API_RATE_LIMIT_PER_HOUR = _performance.get('api_requests_per_hour', 1000)
    
    print("[CONSTANTS] DataService integration active - using dynamic configuration")
    
except ImportError:
    # Fallback values for early initialization or if DataService not available
    print("[CONSTANTS] Using fallback constants - DataService not available")
    
    # Default values (fallbacks)
    DEFAULT_EXAM_TIMER_MINUTES = 60
    DEFAULT_OPTIONS_COUNT = 5
    DEFAULT_QUESTION_POINTS = 1
    
    # File upload settings (fallbacks)
    MAX_FILE_SIZE_MB = 10
    ALLOWED_PDF_EXTENSIONS = ['pdf']
    ALLOWED_AUDIO_EXTENSIONS = ['mp3', 'wav', 'm4a']
    ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']
    
    # File size limits in bytes (fallbacks)
    MAX_PDF_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_AUDIO_SIZE = 50 * 1024 * 1024  # 50MB
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
    
    # Session settings (fallbacks)
    SESSION_TIMEOUT_HOURS = 24
    MIN_PASSING_PERCENTAGE = 70
    
    # Grade limits (fallbacks)
    MIN_GRADE = 1
    MAX_GRADE = 12
    
    # Pagination (fallbacks)
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # Cache settings (fallbacks)
    CACHE_TTL_SECONDS = 3600  # 1 hour
    API_RATE_LIMIT_PER_MINUTE = 60
    API_RATE_LIMIT_PER_HOUR = 1000

# Static cache keys (these don't need to be dynamic)
CURRICULUM_CACHE_KEY_PREFIX = 'curriculum_'
EXAM_CACHE_KEY_PREFIX = 'exam_'

# Email settings (these can remain static for now)
ADMIN_EMAIL_NOTIFICATIONS = True
STUDENT_EMAIL_NOTIFICATIONS = False

# Feature flags (these can remain static for now)
FEATURE_DIFFICULTY_ADJUSTMENT = True
FEATURE_AUDIO_SUPPORT = True
FEATURE_LONG_ANSWER_QUESTIONS = True
FEATURE_AUTO_GRADING = True
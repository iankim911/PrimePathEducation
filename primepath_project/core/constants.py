"""
Centralized constants for the PrimePath application.
This eliminates code duplication and provides a single source of truth.
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

# Default values
DEFAULT_EXAM_TIMER_MINUTES = 60
DEFAULT_OPTIONS_COUNT = 5
DEFAULT_QUESTION_POINTS = 1

# File upload settings
MAX_FILE_SIZE_MB = 10
ALLOWED_PDF_EXTENSIONS = ['pdf']
ALLOWED_AUDIO_EXTENSIONS = ['mp3', 'wav', 'm4a']
ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']

# File size limits in bytes
MAX_PDF_SIZE = 10 * 1024 * 1024  # 10MB
MAX_AUDIO_SIZE = 50 * 1024 * 1024  # 50MB
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

# Session settings
SESSION_TIMEOUT_HOURS = 24
MIN_PASSING_PERCENTAGE = 70

# Grade limits
MIN_GRADE = 1
MAX_GRADE = 12

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Cache settings
CACHE_TTL_SECONDS = 3600  # 1 hour
CURRICULUM_CACHE_KEY_PREFIX = 'curriculum_'
EXAM_CACHE_KEY_PREFIX = 'exam_'

# API rate limiting
API_RATE_LIMIT_PER_MINUTE = 60
API_RATE_LIMIT_PER_HOUR = 1000

# Email settings
ADMIN_EMAIL_NOTIFICATIONS = True
STUDENT_EMAIL_NOTIFICATIONS = False

# Feature flags
FEATURE_DIFFICULTY_ADJUSTMENT = True
FEATURE_AUDIO_SUPPORT = True
FEATURE_LONG_ANSWER_QUESTIONS = True
FEATURE_AUTO_GRADING = True
"""
RoutineTest Constants and Configuration
Defines curriculum whitelist and naming conventions for RoutineTest
"""

# RoutineTest curriculum whitelist - defines which curriculum levels are available for routine testing
# Format: (program_name, subprogram_name, level_number)
ROUTINETEST_CURRICULUM_WHITELIST = [
    # CORE Program - Fundamental curriculum levels
    ('CORE', 'Phonics', 1), ('CORE', 'Phonics', 2), ('CORE', 'Phonics', 3),
    ('CORE', 'Sigma', 1), ('CORE', 'Sigma', 2), ('CORE', 'Sigma', 3),
    ('CORE', 'Elite', 1), ('CORE', 'Elite', 2), ('CORE', 'Elite', 3),
    ('CORE', 'Pro', 1), ('CORE', 'Pro', 2), ('CORE', 'Pro', 3),
    
    # ASCENT Program - Advanced progression levels
    ('ASCENT', 'Nova', 1), ('ASCENT', 'Nova', 2), ('ASCENT', 'Nova', 3),
    ('ASCENT', 'Drive', 1), ('ASCENT', 'Drive', 2), ('ASCENT', 'Drive', 3),
    ('ASCENT', 'Pro', 1), ('ASCENT', 'Pro', 2), ('ASCENT', 'Pro', 3),
    
    # EDGE Program - Specialized advancement
    ('EDGE', 'Spark', 1), ('EDGE', 'Spark', 2), ('EDGE', 'Spark', 3),
    ('EDGE', 'Rise', 1), ('EDGE', 'Rise', 2), ('EDGE', 'Rise', 3),
    ('EDGE', 'Pursuit', 1), ('EDGE', 'Pursuit', 2), ('EDGE', 'Pursuit', 3),
    ('EDGE', 'Pro', 1), ('EDGE', 'Pro', 2), ('EDGE', 'Pro', 3),
    
    # PINNACLE Program - Mastery levels
    ('PINNACLE', 'Vision', 1), ('PINNACLE', 'Vision', 2),
    ('PINNACLE', 'Endeavor', 1), ('PINNACLE', 'Endeavor', 2),
    ('PINNACLE', 'Success', 1), ('PINNACLE', 'Success', 2),
    ('PINNACLE', 'Pro', 1), ('PINNACLE', 'Pro', 2),
]

# Subject categories for RoutineTest (can be extended later)
ROUTINETEST_SUBJECTS = [
    ('MATHEMATICS', 'Mathematics'),
    ('SCIENCE', 'Science'),
    ('LANGUAGE_ARTS', 'Language Arts'),
    ('SOCIAL_STUDIES', 'Social Studies'),
    ('COMPREHENSIVE', 'Comprehensive Review'),
]

# Naming pattern configurations
ROUTINETEST_NAMING_CONFIG = {
    'REVIEW': {
        'prefix': 'RT',
        'time_period_type': 'month',
        'description': 'Review/Monthly Exams'
    },
    'QUARTERLY': {
        'prefix': 'QTR',
        'time_period_type': 'quarter',
        'description': 'Quarterly Exams'
    }
}

# Default values for new RoutineTest exams
ROUTINETEST_DEFAULTS = {
    'timer_minutes': 90,  # Longer than PlacementTest (60 min)
    'default_options_count': 5,
    'passing_score': 70,  # Higher than PlacementTest default
    'exam_type': 'REVIEW',
}

# Console logging configuration for RoutineTest naming
ROUTINETEST_LOGGING_CONFIG = {
    'enable_console_logs': True,
    'log_naming_generation': True,
    'log_curriculum_filtering': True,
    'log_dropdown_population': True,
}
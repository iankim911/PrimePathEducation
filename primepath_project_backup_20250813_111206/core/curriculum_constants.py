"""
Curriculum Constants and Valid Structure Configuration
This file defines the official curriculum structure for PrimePath.
Any subprograms not in this list should be considered test/QA data.
"""

# Valid curriculum structure as per official specification
# Format: Program -> List of valid subprogram names
VALID_CURRICULUM_STRUCTURE = {
    'CORE': {
        'subprograms': ['Phonics', 'Sigma', 'Elite', 'Pro'],
        'levels': [1, 2, 3],
        'grade_range': (1, 4)
    },
    'ASCENT': {
        'subprograms': ['Nova', 'Drive', 'Flex', 'Pro'],  # Added missing 'Flex' subprogram
        'levels': [1, 2, 3],
        'grade_range': (5, 6)
    },
    'EDGE': {
        'subprograms': ['Spark', 'Rise', 'Pursuit', 'Pro'],
        'levels': [1, 2, 3],
        'grade_range': (7, 9)
    },
    'PINNACLE': {
        'subprograms': ['Vision', 'Endeavor', 'Success', 'Pro'],
        'levels': [1, 2],  # Note: PINNACLE only has levels 1 and 2
        'grade_range': (10, 12)
    }
}

def get_valid_subprogram_names():
    """
    Returns a set of all valid subprogram names in various formats.
    Handles both standalone names (e.g., 'Phonics') and prefixed names (e.g., 'CORE PHONICS').
    """
    valid_names = set()
    
    for program, config in VALID_CURRICULUM_STRUCTURE.items():
        for subprogram in config['subprograms']:
            # Add standalone name
            valid_names.add(subprogram.upper())
            valid_names.add(subprogram.lower())
            valid_names.add(subprogram)
            
            # Add program-prefixed versions
            valid_names.add(f"{program} {subprogram.upper()}")
            valid_names.add(f"{program} {subprogram}")
            valid_names.add(f"{program} {subprogram.lower()}")
            
            # Add variations that might exist in database
            valid_names.add(f"{program} {subprogram.upper()}")
            valid_names.add(f"{program.upper()} {subprogram.upper()}")
    
    # Add specific variations found in database
    valid_names.update([
        'PHONICS',  # Standalone PHONICS under CORE
        'CORE PHONICS',
        'CORE SIGMA',
        'CORE ELITE',
        'CORE PRO',
        'ASCENT NOVA',
        'ASCENT DRIVE',
        'ASCENT FLEX',  # Added missing subprogram
        'ASCENT PRO',
        'EDGE SPARK',
        'EDGE RISE',
        'EDGE PURSUIT',
        'EDGE PRO',
        'PINNACLE VISION',
        'PINNACLE ENDEAVOR',
        'PINNACLE SUCCESS',
        'PINNACLE PRO'
    ])
    
    return valid_names

def is_valid_subprogram(subprogram_name):
    """
    Check if a subprogram name is valid according to the official curriculum structure.
    
    Args:
        subprogram_name: The subprogram name to check
        
    Returns:
        bool: True if valid, False if it's a test/QA subprogram
    """
    if not subprogram_name:
        return False
    
    valid_names = get_valid_subprogram_names()
    return subprogram_name in valid_names

def is_test_subprogram(subprogram_name):
    """
    Check if a subprogram name is a test/QA subprogram that should be filtered out.
    
    Args:
        subprogram_name: The subprogram name to check
        
    Returns:
        bool: True if it's a test subprogram, False if it's valid
    """
    if not subprogram_name:
        return False
    
    # Check if marked as inactive (added by final_fix_exam_mapping.py)
    if subprogram_name.startswith('[INACTIVE]'):
        return True
    
    # Keywords that indicate test/QA data
    test_indicators = [
        'test',
        'TEST',
        'Test',
        'demo',
        'DEMO',
        'Demo',
        'sample',
        'SAMPLE',
        'Sample',
        'SHORT Answer',  # Specific test subprogram
        'SHORT Display',  # Specific test subprogram
        'Comprehensive Test',  # Specific test subprogram
        'Management Test',  # Specific test subprogram
        'Submit Test',  # Specific test subprogram
        'Final Test'  # Specific test subprogram
    ]
    
    # Check if any test indicator is in the name
    for indicator in test_indicators:
        if indicator in subprogram_name:
            return True
    
    # Also check if it's NOT in the valid list
    return not is_valid_subprogram(subprogram_name)

def get_curriculum_structure_summary():
    """
    Returns a formatted summary of the valid curriculum structure.
    Useful for logging and documentation.
    """
    summary = []
    for program, config in VALID_CURRICULUM_STRUCTURE.items():
        for subprogram in config['subprograms']:
            for level in config['levels']:
                summary.append(f"{program}, {subprogram}, Level {level}")
    return summary

# Test/QA subprograms that should be filtered out
# These are known test entries that exist in the database
KNOWN_TEST_SUBPROGRAMS = [
    'Test SubProgram',
    'SHORT Answer Test SubProgram',
    'Comprehensive Test SubProgram',
    'Management Test SubProgram',
    'SHORT Display Test SubProgram',
    'Submit Test SubProgram',
    'Final Test SubProgram',
    # Marked as inactive versions
    '[INACTIVE] Test SubProgram',
    '[INACTIVE] SHORT Answer Test SubProgram',
    '[INACTIVE] Comprehensive Test SubProgram',
    '[INACTIVE] Management Test SubProgram',
    '[INACTIVE] SHORT Display Test SubProgram',
    '[INACTIVE] Submit Test SubProgram',
    '[INACTIVE] Final Test SubProgram'
]

def log_filtered_subprograms(logger, filtered_subprograms):
    """
    Helper function to log filtered subprograms consistently.
    
    Args:
        logger: The logger instance to use
        filtered_subprograms: List of subprogram names that were filtered
    """
    if filtered_subprograms:
        logger.warning(
            f"[CURRICULUM_FILTER] Filtered out {len(filtered_subprograms)} test/QA subprograms: {', '.join(filtered_subprograms)}"
        )
        
        # Also log to console for debugging
        import json
        console_log = {
            "action": "curriculum_filter",
            "filtered_count": len(filtered_subprograms),
            "filtered_subprograms": filtered_subprograms,
            "message": "Test/QA subprograms filtered from display"
        }
        print(f"[CURRICULUM_FILTER] {json.dumps(console_log, indent=2)}")
"""
Curriculum Display Utilities
Provides consistent display formatting for curriculum names across the application.
"""

import logging

logger = logging.getLogger(__name__)

# Correct curriculum structure mapping - Updated for clean names
CURRICULUM_DISPLAY_MAPPING = {
    'CORE': {
        'program_display': 'PRIME CORE',
        'subprograms': {
            # Clean names (after normalization)
            'PHONICS': 'Phonics',
            'SIGMA': 'Sigma',
            'ELITE': 'Elite',
            'PRO': 'Pro',
            # Legacy names (for backward compatibility)
            'CORE PHONICS': 'Phonics',
            'CORE SIGMA': 'Sigma',
            'CORE ELITE': 'Elite',
            'CORE PRO': 'Pro'
        }
    },
    'ASCENT': {
        'program_display': 'PRIME ASCENT',
        'subprograms': {
            # Clean names (after normalization)
            'NOVA': 'Nova',
            'DRIVE': 'Drive',
            'FLEX': 'Flex',
            'PRO': 'Pro',
            # Legacy names (for backward compatibility)
            'ASCENT NOVA': 'Nova',
            'ASCENT DRIVE': 'Drive',
            'ASCENT FLEX': 'Flex',
            'ASCENT PRO': 'Pro'
        }
    },
    'EDGE': {
        'program_display': 'PRIME EDGE',
        'subprograms': {
            # Clean names (after normalization)
            'SPARK': 'Spark',
            'RISE': 'Rise',
            'PURSUIT': 'Pursuit',
            'PRO': 'Pro',
            # Legacy names (for backward compatibility)
            'EDGE SPARK': 'Spark',
            'EDGE RISE': 'Rise',
            'EDGE PURSUIT': 'Pursuit',
            'EDGE PRO': 'Pro'
        }
    },
    'PINNACLE': {
        'program_display': 'PRIME PINNACLE',
        'subprograms': {
            # Clean names (after normalization)
            'VISION': 'Vision',
            'ENDEAVOR': 'Endeavor',
            'SUCCESS': 'Success',
            'PRO': 'Pro',
            # Legacy names (for backward compatibility)
            'PINNACLE VISION': 'Vision',
            'PINNACLE ENDEAVOR': 'Endeavor',
            'PINNACLE SUCCESS': 'Success',
            'PINNACLE PRO': 'Pro'
        }
    }
}

def get_formatted_subprogram_name(program_name, subprogram_name):
    """
    Get the properly formatted subprogram name.
    
    Args:
        program_name: The program name (e.g., 'CORE', 'ASCENT')
        subprogram_name: The raw subprogram name from database
        
    Returns:
        Formatted name like "CORE Phonics" or "PINNACLE Vision"
    """
    if not program_name or not subprogram_name:
        logger.warning(f"[CURRICULUM_DISPLAY] Invalid input: program={program_name}, subprogram={subprogram_name}")
        return subprogram_name or ''
    
    # Get the mapping for this program
    program_mapping = CURRICULUM_DISPLAY_MAPPING.get(program_name.upper())
    if not program_mapping:
        logger.warning(f"[CURRICULUM_DISPLAY] Unknown program: {program_name}")
        return subprogram_name
    
    # Get the display name for this subprogram
    subprogram_display = program_mapping['subprograms'].get(subprogram_name.upper())
    if not subprogram_display:
        # Try without program prefix
        clean_name = subprogram_name.upper().replace(program_name.upper() + ' ', '')
        subprogram_display = program_mapping['subprograms'].get(clean_name)
    
    if not subprogram_display:
        logger.warning(f"[CURRICULUM_DISPLAY] Unknown subprogram: {program_name}/{subprogram_name}")
        return subprogram_name
    
    # Return formatted name
    return f"{program_name.upper()} {subprogram_display}"

def get_formatted_level_name(program_name, subprogram_name, level_number):
    """
    Get the properly formatted level name.
    
    Args:
        program_name: The program name (e.g., 'CORE', 'ASCENT')
        subprogram_name: The raw subprogram name from database
        level_number: The level number
        
    Returns:
        Formatted name like "CORE Phonics Level 1"
    """
    formatted_subprogram = get_formatted_subprogram_name(program_name, subprogram_name)
    return f"{formatted_subprogram} Level {level_number}"

def get_curriculum_level_display_data(curriculum_level):
    """
    Get complete display data for a curriculum level.
    
    Args:
        curriculum_level: A CurriculumLevel model instance
        
    Returns:
        Dict with formatted display names and metadata
    """
    program = curriculum_level.subprogram.program
    
    # Log for debugging
    logger.debug(f"[CURRICULUM_DISPLAY] Processing level: {curriculum_level}")
    
    formatted_subprogram = get_formatted_subprogram_name(
        program.name,
        curriculum_level.subprogram.name
    )
    
    display_data = {
        'program_name': program.name,
        'program_display': CURRICULUM_DISPLAY_MAPPING.get(program.name, {}).get('program_display', program.get_name_display()),
        'subprogram_raw': curriculum_level.subprogram.name,
        'subprogram_display': formatted_subprogram,
        'level_number': curriculum_level.level_number,
        'full_display': f"{formatted_subprogram} Level {curriculum_level.level_number}",
        'short_display': f"{formatted_subprogram} Lv {curriculum_level.level_number}",
        'id': curriculum_level.id
    }
    
    # Add console logging for debugging
    console_log = {
        'action': 'format_curriculum_level',
        'input': {
            'program': program.name,
            'subprogram': curriculum_level.subprogram.name,
            'level': curriculum_level.level_number
        },
        'output': {
            'subprogram_display': display_data['subprogram_display'],
            'full_display': display_data['full_display']
        }
    }
    print(f"[CURRICULUM_DISPLAY] {console_log}")
    
    return display_data

def validate_curriculum_display():
    """
    Validate that all curriculum levels can be properly displayed.
    Used for testing and debugging.
    """
    from core.models import CurriculumLevel
    
    issues = []
    success_count = 0
    
    for level in CurriculumLevel.objects.all():
        try:
            display_data = get_curriculum_level_display_data(level)
            if not display_data['subprogram_display']:
                issues.append(f"No display name for: {level}")
            else:
                success_count += 1
        except Exception as e:
            issues.append(f"Error processing {level}: {e}")
    
    return {
        'success_count': success_count,
        'issues': issues,
        'total': CurriculumLevel.objects.count()
    }
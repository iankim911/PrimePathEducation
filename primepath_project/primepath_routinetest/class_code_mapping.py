"""
Class Code Mapping for PrimePath Curriculum
Updated: 2025-08-20
This file contains the official mapping between class codes and curriculum programs
"""

CLASS_CODE_CURRICULUM_MAPPING = {
    # CORE Program - Phonics
    'PS1': 'CORE Phonics Level 1',
    'P2': 'CORE Phonics Level 3',
    
    # CORE Program - Sigma
    'A2': 'CORE Sigma Level 1',
    'B2': 'CORE Sigma Level 2',
    'B3': 'CORE Sigma Level 3',
    
    # CORE Program - Elite
    'B4': 'CORE Elite Level 1',
    'B5': 'CORE Elite Level 2',
    'S2': 'CORE Elite Level 3',
    
    # CORE Program - Additional Sigma
    'S3': 'CORE Sigma Level 1',
    'H1': 'CORE Sigma Level 3',
    'H2': 'CORE Sigma Level 3',
    
    # CORE Program - Additional Elite
    'C2': 'CORE Elite Level 1',
    'C3': 'CORE Sigma Level 3',
    'C4': 'CORE Sigma Level 3',
    'C5': 'CORE Elite Level 1',
    'H3': 'CORE Elite Level 2',
    'H4': 'CORE Elite Level 3',
    
    # EDGE Program - Rise
    'Young-cho2': 'EDGE Rise Level 1',
    'Chung-cho4': 'EDGE Rise Level 2',
    'Chung-cho1': 'EDGE Rise Level 3',
    
    # EDGE Program - Pursuit
    'SejongM': 'EDGE Pursuit Level 3',
    
    # EDGE Program - Pro
    'MAS': 'EDGE Pro Level 1',
    
    # ASCENT Program - Drive
    'TaejoC': 'ASCENT Drive Level 1',
    'TaejoD': 'ASCENT Drive Level 2',
    'TaejoE': 'ASCENT Drive Level 3',
    'TaejoG': 'ASCENT Drive Level 3',
    
    # ASCENT Program - Pro
    'SungjongM': 'ASCENT Pro Level 1',
    'Sungjong2': 'ASCENT Pro Level 2',
    
    # EDGE Program - Spark
    'Sungjong3': 'EDGE Spark Level 1',
    'Sungjong4': 'EDGE Spark Level 2',
    'Young-choM': 'EDGE Spark Level 3',
    
    # ASCENT Program - Nova
    'D2': 'ASCENT Nova Level 1',
    'D3': 'ASCENT Nova Level 1',
    'D4': 'ASCENT Nova Level 2',
    
    # PINNACLE Program - Vision
    'High1.SatSun.3-5': 'PINNACLE Vision Level 1',
    'High1.SatSun.5-7': 'PINNACLE Vision Level 1',
    
    # PINNACLE Program - Endeavor
    'High1/2.SatSun.11-1': 'PINNACLE Endeavor Level 2',
    'High1/2.SatSun.1-3': 'PINNACLE Endeavor Level 2',
}

# Reverse mapping for quick lookup
CURRICULUM_TO_CLASS_CODES = {}
for class_code, curriculum in CLASS_CODE_CURRICULUM_MAPPING.items():
    if curriculum not in CURRICULUM_TO_CLASS_CODES:
        CURRICULUM_TO_CLASS_CODES[curriculum] = []
    CURRICULUM_TO_CLASS_CODES[curriculum].append(class_code)

# Class code categories for grouping
CLASS_CODE_CATEGORIES = {
    'CORE_PHONICS': ['PS1', 'P2'],
    'CORE_SIGMA': ['A2', 'B2', 'B3', 'S3', 'H1', 'H2', 'C3', 'C4'],
    'CORE_ELITE': ['B4', 'B5', 'S2', 'C2', 'C5', 'H3', 'H4'],
    'EDGE_RISE': ['Young-cho2', 'Chung-cho4', 'Chung-cho1'],
    'EDGE_PURSUIT': ['SejongM'],
    'EDGE_PRO': ['MAS'],
    'EDGE_SPARK': ['Sungjong3', 'Sungjong4', 'Young-choM'],
    'ASCENT_DRIVE': ['TaejoC', 'TaejoD', 'TaejoE', 'TaejoG'],
    'ASCENT_PRO': ['SungjongM', 'Sungjong2'],
    'ASCENT_NOVA': ['D2', 'D3', 'D4'],
    'PINNACLE_VISION': ['High1.SatSun.3-5', 'High1.SatSun.5-7'],
    'PINNACLE_ENDEAVOR': ['High1/2.SatSun.11-1', 'High1/2.SatSun.1-3'],
}

def get_curriculum_for_class(class_code):
    """
    Get the curriculum level for a given class code
    
    Args:
        class_code (str): The class code (e.g., 'PS1', 'P1', etc.)
    
    Returns:
        str: The curriculum level or None if not found
    """
    return CLASS_CODE_CURRICULUM_MAPPING.get(class_code)

def get_classes_for_curriculum(curriculum_level):
    """
    Get all class codes that use a specific curriculum level
    
    Args:
        curriculum_level (str): The curriculum level (e.g., 'CORE Phonics Level 1')
    
    Returns:
        list: List of class codes using this curriculum
    """
    return CURRICULUM_TO_CLASS_CODES.get(curriculum_level, [])

def get_program_from_class_code(class_code):
    """
    Extract the program name from a class code
    
    Args:
        class_code (str): The class code
    
    Returns:
        str: The program name (CORE, EDGE, ASCENT, or PINNACLE)
    """
    curriculum = get_curriculum_for_class(class_code)
    if curriculum:
        return curriculum.split()[0]
    return None

def get_subprogram_from_class_code(class_code):
    """
    Extract the subprogram name from a class code
    
    Args:
        class_code (str): The class code
    
    Returns:
        str: The subprogram name (Phonics, Sigma, Elite, etc.)
    """
    curriculum = get_curriculum_for_class(class_code)
    if curriculum:
        parts = curriculum.split()
        if len(parts) >= 2:
            return parts[1]
    return None

def get_level_from_class_code(class_code):
    """
    Extract the level from a class code
    
    Args:
        class_code (str): The class code
    
    Returns:
        str: The level (1, 2, or 3)
    """
    curriculum = get_curriculum_for_class(class_code)
    if curriculum:
        parts = curriculum.split()
        if len(parts) >= 4 and parts[2] == 'Level':
            return parts[3]
    return None

def validate_class_code(class_code):
    """
    Check if a class code is valid
    
    Args:
        class_code (str): The class code to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    return class_code in CLASS_CODE_CURRICULUM_MAPPING

def get_all_class_codes():
    """
    Get all valid class codes
    
    Returns:
        list: Sorted list of all class codes
    """
    return sorted(CLASS_CODE_CURRICULUM_MAPPING.keys())

def get_class_codes_by_program(program_name):
    """
    Get all class codes for a specific program
    
    Args:
        program_name (str): The program name (CORE, EDGE, ASCENT, PINNACLE)
    
    Returns:
        list: List of class codes for that program
    """
    result = []
    for class_code, curriculum in CLASS_CODE_CURRICULUM_MAPPING.items():
        if curriculum.startswith(program_name):
            result.append(class_code)
    return sorted(result)

# Statistics functions
def get_curriculum_statistics():
    """
    Get statistics about the curriculum mapping
    
    Returns:
        dict: Statistics including counts by program
    """
    stats = {
        'total_class_codes': len(CLASS_CODE_CURRICULUM_MAPPING),
        'total_unique_curricula': len(CURRICULUM_TO_CLASS_CODES),
        'programs': {}
    }
    
    for program in ['CORE', 'EDGE', 'ASCENT', 'PINNACLE']:
        class_codes = get_class_codes_by_program(program)
        stats['programs'][program] = {
            'class_codes': len(class_codes),
            'codes': class_codes
        }
    
    return stats

if __name__ == '__main__':
    # Test the mapping
    print("Class Code to Curriculum Mapping")
    print("=" * 80)
    
    for program in ['CORE', 'EDGE', 'ASCENT', 'PINNACLE']:
        print(f"\n{program} Program:")
        print("-" * 40)
        codes = get_class_codes_by_program(program)
        for code in codes:
            curriculum = get_curriculum_for_class(code)
            print(f"  {code:20} -> {curriculum}")
    
    print("\n" + "=" * 80)
    stats = get_curriculum_statistics()
    print(f"Total Class Codes: {stats['total_class_codes']}")
    print(f"Unique Curricula: {stats['total_unique_curricula']}")
    
    print("\nClass Codes per Program:")
    for program, data in stats['programs'].items():
        print(f"  {program}: {data['class_codes']} codes")
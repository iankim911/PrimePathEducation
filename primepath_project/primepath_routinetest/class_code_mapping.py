"""
Class Code Mapping for PrimePath
Updated: 2025-08-25
This file contains the actual class codes from the system
NO CURRICULUM MAPPING - Classes are independent entities
"""

# ACTUAL CLASS CODES FROM THE SYSTEM - NO FAKE CLASSES
CLASS_CODE_CURRICULUM_MAPPING = {
    # Primary/Preschool Classes
    'PS1': 'PS1',
    'P1': 'P1', 
    'P2': 'P2',
    
    # A-Series Classes
    'A2': 'A2',
    
    # B-Series Classes  
    'B2': 'B2',
    'B3': 'B3',
    'B4': 'B4',
    'B5': 'B5',
    
    # S-Series Classes
    'S2': 'S2',
    
    # H-Series Classes
    'H1': 'H1',
    'H2': 'H2',
    'H4': 'H4',
    
    # C-Series Classes
    'C2': 'C2',
    'C3': 'C3',
    'C4': 'C4',
    'C5': 'C5',
    
    # Young-cho Classes
    'Young-cho2': 'Young-cho2',
    'Young-choM': 'Young-choM',
    
    # Chung-cho Classes
    'Chung-choM': 'Chung-choM',
    'Chung-cho1': 'Chung-cho1',
    
    # Sejong Classes
    'SejongM': 'SejongM',
    
    # MAS Classes
    'MAS': 'MAS',
    
    # Taejo Classes
    'TaejoG': 'TaejoG',
    'TaejoD': 'TaejoD',
    'TaejoDC': 'TaejoDC',
    
    # Sungjong Classes
    'SungjongM': 'SungjongM',
    'Sungjong2': 'Sungjong2',
    'Sungjong3': 'Sungjong3',
    'Sungjong4': 'Sungjong4',
    'SungjongC': 'SungjongC',
    
    # D-Series Classes
    'D2': 'D2',
    'D3': 'D3',
    'D4': 'D4',
    
    # High SaiSun Classes (using underscore for spaces in keys)
    'High1_SaiSun_3-5': 'High1 SaiSun 3-5',
    'High1_SaiSun_5-7': 'High1 SaiSun 5-7',
    'High1V2_SaiSun_11-1': 'High1V2 SaiSun 11-1',
    'High1V2_SaiSun_1-3': 'High1V2 SaiSun 1-3',
    
    # High School Classes
    'HIGH_10E': 'HIGH 10E',
    'HIGH_10F': 'HIGH 10F', 
    'HIGH_11D': 'HIGH 11D',
    
    # Middle School Classes
    'MIDDLE_7A': 'MIDDLE 7A',
    
    # Primary School Classes
    'PRIMARY_1D': 'PRIMARY 1D',
    'PRIMARY_2A': 'PRIMARY 2A',
    
    # Taejo Classes
    'TaejoE': 'TaejoE',
    
    # PINNACLE Classes (Added August 25, 2025)
    'PINNACLE_V1': 'PINNACLE Vision Level 1',
    'PINNACLE_V2': 'PINNACLE Vision Level 2',
    'PINNACLE_E1': 'PINNACLE Endeavor Level 1',
    'PINNACLE_E2': 'PINNACLE Endeavor Level 2',
    'PINNACLE_S1': 'PINNACLE Success Level 1',
    'PINNACLE_S2': 'PINNACLE Success Level 2',
    'PINNACLE_P1': 'PINNACLE Pro Level 1',
    'PINNACLE_P2': 'PINNACLE Pro Level 2',
}

# Reverse mapping for quick lookup
CURRICULUM_TO_CLASS_CODES = {}
for class_code, display_name in CLASS_CODE_CURRICULUM_MAPPING.items():
    if display_name not in CURRICULUM_TO_CLASS_CODES:
        CURRICULUM_TO_CLASS_CODES[display_name] = []
    CURRICULUM_TO_CLASS_CODES[display_name].append(class_code)

# Class code categories for logical grouping (no curriculum association)
CLASS_CODE_CATEGORIES = {
    'PRIMARY': ['PS1', 'P1', 'P2'],
    'LETTER_SERIES_A': ['A2'],
    'LETTER_SERIES_B': ['B2', 'B3', 'B4', 'B5'],
    'LETTER_SERIES_S': ['S2'],
    'LETTER_SERIES_H': ['H1', 'H2', 'H4'],
    'LETTER_SERIES_C': ['C2', 'C3', 'C4', 'C5'],
    'LETTER_SERIES_D': ['D2', 'D3', 'D4'],
    'YOUNG_CHO': ['Young-cho2', 'Young-choM'],
    'CHUNG_CHO': ['Chung-choM', 'Chung-cho1'],
    'SEJONG': ['SejongM'],
    'MAS': ['MAS'],
    'TAEJO': ['TaejoG', 'TaejoD', 'TaejoDC', 'TaejoE'],
    'SUNGJONG': ['SungjongM', 'Sungjong2', 'Sungjong3', 'Sungjong4', 'SungjongC'],
    'HIGH_SAISUN': ['High1_SaiSun_3-5', 'High1_SaiSun_5-7', 'High1V2_SaiSun_11-1', 'High1V2_SaiSun_1-3'],
    'HIGH_SCHOOL': ['HIGH_10E', 'HIGH_10F', 'HIGH_11D'],
    'MIDDLE_SCHOOL': ['MIDDLE_7A'],
    'PRIMARY_SCHOOL': ['PRIMARY_1D', 'PRIMARY_2A'],
    'PINNACLE': ['PINNACLE_V1', 'PINNACLE_V2', 'PINNACLE_E1', 'PINNACLE_E2', 
                 'PINNACLE_S1', 'PINNACLE_S2', 'PINNACLE_P1', 'PINNACLE_P2'],
}

def get_curriculum_for_class(class_code):
    """
    Get the display name for a given class code
    
    Args:
        class_code (str): The class code (e.g., 'PS1', 'P1', etc.)
    
    Returns:
        str: The display name or None if not found
    """
    print(f"[CLASS_CODE_MAPPING] Getting display for class: {class_code}")
    result = CLASS_CODE_CURRICULUM_MAPPING.get(class_code)
    
    # CRITICAL: Never return generic placeholder text
    if result == "Curriculum Level" or result == "Curriculum level":
        print(f"[CLASS_CODE_MAPPING] WARNING: Placeholder text detected for {class_code}, returning class code instead")
        return class_code
    
    return result

def get_classes_for_curriculum(curriculum_level):
    """
    DEPRECATED: No curriculum levels - classes are independent
    
    Args:
        curriculum_level (str): Not used
    
    Returns:
        list: Empty list
    """
    print(f"[CLASS_CODE_MAPPING] WARNING: get_classes_for_curriculum called - no curriculum mapping exists")
    return []

def get_program_from_class_code(class_code):
    """
    Get logical grouping for a class code
    
    Args:
        class_code (str): The class code
    
    Returns:
        str: The category name or 'GENERAL'
    """
    print(f"[CLASS_CODE_MAPPING] Getting category for class: {class_code}")
    for category, codes in CLASS_CODE_CATEGORIES.items():
        if class_code in codes:
            return category
    return 'GENERAL'

def get_subprogram_from_class_code(class_code):
    """
    DEPRECATED: No subprograms - classes are independent
    
    Args:
        class_code (str): The class code
    
    Returns:
        str: None
    """
    print(f"[CLASS_CODE_MAPPING] WARNING: get_subprogram_from_class_code called - no subprograms exist")
    return None

def get_level_from_class_code(class_code):
    """
    DEPRECATED: No levels - classes are independent
    
    Args:
        class_code (str): The class code
    
    Returns:
        str: None
    """
    print(f"[CLASS_CODE_MAPPING] WARNING: get_level_from_class_code called - no levels exist")
    return None

def validate_class_code(class_code):
    """
    Check if a class code is valid
    
    Args:
        class_code (str): The class code to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    is_valid = class_code in CLASS_CODE_CURRICULUM_MAPPING
    print(f"[CLASS_CODE_MAPPING] Validating class {class_code}: {'VALID' if is_valid else 'INVALID'}")
    return is_valid

def get_all_class_codes():
    """
    Get all valid class codes
    
    Returns:
        list: Sorted list of all class codes
    """
    codes = sorted(CLASS_CODE_CURRICULUM_MAPPING.keys())
    print(f"[CLASS_CODE_MAPPING] Returning {len(codes)} class codes")
    return codes

def get_class_codes_by_program(program_name):
    """
    Get class codes by category (replaces program concept)
    
    Args:
        program_name (str): The category name
    
    Returns:
        list: List of class codes for that category
    """
    print(f"[CLASS_CODE_MAPPING] Getting classes for category: {program_name}")
    
    # Map old program names to new categories for backward compatibility
    program_to_category = {
        'CORE': ['PRIMARY', 'LETTER_SERIES_A', 'LETTER_SERIES_B', 'LETTER_SERIES_S', 'PRIMARY_SCHOOL'],
        'ASCENT': ['LETTER_SERIES_H', 'LETTER_SERIES_C', 'LETTER_SERIES_D', 'MIDDLE_SCHOOL'],
        'EDGE': ['YOUNG_CHO', 'CHUNG_CHO', 'SEJONG', 'MAS'],
        'PINNACLE': ['PINNACLE']  # Updated to use new PINNACLE category directly
    }
    
    result = []
    if program_name in program_to_category:
        for category in program_to_category[program_name]:
            result.extend(CLASS_CODE_CATEGORIES.get(category, []))
    elif program_name in CLASS_CODE_CATEGORIES:
        result = CLASS_CODE_CATEGORIES[program_name]
    
    print(f"[CLASS_CODE_MAPPING] Found {len(result)} classes for {program_name}")
    return sorted(result)

# Statistics functions
def get_curriculum_statistics():
    """
    Get statistics about the class codes
    
    Returns:
        dict: Statistics including counts by category
    """
    stats = {
        'total_class_codes': len(CLASS_CODE_CURRICULUM_MAPPING),
        'total_categories': len(CLASS_CODE_CATEGORIES),
        'categories': {}
    }
    
    for category, codes in CLASS_CODE_CATEGORIES.items():
        stats['categories'][category] = {
            'class_codes': len(codes),
            'codes': codes
        }
    
    print(f"[CLASS_CODE_MAPPING] Statistics: {stats['total_class_codes']} total codes in {stats['total_categories']} categories")
    return stats

if __name__ == '__main__':
    # Test the mapping
    print("Class Code Mapping - ACTUAL CLASSES")
    print("=" * 80)
    
    print("\nAll Class Codes:")
    print("-" * 40)
    all_codes = get_all_class_codes()
    for code in all_codes:
        display = get_curriculum_for_class(code)
        print(f"  {code:25} -> {display}")
    
    print("\n" + "=" * 80)
    stats = get_curriculum_statistics()
    print(f"Total Class Codes: {stats['total_class_codes']}")
    print(f"Total Categories: {stats['total_categories']}")
    
    print("\nClass Codes per Category:")
    for category, data in stats['categories'].items():
        print(f"  {category}: {data['class_codes']} codes")
        print(f"    Codes: {', '.join(data['codes'][:5])}{' ...' if len(data['codes']) > 5 else ''}")
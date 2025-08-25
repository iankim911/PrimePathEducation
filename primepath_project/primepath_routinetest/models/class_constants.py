"""
Class Constants and Classification Helpers
Actual class codes from the system

Updated: August 25, 2025
"""

# Complete class choices for Django models - ACTUAL CLASSES FROM SYSTEM
CLASS_CODE_CHOICES = [
    # Primary/Preschool Classes
    ('PS1', 'PS1'),
    ('P1', 'P1'),
    ('P2', 'P2'),
    
    # A-Series Classes
    ('A2', 'A2'),
    
    # B-Series Classes
    ('B2', 'B2'),
    ('B3', 'B3'),
    ('B4', 'B4'),
    ('B5', 'B5'),
    
    # S-Series Classes
    ('S2', 'S2'),
    
    # H-Series Classes
    ('H1', 'H1'),
    ('H2', 'H2'),
    ('H4', 'H4'),
    
    # C-Series Classes
    ('C2', 'C2'),
    ('C3', 'C3'),
    ('C4', 'C4'),
    ('C5', 'C5'),
    
    # Young-cho Classes
    ('Young-cho2', 'Young-cho2'),
    ('Young-choM', 'Young-choM'),
    
    # Chung-cho Classes
    ('Chung-choM', 'Chung-choM'),
    ('Chung-cho1', 'Chung-cho1'),
    
    # Sejong Classes
    ('SejongM', 'SejongM'),
    
    # MAS Classes
    ('MAS', 'MAS'),
    
    # Taejo Classes
    ('TaejoG', 'TaejoG'),
    ('TaejoD', 'TaejoD'),
    ('TaejoDC', 'TaejoDC'),
    
    # Sungjong Classes
    ('SungjongM', 'SungjongM'),
    ('Sungjong2', 'Sungjong2'),
    ('Sungjong3', 'Sungjong3'),
    ('SungjongC', 'SungjongC'),
    
    # D-Series Classes
    ('D2', 'D2'),
    ('D3', 'D3'),
    ('D4', 'D4'),
    
    # High SaiSun Classes
    ('High1_SaiSun_3-5', 'High1 SaiSun 3-5'),
    ('High1_SaiSun_5-7', 'High1 SaiSun 5-7'),
    ('High1V2_SaiSun_11-1', 'High1V2 SaiSun 11-1'),
    ('High1V2_SaiSun_1-3', 'High1V2 SaiSun 1-3'),
]

# Classification helpers - grouping actual classes logically
CLASS_CATEGORIES = {
    'PRIMARY': ['PS1', 'P1', 'P2'],
    'ELEMENTARY': ['A2', 'B2', 'B3', 'B4', 'B5', 'S2'],
    'MIDDLE': ['H1', 'H2', 'H4', 'C2', 'C3', 'C4', 'C5'],
    'YOUNG_CHO': ['Young-cho2', 'Young-choM'],
    'CHUNG_CHO': ['Chung-choM', 'Chung-cho1'],
    'SEJONG': ['SejongM'],
    'MAS': ['MAS'],
    'TAEJO': ['TaejoG', 'TaejoD', 'TaejoDC'],
    'SUNGJONG': ['SungjongM', 'Sungjong2', 'Sungjong3', 'SungjongC'],
    'DEVELOPMENT': ['D2', 'D3', 'D4'],
    'HIGH_SAISUN': ['High1_SaiSun_3-5', 'High1_SaiSun_5-7', 'High1V2_SaiSun_11-1', 'High1V2_SaiSun_1-3'],
}

# Simplified stream mapping for actual classes
CLASS_STREAMS = {
    # Primary/Preschool
    'PS1': 'Preschool', 'P1': 'Primary 1', 'P2': 'Primary 2',
    
    # Letter-Series
    'A2': 'A-Track', 
    'B2': 'B-Track', 'B3': 'B-Track', 'B4': 'B-Track', 'B5': 'B-Track',
    'S2': 'S-Track',
    'H1': 'H-Track', 'H2': 'H-Track', 'H4': 'H-Track',
    'C2': 'C-Track', 'C3': 'C-Track', 'C4': 'C-Track', 'C5': 'C-Track',
    'D2': 'D-Track', 'D3': 'D-Track', 'D4': 'D-Track',
    
    # Korean Programs
    'Young-cho2': 'Young-cho Program', 'Young-choM': 'Young-cho Program',
    'Chung-choM': 'Chung-cho Program', 'Chung-cho1': 'Chung-cho Program',
    'SejongM': 'Sejong Program',
    'MAS': 'MAS Program',
    'TaejoG': 'Taejo Program', 'TaejoD': 'Taejo Program', 'TaejoDC': 'Taejo Program',
    'SungjongM': 'Sungjong Program', 'Sungjong2': 'Sungjong Program', 
    'Sungjong3': 'Sungjong Program', 'SungjongC': 'Sungjong Program',
    
    # High SaiSun
    'High1_SaiSun_3-5': 'High SaiSun', 'High1_SaiSun_5-7': 'High SaiSun',
    'High1V2_SaiSun_11-1': 'High SaiSun V2', 'High1V2_SaiSun_1-3': 'High SaiSun V2',
}

# Grade mapping (approximate for actual classes)
CLASS_GRADES = {
    # Primary
    'PS1': 0, 'P1': 1, 'P2': 2,
    
    # Elementary (2-5)
    'A2': 2,
    'B2': 2, 'B3': 3, 'B4': 4, 'B5': 5,
    'S2': 2,
    
    # Middle (6-8)
    'H1': 6, 'H2': 7, 'H4': 8,
    'C2': 6, 'C3': 7, 'C4': 8, 'C5': 9,
    
    # Development
    'D2': 2, 'D3': 3, 'D4': 4,
    
    # Korean Programs (various levels)
    'Young-cho2': 2, 'Young-choM': 6,
    'Chung-choM': 7, 'Chung-cho1': 8,
    'SejongM': 8,
    'MAS': 9,
    'TaejoG': 10, 'TaejoD': 10, 'TaejoDC': 10,
    'SungjongM': 11, 'Sungjong2': 11, 'Sungjong3': 11, 'SungjongC': 11,
    
    # High SaiSun
    'High1_SaiSun_3-5': 10, 'High1_SaiSun_5-7': 10,
    'High1V2_SaiSun_11-1': 11, 'High1V2_SaiSun_1-3': 11,
}

# Helper functions
def get_class_category(class_code):
    """Get category (PRIMARY/MIDDLE/HIGH) for a class code"""
    for category, classes in CLASS_CATEGORIES.items():
        if class_code in classes:
            return category
    return 'UNKNOWN'

def get_class_stream(class_code):
    """Get stream/track for a class code"""
    return CLASS_STREAMS.get(class_code, 'Unknown Stream')

def get_class_grade(class_code):
    """Get grade level for a class code"""
    return CLASS_GRADES.get(class_code, 0)

def get_classes_by_category(category):
    """Get all classes in a specific category"""
    return CLASS_CATEGORIES.get(category, [])

def get_classes_by_grade(grade):
    """Get all classes for a specific grade"""
    return [code for code, g in CLASS_GRADES.items() if g == grade]

def get_classes_by_stream(stream):
    """Get all classes with a specific stream"""
    return [code for code, s in CLASS_STREAMS.items() if s == stream]

# Statistics
def get_class_statistics():
    """Get statistics about the class structure"""
    return {
        'total_classes': len(CLASS_CODE_CHOICES),
        'by_category': {cat: len(classes) for cat, classes in CLASS_CATEGORIES.items()},
        'by_grade': {grade: len(get_classes_by_grade(grade)) for grade in range(1, 13)},
        'streams': list(set(CLASS_STREAMS.values())),
        'stream_counts': {stream: len(get_classes_by_stream(stream)) for stream in set(CLASS_STREAMS.values())}
    }
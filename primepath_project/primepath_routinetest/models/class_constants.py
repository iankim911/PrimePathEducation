"""
Class Constants and Classification Helpers
For 60-class structure with proper categorization

Created: August 18, 2025
"""

# Complete class choices for Django models
CLASS_CODE_CHOICES = [
    # PRIMARY SCHOOL
    ('PRIMARY_1A', 'Primary Grade 1A'),
    ('PRIMARY_1B', 'Primary Grade 1B'),
    ('PRIMARY_1C', 'Primary Grade 1C'),
    ('PRIMARY_1D', 'Primary Grade 1D'),
    ('PRIMARY_2A', 'Primary Grade 2A'),
    ('PRIMARY_2B', 'Primary Grade 2B'),
    ('PRIMARY_2C', 'Primary Grade 2C'),
    ('PRIMARY_2D', 'Primary Grade 2D'),
    ('PRIMARY_3A', 'Primary Grade 3A'),
    ('PRIMARY_3B', 'Primary Grade 3B'),
    ('PRIMARY_3C', 'Primary Grade 3C'),
    ('PRIMARY_3D', 'Primary Grade 3D'),
    ('PRIMARY_4A', 'Primary Grade 4A'),
    ('PRIMARY_4B', 'Primary Grade 4B'),
    ('PRIMARY_4C', 'Primary Grade 4C'),
    ('PRIMARY_4D', 'Primary Grade 4D'),
    ('PRIMARY_5A', 'Primary Grade 5A'),
    ('PRIMARY_5B', 'Primary Grade 5B'),
    ('PRIMARY_5C', 'Primary Grade 5C'),
    ('PRIMARY_5D', 'Primary Grade 5D'),
    ('PRIMARY_6A', 'Primary Grade 6A'),
    ('PRIMARY_6B', 'Primary Grade 6B'),
    ('PRIMARY_6C', 'Primary Grade 6C'),
    ('PRIMARY_6D', 'Primary Grade 6D'),

    # MIDDLE SCHOOL
    ('MIDDLE_7A', 'Middle School Grade 7A'),
    ('MIDDLE_7B', 'Middle School Grade 7B'),
    ('MIDDLE_7C', 'Middle School Grade 7C'),
    ('MIDDLE_7D', 'Middle School Grade 7D'),
    ('MIDDLE_7E', 'Middle School Grade 7E'),
    ('MIDDLE_7F', 'Middle School Grade 7F'),
    ('MIDDLE_8A', 'Middle School Grade 8A'),
    ('MIDDLE_8B', 'Middle School Grade 8B'),
    ('MIDDLE_8C', 'Middle School Grade 8C'),
    ('MIDDLE_8D', 'Middle School Grade 8D'),
    ('MIDDLE_8E', 'Middle School Grade 8E'),
    ('MIDDLE_8F', 'Middle School Grade 8F'),
    ('MIDDLE_9A', 'Middle School Grade 9A'),
    ('MIDDLE_9B', 'Middle School Grade 9B'),
    ('MIDDLE_9C', 'Middle School Grade 9C'),
    ('MIDDLE_9D', 'Middle School Grade 9D'),
    ('MIDDLE_9E', 'Middle School Grade 9E'),
    ('MIDDLE_9F', 'Middle School Grade 9F'),

    # HIGH SCHOOL
    ('HIGH_10A', 'High School Grade 10A'),
    ('HIGH_10B', 'High School Grade 10B'),
    ('HIGH_10C', 'High School Grade 10C'),
    ('HIGH_10D', 'High School Grade 10D'),
    ('HIGH_10E', 'High School Grade 10E'),
    ('HIGH_10F', 'High School Grade 10F'),
    ('HIGH_11A', 'High School Grade 11A'),
    ('HIGH_11B', 'High School Grade 11B'),
    ('HIGH_11C', 'High School Grade 11C'),
    ('HIGH_11D', 'High School Grade 11D'),
    ('HIGH_11E', 'High School Grade 11E'),
    ('HIGH_11F', 'High School Grade 11F'),
    ('HIGH_12A', 'High School Grade 12A'),
    ('HIGH_12B', 'High School Grade 12B'),
    ('HIGH_12C', 'High School Grade 12C'),
    ('HIGH_12D', 'High School Grade 12D'),
    ('HIGH_12E', 'High School Grade 12E'),
    ('HIGH_12F', 'High School Grade 12F'),
]

# Classification helpers
CLASS_CATEGORIES = {
    'PRIMARY': ['PRIMARY_1A', 'PRIMARY_1B', 'PRIMARY_1C', 'PRIMARY_1D', 
                'PRIMARY_2A', 'PRIMARY_2B', 'PRIMARY_2C', 'PRIMARY_2D',
                'PRIMARY_3A', 'PRIMARY_3B', 'PRIMARY_3C', 'PRIMARY_3D',
                'PRIMARY_4A', 'PRIMARY_4B', 'PRIMARY_4C', 'PRIMARY_4D',
                'PRIMARY_5A', 'PRIMARY_5B', 'PRIMARY_5C', 'PRIMARY_5D',
                'PRIMARY_6A', 'PRIMARY_6B', 'PRIMARY_6C', 'PRIMARY_6D'],
    'MIDDLE': ['MIDDLE_7A', 'MIDDLE_7B', 'MIDDLE_7C', 'MIDDLE_7D', 'MIDDLE_7E', 'MIDDLE_7F',
               'MIDDLE_8A', 'MIDDLE_8B', 'MIDDLE_8C', 'MIDDLE_8D', 'MIDDLE_8E', 'MIDDLE_8F',
               'MIDDLE_9A', 'MIDDLE_9B', 'MIDDLE_9C', 'MIDDLE_9D', 'MIDDLE_9E', 'MIDDLE_9F'],
    'HIGH': ['HIGH_10A', 'HIGH_10B', 'HIGH_10C', 'HIGH_10D', 'HIGH_10E', 'HIGH_10F',
             'HIGH_11A', 'HIGH_11B', 'HIGH_11C', 'HIGH_11D', 'HIGH_11E', 'HIGH_11F',
             'HIGH_12A', 'HIGH_12B', 'HIGH_12C', 'HIGH_12D', 'HIGH_12E', 'HIGH_12F'],
}

CLASS_STREAMS = {
    # Primary streams (by section)
    'PRIMARY_1A': 'Advanced Track', 'PRIMARY_1B': 'Standard Track', 'PRIMARY_1C': 'Foundation Track', 'PRIMARY_1D': 'Support Track',
    'PRIMARY_2A': 'Advanced Track', 'PRIMARY_2B': 'Standard Track', 'PRIMARY_2C': 'Foundation Track', 'PRIMARY_2D': 'Support Track',
    'PRIMARY_3A': 'Advanced Track', 'PRIMARY_3B': 'Standard Track', 'PRIMARY_3C': 'Foundation Track', 'PRIMARY_3D': 'Support Track',
    'PRIMARY_4A': 'Advanced Track', 'PRIMARY_4B': 'Standard Track', 'PRIMARY_4C': 'Foundation Track', 'PRIMARY_4D': 'Support Track',
    'PRIMARY_5A': 'Advanced Track', 'PRIMARY_5B': 'Standard Track', 'PRIMARY_5C': 'Foundation Track', 'PRIMARY_5D': 'Support Track',
    'PRIMARY_6A': 'Advanced Track', 'PRIMARY_6B': 'Standard Track', 'PRIMARY_6C': 'Foundation Track', 'PRIMARY_6D': 'Support Track',
    
    # Middle school streams (by focus)
    'MIDDLE_7A': 'Science Focus', 'MIDDLE_7B': 'Mathematics Focus', 'MIDDLE_7C': 'Language Arts Focus',
    'MIDDLE_7D': 'Technology Focus', 'MIDDLE_7E': 'Arts & Humanities', 'MIDDLE_7F': 'General Studies',
    'MIDDLE_8A': 'Science Focus', 'MIDDLE_8B': 'Mathematics Focus', 'MIDDLE_8C': 'Language Arts Focus',
    'MIDDLE_8D': 'Technology Focus', 'MIDDLE_8E': 'Arts & Humanities', 'MIDDLE_8F': 'General Studies',
    'MIDDLE_9A': 'Science Focus', 'MIDDLE_9B': 'Mathematics Focus', 'MIDDLE_9C': 'Language Arts Focus',
    'MIDDLE_9D': 'Technology Focus', 'MIDDLE_9E': 'Arts & Humanities', 'MIDDLE_9F': 'General Studies',
    
    # High school streams (by track)
    'HIGH_10A': 'STEM Track', 'HIGH_10B': 'Business Track', 'HIGH_10C': 'Liberal Arts',
    'HIGH_10D': 'Creative Arts', 'HIGH_10E': 'Technical/Vocational', 'HIGH_10F': 'International Baccalaureate',
    'HIGH_11A': 'STEM Track', 'HIGH_11B': 'Business Track', 'HIGH_11C': 'Liberal Arts',
    'HIGH_11D': 'Creative Arts', 'HIGH_11E': 'Technical/Vocational', 'HIGH_11F': 'International Baccalaureate',
    'HIGH_12A': 'STEM Track', 'HIGH_12B': 'Business Track', 'HIGH_12C': 'Liberal Arts',
    'HIGH_12D': 'Creative Arts', 'HIGH_12E': 'Technical/Vocational', 'HIGH_12F': 'International Baccalaureate',
}

CLASS_GRADES = {
    # Primary grades
    'PRIMARY_1A': 1, 'PRIMARY_1B': 1, 'PRIMARY_1C': 1, 'PRIMARY_1D': 1,
    'PRIMARY_2A': 2, 'PRIMARY_2B': 2, 'PRIMARY_2C': 2, 'PRIMARY_2D': 2,
    'PRIMARY_3A': 3, 'PRIMARY_3B': 3, 'PRIMARY_3C': 3, 'PRIMARY_3D': 3,
    'PRIMARY_4A': 4, 'PRIMARY_4B': 4, 'PRIMARY_4C': 4, 'PRIMARY_4D': 4,
    'PRIMARY_5A': 5, 'PRIMARY_5B': 5, 'PRIMARY_5C': 5, 'PRIMARY_5D': 5,
    'PRIMARY_6A': 6, 'PRIMARY_6B': 6, 'PRIMARY_6C': 6, 'PRIMARY_6D': 6,
    
    # Middle school grades
    'MIDDLE_7A': 7, 'MIDDLE_7B': 7, 'MIDDLE_7C': 7, 'MIDDLE_7D': 7, 'MIDDLE_7E': 7, 'MIDDLE_7F': 7,
    'MIDDLE_8A': 8, 'MIDDLE_8B': 8, 'MIDDLE_8C': 8, 'MIDDLE_8D': 8, 'MIDDLE_8E': 8, 'MIDDLE_8F': 8,
    'MIDDLE_9A': 9, 'MIDDLE_9B': 9, 'MIDDLE_9C': 9, 'MIDDLE_9D': 9, 'MIDDLE_9E': 9, 'MIDDLE_9F': 9,
    
    # High school grades
    'HIGH_10A': 10, 'HIGH_10B': 10, 'HIGH_10C': 10, 'HIGH_10D': 10, 'HIGH_10E': 10, 'HIGH_10F': 10,
    'HIGH_11A': 11, 'HIGH_11B': 11, 'HIGH_11C': 11, 'HIGH_11D': 11, 'HIGH_11E': 11, 'HIGH_11F': 11,
    'HIGH_12A': 12, 'HIGH_12B': 12, 'HIGH_12C': 12, 'HIGH_12D': 12, 'HIGH_12E': 12, 'HIGH_12F': 12,
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
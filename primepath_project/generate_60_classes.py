#!/usr/bin/env python
"""
Generate 60 Class Codes with Classification System
For Teacher Assessment Module

Classification Structure:
- Primary (Grades 1-6): 24 classes
- Middle School (Grades 7-9): 18 classes  
- High School (Grades 10-12): 18 classes

Each grade has multiple streams/sections for differentiated learning.

Created: August 18, 2025
"""

def generate_class_structure():
    """Generate 60 classes with proper classification"""
    
    classes = []
    
    # PRIMARY SCHOOL (Grades 1-6) - 24 classes total
    # Each grade has 4 sections: A (Advanced), B (Standard), C (Foundation), D (Support)
    primary_grades = [1, 2, 3, 4, 5, 6]
    primary_sections = ['A', 'B', 'C', 'D']
    
    for grade in primary_grades:
        for section in primary_sections:
            class_code = f"PRIMARY_{grade}{section}"
            class_name = f"Primary Grade {grade}{section}"
            
            if section == 'A':
                stream = "Advanced Track"
            elif section == 'B':
                stream = "Standard Track"
            elif section == 'C':
                stream = "Foundation Track"
            else:  # D
                stream = "Support Track"
                
            classes.append({
                'code': class_code,
                'name': class_name,
                'category': 'PRIMARY',
                'grade': grade,
                'section': section,
                'stream': stream,
                'description': f"Primary education for Grade {grade} students in {stream}"
            })
    
    # MIDDLE SCHOOL (Grades 7-9) - 18 classes total
    # Each grade has 6 sections: A-F with different focuses
    middle_grades = [7, 8, 9]
    middle_sections = {
        'A': 'Science Focus',
        'B': 'Mathematics Focus', 
        'C': 'Language Arts Focus',
        'D': 'Technology Focus',
        'E': 'Arts & Humanities',
        'F': 'General Studies'
    }
    
    for grade in middle_grades:
        for section, focus in middle_sections.items():
            class_code = f"MIDDLE_{grade}{section}"
            class_name = f"Middle School Grade {grade}{section}"
            
            classes.append({
                'code': class_code,
                'name': class_name,
                'category': 'MIDDLE',
                'grade': grade,
                'section': section,
                'stream': focus,
                'description': f"Middle school Grade {grade} with {focus} specialization"
            })
    
    # HIGH SCHOOL (Grades 10-12) - 18 classes total
    # Each grade has 6 sections: Different academic tracks
    high_grades = [10, 11, 12]
    high_sections = {
        'A': 'STEM Track',
        'B': 'Business Track',
        'C': 'Liberal Arts',
        'D': 'Creative Arts',
        'E': 'Technical/Vocational',
        'F': 'International Baccalaureate'
    }
    
    for grade in high_grades:
        for section, track in high_sections.items():
            class_code = f"HIGH_{grade}{section}"
            class_name = f"High School Grade {grade}{section}"
            
            classes.append({
                'code': class_code,
                'name': class_name,
                'category': 'HIGH',
                'grade': grade,
                'section': section,
                'stream': track,
                'description': f"High school Grade {grade} in {track} program"
            })
    
    return classes

def generate_django_choices():
    """Generate Django model choices format"""
    
    classes = generate_class_structure()
    
    print("="*80)
    print("DJANGO MODEL CHOICES FOR 60 CLASSES")
    print("="*80)
    print()
    
    # Generate choices tuple format
    choices = []
    
    print("CLASS_CODE_CHOICES = [")
    
    # Group by category for better organization
    categories = ['PRIMARY', 'MIDDLE', 'HIGH']
    
    for category in categories:
        print(f"    # {category} SCHOOL")
        category_classes = [c for c in classes if c['category'] == category]
        
        for cls in category_classes:
            choice_tuple = f"    ('{cls['code']}', '{cls['name']}'),"
            print(choice_tuple)
            choices.append((cls['code'], cls['name']))
        
        print()
    
    print("]")
    print()
    print(f"# Total classes: {len(choices)}")
    
    # Generate classification helpers
    print("\n" + "="*50)
    print("CLASSIFICATION HELPERS")
    print("="*50)
    
    print("\nCLASS_CATEGORIES = {")
    for category in categories:
        category_classes = [c for c in classes if c['category'] == category]
        codes = [c['code'] for c in category_classes]
        print(f"    '{category}': {codes},")
    print("}")
    
    print("\nCLASS_STREAMS = {")
    for cls in classes:
        print(f"    '{cls['code']}': '{cls['stream']}',")
    print("}")
    
    print("\nCLASS_GRADES = {")
    for cls in classes:
        print(f"    '{cls['code']}': {cls['grade']},")
    print("}")
    
    return classes, choices

def generate_summary_stats():
    """Generate summary statistics"""
    
    classes = generate_class_structure()
    
    print("\n" + "="*80)
    print("CLASS DISTRIBUTION SUMMARY")
    print("="*80)
    
    # By category
    categories = {}
    for cls in classes:
        cat = cls['category']
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1
    
    for cat, count in categories.items():
        print(f"{cat} SCHOOL: {count} classes")
    
    print(f"\nTOTAL: {len(classes)} classes")
    
    # By grade level
    print("\nGRADE DISTRIBUTION:")
    grades = {}
    for cls in classes:
        grade = cls['grade']
        if grade not in grades:
            grades[grade] = []
        grades[grade].append(cls['code'])
    
    for grade in sorted(grades.keys()):
        print(f"  Grade {grade}: {len(grades[grade])} classes ({', '.join(grades[grade])})")
    
    # By stream type
    print("\nSTREAM DISTRIBUTION:")
    streams = {}
    for cls in classes:
        stream = cls['stream']
        if stream not in streams:
            streams[stream] = 0
        streams[stream] += 1
    
    for stream, count in sorted(streams.items()):
        print(f"  {stream}: {count} classes")

if __name__ == '__main__':
    print("GENERATING 60 CLASS STRUCTURE WITH CLASSIFICATION")
    print("="*80)
    
    classes, choices = generate_django_choices()
    generate_summary_stats()
    
    print("\n" + "="*80)
    print("SAMPLE CLASS DETAILS")
    print("="*80)
    
    # Show sample from each category
    sample_classes = [
        classes[0],    # Primary
        classes[24],   # Middle  
        classes[42]    # High
    ]
    
    for cls in sample_classes:
        print(f"\nCode: {cls['code']}")
        print(f"Name: {cls['name']}")
        print(f"Category: {cls['category']}")
        print(f"Grade: {cls['grade']}")
        print(f"Section: {cls['section']}")
        print(f"Stream: {cls['stream']}")
        print(f"Description: {cls['description']}")
    
    print("\n" + "="*80)
    print("✅ Ready to implement in Django models!")
    print("Copy the CLASS_CODE_CHOICES above into your models.")
    print("="*80)
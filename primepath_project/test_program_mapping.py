"""
Test PROGRAM_MAPPING for PINNACLE classes
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from primepath_routinetest.class_code_mapping import get_class_codes_by_program, CLASS_CODE_CURRICULUM_MAPPING

def test_program_mapping():
    print("\n=== TESTING PROGRAM MAPPING ===\n")
    
    # Get PINNACLE classes from mapping function
    pinnacle_classes = get_class_codes_by_program('PINNACLE')
    
    print(f"PINNACLE classes from get_class_codes_by_program: {len(pinnacle_classes)}")
    print(f"Classes: {pinnacle_classes}")
    
    # Check if PINNACLE classes are in CLASS_CODE_CURRICULUM_MAPPING
    print("\n=== PINNACLE in CLASS_CODE_CURRICULUM_MAPPING ===")
    pinnacle_in_mapping = [k for k in CLASS_CODE_CURRICULUM_MAPPING.keys() if k.startswith('PINNACLE')]
    print(f"Found {len(pinnacle_in_mapping)} PINNACLE classes:")
    for code in pinnacle_in_mapping:
        print(f"  {code}: {CLASS_CODE_CURRICULUM_MAPPING[code]}")
    
    # Check what get_class_codes_by_program returns
    print("\n=== ALL PROGRAM MAPPINGS ===")
    for program in ['CORE', 'ASCENT', 'EDGE', 'PINNACLE']:
        classes = get_class_codes_by_program(program)
        print(f"{program}: {len(classes)} classes")
        if program == 'PINNACLE':
            print(f"  Details: {classes}")

if __name__ == "__main__":
    test_program_mapping()
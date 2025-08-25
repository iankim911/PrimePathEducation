#!/usr/bin/env python
"""
Test script to verify class code updates
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from primepath_routinetest.models.class_constants import CLASS_CODE_CHOICES
from primepath_routinetest.services.exam_service import ExamService

def test_class_constants():
    """Test that class constants are updated correctly"""
    print("=" * 60)
    print("TESTING CLASS CODE UPDATES")
    print("=" * 60)
    
    # Expected classes from screenshot
    expected_classes = [
        'PS1', 'P1', 'P2', 'A2', 'B2', 'B3', 'B4', 'B5', 'S2',
        'H1', 'H2', 'H4', 'C2', 'C3', 'C4', 'C5',
        'Young-cho2', 'Young-choM', 'Chung-choM', 'Chung-cho1',
        'SejongM', 'MAS', 'TaejoG', 'TaejoD', 'TaejoDC',
        'SungjongM', 'Sungjong2', 'Sungjong3', 'SungjongC',
        'D2', 'D3', 'D4',
        'High1_SaiSun_3-5', 'High1_SaiSun_5-7',
        'High1V2_SaiSun_11-1', 'High1V2_SaiSun_1-3'
    ]
    
    # Get actual class codes
    actual_codes = [code for code, _ in CLASS_CODE_CHOICES]
    
    print(f"\n✓ Total classes defined: {len(actual_codes)}")
    print(f"✓ Expected classes: {len(expected_classes)}")
    
    # Check for missing classes
    missing = set(expected_classes) - set(actual_codes)
    if missing:
        print(f"\n✗ Missing classes: {missing}")
    else:
        print("\n✓ All expected classes are present")
    
    # Check for old classes that should be removed
    old_classes = ['PRIMARY_1A', 'MIDDLE_7A', 'HIGH_10A']
    found_old = [c for c in old_classes if c in actual_codes]
    if found_old:
        print(f"\n✗ Old classes still present (should be removed): {found_old}")
    else:
        print("✓ No old class codes found (good!)")
    
    # Test PROGRAM_CLASS_MAPPING
    print("\n" + "=" * 60)
    print("TESTING PROGRAM CLASS MAPPING")
    print("=" * 60)
    
    for program, classes in ExamService.PROGRAM_CLASS_MAPPING.items():
        print(f"\n{program}: {len(classes)} classes")
        # Check first few classes to verify they're updated
        sample = classes[:3] if len(classes) >= 3 else classes
        print(f"  Sample: {sample}")
        
        # Verify no old classes
        old_in_program = [c for c in classes if c.startswith(('PRIMARY_', 'MIDDLE_', 'HIGH_'))]
        if old_in_program:
            print(f"  ✗ Old classes found: {old_in_program[:3]}...")
    
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)
    
    # Summary
    if not missing and not found_old:
        print("\n✅ ALL TESTS PASSED - Class codes updated successfully!")
    else:
        print("\n⚠️ Some issues found - please review above")
    
    return not missing and not found_old

if __name__ == "__main__":
    success = test_class_constants()
    sys.exit(0 if success else 1)
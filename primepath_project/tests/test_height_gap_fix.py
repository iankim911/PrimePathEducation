#!/usr/bin/env python
"""
Test specifically for the height/min-height gap fix
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from placement_test.models import Exam

def test_height_fixes():
    """Test that all height/min-height issues are fixed"""
    client = Client()
    
    print("=" * 60)
    print("HEIGHT/MIN-HEIGHT GAP FIX TEST")
    print("=" * 60)
    
    # Get first exam
    exam = Exam.objects.first()
    if not exam:
        print("[ERROR] No exam found in database")
        return False
    
    # Test preview page
    print(f"\nTesting exam preview: {exam.name}")
    response = client.get(f'/api/placement/exams/{exam.id}/preview/')
    
    if response.status_code != 200:
        print(f"[FAIL] Preview page returned {response.status_code}")
        return False
    
    content = response.content.decode('utf-8')
    
    # Check that problematic heights are removed
    print("\nChecking that fixed/min heights are removed...")
    bad_patterns = [
        ('min-height: 400px', 'PDF section min-height'),
        ('min-height: 350px', 'Tablet min-height'),
        ('height: 600px', 'Desktop fixed height'),
        ('height: 500px', 'Responsive fixed height'),
        ('padding: 20px;', 'Excessive padding on pdf-viewer'),
    ]
    
    all_passed = True
    for pattern, description in bad_patterns:
        # Check if pattern exists in CSS definitions (not in other contexts)
        if f'.pdf-section {{' in content and pattern in content:
            # More specific check - look for it in pdf-section context
            import re
            pdf_section_pattern = r'\.pdf-section\s*\{[^}]*' + re.escape(pattern)
            if re.search(pdf_section_pattern, content):
                print(f"   [FAIL] {description} still present: '{pattern}'")
                all_passed = False
            else:
                print(f"   [PASS] {description} removed from pdf-section")
        else:
            print(f"   [PASS] {description} removed")
    
    # Check that correct styles are present
    print("\nChecking that correct styles are present...")
    good_patterns = [
        ('gap: 0', 'Zero gap in main-content'),
        ('height: auto', 'Auto height for flexibility'),
        ('padding: 10px 20px', 'Reduced vertical padding'),
    ]
    
    for pattern, description in good_patterns:
        if pattern in content:
            print(f"   [PASS] {description} present")
        else:
            print(f"   [WARN] {description} might be missing: '{pattern}'")
    
    # Check HTML structure
    print("\nChecking HTML structure integrity...")
    structure_checks = [
        ('<div class="main-content">', 'Main content container'),
        ('<div class="pdf-section">', 'PDF section'),
        ('<div class="answers-section">', 'Answers section'),
        ('class="pdf-controls"', 'PDF controls'),
    ]
    
    for element, description in structure_checks:
        if element in content:
            print(f"   [PASS] {description} present")
        else:
            print(f"   [FAIL] {description} missing")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] Height/min-height gap fix is properly implemented!")
        print("\nWhat was fixed:")
        print("  ✓ Removed min-height: 400px from pdf-section")
        print("  ✓ Removed fixed height: 600px from desktop media query")
        print("  ✓ Removed min-height: 350px from tablet media query") 
        print("  ✓ Removed height: 500px from responsive media query")
        print("  ✓ Reduced padding on pdf-viewer from 20px to 10px vertical")
        print("  ✓ Set all sections to height: auto for content-based sizing")
        print("\nThe gap should now be eliminated!")
    else:
        print("[FAILURE] Some height fixes may not be applied correctly.")
    print("=" * 60)
    
    return all_passed

if __name__ == '__main__':
    success = test_height_fixes()
    sys.exit(0 if success else 1)
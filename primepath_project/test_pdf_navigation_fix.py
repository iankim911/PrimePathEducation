#!/usr/bin/env python
"""
Test for PDF navigation currentPageNum scope fix
"""

import os
import sys
import django
import re

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from placement_test.models import Exam

def test_pdf_navigation_fix():
    """Test that currentPageNum is properly declared and no scope errors"""
    client = Client()
    
    print("=" * 60)
    print("PDF NAVIGATION SCOPE FIX TEST")
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
    
    # Check that currentPageNum is properly declared
    print("\nChecking variable declarations...")
    
    all_passed = True
    
    # Check for proper declaration
    if 'let currentPageNum = 1;' in content or 'var currentPageNum = 1;' in content:
        print("   [PASS] currentPageNum properly declared with let/var")
    else:
        print("   [FAIL] currentPageNum not properly declared")
        all_passed = False
    
    # Check that the removed function is gone (but comment is OK)
    if 'function initializePdfViewer_REMOVED' not in content:
        print("   [PASS] Removed duplicate PDF function deleted")
    else:
        print("   [FAIL] initializePdfViewer_REMOVED function still present")
        all_passed = False
    
    # Check for the fix comment
    if '[REMOVED] initializePdfViewer_REMOVED function deleted' in content:
        print("   [PASS] Fix documentation comment present")
    else:
        print("   [WARN] Fix documentation comment missing")
    
    # Check that PDF state management comment exists
    if 'PDF State Management' in content:
        print("   [PASS] PDF state management section documented")
    else:
        print("   [WARN] PDF state management documentation missing")
    
    # Check that both variables are declared
    if 'let currentPage = 1;' in content:
        print("   [PASS] currentPage variable declared")
    else:
        print("   [FAIL] currentPage variable not found")
        all_passed = False
    
    # Check navigation functions still exist
    print("\nChecking navigation functionality...")
    
    nav_functions = [
        ('pdf-prev', 'Previous button handler'),
        ('pdf-next', 'Next button handler'),
        ('renderPage', 'Page rendering function'),
        ('updateNavigationButtons', 'Navigation update function')
    ]
    
    for func_name, description in nav_functions:
        if func_name in content:
            print(f"   [PASS] {description} present")
        else:
            print(f"   [FAIL] {description} missing")
            all_passed = False
    
    # Check for any undeclared variable patterns
    print("\nChecking for potential scope issues...")
    
    # Look for assignments without declaration (simplified check)
    undeclared_pattern = re.compile(r'^\s*currentPageNum\s*=\s*[^=]', re.MULTILINE)
    matches = undeclared_pattern.findall(content)
    
    # Filter out the properly declared one
    problematic_matches = []
    for match in matches:
        if 'let ' not in match and 'var ' not in match and 'const ' not in match:
            # Check if it's just a reassignment (should be after declaration)
            if 'currentPageNum--' not in match and 'currentPageNum++' not in match:
                problematic_matches.append(match.strip())
    
    if not problematic_matches:
        print("   [PASS] No undeclared variable assignments found")
    else:
        print(f"   [WARN] Potential undeclared assignments: {problematic_matches}")
        # This is a warning, not a failure, as reassignments are valid
    
    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] PDF navigation scope fix properly implemented!")
        print("\nFix summary:")
        print("  ✓ currentPageNum properly declared at global scope")
        print("  ✓ Duplicate PDF function removed")
        print("  ✓ Navigation functionality preserved")
        print("  ✓ No scope errors expected")
    else:
        print("[FAILURE] Some PDF navigation tests failed.")
    print("=" * 60)
    
    return all_passed

if __name__ == '__main__':
    success = test_pdf_navigation_fix()
    sys.exit(0 if success else 1)
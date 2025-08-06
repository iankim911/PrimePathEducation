#!/usr/bin/env python
"""
Test specifically for the gap fix between PDF and Answer Keys sections
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from placement_test.models import Exam

def test_gap_fix():
    """Test that the gap fix CSS is properly applied"""
    client = Client()
    
    print("=" * 60)
    print("GAP FIX SPECIFIC TEST")
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
    
    # Check for the gap fix CSS
    print("\nChecking for gap fix CSS...")
    tests = [
        ('gap: 0', 'Main content has zero gap'),
        ('.pdf-section + .answers-section', 'Adjacent sibling selector present'),
        ('border-top: none !important', 'Border removal for direct adjacency'),
        ('margin-top: 0 !important', 'Margin removal for direct adjacency'),
        ('margin: 0;', 'PDF controls margin set to 0'),
    ]
    
    all_passed = True
    for test_string, description in tests:
        if test_string in content:
            print(f"   [PASS] {description}")
        else:
            print(f"   [FAIL] {description} - '{test_string}' not found")
            all_passed = False
    
    # Check for removed aggressive fixes
    print("\nChecking that aggressive fixes are removed...")
    bad_strings = [
        'ULTRA AGGRESSIVE',
        '[GAP FIX]',
        'gap: 0 !important',
        'mainContent.style.gap',
    ]
    
    for bad_string in bad_strings:
        if bad_string in content:
            print(f"   [FAIL] Found remnant of aggressive fix: '{bad_string}'")
            all_passed = False
        else:
            print(f"   [PASS] No '{bad_string}' found")
    
    # Check HTML structure
    print("\nChecking HTML structure...")
    if '<div class="main-content">' in content:
        print("   [PASS] Main content div present")
    else:
        print("   [FAIL] Main content div not found")
        all_passed = False
    
    if '<div class="pdf-section">' in content:
        print("   [PASS] PDF section present")
    else:
        print("   [FAIL] PDF section not found")
        all_passed = False
    
    if '<div class="answers-section">' in content:
        print("   [PASS] Answers section present")
    else:
        print("   [FAIL] Answers section not found")
        all_passed = False
    
    # Check audio files condition
    print("\nChecking audio files handling...")
    if exam.audio_files.exists():
        if '<div class="audio-files-section">' in content:
            print(f"   [PASS] Audio section present (exam has {exam.audio_files.count()} audio files)")
        else:
            print(f"   [FAIL] Audio section missing but exam has {exam.audio_files.count()} audio files")
            all_passed = False
    else:
        if '<div class="audio-files-section">' not in content:
            print("   [PASS] Audio section correctly absent (exam has no audio files)")
        else:
            print("   [FAIL] Audio section present but exam has no audio files")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] Gap fix is properly implemented!")
        print("The CSS precisely targets the gap issue without disrupting other features.")
    else:
        print("[FAILURE] Some gap fix tests failed. Please review.")
    print("=" * 60)
    
    return all_passed

if __name__ == '__main__':
    success = test_gap_fix()
    sys.exit(0 if success else 1)
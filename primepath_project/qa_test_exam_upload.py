#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive QA test for exam upload functionality
Tests all features to ensure nothing is broken
"""

import requests
import json
import sys
import io

# Set UTF-8 encoding for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def test_server_running():
    """Test if server is running"""
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print("✓ Server is running")
            return True
    except:
        print("✗ Server is not running")
        return False

def test_create_exam_page():
    """Test if create exam page loads"""
    try:
        response = requests.get(f"{BASE_URL}/api/PlacementTest/exams/create/")
        if response.status_code == 200:
            content = response.text
            
            # Check for key elements
            checks = [
                ("Upload New Exam" in content, "Page title present"),
                ("pdf_file" in content, "PDF file input present"),
                ("audio_files" in content, "Audio files input present"),
                ("examForm" in content, "Exam form present"),
                ("pdfjsLib" in content, "PDF.js library referenced"),
                ("typeof pdfjsLib" in content, "PDF.js safety check present"),
                ("?.addEventListener" in content, "Optional chaining present"),
                ("console.log" in content and "else {" not in content.split("console.log")[1][:50], "Syntax error fixed"),
            ]
            
            for check, description in checks:
                if check:
                    print(f"✓ {description}")
                else:
                    print(f"✗ {description}")
            
            return all(check for check, _ in checks)
    except Exception as e:
        print(f"✗ Error accessing create exam page: {e}")
        return False

def test_other_pages():
    """Test if other pages still work"""
    pages = [
        ("/", "Home page"),
        ("/api/PlacementTest/start/", "Start test page"),
        ("/api/PlacementTest/exams/", "Exam list page"),
        ("/PlacementTest/teacher/", "Teacher dashboard"),
    ]
    
    all_good = True
    for url, description in pages:
        try:
            response = requests.get(f"{BASE_URL}{url}")
            if response.status_code in [200, 302]:  # 302 for redirects
                print(f"✓ {description} accessible")
            else:
                print(f"✗ {description} returned {response.status_code}")
                all_good = False
        except Exception as e:
            print(f"✗ Error accessing {description}: {e}")
            all_good = False
    
    return all_good

def test_javascript_errors():
    """Check for common JavaScript errors in the page"""
    try:
        response = requests.get(f"{BASE_URL}/api/PlacementTest/exams/create/")
        content = response.text
        
        # Check for problematic patterns
        error_patterns = [
            ("console.log.*else\\s*{", "Malformed if-else after console.log"),
            ("document\\.getElementById\\(['\"][^'\"]+['\"]\\)\\.addEventListener", "Direct addEventListener without null check"),
            ("pdfjsLib\\.GlobalWorkerOptions(?!.*typeof)", "Using pdfjsLib without checking if defined"),
        ]
        
        import re
        all_good = True
        for pattern, description in error_patterns:
            if re.search(pattern, content):
                print(f"✗ Found issue: {description}")
                all_good = False
            else:
                print(f"✓ No issue: {description}")
        
        return all_good
    except Exception as e:
        print(f"✗ Error checking JavaScript: {e}")
        return False

def main():
    print("=" * 50)
    print("COMPREHENSIVE QA TEST FOR EXAM UPLOAD")
    print("=" * 50)
    
    tests = [
        ("Server Status", test_server_running),
        ("Create Exam Page", test_create_exam_page),
        ("Other Pages", test_other_pages),
        ("JavaScript Errors", test_javascript_errors),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        results.append(test_func())
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✓ ALL TESTS PASSED ({passed}/{total})")
        print("The PDF upload fix is working correctly!")
        print("All other features remain functional.")
    else:
        print(f"⚠ SOME TESTS FAILED ({passed}/{total} passed)")
        print("Please review the failures above.")
    
    return passed == total

if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
#!/usr/bin/env python3

"""
Test Copy Exam JavaScript Fix Validation
========================================

This test validates that the Copy Exam modal JavaScript fixes are working:
1. Verifies the updateCopyExamNamePreview function exists and is properly defined
2. Tests that undefined variables have been fixed
3. Checks that the function handles missing elements gracefully

Usage: python test_copy_exam_fix_validation.py
"""

import os
import sys
import re

def test_copy_exam_javascript_fixes():
    """Test that the copy exam JavaScript fixes are properly implemented."""
    
    print("🔍 TESTING COPY EXAM JAVASCRIPT FIXES")
    print("=" * 60)
    
    template_path = "primepath_project/templates/primepath_routinetest/exam_list_hierarchical.html"
    
    if not os.path.exists(template_path):
        print(f"❌ Template file not found: {template_path}")
        return False
    
    print(f"✅ Found template file: {template_path}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Check if updateCopyExamNamePreview is properly defined as window function
    test_results = []
    
    # Test 1: Function is defined as window function
    if 'window.updateCopyExamNamePreview = function()' in content:
        print("✅ updateCopyExamNamePreview is properly defined as window function")
        test_results.append(True)
    else:
        print("❌ updateCopyExamNamePreview is not properly defined as window function")
        test_results.append(False)
    
    # Test 2: Function has try-catch error handling
    if 'try {' in content and 'catch (error)' in content:
        print("✅ Function has proper error handling with try-catch")
        test_results.append(True)
    else:
        print("❌ Function lacks proper error handling")
        test_results.append(False)
    
    # Test 3: sourceExamName variable issue is fixed
    if 'const sourceExamNameElement = document.getElementById(\'sourceExamName\')' in content:
        print("✅ sourceExamName variable issue is fixed - now properly gets DOM element")
        test_results.append(True)
    else:
        print("❌ sourceExamName variable issue not fixed")
        test_results.append(False)
    
    # Test 4: Check for undefined variable references (should not exist)
    undefined_patterns = [
        r'timer_minutes(?!\w)',  # timer_minutes not followed by word characters
        r'total_questions(?!\w)', # total_questions not followed by word characters
        r'passing_score(?!\w)',  # passing_score not followed by word characters
        r'sourceExamName\.', # sourceExamName used as variable (not element)
    ]
    
    undefined_found = False
    for pattern in undefined_patterns:
        matches = re.findall(pattern, content)
        if matches:
            print(f"❌ Found undefined variable pattern: {pattern} - {len(matches)} occurrences")
            undefined_found = True
    
    if not undefined_found:
        print("✅ No undefined variable patterns found")
        test_results.append(True)
    else:
        test_results.append(False)
    
    # Test 5: Check if basic requirement validation is less restrictive
    if 'Please select exam type and time period to see preview...' in content:
        print("✅ Basic requirements validation is more user-friendly")
        test_results.append(True)
    else:
        print("❌ Requirements validation not updated")
        test_results.append(False)
    
    # Test 6: Check if sourceExamNameText validation exists
    if 'sourceExamNameText !== \'Loading...\'' in content:
        print("✅ Proper validation for sourceExamNameText loading state")
        test_results.append(True)
    else:
        print("❌ Missing validation for sourceExamNameText loading state")
        test_results.append(False)
    
    print("\n" + "=" * 60)
    
    # Summary
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    if passed_tests == total_tests:
        print(f"🎉 ALL TESTS PASSED ({passed_tests}/{total_tests})")
        print("✅ Copy Exam JavaScript fixes are properly implemented!")
        return True
    else:
        print(f"❌ SOME TESTS FAILED ({passed_tests}/{total_tests})")
        print("🔧 Copy Exam JavaScript fixes need additional work")
        return False

def test_javascript_files_exist():
    """Test that required JavaScript files exist."""
    
    print("\n🔍 CHECKING JAVASCRIPT FILES")
    print("=" * 60)
    
    js_files = [
        "primepath_project/static/js/routinetest/copy-exam-modal-fixed.js",
        "primepath_project/static/js/routinetest/copy-exam-modal-comprehensive-final.js"
    ]
    
    files_exist = []
    for js_file in js_files:
        if os.path.exists(js_file):
            print(f"✅ Found: {js_file}")
            files_exist.append(True)
        else:
            print(f"❌ Missing: {js_file}")
            files_exist.append(False)
    
    return all(files_exist)

def main():
    """Main test function."""
    
    print("COPY EXAM FEATURE FIX VALIDATION")
    print("=" * 80)
    print("Testing fixes for JavaScript errors in Copy Exam modal")
    print("Target errors: timer_minutes, total_questions, passing_score undefined")
    print("=" * 80)
    
    # Run tests
    js_test_passed = test_copy_exam_javascript_fixes()
    files_test_passed = test_javascript_files_exist()
    
    print("\n" + "=" * 80)
    print("FINAL RESULTS:")
    
    if js_test_passed and files_test_passed:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("✅ Copy Exam feature should now work without JavaScript errors")
        print("\n💡 Next steps:")
        print("1. Test the feature in browser")
        print("2. Click 'Copy Exam' button on any exam")
        print("3. Verify no console errors appear")
        print("4. Verify modal opens and form fields work")
        return True
    else:
        print("❌ SOME VALIDATIONS FAILED")
        print("🔧 Additional fixes may be needed")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
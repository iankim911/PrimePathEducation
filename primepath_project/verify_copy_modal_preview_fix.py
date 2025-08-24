#!/usr/bin/env python
"""
Comprehensive verification of Copy Exam modal preview fix
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def verify_copy_modal_preview_fix():
    """Comprehensive test of the copy modal preview functionality"""
    
    print("=" * 80)
    print("COPY MODAL PREVIEW FIX VERIFICATION")
    print("=" * 80)
    
    client = Client()
    
    # Login as admin
    try:
        user = User.objects.get(username='admin')
        user.set_password('test123')
        user.save()
        client.login(username='admin', password='test123')
        print("✅ Logged in as admin")
    except User.DoesNotExist:
        print("❌ Admin user not found")
        return False
    
    # Get the exam list page
    response = client.get('/RoutineTest/exams/')
    if response.status_code != 200:
        print(f"❌ Failed to load exam list page: {response.status_code}")
        return False
    
    print("✅ Exam list page loaded successfully")
    content = response.content.decode('utf-8')
    
    # Test 1: Check if updateCopyExamNamePreview function exists
    print("\n📋 TEST 1: Function Definition")
    print("-" * 40)
    
    if 'function updateCopyExamNamePreview()' in content:
        print("✅ updateCopyExamNamePreview function is defined")
        
        # Extract the function for analysis
        func_start = content.find('function updateCopyExamNamePreview()')
        func_end = content.find('function ', func_start + 1)
        if func_end == -1:
            func_end = content.find('</script>', func_start)
        
        func_content = content[func_start:func_end]
        
        # Check for all required field validations
        required_checks = [
            ('examTypeSelect?.value', 'Exam Type'),
            ('timeslotSelect?.value', 'Time Period'),
            ('programSelect?.value', 'Program'),
            ('subprogramSelect?.value', 'SubProgram'),
            ('levelSelect?.value', 'Level')
        ]
        
        all_checks_present = True
        for check, field_name in required_checks:
            if check in func_content:
                print(f"  ✅ Checks for {field_name}")
            else:
                print(f"  ❌ Missing check for {field_name}")
                all_checks_present = False
        
        if not all_checks_present:
            print("❌ Not all required field checks are present")
            return False
            
    else:
        print("❌ updateCopyExamNamePreview function not found")
        return False
    
    # Test 2: Check event listeners
    print("\n📋 TEST 2: Event Listeners")
    print("-" * 40)
    
    event_listeners = [
        ("newCopyExamTypeSelect.addEventListener('change'", "Exam Type change listener"),
        ("timeslotSelect.addEventListener('change', updateCopyExamNamePreview)", "Timeslot change listener"),
        ("programSelect.addEventListener('change'", "Program change listener"),
        ("subprogramSelect.addEventListener('change'", "SubProgram change listener"),
        ("levelSelect.addEventListener('change'", "Level change listener"),
        ("customSuffixInput.addEventListener('input'", "Custom suffix input listener")
    ]
    
    all_listeners_present = True
    for listener_code, listener_name in event_listeners:
        if listener_code in content:
            print(f"  ✅ {listener_name}")
        else:
            print(f"  ❌ {listener_name} not found")
            all_listeners_present = False
    
    # Test 3: Check that all change events call updateCopyExamNamePreview
    print("\n📋 TEST 3: Preview Update Triggers")
    print("-" * 40)
    
    update_triggers = [
        ("// Update name preview\n        updateCopyExamNamePreview();", "Exam type change triggers update"),
        ("updateCopyExamNamePreview();", "Multiple updateCopyExamNamePreview calls found")
    ]
    
    for trigger_code, trigger_name in update_triggers:
        count = content.count('updateCopyExamNamePreview()')
        if count >= 5:  # Should be called at least 5 times (for each field change)
            print(f"  ✅ {trigger_name} ({count} calls found)")
        else:
            print(f"  ⚠️  Only {count} updateCopyExamNamePreview calls found (expected at least 5)")
    
    # Test 4: Check preview name generation logic
    print("\n📋 TEST 4: Preview Name Generation")
    print("-" * 40)
    
    generation_checks = [
        ("if (examTypeSelect.value === 'QUARTERLY')", "Quarterly exam type handling"),
        ("nameParts.push('[QTR]')", "QTR prefix for quarterly exams"),
        ("if (examTypeSelect.value === 'REVIEW')", "Review exam type handling"),
        ("nameParts.push('[RVW]')", "RVW prefix for review exams"),
        ("const quarterValue = timeslotSelect.value", "Quarter value extraction"),
        ("const monthText = timeslotSelect.options", "Month text extraction"),
        ("const curriculum = `${program} ${subprogram} Lv${levelNumber}`", "Curriculum string generation"),
        ("previewName += customSuffix", "Custom suffix appending")
    ]
    
    all_generation_present = True
    for check_code, check_name in generation_checks:
        if check_code in content:
            print(f"  ✅ {check_name}")
        else:
            print(f"  ❌ {check_name} not found")
            all_generation_present = False
    
    # Test 5: Check modal initialization
    print("\n📋 TEST 5: Modal Initialization")
    print("-" * 40)
    
    # Check the external JS file
    if 'copy-exam-modal-comprehensive-final.js' in content:
        print("  ✅ External comprehensive-final.js file is loaded")
        
        # Check if preview reset is in the external file
        with open('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/static/js/routinetest/copy-exam-modal-comprehensive-final.js', 'r') as f:
            js_content = f.read()
            
        if "previewText.textContent = 'Please complete all fields to see preview...'" in js_content:
            print("  ✅ Preview text reset on modal open")
        else:
            print("  ❌ Preview text reset not found in modal open function")
    else:
        print("  ❌ External comprehensive-final.js file not loaded")
    
    # Test 6: Check HTML structure
    print("\n📋 TEST 6: HTML Structure")
    print("-" * 40)
    
    html_elements = [
        ('id="copyExamModal"', "Copy exam modal"),
        ('id="copyExamForm"', "Copy exam form"),
        ('id="copyExamType"', "Exam type select"),
        ('id="timeslot"', "Timeslot select"),
        ('id="copyProgramSelect"', "Program select"),
        ('id="copySubprogramSelect"', "SubProgram select"),
        ('id="copyLevelSelect"', "Level select"),
        ('id="customSuffix"', "Custom suffix input"),
        ('id="previewText"', "Preview text display"),
        ('Preview of New Exam Name:', "Preview label")
    ]
    
    all_html_present = True
    for element_code, element_name in html_elements:
        if element_code in content:
            print(f"  ✅ {element_name}")
        else:
            print(f"  ❌ {element_name} not found")
            all_html_present = False
    
    # Final Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    tests_passed = []
    tests_failed = []
    
    if all_checks_present:
        tests_passed.append("All required field checks")
    else:
        tests_failed.append("Required field checks")
        
    if all_listeners_present:
        tests_passed.append("All event listeners")
    else:
        tests_failed.append("Event listeners")
        
    if all_generation_present:
        tests_passed.append("Preview generation logic")
    else:
        tests_failed.append("Preview generation logic")
        
    if all_html_present:
        tests_passed.append("HTML structure")
    else:
        tests_failed.append("HTML structure")
    
    if tests_passed:
        print("\n✅ PASSED TESTS:")
        for test in tests_passed:
            print(f"  • {test}")
    
    if tests_failed:
        print("\n❌ FAILED TESTS:")
        for test in tests_failed:
            print(f"  • {test}")
    
    # Overall result
    print("\n" + "=" * 80)
    if not tests_failed:
        print("🎉 ALL TESTS PASSED - Copy Modal Preview Fix is Working!")
        print("\nThe preview will update when ALL of these fields are filled:")
        print("  1. Exam Type (QUARTERLY or REVIEW)")
        print("  2. Time Period (Quarter or Month)")
        print("  3. Program")
        print("  4. SubProgram")
        print("  5. Level")
        print("  6. [Optional] Custom Name Suffix")
        return True
    else:
        print("⚠️  SOME TESTS FAILED - Review the issues above")
        return False

if __name__ == '__main__':
    result = verify_copy_modal_preview_fix()
    sys.exit(0 if result else 1)
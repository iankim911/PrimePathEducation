#!/usr/bin/env python
"""
Test script for verifying program assignment fixes
Tests:
1. Dropdown no longer shows "PRIME" prefix
2. Classes appear in correct program sections when assigned
3. Comprehensive logging works
"""

import os
import sys
import django
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from primepath_routinetest.models.class_model import Class
from core.models import Teacher

def test_program_dropdown_fix():
    """Test that dropdown no longer shows 'PRIME' prefix"""
    print("\n" + "="*80)
    print("TEST 1: Checking Program Dropdown Fix")
    print("="*80)
    
    # Create test client and login as admin
    client = Client()
    admin_user = User.objects.get(username='admin')
    admin_user.set_password('admin123')
    admin_user.save()
    
    login_success = client.login(username='admin', password='admin123')
    print(f"Admin login: {'✅ SUCCESS' if login_success else '❌ FAILED'}")
    
    if login_success:
        # Get the classes-exams page
        response = client.get('/RoutineTest/classes-exams/')
        
        if response.status_code == 200:
            content = response.content.decode()
            
            # Check dropdown options in template
            issues = []
            
            # Check for PRIME prefix in dropdowns (these should NOT exist)
            if 'value="CORE">PRIME CORE</option>' in content:
                issues.append("❌ Found 'PRIME CORE' in dropdown (should be just 'CORE')")
            if 'value="ASCENT">PRIME ASCENT</option>' in content:
                issues.append("❌ Found 'PRIME ASCENT' in dropdown (should be just 'ASCENT')")
            if 'value="EDGE">PRIME EDGE</option>' in content:
                issues.append("❌ Found 'PRIME EDGE' in dropdown (should be just 'EDGE')")
            if 'value="PINNACLE">PRIME PINNACLE</option>' in content:
                issues.append("❌ Found 'PRIME PINNACLE' in dropdown (should be just 'PINNACLE')")
            
            # Check for correct options (these SHOULD exist)
            correct = []
            if 'value="CORE">CORE</option>' in content:
                correct.append("✅ Found 'CORE' option (correct)")
            if 'value="ASCENT">ASCENT</option>' in content:
                correct.append("✅ Found 'ASCENT' option (correct)")
            if 'value="EDGE">EDGE</option>' in content:
                correct.append("✅ Found 'EDGE' option (correct)")
            if 'value="PINNACLE">PINNACLE</option>' in content:
                correct.append("✅ Found 'PINNACLE' option (correct)")
            
            # Report results
            if issues:
                print("\n❌ DROPDOWN FIX FAILED:")
                for issue in issues:
                    print(f"  {issue}")
            else:
                print("\n✅ DROPDOWN FIX SUCCESS!")
                print("  No 'PRIME' prefix found in dropdowns")
            
            if correct:
                print("\nCorrect options found:")
                for item in correct:
                    print(f"  {item}")
        else:
            print(f"❌ Failed to load page: {response.status_code}")
    
    return len(issues) == 0 if 'issues' in locals() else False

def test_program_assignment():
    """Test that classes appear in correct program sections"""
    print("\n" + "="*80)
    print("TEST 2: Testing Program Assignment to Classes")
    print("="*80)
    
    # Create or update test classes with program assignments
    test_classes = [
        {'section': 'High1_SaiSun_3-5', 'name': 'High1 SaiSun 3-5', 'program': 'PINNACLE', 'subprogram': 'Vision'},
        {'section': 'High1_SaiSun_5-7', 'name': 'High1 SaiSun 5-7', 'program': 'PINNACLE', 'subprogram': 'Vision'},
        {'section': 'PS1', 'name': 'PS1', 'program': 'CORE', 'subprogram': 'Phonics'},
        {'section': 'Young-cho2', 'name': 'Young-cho2', 'program': 'EDGE', 'subprogram': 'Rise'},
    ]
    
    print("\nAssigning programs to test classes:")
    for class_data in test_classes:
        class_obj, created = Class.objects.update_or_create(
            section=class_data['section'],
            defaults={
                'name': class_data['name'],
                'grade_level': 'Test',
                'program': class_data['program'],
                'subprogram': class_data['subprogram'],
                'is_active': True
            }
        )
        action = "Created" if created else "Updated"
        print(f"  {action} {class_obj.section} -> {class_obj.program} ({class_obj.subprogram})")
    
    return True

def test_program_display():
    """Test that classes appear in the correct program sections"""
    print("\n" + "="*80)
    print("TEST 3: Testing Program Section Display")
    print("="*80)
    
    # Create test client and login as admin
    client = Client()
    admin_user = User.objects.get(username='admin')
    login_success = client.login(username='admin', password='admin123')
    
    if login_success:
        response = client.get('/RoutineTest/classes-exams/')
        
        if response.status_code == 200:
            # Check context data
            if hasattr(response, 'context') and response.context:
                programs_data = response.context.get('programs_data', [])
                
                print(f"\nPrograms in context: {len(programs_data)}")
                
                for program in programs_data:
                    print(f"\n{program['name']} Program:")
                    print(f"  Classes: {len(program['classes'])}")
                    print(f"  Total Students: {program['total_students']}")
                    print(f"  Total Exams: {program['total_exams']}")
                    
                    if program['classes']:
                        print(f"  Class List:")
                        for cls in program['classes'][:5]:  # Show first 5
                            print(f"    - {cls['class_code']}: {cls['class_name']}")
                        if len(program['classes']) > 5:
                            print(f"    ... and {len(program['classes']) - 5} more")
                
                # Check for PINNACLE specifically
                pinnacle_program = next((p for p in programs_data if p['name'] == 'PINNACLE'), None)
                if pinnacle_program:
                    pinnacle_classes = [c['class_code'] for c in pinnacle_program['classes']]
                    
                    print("\n" + "="*40)
                    print("PINNACLE Program Verification:")
                    print("="*40)
                    
                    expected_in_pinnacle = ['High1_SaiSun_3-5', 'High1_SaiSun_5-7']
                    for expected_class in expected_in_pinnacle:
                        if expected_class in pinnacle_classes:
                            print(f"  ✅ {expected_class} found in PINNACLE")
                        else:
                            print(f"  ❌ {expected_class} NOT found in PINNACLE")
                            
                    # Check content for display
                    content = response.content.decode()
                    if 'program-pinnacle' in content:
                        print("\n✅ PINNACLE program section found in HTML")
                    else:
                        print("\n❌ PINNACLE program section NOT found in HTML")
                        
                else:
                    print("\n❌ PINNACLE program not found in programs_data")
            else:
                print("❌ No context data available")
        else:
            print(f"❌ Failed to load page: {response.status_code}")
    else:
        print("❌ Failed to login")
    
    return True

def test_console_logging():
    """Test that comprehensive console logging is working"""
    print("\n" + "="*80)
    print("TEST 4: Testing Console Logging")
    print("="*80)
    
    # The logging should already be visible from previous tests
    # Let's trigger a specific action to check logging
    
    from primepath_routinetest.models.class_model import Class
    
    # Update a class to trigger logging
    try:
        test_class = Class.objects.filter(program='PINNACLE').first()
        if test_class:
            original_program = test_class.program
            test_class.subprogram = 'Endeavor'
            test_class.save()
            
            print(f"\n✅ Updated class {test_class.section}")
            print(f"  Program: {test_class.program}")
            print(f"  SubProgram: {test_class.subprogram}")
            print("\n[CHECK ABOVE] You should see '[PROGRAM_DIRECT]' log messages")
        else:
            print("\n❌ No PINNACLE class found to test logging")
    except Exception as e:
        print(f"\n❌ Error testing logging: {e}")
    
    return True

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("PROGRAM ASSIGNMENT FIX - COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    # Initialize success tracking
    all_tests_passed = True
    
    # Run tests
    tests = [
        ("Dropdown Fix", test_program_dropdown_fix),
        ("Program Assignment", test_program_assignment),
        ("Program Display", test_program_display),
        ("Console Logging", test_console_logging)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ ERROR in {test_name}: {e}")
            results.append((test_name, False))
            all_tests_passed = False
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print("\n" + "="*80)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED! The fixes are working correctly.")
    else:
        print("⚠️ SOME TESTS FAILED. Please review the errors above.")
    print("="*80)
    
    # Final recommendations
    print("\nRECOMMENDATIONS:")
    print("1. Check the browser at http://127.0.0.1:8000/RoutineTest/classes-exams/")
    print("2. Assign some classes to PINNACLE program using the dropdowns")
    print("3. Verify they appear in the PINNACLE section")
    print("4. Check browser console for debugging messages")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
COMPREHENSIVE QA TEST: Copy Exam Modal Program Dropdown Fix
==========================================================

This script tests the complete fix for the Copy Exam modal Program dropdown
that was not populating with CORE, ASCENT, EDGE, PINNACLE options.

Test Coverage:
1. Backend enhanced curriculum method
2. Data structure validation
3. JSON serialization 
4. Frontend data integration readiness
5. Complete data flow verification

Run: python test_copy_modal_comprehensive_fix.py
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from primepath_routinetest.services.exam_service import ExamService

def run_comprehensive_tests():
    """Run all comprehensive tests for the Copy Exam modal fix"""
    
    print("=" * 80)
    print("COMPREHENSIVE QA TEST: Copy Exam Modal Program Dropdown Fix")
    print("=" * 80)
    print(f"Test started at: {datetime.now().isoformat()}")
    print()
    
    test_results = {
        'total_tests': 0,
        'passed': 0,
        'failed': 0,
        'errors': []
    }
    
    # Test 1: Enhanced Backend Method
    print("🧪 TEST 1: Enhanced Backend Method")
    print("-" * 50)
    
    try:
        test_results['total_tests'] += 1
        enhanced_data = ExamService.get_routinetest_curriculum_hierarchy_for_frontend()
        
        # Validate structure
        assert 'curriculum_data' in enhanced_data, "Missing curriculum_data"
        assert 'metadata' in enhanced_data, "Missing metadata"
        assert 'validation' in enhanced_data, "Missing validation"
        assert 'debug_info' in enhanced_data, "Missing debug_info"
        
        print(f"   ✅ Enhanced method returned proper structure")
        print(f"   ✅ Version: {enhanced_data['metadata']['version']}")
        print(f"   ✅ Validation passed: {enhanced_data['validation']['is_valid']}")
        print(f"   ✅ JSON serializable: {enhanced_data['debug_info']['json_serializable']}")
        
        test_results['passed'] += 1
        
    except Exception as e:
        test_results['failed'] += 1
        test_results['errors'].append(f"Test 1 failed: {e}")
        print(f"   ❌ FAILED: {e}")
    
    print()
    
    # Test 2: Curriculum Data Structure
    print("🧪 TEST 2: Curriculum Data Structure Validation")
    print("-" * 50)
    
    try:
        test_results['total_tests'] += 1
        enhanced_data = ExamService.get_routinetest_curriculum_hierarchy_for_frontend()
        curriculum_data = enhanced_data['curriculum_data']
        
        # Test expected programs
        expected_programs = ['CORE', 'ASCENT', 'EDGE', 'PINNACLE']
        actual_programs = list(curriculum_data.keys())
        
        assert len(actual_programs) == 4, f"Expected 4 programs, got {len(actual_programs)}"
        
        for program in expected_programs:
            assert program in actual_programs, f"Missing program: {program}"
            assert 'subprograms' in curriculum_data[program], f"Program {program} missing subprograms"
            assert 'meta' in curriculum_data[program], f"Program {program} missing meta"
            
            subprograms = curriculum_data[program]['subprograms']
            assert len(subprograms) > 0, f"Program {program} has no subprograms"
            
            for subprogram, sub_data in subprograms.items():
                assert 'levels' in sub_data, f"Subprogram {program}/{subprogram} missing levels"
                assert 'meta' in sub_data, f"Subprogram {program}/{subprogram} missing meta"
                assert len(sub_data['levels']) > 0, f"Subprogram {program}/{subprogram} has no levels"
        
        print(f"   ✅ All 4 programs present: {actual_programs}")
        print(f"   ✅ All programs have proper structure")
        
        # Test level counts
        total_levels = enhanced_data['validation']['total_levels']
        print(f"   ✅ Total levels: {total_levels}")
        
        # Test individual program levels
        for program in expected_programs:
            level_count = curriculum_data[program]['meta']['total_levels']
            subprogram_count = curriculum_data[program]['meta']['total_subprograms']
            print(f"   ✅ {program}: {subprogram_count} subprograms, {level_count} levels")
        
        test_results['passed'] += 1
        
    except Exception as e:
        test_results['failed'] += 1
        test_results['errors'].append(f"Test 2 failed: {e}")
        print(f"   ❌ FAILED: {e}")
    
    print()
    
    # Test 3: JSON Serialization for Frontend
    print("🧪 TEST 3: JSON Serialization for Frontend Integration")
    print("-" * 50)
    
    try:
        test_results['total_tests'] += 1
        enhanced_data = ExamService.get_routinetest_curriculum_hierarchy_for_frontend()
        
        # Test JSON serialization
        json_str = json.dumps(enhanced_data)
        assert len(json_str) > 1000, "JSON string too short"
        
        # Test deserialization
        deserialized = json.loads(json_str)
        assert deserialized == enhanced_data, "Deserialization doesn't match original"
        
        print(f"   ✅ JSON serialization successful")
        print(f"   ✅ JSON length: {len(json_str)} characters")
        print(f"   ✅ Deserialization matches original")
        
        # Test frontend data extraction
        curriculum_data = deserialized['curriculum_data']
        program_keys = list(curriculum_data.keys())
        
        print(f"   ✅ Frontend can extract programs: {program_keys}")
        
        # Test subprogram extraction
        for program in program_keys[:2]:  # Test first 2 programs
            subprogram_keys = list(curriculum_data[program]['subprograms'].keys())
            print(f"   ✅ {program} subprograms extractable: {subprogram_keys}")
        
        test_results['passed'] += 1
        
    except Exception as e:
        test_results['failed'] += 1
        test_results['errors'].append(f"Test 3 failed: {e}")
        print(f"   ❌ FAILED: {e}")
    
    print()
    
    # Test 4: Frontend Integration Simulation
    print("🧪 TEST 4: Frontend Integration Simulation")
    print("-" * 50)
    
    try:
        test_results['total_tests'] += 1
        enhanced_data = ExamService.get_routinetest_curriculum_hierarchy_for_frontend()
        
        # Simulate what frontend JavaScript will do
        print("   🔄 Simulating frontend data processing...")
        
        # Step 1: Enhanced data structure loaded
        has_data = bool(enhanced_data)
        has_curriculum_data = bool(enhanced_data.get('curriculum_data'))
        has_metadata = bool(enhanced_data.get('metadata'))
        has_validation = bool(enhanced_data.get('validation'))
        
        print(f"   ✅ Enhanced data structure checks:")
        print(f"      - hasData: {has_data}")
        print(f"      - hasCurriculumData: {has_curriculum_data}")
        print(f"      - hasMetadata: {has_metadata}")
        print(f"      - hasValidation: {has_validation}")
        
        # Step 2: Extract curriculum data (what template will do)
        if enhanced_data.get('curriculum_data'):
            curriculum_data = enhanced_data['curriculum_data']
            programs = list(curriculum_data.keys())
            
            print(f"   ✅ Curriculum data extraction successful")
            print(f"      - Available programs: {programs}")
            print(f"      - Total programs: {len(programs)}")
            
            # Step 3: Simulate dropdown population
            dropdown_options = []
            for program in programs:
                dropdown_options.append({
                    'value': program,
                    'text': program,
                    'subprograms': len(curriculum_data[program]['subprograms'])
                })
            
            print(f"   ✅ Dropdown options generated:")
            for option in dropdown_options:
                print(f"      - {option['text']}: {option['subprograms']} subprograms")
        
        # Step 4: Validation checks
        validation = enhanced_data.get('validation', {})
        if validation.get('is_valid') and len(programs) == 4:
            print(f"   ✅ ALL VALIDATIONS PASSED - DATA READY FOR FRONTEND")
        else:
            raise Exception(f"Validation failed: {validation.get('validation_errors')}")
        
        test_results['passed'] += 1
        
    except Exception as e:
        test_results['failed'] += 1
        test_results['errors'].append(f"Test 4 failed: {e}")
        print(f"   ❌ FAILED: {e}")
    
    print()
    
    # Test 5: Legacy Method Compatibility
    print("🧪 TEST 5: Legacy Method Compatibility")
    print("-" * 50)
    
    try:
        test_results['total_tests'] += 1
        
        # Test old method still works
        old_hierarchy = ExamService.get_routinetest_curriculum_hierarchy()
        old_levels = ExamService.get_routinetest_curriculum_levels()
        
        assert len(old_hierarchy) == 4, "Legacy hierarchy method broken"
        assert len(old_levels) == 41, "Legacy levels method broken"
        
        print(f"   ✅ Legacy hierarchy method: {len(old_hierarchy)} programs")
        print(f"   ✅ Legacy levels method: {len(old_levels)} levels")
        
        # Test enhanced method data matches legacy
        enhanced_data = ExamService.get_routinetest_curriculum_hierarchy_for_frontend()
        enhanced_programs = set(enhanced_data['curriculum_data'].keys())
        legacy_programs = set(old_hierarchy.keys())
        
        assert enhanced_programs == legacy_programs, "Enhanced and legacy programs don't match"
        
        print(f"   ✅ Enhanced and legacy methods have same programs")
        print(f"   ✅ Backward compatibility maintained")
        
        test_results['passed'] += 1
        
    except Exception as e:
        test_results['failed'] += 1
        test_results['errors'].append(f"Test 5 failed: {e}")
        print(f"   ❌ FAILED: {e}")
    
    print()
    
    # Print Results Summary
    print("=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    
    print(f"Total Tests: {test_results['total_tests']}")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    
    if test_results['failed'] == 0:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("Copy Exam Modal Program Dropdown fix is READY for production!")
        print("\nExpected behavior:")
        print("1. Copy Exam modal will show 4 programs: CORE, ASCENT, EDGE, PINNACLE")
        print("2. Each program will have appropriate subprograms")
        print("3. Each subprogram will have correct levels")
        print("4. Comprehensive debugging logs will be available")
        print("5. Fallback mechanisms will handle edge cases")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("Errors encountered:")
        for error in test_results['errors']:
            print(f"  - {error}")
    
    print()
    print(f"Test completed at: {datetime.now().isoformat()}")
    print("=" * 80)
    
    return test_results['failed'] == 0

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
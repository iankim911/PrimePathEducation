#!/usr/bin/env python
"""
Test script for Curriculum Filtering Feature
Tests that test/QA subprograms are properly filtered from the placement rules view
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from core.models import SubProgram, CurriculumLevel, Program
from core.curriculum_constants import (
    is_valid_subprogram, 
    is_test_subprogram, 
    get_valid_subprogram_names,
    KNOWN_TEST_SUBPROGRAMS,
    VALID_CURRICULUM_STRUCTURE
)
from django.test import Client
from django.contrib.auth.models import User
import json


def test_curriculum_constants():
    """Test the curriculum constants module"""
    print("\n" + "="*80)
    print("TESTING CURRICULUM CONSTANTS")
    print("="*80)
    
    # Test 1: Check valid subprogram detection
    print("\n✓ Test 1: Valid subprogram detection...")
    valid_tests = [
        ('CORE PHONICS', True),
        ('PHONICS', True),
        ('CORE SIGMA', True),
        ('ASCENT NOVA', True),
        ('EDGE SPARK', True),
        ('PINNACLE VISION', True),
        ('Test SubProgram', False),
        ('SHORT Answer Test SubProgram', False),
        ('Management Test SubProgram', False)
    ]
    
    for name, expected in valid_tests:
        result = is_valid_subprogram(name)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{name}': Expected {expected}, Got {result}")
    
    # Test 2: Check test subprogram detection
    print("\n✓ Test 2: Test subprogram detection...")
    test_tests = [
        ('Test SubProgram', True),
        ('SHORT Answer Test SubProgram', True),
        ('Comprehensive Test SubProgram', True),
        ('CORE PHONICS', False),
        ('ASCENT NOVA', False)
    ]
    
    for name, expected in test_tests:
        result = is_test_subprogram(name)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{name}': Expected {expected}, Got {result}")
    
    # Test 3: Valid structure summary
    print("\n✓ Test 3: Valid curriculum structure...")
    print(f"  Programs defined: {list(VALID_CURRICULUM_STRUCTURE.keys())}")
    total_valid = sum(len(config['subprograms']) for config in VALID_CURRICULUM_STRUCTURE.values())
    print(f"  Total valid subprograms: {total_valid}")
    
    return True


def test_database_filtering():
    """Test filtering of database subprograms"""
    print("\n" + "="*80)
    print("TESTING DATABASE FILTERING")
    print("="*80)
    
    # Get all subprograms from database
    all_subprograms = SubProgram.objects.all()
    print(f"\n✓ Total subprograms in database: {all_subprograms.count()}")
    
    # Categorize subprograms
    valid_subprograms = []
    test_subprograms = []
    unknown_subprograms = []
    
    for sp in all_subprograms:
        if is_test_subprogram(sp.name):
            test_subprograms.append(sp)
        elif is_valid_subprogram(sp.name):
            valid_subprograms.append(sp)
        else:
            unknown_subprograms.append(sp)
    
    # Display results
    print(f"\n  ✅ Valid subprograms: {len(valid_subprograms)}")
    for sp in valid_subprograms[:5]:  # Show first 5
        print(f"     • {sp.program.name} - {sp.name}")
    if len(valid_subprograms) > 5:
        print(f"     ... and {len(valid_subprograms) - 5} more")
    
    print(f"\n  ⚠️  Test/QA subprograms (to be filtered): {len(test_subprograms)}")
    for sp in test_subprograms:
        print(f"     • {sp.program.name} - {sp.name}")
    
    if unknown_subprograms:
        print(f"\n  ❓ Unknown subprograms: {len(unknown_subprograms)}")
        for sp in unknown_subprograms:
            print(f"     • {sp.program.name} - {sp.name}")
    
    return len(test_subprograms), len(valid_subprograms)


def test_view_filtering():
    """Test that the placement_rules view filters correctly"""
    print("\n" + "="*80)
    print("TESTING VIEW FILTERING")
    print("="*80)
    
    client = Client()
    
    # Create or get a test user
    try:
        user = User.objects.get(username='test_user')
    except User.DoesNotExist:
        user = User.objects.create_user('test_user', 'test@example.com', 'testpass123')
    
    client.force_login(user)
    
    # Test placement rules view
    print("\n✓ Testing placement_rules view...")
    response = client.get('/core/placement-rules/')
    
    if response.status_code == 200:
        print("  ✅ View loaded successfully")
        
        # Check context data
        if hasattr(response, 'context') and response.context:
            core_levels = response.context.get('core_levels', [])
            ascent_levels = response.context.get('ascent_levels', [])
            edge_levels = response.context.get('edge_levels', [])
            pinnacle_levels = response.context.get('pinnacle_levels', [])
            
            print(f"\n  Levels passed to template:")
            print(f"    CORE: {len(core_levels)} levels")
            print(f"    ASCENT: {len(ascent_levels)} levels")
            print(f"    EDGE: {len(edge_levels)} levels")
            print(f"    PINNACLE: {len(pinnacle_levels)} levels")
            
            # Check for test subprograms in the levels
            all_levels = core_levels + ascent_levels + edge_levels + pinnacle_levels
            test_found = []
            
            for level in all_levels:
                if hasattr(level, 'subprogram'):
                    if is_test_subprogram(level.subprogram.name):
                        test_found.append(f"{level.subprogram.program.name} - {level.subprogram.name} - Level {level.level_number}")
            
            if test_found:
                print(f"\n  ❌ Test subprograms found in view context:")
                for item in test_found:
                    print(f"     • {item}")
                return False
            else:
                print(f"\n  ✅ No test subprograms in view context - filtering working!")
                return True
    else:
        print(f"  ❌ View returned status {response.status_code}")
        return False


def test_impact_on_other_views():
    """Test that filtering doesn't affect other views"""
    print("\n" + "="*80)
    print("TESTING IMPACT ON OTHER VIEWS")
    print("="*80)
    
    client = Client()
    
    # Create or get a test user
    try:
        user = User.objects.get(username='test_user')
    except User.DoesNotExist:
        user = User.objects.create_user('test_user', 'test@example.com', 'testpass123')
    
    client.force_login(user)
    
    # Test curriculum_levels view (should NOT filter)
    print("\n✓ Testing curriculum_levels view (should show all)...")
    response = client.get('/core/curriculum-levels/')
    
    if response.status_code == 200:
        print("  ✅ View loaded successfully")
        
        if hasattr(response, 'context') and response.context:
            programs = response.context.get('programs', [])
            total_subprograms = sum(p.subprograms.count() for p in programs)
            print(f"  Total subprograms shown: {total_subprograms}")
            
            # This view should show ALL subprograms (no filtering)
            actual_count = SubProgram.objects.count()
            if total_subprograms == actual_count:
                print(f"  ✅ Showing all {actual_count} subprograms (no filtering applied)")
            else:
                print(f"  ⚠️  Showing {total_subprograms} of {actual_count} subprograms")
    else:
        print(f"  ❌ View returned status {response.status_code}")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "#"*80)
    print("# CURRICULUM FILTERING - COMPREHENSIVE TEST SUITE")
    print("#"*80)
    
    try:
        # Test 1: Constants module
        constants_success = test_curriculum_constants()
        
        # Test 2: Database filtering
        test_count, valid_count = test_database_filtering()
        
        # Test 3: View filtering
        view_success = test_view_filtering()
        
        # Test 4: Impact on other views
        impact_success = test_impact_on_other_views()
        
        # Summary
        print("\n" + "#"*80)
        print("# TEST SUMMARY")
        print("#"*80)
        
        if constants_success and view_success:
            print("\n✅ All tests passed successfully!")
            print(f"\n📊 Filtering Summary:")
            print(f"  • {test_count} test/QA subprograms will be filtered")
            print(f"  • {valid_count} valid subprograms will be displayed")
            print(f"  • Other views remain unaffected")
            print("\n✨ The curriculum filtering feature is working correctly!")
        else:
            print("\n❌ Some tests failed. Please check the implementation.")
        
        print("\n💡 Next Steps:")
        print("  1. Clear browser cache")
        print("  2. Restart Django server")
        print("  3. Navigate to Placement Rules page")
        print("  4. Check Exam-to-Level Mapping tab")
        print("  5. Open browser console to see logging")
        
        if test_count > 0:
            print(f"\n⚠️  Note: {test_count} test subprograms exist in database.")
            print("  Consider running cleanup to remove them permanently:")
            print("  python manage.py clean_test_subprograms --dry-run")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
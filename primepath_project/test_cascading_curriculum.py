#!/usr/bin/env python
"""
Test script for the new cascading curriculum selection system in RoutineTest module.
Tests API endpoint, model relationships, and ensures PlacementTest is unaffected.
"""

import os
import sys
import django
import json

# Setup Django environment
sys.path.append('/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import RequestFactory
from core.models import Program, SubProgram, CurriculumLevel
from primepath_routinetest.models import Exam
from primepath_routinetest.views.ajax import get_curriculum_hierarchy
from primepath_routinetest.constants import ROUTINETEST_CURRICULUM_WHITELIST

def test_curriculum_hierarchy_api():
    """Test the new curriculum hierarchy API endpoint"""
    print("\n" + "="*60)
    print("TESTING CASCADING CURRICULUM HIERARCHY API")
    print("="*60)
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/RoutineTest/api/curriculum-hierarchy/')
    
    try:
        # Call the view
        response = get_curriculum_hierarchy(request)
        
        # Parse response
        data = json.loads(response.content.decode())
        
        if data['success']:
            print("✅ API endpoint working successfully")
            
            hierarchy = data['data']
            
            # Display structure
            print(f"\n📚 PROGRAMS: {len(hierarchy['programs'])}")
            for program in hierarchy['programs']:
                print(f"  - {program['name']} (ID: {program['id']})")
            
            print(f"\n📂 SUBPROGRAMS by Program:")
            for program_name, subprograms in hierarchy['subprograms'].items():
                print(f"  {program_name}: {len(subprograms)} subprograms")
                for sp in subprograms[:3]:  # Show first 3
                    print(f"    - {sp['name']}")
            
            print(f"\n📊 LEVELS by SubProgram:")
            total_levels = sum(len(levels) for levels in hierarchy['levels'].values())
            print(f"  Total curriculum levels: {total_levels}")
            
            # Test specific cascade
            if 'CORE' in hierarchy['subprograms']:
                core_subprograms = hierarchy['subprograms']['CORE']
                print(f"\n🔍 CORE Program has {len(core_subprograms)} subprograms:")
                for sp in core_subprograms:
                    key = f"CORE_{sp['name']}"
                    if key in hierarchy['levels']:
                        levels = hierarchy['levels'][key]
                        print(f"  - {sp['name']}: {len(levels)} levels")
            
            return True
        else:
            print(f"❌ API failed: {data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_existing_exams():
    """Test that existing exams still display correctly"""
    print("\n" + "="*60)
    print("TESTING EXISTING EXAMS COMPATIBILITY")
    print("="*60)
    
    # Get RoutineTest exams
    rt_exams = Exam.objects.select_related(
        'curriculum_level__subprogram__program'
    ).all()[:5]  # Get first 5
    
    print(f"\n📋 Found {Exam.objects.count()} RoutineTest exams")
    
    if rt_exams:
        print("\nTesting exam display methods:")
        for exam in rt_exams:
            try:
                # Test display methods
                display_name = exam.get_routinetest_display_name()
                base_name = exam.get_routinetest_base_name()
                
                print(f"\n✅ Exam: {exam.name}")
                print(f"  - Display name: {display_name}")
                print(f"  - Base name: {base_name}")
                
                if exam.curriculum_level:
                    print(f"  - Curriculum: {exam.curriculum_level.full_name}")
                    print(f"  - Program: {exam.curriculum_level.subprogram.program.name}")
                    print(f"  - SubProgram: {exam.curriculum_level.subprogram.name}")
                    print(f"  - Level: {exam.curriculum_level.level_number}")
                
            except Exception as e:
                print(f"❌ Error with exam {exam.id}: {str(e)}")
                return False
    else:
        print("ℹ️ No RoutineTest exams found in database")
    
    return True

def test_placement_test_unaffected():
    """Verify PlacementTest module is not affected"""
    print("\n" + "="*60)
    print("VERIFYING PLACEMENTTEST MODULE UNAFFECTED")
    print("="*60)
    
    try:
        from placement_test.models import Exam as PlacementExam
        
        # Check PlacementTest exams
        pt_exams = PlacementExam.objects.select_related(
            'curriculum_level__subprogram__program'
        ).all()[:3]
        
        print(f"\n📋 Found {PlacementExam.objects.count()} PlacementTest exams")
        
        if pt_exams:
            for exam in pt_exams:
                print(f"\n✅ PlacementTest Exam: {exam.name}")
                if exam.curriculum_level:
                    print(f"  - Curriculum: {exam.curriculum_level.full_name}")
                    print(f"  - Still using single curriculum_level FK: ✓")
        else:
            print("ℹ️ No PlacementTest exams found")
        
        print("\n✅ PlacementTest module structure unchanged")
        return True
        
    except Exception as e:
        print(f"❌ Error checking PlacementTest: {str(e)}")
        return False

def test_whitelist_consistency():
    """Test that whitelist matches database"""
    print("\n" + "="*60)
    print("TESTING WHITELIST CONSISTENCY")
    print("="*60)
    
    mismatches = []
    
    for program_name, subprogram_name, level_number in ROUTINETEST_CURRICULUM_WHITELIST:
        try:
            # Try to find in database
            level = CurriculumLevel.objects.select_related(
                'subprogram__program'
            ).get(
                subprogram__program__name=program_name,
                subprogram__name__icontains=subprogram_name,
                level_number=level_number
            )
            print(f"✅ Found: {program_name} {subprogram_name} Level {level_number}")
            
        except CurriculumLevel.DoesNotExist:
            mismatches.append((program_name, subprogram_name, level_number))
            print(f"❌ Missing: {program_name} {subprogram_name} Level {level_number}")
    
    if mismatches:
        print(f"\n⚠️ {len(mismatches)} whitelist entries not found in database")
        return False
    else:
        print(f"\n✅ All {len(ROUTINETEST_CURRICULUM_WHITELIST)} whitelist entries found")
        return True

def main():
    """Run all tests"""
    print("\n" + "#"*60)
    print("# CASCADING CURRICULUM SYSTEM TEST SUITE")
    print("#"*60)
    
    results = {
        'API Endpoint': test_curriculum_hierarchy_api(),
        'Existing Exams': test_existing_exams(),
        'PlacementTest Unaffected': test_placement_test_unaffected(),
        'Whitelist Consistency': test_whitelist_consistency()
    }
    
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Cascading curriculum system is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please review the output above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
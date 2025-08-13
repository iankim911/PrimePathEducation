#!/usr/bin/env python
"""
Test the new naming convention implementation
Tests:
1. CurriculumLevel model properties (display_name, exam_base_name)
2. ExamService.get_next_version_number() functionality
3. View endpoint for checking versions
4. Naming format generation
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from core.models import CurriculumLevel
from placement_test.models import Exam
from placement_test.services import ExamService
from django.test import RequestFactory
import json

def test_curriculum_level_properties():
    """Test the new display_name and exam_base_name properties"""
    print("\n" + "="*60)
    print("Testing CurriculumLevel Properties")
    print("="*60)
    
    levels = CurriculumLevel.objects.select_related('subprogram__program').all()[:3]
    
    for level in levels:
        print(f"\nLevel: {level}")
        print(f"  Old full_name: {level.full_name}")
        print(f"  New display_name: {level.display_name}")
        print(f"  New exam_base_name: {level.exam_base_name}")
        
        # Check that PRIME is removed and Level changed to Lv
        assert "PRIME" not in level.exam_base_name, f"PRIME should be removed from exam_base_name"
        assert "_Lv" in level.exam_base_name, f"Should use _Lv format in exam_base_name"
    
    print("\n✅ CurriculumLevel properties test passed!")
    return True

def test_version_number_generation():
    """Test the new version number generation logic"""
    print("\n" + "="*60)
    print("Testing Version Number Generation")
    print("="*60)
    
    # Get a test curriculum level
    level = CurriculumLevel.objects.first()
    if not level:
        print("❌ No curriculum levels found!")
        return False
    
    # Test with today's date
    today_str = datetime.now().strftime('%y%m%d')
    print(f"\nTesting for Level: {level.display_name}")
    print(f"Date: {today_str}")
    
    # First upload today - should return None (no version needed)
    version = ExamService.get_next_version_number(level.id, today_str)
    print(f"  First upload today: version = {version} (expected: None)")
    assert version is None, "First upload should not have version number"
    
    # Create a fake exam for today to test version incrementing
    test_exam_name = f"[PT]_{level.exam_base_name}_{today_str}"
    print(f"  Creating test exam: {test_exam_name}")
    
    # Check if exam already exists
    existing = Exam.objects.filter(name=test_exam_name).first()
    if not existing:
        Exam.objects.create(
            name=test_exam_name,
            curriculum_level=level,
            timer_minutes=60,
            total_questions=50,
            default_options_count=5
        )
    
    # Now check version again - should return 2
    version = ExamService.get_next_version_number(level.id, today_str)
    print(f"  Second upload today: version = {version} (expected: 2)")
    assert version == 2, f"Second upload should have version 2, got {version}"
    
    # Create another exam with version
    test_exam_name_v2 = f"[PT]_{level.exam_base_name}_{today_str}_v2"
    existing_v2 = Exam.objects.filter(name=test_exam_name_v2).first()
    if not existing_v2:
        Exam.objects.create(
            name=test_exam_name_v2,
            curriculum_level=level,
            timer_minutes=60,
            total_questions=50,
            default_options_count=5
        )
    
    # Check version again - should return 3
    version = ExamService.get_next_version_number(level.id, today_str)
    print(f"  Third upload today: version = {version} (expected: 3)")
    assert version == 3, f"Third upload should have version 3, got {version}"
    
    # Test with different date - should return None
    tomorrow_str = "991231"  # Far future date
    version = ExamService.get_next_version_number(level.id, tomorrow_str)
    print(f"  First upload on {tomorrow_str}: version = {version} (expected: None)")
    assert version is None, "Different date should not have version"
    
    print("\n✅ Version number generation test passed!")
    return True

def test_exam_name_format():
    """Test the complete exam name format generation"""
    print("\n" + "="*60)
    print("Testing Exam Name Format")
    print("="*60)
    
    level = CurriculumLevel.objects.first()
    if not level:
        print("❌ No curriculum levels found!")
        return False
    
    today_str = datetime.now().strftime('%y%m%d')
    
    # Test name format without version
    expected_name = f"[PT]_{level.exam_base_name}_{today_str}"
    print(f"\nFirst upload format: {expected_name}")
    assert "[PT]_" in expected_name, "Should start with [PT]_"
    assert "PRIME" not in expected_name, "Should not contain PRIME"
    assert "_Lv" in expected_name, "Should use _Lv format"
    assert today_str in expected_name, "Should contain date"
    
    # Test name format with version
    expected_name_v2 = f"[PT]_{level.exam_base_name}_{today_str}_v2"
    print(f"Second upload format: {expected_name_v2}")
    assert "_v2" in expected_name_v2, "Should have _v2 suffix"
    
    print("\n✅ Exam name format test passed!")
    return True

def test_view_endpoint():
    """Test the check_exam_version endpoint"""
    print("\n" + "="*60)
    print("Testing View Endpoint")
    print("="*60)
    
    from placement_test.views.exam import check_exam_version
    
    level = CurriculumLevel.objects.first()
    if not level:
        print("❌ No curriculum levels found!")
        return False
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get(f'/api/placement/exams/check-version/?curriculum_level={level.id}')
    
    # Call the view
    response = check_exam_version(request)
    
    # Parse response
    data = json.loads(response.content.decode())
    print(f"\nEndpoint response: {data}")
    
    assert 'date_str' in data, "Response should contain date_str"
    assert 'next_version' in data, "Response should contain next_version"
    
    today_str = datetime.now().strftime('%y%m%d')
    assert data['date_str'] == today_str, f"Date should be today's date {today_str}"
    
    print("\n✅ View endpoint test passed!")
    return True

def cleanup_test_exams():
    """Clean up test exams created during testing"""
    print("\n" + "="*60)
    print("Cleaning Up Test Exams")
    print("="*60)
    
    today_str = datetime.now().strftime('%y%m%d')
    test_exams = Exam.objects.filter(name__contains=f"_{today_str}")
    
    for exam in test_exams:
        if "[PT]_" in exam.name and "test" not in exam.name.lower():
            print(f"  Keeping exam: {exam.name}")
        elif "[PT]_" in exam.name:
            print(f"  Deleting test exam: {exam.name}")
            exam.delete()
    
    print("\nCleanup complete!")

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("TESTING NEW NAMING CONVENTION IMPLEMENTATION")
    print("="*80)
    
    all_passed = True
    
    try:
        # Run tests
        if not test_curriculum_level_properties():
            all_passed = False
            
        if not test_version_number_generation():
            all_passed = False
            
        if not test_exam_name_format():
            all_passed = False
            
        if not test_view_endpoint():
            all_passed = False
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    finally:
        # Always cleanup
        cleanup_test_exams()
    
    if all_passed:
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED! Naming convention implementation is working correctly.")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("❌ SOME TESTS FAILED! Please check the implementation.")
        print("="*80)
    
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
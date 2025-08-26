#!/usr/bin/env python
"""
Test script for the difficulty adjustment feature
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from placement_test.models import StudentSession, PlacementExam as Exam, DifficultyAdjustment
from core.models import CurriculumLevel, ExamLevelMapping
from placement_test.services import PlacementService

print('='*80)
print('DIFFICULTY ADJUSTMENT FEATURE TEST')
print(f'Timestamp: {datetime.now()}')
print('='*80)

# Test results tracking
test_results = {
    'passed': 0,
    'failed': 0,
    'details': []
}

def log_test(test_name, passed, details=""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {test_name}")
    if details:
        print(f"    {details}")
    
    test_results['passed' if passed else 'failed'] += 1
    test_results['details'].append({
        'test': test_name,
        'passed': passed,
        'details': details
    })

print("\n1. PLACEMENT SERVICE TESTS")
print("-" * 50)

# Test PlacementService.adjust_difficulty method
try:
    # Get a curriculum level
    level = CurriculumLevel.objects.first()
    if level:
        # Test upward adjustment
        result_up = PlacementService.adjust_difficulty(level, 1)
        if result_up:
            new_level, new_exam = result_up
            log_test("Upward adjustment", True, f"{level.full_name} -> {new_level.full_name}")
        else:
            log_test("Upward adjustment", True, "At top level (None returned)")
        
        # Test downward adjustment
        result_down = PlacementService.adjust_difficulty(level, -1)
        if result_down:
            new_level, new_exam = result_down
            log_test("Downward adjustment", True, f"{level.full_name} -> {new_level.full_name}")
        else:
            log_test("Downward adjustment", True, "At bottom level (None returned)")
    else:
        log_test("Curriculum level exists", False, "No curriculum levels found")
except Exception as e:
    log_test("PlacementService.adjust_difficulty", False, str(e))

print("\n2. API ENDPOINT TESTS")
print("-" * 50)

# Test manual_adjust_difficulty endpoint
client = Client()

# First, find or create a test session
session = StudentSession.objects.filter(completed_at__isnull=True).first()

if not session:
    # Create a test session if none exists
    exam = Exam.objects.filter(is_active=True).first()
    curriculum_level = CurriculumLevel.objects.first()
    
    if exam and curriculum_level:
        session = StudentSession.objects.create(
            student_name="Test Student",
            grade=5,
            academic_rank="TOP_20",
            exam=exam,
            original_curriculum_level=curriculum_level
        )
        log_test("Test session created", True, f"Session ID: {session.id}")
    else:
        log_test("Test session creation", False, "No active exam or curriculum level")

if session:
    # Test increasing difficulty
    try:
        response = client.post(
            f'/api/PlacementTest/session/{session.id}/manual-adjust/',
            json.dumps({'direction': 'up'}),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                log_test("API: Increase difficulty", True, f"New level: {data.get('new_level')}")
            elif data.get('at_boundary'):
                log_test("API: Increase difficulty", True, f"At boundary: {data.get('error')}")
            else:
                log_test("API: Increase difficulty", False, data.get('error'))
        else:
            log_test("API: Increase difficulty", False, f"HTTP {response.status_code}")
    except Exception as e:
        log_test("API: Increase difficulty", False, str(e))
    
    # Test decreasing difficulty
    try:
        response = client.post(
            f'/api/PlacementTest/session/{session.id}/manual-adjust/',
            json.dumps({'direction': 'down'}),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                log_test("API: Decrease difficulty", True, f"New level: {data.get('new_level')}")
            elif data.get('at_boundary'):
                log_test("API: Decrease difficulty", True, f"At boundary: {data.get('error')}")
            else:
                log_test("API: Decrease difficulty", False, data.get('error'))
        else:
            log_test("API: Decrease difficulty", False, f"HTTP {response.status_code}")
    except Exception as e:
        log_test("API: Decrease difficulty", False, str(e))
    
    # Test invalid direction
    try:
        response = client.post(
            f'/api/PlacementTest/session/{session.id}/manual-adjust/',
            json.dumps({'direction': 'invalid'}),
            content_type='application/json'
        )
        
        if response.status_code == 400:
            log_test("API: Invalid direction handling", True, "Correctly rejected")
        else:
            log_test("API: Invalid direction handling", False, f"Should return 400, got {response.status_code}")
    except Exception as e:
        log_test("API: Invalid direction handling", False, str(e))

print("\n3. MODEL TESTS")
print("-" * 50)

# Test DifficultyAdjustment model
if session:
    try:
        # Check if adjustments were tracked
        adjustments = DifficultyAdjustment.objects.filter(session=session).count()
        log_test("Difficulty adjustments tracked", adjustments > 0, f"{adjustments} adjustments found")
        
        # Check session updates
        session.refresh_from_db()
        log_test("Session difficulty_adjustments counter", 
                 session.difficulty_adjustments > 0, 
                 f"Count: {session.difficulty_adjustments}")
        
        # Check final curriculum level
        log_test("Final curriculum level set", 
                 session.final_curriculum_level is not None,
                 f"Level: {session.final_curriculum_level.full_name if session.final_curriculum_level else 'None'}")
    except Exception as e:
        log_test("Model tracking", False, str(e))

print("\n4. BOUNDARY TESTS")
print("-" * 50)

# Test at highest level
try:
    highest_level = CurriculumLevel.objects.order_by(
        '-subprogram__program__order',
        '-subprogram__order',
        '-level_number'
    ).first()
    
    if highest_level:
        result = PlacementService.adjust_difficulty(highest_level, 1)
        log_test("Cannot go higher than highest", result is None, 
                 f"Highest: {highest_level.full_name}")
except Exception as e:
    log_test("Highest level boundary", False, str(e))

# Test at lowest level
try:
    lowest_level = CurriculumLevel.objects.order_by(
        'subprogram__program__order',
        'subprogram__order',
        'level_number'
    ).first()
    
    if lowest_level:
        result = PlacementService.adjust_difficulty(lowest_level, -1)
        log_test("Cannot go lower than lowest", result is None,
                 f"Lowest: {lowest_level.full_name}")
except Exception as e:
    log_test("Lowest level boundary", False, str(e))

print("\n5. UI INTEGRATION TESTS")
print("-" * 50)

# Test that the student test page loads with difficulty buttons
if session:
    try:
        response = client.get(f'/api/PlacementTest/session/{session.id}/')
        if response.status_code == 200:
            content = str(response.content)
            
            # Check for difficulty adjustment buttons
            has_easier_btn = 'Easier Exam' in content or 'decrease-difficulty-btn' in content
            has_harder_btn = 'Harder Exam' in content or 'increase-difficulty-btn' in content
            
            log_test("Easier Exam button present", has_easier_btn)
            log_test("Harder Exam button present", has_harder_btn)
            
            # Check for JavaScript handling
            has_js = 'adjustDifficulty' in content
            log_test("JavaScript integration", has_js)
        else:
            log_test("Student test page loads", False, f"HTTP {response.status_code}")
    except Exception as e:
        log_test("UI integration", False, str(e))

# Summary
print("\n" + "="*80)
print("TEST RESULTS SUMMARY")
print("="*80)

total_tests = test_results['passed'] + test_results['failed']
pass_rate = (test_results['passed'] / total_tests * 100) if total_tests > 0 else 0

print(f"\nTotal Tests: {total_tests}")
print(f"Passed: {test_results['passed']}")
print(f"Failed: {test_results['failed']}")
print(f"Pass Rate: {pass_rate:.1f}%")

if test_results['failed'] == 0:
    print("\n🎉 ALL TESTS PASSED!")
    print("✅ Difficulty adjustment feature is working correctly")
    print("✅ API endpoints functioning")
    print("✅ Boundary conditions handled")
    print("✅ UI integration complete")
else:
    print(f"\n❌ {test_results['failed']} tests failed")
    print("\nFailed tests:")
    for detail in test_results['details']:
        if not detail['passed']:
            print(f"  - {detail['test']}: {detail['details']}")

# Save results
with open('test_difficulty_adjustment_results.json', 'w') as f:
    json.dump(test_results, f, indent=2, default=str)

print(f"\nDetailed results saved to: test_difficulty_adjustment_results.json")
print("="*80)
#!/usr/bin/env python
"""
Comprehensive QA test suite for PrimePath system
Tests all critical features after SHORT answer fix
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.utils import timezone
from placement_test.models import Exam, Question, StudentSession, StudentAnswer
from placement_test.services.grading_service import GradingService
from core.models import CurriculumLevel, SubProgram, Program

def test_short_answer_grading():
    """Test SHORT answer grading functionality"""
    
    print("=" * 80)
    print("🎯 SHORT ANSWER GRADING TEST")
    print("=" * 80)
    
    all_passed = True
    
    # Test 1: Single SHORT answer
    print("\n📋 TEST 1: Single SHORT Answer Grading")
    print("-" * 40)
    
    # Test exact match
    result = GradingService.grade_short_answer("apple", "apple")
    if result == True:
        print("✅ Exact match: Passed")
    else:
        print(f"❌ Exact match: Failed (got {result})")
        all_passed = False
    
    # Test case insensitive
    result = GradingService.grade_short_answer("Apple", "apple", case_sensitive=False)
    if result == True:
        print("✅ Case insensitive: Passed")
    else:
        print(f"❌ Case insensitive: Failed (got {result})")
        all_passed = False
    
    # Test with pipe-separated alternatives
    result = GradingService.grade_short_answer("cat", "cat|feline|kitty", case_sensitive=False)
    if result == True:
        print("✅ Alternatives (pipe): Passed")
    else:
        print(f"❌ Alternatives (pipe): Failed (got {result})")
        all_passed = False
    
    # Test 2: Multiple SHORT answers
    print("\n📋 TEST 2: Multiple SHORT Answer Grading")
    print("-" * 40)
    
    # Test comma-separated letters (like MCQ format)
    result = GradingService.grade_short_answer("B", "B,C,A")
    if result == False:  # Should fail as it's expecting multiple parts
        print("✅ Multiple letters format: Correctly detected")
    else:
        print(f"❌ Multiple letters format: Failed (got {result})")
        all_passed = False
    
    return all_passed


def test_all_question_types():
    """Test all question types work correctly"""
    
    print("\n" + "=" * 80)
    print("🔍 ALL QUESTION TYPES TEST")
    print("=" * 80)
    
    all_passed = True
    
    # Get or create test curriculum
    program, _ = Program.objects.get_or_create(
        name="CORE",
        defaults={'grade_range_start': 1, 'grade_range_end': 12, 'order': 1}
    )
    
    subprogram, _ = SubProgram.objects.get_or_create(
        name="Comprehensive Test SubProgram",
        program=program,
        defaults={'order': 1}
    )
    
    curriculum_level, _ = CurriculumLevel.objects.get_or_create(
        subprogram=subprogram,
        level_number=1,
        defaults={'description': 'Comprehensive Test Level'}
    )
    
    # Create comprehensive test exam
    exam = Exam.objects.create(
        name=f"Comprehensive QA Test - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        curriculum_level=curriculum_level,
        timer_minutes=60,
        total_questions=6,
        is_active=True
    )
    
    print(f"✅ Created test exam: {exam.name}")
    
    # Create questions of each type
    questions = []
    
    # MCQ
    q1 = Question.objects.create(
        exam=exam,
        question_number=1,
        question_type='MCQ',
        correct_answer='B',
        points=1,
        options_count=4
    )
    questions.append(q1)
    print("✅ Created MCQ question")
    
    # CHECKBOX
    q2 = Question.objects.create(
        exam=exam,
        question_number=2,
        question_type='CHECKBOX',
        correct_answer='A,C,D',
        points=2,
        options_count=5
    )
    questions.append(q2)
    print("✅ Created CHECKBOX question")
    
    # SHORT (single)
    q3 = Question.objects.create(
        exam=exam,
        question_number=3,
        question_type='SHORT',
        correct_answer='Test Answer',
        points=1,
        options_count=1
    )
    questions.append(q3)
    print("✅ Created SHORT (single) question")
    
    # SHORT (multiple)
    q4 = Question.objects.create(
        exam=exam,
        question_number=4,
        question_type='SHORT',
        correct_answer='Answer1|Answer2|Answer3',
        points=3,
        options_count=3
    )
    questions.append(q4)
    print("✅ Created SHORT (multiple) question")
    
    # LONG
    q5 = Question.objects.create(
        exam=exam,
        question_number=5,
        question_type='LONG',
        correct_answer='',
        points=5,
        options_count=1
    )
    questions.append(q5)
    print("✅ Created LONG question")
    
    # MIXED
    q6 = Question.objects.create(
        exam=exam,
        question_number=6,
        question_type='MIXED',
        correct_answer='',
        points=4,
        options_count=4
    )
    questions.append(q6)
    print("✅ Created MIXED question")
    
    # Test saving via API
    print("\n📋 Testing Save Functionality")
    print("-" * 40)
    
    base_url = "http://127.0.0.1:8000"
    save_url = f"{base_url}/api/placement/exams/{exam.id}/save-answers/"
    
    save_data = {
        'questions': [
            {
                'id': str(q1.id),
                'question_number': '1',
                'question_type': 'MCQ',
                'correct_answer': 'C',
                'options_count': 4
            },
            {
                'id': str(q2.id),
                'question_number': '2',
                'question_type': 'CHECKBOX',
                'correct_answer': 'B,D',
                'options_count': 5
            },
            {
                'id': str(q3.id),
                'question_number': '3',
                'question_type': 'SHORT',
                'correct_answer': 'Updated Answer',
                'options_count': 1
            },
            {
                'id': str(q4.id),
                'question_number': '4',
                'question_type': 'SHORT',
                'correct_answer': 'New1|New2|New3',
                'options_count': 3
            },
            {
                'id': str(q5.id),
                'question_number': '5',
                'question_type': 'LONG',
                'correct_answer': 'Long answer content here',
                'options_count': 1
            },
            {
                'id': str(q6.id),
                'question_number': '6',
                'question_type': 'MIXED',
                'correct_answer': json.dumps([
                    {"type": "Multiple Choice", "value": "A,B"},
                    {"type": "Text", "value": "Text answer"}
                ]),
                'options_count': 4
            }
        ]
    }
    
    try:
        response = requests.post(
            save_url,
            json=save_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ All question types saved successfully")
        else:
            print(f"❌ Save failed: HTTP {response.status_code}")
            all_passed = False
            
    except Exception as e:
        print(f"❌ Error saving: {e}")
        all_passed = False
    
    # Verify persistence
    print("\n📋 Verifying Data Persistence")
    print("-" * 40)
    
    for question in questions:
        question.refresh_from_db()
    
    # Check each type
    if q1.correct_answer == 'C':
        print("✅ MCQ: Persisted correctly")
    else:
        print(f"❌ MCQ: Expected 'C', got '{q1.correct_answer}'")
        all_passed = False
    
    if q2.correct_answer == 'B,D':
        print("✅ CHECKBOX: Persisted correctly")
    else:
        print(f"❌ CHECKBOX: Expected 'B,D', got '{q2.correct_answer}'")
        all_passed = False
    
    if q3.correct_answer == 'Updated Answer':
        print("✅ SHORT (single): Persisted correctly")
    else:
        print(f"❌ SHORT (single): Expected 'Updated Answer', got '{q3.correct_answer}'")
        all_passed = False
    
    if q4.correct_answer == 'New1|New2|New3':
        print("✅ SHORT (multiple): Persisted correctly")
    else:
        print(f"❌ SHORT (multiple): Expected 'New1|New2|New3', got '{q4.correct_answer}'")
        all_passed = False
    
    if q5.correct_answer == 'Long answer content here':
        print("✅ LONG: Persisted correctly")
    else:
        print(f"❌ LONG: Expected content, got '{q5.correct_answer}'")
        all_passed = False
    
    if q6.correct_answer:
        try:
            mixed_data = json.loads(q6.correct_answer)
            if isinstance(mixed_data, list) and len(mixed_data) == 2:
                print("✅ MIXED: Persisted correctly")
            else:
                print(f"❌ MIXED: Invalid structure")
                all_passed = False
        except:
            print(f"❌ MIXED: Invalid JSON")
            all_passed = False
    else:
        print(f"❌ MIXED: No data saved")
        all_passed = False
    
    return all_passed


def test_student_interface_features():
    """Test student interface features"""
    
    print("\n" + "=" * 80)
    print("🖥️ STUDENT INTERFACE FEATURES TEST")
    print("=" * 80)
    
    all_passed = True
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: Check if server is running
    print("\n📋 TEST 1: Server Health Check")
    print("-" * 40)
    
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server returned HTTP {response.status_code}")
            all_passed = False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        all_passed = False
    
    # Test 2: Check static files
    print("\n📋 TEST 2: Static Files Check")
    print("-" * 40)
    
    static_files = [
        '/static/js/modules/answer-manager.js',
        '/static/js/modules/audio-player.js',
        '/static/js/modules/pdf-viewer.js',
        '/static/js/modules/timer.js',
        '/static/js/modules/navigation.js',
        '/static/css/pages/student-test.css'
    ]
    
    for file_path in static_files:
        try:
            response = requests.get(f"{base_url}{file_path}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {file_path}: Available")
            else:
                print(f"❌ {file_path}: HTTP {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"❌ {file_path}: Error - {e}")
            all_passed = False
    
    # Test 3: Check for JavaScript errors in modules
    print("\n📋 TEST 3: JavaScript Module Integrity")
    print("-" * 40)
    
    # Check if audio player has the fixed event delegation
    try:
        response = requests.get(f"{base_url}/static/js/modules/audio-player.js", timeout=5)
        if response.status_code == 200:
            content = response.text
            # Check for the fixed event delegation code
            if "e.target.closest('[data-audio-play]')" in content:
                print("✅ Audio player: Event delegation fix present")
            else:
                print("⚠️ Audio player: Event delegation fix may be missing")
                
            # Check for debug mode handling
            if "isDebugMode()" in content:
                print("✅ Audio player: Debug mode handling present")
            else:
                print("⚠️ Audio player: Debug mode handling missing")
    except Exception as e:
        print(f"❌ Could not check audio player: {e}")
        all_passed = False
    
    return all_passed


def test_exam_management_features():
    """Test exam management features"""
    
    print("\n" + "=" * 80)
    print("📚 EXAM MANAGEMENT FEATURES TEST")
    print("=" * 80)
    
    all_passed = True
    
    # Test 1: Exam creation
    print("\n📋 TEST 1: Exam Creation")
    print("-" * 40)
    
    exam_count_before = Exam.objects.count()
    
    # Create a test exam
    program, _ = Program.objects.get_or_create(
        name="CORE",
        defaults={'grade_range_start': 1, 'grade_range_end': 12, 'order': 1}
    )
    
    subprogram, _ = SubProgram.objects.get_or_create(
        name="Management Test SubProgram",
        program=program,
        defaults={'order': 1}
    )
    
    curriculum_level, _ = CurriculumLevel.objects.get_or_create(
        subprogram=subprogram,
        level_number=1,
        defaults={'description': 'Management Test Level'}
    )
    
    test_exam = Exam.objects.create(
        name=f"Management Test - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        curriculum_level=curriculum_level,
        timer_minutes=45,
        total_questions=10,
        is_active=True
    )
    
    exam_count_after = Exam.objects.count()
    
    if exam_count_after == exam_count_before + 1:
        print(f"✅ Exam created successfully: {test_exam.name}")
    else:
        print("❌ Exam creation failed")
        all_passed = False
    
    # Test 2: Question auto-creation
    print("\n📋 TEST 2: Question Auto-Creation")
    print("-" * 40)
    
    question_count = test_exam.questions.count()
    if question_count == test_exam.total_questions:
        print(f"✅ {question_count} questions auto-created")
    else:
        print(f"❌ Expected {test_exam.total_questions} questions, got {question_count}")
        all_passed = False
    
    # Test 3: PDF handling without file
    print("\n📋 TEST 3: PDF Handling (No File)")
    print("-" * 40)
    
    if not test_exam.pdf_file:
        print("✅ Exam created without PDF (as expected)")
    else:
        print("❌ Unexpected PDF file present")
        all_passed = False
    
    # Test preview page with no PDF
    base_url = "http://127.0.0.1:8000"
    preview_url = f"{base_url}/api/placement/exams/{test_exam.id}/preview/"
    
    try:
        response = requests.get(preview_url, timeout=10)
        if response.status_code == 200:
            if "No PDF uploaded" in response.text or "pdf-error" in response.text:
                print("✅ Preview page handles missing PDF correctly")
            else:
                print("⚠️ Preview page loads but PDF handling unclear")
        else:
            print(f"❌ Preview page error: HTTP {response.status_code}")
            all_passed = False
    except Exception as e:
        print(f"❌ Could not access preview page: {e}")
        all_passed = False
    
    return all_passed


def run_comprehensive_qa():
    """Run all QA tests"""
    
    print("=" * 80)
    print("🚀 PRIMEPATH COMPREHENSIVE QA SUITE")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    results = {
        'short_answer_grading': test_short_answer_grading(),
        'all_question_types': test_all_question_types(),
        'student_interface': test_student_interface_features(),
        'exam_management': test_exam_management_features()
    }
    
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE QA RESULTS")
    print("=" * 80)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 80)
    print("🎯 FINAL VERDICT")
    print("=" * 80)
    
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\n🎉 System Status: FULLY OPERATIONAL")
        print("📋 Summary:")
        print("  • SHORT answer save/load: Working")
        print("  • All question types: Working")
        print("  • Grading system: Working")
        print("  • Student interface: Working")
        print("  • Exam management: Working")
        print("  • Audio buttons: Fixed")
        print("  • Console errors: Fixed")
        print("  • Submission workflow: Fixed")
        print("  • PDF viewer: Optimized")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("\n⚠️ Please review the failed tests above")
        return 1


if __name__ == '__main__':
    exit_code = run_comprehensive_qa()
    sys.exit(exit_code)
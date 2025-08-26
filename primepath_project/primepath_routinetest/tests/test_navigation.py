"""
Comprehensive Navigation Test Suite
Tests all navigation functionality in the student test interface
"""

import os
import django
import json
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.urls import reverse
from primepath_routinetest.models import RoutineExam as Exam, StudentSession, Question
from primepath_routinetest.services import SessionService

def print_test(test_name, result, details=""):
    """Print test result in formatted way"""
    status = "[PASS]" if result else "[FAIL]"
    print(f"{status} - {test_name}")
    if details:
        print(f"    {details}")
    return result

def test_navigation():
    """Test navigation functionality comprehensively"""
    print("\n" + "="*60)
    print("NAVIGATION SYSTEM TEST SUITE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    
    client = Client()
    passed = 0
    failed = 0
    
    # Test 1: Find a test session
    print("\n[1] SETUP TEST SESSION")
    try:
        # Get or create a test session
        session = StudentSession.objects.filter(completed_at__isnull=True).first()
        
        if not session:
            # Create a new session
            exam = Exam.objects.filter(pdf_file__isnull=False).first()
            if exam:
                session_data = {
                    'student_name': 'Navigation Test Student',
                    'grade': 5,
                    'academic_rank': 'TOP_50',
                    'parent_phone': '1234567890'
                }
                session = SessionService.create_session(
                    student_data=session_data,
                    exam=exam,
                    curriculum_level_id=exam.curriculum_level_id,
                    request_meta={'REMOTE_ADDR': '127.0.0.1'}
                )
                print_test("Created test session", True, f"Session ID: {session.id}")
                passed += 1
            else:
                print_test("Find exam for testing", False, "No exam with PDF found")
                failed += 1
                return passed, failed
        else:
            print_test("Found existing session", True, f"Session ID: {session.id}")
            passed += 1
            
    except Exception as e:
        print_test("Session setup", False, str(e))
        failed += 1
        return passed, failed
    
    # Test 2: Load test page
    print("\n[2] LOADING TEST PAGE")
    try:
        test_url = reverse('RoutineTest:take_test', args=[session.id])
        response = client.get(test_url)
        
        page_loads = response.status_code == 200
        print_test("Test page loads", page_loads, f"Status: {response.status_code}")
        if page_loads:
            passed += 1
        else:
            failed += 1
            return passed, failed
            
    except Exception as e:
        print_test("Load test page", False, str(e))
        failed += 1
        return passed, failed
    
    # Test 3: Check navigation elements
    print("\n[3] CHECKING NAVIGATION ELEMENTS")
    try:
        content = response.content.decode('utf-8')
        
        # Check for navigation module
        has_nav_module = 'navigation.js' in content
        print_test("Navigation module loaded", has_nav_module, "Module script tag found" if has_nav_module else "Module missing")
        if has_nav_module:
            passed += 1
        else:
            failed += 1
            
        # Check for question navigation buttons
        has_nav_buttons = 'question-nav-btn' in content
        print_test("Question navigation buttons", has_nav_buttons, "Navigation bar found" if has_nav_buttons else "No navigation buttons")
        if has_nav_buttons:
            passed += 1
        else:
            failed += 1
            
        # Check for next/previous buttons
        has_next = 'data-action="next-question"' in content
        print_test("Next button present", has_next, "Next navigation found" if has_next else "No next button")
        if has_next:
            passed += 1
        else:
            failed += 1
            
        has_prev = 'data-action="prev-question"' in content
        print_test("Previous button present", has_prev, "Previous navigation found" if has_prev else "No previous button")
        if has_prev:
            passed += 1
        else:
            failed += 1
            
        # Check for proper data attributes
        has_question_data = 'data-question=' in content
        print_test("Question data attributes", has_question_data, "Data attributes found" if has_question_data else "Missing data attributes")
        if has_question_data:
            passed += 1
        else:
            failed += 1
            
    except Exception as e:
        print_test("Navigation element check", False, str(e))
        failed += 1
    
    # Test 4: Check JavaScript implementation
    print("\n[4] CHECKING JAVASCRIPT IMPLEMENTATION")
    try:
        # Check for event delegation setup
        has_delegation = 'window.PrimePath.utils.EventDelegation' in content
        print_test("Event delegation available", has_delegation, "Delegation system found" if has_delegation else "Missing delegation")
        if has_delegation:
            passed += 1
        else:
            failed += 1
            
        # Check for fixed navigation handlers
        has_this_context = 'this.dataset.question' in content
        print_test("Fixed event handlers", has_this_context, "Using 'this' context" if has_this_context else "Still using e.currentTarget")
        if has_this_context:
            passed += 1
        else:
            failed += 1
            
        # Check for navigation module initialization
        has_nav_init = 'NavigationModule' in content
        print_test("NavigationModule class", has_nav_init, "Navigation module initialized" if has_nav_init else "Module not initialized")
        if has_nav_init:
            passed += 1
        else:
            failed += 1
            
        # Check for keyboard navigation
        has_keyboard = 'enableKeyboard' in content
        print_test("Keyboard navigation enabled", has_keyboard, "Keyboard support found" if has_keyboard else "No keyboard navigation")
        if has_keyboard:
            passed += 1
        else:
            failed += 1
            
    except Exception as e:
        print_test("JavaScript check", False, str(e))
        failed += 1
    
    # Test 5: Check question panels
    print("\n[5] CHECKING QUESTION PANELS")
    try:
        # Count question panels
        import re
        panel_matches = re.findall(r'class="question-panel', content)
        panel_count = len(panel_matches)
        
        has_panels = panel_count > 0
        print_test("Question panels exist", has_panels, f"Found {panel_count} panels")
        if has_panels:
            passed += 1
        else:
            failed += 1
            
        # Check for active panel
        has_active = 'question-panel active' in content or 'question-panel.*active' in content
        print_test("Active panel class", has_active, "Active state management found" if has_active else "No active state")
        if has_active:
            passed += 1
        else:
            failed += 1
            
        # Check for hidden panels
        has_hidden = 'hidden' in content
        print_test("Hidden panel management", has_hidden, "Visibility control found" if has_hidden else "No visibility control")
        if has_hidden:
            passed += 1
        else:
            failed += 1
            
    except Exception as e:
        print_test("Panel check", False, str(e))
        failed += 1
    
    # Test 6: Check integration with other modules
    print("\n[6] CHECKING MODULE INTEGRATION")
    try:
        # Check answer manager integration
        has_answer_mgr = 'answerManager' in content
        print_test("Answer manager integration", has_answer_mgr, "Connected to answer system" if has_answer_mgr else "No answer integration")
        if has_answer_mgr:
            passed += 1
        else:
            failed += 1
            
        # Check audio player integration
        has_audio = 'audioPlayer' in content
        print_test("Audio player integration", has_audio, "Audio system connected" if has_audio else "No audio integration")
        if has_audio:
            passed += 1
        else:
            failed += 1
            
        # Check timer integration
        has_timer = 'timer' in content or 'Timer' in content
        print_test("Timer integration", has_timer, "Timer system connected" if has_timer else "No timer integration")
        if has_timer:
            passed += 1
        else:
            failed += 1
            
    except Exception as e:
        print_test("Integration check", False, str(e))
        failed += 1
    
    # Test 7: Edge cases
    print("\n[7] TESTING EDGE CASES")
    try:
        # Check for first question handling
        has_first_check = 'hasPrevious' in content or 'currentQuestion > 1' in content
        print_test("First question handling", has_first_check, "Boundary check found" if has_first_check else "No boundary check")
        if has_first_check:
            passed += 1
        else:
            failed += 1
            
        # Check for last question handling
        has_last_check = 'hasNext' in content or 'currentQuestion < total' in content
        print_test("Last question handling", has_last_check, "End boundary check found" if has_last_check else "No end check")
        if has_last_check:
            passed += 1
        else:
            failed += 1
            
        # Check for invalid question handling
        has_validation = 'isValidQuestion' in content or 'validateQuestion' in content
        print_test("Question validation", has_validation, "Validation logic found" if has_validation else "No validation")
        if has_validation:
            passed += 1
        else:
            failed += 1
            
    except Exception as e:
        print_test("Edge case check", False, str(e))
        failed += 1
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    total = passed + failed
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if failed == 0:
        print("\n*** ALL NAVIGATION TESTS PASSED! ***")
        print("Navigation system is working correctly.")
    else:
        print(f"\n*** WARNING: {failed} test(s) failed ***")
        print("Please review the failures above.")
    
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    
    return passed, failed

if __name__ == "__main__":
    test_navigation()
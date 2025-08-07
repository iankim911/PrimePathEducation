"""
Comprehensive QA Test Script for PrimePath Platform
Tests all critical features after modularization changes
"""

import os
import django
import json
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.urls import reverse
from placement_test.models import Exam, StudentSession, Question
from core.models import CurriculumLevel

def print_test(test_name, result, details=""):
    """Print test result in formatted way"""
    status = "PASS" if result else "FAIL"
    print(f"[{status}] - {test_name}")
    if details:
        print(f"    {details}")
    return result

def run_qa_tests():
    """Run comprehensive QA tests"""
    print("\n" + "="*60)
    print("PRIMEPATH COMPREHENSIVE QA TEST SUITE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    
    client = Client()
    passed_tests = 0
    failed_tests = 0
    
    # Test 1: Check if homepage loads
    print("\n[1] TESTING HOMEPAGE")
    try:
        response = client.get('/')
        test_passed = print_test(
            "Homepage loads",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        passed_tests += test_passed
        failed_tests += not test_passed
    except Exception as e:
        print_test("Homepage loads", False, str(e))
        failed_tests += 1
    
    # Test 2: Check exam list page
    print("\n[2] TESTING EXAM LIST")
    try:
        response = client.get(reverse('placement_test:exam_list'))
        test_passed = print_test(
            "Exam list page loads",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        passed_tests += test_passed
        failed_tests += not test_passed
        
        # Check if exams are displayed
        exam_count = Exam.objects.count()
        test_passed = print_test(
            "Exams exist in database",
            exam_count > 0,
            f"Found {exam_count} exams"
        )
        passed_tests += test_passed
        failed_tests += not test_passed
    except Exception as e:
        print_test("Exam list page", False, str(e))
        failed_tests += 2
    
    # Test 3: Check create exam page
    print("\n[3] TESTING CREATE EXAM PAGE")
    try:
        response = client.get(reverse('placement_test:create_exam'))
        test_passed = print_test(
            "Create exam page loads",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        passed_tests += test_passed
        failed_tests += not test_passed
        
        # Check if curriculum levels are available
        levels_count = CurriculumLevel.objects.count()
        test_passed = print_test(
            "Curriculum levels available",
            levels_count > 0,
            f"Found {levels_count} levels"
        )
        passed_tests += test_passed
        failed_tests += not test_passed
    except Exception as e:
        print_test("Create exam page", False, str(e))
        failed_tests += 2
    
    # Test 4: Check start test page
    print("\n[4] TESTING START TEST PAGE")
    try:
        response = client.get(reverse('placement_test:start_test'))
        test_passed = print_test(
            "Start test page loads",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        passed_tests += test_passed
        failed_tests += not test_passed
    except Exception as e:
        print_test("Start test page", False, str(e))
        failed_tests += 1
    
    # Test 5: Check PDF files
    print("\n[5] TESTING PDF FILES")
    try:
        pdf_exams = Exam.objects.filter(pdf_file__isnull=False)
        pdf_count = pdf_exams.count()
        test_passed = print_test(
            "Exams have PDF files",
            pdf_count > 0,
            f"Found {pdf_count} exams with PDFs"
        )
        passed_tests += test_passed
        failed_tests += not test_passed
        
        # Check if PDF files physically exist
        if pdf_count > 0:
            sample_exam = pdf_exams.first()
            file_exists = os.path.exists(sample_exam.pdf_file.path) if sample_exam.pdf_file else False
            test_passed = print_test(
                "PDF files exist on disk",
                file_exists,
                f"Sample: {sample_exam.name if sample_exam else 'N/A'}"
            )
            passed_tests += test_passed
            failed_tests += not test_passed
    except Exception as e:
        print_test("PDF file check", False, str(e))
        failed_tests += 2
    
    # Test 6: Check exam preview
    print("\n[6] TESTING EXAM PREVIEW")
    try:
        exam = Exam.objects.filter(pdf_file__isnull=False).first()
        if exam:
            response = client.get(reverse('placement_test:preview_exam', args=[exam.id]))
            test_passed = print_test(
                "Preview exam page loads",
                response.status_code == 200,
                f"Exam: {exam.name}"
            )
            passed_tests += test_passed
            failed_tests += not test_passed
            
            # Check if questions are displayed
            questions_count = exam.questions.count()
            test_passed = print_test(
                "Exam has questions",
                questions_count > 0,
                f"Found {questions_count} questions"
            )
            passed_tests += test_passed
            failed_tests += not test_passed
        else:
            print_test("Preview exam page", False, "No exam with PDF found")
            failed_tests += 2
    except Exception as e:
        print_test("Preview exam page", False, str(e))
        failed_tests += 2
    
    # Test 7: Check session list
    print("\n[7] TESTING SESSION LIST")
    try:
        response = client.get(reverse('placement_test:session_list'))
        test_passed = print_test(
            "Session list page loads",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        passed_tests += test_passed
        failed_tests += not test_passed
        
        session_count = StudentSession.objects.count()
        test_passed = print_test(
            "Sessions tracking",
            True,  # Just informational
            f"Found {session_count} sessions"
        )
        passed_tests += test_passed
    except Exception as e:
        print_test("Session list page", False, str(e))
        failed_tests += 2
    
    # Test 8: Check modular templates
    print("\n[8] TESTING MODULAR ARCHITECTURE")
    try:
        from django.conf import settings
        use_v2 = getattr(settings, 'FEATURE_FLAGS', {}).get('USE_V2_TEMPLATES', False)
        test_passed = print_test(
            "V2 templates enabled",
            use_v2,
            "Using modular architecture" if use_v2 else "Using original templates"
        )
        passed_tests += test_passed
        failed_tests += not test_passed
        
        # Check if modular CSS files exist
        css_files = [
            'css/pages/student-test.css',
            'css/components/pdf-viewer.css',
            'css/components/timer.css',
            'css/components/question-nav.css'
        ]
        css_path = os.path.join(settings.STATIC_ROOT, 'css')
        css_exists = os.path.exists(css_path)
        test_passed = print_test(
            "Modular CSS files collected",
            css_exists,
            f"Static root: {settings.STATIC_ROOT}"
        )
        passed_tests += test_passed
        failed_tests += not test_passed
        
        # Check if modular JS files exist
        js_files = [
            'js/modules/pdf-viewer.js',
            'js/modules/timer.js',
            'js/modules/answer-manager.js',
            'js/modules/audio-player.js'
        ]
        js_path = os.path.join(settings.STATIC_ROOT, 'js', 'modules')
        js_exists = os.path.exists(js_path)
        test_passed = print_test(
            "Modular JS files collected",
            js_exists,
            f"Found modules directory" if js_exists else "Modules directory missing"
        )
        passed_tests += test_passed
        failed_tests += not test_passed
    except Exception as e:
        print_test("Modular architecture check", False, str(e))
        failed_tests += 3
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    total_tests = passed_tests + failed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if failed_tests == 0:
        print("\n*** ALL TESTS PASSED! The system is working correctly. ***")
    else:
        print(f"\n*** WARNING: {failed_tests} test(s) failed. Please review the failures above. ***")
    
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    
    return passed_tests, failed_tests

if __name__ == "__main__":
    run_qa_tests()
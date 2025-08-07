"""
Comprehensive QA Test Suite
Tests all features after DRF and Celery installation
"""
import os
import django
import json
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from placement_test.models import Exam, StudentSession, Question
from core.models import School, Program, SubProgram, CurriculumLevel

def test_traditional_views():
    """Test traditional Django views are still working"""
    client = Client()
    tests_passed = 0
    tests_total = 0
    
    print("\n=== Testing Traditional Django Views ===")
    
    # Test URLs that should work
    test_urls = [
        ('/', 'Home page'),
        ('/create-exam/', 'Create exam page'),
        ('/exams/', 'Exams list page'),
        ('/admin-dashboard/', 'Admin dashboard'),
        ('/upload-exam/', 'Upload exam page'),
    ]
    
    for url, description in test_urls:
        tests_total += 1
        try:
            response = client.get(url)
            if response.status_code in [200, 302]:  # 302 for redirects
                print(f"[PASS] {description} ({url}): {response.status_code}")
                tests_passed += 1
            else:
                print(f"[FAIL] {description} ({url}): {response.status_code}")
        except Exception as e:
            print(f"[FAIL] {description} ({url}): {str(e)[:50]}")
    
    return tests_passed, tests_total

def test_drf_api_endpoints():
    """Test DRF API endpoints"""
    client = Client()
    tests_passed = 0
    tests_total = 0
    
    print("\n=== Testing DRF API Endpoints ===")
    
    endpoints = [
        ('/api/v1/exams/', 'Exams API'),
        ('/api/v1/sessions/', 'Sessions API'),
        ('/api/v1/schools/', 'Schools API'),
        ('/api/v1/programs/', 'Programs API'),
        ('/api/v1/health/', 'Health Check API'),
    ]
    
    for endpoint, description in endpoints:
        tests_total += 1
        try:
            response = client.get(endpoint)
            if response.status_code == 200:
                print(f"[PASS] {description} ({endpoint}): {response.status_code}")
                tests_passed += 1
            elif response.status_code == 403:
                print(f"[PASS] {description} ({endpoint}): {response.status_code} (Auth required)")
                tests_passed += 1
            else:
                print(f"[FAIL] {description} ({endpoint}): {response.status_code}")
        except Exception as e:
            print(f"[FAIL] {description} ({endpoint}): {str(e)[:50]}")
    
    return tests_passed, tests_total

def test_ajax_endpoints():
    """Test AJAX endpoints used by frontend"""
    client = Client()
    tests_passed = 0
    tests_total = 0
    
    print("\n=== Testing AJAX Endpoints ===")
    
    # Get first exam for testing
    exam = Exam.objects.first()
    if exam:
        ajax_urls = [
            (f'/api/placement/exams/{exam.id}/questions/', 'Get exam questions'),
            ('/api/placement/curriculum-levels/', 'Get curriculum levels'),
            ('/api/schools/', 'Get schools list'),
        ]
        
        for url, description in ajax_urls:
            tests_total += 1
            try:
                response = client.get(url)
                if response.status_code == 200:
                    print(f"[PASS] {description} ({url}): {response.status_code}")
                    tests_passed += 1
                else:
                    print(f"[FAIL] {description} ({url}): {response.status_code}")
            except Exception as e:
                print(f"[FAIL] {description} ({url}): {str(e)[:50]}")
    
    return tests_passed, tests_total

def test_models_integrity():
    """Test database models are working correctly"""
    tests_passed = 0
    tests_total = 0
    
    print("\n=== Testing Model Integrity ===")
    
    # Test Exam model
    tests_total += 1
    try:
        exam_count = Exam.objects.count()
        print(f"[PASS] Exam model: {exam_count} exams found")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Exam model: {str(e)[:50]}")
    
    # Test Question model
    tests_total += 1
    try:
        question_count = Question.objects.count()
        print(f"[PASS] Question model: {question_count} questions found")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Question model: {str(e)[:50]}")
    
    # Test StudentSession model
    tests_total += 1
    try:
        session_count = StudentSession.objects.count()
        print(f"[PASS] StudentSession model: {session_count} sessions found")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] StudentSession model: {str(e)[:50]}")
    
    # Test School model
    tests_total += 1
    try:
        school_count = School.objects.count()
        print(f"[PASS] School model: {school_count} schools found")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] School model: {str(e)[:50]}")
    
    # Test CurriculumLevel model
    tests_total += 1
    try:
        level_count = CurriculumLevel.objects.count()
        print(f"[PASS] CurriculumLevel model: {level_count} levels found")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] CurriculumLevel model: {str(e)[:50]}")
    
    return tests_passed, tests_total

def test_celery_config():
    """Test Celery configuration"""
    tests_passed = 0
    tests_total = 0
    
    print("\n=== Testing Celery Configuration ===")
    
    # Test Celery import
    tests_total += 1
    try:
        from primepath_project.celery import app
        print(f"[PASS] Celery app imported successfully")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Celery import: {str(e)[:50]}")
    
    # Test task discovery
    tests_total += 1
    try:
        from core.tasks import cleanup_old_sessions, process_exam_pdf
        print(f"[PASS] Celery tasks discovered")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Task discovery: {str(e)[:50]}")
    
    # Test Celery settings
    tests_total += 1
    try:
        from django.conf import settings
        if hasattr(settings, 'CELERY_BROKER_URL'):
            print(f"[PASS] Celery settings configured")
            tests_passed += 1
        else:
            print(f"[FAIL] Celery settings missing")
    except Exception as e:
        print(f"[FAIL] Celery settings: {str(e)[:50]}")
    
    return tests_passed, tests_total

def test_student_interface():
    """Test student test-taking interface"""
    client = Client()
    tests_passed = 0
    tests_total = 0
    
    print("\n=== Testing Student Interface ===")
    
    # Get first exam for testing
    exam = Exam.objects.first()
    if exam:
        # Test student login page
        tests_total += 1
        try:
            response = client.get(f'/placement-test/{exam.id}/')
            if response.status_code == 200:
                print(f"[PASS] Student login page loads")
                tests_passed += 1
            else:
                print(f"[FAIL] Student login page: {response.status_code}")
        except Exception as e:
            print(f"[FAIL] Student login page: {str(e)[:50]}")
        
        # Test starting a session
        tests_total += 1
        try:
            response = client.post(f'/placement-test/{exam.id}/', {
                'student_name': 'Test Student',
                'parent_phone': '1234567890',
                'grade': 10,
                'school': 'Test School',
                'academic_rank': 'TOP_10'
            })
            if response.status_code in [200, 302]:
                print(f"[PASS] Can start test session")
                tests_passed += 1
            else:
                print(f"[FAIL] Start session: {response.status_code}")
        except Exception as e:
            print(f"[FAIL] Start session: {str(e)[:50]}")
    
    return tests_passed, tests_total

def main():
    """Run all tests and report results"""
    print("=" * 60)
    print("COMPREHENSIVE QA TEST SUITE")
    print("Testing after DRF and Celery Installation")
    print("=" * 60)
    
    total_passed = 0
    total_tests = 0
    
    # Run all test suites
    test_suites = [
        test_traditional_views,
        test_drf_api_endpoints,
        test_ajax_endpoints,
        test_models_integrity,
        test_celery_config,
        test_student_interface,
    ]
    
    for test_suite in test_suites:
        passed, total = test_suite()
        total_passed += passed
        total_tests += total
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_tests - total_passed}")
    print(f"Success Rate: {(total_passed/total_tests*100):.1f}%")
    
    if total_passed == total_tests:
        print("\n[SUCCESS] All tests passed! DRF and Celery installation successful.")
    elif total_passed / total_tests >= 0.9:
        print("\n[WARNING] Most tests passed but some issues detected.")
    else:
        print("\n[ERROR] Significant test failures detected.")
    
    return total_passed == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
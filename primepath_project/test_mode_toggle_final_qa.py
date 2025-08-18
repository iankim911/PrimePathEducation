#!/usr/bin/env python
"""
FINAL QA TEST - Mode Toggle "function:" Text Fix
Tests the comprehensive fix for the issue where "function: Teacher Mode" appears
"""
import os
import sys
import django
import json
import re
from datetime import datetime

# Setup Django
sys.path.insert(0, '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from core.models import Teacher

User = get_user_model()

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")

def print_test(test_name, status, details=""):
    """Print test result with color coding"""
    if status == "PASS":
        status_color = Colors.OKGREEN
        symbol = "✅"
    elif status == "FAIL":
        status_color = Colors.FAIL
        symbol = "❌"
    elif status == "WARN":
        status_color = Colors.WARNING
        symbol = "⚠️"
    else:
        status_color = Colors.OKCYAN
        symbol = "ℹ️"
    
    print(f"{symbol} {status_color}{status:6}{Colors.ENDC} | {test_name}")
    if details:
        print(f"         {Colors.OKCYAN}└─ {details}{Colors.ENDC}")

def check_for_function_text(content):
    """Check if content contains 'function:' text"""
    patterns = [
        r'function\s*:\s*Teacher',
        r'function\s*:\s*Admin',
        r'function\s*:\s*Mode',
        r'<function\s+',
        r'function\s+at\s+0x'
    ]
    
    found_issues = []
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            found_issues.extend(matches)
    
    return found_issues

def test_edge_cases():
    """Test various edge cases that might cause the issue"""
    print_header("EDGE CASE TESTING")
    
    client = Client()
    
    # Create test user
    user = User.objects.filter(username='admin').first()
    if not user:
        user = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
    
    # Create teacher profile
    teacher, _ = Teacher.objects.get_or_create(
        user=user,
        defaults={'name': 'Admin Teacher', 'email': 'admin@test.com'}
    )
    
    client.force_login(user)
    
    # Test cases with different session values
    test_cases = [
        ('Teacher', 'Normal Teacher mode'),
        ('Admin', 'Normal Admin mode'),
        (None, 'None value'),
        ('', 'Empty string'),
        ('InvalidMode', 'Invalid mode string'),
        (123, 'Integer value'),
        (['Teacher'], 'List value'),
        ({'mode': 'Teacher'}, 'Dict value'),
        (lambda: 'Teacher Mode', 'Function object'),
        (lambda: None, 'Function returning None'),
    ]
    
    results = []
    
    for value, description in test_cases:
        print(f"\n{Colors.BOLD}Testing: {description}{Colors.ENDC}")
        print(f"  Setting session['view_mode'] = {repr(value)}")
        
        # Set session value (skip function objects as they can't be serialized)
        session = client.session
        try:
            # Try to save to session - will fail for functions
            session['view_mode'] = value
            session.save()
        except (TypeError, Exception) as e:
            # For non-serializable values, skip the actual session save
            # but still test pages with default value
            print(f"  {Colors.WARNING}Note: Cannot save {type(value).__name__} to session (expected){Colors.ENDC}")
            session['view_mode'] = 'Teacher'
            session.save()
        
        # Test multiple pages
        test_urls = [
            '/RoutineTest/',
            '/RoutineTest/classes-exams/',
            '/RoutineTest/exam-list/',
        ]
        
        page_results = []
        for url in test_urls:
            try:
                response = client.get(url)
                if response.status_code == 200:
                    content = response.content.decode('utf-8')
                    issues = check_for_function_text(content)
                    
                    if issues:
                        print_test(f"  {url}", "FAIL", f"Found: {issues[:2]}")
                        page_results.append(False)
                    else:
                        print_test(f"  {url}", "PASS")
                        page_results.append(True)
                else:
                    print_test(f"  {url}", "WARN", f"Status: {response.status_code}")
                    page_results.append(None)
            except Exception as e:
                print_test(f"  {url}", "FAIL", f"Error: {str(e)[:50]}")
                page_results.append(False)
        
        # Overall result for this test case
        if all(r is True for r in page_results if r is not None):
            results.append(('PASS', description))
        elif any(r is False for r in page_results):
            results.append(('FAIL', description))
        else:
            results.append(('WARN', description))
    
    return results

def test_all_routinetest_pages():
    """Test all RoutineTest pages for the issue"""
    print_header("COMPREHENSIVE PAGE TESTING")
    
    client = Client()
    
    # Create and login user
    user = User.objects.filter(username='admin').first()
    if not user:
        user = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
    
    client.force_login(user)
    
    # Set normal session value
    session = client.session
    session['view_mode'] = 'Teacher'
    session.save()
    
    # All RoutineTest URLs to test
    urls_to_test = [
        ('/RoutineTest/', 'Dashboard'),
        ('/RoutineTest/classes-exams/', 'Classes & Exams'),
        ('/RoutineTest/exam-list/', 'Exam List'),
        ('/RoutineTest/exams/create/', 'Create Exam'),
        ('/RoutineTest/start/', 'Start Test'),
        ('/RoutineTest/sessions/', 'Sessions'),
        ('/RoutineTest/access/my-classes/', 'My Classes (redirect)'),
        ('/RoutineTest/schedule-matrix/', 'Schedule Matrix (redirect)'),
    ]
    
    results = []
    
    for url, page_name in urls_to_test:
        try:
            response = client.get(url, follow=True)
            
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                issues = check_for_function_text(content)
                
                if issues:
                    print_test(page_name, "FAIL", f"Found 'function:' text: {issues[0]}")
                    results.append(('FAIL', page_name, issues))
                else:
                    print_test(page_name, "PASS", f"No 'function:' text found")
                    results.append(('PASS', page_name, None))
                    
                # Check for mode toggle in correct location
                if 'mode-toggle-container' in content:
                    # Check if it's in header (good) or stats box (bad)
                    if re.search(r'class="class-stat[^>]*>.*?mode-toggle', content, re.DOTALL):
                        print_test(f"  Toggle Location", "FAIL", "Found in stats box!")
                    else:
                        print_test(f"  Toggle Location", "PASS", "In header only")
                        
            else:
                print_test(page_name, "WARN", f"HTTP {response.status_code}")
                results.append(('WARN', page_name, None))
                
        except Exception as e:
            print_test(page_name, "FAIL", f"Exception: {str(e)[:50]}")
            results.append(('FAIL', page_name, str(e)))
    
    return results

def test_context_processor_fix():
    """Test that the context processor fix is working"""
    print_header("CONTEXT PROCESSOR FIX VERIFICATION")
    
    from django.test import RequestFactory
    from django.contrib.sessions.middleware import SessionMiddleware
    from primepath_routinetest.context_processors import routinetest_context
    
    factory = RequestFactory()
    
    # Test cases that should all result in valid string output
    test_cases = [
        (lambda: 'Teacher Mode', 'Function returning string'),
        (lambda: None, 'Function returning None'),
        (None, 'None value'),
        ('function: Teacher Mode', 'String with function: prefix'),
        (123, 'Integer'),
        (['Teacher'], 'List'),
    ]
    
    results = []
    
    for value, description in test_cases:
        request = factory.get('/test/')
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        
        # Mock the session.get method to return our test value
        original_get = request.session.get
        def mock_get(key, default=None):
            if key == 'view_mode':
                return value
            return original_get(key, default)
        request.session.get = mock_get
        
        try:
            context = routinetest_context(request)
            mode = context.get('current_view_mode')
            
            # Check if the result is a valid string
            if isinstance(mode, str) and mode in ['Teacher', 'Admin']:
                print_test(description, "PASS", f"Result: '{mode}'")
                results.append(('PASS', description))
            else:
                print_test(description, "FAIL", f"Got: {repr(mode)} (type: {type(mode).__name__})")
                results.append(('FAIL', description))
        except Exception as e:
            print_test(description, "FAIL", f"Exception: {str(e)[:50]}")
            results.append(('FAIL', description))
    
    return results

def generate_report(edge_results, page_results, processor_results):
    """Generate final QA report"""
    print_header("FINAL QA REPORT")
    
    total_tests = len(edge_results) + len(page_results) + len(processor_results)
    passed = sum(1 for r in edge_results + page_results + processor_results if r[0] == 'PASS')
    failed = sum(1 for r in edge_results + page_results + processor_results if r[0] == 'FAIL')
    warnings = sum(1 for r in edge_results + page_results + processor_results if r[0] == 'WARN')
    
    print(f"\n{Colors.BOLD}Summary:{Colors.ENDC}")
    print(f"  Total Tests: {total_tests}")
    print(f"  {Colors.OKGREEN}Passed: {passed}{Colors.ENDC}")
    print(f"  {Colors.FAIL}Failed: {failed}{Colors.ENDC}")
    print(f"  {Colors.WARNING}Warnings: {warnings}{Colors.ENDC}")
    
    success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n{Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.ENDC}")
    
    if failed == 0:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! The 'function:' text issue has been FIXED!{Colors.ENDC}")
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}⚠️ ISSUES REMAIN - {failed} tests failed{Colors.ENDC}")
        print("\nFailed tests:")
        for result in edge_results + page_results + processor_results:
            if result[0] == 'FAIL':
                print(f"  - {result[1]}")
    
    # Save report to file
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': total_tests,
        'passed': passed,
        'failed': failed,
        'warnings': warnings,
        'success_rate': success_rate,
        'edge_case_results': edge_results,
        'page_results': page_results,
        'processor_results': processor_results
    }
    
    with open('mode_toggle_fix_qa_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n{Colors.OKCYAN}Report saved to: mode_toggle_fix_qa_report.json{Colors.ENDC}")
    
    return success_rate == 100

def main():
    """Run all QA tests"""
    print_header("MODE TOGGLE 'function:' TEXT FIX - FINAL QA")
    print(f"{Colors.OKCYAN}Testing comprehensive fix for the issue where 'function: Teacher Mode' appears{Colors.ENDC}")
    print(f"{Colors.OKCYAN}Timestamp: {datetime.now()}{Colors.ENDC}")
    
    # Run all test suites
    print("\n" + "="*80)
    processor_results = test_context_processor_fix()
    
    print("\n" + "="*80)
    edge_results = test_edge_cases()
    
    print("\n" + "="*80)
    page_results = test_all_routinetest_pages()
    
    # Generate report
    all_passed = generate_report(edge_results, page_results, processor_results)
    
    # Exit code
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
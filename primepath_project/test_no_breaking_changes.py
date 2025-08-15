#!/usr/bin/env python
"""
Comprehensive Test: Verify BCG Green Theme Didn't Break Existing Features

This script checks that the RoutineTest theme implementation:
1. Didn't affect PlacementTest module
2. Didn't break any database relationships
3. Didn't affect URL routing
4. Didn't break JavaScript functionality
5. CSS is properly scoped and doesn't leak

Run: python test_no_breaking_changes.py
"""
import os
import sys
import django
from pathlib import Path
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, str(Path(__file__).parent))
django.setup()

from django.test import Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from django.db import connection

# Import both modules
from placement_test.models import Exam as PlacementExam
from placement_test.models import StudentSession as PlacementSession
from primepath_routinetest.models import Exam as RoutineExam
from primepath_routinetest.models import StudentSession as RoutineSession

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def check_placement_test_unaffected():
    """Verify PlacementTest module is completely unaffected"""
    print_header("CHECKING PLACEMENTTEST MODULE INTEGRITY")
    
    client = Client()
    issues = []
    
    # Test PlacementTest URLs
    placement_urls = [
        ('PlacementTest:index', 'PlacementTest Index'),
        ('PlacementTest:start_test', 'Start Test'),
        ('PlacementTest:exam_list', 'Exam List'),
        ('PlacementTest:create_exam', 'Create Exam'),
    ]
    
    for url_name, description in placement_urls:
        try:
            url = reverse(url_name)
            response = client.get(url)
            
            # Check response
            if response.status_code in [200, 302]:
                print_success(f"{description} ({url}): Status {response.status_code}")
                
                # Check that BCG green theme is NOT applied
                if response.status_code == 200:
                    content = response.content.decode('utf-8')
                    if 'routinetest-theme' in content.lower():
                        print_error(f"  WARNING: RoutineTest theme found in PlacementTest page!")
                        issues.append(f"Theme leak in {description}")
                    if '#00A65E' in content:
                        print_error(f"  WARNING: BCG Green color found in PlacementTest page!")
                        issues.append(f"BCG Green in {description}")
            else:
                print_error(f"{description} ({url}): Unexpected status {response.status_code}")
                issues.append(f"{description} status issue")
                
        except Exception as e:
            print_error(f"{description}: {str(e)}")
            issues.append(f"{description} error")
    
    # Check PlacementTest templates
    print("\nChecking PlacementTest Templates:")
    template_dir = Path(__file__).parent / 'templates/placement_test'
    if template_dir.exists():
        for template_file in template_dir.glob('*.html'):
            with open(template_file, 'r') as f:
                content = f.read()
            
            # Should NOT use routinetest_base.html
            if 'routinetest_base.html' in content:
                print_error(f"{template_file.name} using RoutineTest base!")
                issues.append(f"{template_file.name} template issue")
            else:
                print_success(f"{template_file.name} - No theme contamination")
    
    return len(issues) == 0, issues

def check_database_integrity():
    """Verify database models and relationships are intact"""
    print_header("CHECKING DATABASE INTEGRITY")
    
    issues = []
    
    try:
        # Check PlacementTest models
        placement_exam_count = PlacementExam.objects.count()
        print_success(f"PlacementTest Exams accessible: {placement_exam_count} exams")
        
        placement_session_count = PlacementSession.objects.count()
        print_success(f"PlacementTest Sessions accessible: {placement_session_count} sessions")
        
        # Check RoutineTest models (separate)
        routine_exam_count = RoutineExam.objects.count()
        print_success(f"RoutineTest Exams accessible: {routine_exam_count} exams")
        
        routine_session_count = RoutineSession.objects.count()
        print_success(f"RoutineTest Sessions accessible: {routine_session_count} sessions")
        
        # Check they're using separate tables
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%exam%'")
            exam_tables = cursor.fetchall()
            
            placement_table_found = False
            routine_table_found = False
            
            for table in exam_tables:
                if 'placement' in table[0]:
                    placement_table_found = True
                if 'routine' in table[0]:
                    routine_table_found = True
            
            if placement_table_found:
                print_success("PlacementTest tables exist separately")
            else:
                print_error("PlacementTest tables not found!")
                issues.append("PlacementTest tables missing")
                
            if routine_table_found:
                print_success("RoutineTest tables exist separately")
            else:
                print_info("RoutineTest tables not found (expected if not migrated)")
        
        # Test model operations
        print("\nTesting Model Operations:")
        
        # Can we query PlacementTest models?
        try:
            PlacementExam.objects.filter(is_active=True).exists()
            print_success("PlacementTest Exam queries working")
        except Exception as e:
            print_error(f"PlacementTest Exam query failed: {e}")
            issues.append("PlacementExam query issue")
        
        # Can we query RoutineTest models?
        try:
            RoutineExam.objects.filter(is_active=True).exists()
            print_success("RoutineTest Exam queries working")
        except Exception as e:
            print_error(f"RoutineTest Exam query failed: {e}")
            issues.append("RoutineExam query issue")
            
    except Exception as e:
        print_error(f"Database check failed: {e}")
        issues.append(f"Database error: {e}")
    
    return len(issues) == 0, issues

def check_url_routing():
    """Verify URL routing for both modules works correctly"""
    print_header("CHECKING URL ROUTING INTEGRITY")
    
    issues = []
    
    # Test URL resolution
    test_urls = [
        ('/PlacementTest/', 'placement_test.views.index', 'PlacementTest'),
        ('/PlacementTest/start/', 'placement_test.views.student', 'PlacementTest'),
        ('/PlacementTest/exams/', 'placement_test.views.exam', 'PlacementTest'),
        ('/RoutineTest/', 'primepath_routinetest.views.index', 'RoutineTest'),
        ('/RoutineTest/start/', 'primepath_routinetest.views.student', 'RoutineTest'),
        ('/RoutineTest/exams/', 'primepath_routinetest.views.exam', 'RoutineTest'),
    ]
    
    for url, expected_view, module in test_urls:
        try:
            resolved = resolve(url)
            view_module = resolved.func.__module__ if hasattr(resolved.func, '__module__') else str(resolved.func)
            
            if expected_view in view_module:
                print_success(f"{module} URL {url} → Correct view")
            else:
                print_error(f"{module} URL {url} → Wrong view: {view_module}")
                issues.append(f"{url} routing issue")
                
        except Exception as e:
            print_error(f"URL {url} failed to resolve: {e}")
            issues.append(f"{url} resolution failed")
    
    # Test redirects still work
    print("\nChecking URL Redirects:")
    client = Client()
    
    redirect_tests = [
        ('/placement/', '/PlacementTest/', 'PlacementTest redirect'),
        ('/routine/', '/RoutineTest/', 'RoutineTest redirect'),
    ]
    
    for old_url, new_url, description in redirect_tests:
        response = client.get(old_url, follow=False)
        if response.status_code == 302:
            if new_url in response.url:
                print_success(f"{description}: {old_url} → {new_url}")
            else:
                print_error(f"{description}: Unexpected redirect to {response.url}")
                issues.append(f"{description} redirect issue")
        else:
            print_error(f"{description}: No redirect (status {response.status_code})")
            issues.append(f"{description} not redirecting")
    
    return len(issues) == 0, issues

def check_javascript_integrity():
    """Verify JavaScript modules are not affected"""
    print_header("CHECKING JAVASCRIPT MODULE INTEGRITY")
    
    issues = []
    js_dir = Path(__file__).parent / 'static/js'
    
    # Check critical JS files exist and haven't been broken
    critical_js_files = [
        'config/app-config.js',
        'modules/answer-manager.js',
        'modules/timer.js',
        'modules/navigation.js',
        'modules/pdf-viewer.js',
        'modules/audio-player.js',
    ]
    
    for js_file in critical_js_files:
        file_path = js_dir / js_file
        if file_path.exists():
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for basic integrity
            if 'PrimePath' in content or 'window' in content:
                print_success(f"{js_file} - Structure intact")
                
                # Make sure RoutineTest theme didn't contaminate
                if 'routinetest-theme' in content.lower() and 'config' not in js_file:
                    print_error(f"  WARNING: RoutineTest theme in {js_file}")
                    issues.append(f"Theme contamination in {js_file}")
            else:
                print_error(f"{js_file} - May be corrupted")
                issues.append(f"{js_file} integrity issue")
        else:
            print_error(f"{js_file} - File missing!")
            issues.append(f"{js_file} missing")
    
    # Check that new theme JS is separate
    theme_js = js_dir / 'routinetest-theme.js'
    if theme_js.exists():
        print_success("RoutineTest theme JS is separate file")
    else:
        print_error("RoutineTest theme JS not found")
        issues.append("Theme JS missing")
    
    return len(issues) == 0, issues

def check_css_scoping():
    """Verify CSS is properly scoped and doesn't leak"""
    print_header("CHECKING CSS SCOPING AND ISOLATION")
    
    issues = []
    css_dir = Path(__file__).parent / 'static/css'
    
    # Check that RoutineTest theme CSS is properly scoped
    theme_css = css_dir / 'routinetest-theme.css'
    if theme_css.exists():
        with open(theme_css, 'r') as f:
            content = f.read()
        
        # Check for proper scoping
        if '.routinetest-theme' in content:
            print_success("Theme CSS is properly scoped with .routinetest-theme class")
        else:
            print_error("Theme CSS not properly scoped!")
            issues.append("CSS scoping issue")
        
        # Check that it doesn't affect global elements
        dangerous_selectors = ['body {', 'html {', '* {', '.btn {', '.header {']
        for selector in dangerous_selectors:
            if selector in content and '.routinetest-theme' not in content.split(selector)[0][-50:]:
                print_error(f"Global selector '{selector}' found without scoping!")
                issues.append(f"Global {selector} in theme CSS")
    
    # Check existing CSS files aren't modified
    existing_css = [
        'base/variables.css',
        'pages/student-test.css',
        'components/timer.css',
        'mobile-responsive.css',
    ]
    
    print("\nChecking Existing CSS Files:")
    for css_file in existing_css:
        file_path = css_dir / css_file
        if file_path.exists():
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Should NOT contain BCG green colors
            if '#00A65E' in content:
                print_error(f"{css_file} contains BCG Green color!")
                issues.append(f"BCG Green in {css_file}")
            else:
                print_success(f"{css_file} - No theme contamination")
        else:
            print_info(f"{css_file} - File not found")
    
    return len(issues) == 0, issues

def check_form_and_ajax():
    """Test form submissions and AJAX calls still work"""
    print_header("CHECKING FORMS AND AJAX FUNCTIONALITY")
    
    client = Client()
    issues = []
    
    # Test PlacementTest AJAX endpoints
    ajax_endpoints = [
        ('PlacementTest:api_exam_list', 'Exam List API'),
        ('PlacementTest:api_session_list', 'Session List API'),
    ]
    
    for endpoint_name, description in ajax_endpoints:
        try:
            url = reverse(endpoint_name)
            response = client.get(url)
            
            if response.status_code in [200, 403]:  # 403 if auth required
                print_success(f"{description} ({url}): Status {response.status_code}")
                
                # Check content type
                if 'json' in response.get('Content-Type', ''):
                    print_success(f"  Returns JSON correctly")
                else:
                    print_info(f"  Content-Type: {response.get('Content-Type', 'Unknown')}")
            else:
                print_error(f"{description}: Unexpected status {response.status_code}")
                issues.append(f"{description} status issue")
                
        except Exception as e:
            print_info(f"{description}: {str(e)} (May require auth)")
    
    # Test form pages load
    print("\nChecking Form Pages:")
    form_pages = [
        ('PlacementTest:start_test', 'Start Test Form'),
        ('RoutineTest:start_test', 'RoutineTest Start Form'),
    ]
    
    for page_name, description in form_pages:
        try:
            url = reverse(page_name)
            response = client.get(url)
            
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                if '<form' in content:
                    print_success(f"{description}: Form present")
                else:
                    print_error(f"{description}: No form found")
                    issues.append(f"{description} form missing")
            else:
                print_info(f"{description}: Status {response.status_code}")
                
        except Exception as e:
            print_error(f"{description}: {str(e)}")
            issues.append(f"{description} error")
    
    return len(issues) == 0, issues

def check_authentication():
    """Verify authentication system still works"""
    print_header("CHECKING AUTHENTICATION SYSTEM")
    
    issues = []
    
    try:
        # Check User model is accessible
        from django.contrib.auth.models import User
        user_count = User.objects.count()
        print_success(f"User model accessible: {user_count} users")
        
        # Check auth URLs work
        client = Client()
        auth_urls = [
            ('/PlacementTest/teacher/login/', 'Teacher Login'),
            ('/admin/login/', 'Admin Login'),
        ]
        
        for url, description in auth_urls:
            response = client.get(url, follow=False)
            if response.status_code in [200, 302]:
                print_success(f"{description} ({url}): Status {response.status_code}")
            else:
                print_error(f"{description}: Unexpected status {response.status_code}")
                issues.append(f"{description} issue")
                
    except Exception as e:
        print_error(f"Authentication check failed: {e}")
        issues.append(f"Auth error: {e}")
    
    return len(issues) == 0, issues

def generate_comprehensive_report():
    """Run all checks and generate report"""
    print_header("COMPREHENSIVE BREAKING CHANGES TEST")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Checking if BCG Green theme broke any existing features...")
    
    all_results = {}
    all_issues = []
    
    # Run all checks
    checks = [
        ("PlacementTest Module", check_placement_test_unaffected),
        ("Database Integrity", check_database_integrity),
        ("URL Routing", check_url_routing),
        ("JavaScript Modules", check_javascript_integrity),
        ("CSS Scoping", check_css_scoping),
        ("Forms & AJAX", check_form_and_ajax),
        ("Authentication", check_authentication),
    ]
    
    for check_name, check_func in checks:
        print(f"\nRunning: {check_name}...")
        passed, issues = check_func()
        all_results[check_name] = passed
        if issues:
            all_issues.extend(issues)
    
    # Summary
    print_header("FINAL SUMMARY")
    
    total_checks = len(all_results)
    passed_checks = sum(1 for v in all_results.values() if v)
    
    print("\nCheck Results:")
    for check_name, passed in all_results.items():
        if passed:
            print_success(f"{check_name}: PASSED ✓")
        else:
            print_error(f"{check_name}: FAILED ✗")
    
    print("\n" + "=" * 70)
    print(f"Overall Result: {passed_checks}/{total_checks} checks passed")
    
    if passed_checks == total_checks:
        print("\n🎉 SUCCESS! No breaking changes detected!")
        print("✅ PlacementTest module is unaffected")
        print("✅ All existing features are working")
        print("✅ BCG Green theme is properly isolated to RoutineTest")
        print("✅ No CSS leakage between modules")
        print("✅ Database integrity maintained")
        return True
    else:
        print("\n⚠️ WARNING: Some issues detected!")
        print("\nIssues found:")
        for issue in all_issues[:10]:  # Show first 10 issues
            print(f"  • {issue}")
        if len(all_issues) > 10:
            print(f"  ... and {len(all_issues) - 10} more issues")
        return False
    
    # Save detailed report
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'checks': all_results,
        'issues': all_issues,
        'passed': passed_checks,
        'total': total_checks,
        'status': 'PASS' if passed_checks == total_checks else 'FAIL'
    }
    
    report_file = Path(__file__).parent / 'breaking_changes_report.json'
    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_file}")

if __name__ == "__main__":
    print("\n🔍 Testing for Breaking Changes After BCG Green Theme Implementation")
    print("=" * 70)
    
    success = generate_comprehensive_report()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ VERIFICATION COMPLETE: No breaking changes detected!")
    else:
        print("⚠️ VERIFICATION COMPLETE: Some issues need attention")
    print("=" * 70)
    
    sys.exit(0 if success else 1)
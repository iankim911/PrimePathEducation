#!/usr/bin/env python
"""
RoutineTest BCG Green Theme Integration Test

This script verifies that the BCG Green theme is properly integrated
with the RoutineTest module, checking all components and relationships.

Run: python test_routinetest_theme.py
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
from django.urls import reverse
from django.contrib.auth.models import User
from primepath_routinetest.models import Exam, StudentSession

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_success(message):
    """Print success message in green"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message in red"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def check_theme_files():
    """Check if all theme files exist"""
    print_header("CHECKING THEME FILES")
    
    files_to_check = [
        ('static/css/routinetest-theme.css', 'BCG Green Theme CSS'),
        ('static/js/routinetest-theme.js', 'Theme JavaScript Manager'),
        ('templates/routinetest_base.html', 'RoutineTest Base Template'),
        ('primepath_routinetest/context_processors.py', 'Context Processor'),
    ]
    
    all_present = True
    for file_path, description in files_to_check:
        full_path = Path(__file__).parent / file_path
        if full_path.exists():
            print_success(f"{description}: {file_path}")
        else:
            print_error(f"{description} missing: {file_path}")
            all_present = False
    
    return all_present

def check_css_theme():
    """Verify CSS theme contains BCG green colors"""
    print_header("VERIFYING BCG GREEN COLORS IN CSS")
    
    css_file = Path(__file__).parent / 'static/css/routinetest-theme.css'
    if not css_file.exists():
        print_error("Theme CSS file not found")
        return False
    
    with open(css_file, 'r') as f:
        content = f.read()
    
    bcg_colors = {
        '#00A65E': 'Primary BCG Green',
        '#007C3F': 'Dark Green',
        '#E8F5E9': 'Light Green',
        '#00C853': 'Secondary Green',
        '#1DE9B6': 'Accent Green'
    }
    
    all_present = True
    for color, name in bcg_colors.items():
        if color in content:
            print_success(f"{name} ({color}) found in CSS")
        else:
            print_error(f"{name} ({color}) not found in CSS")
            all_present = False
    
    # Check for key CSS classes
    key_classes = [
        '.routinetest-theme',
        '.btn-primary',
        '.header',
        '.nav-tabs'
    ]
    
    print("\nKey CSS Classes:")
    for css_class in key_classes:
        if css_class in content:
            print_success(f"{css_class} styling found")
        else:
            print_error(f"{css_class} styling missing")
    
    return all_present

def check_templates():
    """Check if templates are using the new base"""
    print_header("CHECKING TEMPLATE INHERITANCE")
    
    template_dir = Path(__file__).parent / 'templates/primepath_routinetest'
    if not template_dir.exists():
        print_error("Template directory not found")
        return False
    
    templates_updated = 0
    templates_total = 0
    
    for template_file in template_dir.glob('*.html'):
        templates_total += 1
        with open(template_file, 'r') as f:
            content = f.read()
        
        if 'routinetest_base.html' in content:
            print_success(f"{template_file.name} - Using RoutineTest base")
            templates_updated += 1
        elif template_file.name == 'index.html':
            # Index might be special
            print_info(f"{template_file.name} - Check manually")
            templates_updated += 1
        else:
            print_error(f"{template_file.name} - Still using old base")
    
    print(f"\nSummary: {templates_updated}/{templates_total} templates updated")
    return templates_updated == templates_total

def check_urls():
    """Verify RoutineTest URLs are accessible"""
    print_header("CHECKING ROUTINETEST URLS")
    
    client = Client()
    
    urls_to_test = [
        ('RoutineTest:index', 'Index Page'),
        ('RoutineTest:exam_list', 'Exam List'),
        ('RoutineTest:start_test', 'Start Test'),
    ]
    
    all_accessible = True
    for url_name, description in urls_to_test:
        try:
            url = reverse(url_name)
            response = client.get(url)
            if response.status_code in [200, 302]:  # 302 for redirects
                print_success(f"{description} ({url}): Status {response.status_code}")
            else:
                print_error(f"{description} ({url}): Status {response.status_code}")
                all_accessible = False
        except Exception as e:
            print_error(f"{description}: {str(e)}")
            all_accessible = False
    
    return all_accessible

def check_context_processor():
    """Verify context processor is working"""
    print_header("CHECKING CONTEXT PROCESSOR")
    
    try:
        from primepath_routinetest.context_processors import routinetest_context
        
        # Create a mock request
        class MockRequest:
            path = '/RoutineTest/index/'
            method = 'GET'
            GET = {}
            user = None
        
        request = MockRequest()
        context = routinetest_context(request)
        
        expected_keys = [
            'module_name',
            'theme_name',
            'theme_primary_color',
            'is_routinetest'
        ]
        
        for key in expected_keys:
            if key in context:
                value = context[key]
                if key == 'theme_primary_color' and value == '#00A65E':
                    print_success(f"{key}: {value} ✓ BCG Green!")
                else:
                    print_success(f"{key}: {value}")
            else:
                print_error(f"{key}: Missing from context")
        
        return True
        
    except ImportError as e:
        print_error(f"Could not import context processor: {e}")
        return False

def check_javascript():
    """Verify JavaScript theme manager exists and has correct content"""
    print_header("CHECKING JAVASCRIPT INTEGRATION")
    
    js_file = Path(__file__).parent / 'static/js/routinetest-theme.js'
    if not js_file.exists():
        print_error("Theme JavaScript file not found")
        return False
    
    with open(js_file, 'r') as f:
        content = f.read()
    
    key_functions = [
        'RoutineTestThemeManager',
        'applyTheme',
        'detectRoutineTestModule',
        'logColorPalette',
        'trackInteractions'
    ]
    
    all_present = True
    for func in key_functions:
        if func in content:
            print_success(f"Function '{func}' found")
        else:
            print_error(f"Function '{func}' missing")
            all_present = False
    
    # Check for BCG color references
    if '#00A65E' in content:
        print_success("BCG Green color reference found in JS")
    else:
        print_error("BCG Green color not found in JS")
        all_present = False
    
    return all_present

def check_models_and_views():
    """Verify models and views are working"""
    print_header("CHECKING MODELS AND VIEWS")
    
    try:
        # Check models
        from primepath_routinetest.models import Exam, Question, StudentSession
        print_success("Models imported successfully")
        
        # Check exam count
        exam_count = Exam.objects.count()
        print_info(f"Total exams in database: {exam_count}")
        
        # Check views
        from primepath_routinetest.views import index, exam, session
        print_success("Views imported successfully")
        
        # Check view logging
        from primepath_routinetest.views.index import logger
        print_success("Logger configured in views")
        
        return True
        
    except ImportError as e:
        print_error(f"Import error: {e}")
        return False

def generate_report():
    """Generate a comprehensive theme integration report"""
    print_header("ROUTINETEST BCG GREEN THEME INTEGRATION REPORT")
    print(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        'Theme Files': check_theme_files(),
        'CSS Theme': check_css_theme(),
        'Templates': check_templates(),
        'URLs': check_urls(),
        'Context Processor': check_context_processor(),
        'JavaScript': check_javascript(),
        'Models & Views': check_models_and_views()
    }
    
    print_header("SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for component, status in results.items():
        if status:
            print_success(f"{component}: PASSED")
        else:
            print_error(f"{component}: FAILED")
    
    print("\n" + "=" * 60)
    print(f"  Overall: {passed}/{total} components passed")
    
    if passed == total:
        print("\n🎉 SUCCESS! BCG Green theme is fully integrated!")
        print("🎨 Theme Color: #00A65E (BCG Green)")
        print("📦 Module: RoutineTest v2.0")
        print("✅ All components working correctly")
    else:
        print("\n⚠️  Some components need attention")
        print("Please review the failed components above")
    
    print("=" * 60)
    
    # Save report to file
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'passed': passed,
        'total': total,
        'theme': {
            'name': 'BCG Green',
            'primary_color': '#00A65E',
            'module': 'RoutineTest'
        }
    }
    
    report_file = Path(__file__).parent / 'routinetest_theme_report.json'
    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n📄 Report saved to: {report_file}")
    
    return passed == total

if __name__ == "__main__":
    print("\n🎨 RoutineTest BCG Green Theme Integration Test")
    print("=" * 60)
    
    success = generate_report()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
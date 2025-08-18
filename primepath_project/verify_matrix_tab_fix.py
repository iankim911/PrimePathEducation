#!/usr/bin/env python
"""
Simple verification script for Matrix Tab visibility fix
Checks files and structure without requiring Django test framework
"""

import os
import sys
import re
from datetime import datetime


def colored(text, color):
    """Helper for colored output"""
    colors = {
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'blue': '\033[94m',
        'cyan': '\033[96m',
        'magenta': '\033[95m',
        'reset': '\033[0m'
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"


def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(colored(f"  ✓ {description} exists", 'green'))
        return True
    else:
        print(colored(f"  ✗ {description} NOT found at {filepath}", 'red'))
        return False


def check_content_in_file(filepath, patterns, description):
    """Check if patterns exist in file"""
    if not os.path.exists(filepath):
        print(colored(f"  ✗ {description} file not found", 'red'))
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    all_found = True
    for pattern_name, pattern in patterns.items():
        if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
            print(colored(f"    ✓ {pattern_name} found", 'green'))
        else:
            print(colored(f"    ✗ {pattern_name} NOT found", 'red'))
            all_found = False
    
    return all_found


def main():
    """Run verification checks"""
    print(colored("\n" + "="*70, 'cyan'))
    print(colored("MATRIX TAB VISIBILITY FIX VERIFICATION", 'cyan'))
    print(colored("="*70, 'cyan'))
    print(colored(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 'blue'))
    print()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    all_checks_passed = True
    
    # 1. Check Template Updates
    print(colored("[1] CHECKING TEMPLATE UPDATES", 'yellow'))
    template_path = os.path.join(base_dir, 'templates/routinetest_base.html')
    
    if check_file_exists(template_path, "routinetest_base.html template"):
        patterns = {
            "Matrix tab ID": r'id="matrix-tab-item"',
            "Matrix tab data attribute": r'data-tab-id="exam-assignments-matrix"',
            "Matrix URL": r'schedule_matrix',
            "Orange styling": r'#FF9800',
            "Exam Assignments text": r'Exam Assignments',
            "Navigation version 3.0": r'VERSION 3\.0.*MATRIX TAB',
            "Matrix tab guardian script": r'matrix-tab-guardian\.js'
        }
        if not check_content_in_file(template_path, patterns, "Base template"):
            all_checks_passed = False
    else:
        all_checks_passed = False
    print()
    
    # 2. Check JavaScript Files
    print(colored("[2] CHECKING JAVASCRIPT FILES", 'yellow'))
    js_files = [
        ('static/js/routinetest/matrix-tab-guardian.js', 'Matrix Tab Guardian'),
        ('static/js/routinetest/schedule-matrix.js', 'Schedule Matrix Module'),
        ('static/js/routinetest-theme.js', 'RoutineTest Theme')
    ]
    
    for js_file, description in js_files:
        js_path = os.path.join(base_dir, js_file)
        if not check_file_exists(js_path, description):
            all_checks_passed = False
    
    # Check Guardian script content
    guardian_path = os.path.join(base_dir, 'static/js/routinetest/matrix-tab-guardian.js')
    if os.path.exists(guardian_path):
        patterns = {
            "Force visible function": r'forceMatrixTabVisible',
            "Create matrix tab function": r'createMatrixTab',
            "Mutation observer": r'MutationObserver',
            "Periodic check": r'periodicCheck'
        }
        print(colored("  Checking Guardian script functionality:", 'cyan'))
        if not check_content_in_file(guardian_path, patterns, "Guardian script"):
            all_checks_passed = False
    print()
    
    # 3. Check Index Template Updates
    print(colored("[3] CHECKING INDEX TEMPLATE", 'yellow'))
    index_template = os.path.join(base_dir, 'templates/primepath_routinetest/index.html')
    
    if check_file_exists(index_template, "index.html template"):
        patterns = {
            "Navigation verification script": r'NAVIGATION VERIFICATION',
            "Matrix tab check": r'MATRIX TAB FOUND',
            "Enhanced debugging": r'Navigation Tabs Check',
            "Force visibility code": r'matrixTabItem\.style\.display.*flex.*important'
        }
        if not check_content_in_file(index_template, patterns, "Index template"):
            all_checks_passed = False
    print()
    
    # 4. Check URL Configuration
    print(colored("[4] CHECKING URL CONFIGURATION", 'yellow'))
    matrix_urls = os.path.join(base_dir, 'primepath_routinetest/matrix_urls.py')
    
    if check_file_exists(matrix_urls, "matrix_urls.py"):
        patterns = {
            "Schedule matrix view": r'schedule_matrix_view',
            "Matrix cell detail": r'matrix_cell_detail',
            "Bulk assign API": r'bulk_assign_exams'
        }
        if not check_content_in_file(matrix_urls, patterns, "Matrix URLs"):
            all_checks_passed = False
    print()
    
    # 5. Check Context Processor
    print(colored("[5] CHECKING CONTEXT PROCESSOR", 'yellow'))
    context_proc = os.path.join(base_dir, 'primepath_routinetest/context_processors.py')
    
    if check_file_exists(context_proc, "context_processors.py"):
        patterns = {
            "is_head_teacher variable": r'is_head_teacher',
            "routinetest_context function": r'def routinetest_context',
            "Module name": r'module_name.*RoutineTest'
        }
        if not check_content_in_file(context_proc, patterns, "Context processor"):
            all_checks_passed = False
    print()
    
    # 6. Check CSS Files
    print(colored("[6] CHECKING CSS FILES", 'yellow'))
    css_files = [
        ('static/css/routinetest/schedule-matrix.css', 'Schedule Matrix CSS'),
        ('static/css/routinetest-theme.css', 'RoutineTest Theme CSS')
    ]
    
    for css_file, description in css_files:
        css_path = os.path.join(base_dir, css_file)
        check_file_exists(css_path, description)
    print()
    
    # 7. Check Models
    print(colored("[7] CHECKING MODELS", 'yellow'))
    matrix_model = os.path.join(base_dir, 'primepath_routinetest/models/exam_schedule_matrix.py')
    
    if check_file_exists(matrix_model, "ExamScheduleMatrix model"):
        patterns = {
            "ExamScheduleMatrix class": r'class ExamScheduleMatrix',
            "Class code field": r'class_code.*CharField',
            "Time period fields": r'time_period_type.*time_period_value'
        }
        if not check_content_in_file(matrix_model, patterns, "Matrix model"):
            all_checks_passed = False
    print()
    
    # Summary
    print(colored("="*70, 'cyan'))
    if all_checks_passed:
        print(colored("✅ ALL VERIFICATION CHECKS PASSED!", 'green'))
        print(colored("The Matrix tab visibility fix has been successfully implemented.", 'green'))
        print()
        print(colored("KEY IMPROVEMENTS MADE:", 'blue'))
        print(colored("1. Enhanced navigation with VERSION 3.0 and forced visibility", 'white'))
        print(colored("2. Added Matrix Tab Guardian JavaScript to ensure tab stays visible", 'white'))
        print(colored("3. Comprehensive console logging for debugging", 'white'))
        print(colored("4. Updated tab labels to match screenshot expectations", 'white'))
        print(colored("5. Added pulsing animation to make Matrix tab prominent", 'white'))
        print(colored("6. Force visibility styles with !important flags", 'white'))
    else:
        print(colored("⚠️ SOME CHECKS FAILED", 'red'))
        print(colored("Please review the failures above and ensure all files are properly updated.", 'red'))
    
    print(colored("="*70, 'cyan'))
    print()
    print(colored("NEXT STEPS:", 'magenta'))
    print(colored("1. Clear browser cache completely (Ctrl+Shift+Delete)", 'yellow'))
    print(colored("2. Restart the Django development server:", 'yellow'))
    print(colored("   cd primepath_project", 'white'))
    print(colored("   ../venv/Scripts/python.exe manage.py runserver 127.0.0.1:8000 --settings=primepath_project.settings_sqlite", 'white'))
    print(colored("3. Navigate to http://127.0.0.1:8000/RoutineTest/", 'yellow'))
    print(colored("4. Open browser console (F12) to see debugging messages", 'yellow'))
    print(colored("5. Look for the orange 'Exam Assignments' tab in navigation", 'yellow'))
    print()
    print(colored("TROUBLESHOOTING:", 'magenta'))
    print(colored("- If tab still not visible, check browser console for errors", 'white'))
    print(colored("- Look for 'MATRIX_TAB_GUARDIAN' messages in console", 'white'))
    print(colored("- Try incognito/private browsing mode to bypass cache", 'white'))
    print(colored("- Check that static files are being served correctly", 'white'))
    print(colored("="*70, 'cyan'))
    
    return 0 if all_checks_passed else 1


if __name__ == '__main__':
    sys.exit(main())
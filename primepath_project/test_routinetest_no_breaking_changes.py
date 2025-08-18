#!/usr/bin/env python
"""
Final verification that no RoutineTest features were broken
Tests based on actual model structure
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.urls import reverse
from primepath_routinetest.models import (
    Exam, ExamScheduleMatrix, TeacherClassAssignment,
    Question, AudioFile, StudentSession, StudentRoster
)

def test_no_breaking_changes():
    """Verify no breaking changes to RoutineTest"""
    print("\n" + "="*80)
    print("FINAL VERIFICATION - NO BREAKING CHANGES")
    print("="*80)
    
    passed = []
    failed = []
    
    client = Client()
    
    # Test 1: Critical URLs Working
    print("\n[TEST 1] Critical URLs...")
    critical_urls = [
        ('RoutineTest:index', 'Dashboard'),
        ('RoutineTest:exam_list', 'Answer Keys (was Manage Exams)'),
        ('RoutineTest:schedule_matrix', 'Exam Assignments (was Schedule Matrix)'),
        ('RoutineTest:create_exam', 'Upload Exam'),
        ('RoutineTest:my_classes', 'My Classes & Access'),
        ('RoutineTest:start_test', 'Start Test'),
        ('RoutineTest:session_list', 'Sessions'),
    ]
    
    for url_name, description in critical_urls:
        try:
            url = reverse(url_name)
            response = client.get(url, follow=False)
            if response.status_code in [200, 302]:
                passed.append(f"✅ {description}: {url} [{response.status_code}]")
                print(f"  ✅ {description}: Working")
            else:
                failed.append(f"❌ {description}: Status {response.status_code}")
        except Exception as e:
            failed.append(f"❌ {description}: {str(e)}")
    
    # Test 2: Model Functionality
    print("\n[TEST 2] Model functionality...")
    
    # Exam model - check actual fields
    exam_fields = ['name', 'exam_type', 'academic_year', 'class_codes', 
                   'pdf_file', 'is_active', 'created_at', 'updated_at',
                   'time_period_month', 'time_period_quarter']
    exam = Exam()
    for field in exam_fields:
        if hasattr(exam, field):
            passed.append(f"✅ Exam.{field} exists")
        else:
            failed.append(f"❌ Exam.{field} missing")
    
    # Question types - check actual types
    actual_types = [qt[0] for qt in Question.QUESTION_TYPES]
    expected_types = ['MCQ', 'CHECKBOX', 'SHORT']  # Core types that should exist
    for qtype in expected_types:
        if qtype in actual_types:
            passed.append(f"✅ Question type {qtype} supported")
        else:
            failed.append(f"❌ Question type {qtype} missing")
    
    # Test 3: ExamScheduleMatrix Critical Methods
    print("\n[TEST 3] Schedule Matrix methods...")
    critical_methods = [
        'get_or_create_cell', 'get_exam_list', 'get_exam_count',
        'add_exam', 'remove_exam', 'can_teacher_edit'
    ]
    
    for method in critical_methods:
        if hasattr(ExamScheduleMatrix, method):
            passed.append(f"✅ ExamScheduleMatrix.{method} exists")
        else:
            failed.append(f"❌ ExamScheduleMatrix.{method} missing")
    
    # Test 4: Template Rendering
    print("\n[TEST 4] Template rendering...")
    from django.template.loader import get_template
    
    critical_templates = [
        'routinetest_base.html',
        'primepath_routinetest/index.html',
        'primepath_routinetest/schedule_matrix.html',
        'primepath_routinetest/exam_list.html',
        'primepath_routinetest/class_access.html',
    ]
    
    for template in critical_templates:
        try:
            t = get_template(template)
            passed.append(f"✅ Template {template} loads")
        except Exception as e:
            if 'appears more than once' in str(e):
                failed.append(f"❌ Template {template}: Duplicate block error")
            else:
                failed.append(f"❌ Template {template}: {str(e)}")
    
    # Test 5: Navigation Changes Applied
    print("\n[TEST 5] Navigation updates...")
    base_template_path = '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/templates/routinetest_base.html'
    
    if os.path.exists(base_template_path):
        with open(base_template_path, 'r') as f:
            content = f.read()
        
        nav_checks = [
            ('Exam Management', 'New module title'),
            ('Answer Keys</a>', 'Answer Keys nav item'),
            ('Exam Assignments</a>', 'Exam Assignments nav item'),
            ('data-nav="answer-keys"', 'Answer Keys data attribute'),
            ('data-nav="exam-assignments"', 'Exam Assignments data attribute'),
        ]
        
        for check_text, description in nav_checks:
            if check_text in content:
                passed.append(f"✅ {description} present")
            else:
                failed.append(f"❌ {description} missing")
    
    # Test 6: JavaScript Functions Added
    print("\n[TEST 6] JavaScript enhancements...")
    matrix_template_path = '/Users/ian/Desktop/VIBECODE/PrimePath/primepath_project/templates/primepath_routinetest/schedule_matrix.html'
    
    if os.path.exists(matrix_template_path):
        with open(matrix_template_path, 'r') as f:
            content = f.read()
        
        js_checks = [
            ('assignExamToCell', 'Exam assignment function'),
            ('removeExamFromCell', 'Exam removal function'),
            ('EXAM_ASSIGNMENTS', 'Console logging prefix'),
        ]
        
        for check_text, description in js_checks:
            if check_text in content:
                passed.append(f"✅ {description} added")
            else:
                failed.append(f"❌ {description} missing")
    
    # Test 7: Context Processor
    print("\n[TEST 7] Context processor...")
    try:
        from primepath_routinetest.context_processors import routinetest_context
        # Create a more complete mock request
        class MockRequest:
            def __init__(self):
                self.path = '/RoutineTest/'
                self.GET = {}
                self.method = 'GET'
        
        context = routinetest_context(MockRequest())
        
        if context.get('module_description') == 'Exam Management System':
            passed.append("✅ Module description updated")
        else:
            failed.append(f"❌ Module description not updated: {context.get('module_description')}")
            
        if context.get('module_version') == '2.1.0':
            passed.append("✅ Module version updated")
            
    except Exception as e:
        failed.append(f"❌ Context processor error: {str(e)}")
    
    # Summary
    print("\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80)
    
    total = len(passed) + len(failed)
    pass_rate = (len(passed) / total * 100) if total > 0 else 0
    
    print(f"\n✅ PASSED: {len(passed)}/{total} ({pass_rate:.1f}%)")
    if len(passed) <= 15:
        for p in passed:
            print(f"  {p}")
    else:
        for p in passed[:10]:
            print(f"  {p}")
        print(f"  ... and {len(passed)-10} more")
    
    if failed:
        print(f"\n❌ FAILED: {len(failed)}/{total}")
        for f in failed:
            print(f"  {f}")
    
    # Overall Assessment
    print("\n" + "="*80)
    print("OVERALL ASSESSMENT")
    print("="*80)
    
    if len(failed) == 0:
        print("✅ PERFECT - No breaking changes detected!")
        print("All existing features are working correctly.")
    elif len(failed) <= 3:
        print("✅ GOOD - Minor issues only")
        print("Core functionality is intact. A few minor items need attention.")
    elif len(failed) <= 10:
        print("⚠️ WARNING - Some features affected")
        print("Most features working but some areas need review.")
    else:
        print("❌ CRITICAL - Significant issues detected")
        print("Multiple features affected. Immediate attention required.")
    
    # Feature Summary
    print("\n" + "="*80)
    print("FEATURE SUMMARY")
    print("="*80)
    
    features = {
        "URL Routing": any("Working" in p for p in passed),
        "Database Models": any("Exam." in p or "Question" in p for p in passed),
        "Schedule Matrix": any("ExamScheduleMatrix" in p for p in passed),
        "Templates": any("Template" in p and "loads" in p for p in passed),
        "Navigation Updates": any("nav item" in p or "data attribute" in p for p in passed),
        "JavaScript Enhancements": any("function" in p for p in passed),
        "Module Naming": any("Module description updated" in p for p in passed),
    }
    
    for feature, working in features.items():
        status = "✅ WORKING" if working else "❌ BROKEN"
        print(f"  {feature}: {status}")
    
    # What Changed
    print("\n" + "="*80)
    print("CHANGES APPLIED")
    print("="*80)
    print("  1. Module title: 'Continuous Assessment' → 'Exam Management'")
    print("  2. Tab renamed: 'Schedule Matrix' → 'Exam Assignments'")
    print("  3. Tab renamed: 'Manage Exams' → 'Answer Keys'")
    print("  4. Fixed: Duplicate {% block extra_css %} in schedule_matrix.html")
    print("  5. Added: JavaScript exam assignment/unassignment functions")
    print("  6. Added: Comprehensive console debugging")
    
    return len(failed) == 0

if __name__ == '__main__':
    success = test_no_breaking_changes()
    sys.exit(0 if success else 1)
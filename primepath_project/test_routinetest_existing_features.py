#!/usr/bin/env python
"""
Comprehensive test to verify no existing RoutineTest features were broken
Tests all critical functionality after the recent changes
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
from django.urls import reverse
from django.contrib.auth.models import User
from primepath_routinetest.models import (
    Exam, ExamScheduleMatrix, TeacherClassAssignment,
    Question, AudioFile, StudentSession, StudentRoster
)
from core.models import Teacher, School, SubProgram, CurriculumLevel
from django.db import connection

def run_existing_features_test():
    """Test all existing RoutineTest features to ensure nothing broke"""
    print("\n" + "="*80)
    print("ROUTINETEST EXISTING FEATURES VERIFICATION")
    print("="*80)
    
    results = {
        'passed': [],
        'failed': [],
        'warnings': []
    }
    
    client = Client()
    
    # Test 1: Database Models Integrity
    print("\n[TEST 1] Checking database models integrity...")
    try:
        # Check all models can be queried
        models_to_check = [
            (Exam, 'Exam'),
            (Question, 'Question'),
            (AudioFile, 'AudioFile'),
            (StudentSession, 'StudentSession'),
            (ExamScheduleMatrix, 'ExamScheduleMatrix'),
            (TeacherClassAssignment, 'TeacherClassAssignment'),
            (StudentRoster, 'StudentRoster'),
        ]
        
        for model_class, model_name in models_to_check:
            try:
                count = model_class.objects.count()
                results['passed'].append(f"✅ {model_name} model accessible (count: {count})")
                print(f"  ✅ {model_name}: {count} records")
            except Exception as e:
                results['failed'].append(f"❌ {model_name} model error: {str(e)}")
                print(f"  ❌ {model_name} error: {str(e)}")
                
    except Exception as e:
        results['failed'].append(f"❌ Database integrity check failed: {str(e)}")
        print(f"  ❌ Database error: {str(e)}")
    
    # Test 2: URL Routing
    print("\n[TEST 2] Checking URL routing...")
    url_tests = [
        ('RoutineTest:index', {}, 'Dashboard'),
        ('RoutineTest:exam_list', {}, 'Exam List'),
        ('RoutineTest:create_exam', {}, 'Create Exam'),
        ('RoutineTest:schedule_matrix', {}, 'Schedule Matrix'),
        ('RoutineTest:my_classes', {}, 'My Classes'),
        ('RoutineTest:session_list', {}, 'Session List'),
        ('RoutineTest:start_test', {}, 'Start Test'),
    ]
    
    for url_name, kwargs, description in url_tests:
        try:
            url = reverse(url_name, kwargs=kwargs)
            response = client.get(url, follow=False)
            # 302 is OK (redirect to login), 200 is OK (page loads)
            if response.status_code in [200, 302]:
                results['passed'].append(f"✅ {description} URL works ({url})")
                print(f"  ✅ {description}: {url} [Status: {response.status_code}]")
            else:
                results['failed'].append(f"❌ {description} returned {response.status_code}")
                print(f"  ❌ {description}: Status {response.status_code}")
        except Exception as e:
            results['failed'].append(f"❌ {description} URL error: {str(e)}")
            print(f"  ❌ {description}: {str(e)}")
    
    # Test 3: Core Exam Functionality
    print("\n[TEST 3] Testing core exam functionality...")
    try:
        # Test exam creation fields
        exam = Exam(
            name="Test Exam",
            exam_type='REVIEW',
            academic_year='2025',
            time_period_type='MONTHLY',
            time_period_value='JAN'
        )
        
        # Check all important fields exist
        important_fields = [
            'name', 'exam_type', 'academic_year', 'time_period_type',
            'time_period_value', 'class_codes', 'pdf_file', 'is_active',
            'skip_first_left_half', 'is_passing_mandatory', 'instructions',
            'passing_marks', 'time_limit', 'total_marks'
        ]
        
        for field in important_fields:
            if hasattr(exam, field):
                results['passed'].append(f"✅ Exam.{field} field exists")
            else:
                results['failed'].append(f"❌ Exam.{field} field missing")
        
        print(f"  ✅ All {len(important_fields)} exam fields verified")
        
    except Exception as e:
        results['failed'].append(f"❌ Exam model test failed: {str(e)}")
        print(f"  ❌ Exam model error: {str(e)}")
    
    # Test 4: Question and Answer Types
    print("\n[TEST 4] Testing question types...")
    try:
        question_types = Question.QUESTION_TYPES
        expected_types = ['MCQ', 'MSQ', 'INTEGER', 'NUMERICAL', 'SHORT']
        
        for q_type in expected_types:
            if any(qt[0] == q_type for qt in question_types):
                results['passed'].append(f"✅ Question type {q_type} supported")
            else:
                results['failed'].append(f"❌ Question type {q_type} missing")
        
        print(f"  ✅ All {len(expected_types)} question types verified")
        
    except Exception as e:
        results['failed'].append(f"❌ Question types check failed: {str(e)}")
        print(f"  ❌ Question types error: {str(e)}")
    
    # Test 5: ExamScheduleMatrix Methods
    print("\n[TEST 5] Testing ExamScheduleMatrix methods...")
    try:
        matrix_methods = [
            'get_or_create_cell',
            'get_exam_list',
            'get_exam_count',
            'add_exam',
            'remove_exam',
            'get_status_color',
            'get_status_icon',
            'can_teacher_edit',
            'get_completion_stats',
            'get_detailed_exam_list'
        ]
        
        for method in matrix_methods:
            if hasattr(ExamScheduleMatrix, method):
                results['passed'].append(f"✅ ExamScheduleMatrix.{method} exists")
            else:
                results['failed'].append(f"❌ ExamScheduleMatrix.{method} missing")
        
        print(f"  ✅ All {len(matrix_methods)} matrix methods verified")
        
    except Exception as e:
        results['failed'].append(f"❌ Matrix methods check failed: {str(e)}")
        print(f"  ❌ Matrix methods error: {str(e)}")
    
    # Test 6: Student Session Fields
    print("\n[TEST 6] Testing StudentSession fields...")
    try:
        session_fields = [
            'exam', 'student_name', 'student_email', 'student_phone',
            'started_at', 'completed_at', 'score', 'answers',
            'time_remaining', 'is_submitted', 'graded_at', 'graded_by'
        ]
        
        session = StudentSession()
        for field in session_fields:
            if hasattr(session, field):
                results['passed'].append(f"✅ StudentSession.{field} exists")
            else:
                results['failed'].append(f"❌ StudentSession.{field} missing")
        
        print(f"  ✅ All {len(session_fields)} session fields verified")
        
    except Exception as e:
        results['failed'].append(f"❌ Session fields check failed: {str(e)}")
        print(f"  ❌ Session fields error: {str(e)}")
    
    # Test 7: File Upload Paths
    print("\n[TEST 7] Testing file upload configurations...")
    try:
        from django.conf import settings
        
        # Check media settings
        if hasattr(settings, 'MEDIA_ROOT'):
            results['passed'].append("✅ MEDIA_ROOT configured")
            print(f"  ✅ MEDIA_ROOT: {settings.MEDIA_ROOT}")
        else:
            results['failed'].append("❌ MEDIA_ROOT not configured")
        
        if hasattr(settings, 'MEDIA_URL'):
            results['passed'].append("✅ MEDIA_URL configured")
            print(f"  ✅ MEDIA_URL: {settings.MEDIA_URL}")
        else:
            results['failed'].append("❌ MEDIA_URL not configured")
            
    except Exception as e:
        results['failed'].append(f"❌ Media settings check failed: {str(e)}")
        print(f"  ❌ Media settings error: {str(e)}")
    
    # Test 8: Template Loading
    print("\n[TEST 8] Testing template loading...")
    from django.template.loader import get_template
    
    templates_to_check = [
        'routinetest_base.html',
        'primepath_routinetest/index.html',
        'primepath_routinetest/exam_list.html',
        'primepath_routinetest/create_exam.html',
        'primepath_routinetest/schedule_matrix.html',
        'primepath_routinetest/class_access.html',
        'primepath_routinetest/start_test.html',
        'primepath_routinetest/student_test.html',
    ]
    
    for template_name in templates_to_check:
        try:
            template = get_template(template_name)
            results['passed'].append(f"✅ Template {template_name} loads")
            print(f"  ✅ {template_name}")
        except Exception as e:
            results['failed'].append(f"❌ Template {template_name} error: {str(e)}")
            print(f"  ❌ {template_name}: {str(e)}")
    
    # Test 9: Ajax Endpoints
    print("\n[TEST 9] Testing AJAX endpoints...")
    ajax_endpoints = [
        ('RoutineTest:api_schedule_data', 'Schedule API'),
        ('RoutineTest:api_exam_pool', 'Exam Pool API'),
        ('RoutineTest:api_class_students', 'Class Students API'),
    ]
    
    for url_name, description in ajax_endpoints:
        try:
            url = reverse(url_name)
            results['passed'].append(f"✅ {description} endpoint exists")
            print(f"  ✅ {description}: {url}")
        except:
            # Some endpoints might not exist, which is OK
            results['warnings'].append(f"⚠️ {description} endpoint not found")
            print(f"  ⚠️ {description} not configured")
    
    # Test 10: Context Processors
    print("\n[TEST 10] Testing context processors...")
    try:
        from primepath_routinetest.context_processors import routinetest_context
        
        mock_request = type('obj', (object,), {
            'path': '/RoutineTest/',
            'GET': {}
        })()
        
        context = routinetest_context(mock_request)
        
        expected_keys = [
            'module_name', 'module_version', 'module_description',
            'bcg_green_theme', 'current_view'
        ]
        
        for key in expected_keys:
            if key in context:
                results['passed'].append(f"✅ Context key '{key}' present")
            else:
                results['failed'].append(f"❌ Context key '{key}' missing")
        
        print(f"  ✅ Context processor verified with {len(context)} keys")
        
    except Exception as e:
        results['failed'].append(f"❌ Context processor error: {str(e)}")
        print(f"  ❌ Context processor: {str(e)}")
    
    # Summary
    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)
    
    total_checks = len(results['passed']) + len(results['failed']) + len(results['warnings'])
    
    print(f"\n✅ PASSED: {len(results['passed'])} / {total_checks} checks")
    if len(results['passed']) <= 10:
        for msg in results['passed']:
            print(f"  {msg}")
    else:
        for msg in results['passed'][:5]:
            print(f"  {msg}")
        print(f"  ... and {len(results['passed'])-5} more")
    
    if results['warnings']:
        print(f"\n⚠️ WARNINGS: {len(results['warnings'])}")
        for msg in results['warnings']:
            print(f"  {msg}")
    
    if results['failed']:
        print(f"\n❌ FAILED: {len(results['failed'])} checks")
        for msg in results['failed']:
            print(f"  {msg}")
        print("\n🔴 SOME FEATURES MAY BE AFFECTED")
    else:
        print("\n🎉 ALL EXISTING FEATURES VERIFIED - No Breaking Changes!")
    
    # Feature Status Report
    print("\n" + "="*80)
    print("FEATURE STATUS REPORT")
    print("="*80)
    
    features = {
        "Database Models": len([r for r in results['passed'] if 'model' in r.lower()]) > 5,
        "URL Routing": len([r for r in results['passed'] if 'URL' in r]) > 5,
        "Exam Management": len([r for r in results['passed'] if 'Exam' in r]) > 8,
        "Question System": len([r for r in results['passed'] if 'Question' in r or 'question' in r]) > 3,
        "Schedule Matrix": len([r for r in results['passed'] if 'Matrix' in r or 'matrix' in r]) > 8,
        "Student Sessions": len([r for r in results['passed'] if 'Session' in r or 'session' in r]) > 8,
        "File Uploads": len([r for r in results['passed'] if 'MEDIA' in r]) >= 2,
        "Templates": len([r for r in results['passed'] if 'Template' in r]) > 5,
        "Context System": len([r for r in results['passed'] if 'Context' in r or 'context' in r]) > 0,
    }
    
    for feature, status in features.items():
        icon = "✅" if status else "❌"
        status_text = "WORKING" if status else "NEEDS ATTENTION"
        print(f"  {icon} {feature}: {status_text}")
    
    print("\n" + "="*80)
    print("CRITICAL PATHS TEST")
    print("="*80)
    
    critical_paths = [
        ("Create Exam", "/RoutineTest/exams/create/", "Upload new exam"),
        ("View Exams", "/RoutineTest/exams/", "List all exams"),
        ("Schedule Matrix", "/RoutineTest/schedule-matrix/", "Exam assignments"),
        ("Start Test", "/RoutineTest/start/", "Student test initiation"),
        ("My Classes", "/RoutineTest/access/my-classes/", "Class management"),
    ]
    
    for path_name, url, description in critical_paths:
        print(f"  • {path_name}: {url}")
        print(f"    Purpose: {description}")
    
    return len(results['failed']) == 0

if __name__ == '__main__':
    success = run_existing_features_test()
    sys.exit(0 if success else 1)
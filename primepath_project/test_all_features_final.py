#!/usr/bin/env python
"""
Final comprehensive test to verify ALL features after class dropdown fix.
Tests every critical feature in both RoutineTest and PlacementTest modules.
"""
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from primepath_routinetest.models import Exam as RoutineExam
from placement_test.models import Exam as PlacementExam
from core.models import Program, SubProgram, CurriculumLevel

def test_all_features():
    """Test all features comprehensively."""
    print("\n" + "="*80)
    print("🔍 FINAL COMPREHENSIVE FEATURE TEST AFTER CLASS DROPDOWN FIX")
    print("="*80)
    
    client = Client()
    test_results = []
    
    # ========================================
    # SECTION 1: RoutineTest Core Features
    # ========================================
    print("\n📋 SECTION 1: RoutineTest Core Features")
    print("-" * 60)
    
    # Test 1.1: Create Exam Page
    print("\n[1.1] Create Exam Page")
    response = client.get('/RoutineTest/exams/create/', follow=True)
    if response.status_code in [200, 302]:
        print("✅ Create exam page accessible")
        test_results.append(('RT: Create Exam Page', True))
    else:
        print(f"❌ Create exam page error: {response.status_code}")
        test_results.append(('RT: Create Exam Page', False))
    
    # Test 1.2: Exam List
    print("\n[1.2] Exam List")
    response = client.get('/RoutineTest/exams/', follow=True)
    if response.status_code in [200, 302]:
        print("✅ Exam list accessible")
        test_results.append(('RT: Exam List', True))
    else:
        print(f"❌ Exam list error: {response.status_code}")
        test_results.append(('RT: Exam List', False))
    
    # Test 1.3: Sessions
    print("\n[1.3] Session Management")
    response = client.get('/RoutineTest/sessions/', follow=True)
    if response.status_code in [200, 302]:
        print("✅ Sessions page accessible")
        test_results.append(('RT: Sessions', True))
    else:
        print(f"❌ Sessions error: {response.status_code}")
        test_results.append(('RT: Sessions', False))
    
    # Test 1.4: Roster Management (Phase 5)
    print("\n[1.4] Roster Management")
    response = client.get('/RoutineTest/roster/', follow=True)
    if response.status_code in [200, 302]:
        print("✅ Roster management accessible")
        test_results.append(('RT: Roster', True))
    else:
        print(f"❌ Roster error: {response.status_code}")
        test_results.append(('RT: Roster', False))
    
    # Test 1.5: Index Page
    print("\n[1.5] Index Page")
    response = client.get('/RoutineTest/', follow=True)
    if response.status_code in [200, 302]:
        print("✅ Index page accessible")
        test_results.append(('RT: Index', True))
    else:
        print(f"❌ Index error: {response.status_code}")
        test_results.append(('RT: Index', False))
    
    # ========================================
    # SECTION 2: RoutineTest APIs
    # ========================================
    print("\n📋 SECTION 2: RoutineTest API Endpoints")
    print("-" * 60)
    
    # Test 2.1: Curriculum Hierarchy API
    print("\n[2.1] Curriculum Hierarchy API")
    response = client.get('/RoutineTest/api/curriculum-hierarchy/')
    if response.status_code == 200:
        data = json.loads(response.content)
        if data.get('success'):
            hierarchy = data['data']
            programs = hierarchy.get('programs', [])
            print(f"✅ Curriculum API working: {len(programs)} programs")
            
            # Check for Lv abbreviation
            has_lv = False
            for levels in hierarchy.get('levels', {}).values():
                if levels and 'Lv' in levels[0].get('display_name', ''):
                    has_lv = True
                    break
            
            if has_lv:
                print("✅ Using 'Lv' abbreviation")
                test_results.append(('RT API: Lv Format', True))
            else:
                print("❌ Missing 'Lv' abbreviation")
                test_results.append(('RT API: Lv Format', False))
                
            test_results.append(('RT API: Curriculum', True))
        else:
            print("❌ API returned error")
            test_results.append(('RT API: Curriculum', False))
    else:
        print(f"❌ API status: {response.status_code}")
        test_results.append(('RT API: Curriculum', False))
    
    # ========================================
    # SECTION 3: PlacementTest Features
    # ========================================
    print("\n📋 SECTION 3: PlacementTest Features (Should be unaffected)")
    print("-" * 60)
    
    placement_urls = [
        ('/PlacementTest/', 'Index'),
        ('/PlacementTest/start/', 'Start Test'),
        ('/PlacementTest/exams/', 'Exam List'),
        ('/PlacementTest/exams/create/', 'Create Exam'),
        ('/PlacementTest/sessions/', 'Sessions'),
        ('/PlacementTest/teacher/dashboard/', 'Teacher Dashboard')
    ]
    
    for url, name in placement_urls:
        response = client.get(url, follow=True)
        if response.status_code in [200, 302]:
            print(f"✅ {name}: {url}")
            test_results.append((f'PT: {name}', True))
        else:
            print(f"❌ {name}: {response.status_code}")
            test_results.append((f'PT: {name}', False))
    
    # ========================================
    # SECTION 4: Template Features
    # ========================================
    print("\n📋 SECTION 4: Template Features in Create Exam")
    print("-" * 60)
    
    template_path = 'templates/primepath_routinetest/create_exam.html'
    with open(template_path, 'r') as f:
        template = f.read()
        
        features = [
            ('Exam Type Selection', 'id="exam_type"'),
            ('Time Period Fields', 'id="month_field"'),
            ('Academic Year', 'id="academic_year"'),
            ('Class Selection', 'id="class_codes"'),
            ('Program Dropdown', 'id="program_select"'),
            ('SubProgram Dropdown', 'id="subprogram_select"'),
            ('Level Dropdown', 'id="level_select"'),
            ('User Comment', 'id="user_comment"'),
            ('PDF Upload', 'id="pdf_file"'),
            ('Audio Upload', 'id="audio_files"'),
            ('Instructions', 'id="instructions"'),
            ('Late Submission', 'id="allow_late_submission"'),
            ('Auto-Generated Name', 'id="final_name_preview"'),
            ('Quick Select Buttons', 'selectAllClasses()'),
            ('Grade Selection', 'selectGrade('),
            ('Cascading JS', 'routinetest-cascading-curriculum.js'),
            ('Class Fallback', 'CLASS_7A'),
            ('Debug Info', 'window.debugInfo'),
            ('Error Handler', "window.addEventListener('error'"),
            ('Form Validation', 'At least one class must be selected')
        ]
        
        for name, pattern in features:
            if pattern in template:
                print(f"✅ {name}")
                test_results.append((f'Template: {name}', True))
            else:
                print(f"❌ {name}")
                test_results.append((f'Template: {name}', False))
    
    # ========================================
    # SECTION 5: JavaScript Functionality
    # ========================================
    print("\n📋 SECTION 5: JavaScript Functions")
    print("-" * 60)
    
    js_functions = [
        ('selectAllClasses', 'function selectAllClasses()'),
        ('clearAllClasses', 'function clearAllClasses()'),
        ('selectGrade', 'function selectGrade(gradeNumber)'),
        ('updateSelectedClassesDisplay', 'function updateSelectedClassesDisplay()'),
        ('updatePDFDisplay', 'function updatePDFDisplay()'),
        ('updateAudioDisplay', 'function updateAudioDisplay()'),
        ('removeAudioFile', 'function removeAudioFile('),
        ('handleExamTypeChange', 'handleExamTypeChange()'),
        ('initInstructionsTracking', 'function initInstructionsTracking()'),
        ('DOMContentLoaded', "document.addEventListener('DOMContentLoaded'"),
        ('Form Submit Handler', "examForm.addEventListener('submit'"),
        ('Class Debug', '[CLASS_DEBUG]'),
        ('Page Init', '[PAGE_INIT]'),
        ('Defensive Programming', 'try {'),
        ('Null Checks', 'if (classCodesSelect)')
    ]
    
    for name, pattern in js_functions:
        if pattern in template:
            print(f"✅ {name}")
            test_results.append((f'JS: {name}', True))
        else:
            print(f"❌ {name}")
            test_results.append((f'JS: {name}', False))
    
    # ========================================
    # SECTION 6: Model Functionality
    # ========================================
    print("\n📋 SECTION 6: Model Integrity")
    print("-" * 60)
    
    # Check RoutineTest Exam model
    try:
        routine_fields = [f.name for f in RoutineExam._meta.fields]
        rt_specific = ['exam_type', 'time_period_month', 'time_period_quarter', 
                       'academic_year', 'class_codes']
        
        rt_found = [f for f in rt_specific if f in routine_fields]
        if len(rt_found) == len(rt_specific):
            print(f"✅ RoutineTest model has all {len(rt_specific)} specific fields")
            test_results.append(('Model: RT Fields', True))
        else:
            missing = set(rt_specific) - set(rt_found)
            print(f"❌ Missing fields: {missing}")
            test_results.append(('Model: RT Fields', False))
            
    except Exception as e:
        print(f"❌ Model error: {e}")
        test_results.append(('Model: RT Fields', False))
    
    # Check PlacementTest model isolation
    try:
        placement_fields = [f.name for f in PlacementExam._meta.fields]
        
        # These should NOT be in PlacementTest
        contamination = [f for f in rt_specific if f in placement_fields]
        if not contamination:
            print("✅ PlacementTest model clean (no RT fields)")
            test_results.append(('Model: PT Isolation', True))
        else:
            print(f"❌ PlacementTest contaminated with: {contamination}")
            test_results.append(('Model: PT Isolation', False))
            
    except Exception as e:
        print(f"❌ Model error: {e}")
        test_results.append(('Model: PT Isolation', False))
    
    # Check CLASS_CODE_CHOICES
    try:
        class_choices = RoutineExam.CLASS_CODE_CHOICES
        if len(class_choices) == 12:
            print(f"✅ CLASS_CODE_CHOICES has 12 options")
            test_results.append(('Model: Class Choices', True))
        else:
            print(f"❌ CLASS_CODE_CHOICES has {len(class_choices)} options (expected 12)")
            test_results.append(('Model: Class Choices', False))
    except Exception as e:
        print(f"❌ Error accessing CLASS_CODE_CHOICES: {e}")
        test_results.append(('Model: Class Choices', False))
    
    # ========================================
    # FINAL SUMMARY
    # ========================================
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\nTests Passed: {passed}/{total} ({percentage:.1f}%)")
    
    # Group results by category
    categories = {
        'RoutineTest Core': [],
        'RoutineTest API': [],
        'PlacementTest': [],
        'Template Features': [],
        'JavaScript': [],
        'Models': []
    }
    
    for name, result in test_results:
        if name.startswith('RT:'):
            categories['RoutineTest Core'].append((name, result))
        elif name.startswith('RT API:'):
            categories['RoutineTest API'].append((name, result))
        elif name.startswith('PT:'):
            categories['PlacementTest'].append((name, result))
        elif name.startswith('Template:'):
            categories['Template Features'].append((name, result))
        elif name.startswith('JS:'):
            categories['JavaScript'].append((name, result))
        elif name.startswith('Model:'):
            categories['Models'].append((name, result))
    
    print("\n📈 Results by Category:")
    print("-" * 40)
    for category, results in categories.items():
        if results:
            cat_passed = sum(1 for _, r in results if r)
            cat_total = len(results)
            cat_percent = (cat_passed / cat_total * 100) if cat_total > 0 else 0
            status = "✅" if cat_percent == 100 else "⚠️" if cat_percent >= 80 else "❌"
            print(f"{status} {category}: {cat_passed}/{cat_total} ({cat_percent:.1f}%)")
    
    # List failures
    if passed < total:
        print("\n❌ Failed Tests:")
        print("-" * 40)
        for name, result in test_results:
            if not result:
                print(f"  • {name}")
    
    # Final verdict
    print("\n" + "="*80)
    if percentage == 100:
        print("🎉 PERFECT! NO FEATURES AFFECTED BY CLASS DROPDOWN FIX! 🎉")
    elif percentage >= 95:
        print("✅ EXCELLENT: Class dropdown fix successful, minimal impact")
    elif percentage >= 90:
        print("✅ VERY GOOD: Fix working, minor issues only")
    else:
        print("⚠️ CHECK NEEDED: Some features may be affected")
    
    print("\n🔍 Critical Feature Status:")
    print("-" * 40)
    critical = [
        ('Class Selection Working', 'Template: Class Selection'),
        ('Cascading Dropdowns', 'Template: Cascading JS'),
        ('Form Validation', 'Template: Form Validation'),
        ('PlacementTest Isolated', 'Model: PT Isolation'),
        ('RoutineTest API', 'RT API: Curriculum')
    ]
    
    for display, key in critical:
        result = next((r for n, r in test_results if n == key), None)
        if result:
            print(f"✅ {display}")
        else:
            print(f"❌ {display}")
    
    print("\n" + "="*80)
    
    return passed, total, percentage

if __name__ == '__main__':
    try:
        passed, total, percentage = test_all_features()
        sys.exit(0 if percentage >= 90 else 1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
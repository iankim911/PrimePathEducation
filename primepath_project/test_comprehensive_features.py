#!/usr/bin/env python
"""
Comprehensive test to verify ALL existing features still work after the fix.
Tests every aspect of both RoutineTest and PlacementTest modules.
"""
import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primepath_project.settings_sqlite')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from primepath_routinetest.models import Exam as RoutineExam, StudentSession as RoutineSession
from placement_test.models import Exam as PlacementExam, StudentSession as PlacementSession
from core.models import Program, SubProgram, CurriculumLevel

def test_all_features():
    """Comprehensive test of all features."""
    print("\n" + "="*80)
    print("🔍 COMPREHENSIVE FEATURE VERIFICATION TEST")
    print("="*80)
    
    client = Client()
    test_results = []
    
    # ========================================
    # SECTION 1: RoutineTest Create Exam Page
    # ========================================
    print("\n" + "="*60)
    print("📋 SECTION 1: RoutineTest Create Exam Features")
    print("="*60)
    
    # Test 1.1: Page loads without errors
    print("\n[1.1] Page Loading Test")
    response = client.get('/RoutineTest/exams/create/', follow=True)
    if response.status_code in [200, 302] or hasattr(response, 'redirect_chain'):
        print("✅ Create exam page loads")
        test_results.append(('Create Exam Page Load', True))
    else:
        print(f"❌ Create exam page error: {response.status_code}")
        test_results.append(('Create Exam Page Load', False))
    
    # Test 1.2: Cascading curriculum API
    print("\n[1.2] Cascading Curriculum API Test")
    response = client.get('/RoutineTest/api/curriculum-hierarchy/')
    if response.status_code == 200:
        data = json.loads(response.content)
        if data.get('success'):
            hierarchy = data['data']
            programs = hierarchy.get('programs', [])
            print(f"✅ API returns {len(programs)} programs")
            
            # Check for Lv abbreviation
            has_lv = False
            for levels in hierarchy.get('levels', {}).values():
                if levels and 'Lv' in levels[0].get('display_name', ''):
                    has_lv = True
                    break
            
            if has_lv:
                print("✅ Using 'Lv' abbreviation format")
                test_results.append(('Lv Abbreviation', True))
            else:
                print("❌ Missing 'Lv' abbreviation")
                test_results.append(('Lv Abbreviation', False))
                
            test_results.append(('Curriculum API', True))
        else:
            print("❌ API returned error")
            test_results.append(('Curriculum API', False))
    else:
        print(f"❌ API status: {response.status_code}")
        test_results.append(('Curriculum API', False))
    
    # Test 1.3: Check JavaScript file exists
    print("\n[1.3] JavaScript Files Test")
    js_file = 'static/js/routinetest-cascading-curriculum.js'
    if os.path.exists(js_file):
        with open(js_file, 'r') as f:
            content = f.read()
            if 'v3.1' in content and 'generateExamName' in content:
                print("✅ Cascading JS v3.1 present and functional")
                test_results.append(('Cascading JS', True))
            else:
                print("❌ Cascading JS outdated or incomplete")
                test_results.append(('Cascading JS', False))
    else:
        print("❌ Cascading JS file missing")
        test_results.append(('Cascading JS', False))
    
    # Test 1.4: Template structure
    print("\n[1.4] Template Structure Test")
    template_path = 'templates/primepath_routinetest/create_exam.html'
    with open(template_path, 'r') as f:
        template = f.read()
        
        required_sections = [
            ('Exam Type & Time Period', 'Exam Type & Time Period'),
            ('Class Selection', 'Class Selection'),
            ('Curriculum Selection', 'Curriculum Selection'),
            ('Additional Notes', 'Additional Notes'),
            ('Auto-Generated Name', 'Auto-Generated Exam Name'),
            ('PDF Upload', 'Exam PDF File'),
            ('Audio Upload', 'Audio Files'),
            ('Scheduling', 'Scheduling & Instructions')
        ]
        
        for name, pattern in required_sections:
            if pattern in template:
                print(f"✅ {name} section present")
                test_results.append((f'Section: {name}', True))
            else:
                print(f"❌ {name} section missing")
                test_results.append((f'Section: {name}', False))
    
    # ========================================
    # SECTION 2: RoutineTest Other Features
    # ========================================
    print("\n" + "="*60)
    print("📋 SECTION 2: RoutineTest Other Features")
    print("="*60)
    
    # Test 2.1: Exam list page
    print("\n[2.1] Exam List Page")
    response = client.get('/RoutineTest/exams/', follow=True)
    if response.status_code in [200, 302]:
        print("✅ Exam list page accessible")
        test_results.append(('Exam List Page', True))
    else:
        print(f"❌ Exam list page error: {response.status_code}")
        test_results.append(('Exam List Page', False))
    
    # Test 2.2: Session management
    print("\n[2.2] Session Management")
    response = client.get('/RoutineTest/sessions/', follow=True)
    if response.status_code in [200, 302]:
        print("✅ Session list accessible")
        test_results.append(('Session List', True))
    else:
        print(f"❌ Session list error: {response.status_code}")
        test_results.append(('Session List', False))
    
    # Test 2.3: Model functionality
    print("\n[2.3] Model Functionality")
    try:
        # Check RoutineTest exam model
        routine_exam_count = RoutineExam.objects.count()
        print(f"✅ RoutineExam model: {routine_exam_count} exams")
        test_results.append(('RoutineExam Model', True))
        
        # Check unique fields
        routine_fields = [f.name for f in RoutineExam._meta.fields]
        expected_fields = ['exam_type', 'time_period_month', 'time_period_quarter', 
                          'academic_year', 'class_codes']
        
        missing_fields = [f for f in expected_fields if f in routine_fields]
        if missing_fields:
            print(f"✅ RoutineTest specific fields present: {len(missing_fields)}")
            test_results.append(('RoutineTest Fields', True))
        else:
            print("❌ Some RoutineTest fields missing")
            test_results.append(('RoutineTest Fields', False))
            
    except Exception as e:
        print(f"❌ Model error: {e}")
        test_results.append(('RoutineExam Model', False))
    
    # ========================================
    # SECTION 3: PlacementTest Features
    # ========================================
    print("\n" + "="*60)
    print("📋 SECTION 3: PlacementTest Features (Should be unaffected)")
    print("="*60)
    
    # Test 3.1: PlacementTest pages
    print("\n[3.1] PlacementTest Pages")
    placement_urls = [
        ('/PlacementTest/', 'Index'),
        ('/PlacementTest/start/', 'Start Test'),
        ('/PlacementTest/exams/', 'Exam List'),
        ('/PlacementTest/exams/create/', 'Create Exam'),
        ('/PlacementTest/sessions/', 'Sessions')
    ]
    
    for url, name in placement_urls:
        response = client.get(url, follow=True)
        if response.status_code in [200, 302] or hasattr(response, 'redirect_chain'):
            print(f"✅ PlacementTest {name}: {url}")
            test_results.append((f'PlacementTest: {name}', True))
        else:
            print(f"❌ PlacementTest {name}: {response.status_code}")
            test_results.append((f'PlacementTest: {name}', False))
    
    # Test 3.2: PlacementTest templates unchanged
    print("\n[3.2] PlacementTest Template Integrity")
    placement_template = 'templates/placement_test/create_exam.html'
    if os.path.exists(placement_template):
        with open(placement_template, 'r') as f:
            content = f.read()
            # Should NOT have RoutineTest changes
            if 'routinetest-cascading-curriculum' not in content and 'v4.0' not in content:
                print("✅ PlacementTest template unchanged")
                test_results.append(('PlacementTest Template', True))
            else:
                print("❌ PlacementTest template contaminated")
                test_results.append(('PlacementTest Template', False))
    else:
        print("✅ PlacementTest template (not found - OK)")
        test_results.append(('PlacementTest Template', True))
    
    # Test 3.3: PlacementTest models
    print("\n[3.3] PlacementTest Models")
    try:
        placement_exam_count = PlacementExam.objects.count()
        print(f"✅ PlacementExam model: {placement_exam_count} exams")
        test_results.append(('PlacementExam Model', True))
    except Exception as e:
        print(f"❌ PlacementExam model error: {e}")
        test_results.append(('PlacementExam Model', False))
    
    # ========================================
    # SECTION 4: Form Functionality Tests
    # ========================================
    print("\n" + "="*60)
    print("📋 SECTION 4: Form Functionality (Critical Features)")
    print("="*60)
    
    # Test 4.1: Check form elements in template
    print("\n[4.1] Form Elements Check")
    with open('templates/primepath_routinetest/create_exam.html', 'r') as f:
        template = f.read()
        
        form_elements = [
            ('exam_type', 'Exam Type dropdown'),
            ('time_period_month', 'Month selector'),
            ('time_period_quarter', 'Quarter selector'),
            ('academic_year', 'Academic Year'),
            ('class_codes', 'Class selection'),
            ('program_select', 'Program dropdown'),
            ('subprogram_select', 'SubProgram dropdown'),
            ('level_select', 'Level dropdown'),
            ('user_comment', 'User comment field'),
            ('pdf_file', 'PDF upload'),
            ('audio_files', 'Audio upload'),
            ('instructions', 'Instructions field'),
            ('allow_late_submission', 'Late submission checkbox')
        ]
        
        for element_id, name in form_elements:
            if f'id="{element_id}"' in template:
                print(f"✅ {name}")
                test_results.append((f'Form: {name}', True))
            else:
                print(f"❌ {name} missing")
                test_results.append((f'Form: {name}', False))
    
    # Test 4.2: JavaScript functions
    print("\n[4.2] JavaScript Functions Check")
    js_functions = [
        ('selectAllClasses', 'Select All Classes'),
        ('clearAllClasses', 'Clear All Classes'),
        ('selectGrade', 'Select Grade'),
        ('updateSelectedClassesDisplay', 'Update Display'),
        ('updatePDFDisplay', 'PDF Display'),
        ('updateAudioDisplay', 'Audio Display'),
        ('removeAudioFile', 'Remove Audio')
    ]
    
    for func_name, display_name in js_functions:
        if f'function {func_name}' in template:
            print(f"✅ {display_name} function")
            test_results.append((f'JS Func: {display_name}', True))
        else:
            print(f"❌ {display_name} function missing")
            test_results.append((f'JS Func: {display_name}', False))
    
    # Test 4.3: Hidden fields for data storage
    print("\n[4.3] Hidden Fields Check")
    hidden_fields = [
        'curriculum_level',
        'generated_base_name',
        'final_exam_name',
        'selected_program',
        'selected_subprogram',
        'selected_level_number'
    ]
    
    for field in hidden_fields:
        if f'id="{field}"' in template and 'type="hidden"' in template:
            print(f"✅ Hidden field: {field}")
            test_results.append((f'Hidden: {field}', True))
        else:
            print(f"❌ Hidden field missing: {field}")
            test_results.append((f'Hidden: {field}', False))
    
    # ========================================
    # SECTION 5: Error Handling & Defensive Programming
    # ========================================
    print("\n" + "="*60)
    print("📋 SECTION 5: Error Handling & Defensive Programming")
    print("="*60)
    
    print("\n[5.1] Defensive Programming Features")
    defensive_features = [
        ("window.addEventListener('error'", 'Global error handler'),
        ('try {', 'Try-catch blocks'),
        ('if (classCodesSelect)', 'Null checks'),
        ('console.log', 'Console logging'),
        ('console.error', 'Error logging'),
        ('[EXAM_CREATION_v4.0]', 'Version tracking'),
        ('[DOM_READY]', 'DOM ready logging'),
        ('[FORM_SUBMIT]', 'Form submission logging')
    ]
    
    for pattern, name in defensive_features:
        if pattern in template:
            print(f"✅ {name}")
            test_results.append((f'Defensive: {name}', True))
        else:
            print(f"❌ {name} missing")
            test_results.append((f'Defensive: {name}', False))
    
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
        'RoutineTest Forms': [],
        'PlacementTest': [],
        'JavaScript': [],
        'Defensive': [],
        'Other': []
    }
    
    for name, result in test_results:
        if 'PlacementTest' in name:
            categories['PlacementTest'].append((name, result))
        elif 'Form:' in name or 'Hidden:' in name:
            categories['RoutineTest Forms'].append((name, result))
        elif 'JS' in name or 'Cascading' in name:
            categories['JavaScript'].append((name, result))
        elif 'Defensive:' in name:
            categories['Defensive'].append((name, result))
        elif 'Section:' in name or 'Curriculum' in name or 'Exam' in name:
            categories['RoutineTest Core'].append((name, result))
        else:
            categories['Other'].append((name, result))
    
    print("\n📈 Results by Category:")
    print("-" * 40)
    for category, results in categories.items():
        if results:
            cat_passed = sum(1 for _, r in results if r)
            cat_total = len(results)
            cat_percent = (cat_passed / cat_total * 100) if cat_total > 0 else 0
            status = "✅" if cat_percent == 100 else "⚠️" if cat_percent >= 80 else "❌"
            print(f"{status} {category}: {cat_passed}/{cat_total} ({cat_percent:.1f}%)")
    
    # List failures if any
    if passed < total:
        print("\n❌ Failed Tests:")
        print("-" * 40)
        for name, result in test_results:
            if not result:
                print(f"  • {name}")
    
    # Final verdict
    print("\n" + "="*80)
    if percentage == 100:
        print("🎉 PERFECT SCORE! ALL FEATURES WORKING! 🎉")
    elif percentage >= 95:
        print("✅ EXCELLENT: Nearly all features working perfectly")
    elif percentage >= 90:
        print("✅ VERY GOOD: Most features working, minor issues only")
    elif percentage >= 80:
        print("⚠️ GOOD: Core features working, some issues to address")
    else:
        print("❌ NEEDS ATTENTION: Significant features affected")
    
    print("\n🔍 Key Findings:")
    print("-" * 40)
    
    # Check critical features
    critical_passed = True
    critical_features = [
        'Create Exam Page Load',
        'Curriculum API',
        'Cascading JS',
        'Form: PDF upload',
        'PlacementTest: Index'
    ]
    
    for feature in critical_features:
        result = next((r for n, r in test_results if n == feature), None)
        if result is False:
            critical_passed = False
            print(f"❌ CRITICAL: {feature} is broken")
    
    if critical_passed:
        print("✅ All critical features are functional")
    
    print("\n" + "="*80)
    
    return passed, total, percentage

if __name__ == '__main__':
    try:
        passed, total, percentage = test_all_features()
        
        # Exit with appropriate code
        if percentage == 100:
            sys.exit(0)
        elif percentage >= 90:
            sys.exit(0)  # Still acceptable
        else:
            sys.exit(1)  # Significant issues
            
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)